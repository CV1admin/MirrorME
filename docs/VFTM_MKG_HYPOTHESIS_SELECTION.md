# VFTM–MKG Hypothesis-Selection Operator

**Status:** Research specification  
**Scope:** Vortex Field Tensor Memory (VFTM), MirrorME reasoning, uncertainty-aware action selection  
**Author:** Marek Kowalski

## 1. Purpose

This specification defines a sequential hypothesis-selection operator that explicitly permits abstention. It separates predicted observations from external observations, maintains provenance-aware compressed memory, and exposes uncertainty as a first-class output.

The operator is intended as a computational reasoning component for VFTM and MirrorME. It is not a claim that physical vortices themselves perform symbolic inference. VFTM supplies a structured memory representation; the MKG operator supplies the decision rule over candidate hypotheses.

## 2. State and hypothesis space

At discrete time \(t\), define:

- \(s_t\): current system state;
- \(e_t\): currently available evidence;
- \(M_t\): compressed memory state;
- \(\mathcal{H}_t\): admissible candidate hypotheses;
- \(u_t\): residual uncertainty;
- \(\pi_t\): provenance record.

Each hypothesis \(h\in\mathcal{H}_t\) may contain:

- a predictive model;
- a state-transition operator \(T_h\);
- expected observation \(o_h\);
- declared assumptions and constraints;
- computational cost and risk metadata.

## 3. Multi-criteria score

Each candidate hypothesis is scored by

\[
Q_t(h)=w_eE_t(h)+w_cC_t(h)+w_nN_t(h)+w_iI_t(h)+w_pP_t(h)-w_kK_t(h)-w_rR_t(h).
\]

Positive terms:

- \(E_t(h)\): agreement with available evidence;
- \(C_t(h)\): satisfaction of hard constraints;
- \(N_t(h)\): novelty relative to existing memory;
- \(I_t(h)\): expected information gain;
- \(P_t(h)\): prior plausibility.

Penalty terms:

- \(K_t(h)\): description length or computational complexity;
- \(R_t(h)\): estimated operational, scientific, or safety risk.

The weights \(w_\bullet\ge 0\) are explicit configuration parameters. All component scores should be normalized to a declared range before combination.

### Hard-constraint rule

A hard constraint should not be treated only as a soft reward. Define

\[
C_t(h)\in\{0,1\}
\]

and reject any hypothesis with \(C_t(h)=0\), or equivalently assign

\[
Q_t(h)=-\infty.
\]

This prevents a sufficiently high novelty or information-gain term from compensating for a violated safety or physical constraint.

## 4. Selection with abstention

The selected action is

\[
h_t^*=\begin{cases}
\arg\max_{h\in\mathcal{H}_t}Q_t(h), & \max_hQ_t(h)\ge \tau_t,\\
\emptyset, & \text{otherwise}.
\end{cases}
\]

The null action \(\emptyset\) is mandatory. It represents insufficient justification to select any available hypothesis.

Abstention must also occur when:

- \(\mathcal{H}_t=\varnothing\);
- hard constraints eliminate every hypothesis;
- the highest-scoring candidates are insufficiently distinguishable;
- estimated uncertainty exceeds an independent bound;
- required provenance is missing or unreliable.

A margin condition is recommended:

\[
Q_t(h_{(1)})-Q_t(h_{(2)})\ge \delta_t,
\]

where \(h_{(1)}\) and \(h_{(2)}\) are the first- and second-ranked candidates. This avoids arbitrary selection under near-ties.

## 5. State transition

The state transition is

\[
s_{t+1}=\begin{cases}
T_{h_t^*}(s_t), & h_t^*\neq\emptyset,\\
s_t, & h_t^*=\emptyset.
\end{cases}
\]

For consequential actions, \(T_h\) should first be evaluated in a simulation or proposal state. External effects require a separate authorization gate.

## 6. Prediction and observation separation

The selected hypothesis produces a predicted observation

\[
\widehat{o}_{t+1}=o_{h_t^*}.
\]

The external or instrument-derived observation is obtained independently:

\[
o_{t+1}=\operatorname{Observe}(s_{t+1}).
\]

These values must remain distinct until verification:

\[
\varepsilon_{t+1}=d\!\left(\widehat{o}_{t+1},o_{t+1}\right),
\]

where \(d\) is an explicitly chosen discrepancy measure.

The operator must never insert \(\widehat{o}_{t+1}\) into memory as if it were an external observation.

## 7. Uncertainty update

Residual uncertainty should be derived from multiple sources rather than stored as an undefined scalar. One admissible decomposition is

\[
u_{t+1}=g\!\left(
U_{\mathrm{model}},
U_{\mathrm{data}},
U_{\mathrm{measurement}},
U_{\mathrm{selection}},
\varepsilon_{t+1}
\right).
\]

Possible components include:

