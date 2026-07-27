"""
graph_schema.py — Core data structures for the Skill Dependency Graph.

The graph is a Directed Acyclic Graph (DAG) where:
  - Nodes  = Skills (SkillNode)
  - Edges  = Prerequisite relationships (SkillEdge)
  - Weights= Transition difficulty 0.0 (easy) → 1.0 (hard)

Two storage backends are supported:
  1. JSON file  — fast dev cache, no DB required
  2. PostgreSQL — production source of truth (habilidades_catalogo + grafo_habilidades_aristas)
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional

logger = logging.getLogger("lpo.graph_schema")


# ─────────────────────────────────────────────────────────────────────────────
#  Data Classes
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class SkillNode:
    """A single skill in the dependency graph."""
    skill_id:                 int
    skill_name:               str
    category:                 str    # foundational | technical | creative | business
    difficulty_level:         float  # 0.0 = beginner  →  1.0 = expert
    estimated_learning_hours: float  # hours to reach ~70/100 mastery from zero

    def __post_init__(self):
        assert 0.0 <= self.difficulty_level <= 1.0, \
            f"difficulty_level must be 0–1, got {self.difficulty_level}"
        assert self.estimated_learning_hours >= 0, \
            f"estimated_learning_hours must be ≥ 0, got {self.estimated_learning_hours}"


@dataclass
class SkillEdge:
    """A directed prerequisite relationship: source → target."""
    source_id:        int    # prerequisite skill
    target_id:        int    # skill that depends on source
    weight:           float  # transition difficulty 0.0–1.0
    required_mastery: float  # min mastery of source before starting target (0–100)
    rationale:        str    # human-readable explanation

    def __post_init__(self):
        assert 0.0 <= self.weight <= 1.0, \
            f"edge weight must be 0–1, got {self.weight}"
        assert 0.0 <= self.required_mastery <= 100.0, \
            f"required_mastery must be 0–100, got {self.required_mastery}"
        assert self.source_id != self.target_id, \
            "Self-loop detected: source_id == target_id"


@dataclass
class SkillGraph:
    """Complete skill dependency graph."""
    nodes: Dict[int, SkillNode]  # skill_id → SkillNode
    edges: List[SkillEdge]

    # Built lazily on first access
    _adj_out: Optional[Dict[int, List[SkillEdge]]] = field(default=None, repr=False)
    _adj_in:  Optional[Dict[int, List[SkillEdge]]] = field(default=None, repr=False)

    # ── Adjacency helpers ────────────────────────────────────────────────────

    def _build_adjacency(self):
        self._adj_out = {nid: [] for nid in self.nodes}
        self._adj_in  = {nid: [] for nid in self.nodes}
        for edge in self.edges:
            self._adj_out.setdefault(edge.source_id, []).append(edge)
            self._adj_in.setdefault(edge.target_id, []).append(edge)

    def get_prerequisites(self, skill_id: int) -> List[int]:
        """All skills that must be learned before this one."""
        if self._adj_in is None:
            self._build_adjacency()
        return [e.source_id for e in self._adj_in.get(skill_id, [])]

    def get_dependents(self, skill_id: int) -> List[int]:
        """All skills unlocked by mastering this one."""
        if self._adj_out is None:
            self._build_adjacency()
        return [e.target_id for e in self._adj_out.get(skill_id, [])]

    def get_edge(self, source_id: int, target_id: int) -> Optional[SkillEdge]:
        for e in self.edges:
            if e.source_id == source_id and e.target_id == target_id:
                return e
        return None

    def stats(self) -> dict:
        return {
            "total_skills": len(self.nodes),
            "total_edges":  len(self.edges),
            "categories":   list({n.category for n in self.nodes.values()}),
        }

    # ── Serialization ────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "nodes": {
                str(sid): asdict(node)
                for sid, node in self.nodes.items()
            },
            "edges": [asdict(e) for e in self.edges],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SkillGraph":
        nodes = {
            int(sid): SkillNode(**node_data)
            for sid, node_data in data["nodes"].items()
        }
        edges = [SkillEdge(**e) for e in data["edges"]]
        return cls(nodes=nodes, edges=edges)

    def save(self, filepath: str):
        """Persist graph to a JSON cache file."""
        import os
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        logger.info("Graph saved → %s  (%d nodes, %d edges)",
                    filepath, len(self.nodes), len(self.edges))

    @classmethod
    def load(cls, filepath: str) -> "SkillGraph":
        """Load graph from a JSON cache file."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        graph = cls.from_dict(data)
        logger.info("Graph loaded ← %s  (%d nodes, %d edges)",
                    filepath, len(graph.nodes), len(graph.edges))
        return graph

    # ── PostgreSQL loaders ───────────────────────────────────────────────────

    @classmethod
    def load_from_db(cls, conn) -> "SkillGraph":
        """
        Load the skill graph from DELPHOS PostgreSQL.

        Reads:
          habilidades_catalogo        → SkillNode objects
          grafo_habilidades_aristas   → SkillEdge objects
        """
        try:
            from db import get_cursor
        except ImportError:
            raise RuntimeError("db.py must be in the same directory as graph_schema.py")

        with get_cursor(conn) as cur:
            # ── Nodes ──────────────────────────────────────────────────────
            cur.execute("""
                SELECT id, nombre, categoria, dificultad_nivel, horas_estimadas
                FROM habilidades_catalogo
                WHERE esta_activo = TRUE
            """)
            nodes = {
                row["id"]: SkillNode(
                    skill_id=row["id"],
                    skill_name=row["nombre"],
                    category=row["categoria"],
                    difficulty_level=float(row["dificultad_nivel"] or 0.5),
                    estimated_learning_hours=float(row["horas_estimadas"] or 20.0),
                )
                for row in cur.fetchall()
            }

            # ── Edges ──────────────────────────────────────────────────────
            cur.execute("""
                SELECT habilidad_origen_id, habilidad_destino_id,
                       peso, maestria_requerida, COALESCE(justificacion, '') AS justificacion
                FROM grafo_habilidades_aristas
                WHERE esta_activo = TRUE
            """)
            edges = [
                SkillEdge(
                    source_id=row["habilidad_origen_id"],
                    target_id=row["habilidad_destino_id"],
                    weight=float(row["peso"]),
                    required_mastery=float(row["maestria_requerida"]),
                    rationale=row["justificacion"],
                )
                for row in cur.fetchall()
            ]

        graph = cls(nodes=nodes, edges=edges)
        logger.info("Graph loaded from DB — %d nodes, %d edges", len(nodes), len(edges))
        return graph

    def save_to_db(self, conn):
        """
        Upsert the current in-memory graph to PostgreSQL.
        Safe to run multiple times (idempotent).
        """
        try:
            from db import get_cursor
        except ImportError:
            raise RuntimeError("db.py must be in the same directory as graph_schema.py")

        with get_cursor(conn, dict_cursor=False) as cur:
            # ── Upsert nodes ───────────────────────────────────────────────
            for node in self.nodes.values():
                cur.execute("""
                    INSERT INTO habilidades_catalogo
                        (nombre, slug, categoria, dificultad_nivel, horas_estimadas, esta_activo)
                    VALUES (%s, %s, %s, %s, %s, TRUE)
                    ON CONFLICT (nombre) DO UPDATE
                        SET dificultad_nivel = EXCLUDED.dificultad_nivel,
                            horas_estimadas  = EXCLUDED.horas_estimadas,
                            actualizado_en   = NOW()
                """, (
                    node.skill_name,
                    node.skill_name.replace("_", "-"),
                    node.category,
                    node.difficulty_level,
                    node.estimated_learning_hours,
                ))

            # ── Build name → DB id lookup ──────────────────────────────────
            cur.execute("SELECT id, nombre FROM habilidades_catalogo")
            name_to_id = {row[1]: row[0] for row in cur.fetchall()}

            # ── Upsert edges ───────────────────────────────────────────────
            inserted = skipped = 0
            for edge in self.edges:
                src = name_to_id.get(self.nodes[edge.source_id].skill_name)
                tgt = name_to_id.get(self.nodes[edge.target_id].skill_name)
                if not src or not tgt:
                    skipped += 1
                    continue
                cur.execute("""
                    INSERT INTO grafo_habilidades_aristas
                        (habilidad_origen_id, habilidad_destino_id,
                         peso, maestria_requerida, justificacion)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (habilidad_origen_id, habilidad_destino_id) DO NOTHING
                """, (src, tgt, edge.weight, edge.required_mastery, edge.rationale))
                inserted += 1

        logger.info("Graph saved to DB — %d nodes, %d edges (%d skipped)",
                    len(self.nodes), inserted, skipped)
