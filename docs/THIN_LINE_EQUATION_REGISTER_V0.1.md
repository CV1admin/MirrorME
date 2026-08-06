# The Thin Line — Canonical Equation Register v0.1

**Project:** Civilisation.One / MirrorME / Thin Line Engine  
**Status:** research specification; not an experimentally established Theory of Everything  
**Owner:** Marek Kowalski  
**Protocol status classes:** `[E]` established formalism, `[P]` phenomenological model, `[H]` hypothesis, `[D]` definition, `[X]` deprecated.

---

## 0. Scope and scientific boundary

This register consolidates the current Thin Line equations into one versioned document. It separates standard physics from proposed Thin Line structures.

The framework presently consists of:

1. a scalar–tensor effective field theory connecting quantum matter and classical geometry;
2. a canonical quantum-spacetime extension using ADM and Wheeler–DeWitt quantisation;
3. a semiclassical limit recovering general relativity and ordinary quantum-field evolution;
4. low-energy stability conditions;
5. falsifiable Yukawa and gravity-mediated entanglement observables;
6. separate phenomenological Thin Line functionals not yet derived from the action.

The framework does **not** yet provide a regulated ultraviolet completion, a unique Standard Model embedding, or an experimentally validated unification.

---

# A. Geometric compatibility layer

## TL-001 — Quantum and relativistic sectors `[D]`

\[
\Phi_Q:\mathcal M\rightarrow\mathbb R,
\qquad
\Phi_R:\mathcal M\rightarrow\mathbb R.
\]

Here \(\mathcal M\) is a shared configuration or state space.

## TL-002 — General Thin Line compatibility locus `[D]`

\[
\boxed{
\mathcal T
=
\left\{
x\in\mathcal M
\;\middle|\;
F\!\left(
\Phi_Q,
\Phi_R,
\nabla\Phi_Q,
\nabla\Phi_R
\right)=0
\right\}
}
\]

## TL-003 — Simple intersection form `[D]`

\[
\boxed{
\mathcal T
=
\left\{
x\in\mathcal M
\mid
\Phi_Q(x)=0,
\;\Phi_R(x)=0
\right\}
}
\]

This is a geometric definition only; it does not establish physical unification.

---

# B. Thin Line scalar–tensor effective theory

## TL-010 — Fundamental low-energy action `[H]`

\[
\boxed{
S=
\int d^4x\sqrt{-g}
\left[
\frac{M_{\rm Pl}^{2}}{2}(R-2\Lambda)
-\frac12\nabla_\mu\phi\nabla^\mu\phi
-V(\phi)
\right]
+S_Q[A^2(\phi)g_{\mu\nu},\Psi]
+S_{\rm EFT}
}
\]

Interpretation:

\[
\Phi_Q\equiv\Psi,
\qquad
\Phi_R\equiv g_{\mu\nu},
\qquad
\Phi_{\rm TL}\equiv\phi.
\]

## TL-011 — Physical matter metric `[H]`

\[
\boxed{
\widetilde g_{\mu\nu}=A^2(\phi)g_{\mu\nu}
}
\]

## TL-012 — Universal conformal coupling `[H]`

\[
\boxed{
A(\phi)=
\exp\!\left[
\frac{\beta(\phi-\phi_0)}{M_{\rm Pl}}
\right]
}
\]

## TL-013 — Thin Line potential `[H]`

\[
\boxed{
V(\phi)=
\Lambda
+\frac12m_\phi^2(\phi-\phi_0)^2
+\frac{\lambda_\phi}{4}(\phi-\phi_0)^4
}
\]

## TL-014 — Representative complex-scalar matter action `[H]`

\[
S_Q=
-\int d^4x\sqrt{-\widetilde g}
\left[
\widetilde g^{\mu\nu}
\partial_\mu\Psi^*\partial_\nu\Psi
+m_\Psi^2|\Psi|^2
+\frac{\lambda_\Psi}{2}|\Psi|^4
\right].
\]

