#!/usr/bin/env python3
"""
Deliverable 2 - Mapper
Covariance & correlation between Dry Bulb Temp and two other variables:
Dew Point Temp and Relative Humidity.

PSEUDOCODE
----------
for each line of input:
    fields <- split(line, ",")
    if line is the CSV header: skip it
    dbt <- float(fields[DryBulbTemp])
    dew <- float(fields[DewPointTemp])
    rh  <- float(fields[RelativeHumidity])
    if dbt and dew are both valid:
        emit(key = "DBT_vs_DewPoint", value = (dbt, dew))
    if dbt and rh are both valid:
        emit(key = "DBT_vs_RelativeHumidity", value = (dbt, rh))

Every mapper only ever emits two possible keys, so the shuffle phase
routes every (x, y) pair for a given variable-pair to one reducer group,
which is exactly what lets that reducer accumulate the running sums
needed for covariance/correlation without seeing the whole dataset.
"""
import sys
from weather_columns import parse_fields, get_field

for raw_line in sys.stdin:
    fields = parse_fields(raw_line)
    if fields is None:
        continue

    dry_bulb_temp = get_field(fields, "DryBulbTemp")
    dew_point_temp = get_field(fields, "DewPointTemp")
    relative_humidity = get_field(fields, "RelativeHumidity")

    if dry_bulb_temp is not None and dew_point_temp is not None:
        print(f"DBT_vs_DewPoint\t{dry_bulb_temp},{dew_point_temp}")

    if dry_bulb_temp is not None and relative_humidity is not None:
        print(f"DBT_vs_RelativeHumidity\t{dry_bulb_temp},{relative_humidity}")
