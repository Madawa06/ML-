#!/usr/bin/env python3
"""
Deliverable 3 - Mapper
Station-level summary statistics for Dry Bulb Temp and Wind Speed:
count, mean, population variance, standard deviation, min, and max,
computed separately for every weather station (WBAN id).

PSEUDOCODE
----------
for each line of input:
    fields <- split(line, ",")
    if line is the CSV header: skip it
    station <- fields[Wban]
    dbt  <- float(fields[DryBulbTemp])
    wspd <- float(fields[WindSpeed])
    if dbt valid:
        emit(key = station + "_DBT", value = dbt)
    if wspd valid:
        emit(key = station + "_WS", value = wspd)
"""
import sys
from weather_columns import parse_fields, get_field, IDX

for raw_line in sys.stdin:
    fields = parse_fields(raw_line)
    if fields is None:
        continue

    station = fields[IDX["WbanNumber"]].strip()

    dry_bulb_temp = get_field(fields, "DryBulbTemp")
    if dry_bulb_temp is not None:
        print(f"{station}_DBT\t{dry_bulb_temp}")

    wind_speed = get_field(fields, "WindSpeed")
    if wind_speed is not None:
        print(f"{station}_WS\t{wind_speed}")
