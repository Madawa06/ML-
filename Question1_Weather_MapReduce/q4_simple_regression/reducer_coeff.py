#!/usr/bin/env python3
"""
Deliverable 4 - Stage 1 Reducer
Fits  y = m*x + b  using the closed-form ordinary-least-squares formulas
given in the coursework brief:

    Slope (m)     = (n*Sxy - Sx*Sy) / (n*Sxx - Sx^2)
    Intercept (b) = (Sy - m*Sx) / n

All (x, y) pairs arrive under the single key "constant_identifier", so
this reducer streams through them once, keeping four running totals
(Sx, Sy, Sxx, Sxy) plus the count n - it never needs to hold the whole
dataset in memory, which is what makes the fit distributable.
"""
import sys

n = 0
Sx = Sy = Sxx = Sxy = 0.0

for raw_line in sys.stdin:
    line = raw_line.rstrip("\n")
    if not line:
        continue
    _key, value = line.split("\t", 1)
    x_str, y_str = value.split(",", 1)
    x, y = float(x_str), float(y_str)

    n += 1
    Sx += x
    Sy += y
    Sxx += x ** 2
    Sxy += x * y

if n > 0:
    denominator = (n * Sxx) - (Sx ** 2)
    slope = ((n * Sxy) - (Sx * Sy)) / denominator
    intercept = (Sy - slope * Sx) / n
    # This line is the input the stage-2 job needs (see mapper_mse.py) -
    # copy the slope/intercept values into -cmdenv SLOPE=... INTERCEPT=...
    print(f"n={n}\tslope={slope}\tintercept={intercept}")
