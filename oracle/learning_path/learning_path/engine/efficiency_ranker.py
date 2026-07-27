"""
efficiency_ranker.py — PageRank-based skill efficiency scoring.

"Efficiency" measures how much unlocking power a skill has: mastering a
gateway skill (e.g. python) opens many downstream paths (pandas, numpy,
scikit-learn, …) while a leaf skill (e.g. tableau) opens very little.

Algorithm: Personalized PageRank via NumPy power iteration.
  - No scipy, no MindSpore, no external dependencies beyond numpy.
  - NetworkX is used only for graph structure (node/edge traversal),
    NOT for its nx.pagerank() call which requires scipy.

Backend selection (automatic):
  NumPy power iteration  ← always available, used by default
  NetworkX DiGraph       ← used as the graph format for traversal
"""

import sys
import os
import logging
from typing import Dict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import SKILL_GRAPH_PATH, DAMPING_FACTOR, PAGERANK_ITERATIONS, PAGERANK_TOLERANCE

logger = logging.getLogger("lpo.efficiency_ranker")

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    logger.warning("NetworkX not installed. Run: pip install networkx")


# ─────────────────────────────────────────────────────────────────────────────
#  Core: NumPy power-iteration PageRank (no scipy required)
# ─────────────────────────────────────────────────────────────────────────────

def _pagerank_numpy(
    matrix:        np.ndarray,        # (N, N) weighted adjacency
    node_ids:      list,
    user_skills:   Dict[int, float],  # {skill_id: mastery 0-100}
    damping:       float = DAMPING_FACTOR,
    max_iter:      int   = PAGERANK_ITERATIONS,
    tolerance:     float = PAGERANK_TOLERANCE,
) -> Dict[int, float]:
    """
    Personalized PageRank via power iteration.

    P[i][j] = edge weight from node i → node j (row-normalized).
    Personalization vector biased toward skills the user already knows.

    Returns {skill_id: score}.
    """
    n   = len(node_ids)
    idx = {nid: i for i, nid in enumerate(node_ids)}

    # Row-normalize to get transition probability matrix
    row_sums = matrix.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1.0          # avoid division by zero (dangling nodes)
    P = (matrix / row_sums).astype(np.float64)

    # Build personalization vector: weight known skills proportional to mastery
    personal = np.zeros(n, dtype=np.float64)
    for skill_id, mastery in user_skills.items():
        i = idx.get(skill_id)
        if i is not None:
            personal[i] = max(0.0, mastery) / 100.0

    total = personal.sum()
    if total > 0:
        personal /= total
    else:
        personal[:] = 1.0 / n   # uniform if user has no known skills

    # Power iteration:  r = d * P^T r  +  (1-d) * personal
    r = personal.copy()
    for iteration in range(max_iter):
        r_new = damping * (P.T @ r) + (1.0 - damping) * personal
        delta = np.abs(r_new - r).max()
        r = r_new
        if delta < tolerance:
            logger.debug("PageRank converged after %d iterations (delta=%.2e)", iteration + 1, delta)
            break
    else:
        logger.debug("PageRank reached max_iter=%d (final delta=%.2e)", max_iter, delta)

    return {node_ids[i]: float(r[i]) for i in range(n)}


# ─────────────────────────────────────────────────────────────────────────────
#  Public API
# ─────────────────────────────────────────────────────────────────────────────

def calculate_efficiency(
    graph,                            # SkillGraph
    user_skills:  Dict[int, float],   # {skill_id: mastery 0-100}
    nx_graph=None,                    # optional pre-built nx.DiGraph (ignored for PageRank)
) -> Dict[int, float]:
    """
    Calculate PageRank efficiency scores for all skills.

    Uses pure NumPy power iteration — no scipy, no MindSpore required.
    Returns {skill_id: score}  (higher = more gateway / unlocking value).
    """
    from learning_path.core.graph_converter import to_adjacency_matrix

    matrix, node_ids = to_adjacency_matrix(graph)
    logger.info("Running NumPy PageRank — %d nodes, damping=%.2f", len(node_ids), DAMPING_FACTOR)

    return _pagerank_numpy(matrix, node_ids, user_skills)


# ─────────────────────────────────────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    from learning_path.core.graph_schema import SkillGraph
    from learning_path.core.graph_converter import to_networkx

    print("\nDELPHOS LPO — Efficiency Ranker\n")

    graph    = SkillGraph.load(SKILL_GRAPH_PATH)
    maria_skills = {71: 72.0, 5: 76.0, 1: 65.0, 3: 74.0, 15: 60.0}

    scores = calculate_efficiency(graph, maria_skills)

    # Top-15 most efficient gateway skills
    top = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:15]
    print(f"  Top 15 gateway skills (PageRank efficiency):\n")
    print(f"  {'#':>3}  {'Skill':<28} {'Score':>10}  Category")
    print("  " + "─" * 60)
    for rank, (skill_id, score) in enumerate(top, 1):
        node = graph.nodes.get(skill_id)
        name = node.skill_name if node else f"skill_{skill_id}"
        cat  = node.category   if node else "?"
        print(f"  {rank:>3}. {name:<28} {score:>10.6f}  {cat}")

    print(f"\n  Backend : NumPy power iteration (no scipy/MindSpore needed)")
    print(f"  Damping : {DAMPING_FACTOR}  |  Max iter : {PAGERANK_ITERATIONS}\n")


if __name__ == "__main__":
    main()
