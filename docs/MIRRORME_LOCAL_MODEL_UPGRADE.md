# MirrorME Local Model Upgrade

This upgrade adds complex matrix validation to the MK-HIGE information engine so MirrorME can reject or repair invalid density-like local model states before using them in metrics, memory, or runtime loops.

## Purpose

MirrorME local state updates should preserve basic density-matrix invariants when complex-valued representations are used:

```text
shape is square
entries are finite
rho is Hermitian-like
trace is real and normalized to 1
imaginary trace drift is rejected before normalization
negative diagonal drift is clamped during beta repair
```

This is a software safety layer. It is quantum-information-inspired validation, not a physical quantum backend.

## Files

```text
lib/hige/complexMatrix.ts
lib/hige/complexRuntimeValidation.ts
lib/hige/tsconfig.json
```

## Run

```bash
npm install
npm run test:hige:complex
npm run typecheck:hige
```

## Runtime rule

```text
No complex local-model state enters HIGE metrics unless it is square, finite, Hermitian-repaired, and trace-normalized with near-zero imaginary trace.
```

## Correct validation sequence

```text
validate shape
validate finite entries
repair Hermitian symmetry
compute trace
reject large imaginary trace drift
normalize by real trace
validate final state
```

## Integration target

The complex validator can be used before:

```text
HIGE metric calculation
QHEL candidate rho update
MirrorME local model memory write
Phase Anchor correction
MeraGraph projection
```
