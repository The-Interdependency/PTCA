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

# === MODULE_BUILD ===
# id: prime_core_constants
#   module_name: constants
#   module_kind: engine
#   summary: frozen PTCA composition counts plus the recursive coherence-prime guard
#   owner: Erin Spencer
#   public_surface: SEED_COUNT, CIRCLES_PER_SEED, TENSORS_PER_CIRCLE, TENSOR_DIM, TENSOR_LEAVES, PARAM_COUNT, CIRCLE_ROUTING_STEP, SEED_ROUTING_STEP, is_coherence_prime
#   internal_surface: _build_coherence_up_to, _is_prime, _prime_factors
#   auth_boundary: none
#   storage_boundary: none
#   network_boundary: none
#   user_data_boundary: none
#   admin_only: false
#   tests: prime_core.tests.test_constants_coherence_prime
#   rollout: default_enabled (imported by prime_core.core via prime_core.__init__)
#   rollback: revert is_coherence_prime to the prior frozen-universe implementation
#   requires: coherence_primes (mirrored from interdependent_lib, not imported — would invert the dependency graph)
#   since: 2026-06-02 (manifest added; module predates the doctrine)
#   unresolved: composition counts SEED_COUNT/TENSOR_DIM remain provisional pending the absent canon documents
# === END MODULE_BUILD ===

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
# The membership rule is *recursive*: a prime's kernel (p-1)//4 must factor only
# into earlier coherence primes (genealogical ancestry), not into a fixed
# pre-listed universe. The previous frozen-universe approximation (capped at
# 421) silently disagreed with this rule for the first time at p=4373, whose
# kernel 1093 is itself a coherence prime above the cap.
#
# CANON: the single source of truth for this sequence is
#   interdependent_lib.coherence_primes  (The-Interdependency/interdependent-lib)
# prime_core cannot import it — interdependent-lib optionally depends on
# ptca-lib, so importing the aggregator here would invert the dependency graph
# (and `ucns`/the canon package are not importable in this environment anyway).
# The recursive algorithm is therefore mirrored verbatim; behaviour MUST match
# canon, whose shared test oracle includes the p=4373 regression.
_COHERENCE_BASE = frozenset({3, 5, 7})
_coherence_known: set = set(_COHERENCE_BASE)
_coherence_scanned_to: int = max(_COHERENCE_BASE)


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


def _build_coherence_up_to(limit: int) -> None:
    """Admit every coherence prime ``<= limit`` in ascending order so the
    recursive ancestry check can consult the already-admitted set. Idempotent:
    ``_coherence_scanned_to`` guards against re-scanning."""
    global _coherence_scanned_to
    if limit <= _coherence_scanned_to:
        return
    for p in range(_coherence_scanned_to + 1, limit + 1):
        if not _is_prime(p) or p in _COHERENCE_BASE or (p - 1) % 4 != 0:
            continue
        factors = _prime_factors((p - 1) // 4)
        if len(set(factors)) != len(factors):          # square-free
            continue
        if set(factors) <= _coherence_known:           # recursive ancestry
            _coherence_known.add(p)
    _coherence_scanned_to = limit


def is_coherence_prime(p: int) -> bool:
    """Coherence-prime membership test (handoff §1.4 / §4.5).

    p is a coherence prime iff either:
      - p is in the base set {3, 5, 7}, or
      - p is prime, p % 4 == 1, q = (p - 1) // 4 is square-free, and every
        prime factor of q is itself a coherence prime (recursive).

    Mirrors ``interdependent_lib.coherence_primes`` exactly — see the CANON
    note above.
    """
    if p < 2:
        return False
    if p in _COHERENCE_BASE:
        return True
    if not _is_prime(p) or p % 4 != 1:
        return False
    _build_coherence_up_to(p)
    return p in _coherence_known
