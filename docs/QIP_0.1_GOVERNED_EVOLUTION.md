# QIP-0.1 Governed Evolution

**Issue:** #38  
**Status:** implementation candidate; simulator-tested only  
**Scientific boundary:** traceability and statistical bounds do not establish physical truth or faithful QPU execution.

## 1. Observable normalization

Each Pauli term is validated against the declared qubit count and the alphabet `I`, `X`, `Y`, `Z`.

The request declares one duplicate policy:

- `aggregate` — uppercase identical Pauli words, sort them lexicographically, and combine coefficients using deterministic `math.fsum` aggregation;
- `reject` — reject the request when the same normalized Pauli word appears more than once.

The canonical request digest is computed after normalization. Equivalent Hamiltonians with reordered duplicate terms therefore produce the same normalized observable list.

## 2. Measurement conventions

QIP records these conventions explicitly:

```text
qubit_order_convention:
  pauli_label_left_to_right_matches_result_bitstrings

basis_rotation_convention:
  caller_pre_rotates_each_measurement_group_to_z_basis
```

The protocol does not silently infer provider-specific endianness or basis rotation.

## 3. Commutation grouping

`group_commuting_observables` performs deterministic greedy first-fit grouping. A pair of Pauli words commutes when the number of positions containing distinct non-identity Pauli symbols is even.

The grouping is valid and deterministic, but it is not claimed to minimize the number of measurement groups.

## 4. Uncertainty methods

For

\[
H=\sum_j c_jP_j
\]

with independently sampled Pauli estimators using `n_j` shots, the coefficient-weighted Hoeffding half-width is

\[
\epsilon=
\sqrt{
2\ln\!\left(\frac{2}{\alpha}\right)
\sum_j\frac{c_j^2}{n_j}
},
\qquad \alpha=1-\text{confidence level}.
\]

The report records:

- method;
- confidence level;
- half-width;
- theoretical variance proxy;
- optional empirical estimator variance as a separate field;
- shot allocation per normalized observable;
- assumptions and interpretation boundary.

Assumptions:

1. independent shots;
2. bounded Pauli outcomes in `[-1, 1]`;
3. fixed circuit and observable definition;
4. fixed calibration interval for hardware data;
5. no unmodelled mitigation bias.

The bound is not a hardware-accuracy, calibration, compilation, or mitigation guarantee.

Additional utilities provide:

- Wilson score intervals for binomial probabilities;
- deterministic percentile-bootstrap intervals for scalar sample means.

## 5. Raw and mitigated values

A result containing a key identified as mitigated must also contain a corresponding raw result field. The protocol rejects mitigated-only receipts.

Simulator or deterministic-fixture output cannot be labelled as hardware execution.

## 6. Audit anchoring

When an `AuditLedger` is supplied, QIP anchors:

- request digest;
- normalized result digest;
- provider and backend;
- mode, status, job ID, and shot count;
- available execution metadata;
- a truth-boundary statement.

Raw results remain in the independent execution receipt. Ledger failure does not alter the validity of the raw receipt digest.

The ledger now verifies:

- record index continuity;
- previous-hash continuity;
- canonical payload hash;
- current record hash.

It deep-copies committed payloads and supports tail-only rollback with an explicitly acknowledged expected hash.

Duplicate anchoring of the same request digest, result digest, and job ID is rejected as a replay.

Ledger anchoring can be disabled with:

```python
QuantumIntegrationProtocol(
    audit_ledger=ledger,
    audit_anchoring_enabled=False,
)
```

Canonical request/result digests and standalone receipts continue to work while anchoring is disabled.

## 7. Test coverage

```powershell
python -m unittest tests.test_quantum_protocol -v
python -m unittest tests.test_quantum_protocol_evolution -v
```

The evolution tests cover:

- deterministic duplicate aggregation;
- duplicate rejection;
- pairwise commutation and grouping;
- coefficient-weighted Hoeffding calculations;
- separate empirical variance reporting;
- Wilson and bootstrap intervals;
- audit corruption and missing-record handling;
- replay rejection;
- ledger-disable rollback path;
- mitigated-only result rejection.

## 8. Unresolved empirical work

This change does not claim completion of the cross-provider validation programme. Still required:

- repeated simulator runs under documented noise models;
- approved hardware runs across separate calibration windows;
- provider metadata completeness measurements;
- raw-versus-mitigated comparisons;
- independent receipt and digest verification;
- cross-provider scientific comparison.

API compatibility must not be reported as scientific agreement.
