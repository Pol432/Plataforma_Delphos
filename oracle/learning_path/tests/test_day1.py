"""
tests/test_day1.py — Day 1 unit tests: graph schema + builder

Run:
    python -m pytest tests/test_day1.py -v
    # or from project root:
    python tests/test_day1.py
"""

import sys
import os
import json
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from learning_path.core.graph_schema import SkillNode, SkillEdge, SkillGraph
from learning_path.core.build_initial_graph import create_foundational_graph


class TestSkillNode(unittest.TestCase):

    def test_valid_node(self):
        node = SkillNode(1, "python", "technical", 0.4, 40.0)
        self.assertEqual(node.skill_id, 1)
        self.assertEqual(node.skill_name, "python")

    def test_difficulty_out_of_range(self):
        with self.assertRaises(AssertionError):
            SkillNode(1, "test", "technical", 1.5, 10.0)

    def test_negative_hours(self):
        with self.assertRaises(AssertionError):
            SkillNode(1, "test", "technical", 0.5, -1.0)


class TestSkillEdge(unittest.TestCase):

    def test_valid_edge(self):
        edge = SkillEdge(1, 2, 0.35, 50.0, "Test rationale")
        self.assertEqual(edge.source_id, 1)
        self.assertEqual(edge.target_id, 2)

    def test_self_loop_rejected(self):
        with self.assertRaises(AssertionError):
            SkillEdge(1, 1, 0.5, 50.0, "Self-loop")

    def test_weight_out_of_range(self):
        with self.assertRaises(AssertionError):
            SkillEdge(1, 2, 1.5, 50.0, "Bad weight")


class TestSkillGraph(unittest.TestCase):

    def setUp(self):
        self.graph = create_foundational_graph()

    def test_node_count(self):
        self.assertEqual(len(self.graph.nodes), 100,
                         f"Expected 100 nodes, got {len(self.graph.nodes)}")

    def test_edge_count(self):
        self.assertGreater(len(self.graph.edges), 40,
                           "Expected at least 40 prerequisite edges")

    def test_categories_present(self):
        cats = {n.category for n in self.graph.nodes.values()}
        self.assertIn("foundational", cats)
        self.assertIn("technical", cats)
        self.assertIn("creative", cats)
        self.assertIn("business", cats)

    def test_get_prerequisites(self):
        # python (31) requires analytical_thinking (1) and problem_solving (2)
        prereqs = self.graph.get_prerequisites(31)
        self.assertIn(1, prereqs, "analytical_thinking should be a prereq of python")
        self.assertIn(2, prereqs, "problem_solving should be a prereq of python")

    def test_get_dependents(self):
        # python (31) should unlock pandas (41), numpy (42), etc.
        deps = self.graph.get_dependents(31)
        self.assertIn(41, deps, "pandas should depend on python")
        self.assertIn(42, deps, "numpy should depend on python")

    def test_no_self_loops(self):
        self_loops = [e for e in self.graph.edges if e.source_id == e.target_id]
        self.assertEqual(len(self_loops), 0, "Graph contains self-loops!")

    def test_no_orphan_edges(self):
        orphans = [
            e for e in self.graph.edges
            if e.source_id not in self.graph.nodes or e.target_id not in self.graph.nodes
        ]
        self.assertEqual(len(orphans), 0,
                         f"{len(orphans)} edges reference non-existent nodes")

    def test_all_difficulties_in_range(self):
        for node in self.graph.nodes.values():
            self.assertGreaterEqual(node.difficulty_level, 0.0)
            self.assertLessEqual(node.difficulty_level, 1.0)


class TestSkillGraphSerialization(unittest.TestCase):

    def setUp(self):
        self.graph = create_foundational_graph()

    def test_to_dict_and_back(self):
        d = self.graph.to_dict()
        restored = SkillGraph.from_dict(d)
        self.assertEqual(len(restored.nodes), len(self.graph.nodes))
        self.assertEqual(len(restored.edges), len(self.graph.edges))

    def test_save_and_load_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test_graph.json")
            self.graph.save(path)
            self.assertTrue(os.path.exists(path))

            loaded = SkillGraph.load(path)
            self.assertEqual(len(loaded.nodes), 100)
            self.assertEqual(
                loaded.nodes[31].skill_name,
                self.graph.nodes[31].skill_name,
            )

    def test_json_is_valid(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test_graph.json")
            self.graph.save(path)
            with open(path) as f:
                data = json.load(f)
            self.assertIn("nodes", data)
            self.assertIn("edges", data)
            self.assertEqual(len(data["nodes"]), 100)


if __name__ == "__main__":
    print("\nRunning Day 1 Tests...\n")
    unittest.main(verbosity=2)
