"""
ptca-lib — Prime Tensor Core Architecture

Zero-dependency pure-Python library implementing:

  * 53-prime-node × 9-sentinel × 8-phase × 7-slot tensor schema
  * Nine sentinel channels (S1_PROVENANCE … S9_AUDIT)
  * SHA-256 provenance hashing and chain verification
  * Exchange mechanics (delta, alpha, beta, gamma constants)
  * PTCAInstance — a PTCA-aware stateful model session

Quick start
-----------
::

    from ptca import PTCAInstance

    inst = PTCAInstance(model_id="claude-sonnet-4-6", caller_id="user:alice")
    inst.push_context({"role": "user", "content": "Hello", "tokens": 5})
    result = inst.route(node=0, phase=0, slot=0, s1=1.0, s5=0.9)
    print(inst.snapshot())
"""

from ptca.constants import (
    NODES,
    SENTINELS,
    PHASES,
    SLOTS,
    DELTA,
    ALPHA,
    BETA,
    GAMMA,
    AGG6,
    AGG_SEEDS,
    SENTINEL_NAMES,
    SENTINEL_INDEX,
    SENTINEL_WEIGHTS,
)
from ptca.exchange import Exchange, ExchangeResult, compute_score, aggregate_seeds
from ptca.instance import PTCAInstance
from ptca.primes import PRIME_NODES, PRIME_TO_NODE, node_for_prime, prime_for_node
from ptca.provenance import (
    build_block,
    hash_block,
    chain_hashes,
    verify_chain,
    extend_chain,
)
from ptca.sentinels import (
    SentinelState,
    S1ProvenanceState,
    S2PolicyState,
    S3BoundsState,
    S4ApprovalState,
    S5ContextState,
    S6IdentityState,
    S7MemoryState,
    S8RiskState,
    S9AuditState,
)
from ptca.tensor import PTCATensor

__version__ = "0.1.0"
__all__ = [
    # constants
    "NODES", "SENTINELS", "PHASES", "SLOTS",
    "DELTA", "ALPHA", "BETA", "GAMMA",
    "AGG6", "AGG_SEEDS",
    "SENTINEL_NAMES", "SENTINEL_INDEX", "SENTINEL_WEIGHTS",
    # primes
    "PRIME_NODES", "PRIME_TO_NODE", "node_for_prime", "prime_for_node",
    # provenance
    "build_block", "hash_block", "chain_hashes", "verify_chain", "extend_chain",
    # sentinels
    "SentinelState",
    "S1ProvenanceState", "S2PolicyState", "S3BoundsState", "S4ApprovalState",
    "S5ContextState", "S6IdentityState", "S7MemoryState", "S8RiskState", "S9AuditState",
    # tensor
    "PTCATensor",
    # exchange
    "Exchange", "ExchangeResult", "compute_score", "aggregate_seeds",
    # instance
    "PTCAInstance",
    # version
    "__version__",
]
