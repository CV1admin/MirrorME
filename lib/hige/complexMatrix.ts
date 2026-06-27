export type Complex = {
  real: number;
  imag: number;
};

export type ComplexMatrix = {
  rows: number;
  cols: number;
  dataType: "complex";
  data: Complex[];
};

export type ComplexMatrixValidation = {
  valid: boolean;
  errors: string[];
  warnings: string[];
  trace: Complex;
  hermitian: boolean;
};

const DEFAULT_REAL_TOLERANCE = 1e-6;
const DEFAULT_IMAG_TOLERANCE = 1e-8;

export const complex = (real: number, imag = 0): Complex => ({ real, imag });

export const isFiniteComplex = (value: Complex): boolean =>
  Number.isFinite(value.real) && Number.isFinite(value.imag);

export const cloneComplexMatrix = (matrix: ComplexMatrix): ComplexMatrix => ({
  rows: matrix.rows,
  cols: matrix.cols,
  dataType: "complex",
  data: matrix.data.map((value) => ({ ...value })),
});

const indexOf = (matrix: ComplexMatrix, row: number, col: number): number => row * matrix.cols + col;

export const isSquareComplexMatrix = (matrix: ComplexMatrix): boolean =>
  matrix.rows > 0 && matrix.rows === matrix.cols && matrix.data.length === matrix.rows * matrix.cols;

export const getComplexAt = (matrix: ComplexMatrix, row: number, col: number): Complex => {
  const value = matrix.data[indexOf(matrix, row, col)];
  if (!value) return complex(0, 0);
  return value;
};

export const setComplexAt = (matrix: ComplexMatrix, row: number, col: number, value: Complex): void => {
  matrix.data[indexOf(matrix, row, col)] = value;
};

export const conjugate = (value: Complex): Complex => complex(value.real, -value.imag);

export const computeComplexTrace = (matrix: ComplexMatrix): Complex => {
  if (!isSquareComplexMatrix(matrix)) return complex(Number.NaN, Number.NaN);

  let real = 0;
  let imag = 0;
  for (let i = 0; i < matrix.rows; i += 1) {
    const value = getComplexAt(matrix, i, i);
    real += value.real;
    imag += value.imag;
  }
  return complex(real, imag);
};

export const validateComplexTraceNormalization = (
  matrix: ComplexMatrix,
  realTolerance = DEFAULT_REAL_TOLERANCE,
  imagTolerance = DEFAULT_IMAG_TOLERANCE,
): boolean => {
  const trace = computeComplexTrace(matrix);
  return Math.abs(trace.real - 1) <= realTolerance && Math.abs(trace.imag) <= imagTolerance;
};

export const validateHermitian = (matrix: ComplexMatrix, tolerance = DEFAULT_IMAG_TOLERANCE): boolean => {
  if (!isSquareComplexMatrix(matrix)) return false;

  for (let row = 0; row < matrix.rows; row += 1) {
    for (let col = 0; col < matrix.cols; col += 1) {
      const a = getComplexAt(matrix, row, col);
      const b = conjugate(getComplexAt(matrix, col, row));
      if (Math.abs(a.real - b.real) > tolerance || Math.abs(a.imag - b.imag) > tolerance) {
        return false;
      }
    }
  }

  return true;
};

export const hermitianRepair = (matrix: ComplexMatrix): ComplexMatrix => {
  if (!isSquareComplexMatrix(matrix)) {
    throw new Error("hermitianRepair requires a square complex matrix.");
  }

  const repaired = cloneComplexMatrix(matrix);
  for (let row = 0; row < matrix.rows; row += 1) {
    for (let col = 0; col < matrix.cols; col += 1) {
      const a = getComplexAt(matrix, row, col);
      const b = conjugate(getComplexAt(matrix, col, row));
      const value = complex((a.real + b.real) / 2, (a.imag + b.imag) / 2);
      setComplexAt(repaired, row, col, row === col ? complex(Math.max(0, value.real), 0) : value);
    }
  }

  return repaired;
};

export const normalizeComplexTrace = (
  matrix: ComplexMatrix,
  imagTolerance = DEFAULT_IMAG_TOLERANCE,
): ComplexMatrix => {
  const trace = computeComplexTrace(matrix);

  if (!Number.isFinite(trace.real) || Math.abs(trace.real) <= Number.EPSILON) {
    throw new Error("Cannot normalize complex matrix with invalid or zero real trace.");
  }

  if (Math.abs(trace.imag) > imagTolerance) {
    throw new Error("Cannot normalize complex matrix before repairing imaginary trace drift.");
  }

  return {
    rows: matrix.rows,
    cols: matrix.cols,
    dataType: "complex",
    data: matrix.data.map((value) => complex(value.real / trace.real, value.imag / trace.real)),
  };
};

export const repairComplexDensityLikeMatrix = (matrix: ComplexMatrix): ComplexMatrix =>
  normalizeComplexTrace(hermitianRepair(matrix));

export const validateComplexDensityLikeMatrix = (matrix: ComplexMatrix): ComplexMatrixValidation => {
  const errors: string[] = [];
  const warnings: string[] = [];

  if (!isSquareComplexMatrix(matrix)) {
    errors.push("Complex matrix must be square and data length must equal rows * cols.");
  }

  if (!matrix.data.every(isFiniteComplex)) {
    errors.push("Complex matrix entries must be finite.");
  }

  const trace = computeComplexTrace(matrix);
  const hermitian = validateHermitian(matrix);

  if (!hermitian) warnings.push("Complex matrix is not Hermitian within tolerance.");
  if (!validateComplexTraceNormalization(matrix)) {
    warnings.push("Complex trace is not normalized to real trace 1 with near-zero imaginary part.");
  }

  return { valid: errors.length === 0, errors, warnings, trace, hermitian };
};

export const createComplexIdentityDensityMatrix = (dimension: number): ComplexMatrix => {
  if (!Number.isInteger(dimension) || dimension <= 0) {
    throw new Error("dimension must be a positive integer.");
  }

  return {
    rows: dimension,
    cols: dimension,
    dataType: "complex",
    data: Array.from({ length: dimension * dimension }, (_, index) => {
      const row = Math.floor(index / dimension);
      const col = index % dimension;
      return complex(row === col ? 1 / dimension : 0, 0);
    }),
  };
};
