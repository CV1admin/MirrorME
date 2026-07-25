from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal, Mapping, Protocol, Sequence


RunMode = Literal["sample", "expectation", "variational"]
ProviderName = Literal["local", "qiskit", "ibm_quantum", "fire_opal_ibm"]
RunStatus = Literal["completed", "submitted", "failed"]

_SECRET_MARKERS = (
    "api_key",
    "apikey",
    "authorization",
    "credential",
    "password",
    "secret",
    "token",
)


class QuantumProtocolError(ValueError):
    """Raised when a run violates the MirrorME quantum execution contract."""


@dataclass(frozen=True)
class ObservableTerm:
    """One real-weighted Pauli word in a Hamiltonian or cost observable."""

    pauli: str
    coefficient: float

    def validate(self, qubit_count: int) -> None:
        label = self.pauli.upper()
        if len(label) != qubit_count:
            raise QuantumProtocolError(
                f"Observable {self.pauli!r} has length {len(label)}; "
                f"expected {qubit_count}."
            )
        if any(symbol not in "IXYZ" for symbol in label):
            raise QuantumProtocolError(
                f"Observable {self.pauli!r} contains symbols outside I, X, Y, Z."
            )
        if not math.isfinite(self.coefficient):
            raise QuantumProtocolError("Observable coefficients must be finite real numbers.")


@dataclass(frozen=True)
class OptimizerSpec:
    """Classical optimizer declaration for a variational quantum run."""

    name: str = "COBYLA"
    max_iterations: int = 30
    tolerance: float = 0.01
    initial_parameters: tuple[float, ...] = ()

    def validate(self) -> None:
        if not self.name.strip():
            raise QuantumProtocolError("Optimizer name cannot be empty.")
        if not 1 <= self.max_iterations <= 100_000:
            raise QuantumProtocolError("max_iterations must be between 1 and 100000.")
        if not math.isfinite(self.tolerance) or self.tolerance <= 0:
            raise QuantumProtocolError("Optimizer tolerance must be finite and positive.")
        if any(not math.isfinite(value) for value in self.initial_parameters):
            raise QuantumProtocolError("Initial optimizer parameters must be finite.")


@dataclass(frozen=True)
class QuantumRunRequest:
    """Canonical, credential-free request sent across the quantum boundary."""

    session_id: str
    operator: str
    circuit_qasm: str
    qubit_count: int
    mode: RunMode = "sample"
    provider: ProviderName = "local"
    backend_name: str = "local-reference"
    qasm_version: Literal["2.0", "3.0"] = "3.0"
    shots: int = 2048
    parameters: Mapping[str, float] = field(default_factory=dict)
    observables: tuple[ObservableTerm, ...] = ()
    optimizer: OptimizerSpec | None = None
    seed: int | None = 7
    hardware_execution: bool = False
    human_approved: bool = False
    metadata: Mapping[str, Any] = field(default_factory=dict)
    protocol_version: str = "QIP-0.1"

    def validate(self) -> None:
        if self.protocol_version != "QIP-0.1":
            raise QuantumProtocolError(
                f"Unsupported protocol version: {self.protocol_version!r}."
            )
        if not self.session_id.strip() or not self.operator.strip():
            raise QuantumProtocolError("session_id and operator are required.")
        if not 1 <= self.qubit_count <= 10_000:
            raise QuantumProtocolError("qubit_count must be between 1 and 10000.")
        if not 1 <= self.shots <= 1_000_000:
            raise QuantumProtocolError("shots must be between 1 and 1000000.")
        if self.seed is not None and self.seed < 0:
            raise QuantumProtocolError("seed must be non-negative when supplied.")
        if not self.backend_name.strip():
            raise QuantumProtocolError("backend_name is required.")

        qasm = self.circuit_qasm.lstrip()
        expected_header = f"OPENQASM {self.qasm_version};"
        if not qasm.startswith(expected_header):
            raise QuantumProtocolError(
                f"Circuit must begin with {expected_header!r}."
            )

        for name, value in self.parameters.items():
            if not str(name).strip() or not math.isfinite(float(value)):
                raise QuantumProtocolError("Parameters require non-empty names and finite values.")

        for observable in self.observables:
            observable.validate(self.qubit_count)

        if self.mode in {"expectation", "variational"} and not self.observables:
            raise QuantumProtocolError(f"{self.mode} mode requires at least one observable.")
        if self.mode == "variational":
            if self.optimizer is None:
                raise QuantumProtocolError("variational mode requires an optimizer specification.")
            self.optimizer.validate()

        hardware_provider = self.provider in {"ibm_quantum", "fire_opal_ibm"}
        if hardware_provider and not self.hardware_execution:
            raise QuantumProtocolError(
                "Hardware provider selected without hardware_execution=True."
            )
        if self.hardware_execution and not self.human_approved:
            raise QuantumProtocolError(
                "Quantum hardware execution requires explicit human approval."
            )
        if self.provider == "local" and self.hardware_execution:
            raise QuantumProtocolError("The local provider cannot be marked as hardware execution.")

        _reject_secret_material(asdict(self))


@dataclass(frozen=True)
class PreparedQuantumRun:
    """Validated request plus its deterministic canonical digest."""

    request: QuantumRunRequest
    request_digest: str
    canonical_request: str


