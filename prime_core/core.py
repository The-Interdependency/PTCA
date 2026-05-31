"""prime_core.core — the three-stratum PTCA core builder.

Stratification (handoff §1.1): scalar tensors are grafted into UCNS *circle*
carriers as opaque ``Fiq`` hosts, and circles are grouped into epicyclic
*seeds* (UCNS-in-UCNS). Routing IS the UCNS composition pattern, not an add-on:

    {7/2} heptagram composes tensors -> circle   (CIRCLE_ROUTING_STEP)
    {7/3} heptagram composes circles -> seed     (SEED_ROUTING_STEP)

Gradient policy (handoff §1.2): differentiability descends through the scalar
payloads; UCNS geometry (n_min, face state, anchor ordering) is
non-differentiable scaffold. ``compose_circle`` / ``compose_seed`` are the
structural ``⊠`` operator — they create no autodiff node, so ``∂(⊠)`` never
appears on the tape.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence

from .constants import (
    CIRCLE_ROUTING_STEP,
    CIRCLES_PER_SEED,
    SEED_COUNT,
    SEED_ROUTING_STEP,
    TENSOR_DIM,
    TENSORS_PER_CIRCLE,
)
from .fiq import Fiq, wrap_tensor_fiq

# UCNS-aware rule (handoff §2): when carrier construction touches UCNS identity,
# prefer the A0-safe public boundary over raw factorization sentinels. The
# binding of a real UCNSObject is the next step; until ucns is importable this
# stays a deterministic local tag, and the attach point is marked here.
try:  # pragma: no cover - import availability is environment-dependent
    from ucns import a0_safe as _a0_safe  # noqa: F401
except Exception:  # pragma: no cover
    _a0_safe = None


def heptagram_order(step: int, n: int = 7) -> List[int]:
    """Vertex visitation order of the {n/step} star polygon.

    For n = 7: step 2 -> [0,2,4,6,1,3,5]; step 3 -> [0,3,6,2,5,1,4]. Requires
    gcd(step, n) == 1 so every vertex is visited exactly once.
    """
    return [(step * i) % n for i in range(n)]


def _carrier_identity(*coords: int) -> str:
    """Deterministic carrier identity tag (UCNS-aware attach point, handoff §2).

    When ucns is available this is where identity should route through
    ``a0_safe`` rather than raw ``factor_search`` sentinels. Real UCNSObject
    binding is deferred; this local tag keeps the scaffold runnable meanwhile.
    """
    return "fiq:" + ".".join(str(c) for c in coords)


@dataclass(frozen=True)
class CoreSpec:
    """Composition spec for a core. Defaults are the canon counts (handoff §1.1).

    Parameterized so tests can build a small core for fast gradient checks and
    so the seed count stays a tunable design choice (§6: design choice, not a
    hard invariant).
    """

    seed_count: int = SEED_COUNT
    circles_per_seed: int = CIRCLES_PER_SEED
    tensors_per_circle: int = TENSORS_PER_CIRCLE
    tensor_dim: int = TENSOR_DIM
    circle_routing_step: int = CIRCLE_ROUTING_STEP
    seed_routing_step: int = SEED_ROUTING_STEP

    @property
    def tensor_leaves(self) -> int:
        return self.seed_count * self.circles_per_seed * self.tensors_per_circle

    @property
    def param_count(self) -> int:
        return self.tensor_leaves * self.tensor_dim


class Circle:
    """UCNS carrier hosting ``tensors_per_circle`` fiqs as opaque payloads.

    Geometry (``n_min``, ``face_state``, ``anchor_order``) is non-differentiable
    scaffold: it routes, it does not learn (handoff §1.2 / §4.4).
    """

    __slots__ = ("fiqs", "routing_step", "anchor_order", "n_min", "face_state", "identity")

    def __init__(self, fiqs: Sequence[Fiq], routing_step: int, identity: Optional[str] = None) -> None:
        self.fiqs: List[Fiq] = list(fiqs)
        self.routing_step = routing_step
        self.anchor_order = tuple(heptagram_order(routing_step, len(self.fiqs)))
        self.n_min = len(self.fiqs)   # frozen scaffold
        self.face_state = 0           # frozen scaffold
        self.identity = identity

    @property
    def requires_grad(self) -> bool:
        return False  # geometry never appears as a leaf (handoff §4.4)

    def at(self, anchor: int) -> Fiq:
        """Retrieve the fiq hosted at ``anchor`` (opaque, lossless round-trip)."""
        for f in self.fiqs:
            if f.anchor == anchor:
                return f
        raise KeyError(anchor)

    def tensor_leaves(self) -> List[Fiq]:
        return list(self.fiqs)


class Seed:
    """Epicyclic UCNS object (UCNS-in-UCNS): a grouping of circle carriers.

    Like the circle, its geometry is frozen scaffold; structure ascends,
    differentiability descends to the fiq payloads it ultimately contains.
    """

    __slots__ = ("circles", "routing_step", "anchor_order", "n_min", "face_state", "identity")

    def __init__(self, circles: Sequence[Circle], routing_step: int, identity: Optional[str] = None) -> None:
        self.circles: List[Circle] = list(circles)
        self.routing_step = routing_step
        self.anchor_order = tuple(heptagram_order(routing_step, len(self.circles)))
        self.n_min = len(self.circles)
        self.face_state = 0
        self.identity = identity

    @property
    def requires_grad(self) -> bool:
        return False

    def tensor_leaves(self) -> List[Fiq]:
        out: List[Fiq] = []
        for c in self.circles:
            out.extend(c.tensor_leaves())
        return out


class Core:
    """A full PTCA core: ``seed_count`` epicyclic seeds of circles of fiqs."""

    __slots__ = ("seeds", "spec")

    def __init__(self, seeds: Sequence[Seed], spec: CoreSpec) -> None:
        self.seeds: List[Seed] = list(seeds)
        self.spec = spec

    def tensor_leaves(self) -> List[Fiq]:
        out: List[Fiq] = []
        for s in self.seeds:
            out.extend(s.tensor_leaves())
        return out

    def scalars(self):
        out = []
        for f in self.tensor_leaves():
            out.extend(f.scalars())
        return out


def compose_circle(fiqs: Sequence[Fiq], *, routing_step: int = CIRCLE_ROUTING_STEP,
                   identity: Optional[str] = None) -> Circle:
    """{7/2} composition of tensors into a circle carrier (the ``⊠`` operator).

    Structural only: grafts the fiqs into a carrier and routes them; it creates
    no ``Scalar`` and therefore no ``∂(⊠)`` autodiff node.
    """
    return Circle(fiqs, routing_step=routing_step, identity=identity)


def compose_seed(circles: Sequence[Circle], *, routing_step: int = SEED_ROUTING_STEP,
                 identity: Optional[str] = None) -> Seed:
    """{7/3} epicyclic composition of circles into a seed (the ``⊠`` operator).

    Structural only, like ``compose_circle`` — no autodiff node is registered.
    """
    return Seed(circles, routing_step=routing_step, identity=identity)


def build_core(spec: Optional[CoreSpec] = None, *, init: float = 1.0) -> Core:
    """Construct a stratified PTCA core.

    Each fiq is grafted with a length-``tensor_dim`` scalar payload (opaque
    host). Tensors compose into circles via {7/2} and circles into seeds via
    {7/3}. ``init`` is the constant initial payload value (real initializers are
    a downstream concern).
    """
    spec = spec or CoreSpec()
    seeds: List[Seed] = []
    for s in range(spec.seed_count):
        circles: List[Circle] = []
        for c in range(spec.circles_per_seed):
            fiqs: List[Fiq] = []
            for t in range(spec.tensors_per_circle):
                values = [init] * spec.tensor_dim
                fiqs.append(wrap_tensor_fiq(values, anchor=t, identity=_carrier_identity(s, c, t)))
            circles.append(compose_circle(fiqs, routing_step=spec.circle_routing_step))
        seeds.append(compose_seed(circles, routing_step=spec.seed_routing_step))
    return Core(seeds, spec)
