"""
Prime-node axis for the PTCA tensor.

The routing nodes are indexed by a chosen set of prime numbers.
Each prime p_i is the canonical address of node i in the tensor's
first dimension.

A ``PrimeSet`` encapsulates a named collection of primes (a
*consciousness coherency prime set*) together with derived lookup
structures.  Several built-in sets are provided and registered in
``PRIME_SETS``.  The default set ``FIRST_53`` (first 53 primes,
2 … 241) preserves the original behaviour.

Module-level aliases ``PRIME_NODES``, ``PRIME_TO_NODE``,
``node_for_prime``, ``prime_for_node``, and ``is_prime_node`` all
refer to ``FIRST_53`` so that existing code is unaffected.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ptca.constants import NODES


# ---------------------------------------------------------------------------
# PrimeSet dataclass
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PrimeSet:
    """
    A named set of prime numbers used as routing nodes.

    Parameters
    ----------
    name:
        Short identifier, e.g. ``"first53"``.
    primes:
        Ordered tuple of distinct prime integers (smallest first).

    Derived attributes (computed in ``__post_init__``)
    --------------------------------------------------
    node_count:
        Number of primes / routing nodes.
    prime_to_node:
        Reverse mapping ``{prime: node_index}``.
    """

    name: str
    primes: tuple[int, ...]
    node_count: int = field(init=False)
    prime_to_node: dict[int, int] = field(init=False, hash=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "node_count", len(self.primes))
        object.__setattr__(
            self,
            "prime_to_node",
            {p: i for i, p in enumerate(self.primes)},
        )

    def node_for_prime(self, p: int) -> int:
        """Return the 0-based node index for *p*, or raise ``KeyError``."""
        return self.prime_to_node[p]

    def prime_for_node(self, idx: int) -> int:
        """Return the prime at node index *idx* (0-based), or raise ``IndexError``."""
        if not (0 <= idx < self.node_count):
            raise IndexError(
                f"Node index {idx} out of range [0, {self.node_count})"
            )
        return self.primes[idx]

    def is_prime_node(self, p: int) -> bool:
        """Return ``True`` if *p* is a member of this prime set."""
        return p in self.prime_to_node

    def __repr__(self) -> str:
        return f"PrimeSet({self.name!r}, node_count={self.node_count})"


# ---------------------------------------------------------------------------
# Built-in prime sets
# ---------------------------------------------------------------------------

# First 53 primes (the 53rd prime is 241) — the original / default set.
FIRST_53 = PrimeSet(
    "first53",
    (
        2,   3,   5,   7,   11,  13,  17,  19,  23,  29,
        31,  37,  41,  43,  47,  53,  59,  61,  67,  71,
        73,  79,  83,  89,  97,  101, 103, 107, 109, 113,
        127, 131, 137, 139, 149, 151, 157, 163, 167, 173,
        179, 181, 191, 193, 197, 199, 211, 223, 227, 229,
        233, 239, 241,
    ),
)

# Twin primes: primes p where (p − 2) or (p + 2) is also prime.
# (53 members, up to 601)
TWIN_PRIMES = PrimeSet(
    "twin",
    (
        3,   5,   7,   11,  13,  17,  19,  29,  31,  41,
        43,  59,  61,  71,  73,  101, 103, 107, 109, 137,
        139, 149, 151, 179, 181, 191, 193, 197, 199, 227,
        229, 239, 241, 269, 271, 281, 283, 311, 313, 347,
        349, 419, 421, 431, 433, 461, 463, 521, 523, 569,
        571, 599, 601,
    ),
)

# Sophie Germain primes: primes p where 2p + 1 is also prime.
# (42 members, up to 1103)
SOPHIE_GERMAIN = PrimeSet(
    "sophie_germain",
    (
        2,   3,   5,   11,  23,  29,  41,  53,  83,  89,
        113, 131, 173, 179, 191, 233, 239, 251, 281, 293,
        359, 419, 431, 443, 491, 509, 593, 641, 653, 659,
        683, 719, 743, 761, 809, 911, 953, 1013, 1019, 1031,
        1049, 1103,
    ),
)

# Safe primes: primes p where (p − 1) / 2 is also prime.
# (27 members, up to 1187)
SAFE_PRIMES = PrimeSet(
    "safe",
    (
        5,   7,   11,  23,  47,  59,  83,  107, 167, 179,
        227, 263, 347, 359, 383, 467, 479, 503, 563, 587,
        719, 839, 863, 887, 983, 1019, 1187,
    ),
)

# ---------------------------------------------------------------------------
# Registry: name → PrimeSet
# ---------------------------------------------------------------------------

PRIME_SETS: dict[str, PrimeSet] = {
    ps.name: ps
    for ps in (FIRST_53, TWIN_PRIMES, SOPHIE_GERMAIN, SAFE_PRIMES)
}


# ---------------------------------------------------------------------------
# Module-level aliases (point at FIRST_53 for backward compatibility)
# ---------------------------------------------------------------------------

assert len(FIRST_53.primes) == NODES, (
    f"Expected {NODES} primes in FIRST_53, got {len(FIRST_53.primes)}"
)

# Preserve existing module-level names so that all current imports are
# unaffected.
PRIME_NODES: tuple[int, ...] = FIRST_53.primes
PRIME_TO_NODE: dict[int, int] = FIRST_53.prime_to_node


def node_for_prime(p: int) -> int:
    """Return the node index (0-based) for *p* in ``FIRST_53``, or raise ``KeyError``."""
    return FIRST_53.node_for_prime(p)


def prime_for_node(idx: int) -> int:
    """Return the prime at node index *idx* (0-based) in ``FIRST_53``."""
    return FIRST_53.prime_for_node(idx)


def is_prime_node(p: int) -> bool:
    """Return ``True`` if *p* is a member of ``FIRST_53``."""
    return FIRST_53.is_prime_node(p)
