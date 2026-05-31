# CLAUDE.md — prime_core (PTCA three-stratum core)

Context for AI assistants working in `prime_core/`. This package implements the
stratified PTCA core decided in the "PTCA Core Stratification Handoff" session
(Erin Spencer + Claude). It is **independent of the published `ptca-lib`**
(flat 4-D 53-node tensor) and does not modify it.

---

## What this package is

Three strata, three ontologies (handoff §1.1). The number system changes phase
as you ascend:

| Layer  | Object                                   | Differentiable? |
|--------|------------------------------------------|-----------------|
| Tensor | scalar (`Scalar`) — autodiff leaf        | yes (backprop)  |
| Circle | UCNS carrier hosting `Fiq` opaque grafts | carrier no      |
| Seed   | epicyclic UCNS-in-UCNS grouping          | structure no    |

Composition counts: **7 tensors/circle, 7 circles/seed, 157 seeds → 7,693
fiqs**; payload width `d = 53` → **407,729 scalar params**. Routing IS the UCNS
composition: `{7/2}` composes tensors→circle, `{7/3}` composes circles→seed.

**Gradient policy (frozen, §1.2):** differentiability descends through scalar
payloads; UCNS geometry (`n_min`, `face_state`, `anchor_order`) is
non-differentiable scaffold. `compose_circle`/`compose_seed` are the `⊠`
operator — structural only, so **`∂(⊠)` never appears on the autodiff tape**.

Public surface: `build_core`, `CoreSpec`.

---

## Resolved decisions (handoff §6)

| Decision            | Resolution |
|---------------------|------------|
| prime_core home     | New top-level package in the PTCA repo; `ptca-lib` untouched (packaging `include = ["ptca*"]` excludes it). |
| graft type name     | **`fiq`** — *first iterative qualifier / full isolated query / "the tensor holding the UCNS object"*. |
| tensor dimension `d`| **53** (off the original 32/64/128 menu; itself a coherence prime, echoing the prior seed count). |
| coherence-prime status | **Design choice (tunable)** — test 5 parameterized; 53↔157 both legal. Revert SEED_COUNT→53 keeps the suite green. |
| opaque-host (§1.3)  | **Confirmed** opaque host (not encode), per the "tensors remain scalar" constraint. |
| gradient attach pts | **Nothing crosses upward; payloads only** (the §1.2 default). |

To switch the coherence-prime status to a *hard invariant*, tighten
`tests/test_constants_coherence_prime.py::test_seed_count_is_coherence_prime`
to assert membership of the live `SEED_COUNT` unconditionally.

---

## Tests

```bash
python -m unittest discover -s prime_core/tests -v
```

Covers all six §4 items: structure counts (1), opaque round-trip (2),
gradient path with no `∂(⊠)` node (3), frozen geometry (4), coherence-prime
guard (5), routing steps (6). Stdlib `unittest` only — no pytest dependency.

---

## hmmm — outstanding

- **Canon documents absent.** `canon_definitions_invariants-1.md` and
  `consciousness_primes_prediction1.pdf` are not in any accessible repo. The
  stratum definitions, composition counts, and the coherence-prime ladder are
  encoded here as the handoff *stated* them, not as verified canon. The
  `COHERENCE_FACTOR_UNIVERSE` in `constants.py` is provisional.
- **Validator absent.** `scripts/module_build_check.py` / `universal_parser.py`
  (handoff §5) exist in no repo, so the MODULE_BUILD manifest was validated by
  hand, not mechanically. Vendor them when a source appears.
- **UCNS binding deferred.** `ucns` is not importable in this environment.
  `core._carrier_identity` is the marked attach point where carrier identity
  should route through `ucns.a0_safe` (never raw `factor_search` sentinels,
  per the §2 UCNS-aware rule). Currently a deterministic local tag.
- **Packaging.** `prime_core` is not yet added to `pyproject.toml`
  (`include = ["ptca*"]`). Deliberate — keeps published `ptca-lib` untouched.
  Decide packaging when prime_core is ready to ship.
- **Seam under load.** The descend/ascend split is the whole experiment;
  unfalsified until a core is actually trained.