## TL-015 — Gravitational EFT corrections `[E/H]`

\[
S_{\rm EFT}=
\int d^4x\sqrt{-g}
\left[
c_1R^2
+c_2R_{\mu\nu}R^{\mu\nu}
+c_3R_{\mu\nu\rho\sigma}R^{\mu\nu\rho\sigma}
+\cdots
\right].
\]

The use of curvature corrections as a low-energy expansion is established; the coefficients and Thin Line ultraviolet completion are unspecified.

---

# C. Classical field equations

## TL-020 — Einstein equation `[H]`

\[
\boxed{
M_{\rm Pl}^{2}
\left(G_{\mu\nu}+\Lambda g_{\mu\nu}\right)
=
T_{\mu\nu}^{(\phi)}
+T_{\mu\nu}^{(Q)}
}
\]

## TL-021 — Thin Line stress-energy tensor `[E/H]`

\[
T_{\mu\nu}^{(\phi)}
=
\nabla_\mu\phi\nabla_\nu\phi
-\frac12g_{\mu\nu}(\nabla\phi)^2
-g_{\mu\nu}V(\phi).
\]

## TL-022 — Thin Line scalar equation `[H]`

\[
\boxed{
\Box\phi
=
V_{,\phi}
-\alpha(\phi)T_Q
}
\]

with

\[
\boxed{
\alpha(\phi)
=
\frac{d\ln A}{d\phi}
=
\frac{\beta}{M_{\rm Pl}}
}
\]

and

\[
T_Q=g^{\mu\nu}T_{\mu\nu}^{(Q)}.
\]

## TL-023 — Matter-field equation `[H]`

\[
\boxed{
\widetilde\Box\Psi
-m_\Psi^2\Psi
-\lambda_\Psi|\Psi|^2\Psi
=0
}
\]

## TL-024 — Einstein-frame matter exchange `[H]`

\[
\boxed{
\nabla_\mu T_Q^{\mu\nu}
=
\alpha(\phi)T_Q\nabla^\nu\phi
}
\]

The combined matter-plus-\(\phi\) energy-momentum tensor remains covariantly conserved.

---

# D. Quantum and nonrelativistic limits

## TL-030 — Gravity-decoupling limit `[E/H]`

\[
\boxed{
M_{\rm Pl}\rightarrow\infty,
\qquad
\frac{\beta}{M_{\rm Pl}}\rightarrow0,
\qquad
\phi\rightarrow\phi_0,
\qquad
g_{\mu\nu}\rightarrow\eta_{\mu\nu}
}
\]

## TL-031 — Klein–Gordon limit `[E]`

\[
\boxed{
(\Box-m_\Psi^2)\Psi=0
}
\]

## TL-032 — Nonrelativistic field decomposition `[E]`

\[
\boxed{
\Psi(t,\mathbf x)
=
\frac{e^{-im_\Psi t/\hbar}}{\sqrt{2m_\Psi}}
\psi(t,\mathbf x)
}
\]

with

\[
|\partial_t\psi|\ll m_\Psi|\psi|.
\]

## TL-033 — Schrödinger limit `[E]`

\[
\boxed{
i\hbar\partial_t\psi
=
-\frac{\hbar^2}{2m_\Psi}\nabla^2\psi
}
\]

---

# E. General-relativity limit

## TL-040 — Vacuum perturbation `[D]`

\[
\boxed{
\phi=\phi_0+\varphi
}
\]

## TL-041 — Linearised scalar equation `[H]`

\[
\boxed{
(\Box-m_\phi^2)\varphi
=
-\frac{\beta}{M_{\rm Pl}}T_Q
}
\]

## TL-042 — Exact GR decoupling limit `[E/H]`

\[
\boxed{
\beta\rightarrow0,
\qquad
\varphi\rightarrow0
}
\]

which yields

\[
\boxed{
M_{\rm Pl}^{2}
(G_{\mu\nu}+\Lambda g_{\mu\nu})
=T_{\mu\nu}^{(Q)}
}
\]

