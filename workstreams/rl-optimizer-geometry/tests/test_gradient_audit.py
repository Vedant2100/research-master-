"""Unit tests for arithmetic only, not RL evidence."""
import sys
import unittest
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "diagnostics"))
from gradient_audit import summarize_pair


class TestGradientAudit(unittest.TestCase):
    def test_identical(self):
        m = summarize_pair(np.eye(4), np.eye(4))
        self.assertAlmostEqual(m["split_half_cosine"], 1.0)
        self.assertAlmostEqual(m["normalized_disagreement"], 0.0)
        self.assertAlmostEqual(m["mean_gradient_stable_rank"], 4.0)
        self.assertAlmostEqual(m["bottom_half_singular_energy_fraction"], 0.5)

    def test_orthogonal(self):
        x = np.array([[1., 0.], [0., 0.]])
        y = np.array([[0., 0.], [0., 1.]])
        self.assertAlmostEqual(summarize_pair(x, y)["split_half_cosine"], 0.)

    def test_zero(self):
        m = summarize_pair(np.zeros((2, 3)), np.zeros((2, 3)))
        self.assertEqual(m["mean_gradient_stable_rank"], 0.)
        self.assertEqual(m["split_half_cosine"], 0.)

    def test_bad_inputs(self):
        with self.assertRaises(ValueError): summarize_pair(np.ones((2, 2)), np.ones((2, 3)))
        with self.assertRaises(ValueError): summarize_pair(np.ones((2,)), np.ones((2,)))
        with self.assertRaises(ValueError): summarize_pair(np.array([[np.inf]]), np.zeros((1,1)))


if __name__ == "__main__":
    unittest.main()
