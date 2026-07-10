#!/usr/bin/env python3
"""
Deliverable 5 - Stage 2 Reducer
Averages the per-record squared errors emitted by mapper_mse.py to
obtain the Mean Squared Error of the fitted two-variable model:

    MSE = (1/N) * sum((y_i - y_hat_i)^2)

Compare this value against Deliverable 4's one-variable MSE in the
report: a lower MSE here means adding Relative Humidity as a second
explanatory variable improved the prediction of Dry Bulb Temp.
"""
import sys

n = 0
sum_squared_error = 0.0

for raw_line in sys.stdin:
    line = raw_line.rstrip("\n")
    if not line:
        continue
    _key, value = line.split("\t", 1)
    sum_squared_error += float(value)
    n += 1

if n > 0:
    mse = sum_squared_error / n
    print(f"n={n}\tMSE={mse}")
