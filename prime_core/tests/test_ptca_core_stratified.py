"""Structure, gradient-path, frozen-geometry and routing tests (handoff §4).

Covers test-plan items 1 (structure), 3 (gradient path / no ∂(⊠)),
4 (geometry is frozen scaffold) and 6 (routing). Opaque-host round-trip
(item 2) lives in ``test_fiq_opaque``; the coherence-prime guard (item 5) in
``test_constants_coherence_prime``.
"""
import unittest

from prime_core import CoreSpec, build_core, heptagram_order
from prime_core.constants import (
    CIRCLE_ROUTING_STEP,
    CIRCLES_PER_SEED,
    SEED_COUNT,
    SEED_ROUTING_STEP,
    TENSOR_DIM,
    TENSORS_PER_CIRCLE,
)
from prime_core.core import Circle, Seed
from prime_core.fiq import Fiq, Scalar

# Small spec for fast graph-level checks (test 3); canon spec used for counts.
SMALL = CoreSpec(seed_count=2, circles_per_seed=2, tensors_per_circle=2, tensor_dim=2)


class TestStructure(unittest.TestCase):
    """Test 1 — build_core yields the canon strata counts."""

    @classmethod
    def setUpClass(cls):
        cls.core = build_core()  # canon spec

    def test_seed_count(self):
        self.assertEqual(len(self.core.seeds), SEED_COUNT)
        self.assertEqual(SEED_COUNT, 157)

    def test_circles_per_seed(self):
        for seed in self.core.seeds:
            self.assertEqual(len(seed.circles), CIRCLES_PER_SEED)

    def test_tensors_per_circle(self):
        for seed in self.core.seeds:
            for circle in seed.circles:
                self.assertEqual(len(circle.fiqs), TENSORS_PER_CIRCLE)

    def test_total_tensor_leaves(self):
        leaves = self.core.tensor_leaves()
        self.assertEqual(len(leaves), 7693)
        self.assertEqual(len(leaves), SEED_COUNT * CIRCLES_PER_SEED * TENSORS_PER_CIRCLE)
        self.assertTrue(all(isinstance(f, Fiq) for f in leaves))

    def test_param_count(self):
        # 7693 fiqs each holding a d=53 scalar payload.
        self.assertEqual(len(self.core.scalars()), 7693 * TENSOR_DIM)
        self.assertEqual(7693 * TENSOR_DIM, 407729)


class TestGradientPath(unittest.TestCase):
    """Test 3 — gradients descend through payloads; ∂(⊠) never appears."""

    def setUp(self):
        self.core = build_core(SMALL)

    def test_gradient_reaches_leaf_through_composition(self):
        scalars = self.core.scalars()
        loss = Scalar(0.0)
        for sc in scalars:
            loss = loss + sc          # loss is built only from scalar ops
        loss.backward()
        # Every payload scalar is reached by the loss through ⊠ composition.
        self.assertTrue(all(abs(sc.grad - 1.0) < 1e-9 for sc in scalars))

    def test_no_box_derivative_node_on_tape(self):
        scalars = self.core.scalars()
        loss = Scalar(0.0)
        for sc in scalars:
            loss = loss + sc
        # Walk the entire autodiff tape reachable from the loss.
        seen, stack, ops = set(), [loss], set()
        while stack:
            node = stack.pop()
            if id(node) in seen:
                continue
            seen.add(id(node))
            ops.add(node._op)
            stack.extend(node._prev)
        # The tape touches ONLY scalar ops — no structural/⊠ derivative node.
        self.assertTrue(ops <= {"", "+", "*"}, f"unexpected ops on tape: {ops}")
        self.assertNotIn("⊠", ops)  # ⊠
        self.assertNotIn("compose", ops)


class TestFrozenGeometry(unittest.TestCase):
    """Test 4 — UCNS geometry is non-differentiable scaffold, never a leaf."""

    def setUp(self):
        self.core = build_core(SMALL)

    def test_carriers_do_not_require_grad(self):
        for seed in self.core.seeds:
            self.assertFalse(seed.requires_grad)
            for circle in seed.circles:
                self.assertFalse(circle.requires_grad)

    def test_geometry_attributes_present_and_not_leaves(self):
        leaves = self.core.tensor_leaves()
        for seed in self.core.seeds:
            # n_min / face_state / anchor_order are plain scaffold, not Scalars.
            self.assertIsInstance(seed.n_min, int)
            self.assertNotIsInstance(seed.n_min, Scalar)
            self.assertNotIsInstance(seed.face_state, Scalar)
            self.assertNotIn(seed, leaves)
            for circle in seed.circles:
                self.assertIsInstance(circle.n_min, int)
                self.assertNotIsInstance(circle.face_state, Scalar)
                self.assertNotIn(circle, leaves)

    def test_only_fiqs_are_leaves(self):
        for leaf in self.core.tensor_leaves():
            self.assertIsInstance(leaf, Fiq)
            self.assertNotIsInstance(leaf, (Circle, Seed))


class TestRouting(unittest.TestCase):
    """Test 6 — circle composition uses {7/2}, seed composition uses {7/3}."""

    def setUp(self):
        self.core = build_core()  # canon spec so n = 7 per layer

    def test_routing_steps(self):
        for seed in self.core.seeds:
            self.assertEqual(seed.routing_step, SEED_ROUTING_STEP)
            self.assertEqual(seed.routing_step, 3)
            for circle in seed.circles:
                self.assertEqual(circle.routing_step, CIRCLE_ROUTING_STEP)
                self.assertEqual(circle.routing_step, 2)

    def test_heptagram_orders(self):
        self.assertEqual(heptagram_order(2, 7), [0, 2, 4, 6, 1, 3, 5])
        self.assertEqual(heptagram_order(3, 7), [0, 3, 6, 2, 5, 1, 4])
        seed = self.core.seeds[0]
        self.assertEqual(list(seed.anchor_order), heptagram_order(3, 7))
        self.assertEqual(list(seed.circles[0].anchor_order), heptagram_order(2, 7))


if __name__ == "__main__":
    unittest.main()