## TL-043 — Heavy-field solution `[H]`

For \(E\ll m_\phi\),

\[
\boxed{
\varphi
\simeq
\frac{\beta}{M_{\rm Pl}m_\phi^2}T_Q
+O\!\left(\frac{\Box}{m_\phi^4}\right)
}
\]

## TL-044 — Induced low-energy operator `[H]`

\[
\boxed{
\Delta\mathcal L_{\rm eff}
\sim
\frac{\beta^2}{2M_{\rm Pl}^2m_\phi^2}T_Q^2
}
\]

## TL-045 — Decoupling parameters `[D]`

\[
\boxed{
\epsilon_E=\frac{E^2}{m_\phi^2},
\qquad
\epsilon_G=\frac{E^2}{M_{\rm Pl}^2},
\qquad
\epsilon_\beta=\frac{|\beta|E}{M_{\rm Pl}}
}
\]

The GR regime requires

\[
\epsilon_E,\epsilon_G,\epsilon_\beta\ll1.
\]

---

# F. Stable coupling and environmental equilibrium

## TL-050 — Effective potential `[H]`

For nonrelativistic density \(\rho\),

\[
\boxed{
V_{\rm eff}(\phi;\rho)
=
V(\phi)+\rho A(\phi)
}
\]

## TL-051 — Thin Line equilibrium manifold `[D/H]`

\[
\boxed{
\mathcal T_{\rm eff}
=
\left\{
(\rho,\phi_*)
\;\middle|\;
V_{,\phi}(\phi_*)
+\rho A_{,\phi}(\phi_*)=0
\right\}
}
\]

## TL-052 — Effective mass `[H]`

\[
\boxed{
m_{\rm eff}^2
=
V_{,\phi\phi}(\phi_*)
+\rho A_{,\phi\phi}(\phi_*)
}
\]

For the selected functions,

\[
\boxed{
m_{\rm eff}^2
=
m_\phi^2
+3\lambda_\phi(\phi_*-\phi_0)^2
+\frac{\beta^2\rho}{M_{\rm Pl}^2}A(\phi_*)
}
\]

## TL-053 — Weak-displacement solution `[H]`

\[
\boxed{
\phi_*-\phi_0
\simeq
-\frac{\beta\rho}{M_{\rm Pl}m_\phi^2}
}
\]

valid when

\[
\boxed{
\frac{\beta^2\rho}{M_{\rm Pl}^2m_\phi^2}\ll1
}
\]

---

# G. Stability, propagation and EFT domain

## TL-060 — Quadratic kinetic action `[H]`

\[
S_{\rm kin}^{(2)}
=
\int d^4x\,a^3
\left[
\frac{M_{\rm Pl}^2}{8}
\dot h_{ij}^{\rm TT}\dot h_{ij}^{\rm TT}
-
\frac{M_{\rm Pl}^2}{8a^2}
(\partial_kh_{ij}^{\rm TT})^2
+
\frac12\dot\varphi^2
-
\frac{1}{2a^2}(\nabla\varphi)^2
\right].
\]

## TL-061 — Positive kinetic coefficients `[H]`

\[
\boxed{
Q_T=\frac{M_{\rm Pl}^2}{4}>0,
\qquad
Q_\phi=1>0
}
\]

## TL-062 — Propagation speeds `[H]`

\[
\boxed{
c_T^2=1,
\qquad
c_\phi^2=1
}
\]

## TL-063 — Minimal stability conditions `[H]`

\[
\boxed{
M_{\rm Pl}^2>0,
\qquad
A(\phi)>0,
\qquad
m_{\rm eff}^2\ge0,
\qquad
\lambda_\phi\ge0
}
\]

## TL-064 — EFT validity conditions `[E/H]`

\[
\boxed{
E\ll\Lambda_{\rm EFT},
\qquad
\frac{E}{M_{\rm Pl}}\ll1,
\qquad
\frac{|\beta|E}{M_{\rm Pl}}\ll1
}
\]

