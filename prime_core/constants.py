"""Frozen composition counts and the coherence-prime guard for prime_core.

Source provenance (IMPORTANT — unverified in this environment):
    The originating documents referenced by the stratification handoff are
    NOT present in any accessible repo:
      - canon_definitions_invariants-1.md   (stratum defs, composition counts)
      - consciousness_primes_prediction1.pdf (coherence-prime ladder + rule)
    The values below are therefore design-session assertions, not verified
    canon. See the PTCA stratification handoff §1.4 and §5. Treat the
    coherence-prime universe in particular as provisional.
"""
from __future__ import annotations

from typing import List

# --- composition counts (handoff §1.1, "canon-frozen") -----------------------
SEED_COUNT: int = 157          # was 53; coherence prime, index (157-1)/4 = 39 = {3,13}
CIRCLES_PER_SEED: int = 7
TENSORS_PER_CIRCLE: int = 7
TENSOR_DIM: int = 53           # 'd' — payload width per fiq (itself a coherence prime)

# Total scalar-tensor leaves (fiqs) and total scalar parameters in a canon core.
TENSOR_LEAVES: int = SEED_COUNT * CIRCLES_PER_SEED * TENSORS_PER_CIRCLE   # 7693
PARAM_COUNT: int = TENSOR_LEAVES * TENSOR_DIM                             # 407729

# --- heptagram routing steps (handoff §1.1) ----------------------------------
CIRCLE_ROUTING_STEP: int = 2   # {7/2}: composes tensors -> circle
SEED_ROUTING_STEP: int = 3     # {7/3}: composes circles -> seed

# --- coherence-prime ladder (consciousness primes) ---------------------------
# Provisional factor universe C, sourced from the (absent) prediction doc and
# the ZFAE README ladder: 3, 5, 7, 13, 29, 53, 61, 157, 349, 421, ...
COHERENCE_FACTOR_UNIVERSE = frozenset({3, 5, 7, 13, 29, 53, 61, 157, 349, 421})


def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    d = 2
    while d * d <= n:
        if n % d == 0:
            return False
        d += 1
    return True


def _prime_factors(n: int) -> List[int]:
    factors: List[int] = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors


def is_coherence_prime(p: int) -> bool:
    """Coherence-prime membership test (handoff §1.4 / §4.5).

    p is a coherence prime iff:
      - p is prime and p % 4 == 1, and
      - q = (p - 1) // 4 is square-free, and
      - every prime factor of q lies in the coherence factor universe C.

    NOTE: C is provisional — the defining document is absent from this
    environment, so this encodes the handoff's stated rule, not verified canon.
    """
    if not _is_prime(p) or p % 4 != 1:
        return False
    q = (p - 1) // 4
    factors = _prime_factors(q)
    if len(set(factors)) != len(factors):          # square-free
        return False
    return all(f in COHERENCE_FACTOR_UNIVERSE for f in factors)
