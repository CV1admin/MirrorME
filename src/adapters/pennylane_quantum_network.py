"""
MIRRORME_PENNYLANE_QUANTUM_NETWORK v0.1-draft

Optional PennyLane-powered hybrid quantum-classical simulation layer for MirrorMe.

Boundary:
- This module is optional and is not imported by the Vite frontend.
- It requires local Python dependencies: pennylane and torch.
- It creates differentiable simulated quantum circuits, not physical quantum channels.
- Hardware execution requires separate provider plugins, credentials, and explicit runtime verification.
"""

from __future__ import annotations

import hashlib
import json
import secrets
import time
from dataclasses import asdict, dataclass
from typing import Any, Optional

try:
    import pennylane as qml
    import torch
    import torch.nn as nn
except ImportError as exc:  # pragma: no cover - dependency boundary
    qml = None  # type: ignore[assignment]
    torch = None  # type: ignore[assignment]
    nn = None  # type: ignore[assignment]
    _IMPORT_ERROR: Optional[ImportError] = exc
else:
    _IMPORT_ERROR = None


@dataclass(frozen=True)
class PennyLaneQuantumNode:
    node_id: str
    model_type: str
    wires: int
    device_type: str
    capabilities: list[str]
    created_unix: float


@dataclass(frozen=True)
class QuantumExecutionRecord:
    key: str
    node_id: str
    result: Any
    digest: str
    timestamp_unix: float
    version: str = "v1"


class PennyLaneDependencyError(RuntimeError):
    """Raised when PennyLane/Torch functionality is requested without dependencies."""


