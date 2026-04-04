"""Tests for ptca.sentinels."""
import pytest
from ptca.sentinels import (
    SentinelState,
    S1ProvenanceState, S2PolicyState, S3BoundsState, S4ApprovalState,
    S5ContextState, S6IdentityState, S7MemoryState, S8RiskState, S9AuditState,
)
from ptca.constants import SENTINEL_NAMES


# --- Individual channel tests ---

def test_s1_append():
    s1 = S1ProvenanceState()
    s1.append("abc")
    s1.append("def")
    assert s1.chain == ["abc", "def"]


def test_s2_set_rules():
    s2 = S2PolicyState()
    s2.set_rules(["rule_a", "rule_b"])
    assert s2.rules == ["rule_a", "rule_b"]


def test_s3_within():
    s3 = S3BoundsState(lower=0.0, upper=1.0)
    assert s3.within(0.5)
    assert s3.within(0.0)
    assert s3.within(1.0)
    assert not s3.within(1.1)
    assert not s3.within(-0.1)


def test_s4_approve_revoke():
    s4 = S4ApprovalState()
    assert not s4.approved
    s4.approve("ok")
    assert s4.approved
    assert s4.reason == "ok"
    s4.revoke("nope")
    assert not s4.approved
    assert s4.reason == "nope"


def test_s5_push_and_max():
    s5 = S5ContextState(max_entries=3)
    for i in range(5):
        s5.push({"tokens": i})
    assert len(s5.entries) == 3
    assert s5.entries[0]["tokens"] == 2  # oldest retained


def test_s5_token_count():
    s5 = S5ContextState()
    s5.push({"tokens": 10})
    s5.push({"tokens": 5})
    assert s5.token_count == 15


def test_s5_clear():
    s5 = S5ContextState()
    s5.push({"tokens": 1})
    s5.clear()
    assert s5.entries == []


def test_s6_set_identity():
    s6 = S6IdentityState()
    s6.set_identity(model_id="m", caller_id="c", session_id="s", extra="x")
    assert s6.model_id == "m"
    assert s6.caller_id == "c"
    assert s6.session_id == "s"
    assert s6.metadata["extra"] == "x"


def test_s7_remember_retrieve():
    s7 = S7MemoryState()
    s7.remember("key", "value")
    assert s7.retrieve("key") == "value"
    assert s7.retrieve("missing", "default") == "default"


def test_s8_update_clamps():
    s8 = S8RiskState()
    s8.update(0.5)
    assert s8.score == 0.5
    s8.update(0.7)
    assert s8.score == 1.0  # clamped
    s8.update(-2.0)
    assert s8.score == 0.0  # clamped


def test_s8_reset():
    s8 = S8RiskState()
    s8.update(0.5)
    s8.reset()
    assert s8.score == 0.0
    assert s8.factors == []


def test_s9_record_and_tail():
    s9 = S9AuditState()
    s9.record("event_a", x=1)
    s9.record("event_b", x=2)
    tail = s9.tail(1)
    assert len(tail) == 1
    assert tail[0]["event"] == "event_b"
    assert "ts" in tail[0]


# --- Composite SentinelState ---

def test_sentinel_state_defaults():
    state = SentinelState()
    assert isinstance(state.s1, S1ProvenanceState)
    assert isinstance(state.s9, S9AuditState)


def test_sentinel_state_channel_lookup():
    state = SentinelState()
    for name in SENTINEL_NAMES:
        assert state.channel(name) is not None


def test_sentinel_state_channel_bad_key():
    state = SentinelState()
    with pytest.raises(KeyError):
        state.channel("S99_FAKE")


def test_sentinel_state_to_dict_keys():
    state = SentinelState()
    d = state.to_dict()
    for name in SENTINEL_NAMES:
        assert name in d
