from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict
from datetime import datetime, timezone

from qviraex.quantum import (
    ObservableTerm,
    OptimizerSpec,
    QuantumIntegrationProtocol,
    QuantumProtocolError,
    QuantumRunRequest,
)
from qviraex.quantum.providers import FireOpalIBMProvider


def build_variational_circuit() -> tuple[str, tuple[str, ...]]:
    """Build the three-qubit ansatz from the uploaded Fire Opal VQE notebook."""
    try:
        from qiskit import QuantumCircuit, qasm3
        from qiskit.circuit.library import TwoLocal
    except ImportError as exc:
        raise RuntimeError(
            "Install the optional execution dependencies with: "
            "python -m pip install fire-opal qiskit scipy"
        ) from exc

    initial_state = QuantumCircuit(3)
    initial_state.x(0)
    initial_state.x(2)
    initial_state.barrier()

    circuit = TwoLocal(
        num_qubits=3,
        rotation_blocks=["ry"],
        entanglement_blocks="cx",
        entanglement="full",
        initial_state=initial_state,
        reps=1,
        flatten=True,
        insert_barriers=True,
    )
    circuit.barrier()

    # H = ZIX - 0.5 ZXI + 0.5 IXX.
    # Rotate the X-measured qubits into the computational basis.
    circuit.h(1)
    circuit.h(2)
    circuit.measure_all()

    parameter_names = tuple(parameter.name for parameter in circuit.parameters)
    if len(parameter_names) != 6:
        raise RuntimeError(
            f"Expected six variational parameters, received {len(parameter_names)}."
        )

    return qasm3.dumps(circuit), parameter_names


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the MirrorME QIP-0.1 VQE workload through Fire Opal on IBM Quantum."
    )
    parser.add_argument(
        "--backend",
        default=os.environ.get("IBM_QUANTUM_BACKEND"),
        help="Supported IBM backend name. May also be set with IBM_QUANTUM_BACKEND.",
    )
    parser.add_argument("--shots", type=int, default=2048)
    parser.add_argument("--max-iterations", type=int, default=30)
    parser.add_argument("--tolerance", type=float, default=0.01)
    parser.add_argument("--operator", default="VIREAX")
    parser.add_argument(
        "--session-id",
        default=f"VX-QIP-VQE-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
    )
    parser.add_argument(
        "--approve-hardware",
        action="store_true",
        help="Required explicit authorization for external QPU execution.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.backend:
        raise SystemExit(
            "Missing backend. Pass --backend NAME or set IBM_QUANTUM_BACKEND."
        )
    if not args.approve_hardware:
        raise SystemExit(
            "Hardware execution not approved. Re-run with --approve-hardware after reviewing the workload."
        )

    qasm_circuit, parameter_names = build_variational_circuit()
    initial_parameters = tuple(0.0 for _ in parameter_names)

    request = QuantumRunRequest(
        session_id=args.session_id,
        operator=args.operator,
        circuit_qasm=qasm_circuit,
        qubit_count=3,
        mode="variational",
        provider="fire_opal_ibm",
        backend_name=args.backend,
        shots=args.shots,
        parameters={name: 0.0 for name in parameter_names},
        observables=(
            ObservableTerm("ZIX", 1.0),
            ObservableTerm("ZXI", -0.5),
            ObservableTerm("IXX", 0.5),
        ),
        optimizer=OptimizerSpec(
            name="COBYLA",
            max_iterations=args.max_iterations,
            tolerance=args.tolerance,
            initial_parameters=initial_parameters,
        ),
        hardware_execution=True,
        human_approved=True,
        metadata={
            "experiment": "MirrorME VQE reference",
            "source": "uploaded Fire Opal custom variational algorithms notebook",
            "ideal_ground_energy": -2.0,
            "ansatz": "Three-qubit TwoLocal RY/CX, full entanglement, one repetition",
        },
    )

    try:
        receipt = QuantumIntegrationProtocol().execute(
            request,
            FireOpalIBMProvider(),
        )
    except QuantumProtocolError as exc:
        raise SystemExit(f"QIP execution rejected: {exc}") from exc

    print(json.dumps(asdict(receipt), indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
