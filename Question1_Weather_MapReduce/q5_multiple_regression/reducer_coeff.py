#!/usr/bin/env python3
"""
Deliverable 5 - Stage 1 Reducer
Fits  y = b0 + b1*x1 + b2*x2  by multiple linear regression.

Distributed part: every mapper contributes to nine running sums
(n, Sx1, Sx2, Sy, Sx1x1, Sx2x2, Sx1x2, Sx1y, Sx2y) - exactly the same
streaming-accumulation pattern as the simple regression in Deliverable
4, just with more running totals. Those nine numbers are all a single
reducer needs, regardless of how many rows fed into them.

Centralised part: once we have the nine sums, fitting the model is just
solving the 3x3 system of "normal equations" below for (b0, b1, b2).
That is a tiny, fixed-size computation, so it is done once in the
reducer rather than distributed further:

    n*b0    + Sx1*b1   + Sx2*b2   = Sy
    Sx1*b0  + Sx1x1*b1 + Sx1x2*b2 = Sx1y
    Sx2*b0  + Sx1x2*b1 + Sx2x2*b2 = Sx2y

We solve this 3x3 linear system with Cramer's rule (determinants),
implemented by hand below - no numpy/scipy linear-algebra routines are
used, per the coursework's "no ready-made statistical packages" rule.
"""
import sys

n = 0
Sx1 = Sx2 = Sy = 0.0
Sx1x1 = Sx2x2 = Sx1x2 = 0.0
Sx1y = Sx2y = 0.0

for raw_line in sys.stdin:
    line = raw_line.rstrip("\n")
    if not line:
        continue
    _key, value = line.split("\t", 1)
    x1_str, x2_str, y_str = value.split(",", 2)
    x1, x2, y = float(x1_str), float(x2_str), float(y_str)

    n += 1
    Sx1 += x1
    Sx2 += x2
    Sy += y
    Sx1x1 += x1 * x1
    Sx2x2 += x2 * x2
    Sx1x2 += x1 * x2
    Sx1y += x1 * y
    Sx2y += x2 * y


def det3(matrix):
    """Determinant of a 3x3 matrix, given as a list of three rows."""
    (a, b, c), (d, e, f), (g, h, i) = matrix
    return (a * (e * i - f * h)
            - b * (d * i - f * g)
            + c * (d * h - e * g))


if n > 0:
    # Coefficient matrix and right-hand-side vector from the normal
    # equations above.
    coeff_matrix = [
        [n, Sx1, Sx2],
        [Sx1, Sx1x1, Sx1x2],
        [Sx2, Sx1x2, Sx2x2],
    ]
    rhs = [Sy, Sx1y, Sx2y]

    det_main = det3(coeff_matrix)
    if det_main != 0:
        # Cramer's rule: to solve for coefficient k, replace column k of
        # the coefficient matrix with the right-hand-side vector.
        matrix_b0 = [row[:] for row in coeff_matrix]
        matrix_b1 = [row[:] for row in coeff_matrix]
        matrix_b2 = [row[:] for row in coeff_matrix]
        for row_idx in range(3):
            matrix_b0[row_idx][0] = rhs[row_idx]
            matrix_b1[row_idx][1] = rhs[row_idx]
            matrix_b2[row_idx][2] = rhs[row_idx]

        b0 = det3(matrix_b0) / det_main   # intercept
        b1 = det3(matrix_b1) / det_main   # coefficient on Dew Point Temp
        b2 = det3(matrix_b2) / det_main   # coefficient on Relative Humidity

        # This line is the input the stage-2 job needs (see mapper_mse.py) -
        # copy b0/b1/b2 into -cmdenv B0=... B1=... B2=...
        print(f"n={n}\tintercept={b0}\t"
              f"coef_DewPointCelsius={b1}\tcoef_RelativeHumidity={b2}")
    else:
        print("error\tsingular matrix: DewPointCelsius and "
              "RelativeHumidity are perfectly collinear in this data, "
              "so unique coefficients cannot be found")