- posterior entropy over hypotheses;
- confidence interval width;
- ensemble disagreement;
- observation noise;
- calibration error;
- selection margin;
- prediction error.

## 8. Provenance-aware memory update

The memory update is

\[
M_{t+1}=\operatorname{Compress}\!\left[
M_t\cup
\left\{
 s_t,
 e_t,
 h_t^*,
 Q_t(h_t^*),
 \widehat{o}_{t+1},
 o_{t+1},
 \varepsilon_{t+1},
 s_{t+1},
 u_{t+1},
 \pi_t
\right\}
\right].
\]

The notation \(Q_t(h_t^*)\) is defined as `null` when \(h_t^*=\emptyset\).

Compression must preserve at least:

- source identifiers;
- timestamps;
- content hashes;
- reliability estimates;
- selected and rejected hypotheses;
- score components and weight version;
- prediction-versus-observation discrepancy;
- uncertainty summary;
- authorization outcome.

Compression should be deterministic for audit reproducibility, or record the compressor version and random seed.

## 9. Overall operator

The complete operator is

\[
I_{\mathrm{MKG}}:(s_t,e_t,M_t)\mapsto
(s_{t+1},u_{t+1},M_{t+1}).
\]

A more explicit implementation also returns the decision record:

\[
I_{\mathrm{MKG}}^{+}:(s_t,e_t,M_t)\mapsto
(s_{t+1},h_t^*,\widehat{o}_{t+1},o_{t+1},u_{t+1},M_{t+1},a_t),
\]

where \(a_t\) is an immutable audit record.

## 10. VFTM integration

VFTM can provide structured state and memory features to the hypothesis operator. Let

\[
\mathcal{V}_t=\left(
\mathcal{M}_{ij}(t),
\omega_t,
H_t,
\tau_t,
\Lambda_t
\right),
\]

where:

- \(\mathcal{M}_{ij}\): global tensor-memory state;
- \(\omega_t\): generalized vorticity or circulation feature;
- \(H_t\): helicity or topological-persistence feature;
- \(\tau_t\): estimated memory lifetime;
- \(\Lambda_t\): spectrum or principal modes of the tensor state.

These values may enter \(s_t\), \(e_t\), or hypothesis-specific feature functions. The mapping must be declared as computational. Quantum entanglement is not assumed to possess literal fluid vorticity.

## 11. Reference pseudocode

```python
from dataclasses import dataclass
from typing import Callable, Iterable, Optional


@dataclass(frozen=True)
class ScoreComponents:
    evidence: float
    constraints: bool
    novelty: float
    information_gain: float
    prior: float
    complexity: float
    risk: float


@dataclass(frozen=True)
class Hypothesis:
    name: str
    transition: Callable[[object], object]
    predict: Callable[[object], object]
    score: ScoreComponents


@dataclass(frozen=True)
class Decision:
    selected: Optional[Hypothesis]
    score: Optional[float]
    abstained: bool
    reason: str


def weighted_score(h: Hypothesis, w: dict[str, float]) -> float:
    c = h.score
    if not c.constraints:
        return float("-inf")
    return (
        w["e"] * c.evidence
        + w["n"] * c.novelty
        + w["i"] * c.information_gain
        + w["p"] * c.prior
        - w["k"] * c.complexity
        - w["r"] * c.risk
    )


def select_hypothesis(
    hypotheses: Iterable[Hypothesis],
    weights: dict[str, float],
    threshold: float,
    margin: float,
) -> Decision:
    ranked = sorted(
        ((weighted_score(h, weights), h) for h in hypotheses),
        key=lambda item: item[0],
        reverse=True,
    )
    ranked = [item for item in ranked if item[0] != float("-inf")]
    if not ranked:
        return Decision(None, None, True, "no admissible hypothesis")

    best_score, best = ranked[0]
    if best_score < threshold:
        return Decision(None, best_score, True, "score below threshold")

    if len(ranked) > 1 and best_score - ranked[1][0] < margin:
        return Decision(None, best_score, True, "insufficient selection margin")

    return Decision(best, best_score, False, "selected")
```

## 12. Validation requirements

The operator should be tested for:

1. abstention below threshold;
2. rejection of hard-constraint violations;
3. abstention under near-ties;
4. no state transition on abstention;
5. strict distinction between prediction and observation;
6. deterministic scoring under fixed configuration;
7. provenance retention after compression;
8. calibrated uncertainty on held-out cases;
9. resistance to novelty or prior terms overwhelming evidence;
10. safe failure when score values are missing, non-finite, or out of range.

## 13. Scientific status

This document defines a rational engineering operator. The abstention mechanism, decision-theoretic scoring, prediction/observation separation, and provenance-aware memory are defensible system-design principles.

The specific seven-term linear score is a configurable hypothesis, not a uniquely derived optimal rule. Its usefulness must be established through calibration, ablation studies, baseline comparison, and empirical evaluation.
