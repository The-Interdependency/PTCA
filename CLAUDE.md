# PTCA — Claude Code Project Guide

## What this repo is

`ptca-lib` is a zero-dependency pure-Python library that implements the
**Probabilistic Tensor Context Architecture** used by the
[erinepshovel-code/aimmh](https://github.com/erinepshovel-code/aimmh) AI hub
backend.  It is the second extracted component after `aimmh-lib`; the third is
`EDCM` (erinepshovel-code/EDCM).

pip package name: **`ptca-lib`**
Python requirement: ≥ 3.9
External dependencies: **none** (stdlib only — hashlib, dataclasses, uuid, json, time)

---

## Tensor schema

| Axis | Name     | Size | Notes |
|------|----------|------|-------|
| 0    | node     | 53   | indexed by the first 53 primes (2 … 241) |
| 1    | sentinel | 9    | S1–S9 channels |
| 2    | phase    | 8    | processing phases |
| 3    | slot     | 7    | heptagram slots |

Total cells: **26 796**

## Sentinel channels

| #  | Name           | Role |
|----|----------------|------|
| S1 | PROVENANCE     | origin hash + chain of custody |
| S2 | POLICY         | active policy rule identifiers |
| S3 | BOUNDS         | numeric constraint envelope |
| S4 | APPROVAL       | boolean gate |
| S5 | CONTEXT        | live context-window entries |
| S6 | IDENTITY       | model / caller identity record |
| S7 | MEMORY         | persistent key-value memory |
| S8 | RISK           | running risk score [0, 1] |
| S9 | AUDIT          | append-only audit trail |

## Exchange constants

```python
DELTA     = 1      # base exchange unit
ALPHA     = 0.10   # S1 (provenance) and S8 (risk) weight
BETA      = 0.20   # S2 (policy) weight
GAMMA     = 0.10   # S3 (bounds) and S5 (context) weight
AGG6      = "mean" # S6 identity aggregation
AGG_SEEDS = "mean" # seed aggregation
```

Score formula: `score = DELTA × (α·s1 + β·s2 + γ·s3 + γ·s5 + α·s8 + bonus)`

---

## Package layout

```
ptca/
  __init__.py     clean public API
  constants.py    dims, exchange constants, sentinel names/weights
  primes.py       PRIME_NODES (first 53 primes), forward/reverse lookup
  sentinels.py    S1–S9 dataclass states + SentinelState composite
  tensor.py       PTCATensor — flat-list 4-D tensor
  provenance.py   build_block, hash_block (SHA-256), chain verify
  exchange.py     compute_score, Exchange router, batch_route
  instance.py     PTCAInstance — stateful session, snapshot()
tests/
  test_constants.py
  test_primes.py
  test_sentinels.py
  test_tensor.py
  test_provenance.py
  test_exchange.py
  test_instance.py
pyproject.toml
```

---

## Development workflow

```bash
# Run tests
python -m pytest tests/ -v

# Install editable
pip install -e .
```

No linter or formatter is configured yet; keep code consistent with the
existing style (plain dataclasses, no third-party libs).

## Branch

Active development branch: `claude/extract-ptca-library-xycUX`
Target repo: `erinepshovel-code/PTCA` (maps to `erinepshovel-code/a0` upstream intent)

## Related repos

| Repo | Role |
|------|------|
| erinepshovel-code/aimmh | Hub backend (source of PTCA schema, v1.0.2-S9) |
| erinepshovel-code/EDCM  | Cognitive metrics engine (another extracted component) |
| erinepshovel-code/pcna_edcm | PCNA + EDCM combined (private) |
| erinepshovel-code/UnitCircle | Prime distribution visualisation |

## Composition with aimmh-lib

`PTCAInstance` is designed to be composed with `aimmh_lib.ModelInstance`:

- Pass `inst.sentinel_state` and `inst.tensor` to any PTCA-aware consumer.
- `inst.snapshot()` returns a `sentinel_context` dict with `S5_CONTEXT` …
  `S9_AUDIT` keys matching the shape the aimmh backend already produces.
- `inst.record_provenance()` extends the SHA-256 chain and updates `S1`.
