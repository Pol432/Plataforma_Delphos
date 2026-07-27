"""tests/test_day2.py — Career database + graph converter tests."""
import sys, os, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from learning_path.careers.career_database import (
    CAREERS, get_career_by_slug, get_career_requirements,
    get_critical_skills, list_slugs,
)
from learning_path.core.graph_schema import SkillGraph
from learning_path.core.graph_converter import to_networkx, to_adjacency_matrix, convert
from config import SKILL_GRAPH_PATH


class TestCareerDatabase(unittest.TestCase):

    def test_career_count(self):
        self.assertGreaterEqual(len(CAREERS), 10)

    def test_all_slugs_unique(self):
        slugs = list_slugs()
        self.assertEqual(len(slugs), len(set(slugs)))

    def test_get_career_by_slug(self):
        c = get_career_by_slug("ux-designer")
        self.assertEqual(c["slug"], "ux-designer")

    def test_unknown_slug_raises(self):
        with self.assertRaises(KeyError):
            get_career_by_slug("made-up-career")

    def test_requirements_are_valid_skill_ids(self):
        graph = SkillGraph.load(SKILL_GRAPH_PATH)
        valid = set(graph.nodes.keys())
        for career in CAREERS:
            for sid in career["requirements"]:
                self.assertIn(sid, valid,
                    f"Career '{career['slug']}' references unknown skill_id {sid}")

    def test_mastery_in_range(self):
        for career in CAREERS:
            for sid, (mastery, _) in career["requirements"].items():
                self.assertGreater(mastery, 0)
                self.assertLessEqual(mastery, 100)

    def test_critical_skills_subset(self):
        for career in CAREERS:
            critical = get_critical_skills(career["slug"])
            all_ids  = list(career["requirements"].keys())
            for sid in critical:
                self.assertIn(sid, all_ids)

    def test_ux_designer_has_3_critical(self):
        critical = get_critical_skills("ux-designer")
        self.assertEqual(len(critical), 3,
            f"UX Designer should have 3 critical skills, got {len(critical)}")


class TestGraphConverter(unittest.TestCase):

    def setUp(self):
        self.graph = SkillGraph.load(SKILL_GRAPH_PATH)

    def test_to_networkx(self):
        import networkx as nx
        G = to_networkx(self.graph)
        self.assertIsInstance(G, nx.DiGraph)
        self.assertEqual(G.number_of_nodes(), len(self.graph.nodes))
        self.assertEqual(G.number_of_edges(), len(self.graph.edges))

    def test_to_networkx_node_has_name(self):
        G = to_networkx(self.graph)
        self.assertIn("name", G.nodes[31])
        self.assertEqual(G.nodes[31]["name"], "python")

    def test_to_adjacency_matrix_shape(self):
        matrix, node_ids = to_adjacency_matrix(self.graph)
        n = len(self.graph.nodes)
        self.assertEqual(matrix.shape, (n, n))
        self.assertEqual(len(node_ids), n)

    def test_adjacency_matrix_nonzero(self):
        import numpy as np
        matrix, _ = to_adjacency_matrix(self.graph)
        self.assertEqual(int(np.count_nonzero(matrix)), len(self.graph.edges))

    def test_convert_returns_networkx_by_default(self):
        result = convert(self.graph)
        self.assertEqual(result["backend"], "networkx")
        self.assertIn("graph", result)
        self.assertIn("node_ids", result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
