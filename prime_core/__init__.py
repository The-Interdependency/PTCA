"""prime_core — three-stratum PTCA core (tensor / circle / seed).

Public surface (handoff §2 MODULE_BUILD):
    build_core, CoreSpec

The stratification: scalar ``Fiq`` payloads are grafted into UCNS *circle*
carriers (opaque hosts) and composed into epicyclic *seeds*. Differentiability
descends to the scalar payloads; UCNS geometry is non-differentiable scaffold.

This package is independent of the published ``ptca-lib`` (flat 4-D tensor) and
does not modify it.
"""
from __future__ import annotations

from .constants import (
    CIRCLE_ROUTING_STEP,
    CIRCLES_PER_SEED,
    PARAM_COUNT,
    SEED_COUNT,
    SEED_ROUTING_STEP,
    TENSOR_DIM,
    TENSOR_LEAVES,
    TENSORS_PER_CIRCLE,
    is_coherence_prime,
)
from .core import (
    Circle,
    Core,
    CoreSpec,
    Seed,
    build_core,
    compose_circle,
    compose_seed,
    heptagram_order,
)
from .fiq import Fiq, Scalar, wrap_tensor_fiq

__all__ = [
    # public surface
    "build_core",
    "CoreSpec",
    # strata
    "Core",
    "Seed",
    "Circle",
    "Fiq",
    "Scalar",
    # composition
    "compose_circle",
    "compose_seed",
    "wrap_tensor_fiq",
    "heptagram_order",
    # constants / guard
    "SEED_COUNT",
    "CIRCLES_PER_SEED",
    "TENSORS_PER_CIRCLE",
    "TENSOR_DIM",
    "TENSOR_LEAVES",
    "PARAM_COUNT",
    "CIRCLE_ROUTING_STEP",
    "SEED_ROUTING_STEP",
    "is_coherence_prime",
]
