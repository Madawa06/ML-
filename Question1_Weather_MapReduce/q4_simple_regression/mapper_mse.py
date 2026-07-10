#!/usr/bin/env python3
"""
Deliverable 4 - Stage 2 Mapper
Computes the squared prediction error for every record, using the
slope/intercept fitted by stage 1 (reducer_coeff.py).

The fitted coefficients are passed in as environment variables via
Hadoop Streaming's -cmdenv option, e.g.:
    -cmdenv SLOPE=0.912 -cmdenv INTERCEPT=1.734

PSEUDOCODE
----------
slope, intercept <- read from environment (fitted in stage 1)
for each line of input:
    fields <- split(line, ",")
    if line is the CSV header: skip it
    x <- float(fields[DewPointCelsius])
    y <- float(fields[DryBulbCelsius])
    if x and y are both valid:
        y_hat <- slope * x + intercept
        squared_error <- (y - y_hat) ** 2
        emit(key = "mse", value = squared_error)
"""
import os
import sys
from weather_columns import parse_fields, get_field

SLOPE = float(os.environ.get("SLOPE", "0"))
INTERCEPT = float(os.environ.get("INTERCEPT", "0"))

for raw_line in sys.stdin:
    fields = parse_fields(raw_line)
    if fields is None:
        continue

    x = get_field(fields, "DewPointCelsius")
    y = get_field(fields, "DryBulbCelsius")

    if x is not None and y is not None:
        y_hat = SLOPE * x + INTERCEPT
        squared_error = (y - y_hat) ** 2
        print(f"mse\t{squared_error}")
