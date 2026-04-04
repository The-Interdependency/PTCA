"""Tests for ptca.constants."""
import ptca


def test_tensor_dimensions():
    assert ptca.NODES == 53
    assert ptca.SENTINELS == 9
    assert ptca.PHASES == 8
    assert ptca.SLOTS == 7


def test_exchange_constants():
    assert ptca.DELTA == 1
    assert ptca.ALPHA == 0.10
    assert ptca.BETA == 0.20
    assert ptca.GAMMA == 0.10
    assert ptca.AGG6 == "mean"
    assert ptca.AGG_SEEDS == "mean"


def test_sentinel_names_count():
    assert len(ptca.SENTINEL_NAMES) == 9


def test_sentinel_names_content():
    expected = [
        "S1_PROVENANCE", "S2_POLICY", "S3_BOUNDS", "S4_APPROVAL",
        "S5_CONTEXT", "S6_IDENTITY", "S7_MEMORY", "S8_RISK", "S9_AUDIT",
    ]
    assert list(ptca.SENTINEL_NAMES) == expected


def test_sentinel_index_roundtrip():
    for i, name in enumerate(ptca.SENTINEL_NAMES):
        assert ptca.SENTINEL_INDEX[name] == i


def test_sentinel_weights_length():
    assert len(ptca.SENTINEL_WEIGHTS) == 9