These conditions support low-energy consistency only. They do not prove a ghost-free ultraviolet completion.

---

# H. Canonical quantum spacetime

## TL-070 — ADM decomposition `[E]`

\[
\boxed{
ds^2
=
-N^2dt^2
+q_{ij}(dx^i+N^idt)(dx^j+N^jdt)
}
\]

## TL-071 — Gravitational canonical momentum `[E]`

\[
\boxed{
\pi^{ij}
=
\frac{M_{\rm Pl}^2\sqrt q}{2}
(K^{ij}-q^{ij}K)
}
\]

## TL-072 — Hamiltonian constraint `[E/H]`

\[
\boxed{
\mathcal H
=
\frac{2}{M_{\rm Pl}^2\sqrt q}
\left(\pi_{ij}\pi^{ij}-\frac12\pi^2\right)
-
\frac{M_{\rm Pl}^2}{2}\sqrt q
({}^{(3)}R-2\Lambda)
+
\mathcal H_\phi
+
\mathcal H_Q
=0
}
\]

## TL-073 — Momentum constraint `[E/H]`

\[
\boxed{
\mathcal H_i
=
-2D_j\pi^j{}_i
+\pi_\phi\partial_i\phi
+\mathcal H_i^Q
=0
}
\]

## TL-074 — Thin Line scalar Hamiltonian `[H]`

\[
\boxed{
\mathcal H_\phi
=
\frac{\pi_\phi^2}{2\sqrt q}
+
\sqrt q
\left[
\frac12q^{ij}\partial_i\phi\partial_j\phi
+V(\phi)
\right]
}
\]

## TL-075 — Canonical quantisation `[E/H]`

\[
\boxed{
\pi^{ij}
\rightarrow
-i\hbar\frac{\delta}{\delta q_{ij}},
\qquad
\pi_\phi
\rightarrow
-i\hbar\frac{\delta}{\delta\phi}
}
\]

## TL-076 — Quantum-spacetime state `[E/H]`

\[
\boxed{
\boldsymbol\Psi
=
\boldsymbol\Psi[q_{ij},\phi,\Psi]
}
\]

## TL-077 — Wheeler–DeWitt constraints `[E/H]`

\[
\boxed{
\widehat{\mathcal H}\boldsymbol\Psi=0,
\qquad
\widehat{\mathcal H}_i\boldsymbol\Psi=0
}
\]

## TL-078 — Superposition of geometries `[H]`

\[
\boxed{
|\Omega\rangle
=
\sum_a c_a
|g_{\mu\nu}^{(a)},\phi_a,\Psi_a\rangle
}
\]

This is the central quantum-spacetime statement in the current canonical construction.

---

# I. Semiclassical emergence

## TL-080 — WKB/Born–Oppenheimer ansatz `[E/H]`

\[
\boxed{
\boldsymbol\Psi[q,\phi,\Psi]
=
A[q]
\exp\!\left[
\frac{iM_{\rm Pl}^2}{\hbar}S_0[q]
\right]
\chi[q,\phi,\Psi]
}
\]

## TL-081 — Gravitational Hamilton–Jacobi equation `[E/H]`

\[
\boxed{
\frac{2}{\sqrt q}
\left(
\frac{\delta S_0}{\delta q_{ij}}
\frac{\delta S_0}{\delta q^{ij}}
-
\frac12
\left(q_{ij}\frac{\delta S_0}{\delta q_{ij}}\right)^2
\right)
-
\frac12\sqrt q
({}^{(3)}R-2\Lambda)
=0
}
\]

Its characteristic trajectories recover classical Einstein geometries.

## TL-082 — Emergent matter Schrödinger equation `[E/H]`

\[
\boxed{
i\hbar
\frac{\partial\chi}{\partial t_{\rm WKB}}
=
(\widehat H_\phi+\widehat H_Q)\chi
}
\]

