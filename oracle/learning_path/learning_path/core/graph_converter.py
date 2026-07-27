"""
graph_converter.py — Convert SkillGraph to matrix formats.

Two formats are produced:
  NetworkX DiGraph     — rich graph structure for traversal and inspection
  NumPy adjacency      — (N, N) float32 matrix used by PageRank

No scipy, no MindSpore required.
"""

import sys
import os
import logging
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import SKILL_GRAPH_PATH

logger = logging.getLogger("lpo.graph_converter")

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    logger.warning("NetworkX not installed. Run: pip install networkx")


# ─────────────────────────────────────────────────────────────────────────────
#  NetworkX converter — graph structure only (NOT used for PageRank)
# ─────────────────────────────────────────────────────────────────────────────

def to_networkx(graph) -> "nx.DiGraph":
    """
    Convert a SkillGraph to a NetworkX DiGraph.
    Nodes carry skill metadata; edges carry weight and required_mastery.
    Used for graph inspection, topology queries, and visualisation.
    PageRank is computed separately via NumPy (see efficiency_ranker.py).
    """
    if not NETWORKX_AVAILABLE:
        raise RuntimeError("networkx not installed. Run: pip install networkx")

    G = nx.DiGraph()

    for node in graph.nodes.values():
        G.add_node(
            node.skill_id,
            name=node.skill_name,
            category=node.category,
            difficulty=node.difficulty_level,
            hours=node.estimated_learning_hours,
        )

    for edge in graph.edges:
        G.add_edge(
            edge.source_id,
            edge.target_id,
            weight=edge.weight,
            required_mastery=edge.required_mastery,
            rationale=edge.rationale,
        )

    logger.debug("NetworkX DiGraph — %d nodes, %d edges",
                 G.number_of_nodes(), G.number_of_edges())
    return G


# ─────────────────────────────────────────────────────────────────────────────
#  NumPy adjacency matrix — used by PageRank
# ─────────────────────────────────────────────────────────────────────────────

def to_adjacency_matrix(graph) -> tuple:
    """
    Convert SkillGraph to a dense NumPy adjacency matrix.

    Returns:
        (matrix, node_id_list)
        matrix[i][j] = edge weight from node_id_list[i] → node_id_list[j]
                       (0.0 if no edge exists)
    """
    node_ids = sorted(graph.nodes.keys())
    idx      = {nid: i for i, nid in enumerate(node_ids)}
    n        = len(node_ids)
    matrix   = np.zeros((n, n), dtype=np.float32)

    for edge in graph.edges:
        i = idx.get(edge.source_id)
        j = idx.get(edge.target_id)
        if i is not None and j is not None:
            matrix[i][j] = edge.weight

    logger.debug("Adjacency matrix — shape %s, non-zero: %d",
                 matrix.shape, int(np.count_nonzero(matrix)))
    return matrix, node_ids


# ─────────────────────────────────────────────────────────────────────────────
#  Factory — returns best available representation
# ─────────────────────────────────────────────────────────────────────────────

def convert(graph, force_numpy: bool = False) -> dict:
    """
    Convert the skill graph to the best available format.

    Returns a dict with keys:
        backend  : 'networkx' | 'numpy'
        graph    : nx.DiGraph  or  np.ndarray
        node_ids : sorted list of skill_ids
    """
    if force_numpy or not NETWORKX_AVAILABLE:
        matrix, node_ids = to_adjacency_matrix(graph)
        return {"backend": "numpy", "graph": matrix, "node_ids": node_ids}

    G        = to_networkx(graph)
    node_ids = sorted(graph.nodes.keys())
    return {"backend": "networkx", "graph": G, "node_ids": node_ids}


# ─────────────────────────────────────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    from learning_path.core.graph_schema import SkillGraph

    print("\nDELPHOS LPO — Graph Converter\n")
    graph  = SkillGraph.load(SKILL_GRAPH_PATH)
    result = convert(graph)

    print(f"  Backend    : {result['backend']}")
    print(f"  Skills     : {len(result['node_ids'])}")

    if result["backend"] == "networkx":
        G = result["graph"]
        print(f"  Nodes      : {G.number_of_nodes()}")
        print(f"  Edges      : {G.number_of_edges()}")
        top5 = sorted(G.out_degree(), key=lambda x: x[1], reverse=True)[:5]
        print(f"\n  Top 5 skills by dependents unlocked:")
        for nid, deg in top5:
            print(f"    [{nid:>3}] {G.nodes[nid]['name']:<28} → unlocks {deg} skills")

    elif result["backend"] == "numpy":
        m = result["graph"]
        print(f"  Matrix     : {m.shape}")
        print(f"  Non-zero   : {int(np.count_nonzero(m))}")

    print()


if __name__ == "__main__":
    main()
