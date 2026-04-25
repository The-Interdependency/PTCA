"""Tests for ptca.instance.PTCAInstance."""
import pytest
from ptca.instance import PTCAInstance
from ptca.tensor import PTCATensor
from ptca.sentinels import SentinelState


def _inst(**kwargs) -> PTCAInstance:
    return PTCAInstance(model_id="test-model", caller_id="user:test", **kwargs)


# --- Construction ---

def test_construction_defaults():
    inst = _inst()
    assert inst.model_id == "test-model"
    assert inst.caller_id == "user:test"
    assert inst.session_id != ""
    assert not inst.approved
    assert inst.risk_score == 0.0


def test_construction_custom_session_id():
    inst = PTCAInstance(session_id="my-session")
    assert inst.session_id == "my-session"


def test_construction_approved():
    inst = PTCAInstance(approved=True)
    assert inst.approved


def test_construction_policy():
    inst = PTCAInstance(policy_rules=["rule_a", "rule_b"])
    assert inst.sentinel_state.s2.rules == ["rule_a", "rule_b"]


def test_construction_bounds():
    inst = PTCAInstance(bounds={"lower": 0.0, "upper": 1.0})
    assert inst.sentinel_state.s3.lower == 0.0
    assert inst.sentinel_state.s3.upper == 1.0


def test_construction_genesis_provenance():
    inst = _inst()
    assert len(inst.provenance_chain) == 1
    assert inst.sentinel_state.s1.origin_hash != ""


def test_construction_genesis_audit():
    inst = _inst()
    log = inst.sentinel_state.s9.log
    assert len(log) == 1
    assert log[0]["event"] == "genesis"


# --- S1 Provenance ---

def test_record_provenance_extends_chain():
    inst = _inst()
    inst.record_provenance(payload={"step": 1})
    assert len(inst.provenance_chain) == 2


def test_record_provenance_updates_s1():
    inst = _inst()
    inst.record_provenance()
    assert len(inst.sentinel_state.s1.chain) == 1


# --- S2 Policy ---

def test_set_policy():
    inst = _inst()
    inst.set_policy(["p1", "p2"])
    assert inst.sentinel_state.s2.rules == ["p1", "p2"]


# --- S3 Bounds ---

def test_set_bounds():
    inst = _inst()
    inst.set_bounds(0.0, 100.0)
    assert inst.within_bounds(50.0)
    assert not inst.within_bounds(101.0)


# --- S4 Approval ---

def test_approve_revoke():
    inst = _inst()
    inst.approve("good")
    assert inst.approved
    # audit should record approval
    events = [e["event"] for e in inst.sentinel_state.s9.log]
    assert "approval_granted" in events

    inst.revoke("bad")
    assert not inst.approved
    events = [e["event"] for e in inst.sentinel_state.s9.log]
    assert "approval_revoked" in events


# --- S5 Context ---

def test_push_context():
    inst = _inst()
    inst.push_context({"role": "user", "content": "hi", "tokens": 2})
    assert len(inst.context_entries) == 1


def test_clear_context():
    inst = _inst()
    inst.push_context({"tokens": 1})
    inst.clear_context()
    assert inst.context_entries == []


def test_max_context_entries():
    inst = PTCAInstance(max_context_entries=3)
    for i in range(5):
        inst.push_context({"i": i, "tokens": 1})
    assert len(inst.context_entries) == 3


# --- S7 Memory ---

def test_remember_recall():
    inst = _inst()
    inst.remember("name", "Alice")
    assert inst.recall("name") == "Alice"
    assert inst.recall("missing", "default") == "default"


# --- S8 Risk ---

def test_update_risk():
    inst = _inst()
    inst.update_risk(0.3, factor="test")
    assert inst.risk_score == pytest.approx(0.3)
    # audit entry for risk_update
    events = [e["event"] for e in inst.sentinel_state.s9.log]
    assert "risk_update" in events


