# MK-HIGE Information System Engine

Status: research prototype module.

This module adds a measurable information-system core for MK-HIGE. It is implemented as pure TypeScript under `lib/hige/index.ts`.

## Purpose

The engine evaluates an evolving normalized state matrix using four values:

- coherence / purity
- entropy potential
- resonance / state-change rate
- bounded harmony score

It is a computational engine, not a validated physics engine.

## Core formulas

Purity:

```text
C = Tr(rho^2)
```

Normalized coherence:

```text
C_norm = (C - 1/d) / (1 - 1/d)
```

Entropy potential, diagonal approximation:

```text
S = -sum_i p_i log(p_i)
```

Normalized potential:

```text
P_norm = S / log(d)
```

Resonance:

```text
R = ||(rho_next - rho_prev) / dt||_F
```

Bounded resonance:

```text
R_norm = R / (R + kappa)
```

Harmony:

```text
H = w_C C_norm + w_S P_norm + w_R R_norm
```

Information ratio:

```text
I = C_norm / (P_norm + epsilon)
```

## Notes

The entropy implementation currently uses the matrix diagonal as a probability distribution. This is safe for a beta engine and avoids adding a numerical eigenvalue dependency. A later version can add a Hermitian eigenvalue solver for full von Neumann entropy.

## Example

```ts
import { computeHigeMetrics } from "./lib/hige";

const previous = [
  [0.5, 0],
  [0, 0.5],
];

const current = [
  [0.7, 0],
  [0, 0.3],
];

const metrics = computeHigeMetrics(previous, current, { dt: 1 });
console.log(metrics.harmony);
```

## Boundary

Do not treat output as biological, spiritual, hardware, or cosmological measurement unless connected to verified instrumentation and validation data.
