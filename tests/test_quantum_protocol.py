from __future__ import annotations

import unittest
from dataclasses import replace

from qviraex.quantum import (
    ObservableTerm,
    OptimizerSpec,
    QuantumIntegrationProtocol,
    QuantumProtocolError,
    QuantumRunRequest,
    expectation_from_probabilities,
)
from qviraex.quantum.providers import LocalDeterministicProvider


QASM3 = """OPENQASM 3.0;
bit[3] c;
qubit[3] q;
c[0] = measure q[0];
c[1] = measure q[1];
c[2] = measure q[2];
"""


class QuantumIntegrationProtocolTest(unittest.TestCase):
    def make_request(self) -> QuantumRunRequest:
        return QuantumRunRequest(
            session_id="VX-QIP-1",
            operator="VIREAX",
            circuit_qasm=QASM3,
            qubit_count=3,
            mode="variational",
            provider="local",
            backend_name="local-reference",
            shots=2048,
            parameters={f"theta{index}": 0.0 for index in range(6)},
            observables=(
                ObservableTerm("ZIX", 1.0),
                ObservableTerm("ZXI", -0.5),
                ObservableTerm("IXX", 0.5),
            ),
            optimizer=OptimizerSpec(initial_parameters=(0.0,) * 6),
            human_approved=False,
            hardware_execution=False,
            metadata={"source": "uploaded Fire Opal VQE notebook"},
        )

    def test_prepare_is_deterministic(self) -> None:
        protocol = QuantumIntegrationProtocol()
        first = protocol.prepare(self.make_request())
        second = protocol.prepare(self.make_request())
        self.assertEqual(first.request_digest, second.request_digest)
        self.assertTrue(first.request_digest.startswith("sha256:"))

    def test_hardware_requires_explicit_human_approval(self) -> None:
        request = replace(
            self.make_request(),
            provider="fire_opal_ibm",
            backend_name="ibm_backend",
            hardware_execution=True,
            human_approved=False,
        )
        with self.assertRaisesRegex(QuantumProtocolError, "human approval"):
            request.validate()

    def test_variational_mode_requires_parameter_mapping(self) -> None:
        request = replace(self.make_request(), parameters={})
        with self.assertRaisesRegex(QuantumProtocolError, "parameter mapping"):
            request.validate()

    def test_secret_fields_are_rejected(self) -> None:
        request = replace(
            self.make_request(),
            metadata={"api_key": "must-not-cross-boundary"},
        )
        with self.assertRaisesRegex(QuantumProtocolError, "Credential-like field"):
            request.validate()

    def test_provider_must_match_request(self) -> None:
        provider = LocalDeterministicProvider(results={"probabilities": {"000": 1.0}})
        request = replace(
            self.make_request(),
            provider="qiskit",
            hardware_execution=False,
        )
        with self.assertRaisesRegex(QuantumProtocolError, "does not match"):
            QuantumIntegrationProtocol().execute(request, provider)

    def test_receipt_detects_result_mutation(self) -> None:
        protocol = QuantumIntegrationProtocol()
        receipt = protocol.execute(
            self.make_request(),
            LocalDeterministicProvider(results={"expectation_value": -2.0}),
        )
        self.assertTrue(protocol.verify_receipt(receipt))
        mutated = replace(receipt, results={"expectation_value": 99.0})
        self.assertFalse(protocol.verify_receipt(mutated))

    def test_basis_rotated_expectation(self) -> None:
        probabilities = {"000": 0.5, "111": 0.5}
        observables = (
            ObservableTerm("ZII", 1.0),
            ObservableTerm("IZZ", 0.5),
        )
        self.assertAlmostEqual(
            expectation_from_probabilities(probabilities, observables),
            0.5,
        )

    def test_probability_normalization_is_enforced(self) -> None:
        with self.assertRaisesRegex(QuantumProtocolError, "sum to 1"):
            expectation_from_probabilities(
                {"000": 0.2, "111": 0.2},
                (ObservableTerm("ZII", 1.0),),
            )


if __name__ == "__main__":
    unittest.main()
