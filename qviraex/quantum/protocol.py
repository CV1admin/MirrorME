from __future__ import annotations

import hashlib
import json
import math
import random
from dataclasses import asdict, dataclass, field, replace
from datetime import datetime, timezone
from statistics import NormalDist
from typing import Any, Literal, Mapping, Protocol, Sequence


RunMode = Literal["sample", "expectation", "variational"]
ProviderName = Literal["local", "qiskit", "ibm_quantum", "fire_opal_ibm"]
RunStatus = Literal["completed", "submitted", "failed"]
DuplicateObservablePolicy = Literal["aggregate", "reject"]

_SECRET_MARKERS = (
    "api_key",
    "apikey",
    "authorization",
    "credential",
    "password",
    "secret",
    "token",
)

_SUPPORTED_PROTOCOL_VERSIONS = {"QIP-0.1"}
_SUPPORTED_QUBIT_ORDER = "pauli_label_left_to_right_matches_result_bitstrings"
_SUPPORTED_BASIS_ROTATION = "caller_pre_rotates_each_measurement_group_to_z_basis"
_HOEFFDING_ASSUMPTIONS = (
    "independent shots",
    "bounded Pauli outcomes in [-1, 1]",
    "fixed circuit and observable definition",
    "fixed calibration interval for hardware data",
    "no unmodelled mitigation bias",
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
    duplicate_observable_policy: DuplicateObservablePolicy = "aggregate"
    qubit_order_convention: str = _SUPPORTED_QUBIT_ORDER
    basis_rotation_convention: str = _SUPPORTED_BASIS_ROTATION
    protocol_version: str = "QIP-0.1"

    def validate(self) -> None:
        if self.protocol_version not in _SUPPORTED_PROTOCOL_VERSIONS:
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
        if self.duplicate_observable_policy not in {"aggregate", "reject"}:
            raise QuantumProtocolError("duplicate_observable_policy must be aggregate or reject.")
        if self.qubit_order_convention != _SUPPORTED_QUBIT_ORDER:
            raise QuantumProtocolError(
                f"Unsupported qubit_order_convention: {self.qubit_order_convention!r}."
            )
        if self.basis_rotation_convention != _SUPPORTED_BASIS_ROTATION:
            raise QuantumProtocolError(
                f"Unsupported basis_rotation_convention: {self.basis_rotation_convention!r}."
            )

        qasm = self.circuit_qasm.lstrip()
        expected_header = f"OPENQASM {self.qasm_version};"
        if not qasm.startswith(expected_header):
            raise QuantumProtocolError(
                f"Circuit must begin with {expected_header!r}."
            )

        for name, value in self.parameters.items():
            if not str(name).strip() or not math.isfinite(float(value)):
                raise QuantumProtocolError("Parameters require non-empty names and finite values.")

        normalize_observables(
            self.observables,
            self.qubit_count,
            duplicate_policy=self.duplicate_observable_policy,
        )

        if self.mode in {"expectation", "variational"} and not self.observables:
            raise QuantumProtocolError(f"{self.mode} mode requires at least one observable.")
        if self.mode == "variational":
            if self.optimizer is None:
                raise QuantumProtocolError("variational mode requires an optimizer specification.")
            self.optimizer.validate()
            if not self.parameters:
                raise QuantumProtocolError(
                    "variational mode requires an ordered parameter mapping."
                )
            if self.optimizer.initial_parameters and (
                len(self.optimizer.initial_parameters) != len(self.parameters)
            ):
                raise QuantumProtocolError(
                    "initial parameter count must match the declared parameter mapping."
                )

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


class AuditLedgerProtocol(Protocol):
    records: list[Any]

    def commit(self, payload: Mapping[str, Any]) -> Any:
        ...

    def verify(self) -> bool:
        ...


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
    audit_anchor: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class UncertaintyReport:
    """Separates a theoretical concentration bound from empirical variance."""

    method: str
    confidence_level: float
    half_width: float
    theoretical_variance_proxy: float
    empirical_variance_of_estimator: float | None
    shots_by_observable: Mapping[str, int]
    assumptions: tuple[str, ...]
    interpretation: str


@dataclass
class QuantumIntegrationProtocol:
    """Prepare, authorize, execute, verify, and optionally anchor quantum workloads."""

    audit_ledger: AuditLedgerProtocol | None = None
    audit_anchoring_enabled: bool = True

    def prepare(self, request: QuantumRunRequest) -> PreparedQuantumRun:
        request.validate()
        normalized_request = replace(
            request,
            observables=normalize_observables(
                request.observables,
                request.qubit_count,
                duplicate_policy=request.duplicate_observable_policy,
            ),
        )
        canonical = canonical_json(asdict(normalized_request))
        return PreparedQuantumRun(
            request=normalized_request,
            request_digest=sha256_text(canonical),
            canonical_request=canonical,
        )

    def execute(
        self,
        request: QuantumRunRequest,
        provider: QuantumExecutionProvider,
    ) -> ExecutionReceipt:
        prepared = self.prepare(request)
        request = prepared.request
        if provider.name != request.provider:
            raise QuantumProtocolError(
                f"Provider adapter {provider.name!r} does not match request provider "
                f"{request.provider!r}."
            )

        provider_result = provider.execute(prepared)
        _reject_secret_material(provider_result.execution_metadata)
        _reject_secret_material(provider_result.results)

        execution_metadata = dict(provider_result.execution_metadata)
        execution_metadata.setdefault("provider", request.provider)
        execution_metadata.setdefault("backend_name", request.backend_name)
        execution_metadata.setdefault("qasm_version", request.qasm_version)
        execution_metadata.setdefault("shot_count", request.shots)
        execution_metadata.setdefault("hardware_execution", request.hardware_execution)
        execution_metadata.setdefault(
            "qubit_order_convention", request.qubit_order_convention
        )
        execution_metadata.setdefault(
            "basis_rotation_convention", request.basis_rotation_convention
        )
        _validate_result_semantics(request, provider_result.results, execution_metadata)

        normalized_result = {
            "status": provider_result.status,
            "job_id": provider_result.job_id,
            "results": provider_result.results,
            "execution_metadata": execution_metadata,
        }
        result_digest = sha256_text(canonical_json(normalized_result))
        receipt = ExecutionReceipt(
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
            execution_metadata=execution_metadata,
            created_at_utc=datetime.now(timezone.utc).isoformat(),
        )
        if self.audit_ledger is not None and self.audit_anchoring_enabled:
            receipt = self.anchor_receipt(receipt)
        return receipt

    def anchor_receipt(self, receipt: ExecutionReceipt) -> ExecutionReceipt:
        """Anchor only digests and execution metadata; keep the raw receipt independent."""

        if self.audit_ledger is None:
            raise QuantumProtocolError("audit ledger is not configured")
        if not self.audit_anchoring_enabled:
            return receipt
        if not self.verify_receipt(receipt):
            raise QuantumProtocolError("cannot anchor a receipt with an invalid result digest")

        for record in self.audit_ledger.records:
            payload = getattr(record, "payload", {})
            if (
                isinstance(payload, Mapping)
                and payload.get("event_type") == "qip_execution_anchor"
                and payload.get("request_digest") == receipt.request_digest
                and payload.get("result_digest") == receipt.result_digest
                and payload.get("job_id") == receipt.job_id
            ):
                raise QuantumProtocolError("replayed execution receipt anchor detected")

        payload = {
            "event_type": "qip_execution_anchor",
            "protocol_version": receipt.protocol_version,
            "session_id": receipt.session_id,
            "provider": receipt.provider,
            "backend_name": receipt.backend_name,
            "mode": receipt.mode,
            "status": receipt.status,
            "job_id": receipt.job_id,
            "shots": receipt.shots,
            "request_digest": receipt.request_digest,
            "result_digest": receipt.result_digest,
            "execution_metadata": dict(receipt.execution_metadata),
            "truth_boundary": (
                "Hash-chain consistency establishes traceability and mutation detection; "
                "it does not prove faithful provider or QPU execution."
            ),
        }
        record = self.audit_ledger.commit(payload)
        anchor = {
            "ledger_index": record.index,
            "ledger_hash": record.hash_value,
            "previous_hash": record.previous_hash,
            "event_type": "qip_execution_anchor",
        }
        return replace(receipt, audit_anchor=anchor)

    def verify_audit_anchor(self, receipt: ExecutionReceipt) -> bool:
        """Verify the optional ledger anchor without changing raw receipt validity."""

        if self.audit_ledger is None or receipt.audit_anchor is None:
            return False
        if not self.audit_ledger.verify():
            return False
        index = receipt.audit_anchor.get("ledger_index")
        if isinstance(index, bool) or not isinstance(index, int):
            return False
        if index < 0 or index >= len(self.audit_ledger.records):
            return False
        record = self.audit_ledger.records[index]
        payload = getattr(record, "payload", {})
        return bool(
            getattr(record, "hash_value", None) == receipt.audit_anchor.get("ledger_hash")
            and isinstance(payload, Mapping)
            and payload.get("event_type") == "qip_execution_anchor"
            and payload.get("request_digest") == receipt.request_digest
            and payload.get("result_digest") == receipt.result_digest
            and payload.get("job_id") == receipt.job_id
        )

    @staticmethod
    def verify_receipt(receipt: ExecutionReceipt) -> bool:
        normalized_result = {
            "status": receipt.status,
            "job_id": receipt.job_id,
            "results": receipt.results,
            "execution_metadata": receipt.execution_metadata,
        }
        try:
            expected = sha256_text(canonical_json(normalized_result))
        except (TypeError, ValueError):
            return False
        return expected == receipt.result_digest


def normalize_observables(
    observables: Sequence[ObservableTerm],
    qubit_count: int,
    *,
    duplicate_policy: DuplicateObservablePolicy = "aggregate",
) -> tuple[ObservableTerm, ...]:
    """Uppercase and deterministically aggregate duplicate Pauli terms."""

    if duplicate_policy not in {"aggregate", "reject"}:
        raise QuantumProtocolError("duplicate_policy must be aggregate or reject")
    grouped: dict[str, list[float]] = {}
    for observable in observables:
        observable.validate(qubit_count)
        label = observable.pauli.upper()
        if duplicate_policy == "reject" and label in grouped:
            raise QuantumProtocolError(f"Duplicate observable {label!r} is not allowed.")
        grouped.setdefault(label, []).append(float(observable.coefficient))

    normalized = [
        ObservableTerm(label, math.fsum(sorted(coefficients)))
        for label, coefficients in sorted(grouped.items())
    ]
    return tuple(normalized)


def pauli_words_commute(first: str, second: str) -> bool:
    """Return True when two equal-length Pauli words commute."""

    left = first.upper()
    right = second.upper()
    if len(left) != len(right):
        raise QuantumProtocolError("Pauli words must have equal length for commutation testing.")
    if any(symbol not in "IXYZ" for symbol in left + right):
        raise QuantumProtocolError("Pauli words may contain only I, X, Y, and Z.")
    anti_commuting_positions = sum(
        1
        for a, b in zip(left, right)
        if a != "I" and b != "I" and a != b
    )
    return anti_commuting_positions % 2 == 0


def group_commuting_observables(
    observables: Sequence[ObservableTerm],
    qubit_count: int,
) -> tuple[tuple[ObservableTerm, ...], ...]:
    """Create deterministic pairwise-commuting groups using greedy first fit."""

    normalized = normalize_observables(observables, qubit_count)
    groups: list[list[ObservableTerm]] = []
    for term in normalized:
        for group in groups:
            if all(pauli_words_commute(term.pauli, existing.pauli) for existing in group):
                group.append(term)
                break
        else:
            groups.append([term])
    return tuple(tuple(group) for group in groups)


def coefficient_weighted_hoeffding(
    observables: Sequence[ObservableTerm],
    shots_by_observable: Mapping[str, int],
    *,
    confidence_level: float = 0.95,
    empirical_variances: Mapping[str, float] | None = None,
) -> UncertaintyReport:
    """Bound a weighted Pauli sum while reporting empirical variance separately."""

    if not 0.0 < confidence_level < 1.0:
        raise QuantumProtocolError("confidence_level must lie strictly between 0 and 1")
    if not observables:
        raise QuantumProtocolError("at least one observable is required")
    qubit_count = len(observables[0].pauli)
    normalized = normalize_observables(observables, qubit_count)

    validated_shots: dict[str, int] = {}
    variance_proxy = 0.0
    empirical_estimator_variance = 0.0 if empirical_variances is not None else None
    for term in normalized:
        shots = shots_by_observable.get(term.pauli)
        if isinstance(shots, bool) or not isinstance(shots, int) or shots <= 0:
            raise QuantumProtocolError(
                f"shots_by_observable requires a positive integer for {term.pauli}."
            )
        validated_shots[term.pauli] = shots
        variance_proxy += (term.coefficient * term.coefficient) / shots
        if empirical_variances is not None:
            variance = empirical_variances.get(term.pauli)
            if variance is None or not math.isfinite(variance) or not 0.0 <= variance <= 1.0:
                raise QuantumProtocolError(
                    f"empirical variance for {term.pauli} must be finite and in [0, 1]."
                )
            empirical_estimator_variance += (
                term.coefficient * term.coefficient * variance / shots
            )

    alpha = 1.0 - confidence_level
    half_width = math.sqrt(2.0 * variance_proxy * math.log(2.0 / alpha))
    return UncertaintyReport(
        method="coefficient_weighted_hoeffding",
        confidence_level=confidence_level,
        half_width=half_width,
        theoretical_variance_proxy=variance_proxy,
        empirical_variance_of_estimator=empirical_estimator_variance,
        shots_by_observable=validated_shots,
        assumptions=_HOEFFDING_ASSUMPTIONS,
        interpretation=(
            "This is a concentration bound for finite-shot sampling under the declared "
            "assumptions. It is not a hardware-accuracy, calibration, or mitigation guarantee."
        ),
    )


def wilson_interval(
    successes: int,
    trials: int,
    *,
    confidence_level: float = 0.95,
) -> tuple[float, float]:
    """Wilson score interval for a binomial probability."""

    if isinstance(successes, bool) or isinstance(trials, bool):
        raise QuantumProtocolError("successes and trials must be integers")
    if not isinstance(successes, int) or not isinstance(trials, int):
        raise QuantumProtocolError("successes and trials must be integers")
    if trials <= 0 or successes < 0 or successes > trials:
        raise QuantumProtocolError("require 0 <= successes <= trials and trials > 0")
    if not 0.0 < confidence_level < 1.0:
        raise QuantumProtocolError("confidence_level must lie strictly between 0 and 1")

    z = NormalDist().inv_cdf(0.5 + confidence_level / 2.0)
    proportion = successes / trials
    denominator = 1.0 + (z * z) / trials
    center = (proportion + (z * z) / (2.0 * trials)) / denominator
    radius = (
        z
        * math.sqrt(
            proportion * (1.0 - proportion) / trials
            + (z * z) / (4.0 * trials * trials)
        )
        / denominator
    )
    return max(0.0, center - radius), min(1.0, center + radius)


def bootstrap_mean_interval(
    samples: Sequence[float],
    *,
    confidence_level: float = 0.95,
    resamples: int = 2000,
    seed: int = 0,
) -> tuple[float, float]:
    """Deterministic percentile bootstrap interval for a scalar sample mean."""

    values = tuple(float(value) for value in samples)
    if not values or any(not math.isfinite(value) for value in values):
        raise QuantumProtocolError("bootstrap samples must be non-empty and finite")
    if not 0.0 < confidence_level < 1.0:
        raise QuantumProtocolError("confidence_level must lie strictly between 0 and 1")
    if isinstance(resamples, bool) or not isinstance(resamples, int) or resamples < 100:
        raise QuantumProtocolError("resamples must be an integer of at least 100")

    rng = random.Random(seed)
    n = len(values)
    means = sorted(
        math.fsum(values[rng.randrange(n)] for _ in range(n)) / n
        for _ in range(resamples)
    )
    alpha = 1.0 - confidence_level
    lower_index = max(0, min(resamples - 1, int(math.floor((alpha / 2.0) * resamples))))
    upper_index = max(
        0,
        min(resamples - 1, int(math.ceil((1.0 - alpha / 2.0) * resamples)) - 1),
    )
    return means[lower_index], means[upper_index]


def expectation_from_probabilities(
    probabilities: Mapping[str, float],
    observables: Sequence[ObservableTerm],
) -> float:
    """Evaluate commuting Pauli-Z-basis terms from bitstring probabilities.

    The circuit must already contain the basis rotations needed to map every requested
    Pauli term to computational-basis measurements. Bitstrings and Pauli labels use the
    same left-to-right order, matching the declared QIP convention.
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

    normalized = normalize_observables(observables, qubit_count)
    for observable in normalized:
        if any(symbol not in "IZ" for symbol in observable.pauli):
            raise QuantumProtocolError(
                "expectation_from_probabilities requires basis-rotated I/Z observables."
            )

    expectation = 0.0
    for observable in normalized:
        term_expectation = 0.0
        for bitstring, probability in probabilities.items():
            eigenvalue = 1
            for symbol, bit in zip(observable.pauli, bitstring):
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


def _validate_result_semantics(
    request: QuantumRunRequest,
    results: Mapping[str, Any],
    execution_metadata: Mapping[str, Any],
) -> None:
    reported_hardware = execution_metadata.get("hardware_execution")
    if reported_hardware is True and not request.hardware_execution:
        raise QuantumProtocolError(
            "Provider metadata labels a non-hardware request as hardware execution."
        )
    if request.provider == "local" and reported_hardware is True:
        raise QuantumProtocolError("Local provider output cannot be labelled as hardware telemetry.")

    result_keys = {str(key).lower() for key in results}
    mitigated_keys = {key for key in result_keys if "mitigated" in key}
    if mitigated_keys:
        raw_present = any(key.startswith("raw") or "raw_" in key for key in result_keys)
        if not raw_present:
            raise QuantumProtocolError(
                "Mitigated result values require corresponding raw values in the receipt."
            )


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
