#!/usr/bin/env python3
"""
Deliverable 4 - Stage 2 Reducer
Averages the per-record squared errors emitted by mapper_mse.py to
obtain the Mean Squared Error of the fitted one-variable model:

    MSE = (1/N) * sum((y_i - y_hat_i)^2)
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
