"""Correctness and edge-case tests for all RMQ implementations."""

import importlib.util
import random
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src"


def load_class(name, filename, class_name):
    spec = importlib.util.spec_from_file_location(name, SOURCE / filename)
    if spec is None or spec.loader is None:
        raise ImportError("Could not load {}".format(filename))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, class_name)


APPROACHES = (
    ("Linear Scan", load_class("test_linear_scan", "01_linear_scan.py", "LinearScan")),
    ("Sparse Table", load_class("test_sparse_table", "02_sparse_table.py", "SparseTable")),
    ("Segment Tree", load_class("test_segment_tree", "03_segment_tree.py", "SegmentTree")),
)


class RangeMinimumTests(unittest.TestCase):
    def test_known_answers_and_boundary_ranges(self):
        values = [8, 5, 9, 3, 7, 6, 2, 4]
        for name, cls in APPROACHES:
            with self.subTest(approach=name):
                rmq = cls(values)
                self.assertEqual(rmq.query(0, 7), 2)
                self.assertEqual(rmq.query(1, 6), 2)
                self.assertEqual(rmq.query(0, 0), 8)
                self.assertEqual(rmq.query(7, 7), 4)
                self.assertEqual(rmq.query(0, 3), 3)
                self.assertEqual(rmq.query(4, 7), 2)

    def test_updates_at_both_ends_and_minimum_changes(self):
        for name, cls in APPROACHES:
            with self.subTest(approach=name):
                rmq = cls([4, 2, 9, 7, 3])
                rmq.update(0, -5)
                self.assertEqual(rmq.query(0, 4), -5)
                rmq.update(4, -8)
                self.assertEqual(rmq.query(0, 4), -8)
                rmq.update(4, 10)
                self.assertEqual(rmq.query(0, 4), -5)
                self.assertEqual(rmq.query(4, 4), 10)

    def test_non_power_of_two_and_adversarial_arrays(self):
        arrays = (
            [6],
            [1, 2, 3, 4, 5, 6, 7],
            [7, 6, 5, 4, 3, 2, 1],
            [5, 5, 5, 5, 5],
            [-9, -2, -15, -4, -8, -1, -3],
        )
        for name, cls in APPROACHES:
            for values in arrays:
                with self.subTest(approach=name, values=values):
                    rmq = cls(values)
                    for left in range(len(values)):
                        for right in range(left, len(values)):
                            self.assertEqual(rmq.query(left, right), min(values[left:right + 1]))

    def test_random_operations_match_brute_force(self):
        rng = random.Random(1729)
        for name, cls in APPROACHES:
            with self.subTest(approach=name):
                expected_values = [rng.randint(-100, 100) for _ in range(23)]
                rmq = cls(expected_values)
                for _ in range(100):
                    if rng.random() < 0.35:
                        index = rng.randrange(len(expected_values))
                        value = rng.randint(-100, 100)
                        expected_values[index] = value
                        rmq.update(index, value)
                    else:
                        left = rng.randrange(len(expected_values))
                        right = rng.randrange(left, len(expected_values))
                        self.assertEqual(
                            rmq.query(left, right),
                            min(expected_values[left:right + 1]),
                        )

    def test_invalid_ranges_and_updates_are_rejected(self):
        for name, cls in APPROACHES:
            with self.subTest(approach=name):
                rmq = cls([3, 1, 4])
                for left, right in ((-1, 1), (0, 3), (2, 1), (3, 3)):
                    with self.subTest(range=(left, right)):
                        with self.assertRaises(ValueError):
                            rmq.query(left, right)
                for index in (-1, 3):
                    with self.subTest(index=index):
                        with self.assertRaises(IndexError):
                            rmq.update(index, 0)

    def test_empty_input_is_rejected(self):
        for name, cls in APPROACHES:
            with self.subTest(approach=name):
                with self.assertRaises(ValueError):
                    cls([])

    def test_constructor_does_not_mutate_caller_array(self):
        values = [3, -1, 6, 2, 9]
        original = values.copy()
        for name, cls in APPROACHES:
            with self.subTest(approach=name):
                cls(values)
                self.assertEqual(values, original)


if __name__ == "__main__":
    unittest.main()