## TL-083 — Quantum–relativistic Thin Line regime `[D/H]`

\[
\boxed{
\mathcal T_{\rm QR}
=
\left\{
(q,\phi,\Psi)
\;\middle|\;
\epsilon_{\rm WKB}\ll1,
\;E/M_{\rm Pl}\ll1,
\;\chi\text{ remains quantum}
\right\}
}
\]

## TL-084 — WKB control parameter `[D/H]`

\[
\boxed{
\epsilon_{\rm WKB}
\sim
\frac{
\hbar\,\delta^2S_0/\delta q^2
}{
M_{\rm Pl}^2(\delta S_0/\delta q)^2
}
}
\]

---

# J. Local graviton sector

## TL-090 — Quantised metric perturbation `[E/H]`

\[
\boxed{
\widehat g_{\mu\nu}
=
\bar g_{\mu\nu}
+\frac{2}{M_{\rm Pl}}\widehat h_{\mu\nu}
}
\]

## TL-091 — Graviton mode expansion `[E/H]`

\[
\widehat h_{ij}^{\rm TT}(x)
=
\sum_{\lambda=+,\times}
\int\frac{d^3k}{(2\pi)^3}
\frac{e_{ij}^{(\lambda)}(\mathbf k)}{\sqrt{2\omega_{\mathbf k}}}
\left[
\widehat a_\lambda(\mathbf k)e^{-ikx}
+
\widehat a_\lambda^\dagger(\mathbf k)e^{ikx}
\right].
\]

## TL-092 — Graviton commutator `[E/H]`

