from __future__ import annotations

from qviraex.quantum import (
    ObservableTerm,
    OptimizerSpec,
    QuantumIntegrationProtocol,
    QuantumRunRequest,
)
from qviraex.quantum.providers import FireOpalIBMProvider


QASM3 = """OPENQASM 3.0;
include "stdgates.inc";
bit[3] c;
qubit[3] q;
// Replace this body with the parameterized, basis-rotated VQE circuit.
c[0] = measure q[0];
c[1] = measure q[1];
c[2] = measure q[2];
"""


def main() -> None:
    request = QuantumRunRequest(
        session_id="VX-QIP-VQE-001",
        operator="VIREAX",
        circuit_qasm=QASM3,
        qubit_count=3,
        mode="variational",
        provider="fire_opal_ibm",
        backend_name="REPLACE_WITH_SUPPORTED_IBM_BACKEND",
        shots=2048,
        observables=(
            ObservableTerm("ZIX", 1.0),
            ObservableTerm("ZXI", -0.5),
            ObservableTerm("IXX", 0.5),
        ),
        optimizer=OptimizerSpec(
            name="COBYLA",
            max_iterations=30,
            tolerance=0.01,
            initial_parameters=(0.0,) * 6,
        ),
        hardware_execution=True,
        human_approved=True,
        metadata={
            "experiment": "MirrorME VQE reference",
            "ideal_ground_energy": -2.0,
        },
    )

    receipt = QuantumIntegrationProtocol().execute(
        request,
        FireOpalIBMProvider(),
    )
    print(receipt)


if __name__ == "__main__":
    main()
