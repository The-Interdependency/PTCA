"""Tests for ptca.tensor.PTCATensor."""
import pytest
from ptca.tensor import PTCATensor
from ptca.constants import NODES, SENTINELS, PHASES, SLOTS


def test_shape_constants():
    t = PTCATensor()
    assert t.SHAPE == (NODES, SENTINELS, PHASES, SLOTS)


def test_size():
    t = PTCATensor()
    assert t.SIZE == NODES * SENTINELS * PHASES * SLOTS
    assert len(t) == t.SIZE


def test_initial_zero():
    t = PTCATensor()
    assert t.get(0, 0, 0, 0) == 0.0
    assert t.get(NODES - 1, SENTINELS - 1, PHASES - 1, SLOTS - 1) == 0.0


def test_set_and_get():
    t = PTCATensor()
    t.set(1, 2, 3, 4, 3.14)
    assert t.get(1, 2, 3, 4) == pytest.approx(3.14)


def test_add():
    t = PTCATensor()
    t.set(0, 0, 0, 0, 1.0)
    t.add(0, 0, 0, 0, 0.5)
    assert t.get(0, 0, 0, 0) == pytest.approx(1.5)


def test_out_of_range():
    t = PTCATensor()
    with pytest.raises(IndexError):
        t.get(NODES, 0, 0, 0)
    with pytest.raises(IndexError):
        t.get(0, SENTINELS, 0, 0)
    with pytest.raises(IndexError):
        t.get(0, 0, PHASES, 0)
    with pytest.raises(IndexError):
        t.get(0, 0, 0, SLOTS)


def test_reset():
    t = PTCATensor()
    t.set(5, 3, 2, 1, 99.0)
    t.reset()
    assert t.get(5, 3, 2, 1) == 0.0


def test_reset_node():
    t = PTCATensor()
    t.set(0, 0, 0, 0, 1.0)
    t.set(1, 0, 0, 0, 2.0)
    t.reset_node(0)
    assert t.get(0, 0, 0, 0) == 0.0
    assert t.get(1, 0, 0, 0) == pytest.approx(2.0)


def test_node_slice_length():
    t = PTCATensor()
    assert len(t.node_slice(0)) == SENTINELS * PHASES * SLOTS


def test_sentinel_slice_length():
    t = PTCATensor()
    assert len(t.sentinel_slice(0)) == NODES * PHASES * SLOTS


def test_aggregate_mean_all_zeros():
    t = PTCATensor()
    assert t.aggregate("mean") == 0.0


def test_aggregate_mean():
    t = PTCATensor()
    t.set(0, 0, 0, 0, 2.0)
    t.set(0, 0, 0, 1, 4.0)
    mean = t.aggregate("mean", node=0, sentinel=0, phase=0)
    # 7 slots: 2.0 + 4.0 + 0*5 = 6.0, mean = 6/7
    assert mean == pytest.approx(6.0 / SLOTS)


def test_aggregate_sum():
    t = PTCATensor()
    t.set(0, 0, 0, 0, 3.0)
    t.set(0, 0, 0, 1, 7.0)
    total = t.aggregate("sum", node=0, sentinel=0, phase=0)
    assert total == pytest.approx(10.0)


def test_aggregate_bad_method():
    t = PTCATensor()
    with pytest.raises(ValueError):
        t.aggregate("median")


def test_repr():
    t = PTCATensor()
    r = repr(t)
    assert "PTCATensor" in r
