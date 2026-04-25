"""Tests for ptca.primes."""
import pytest
import ptca
from ptca.primes import (
    PRIME_NODES, node_for_prime, prime_for_node, is_prime_node,
    PrimeSet, PRIME_SETS,
    FIRST_53, TWIN_PRIMES, SOPHIE_GERMAIN, SAFE_PRIMES,
)


def test_prime_count():
    assert len(PRIME_NODES) == 53


def test_first_prime():
    assert PRIME_NODES[0] == 2


def test_last_prime():
    assert PRIME_NODES[52] == 241


def test_all_unique():
    assert len(set(PRIME_NODES)) == 53


def test_sorted_ascending():
    assert list(PRIME_NODES) == sorted(PRIME_NODES)


def test_node_for_prime_known():
    assert node_for_prime(2) == 0
    assert node_for_prime(3) == 1
    assert node_for_prime(241) == 52


def test_node_for_prime_unknown():
    with pytest.raises(KeyError):
        node_for_prime(4)  # not a prime node


def test_prime_for_node_known():
    assert prime_for_node(0) == 2
    assert prime_for_node(52) == 241


def test_prime_for_node_out_of_range():
    with pytest.raises(IndexError):
        prime_for_node(53)
    with pytest.raises(IndexError):
        prime_for_node(-1)


def test_is_prime_node():
    assert is_prime_node(2)
    assert is_prime_node(241)
    assert not is_prime_node(1)
    assert not is_prime_node(4)
    assert not is_prime_node(243)


def test_prime_nodes_exported():
    assert ptca.PRIME_NODES is PRIME_NODES


# ---------------------------------------------------------------------------
# PrimeSet dataclass
# ---------------------------------------------------------------------------

def test_prime_set_node_count():
    assert FIRST_53.node_count == 53
    assert TWIN_PRIMES.node_count == 53
    assert SOPHIE_GERMAIN.node_count == len(SOPHIE_GERMAIN.primes)
    assert SAFE_PRIMES.node_count == len(SAFE_PRIMES.primes)


def test_prime_set_node_for_prime_roundtrip():
    for ps in (FIRST_53, TWIN_PRIMES, SOPHIE_GERMAIN, SAFE_PRIMES):
        for idx, p in enumerate(ps.primes):
            assert ps.node_for_prime(p) == idx
            assert ps.prime_for_node(idx) == p


def test_prime_set_node_for_prime_unknown():
    with pytest.raises(KeyError):
        FIRST_53.node_for_prime(4)  # 4 is not prime
    with pytest.raises(KeyError):
        TWIN_PRIMES.node_for_prime(2)  # 2 is not a twin prime


def test_prime_set_prime_for_node_out_of_range():
    with pytest.raises(IndexError):
        FIRST_53.prime_for_node(53)
    with pytest.raises(IndexError):
        SAFE_PRIMES.prime_for_node(SAFE_PRIMES.node_count)


def test_prime_set_is_prime_node():
    assert FIRST_53.is_prime_node(2)
    assert not FIRST_53.is_prime_node(4)
    assert TWIN_PRIMES.is_prime_node(3)
    assert not TWIN_PRIMES.is_prime_node(2)  # 2 is not in twin set


def test_prime_set_immutable():
    with pytest.raises(AttributeError):
        FIRST_53.name = "changed"  # type: ignore[misc]


def test_prime_set_repr():
    r = repr(FIRST_53)
    assert "first53" in r
    assert "53" in r


def test_prime_set_first53_aliases():
    """FIRST_53 must be consistent with the backward-compat module aliases."""
    assert FIRST_53.primes is PRIME_NODES
    assert FIRST_53.prime_to_node is ptca.PRIME_TO_NODE


# ---------------------------------------------------------------------------
# PRIME_SETS registry
# ---------------------------------------------------------------------------

def test_prime_sets_registry_keys():
    assert "first53" in PRIME_SETS
    assert "twin" in PRIME_SETS
    assert "sophie_germain" in PRIME_SETS
    assert "safe" in PRIME_SETS


def test_prime_sets_registry_identity():
    assert PRIME_SETS["first53"] is FIRST_53
    assert PRIME_SETS["twin"] is TWIN_PRIMES
    assert PRIME_SETS["sophie_germain"] is SOPHIE_GERMAIN
    assert PRIME_SETS["safe"] is SAFE_PRIMES


def test_prime_sets_exported():
    assert ptca.PRIME_SETS is PRIME_SETS
    assert ptca.FIRST_53 is FIRST_53
    assert ptca.TWIN_PRIMES is TWIN_PRIMES
    assert ptca.SOPHIE_GERMAIN is SOPHIE_GERMAIN
    assert ptca.SAFE_PRIMES is SAFE_PRIMES


# ---------------------------------------------------------------------------
# Custom PrimeSet construction
# ---------------------------------------------------------------------------

def test_custom_prime_set():
    custom = PrimeSet("custom3", (2, 3, 5))
    assert custom.node_count == 3
    assert custom.node_for_prime(5) == 2
    assert custom.prime_for_node(0) == 2
    assert custom.is_prime_node(3)
    assert not custom.is_prime_node(4)
