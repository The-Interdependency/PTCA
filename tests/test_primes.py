"""Tests for ptca.primes."""
import pytest
import ptca
from ptca.primes import PRIME_NODES, node_for_prime, prime_for_node, is_prime_node


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