def test_reset_risk():
    inst = _inst()
    inst.update_risk(0.9)
    inst.reset_risk()
    assert inst.risk_score == 0.0


# --- Exchange routing ---

def test_route_updates_tensor():
    inst = _inst()
    result = inst.route(node=0, phase=0, slot=0, s1=1.0)
    assert result.score > 0.0
    assert inst.tensor.get(0, 0, 0, 0) > 0.0


def test_batch_route():
    inst = _inst()
    results = inst.batch_route([
        {"node": 0, "phase": 0, "slot": 0, "s1": 1.0},
        {"node": 1, "phase": 1, "slot": 1, "s2": 0.5},
    ])
    assert len(results) == 2


# --- Snapshot ---

def test_snapshot_keys():
    inst = _inst()
    snap = inst.snapshot()
    expected_keys = {
        "session_id", "S5_CONTEXT", "S6_IDENTITY",
        "S7_MEMORY", "S8_RISK", "S9_AUDIT",
    }
    assert expected_keys.issubset(snap.keys())


def test_snapshot_identity():
    inst = PTCAInstance(model_id="m", caller_id="c", session_id="s")
    snap = inst.snapshot()
    assert snap["S6_IDENTITY"]["model_id"] == "m"
    assert snap["S6_IDENTITY"]["caller_id"] == "c"


def test_snapshot_risk():
    inst = _inst()
    inst.update_risk(0.42)
    snap = inst.snapshot()
    assert snap["S8_RISK"]["score"] == pytest.approx(0.42)

# --- repr ---

def test_repr():
    inst = _inst()
    r = repr(inst)
    assert "PTCAInstance" in r
    assert "test-model" in r


# --- Prime set selection ---

def test_default_prime_set():
    from ptca.primes import FIRST_53
    inst = _inst()
    assert inst.prime_set is FIRST_53
    assert inst.tensor.SHAPE[0] == 53


def test_prime_set_by_name_twin():
    from ptca.primes import TWIN_PRIMES
    inst = PTCAInstance(prime_set="twin")
    assert inst.prime_set is TWIN_PRIMES
    assert inst.tensor.SHAPE[0] == TWIN_PRIMES.node_count


def test_prime_set_by_name_sophie_germain():
    from ptca.primes import SOPHIE_GERMAIN
    inst = PTCAInstance(prime_set="sophie_germain")
    assert inst.prime_set is SOPHIE_GERMAIN
    assert inst.tensor.SHAPE[0] == SOPHIE_GERMAIN.node_count


def test_prime_set_by_name_safe():
    from ptca.primes import SAFE_PRIMES
    inst = PTCAInstance(prime_set="safe")
    assert inst.prime_set is SAFE_PRIMES
    assert inst.tensor.SHAPE[0] == SAFE_PRIMES.node_count


def test_prime_set_by_object():
    from ptca.primes import TWIN_PRIMES
    inst = PTCAInstance(prime_set=TWIN_PRIMES)
    assert inst.prime_set is TWIN_PRIMES


def test_prime_set_unknown_name():
    with pytest.raises(KeyError, match="Unknown prime set"):
        PTCAInstance(prime_set="nonexistent")


def test_node_for_prime_method():
    from ptca.primes import TWIN_PRIMES
    inst = PTCAInstance(prime_set="twin")
    assert inst.node_for_prime(3) == TWIN_PRIMES.node_for_prime(3)


def test_snapshot_includes_prime_set():
    inst = PTCAInstance(prime_set="twin")
    snap = inst.snapshot()
    assert snap["prime_set"] == "twin"


def test_route_uses_correct_node_count():
    """Routing to node index within alternate prime set must succeed."""
    from ptca.primes import SAFE_PRIMES
    inst = PTCAInstance(prime_set="safe")
    last_node = SAFE_PRIMES.node_count - 1
    result = inst.route(node=last_node, phase=0, slot=0, s1=1.0)
    assert result.score > 0.0