\[
\boxed{
[
\widehat a_\lambda(\mathbf k),
\widehat a_{\lambda'}^\dagger(\mathbf k')
]
=
(2\pi)^3
\delta_{\lambda\lambda'}
\delta^3(\mathbf k-\mathbf k')
}
\]

---

# K. Falsifiable observables

## TL-100 — Thin Line interaction range `[H]`

\[
\boxed{
\lambda_{\rm TL}
=
\frac{\hbar}{m_\phi c}
}
\]

## TL-101 — Yukawa-corrected gravitational potential `[H]`

\[
\boxed{
U(r)
=
-\frac{Gm_1m_2}{r}
\left[
1+2\beta^2e^{-r/\lambda_{\rm TL}}
\right]
}
\]

## TL-102 — Modified force law `[H]`

\[
\boxed{
F(r)
=
-\frac{Gm_1m_2}{r^2}
\left[
1+
2\beta^2
\left(1+\frac{r}{\lambda_{\rm TL}}\right)
e^{-r/\lambda_{\rm TL}}
\right]
}
\]

A null inverse-square-law test excludes a region in the \((m_\phi,\beta)\) parameter plane.

## TL-103 — Low-energy quantum-gravity correction `[E]`

\[
\boxed{
U_{\rm QG}(r)
=
-\frac{Gm_1m_2}{r}
\left[
1+
\frac{41}{10\pi}
\frac{\ell_{\rm Pl}^2}{r^2}
+\cdots
\right]
}
\]

where

\[
\boxed{
\ell_{\rm Pl}
=
\sqrt{\frac{G\hbar}{c^3}}
}
\]

## TL-104 — Combined Thin Line quantum potential `[H]`

\[
\boxed{
U_{\rm TLQ}(r)
=
-\frac{Gm_1m_2}{r}
\left[
1
+2\beta^2e^{-r/\lambda_{\rm TL}}
+\frac{41}{10\pi}\frac{\ell_{\rm Pl}^2}{r^2}
+\cdots
\right]
}
\]

## TL-105 — Gravity-mediated entanglement phase `[E/H]`

\[
\boxed{
\Phi_{\rm ent}
=
\frac{Gm_1m_2t}{\hbar}
\left(
\frac1{r_{LL}}
+\frac1{r_{RR}}
-\frac1{r_{LR}}
-\frac1{r_{RL}}
\right)
}
\]

Observation of entanglement under controlled conditions would support nonclassical gravitational mediation, but would not uniquely validate the Thin Line model.

---

# L. Existing project phenomenology

The equations in this section are part of the wider Thin Line project but are not yet derived from TL-010.

## TL-110 — Topological phenomenological functional `[P]`

\[
\boxed{
\lambda_{\rm TL}^{(\rm top)}
=
Q_{\rm top}^{\,2}
R
\log\!\left(
1+\frac{E_{\rm SB}}{E_P}
\right)
}
\]

## TL-111 — Time-dependent phenomenological form `[P]`

\[
\boxed{
\lambda_{\rm TL}^{(\rm dyn)}(t)
=
R(t)S_B(t)P(t)
}
\]

## TL-112 — Thin Line eigenvalue equation `[P]`

\[
\boxed{
\widehat P\psi_n
=
\lambda_n\psi_n
}
\]

## TL-113 — Symbolic genesis ordering `[P]`

\[
\boxed{
\Alpha
\longrightarrow
\mathcal S_{\rm potential}
\longrightarrow
\Omega
}
\]

## TL-114 — Potential-state notation `[P]`

\[
\boxed{
0^\infty\in\{0,1\}
}
\]

This is symbolic notation, not standard exponentiation. A separate semantic specification is required before it can enter the executable mathematical model.

---

# M. Master hierarchy

\[
\boxed{
\boldsymbol\Psi[q,\phi,\Psi]
\;\longrightarrow\;
g_{\mu\nu}^{\rm GR}
+\text{quantum fields}
\;\longrightarrow\;
\text{ordinary QFT}
\;\longrightarrow\;
\text{nonrelativistic quantum mechanics}
}
\]

The Thin Line compatibility regime is

\[
\boxed{
\mathcal T_{\rm QR}
=
\text{semiclassical geometry}
\cap
\text{quantum matter}
\cap
\text{stable interface coupling}
}
\]

---

# N. Validation requirements

Before promotion beyond hypothesis status, the following work is required:

1. derive the complete second-order perturbation action on relevant backgrounds;
2. verify the full kinetic and gradient matrices are positive;
3. define a cutoff and demonstrate \(\Lambda_{\rm strong}\gg H\) or the relevant laboratory energy scale;
4. calculate post-Newtonian parameters and compare them with Solar-System and binary-pulsar constraints;
5. derive cosmological background and perturbation equations;
6. compute \(H(z)\), \(w(z)\), \(\mu(k,a)\), \(\eta(k,a)\), \(\Sigma(k,a)\), and \(f\sigma_8\);
7. constrain \((m_\phi,\beta,\lambda_\phi)\) with inverse-square-law, equivalence-principle, pulsar, gravitational-wave and cosmological data;
8. specify a regulated Wheeler–DeWitt operator, physical inner product and relational observables;
9. define the relation, if any, between TL-110/TL-111 and the action TL-010;
10. release reproducible symbolic and numerical test suites.

---

# O. Current status matrix

| Component | Status |
|---|---|
| Einstein, Klein–Gordon, Schrödinger and ADM equations | `[E]` established formalism |
| Scalar–tensor Thin Line action | `[H]` testable model proposal |
| Stable effective-potential manifold | `[H]` derived inside the proposal |
| Wheeler–DeWitt quantum-spacetime layer | `[E/H]` recognised formalism, unresolved completion |
| Yukawa deviation | `[H]` falsifiable model prediction |
| Gravity-mediated entanglement phase | `[E/H]` established proposal, not Thin-Line-specific |
| Topological and dynamic \(\lambda_{\rm TL}\) functionals | `[P]` phenomenological |
| \(0^\infty\) notation | `[P]` symbolic; semantics pending |
| Completed Theory of Everything | not established |

---

## Version notes

- **v0.1:** first consolidated equation register.
- Equation identifiers are stable within the v0.x series unless explicitly deprecated.
- Any future equation change must record its derivation, assumptions, dimensions, status class and replacement relation.