@dataclass(frozen=True)
class ProviderResult:
    """Normalized output returned by a concrete execution provider."""

    status: RunStatus
    job_id: str
    results: Mapping[str, Any]
    execution_metadata: Mapping[str, Any] = field(default_factory=dict)


class QuantumExecutionProvider(Protocol):
    """Interface implemented by local, IBM, or Fire Opal adapters."""

    name: str

    def execute(self, prepared: PreparedQuantumRun) -> ProviderResult:
        """Execute one validated run and return normalized provider data."""


@dataclass(frozen=True)
class ExecutionReceipt:
    """Auditable receipt binding a request digest to normalized result data."""

    protocol_version: str
    session_id: str
    provider: str
    backend_name: str
    mode: RunMode
    status: RunStatus
    job_id: str
    shots: int
    request_digest: str
    result_digest: str
    results: Mapping[str, Any]
    execution_metadata: Mapping[str, Any]
    created_at_utc: str


@dataclass
class QuantumIntegrationProtocol:
    """Prepare, authorize, execute, and verify governed quantum workloads."""

    def prepare(self, request: QuantumRunRequest) -> PreparedQuantumRun:
        request.validate()
        canonical = canonical_json(asdict(request))
        return PreparedQuantumRun(
            request=request,
            request_digest=sha256_text(canonical),
            canonical_request=canonical,
        )

    def execute(
        self,
        request: QuantumRunRequest,
        provider: QuantumExecutionProvider,
    ) -> ExecutionReceipt:
        prepared = self.prepare(request)
        if provider.name != request.provider:
            raise QuantumProtocolError(
                f"Provider adapter {provider.name!r} does not match request provider "
                f"{request.provider!r}."
            )

        provider_result = provider.execute(prepared)
        _reject_secret_material(provider_result.execution_metadata)
        _reject_secret_material(provider_result.results)

        normalized_result = {
            "status": provider_result.status,
            "job_id": provider_result.job_id,
            "results": provider_result.results,
            "execution_metadata": provider_result.execution_metadata,
        }
        result_digest = sha256_text(canonical_json(normalized_result))
        return ExecutionReceipt(
            protocol_version=request.protocol_version,
            session_id=request.session_id,
            provider=request.provider,
            backend_name=request.backend_name,
            mode=request.mode,
            status=provider_result.status,
            job_id=provider_result.job_id,
            shots=request.shots,
            request_digest=prepared.request_digest,
            result_digest=result_digest,
            results=provider_result.results,
            execution_metadata=provider_result.execution_metadata,
            created_at_utc=datetime.now(timezone.utc).isoformat(),
        )

    @staticmethod
    def verify_receipt(receipt: ExecutionReceipt) -> bool:
        normalized_result = {
            "status": receipt.status,
            "job_id": receipt.job_id,
            "results": receipt.results,
            "execution_metadata": receipt.execution_metadata,
        }
        return sha256_text(canonical_json(normalized_result)) == receipt.result_digest


def expectation_from_probabilities(
    probabilities: Mapping[str, float],
    observables: Sequence[ObservableTerm],
) -> float:
    """Evaluate commuting Pauli-Z-basis terms from bitstring probabilities.

    The circuit must already contain the basis rotations needed to map every requested
    Pauli term to computational-basis measurements. Bitstrings and Pauli labels use the
    same left-to-right order, matching Qiskit count keys and Pauli labels.
    """

    if not probabilities:
        raise QuantumProtocolError("Probability distribution cannot be empty.")
    qubit_count = len(next(iter(probabilities)))
    total_probability = 0.0
    for bitstring, probability in probabilities.items():
        if len(bitstring) != qubit_count or any(bit not in "01" for bit in bitstring):
            raise QuantumProtocolError(f"Invalid bitstring: {bitstring!r}.")
        if not math.isfinite(probability) or probability < 0:
            raise QuantumProtocolError("Probabilities must be finite and non-negative.")
        total_probability += probability
    if not math.isclose(total_probability, 1.0, rel_tol=1e-9, abs_tol=1e-9):
        raise QuantumProtocolError(
            f"Probabilities must sum to 1; received {total_probability:.12g}."
        )

    for observable in observables:
        observable.validate(qubit_count)
        if any(symbol not in "IZ" for symbol in observable.pauli.upper()):
            raise QuantumProtocolError(
                "expectation_from_probabilities requires basis-rotated I/Z observables."
            )

    expectation = 0.0
    for observable in observables:
        term_expectation = 0.0
        for bitstring, probability in probabilities.items():
            eigenvalue = 1
            for symbol, bit in zip(observable.pauli.upper(), bitstring):
                if symbol == "Z" and bit == "1":
                    eigenvalue *= -1
            term_expectation += eigenvalue * probability
        expectation += observable.coefficient * term_expectation
    return expectation


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=_json_default,
    )


def sha256_text(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def _json_default(value: Any) -> Any:
    if isinstance(value, tuple):
        return list(value)
    raise TypeError(f"Unsupported canonical JSON value: {type(value).__name__}")


def _reject_secret_material(value: Any, path: str = "payload") -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            normalized = str(key).lower().replace("-", "_")
            if any(marker in normalized for marker in _SECRET_MARKERS):
                raise QuantumProtocolError(
                    f"Credential-like field {path}.{key} is forbidden in protocol payloads."
                )
            _reject_secret_material(item, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _reject_secret_material(item, f"{path}[{index}]")
