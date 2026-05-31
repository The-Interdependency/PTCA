"""Test 5 (handoff §4) — coherence-prime guard for the seed count.

Per §6 the seed count is a *design choice*, not a hard invariant, so this test
is parameterized: both 53 and 157 must pass the membership test, and reverting
SEED_COUNT to 53 must keep the suite green. If the decision is later changed to
'hard invariant', tighten ``test_seed_count_is_coherence_prime`` to assert
membership of the live SEED_COUNT unconditionally.
"""
import unittest

from prime_core.constants import SEED_COUNT, TENSOR_DIM, is_coherence_prime


class TestCoherencePrimeGuard(unittest.TestCase):
    def test_53_and_157_are_coherence_primes(self):
        # 53: (53-1)/4 = 13 in C. 157: (157-1)/4 = 39 = {3,13}, square-free, in C.
        self.assertTrue(is_coherence_prime(53))
        self.assertTrue(is_coherence_prime(157))

    def test_ladder_membership(self):
        # Coherence primes on the ladder satisfying p ≡ 1 mod 4.
        for p in (5, 13, 29, 53, 61, 157, 349, 421):
            self.assertTrue(is_coherence_prime(p), f"{p} should be a coherence prime")

    def test_rejects_non_coherence_primes(self):
        self.assertFalse(is_coherence_prime(3))    # 3 ≡ 3 mod 4
        self.assertFalse(is_coherence_prime(7))    # 7 ≡ 3 mod 4
        self.assertFalse(is_coherence_prime(17))   # (17-1)/4 = 4 not square-free
        self.assertFalse(is_coherence_prime(9))    # not prime
        self.assertFalse(is_coherence_prime(101))  # (101-1)/4 = 25 = 5*5 not square-free

    def test_seed_count_is_coherence_prime(self):
        # Design-choice mode: SEED_COUNT is tunable but must land on the ladder.
        self.assertIn(SEED_COUNT, (53, 157))
        self.assertTrue(is_coherence_prime(SEED_COUNT))

    def test_tensor_dim_is_coherence_prime(self):
        # d = 53 was chosen partly because it is itself a coherence prime.
        self.assertEqual(TENSOR_DIM, 53)
        self.assertTrue(is_coherence_prime(TENSOR_DIM))


if __name__ == "__main__":
    unittest.main()
