#!/usr/bin/env python3
"""
Deliverable 4 - Stage 1 Mapper
Fit  Dry Bulb Temp (y) ~ Dew Point Temp (x)  by simple linear regression.
This mapper just emits the raw (x, y) pairs the reducer needs.

PSEUDOCODE (matches the coursework's Statistical Computation Guide)
--------------------------------------------------------------------
for each line of input:
    fields <- split(line, ",")
    if line is the CSV header: skip it
    x <- float(fields[DewPointTemp])     # explanatory variable
    y <- float(fields[DryBulbTemp])      # response variable
    if x and y are both valid:
        emit(key = "constant_identifier", value = (x, y))

Every mapper deliberately emits to the *same* key: this forces every
(x, y) pair to be shuffled to a single reducer, which is what lets that
reducer accumulate the global sums (n, Sx, Sy, Sxx, Sxy) the closed-form
regression formulas need.
"""
import sys
from weather_columns import parse_fields, get_field

for raw_line in sys.stdin:
    fields = parse_fields(raw_line)
    if fields is None:
        continue

    x = get_field(fields, "DewPointTemp")   # explanatory variable
    y = get_field(fields, "DryBulbTemp")    # response variable

    if x is not None and y is not None:
        print(f"constant_identifier\t{x},{y}")