class PennyLaneQuantumNetwork:
    """Local hybrid quantum-classical simulation registry.

    The network stores PennyLane node metadata and creates differentiable QNodes.
    It deliberately avoids claiming physical quantum networking.
    """

    def __init__(self, default_wires: int = 4, default_device: str = "lightning.qubit") -> None:
        if default_wires < 1:
            raise ValueError("default_wires must be >= 1")
        self.default_wires = default_wires
        self.default_device = default_device
        self.nodes: dict[str, PennyLaneQuantumNode] = {}
        self.tensor_memory: dict[str, QuantumExecutionRecord] = {}

    def create_quantum_node(
        self,
        model_type: str = "hybrid-qnn",
        wires: Optional[int] = None,
        device: Optional[str] = None,
    ) -> PennyLaneQuantumNode:
        """Register a PennyLane-powered simulated quantum node."""
        resolved_wires = wires or self.default_wires
        if resolved_wires < 1:
            raise ValueError("wires must be >= 1")

        resolved_device = device or self.default_device
        node_id = self._node_id(model_type=model_type, wires=resolved_wires, device=resolved_device)
        node = PennyLaneQuantumNode(
            node_id=node_id,
            model_type=model_type,
            wires=resolved_wires,
            device_type=resolved_device,
            capabilities=["qnn", "variational", "hybrid-torch", "tensor-memory", "simulation"],
            created_unix=time.time(),
        )
        self.nodes[node_id] = node
        return node

    def create_qnode(self, node_id: str, interface: str = "torch"):
        """Create a differentiable PennyLane QNode for the given node."""
        self._require_dependencies()
        node = self._get_node(node_id)
        dev = self._make_device(node)

        @qml.qnode(dev, interface=interface)  # type: ignore[union-attr]
        def circuit(inputs, weights):
            # Classical-to-quantum encoding.
            # TorchLayer passes `inputs` by name. Batch-aware indexing is used.
            for wire in range(node.wires):
                qml.RY(inputs[..., wire], wires=wire)  # type: ignore[union-attr]

            qml.StronglyEntanglingLayers(weights, wires=range(node.wires))  # type: ignore[union-attr]
            return qml.expval(qml.PauliZ(0))  # type: ignore[union-attr]

        return circuit

    def hybrid_model(
        self,
        node_id: str,
        n_layers: int = 3,
        output_dim: int = 2,
    ):
        """Return a PyTorch model with one PennyLane quantum layer and a linear head."""
        self._require_dependencies()
        node = self._get_node(node_id)
        qnode = self.create_qnode(node_id=node_id, interface="torch")
        weight_shapes = {"weights": (n_layers, node.wires, 3)}

        class HybridModel(nn.Module):  # type: ignore[union-attr]
            def __init__(self) -> None:
                super().__init__()
                self.qlayer = qml.qnn.TorchLayer(qnode, weight_shapes)  # type: ignore[union-attr]
                self.clayer = nn.Linear(1, output_dim)  # type: ignore[union-attr]

            def forward(self, x):
                if x.shape[-1] < node.wires:
                    raise ValueError(f"input feature dimension must be >= node.wires ({node.wires})")
                x = x[..., : node.wires]
                q_out = self.qlayer(x)
                if q_out.ndim == 0:
                    q_out = q_out.reshape(1, 1)
                elif q_out.ndim == 1:
                    q_out = q_out.unsqueeze(-1)
                return self.clayer(q_out)

        return HybridModel()

    def store_quantum_state(self, key: str, node_id: str, result: Any) -> QuantumExecutionRecord:
        """Store quantum execution output or model output in tensor memory."""
        self._get_node(node_id)
        serializable_result = self._to_serializable(result)
        record = QuantumExecutionRecord(
            key=key,
            node_id=node_id,
            result=serializable_result,
            digest=self._digest(serializable_result),
            timestamp_unix=time.time(),
        )
        self.tensor_memory[key] = record
        return record

    def get_quantum_state(self, key: str) -> Optional[QuantumExecutionRecord]:
        return self.tensor_memory.get(key)

    def network_status(self) -> dict[str, Any]:
        dependency_status = "available" if _IMPORT_ERROR is None else f"missing: {_IMPORT_ERROR.name}"
        return {
            "active_nodes": len(self.nodes),
            "tensor_entries": len(self.tensor_memory),
            "dependency_status": dependency_status,
            "default_wires": self.default_wires,
            "default_device": self.default_device,
            "available_device_hints": ["default.qubit", "lightning.qubit", "lightning.gpu"],
            "boundary": "PennyLane simulation only unless a verified hardware plugin is configured.",
            "nodes": {node_id: asdict(node) for node_id, node in self.nodes.items()},
        }

    def _make_device(self, node: PennyLaneQuantumNode):
        try:
            return qml.device(node.device_type, wires=node.wires)  # type: ignore[union-attr]
        except Exception:
            # Keep the stub usable when lightning is not installed.
            return qml.device("default.qubit", wires=node.wires)  # type: ignore[union-attr]

    def _get_node(self, node_id: str) -> PennyLaneQuantumNode:
        try:
            return self.nodes[node_id]
        except KeyError as exc:
            raise ValueError(f"node not found: {node_id}") from exc

    @staticmethod
    def _require_dependencies() -> None:
        if _IMPORT_ERROR is not None:
            raise PennyLaneDependencyError(
                "PennyLane quantum simulation dependencies are missing. "
                "Install the optional quantum requirements before using QNodes."
            ) from _IMPORT_ERROR

    @staticmethod
    def _node_id(model_type: str, wires: int, device: str) -> str:
        entropy = f"{model_type}:{wires}:{device}:{time.time_ns()}:{secrets.token_hex(8)}"
        return f"pl_{hashlib.sha256(entropy.encode()).hexdigest()[:12]}"

    @staticmethod
    def _to_serializable(value: Any) -> Any:
        if torch is not None and hasattr(value, "detach"):
            return value.detach().cpu().numpy().tolist()
        if hasattr(value, "tolist"):
            return value.tolist()
        return value

    @staticmethod
    def _digest(value: Any) -> str:
        canonical = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    qnet = PennyLaneQuantumNetwork(default_wires=4)
    node = qnet.create_quantum_node("grok-mirror-qnn", wires=4, device="lightning.qubit")
    print(f"Created PennyLane node: {node.node_id}")
    print(json.dumps(qnet.network_status(), indent=2, default=str))

    if _IMPORT_ERROR is None:
        model = qnet.hybrid_model(node.node_id)
        test_input = torch.tensor([[0.1, 0.2, 0.3, 0.4]], dtype=torch.float32)  # type: ignore[union-attr]
        output = model(test_input)
        qnet.store_quantum_state("test_run_1", node.node_id, output)
        print(json.dumps(qnet.network_status(), indent=2, default=str))
    else:
        print("Optional PennyLane/Torch dependencies are not installed; skipped forward pass.")
