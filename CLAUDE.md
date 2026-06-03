# CLAUDE.md — PTCA: Probabilistic Tensor Context Architecture

This file gives AI assistants context needed to work effectively in this repository.

---

## What This Repo Is

The PTCA repo hosts **two independent pure-Python packages**:

1. **`ptca-lib`** (package dir `ptca/`, pip name **`ptca-lib`**, v0.1.0) — a
   zero-dependency library implementing the **Probabilistic Tensor Context
   Architecture**: a sentinel-channel, prime-node 4-D tensor system. This is the
   shippable package (`pyproject.toml` packages `ptca*` only).
2. **`prime_core/`** — an experimental **three-stratum PTCA core**
   (tensor / circle / seed) layered on UCNS composition. It is *independent of*
   `ptca-lib` and is **not** packaged for release yet. See
   `prime_core/CLAUDE.md` for its full design notes.

**Python requirement:** ≥ 3.9
**External dependencies:** none (stdlib only — `hashlib`, `dataclasses`, `uuid`,
`json`, `time`, `typing`)
**License:** **dual** — AGPL-3.0-or-later (default) OR a commercial license. See
`LICENSE` and `LICENSE-COMMERCIAL.md`.

> License note: `LICENSE` is currently an **interim notice** — the full verbatim
> AGPL-3.0 text has not been pasted in yet (the build environment had no network
> access). `pyproject.toml` declares `license = { text = "AGPL-3.0-or-later" }`.
> Do not "fix" the license to Apache anywhere.

---

## Repository Layout

```
ptca/                  # ptca-lib — the published package
  __init__.py          Stable public API surface + __version__
  constants.py         Dims, exchange constants, sentinel names/index/weights
  exchange.py          compute_score, Exchange router (.route/.batch_route),
                       ExchangeResult, aggregate_seeds, aggregate_identity
  instance.py          PTCAInstance — stateful session; snapshot()
  primes.py            PRIME_NODES (first 53 primes), forward/reverse lookup
  provenance.py        build_block, hash_block (SHA-256), chain_hashes,
                       verify_chain, extend_chain
  sentinels.py         S1–S9 dataclass states + SentinelState composite
  tensor.py            PTCATensor — flat-list 4-D tensor

tests/                 # ptca-lib tests (pytest, function-style)
  test_constants.py  test_primes.py  test_sentinels.py  test_tensor.py
  test_provenance.py  test_exchange.py  test_instance.py

prime_core/            # experimental three-stratum core (NOT packaged)
  __init__.py          Public surface: build_core, CoreSpec (+ strata/constants)
  constants.py         Frozen composition counts + recursive coherence-prime guard
  core.py              Core/Seed/Circle, compose_circle, compose_seed, build_core
  fiq.py               Fiq / Scalar opaque-host graft types
  CLAUDE.md            Design notes for prime_core (read before editing it)
  tests/               stdlib unittest suite

.agents/skills/        Agent skills (meta-module-build, msdmd, test-build)
pyproject.toml         Package config (setuptools; packages ptca* only)
LICENSE                Interim AGPL-3.0-or-later notice
LICENSE-COMMERCIAL.md  Commercial dual-license offer
CLAUDE.md              This file
```

> There is **no `README.md`** even though `pyproject.toml` references it. Adding
> one would satisfy that reference; do not assume it exists.

---

## Development Workflow

```bash
# Install editable (packages only ptca-lib)
pip install -e .

# Run ptca-lib tests (requires pytest — not bundled, install it first)
python -m pytest tests/ -v
python -m pytest tests/test_instance.py -v     # single file

# Run prime_core tests (stdlib unittest — no pytest needed)
python -m unittest discover -s prime_core/tests -v
```

- `tests/` uses **pytest** (function-style tests, `import pytest`); it is not in
  `dependencies`, so install it explicitly before running.
- `prime_core/tests/` uses **stdlib `unittest`** only — deliberately no pytest
  dependency.
- No linter/formatter is configured. Keep code consistent with existing style:
  plain dataclasses, type hints, stdlib only. Prefer `ruff` if adding tooling.
- No CI/CD pipeline exists (`.github/` absent).

---

## ptca-lib — Tensor Schema

| Axis | Name     | Size | Notes |
|------|----------|------|-------|
| 0    | node     | 53   | indexed by the first 53 primes (2 … 241) |
| 1    | sentinel | 9    | S1–S9 channels |
| 2    | phase    | 8    | processing phases |
| 3    | slot     | 7    | heptagram slots |

Total cells: **26 796**. Stored as a flat list; access via
`PTCATensor.get(node, sentinel, phase, slot)`,
`set(node, sentinel, phase, slot, value)`, and
`add(node, sentinel, phase, slot, delta)` (the trailing `value`/`delta` is
required for `set`/`add`).

### Sentinel Channels

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

### Exchange Constants & Scoring

```python
DELTA = 1      # base exchange unit
ALPHA = 0.10   # S1 (provenance) and S8 (risk) weight
BETA  = 0.20   # S2 (policy) weight
GAMMA = 0.10   # S3 (bounds) and S5 (context) weight
AGG6      = "mean"   # S6 identity aggregation
AGG_SEEDS = "mean"   # seed aggregation
```

`score = DELTA × (ALPHA·s1 + BETA·s2 + GAMMA·s3 + GAMMA·s5 + ALPHA·s8 + bonus)`

