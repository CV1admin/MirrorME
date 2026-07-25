from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Mapping

from .protocol import (
    PreparedQuantumRun,
    ProviderResult,
    QuantumProtocolError,
)


@dataclass
class LocalDeterministicProvider:
    """Small test/provider boundary that never claims to simulate a QPU."""

    results: Mapping[str, Any]
    name: str = "local"

    def execute(self, prepared: PreparedQuantumRun) -> ProviderResult:
        return ProviderResult(
            status="completed",
            job_id=f"local:{prepared.request_digest[-16:]}",
            results=dict(self.results),
            execution_metadata={
                "execution_class": "deterministic_fixture",
                "simulated_hardware": False,
                "request_digest": prepared.request_digest,
            },
        )


@dataclass
class FireOpalIBMProvider:
    """Optional Fire Opal adapter using credentials only from the local environment."""

    name: str = "fire_opal_ibm"
    token_env: str = "IBM_QUANTUM_TOKEN"
    instance_env: str = "IBM_QUANTUM_INSTANCE"

    def execute(self, prepared: PreparedQuantumRun) -> ProviderResult:
        request = prepared.request
        if request.provider != self.name:
            raise QuantumProtocolError("Fire Opal adapter received a non-Fire-Opal request.")

        token = os.environ.get(self.token_env)
        instance = os.environ.get(self.instance_env)
        if not token or not instance:
            raise QuantumProtocolError(
                f"Set {self.token_env} and {self.instance_env} in the local environment."
            )

        try:
            import fireopal as fo
            from fireopal.types import PauliOperator
        except ImportError as exc:
            raise QuantumProtocolError(
                "Fire Opal support requires the optional 'fire-opal' package."
            ) from exc

        credentials = fo.credentials.make_credentials_for_ibm_cloud(
            token=token,
            instance=instance,
        )

        if request.mode == "sample":
            job = fo.execute(
                circuits=[request.circuit_qasm],
                shot_count=request.shots,
                credentials=credentials,
                backend_name=request.backend_name,
            )
            raw = job.result()
        else:
            observables = PauliOperator.from_list(
                [(term.pauli, term.coefficient) for term in request.observables]
            )
            if request.mode == "expectation":
                job = fo.iterate_expectation(
                    circuits=[request.circuit_qasm],
                    shot_count=request.shots,
                    credentials=credentials,
                    backend_name=request.backend_name,
                    parameters=[dict(request.parameters)],
                    observables=observables,
                )
                raw = job.result()
            else:
                job, raw = self._run_variational_loop(
                    prepared=prepared,
                    credentials=credentials,
                    observables=observables,
                    fireopal=fo,
                )

        job_id = _read_job_id(job, raw)
        return ProviderResult(
            status="completed",
            job_id=job_id,
            results=_normalize_mapping(raw),
            execution_metadata={
                "provider": "Q-CTRL Fire Opal",
                "backend_name": request.backend_name,
                "shot_count": request.shots,
                "qasm_version": request.qasm_version,
                "hardware_execution": True,
            },
        )

    def _run_variational_loop(
        self,
        *,
        prepared: PreparedQuantumRun,
        credentials: Any,
        observables: Any,
        fireopal: Any,
    ) -> tuple[Any, Mapping[str, Any]]:
        request = prepared.request
        optimizer = request.optimizer
        if optimizer is None:
            raise QuantumProtocolError("Missing optimizer after request validation.")

        try:
            from scipy.optimize import minimize
        except ImportError as exc:
            raise QuantumProtocolError(
                "Variational Fire Opal runs require the optional 'scipy' package."
            ) from exc

        parameter_names = tuple(request.parameters)
        initial_values = (
            optimizer.initial_parameters
            if optimizer.initial_parameters
            else tuple(float(request.parameters[name]) for name in parameter_names)
        )
        history: list[float] = []
        last_job: Any = None

        def objective(values: Any) -> float:
            nonlocal last_job
            parameter_values = {
                name: float(value) for name, value in zip(parameter_names, values)
            }
            last_job = fireopal.iterate_expectation(
                circuits=[request.circuit_qasm],
                shot_count=request.shots,
                credentials=credentials,
                backend_name=request.backend_name,
                parameters=[parameter_values],
                observables=observables,
            )
            result = last_job.result()
            expectation = float(result["expectation_values"][0])
            history.append(expectation)
            return expectation

        try:
            optimization = minimize(
                objective,
                initial_values,
                method=optimizer.name,
                tol=optimizer.tolerance,
                options={"maxiter": optimizer.max_iterations},
            )
        finally:
            fireopal.stop_iterate(credentials, request.backend_name)

        if last_job is None:
            raise QuantumProtocolError("Variational optimizer completed without a provider job.")

        raw = {
            "expectation_values": history,
            "final_expectation_value": float(optimization.fun),
            "optimized_parameters": {
                name: float(value)
                for name, value in zip(parameter_names, optimization.x)
            },
            "optimizer": {
                "name": optimizer.name,
                "success": bool(optimization.success),
                "status": int(optimization.status),
                "message": str(optimization.message),
                "iterations": int(getattr(optimization, "nit", len(history))),
                "function_evaluations": int(getattr(optimization, "nfev", len(history))),
            },
        }
        return last_job, raw


def _read_job_id(job: Any, result: Any) -> str:
    for source in (job, result):
        if isinstance(source, Mapping):
            for key in ("job_id", "id", "jobId"):
                value = source.get(key)
                if value:
                    return str(value)
        for attribute in ("job_id", "id"):
            value = getattr(source, attribute, None)
            if callable(value):
                value = value()
            if value:
                return str(value)
    return "provider-job-id-unavailable"


def _normalize_mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    return {"value": value}
