"""Tests for ptca.provenance."""
import pytest
from ptca.provenance import (
    build_block,
    hash_block,
    chain_hashes,
    verify_chain,
    extend_chain,
)


def test_build_block_fields():
    b = build_block(model_id="m", caller_id="c", session_id="s")
    assert b["model_id"] == "m"
    assert b["caller_id"] == "c"
    assert b["session_id"] == "s"
    assert b["parent_hash"] == ""
    assert isinstance(b["ts"], float)
    assert b["payload"] == {}


def test_build_block_payload():
    b = build_block(payload={"x": 1})
    assert b["payload"] == {"x": 1}


def test_hash_block_is_hex64():
    b = build_block()
    h = hash_block(b)
    assert isinstance(h, str)
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_hash_deterministic():
    b = build_block(model_id="m", timestamp=1000.0)
    assert hash_block(b) == hash_block(b)


def test_hash_changes_with_content():
    b1 = build_block(model_id="a", timestamp=1.0)
    b2 = build_block(model_id="b", timestamp=1.0)
    assert hash_block(b1) != hash_block(b2)


def test_chain_hashes_length():
    blocks = [build_block(timestamp=float(i)) for i in range(5)]
    hashes = chain_hashes(blocks)
    assert len(hashes) == 5


def test_verify_chain_valid():
    blocks: list = []
    for i in range(4):
        extend_chain(blocks, model_id="m", payload={"i": i})
    assert verify_chain(blocks)


def test_verify_chain_empty():
    assert verify_chain([])


def test_verify_chain_genesis_no_parent():
    b = build_block(parent_hash="")
    assert verify_chain([b])


def test_verify_chain_tampered():
    blocks: list = []
    for i in range(3):
        extend_chain(blocks, payload={"i": i})
    # Tamper with middle block
    blocks[1]["payload"]["i"] = 999
    assert not verify_chain(blocks)


def test_extend_chain_appends():
    blocks: list = []
    b1 = extend_chain(blocks, model_id="m")
    assert len(blocks) == 1
    assert blocks[0] is b1


def test_extend_chain_parent_hash():
    blocks: list = []
    b1 = extend_chain(blocks)
    b2 = extend_chain(blocks)
    assert b2["parent_hash"] == hash_block(b1)


def test_verify_chain_genesis_bad_parent():
    b = build_block(parent_hash="nonexistent")
    assert not verify_chain([b])
