# MirrorME Quantum Integration Protocol — QIP-0.1

## Status

`QIP-0.1` is an integration-development protocol. It is not evidence of quantum advantage, consciousness, nonlocal agency, or autonomous scientific discovery.

The protocol converts an approved MirrorME task into a credential-free quantum execution request, dispatches it through a provider adapter, and returns a hash-bound execution receipt.

## Architectural boundary

```text
MirrorME / VIREAX task
  -> existing policy and Lightful gates
  -> QIP request validation
  -> canonical request digest
  -> local simulator OR explicitly approved hardware adapter
  -> normalized provider result
  -> result digest and execution receipt
  -> audit ledger / human scientific review
```

Quantum hardware is an external action. Selecting `ibm_quantum` or `fire_opal_ibm` is rejected unless both `hardware_execution=True` and `human_approved=True` are present. Credentials never cross the QIP payload boundary; adapters read them only from the local environment.

## Protocol objects

### `QuantumRunRequest`

Required fields include:

- session and operator identity;
- complete OpenQASM 2.0 or 3.0 program;
- declared qubit count, mode, provider, backend, shots, and seed;
- Pauli observables for expectation or variational modes;
- optimizer declaration and ordered parameter mapping for variational mode;
- explicit hardware and human-approval flags;
- provenance metadata without secrets.

### `PreparedQuantumRun`

The validated request is serialized as sorted canonical JSON and bound to

\[
d_R = \operatorname{SHA256}(\operatorname{CanonicalJSON}(R)).
\]

The digest detects mutation of the declared workload. It does not prove that a remote provider executed the circuit faithfully; provider attestation and independent replication remain separate requirements.

### `ExecutionReceipt`

The normalized result is separately bound to

\[
d_Y = \operatorname{SHA256}(\operatorname{CanonicalJSON}(Y)).
\]

The receipt records provider, backend, mode, shot count, job identifier, request digest, result digest, provider metadata, and UTC creation time.

## Variational execution model

For ansatz state

\[
|\psi(\theta)\rangle = U(\theta)|0\rangle,
\]

and Hamiltonian

\[
H=\sum_j c_j P_j,
\]

the cost function is

\[
E(\theta)=\langle\psi(\theta)|H|\psi(\theta)\rangle
          =\sum_j c_j\langle P_j\rangle_\theta.
\]

The uploaded VQE notebook uses

\[
H=ZIX-\frac12 ZXI+\frac12 IXX.
\]

An exact symbolic calculation gives

\[
\operatorname{spec}(H)=\{-2,-2,0,0,1,1,1,1\},
\qquad E_0=-2.
\]

This value is the mathematical reference target for the notebook, not a claim about hardware performance.

## Provider adapters

### Local deterministic adapter

`LocalDeterministicProvider` exists for protocol, audit, and test verification. It explicitly marks its output as a deterministic fixture and never represents itself as QPU telemetry.

### Fire Opal on IBM Quantum

`FireOpalIBMProvider` implements the uploaded notebook flow:

- `fo.execute` for sampled circuits;
- `fo.iterate_expectation` for expectation calls and each VQA objective evaluation;
- SciPy `minimize` for the declared classical optimization loop, followed by `fo.stop_iterate`;
- IBM credentials read from `IBM_QUANTUM_TOKEN` and `IBM_QUANTUM_INSTANCE`;
- no API keys or tokens in requests, receipts, logs, or Git history.

Optional installation:

```powershell
python -m pip install fire-opal qiskit qiskit-ibm-runtime scipy
$env:IBM_QUANTUM_TOKEN = "..."
$env:IBM_QUANTUM_INSTANCE = "..."
python examples/quantum_vqe_protocol.py
```

Do not commit the environment variables.

## Validation invariants

A run is rejected when any of the following is true:

1. malformed or mismatched OpenQASM version;
2. invalid qubit count or shot count;
3. non-finite parameters or coefficients;
4. malformed Pauli strings;
5. missing observables for expectation/VQA mode;
6. missing optimizer or ordered parameter mapping for variational mode;
7. hardware selection without explicit approval;
8. credential-like keys in request or result payloads;
9. provider adapter and declared provider mismatch;
10. receipt digest mismatch after result mutation.

## Test command

```powershell
python -m unittest tests.test_quantum_protocol -v
```

## Scientific limits

- Shot noise, calibration drift, compilation changes, queue effects, and mitigation bias must be reported, not hidden.
- A simulator result is not hardware telemetry.
- Error suppression is not error correction.
- A lower noisy estimate is not automatically a better ground-state estimate; confidence intervals and exact bounds matter.
- QIP governs execution and provenance. It does not establish physical truth by itself.
