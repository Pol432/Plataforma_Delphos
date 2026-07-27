"""tests/test_integration.py — Full end-to-end pipeline integration tests."""
import sys, os, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from learning_path.api import generate_path, get_current_task, complete_task

MARIA = {71: 72.0, 5: 76.0, 1: 65.0, 3: 74.0, 15: 60.0}


class TestFullPipeline(unittest.TestCase):

    def setUp(self):
        self.path   = generate_path("maria", "ux-designer", MARIA.copy())
        self.skills = MARIA.copy()

    def test_path_has_phases(self):
        self.assertGreater(len(self.path.phases), 0)

    def test_path_has_tasks(self):
        self.assertGreater(self.path.total_tasks, 0)

    def test_first_phase_is_unlocked(self):
        self.assertTrue(self.path.phases[0].unlocked)

    def test_subsequent_phases_locked(self):
        if len(self.path.phases) > 1:
            self.assertFalse(self.path.phases[1].unlocked)

    def test_get_current_task_returns_task(self):
        task = get_current_task(self.path)
        self.assertIsNotNone(task)
        self.assertGreater(task.estimated_minutes, 0)

    def test_high_score_gives_saltar_action(self):
        task = get_current_task(self.path)
        task.task_id = 1
        result = complete_task(self.path, task, 92, 25, self.skills)
        self.assertEqual(result.action, "saltar")
        self.assertGreater(result.xp_earned, 0)

    def test_low_score_gives_refuerzo_action(self):
        task = get_current_task(self.path)
        task.task_id = 1
        result = complete_task(self.path, task, 45, 40, self.skills)
        self.assertEqual(result.action, "refuerzo")

    def test_normal_score_gives_normal_action(self):
        task = get_current_task(self.path)
        task.task_id = 1
        result = complete_task(self.path, task, 72, 35, self.skills)
        self.assertEqual(result.action, "normal")

    def test_mastery_increases_after_completion(self):
        task   = get_current_task(self.path)
        task.task_id = 1
        before = self.skills.get(task.skill_id, 0.0)
        complete_task(self.path, task, 75, 30, self.skills)
        after  = self.skills.get(task.skill_id, 0.0)
        self.assertGreater(after, before)

    def test_path_generation_speed(self):
        import time
        start = time.perf_counter()
        generate_path("speed_test", "data-analyst", {33: 40.0, 36: 30.0})
        elapsed = time.perf_counter() - start
        self.assertLess(elapsed, 5.0, f"Path generation took {elapsed:.2f}s (limit: 5s)")

    def test_multiple_careers(self):
        for slug in ["ux-designer", "data-analyst", "frontend-developer", "ml-engineer"]:
            path = generate_path("test_user", slug, {})
            self.assertGreater(len(path.phases), 0, f"No phases for {slug}")

    def test_user_with_no_skills(self):
        path = generate_path("newbie", "ux-designer", {})
        self.assertGreater(len(path.phases), 0)
        self.assertTrue(path.phases[0].unlocked)

    def test_user_already_qualified(self):
        # User who already meets all requirements
        expert = {
            73: 90.0, 74: 85.0, 75: 80.0, 72: 75.0,
            71: 70.0, 81: 75.0, 85: 70.0, 3: 65.0, 1: 60.0, 15: 60.0
        }
        path = generate_path("expert", "ux-designer", expert)
        # Should generate 0 phases (no gaps)
        active_phases = [p for p in path.phases if p.mastery_gap > 0]
        self.assertEqual(len(active_phases), 0)


if __name__ == "__main__":
    print("\nRunning Integration Tests...\n")
    unittest.main(verbosity=2)
