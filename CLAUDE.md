# CLAUDE.md — PTCA: Probabilistic Tensor Context Architecture

This file gives AI assistants context needed to work effectively in this repository.

---

## What This Repo Is

`ptca-lib` (pip package: **`ptca-lib`**, v0.1.0) is a zero-dependency pure-Python library implementing the **Probabilistic Tensor Context Architecture** — a sentinel-channel, prime-node tensor system used by the a0 AI hub backend. It is one of the four-letter acronym libraries published under The Interdependency.

**Python requirement:** ≥ 3.9  
**External dependencies:** none (stdlib only — hashlib, dataclasses, uuid, json, time)  
**License:** Apache 2.0

---

## Tensor Schema

| Axis | Name     | Size | Notes |
|------|----------|------|-------|
| 0    | node     | 53   | indexed by the first 53 primes (2 … 241) |
| 1    | sentinel | 9    | S1–S9 channels |
| 2    | phase    | 8    | processing phases |
| 3    | slot     | 7    | heptagram slots |

Total cells: **26 796**

## Sentinel Channels

| #  | Name       | Role |
|----|------------|------|
| S1 | PROVENANCE | origin hash + chain of custody |
| S2 | POLICY     | active policy rule identifiers |
| S3 | BOUNDS     | numeric constraint envelope |
| S4 | APPROVAL   | boolean gate |
| S5 | CONTEXT    | live context-window entries |
| S6 | IDENTITY   | model / caller identity record |
| S7 | MEMORY     | persistent key-value memory |
| S8 | RISK       | running risk score [0, 1] |
| S9 | AUDIT      | append-only audit trail |

## Exchange Constants

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

## Repository Layout

```
ptca/
  __init__.py      Clean public API
  constants.py     Dims, exchange constants, sentinel names/weights
  exchange.py      compute_score, Exchange router, batch_route
  instance.py      PTCAInstance — stateful session, snapshot()
  primes.py        PRIME_NODES (first 53 primes), forward/reverse lookup
  provenance.py    build_block, hash_block (SHA-256), chain verify
  sentinels.py     S1–S9 dataclass states + SentinelState composite
  tensor.py        PTCATensor — flat-list 4-D tensor

tests/
  test_constants.py
  test_primes.py
  test_sentinels.py
  test_tensor.py
  test_provenance.py
  test_exchange.py
  test_instance.py

pyproject.toml     Package config (setuptools, ptca-lib, Python >= 3.9)
LICENSE            Apache 2.0
README.md
CLAUDE.md          This file
```

---

## Development Workflow

```bash
# Install editable
pip install -e .

# Run tests
python -m pytest tests/ -v

# Run a specific test
python -m pytest tests/test_instance.py -v
```

No linter or formatter configured yet. Keep code consistent with existing style: plain dataclasses, no third-party libraries.

---

## Public API

```python
from ptca import PTCAInstance, PTCATensor, SentinelState
from ptca.exchange import compute_score, batch_route
from ptca.provenance import build_block, hash_block

# Create a stateful session
inst = PTCAInstance()

# Record provenance (extends SHA-256 chain, updates S1)
inst.record_provenance(data={"source": "user", "action": "query"})

# Take a snapshot (returns sentinel_context dict with S5_CONTEXT..S9_AUDIT keys)
ctx = inst.snapshot()

# Compose with model consumers
# Pass inst.sentinel_state and inst.tensor to any PTCA-aware consumer
```

---

## Key Conventions

- **No external dependencies** — stdlib only. Do not add runtime deps.
- `PRIME_NODES` in `primes.py` is the authoritative 53-prime list — do not modify.
- The 4-D tensor is stored as a flat list — shape is `[N=53, SENTINELS=9, PHASES=8, SLOTS=7]` = 26 796 cells. Access via `PTCATensor.get(node, sentinel, phase, slot)` / `.set(...)`.
- `PTCAInstance.snapshot()` returns `S5_CONTEXT … S9_AUDIT` keys — these match the shape the aimmh backend already produces.
- Provenance chain uses SHA-256; `hash_block` → `build_block` → `chain_verify`. Never bypass this chain for audited operations.
- `ptca/__init__.py` is the stable public API surface — only add exports here that are intentional.

---

## Composition with aimmh-lib

`PTCAInstance` is designed to compose with `aimmh_lib.ModelInstance`:
- Pass `inst.sentinel_state` and `inst.tensor` to any PTCA-aware consumer
- `inst.snapshot()` → `sentinel_context` dict with `S5_CONTEXT … S9_AUDIT` keys matching the aimmh backend shape
- `inst.record_provenance()` extends the SHA-256 chain and updates S1

---

## What Does Not Exist Yet

- No CI/CD pipeline
- No linting config (prefer `ruff` when adding)
- No type stubs / `py.typed` marker
- Tests use `python -m pytest`; no `pytest.ini` or `[tool.pytest.ini_options]` configured in pyproject.toml yet

---

## Related Repos

| Repo | Role |
|------|------|
| The-Interdependency/interdependent-lib | Meta-package bundling ptca-lib + pcea + ucns + aimmh |
| The-Interdependency/a0 | Agent platform — primary consumer of PTCA |
| The-Interdependency/pcea | PCEA — sibling encryption library (same 53-prime design) |
| erinepshovel-code/UnitCircle | Prime distribution visualization |

---

## Git Workflow

- Main branch: `main`
- Feature branches: `feat/<description>`, `fix/<description>`, `docs/<description>`
- Commit style: Conventional Commits (`feat(ptca):`, `fix(exchange):`, etc.)
- Author: Erin Patrick Spencer (wayseer@interdependentway.org)
- License: Apache 2.0