`SENTINEL_WEIGHTS` is parallel to `SENTINEL_NAMES`; S4/S6/S7/S9 carry weight
`0.0` (gate / aggregated-separately / carried-forward / log-only).

---

## ptca-lib — Public API

```python
from ptca import PTCAInstance, PTCATensor, SentinelState
from ptca.exchange import compute_score, Exchange, aggregate_seeds
from ptca.provenance import build_block, hash_block, verify_chain, extend_chain

inst = PTCAInstance(model_id="...", caller_id="user:alice")
inst.push_context({"role": "user", "content": "Hello", "tokens": 5})
inst.record_provenance(payload={"source": "user", "action": "query"})  # extends SHA-256 chain, updates S1 (kwarg is payload=, keyword-only; optional timestamp=)
result = inst.route(node=0, phase=0, slot=0, s1=1.0, s5=0.9)        # ExchangeResult
ctx = inst.snapshot()  # dict keyed S5_CONTEXT … S9_AUDIT
```

`PTCAInstance` exposes properties (`model_id`, `caller_id`, `risk_score`,
`approved`, `context_entries`, `memory_store`, `provenance_chain`) and methods
including `set_policy`, `set_bounds`/`within_bounds`, `approve`/`revoke`,
`push_context`/`clear_context`, `remember`/`recall`, `update_risk`/`reset_risk`,
`audit_tail`, `route`/`batch_route`, `snapshot`.

---

## prime_core — Mental Model

Three strata, three ontologies; the "number system changes phase" as you ascend:

| Layer  | Object                                   | Differentiable? |
|--------|------------------------------------------|-----------------|
| Tensor | scalar (`Scalar`) — autodiff leaf        | yes (backprop)  |
| Circle | UCNS carrier hosting `Fiq` opaque grafts | carrier no      |
| Seed   | epicyclic UCNS-in-UCNS grouping          | structure no    |

Composition counts (`prime_core/constants.py`): **7 tensors/circle, 7
circles/seed, 157 seeds → 7 693 fiqs**; payload width `d = 53` → **407 729**
scalar params. Routing IS the UCNS composition: `{7/2}` (`CIRCLE_ROUTING_STEP`)
composes tensors→circle, `{7/3}` (`SEED_ROUTING_STEP`) composes circles→seed.

**Gradient policy (frozen):** differentiability descends through scalar payloads
only; UCNS geometry is non-differentiable scaffold. `compose_circle`/
`compose_seed` are the `⊠` operator — structural only, so `∂(⊠)` never appears
on the autodiff tape.

**Coherence-prime guard:** `is_coherence_prime` uses the *recursive* definition
(a prime's kernel `(p-1)//4` must be square-free and factor only into earlier
coherence primes). This mirrors `interdependent_lib.coherence_primes` verbatim —
it is **not** imported (that would invert the dependency graph). Do not revert to
the old frozen-universe set (it diverged at p=4373). `SEED_COUNT` is 157 by
design; reverting to 53 keeps the suite green (it is a tunable choice, not a hard
invariant unless the relevant test is tightened).

> Caveats live in `prime_core/CLAUDE.md`: source canon documents are absent,
> `ucns` is not importable here, and prime_core is intentionally excluded from
> packaging. Read that file before editing `prime_core/`.

---

## Key Conventions & Gotchas

- **No external runtime dependencies** — stdlib only. Do not add runtime deps to
  either package.
- `PRIME_NODES` in `ptca/primes.py` is the authoritative 53-prime list — do not
  modify it.
- Provenance helpers are `build_block` → `hash_block` (SHA-256) → `chain_hashes`
  / `verify_chain` / `extend_chain`. The function is `verify_chain`, **not**
  `chain_verify`. Never bypass the chain for audited operations.
- `ptca/__init__.py` is the stable public surface — only add intentional exports.
- `PTCAInstance.snapshot()` returns `S5_CONTEXT … S9_AUDIT` keys, matching the
  shape the downstream backend already produces.
- `prime_core` and `ptca` must stay independent: `prime_core` must not import or
  modify `ptca`, and packaging must keep including only `ptca*`.

---

## Git Workflow

- Main branch: `main`. Feature branches: `feat/<desc>`, `fix/<desc>`,
  `docs/<desc>` (Claude Code branches use `claude/<desc>`).
- Commit style: Conventional Commits (`feat(ptca):`, `fix(prime_core):`,
  `docs:`, `chore(prime_core):`).
- Author: Erin Patrick Spencer (wayseer@interdependentway.org).

---

## Agent Module-Build Doctrine

Before adding a new module, route, service, adapter, schema, worker, engine,
UI panel, migration, or experiment, read:

`./.agents/skills/meta-module-build/SKILL.md`

New module work starts with a `MODULE_BUILD` block (see the example at the top of
`prime_core/constants.py`). Unknown fields must be marked `hmmm`, not guessed.

---

## Related Repos

| Repo | Role |
|------|------|
| The-Interdependency/interdependent-lib | Meta-package; canonical `coherence_primes` source |
| The-Interdependency/a0 | Agent platform — primary consumer of PTCA |
| The-Interdependency/pcea | Sibling encryption library (same 53-prime design) |
| erinepshovel-code/UnitCircle | Prime distribution visualization |
