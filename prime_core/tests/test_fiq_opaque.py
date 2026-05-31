"""Test 2 (handoff §4) — the opaque host round-trips losslessly.

A scalar grafted into a fiq, then retrieved from a circle anchor, is the exact
object inserted: the UCNS carrier wraps but does not interpret or re-encode.
"""
import unittest

from prime_core import build_core, compose_circle, wrap_tensor_fiq
from prime_core.core import CoreSpec
from prime_core.fiq import Scalar


class TestOpaqueHost(unittest.TestCase):
    def test_payload_roundtrip_identity(self):
        s0, s1, s2 = Scalar(0.5), Scalar(-1.25), Scalar(3.0)
        fiq = wrap_tensor_fiq([s0, s1, s2], anchor=0)
        # Same objects come back out — wrapping is lossless and non-copying.
        self.assertIs(fiq.payload[0], s0)
        self.assertIs(fiq.payload[1], s1)
        self.assertIs(fiq.payload[2], s2)

    def test_float_values_preserved(self):
        fiq = wrap_tensor_fiq([0.1, 0.2, 0.3], anchor=4)
        self.assertEqual([sc.data for sc in fiq.payload], [0.1, 0.2, 0.3])
        self.assertTrue(all(isinstance(sc, Scalar) for sc in fiq.payload))

    def test_retrieval_from_circle_anchor(self):
        fiqs = [wrap_tensor_fiq([float(i)], anchor=i) for i in range(7)]
        circle = compose_circle(fiqs)
        for i in range(7):
            retrieved = circle.at(i)
            self.assertIs(retrieved, fiqs[i])
            self.assertEqual(retrieved.payload[0].data, float(i))

    def test_carrier_does_not_mutate_payload(self):
        core = build_core(CoreSpec(seed_count=1, circles_per_seed=1,
                                   tensors_per_circle=3, tensor_dim=4), init=2.0)
        for fiq in core.tensor_leaves():
            self.assertEqual([sc.data for sc in fiq.payload], [2.0, 2.0, 2.0, 2.0])


if __name__ == "__main__":
    unittest.main()
