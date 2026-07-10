#!/usr/bin/env python3
"""
Deliverable 5 - Stage 2 Mapper
Computes the squared prediction error for every record, using the
b0/b1/b2 coefficients fitted by stage 1 (reducer_coeff.py).

Coefficients are passed in via Hadoop Streaming's -cmdenv option, e.g.:
    -cmdenv B0=1.02 -cmdenv B1=0.83 -cmdenv B2=-0.05

PSEUDOCODE
----------
b0, b1, b2 <- read from environment (fitted in stage 1)
for each line of input:
    fields <- split(line, ",")
    if line is the CSV header: skip it
    x1 <- float(fields[DewPointCelsius])
    x2 <- float(fields[RelativeHumidity])
    y  <- float(fields[DryBulbCelsius])
    if x1, x2 and y are all valid:
        y_hat <- b0 + b1*x1 + b2*x2
        squared_error <- (y - y_hat) ** 2
        emit(key = "mse", value = squared_error)
"""
import os
import sys
from weather_columns import parse_fields, get_field

B0 = float(os.environ.get("B0", "0"))
B1 = float(os.environ.get("B1", "0"))
B2 = float(os.environ.get("B2", "0"))

for raw_line in sys.stdin:
    fields = parse_fields(raw_line)
    if fields is None:
        continue

    x1 = get_field(fields, "DewPointCelsius")
    x2 = get_field(fields, "RelativeHumidity")
    y = get_field(fields, "DryBulbCelsius")

    if x1 is not None and x2 is not None and y is not None:
        y_hat = B0 + B1 * x1 + B2 * x2
        squared_error = (y - y_hat) ** 2
        print(f"mse\t{squared_error}")
