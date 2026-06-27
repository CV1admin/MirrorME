import {
  complex,
  createComplexIdentityDensityMatrix,
  repairComplexDensityLikeMatrix,
  validateComplexDensityLikeMatrix,
  validateComplexTraceNormalization,
  validateHermitian,
  type ComplexMatrix,
} from "./complexMatrix";

const assert = (condition: boolean, label: string): void => {
  if (!condition) {
    throw new Error(`HIGE complex validation failed: ${label}`);
  }
  console.log(`${label}: passed`);
};

const unstable: ComplexMatrix = {
  rows: 2,
  cols: 2,
  dataType: "complex",
  data: [
    complex(0.9, 0.2),
    complex(0.2, 0.4),
    complex(0.6, -0.1),
    complex(-0.1, -0.2),
  ],
};

const repaired = repairComplexDensityLikeMatrix(unstable);
const validation = validateComplexDensityLikeMatrix(repaired);
const identity = createComplexIdentityDensityMatrix(2);

console.log("MirrorME HIGE complex matrix validation");
assert(validation.valid, "complex matrix validity");
assert(validateHermitian(repaired), "Hermitian repair");
assert(validateComplexTraceNormalization(repaired), "complex trace normalization");
assert(validateComplexTraceNormalization(identity), "identity complex density matrix");
assert(validation.trace.real > 0.999999 && validation.trace.real < 1.000001, "real trace equals one");
assert(Math.abs(validation.trace.imag) < 1e-8, "imaginary trace suppressed");
