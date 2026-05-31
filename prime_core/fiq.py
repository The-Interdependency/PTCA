"""fiq — the middle stratum object of a PTCA core.

    fiq  (n.)  the tensor holding the UCNS object.
               · first iterative qualifier
               · full isolated query
               · "future idiot's question"

A ``Fiq`` is the opaque-host graft of the three-stratum model (handoff §1.3):
a scalar-tensor payload grafted into a UCNS carrier anchor. The carrier
organizes; it does not interpret. Backprop stays sealed inside the scalar
payload — the carrier geometry is non-differentiable scaffold (handoff §1.2).

Gradient policy: differentiability descends to these payload scalars; the
UCNS composition operator ``⊠`` never touches a Scalar, so no ``∂(⊠)`` node is
ever registered on the autodiff tape.
"""
from __future__ import annotations

from typing import Callable, Iterable, List, Optional


class Scalar:
    """Minimal reverse-mode autodiff scalar — the ONLY differentiable leaf type.

    Differentiability descends to these payload scalars (handoff §1.2). Only
    scalar ops ('+', '*') ever create nodes; structural composition does not,
    which is what keeps ``∂(⊠)`` off the hot path.
    """

    __slots__ = ("data", "grad", "_backward", "_prev", "_op")

    def __init__(self, data: float, _children: Iterable["Scalar"] = (), _op: str = "") -> None:
        self.data: float = float(data)
        self.grad: float = 0.0
        self._backward: Callable[[], None] = lambda: None
        self._prev = tuple(_children)
        self._op = _op  # '' leaf | '+' | '*' — only scalar ops, never '⊠'

    def __add__(self, other: "Scalar | float") -> "Scalar":
        other = other if isinstance(other, Scalar) else Scalar(other)
        out = Scalar(self.data + other.data, (self, other), "+")

        def _backward() -> None:
            self.grad += out.grad
            other.grad += out.grad

        out._backward = _backward
        return out

    __radd__ = __add__

    def __mul__(self, other: "Scalar | float") -> "Scalar":
        other = other if isinstance(other, Scalar) else Scalar(other)
        out = Scalar(self.data * other.data, (self, other), "*")

        def _backward() -> None:
            self.grad += other.data * out.grad
            other.grad += self.data * out.grad

        out._backward = _backward
        return out

    __rmul__ = __mul__

    def backward(self) -> None:
        """Reverse-mode accumulation in iterative topological order.

        Iterative (explicit-stack) topo sort avoids Python's recursion limit on
        the large, deep graphs a full core can produce.
        """
        topo: List["Scalar"] = []
        visited = set()
        stack: List[tuple] = [(self, False)]
        while stack:
            node, processed = stack.pop()
            if processed:
                topo.append(node)
                continue
            if id(node) in visited:
                continue
            visited.add(id(node))
            stack.append((node, True))
            for child in node._prev:
                if id(child) not in visited:
                    stack.append((child, False))
        self.grad = 1.0
        for node in reversed(topo):
            node._backward()

    def __repr__(self) -> str:  # pragma: no cover - debug aid
        return f"Scalar(data={self.data:.6g}, grad={self.grad:.6g}, op={self._op!r})"


class Fiq:
    """Opaque-host graft: a length-``d`` scalar payload at a UCNS carrier anchor.

    'Opaque' means the host stores the payload verbatim and never interprets or
    re-encodes it (the rejected 'encode' branch, handoff §1.3). Round-trips are
    lossless: the payload retrieved equals the payload inserted.
    """

    __slots__ = ("anchor", "_payload", "identity")

    def __init__(self, payload: List[Scalar], anchor: int, identity: Optional[str] = None) -> None:
        self.anchor = anchor
        self._payload = list(payload)  # opaque: stored verbatim, never inspected
        self.identity = identity

    @property
    def payload(self) -> List[Scalar]:
        """Retrieve the hosted payload unchanged (lossless round-trip)."""
        return self._payload

    @property
    def requires_grad(self) -> bool:
        return True  # the payload is the differentiable leaf surface

    def scalars(self) -> List[Scalar]:
        return self._payload

    def __len__(self) -> int:
        return len(self._payload)


def wrap_tensor_fiq(
    values: Iterable["Scalar | float"],
    anchor: int,
    identity: Optional[str] = None,
) -> Fiq:
    """Graft a raw scalar vector into a fiq as an opaque host (handoff §1.3).

    Floats are lifted to ``Scalar`` leaves; existing ``Scalar`` objects are
    hosted as-is. The carrier does not transform the values — it hosts them.
    """
    payload = [v if isinstance(v, Scalar) else Scalar(v) for v in values]
    return Fiq(payload=payload, anchor=anchor, identity=identity)
