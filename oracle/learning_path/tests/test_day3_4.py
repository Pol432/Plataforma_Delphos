"""tests/test_day3_4.py — Gap analysis, urgency, efficiency, and priority tests."""
import sys, os, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from learning_path.core.graph_schema import SkillGraph
from learning_path.core.graph_converter import to_networkx
from learning_path.careers.career_database import get_career_requirements, get_critical_skills
from learning_path.engine.gap_analyzer import calculate_gaps, gaps_only, is_career_ready, career_readiness_pct
from learning_path.engine.urgency_calculator import calculate_urgency, calculate_all_urgencies
from learning_path.engine.efficiency_ranker import calculate_efficiency
from learning_path.engine.priority_scorer import calculate_priorities, top_skills_to_learn
from config import SKILL_GRAPH_PATH

MARIA_SKILLS = {71: 72.0, 5: 76.0, 1: 65.0, 3: 74.0, 15: 60.0}


class TestGapAnalyzer(unittest.TestCase):

    def setUp(self):
        self.graph    = SkillGraph.load(SKILL_GRAPH_PATH)
        self.reqs     = get_career_requirements("ux-designer")
        self.critical = get_critical_skills("ux-designer")
        self.gaps     = calculate_gaps(MARIA_SKILLS, self.reqs, self.graph, self.critical)

    def test_gaps_returned_for_all_career_skills(self):
        self.assertEqual(len(self.gaps), len(self.reqs))

    def test_met_skill_has_zero_gap(self):
        # visual_design (71): Maria has 72, required 65 → gap = 0
        gap_71 = next(g for g in self.gaps if g.skill_id == 71)
        self.assertEqual(gap_71.gap, 0.0)

    def test_missing_skill_has_positive_gap(self):
        # ux_design (73): Maria has 0, required 85 → gap = 85
        gap_73 = next(g for g in self.gaps if g.skill_id == 73)
        self.assertEqual(gap_73.gap, 85.0)

    def test_not_career_ready(self):
        self.assertFalse(is_career_ready(self.gaps))

    def test_gaps_only_excludes_met_skills(self):
        only = gaps_only(self.gaps)
        self.assertTrue(all(g.gap > 0 for g in only))

    def test_readiness_between_0_and_100(self):
        pct = career_readiness_pct(self.gaps)
        self.assertGreater(pct, 0)
        self.assertLess(pct, 100)

    def test_critical_skills_flagged(self):
        critical_gaps = [g for g in self.gaps if g.is_critical]
        self.assertEqual(len(critical_gaps), 3)   # ux_design, user_research, prototyping


class TestUrgencyCalculator(unittest.TestCase):

    def setUp(self):
        self.graph    = SkillGraph.load(SKILL_GRAPH_PATH)
        self.reqs     = get_career_requirements("ux-designer")
        self.critical = get_critical_skills("ux-designer")
        self.gaps     = calculate_gaps(MARIA_SKILLS, self.reqs, self.graph, self.critical)

    def test_critical_skill_urgency_is_1(self):
        gap_73 = next(g for g in self.gaps if g.skill_id == 73)
        self.assertTrue(gap_73.is_critical and gap_73.gap > 0)
        self.assertEqual(calculate_urgency(gap_73), 1.0)

    def test_met_skill_urgency_is_0(self):
        gap_71 = next(g for g in self.gaps if g.skill_id == 71)
        self.assertEqual(calculate_urgency(gap_71), 0.0)

    def test_all_urgencies_between_0_and_1(self):
        urgencies = calculate_all_urgencies(self.gaps)
        for uid, val in urgencies.items():
            self.assertGreaterEqual(val, 0.0)
            self.assertLessEqual(val, 1.0)


class TestEfficiencyRanker(unittest.TestCase):

    def setUp(self):
        self.graph    = SkillGraph.load(SKILL_GRAPH_PATH)
        self.nx_graph = to_networkx(self.graph)

    def test_returns_scores_for_all_nodes(self):
        scores = calculate_efficiency(self.graph, MARIA_SKILLS, self.nx_graph)
        self.assertEqual(len(scores), len(self.graph.nodes))

    def test_all_scores_positive(self):
        scores = calculate_efficiency(self.graph, MARIA_SKILLS, self.nx_graph)
        self.assertTrue(all(v >= 0 for v in scores.values()))

    def test_gateway_skills_score_higher(self):
        scores = calculate_efficiency(self.graph, MARIA_SKILLS, self.nx_graph)
        # python (31) should score higher than figma (81) — more dependents
        self.assertGreater(scores[31], scores[81])


class TestPriorityScorer(unittest.TestCase):

    def setUp(self):
        self.graph    = SkillGraph.load(SKILL_GRAPH_PATH)
        self.nx_graph = to_networkx(self.graph)
        reqs          = get_career_requirements("ux-designer")
        critical      = get_critical_skills("ux-designer")
        gaps          = calculate_gaps(MARIA_SKILLS, reqs, self.graph, critical)
        urgencies     = calculate_all_urgencies(gaps)
        efficiency    = calculate_efficiency(self.graph, MARIA_SKILLS, self.nx_graph)
        self.priorities = calculate_priorities(gaps, efficiency, urgencies)

    def test_priority_count_matches_career_skills(self):
        reqs = get_career_requirements("ux-designer")
        self.assertEqual(len(self.priorities), len(reqs))

    def test_first_priority_has_highest_score(self):
        scores = [p.priority for p in self.priorities]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_met_skills_have_zero_priority(self):
        for p in self.priorities:
            if p.gap == 0:
                self.assertEqual(p.priority, 0.0)

    def test_top_skills_to_learn(self):
        top = top_skills_to_learn(self.priorities, n=3)
        self.assertEqual(len(top), 3)
        self.assertTrue(all(p.gap > 0 for p in top))

    def test_critical_skill_appears_in_top_3(self):
        top3 = top_skills_to_learn(self.priorities, n=3)
        top3_ids = {p.skill_id for p in top3}
        critical = set(get_critical_skills("ux-designer"))
        self.assertTrue(top3_ids & critical,
                        "No critical skills in top-3 — priority scoring may be off")


if __name__ == "__main__":
    unittest.main(verbosity=2)
