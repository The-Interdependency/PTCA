"""Tests for ptca.exchange."""
import pytest
from ptca.exchange import Exchange, compute_score, aggregate_seeds, aggregate_identity
from ptca.tensor import PTCATensor
from ptca.sentinels import SentinelState
from ptca.constants import ALPHA, BETA, GAMMA, DELTA


def test_compute_score_all_zero():
    score, components = compute_score()
    assert score == 0.0
    assert all(v == 0.0 for v in components.values())


def test_compute_score_s1_only():
    score, components = compute_score(s1=1.0)
    assert score == pytest.approx(DELTA * ALPHA * 1.0)
    assert components["s1"] == pytest.approx(ALPHA)


def test_compute_score_s2_only():
    score, components = compute_score(s2=1.0)
    assert score == pytest.approx(DELTA * BETA)


def test_compute_score_s5_only():
    score, components = compute_score(s5=1.0)
    assert score == pytest.approx(DELTA * GAMMA)


def test_compute_score_combined():
    score, _ = compute_score(s1=1.0, s2=1.0, s5=1.0)
    expected = DELTA * (ALPHA + BETA + GAMMA)
    assert score == pytest.approx(expected)


def test_compute_score_bonus():
    score, components = compute_score(bonus=0.5)
    assert score == pytest.approx(DELTA * 0.5)
    assert components["bonus"] == 0.5


def test_aggregate_seeds_mean():
    result = aggregate_seeds([1.0, 2.0, 3.0], "mean")
    assert result == pytest.approx(2.0)


def test_aggregate_seeds_sum():
    result = aggregate_seeds([1.0, 2.0, 3.0], "sum")
    assert result == pytest.approx(6.0)


def test_aggregate_seeds_empty():
    assert aggregate_seeds([], "mean") == 0.0
    assert aggregate_seeds([], "sum") == 0.0


def test_aggregate_seeds_bad_method():
    with pytest.raises(ValueError):
        aggregate_seeds([1.0], "median")


def test_aggregate_identity_default():
    result = aggregate_identity([2.0, 4.0])
    assert result == pytest.approx(3.0)


def _make_exchange():
    t = PTCATensor()
    s = SentinelState()
    return Exchange(t, s), t, s


def test_route_writes_tensor():
    exc, t, _ = _make_exchange()
    exc.route(node=0, phase=0, slot=0, s1=1.0, sentinel_idx=0)
    assert t.get(0, 0, 0, 0) > 0.0


def test_route_accumulates():
    exc, t, _ = _make_exchange()
    exc.route(node=0, phase=0, slot=0, s1=1.0, sentinel_idx=0)
    first = t.get(0, 0, 0, 0)
    exc.route(node=0, phase=0, slot=0, s1=1.0, sentinel_idx=0)
    assert t.get(0, 0, 0, 0) == pytest.approx(first * 2)


def test_route_records_audit():
    exc, _, s = _make_exchange()
    exc.route(node=3, phase=1, slot=2, s2=0.5)
    assert len(s.s9.log) == 1
    entry = s.s9.log[0]
    assert entry["node"] == 3
    assert entry["event"] == "exchange"


def test_route_result_fields():
    exc, _, _ = _make_exchange()
    result = exc.route(node=1, phase=2, slot=3, s1=0.5, sentinel_idx=4)
    assert result.node == 1
    assert result.phase == 2
    assert result.slot == 3
    assert result.sentinel_idx == 4
    assert result.score >= 0.0
    assert "s1" in result.components


def test_batch_route():
    exc, t, _ = _make_exchange()
    exchanges = [
        {"node": 0, "phase": 0, "slot": 0, "s1": 1.0},
        {"node": 1, "phase": 0, "slot": 0, "s2": 1.0},
    ]
    results = exc.batch_route(exchanges)
    assert len(results) == 2
    assert t.get(0, 0, 0, 0) > 0.0
    assert t.get(1, 0, 0, 0) > 0.0
