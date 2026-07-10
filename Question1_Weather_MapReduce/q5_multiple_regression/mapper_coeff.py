#!/usr/bin/env python3
"""
Deliverable 5 - Stage 1 Mapper
Fit  Dry Bulb Temp (y) ~ Dew Point Temp (x1) + Relative Humidity (x2)
by multiple linear regression. This mapper just emits the raw
(x1, x2, y) triples the reducer needs.

PSEUDOCODE
----------
for each line of input:
    fields <- split(line, ",")
    if line is the CSV header: skip it
    x1 <- float(fields[DewPointCelsius])
    x2 <- float(fields[RelativeHumidity])
    y  <- float(fields[DryBulbCelsius])
    if x1, x2 and y are all valid:
        emit(key = "constant_identifier", value = (x1, x2, y))

As in Deliverable 4, every mapper emits to the same key so all triples
are shuffled to one reducer, which accumulates the running sums the
normal equations need.
"""
import sys
from weather_columns import parse_fields, get_field

for raw_line in sys.stdin:
    fields = parse_fields(raw_line)
    if fields is None:
        continue

    x1 = get_field(fields, "DewPointCelsius")     # explanatory variable 1
    x2 = get_field(fields, "RelativeHumidity")    # explanatory variable 2
    y = get_field(fields, "DryBulbCelsius")       # response variable

    if x1 is not None and x2 is not None and y is not None:
        print(f"constant_identifier\t{x1},{x2},{y}")
