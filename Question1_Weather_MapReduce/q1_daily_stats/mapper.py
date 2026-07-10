#!/usr/bin/env python3
"""
Deliverable 1 - Mapper
Daily min/max/mean/std of Dry Bulb Temp, and daily average/max Wind Speed
(aggregated across all weather stations) for the selected month.

PSEUDOCODE
----------
for each line of input:
    fields <- split(line, ",")
    if line is the CSV header: skip it
    date <- fields[YearMonthDay]                      # e.g. "20070401"
    dbt  <- float(fields[DryBulbTemp])
    wspd <- float(fields[WindSpeed])
    if dbt is a valid reading:
        emit(key = date, value = ("DBT", dbt))
    if wspd is a valid reading:
        emit(key = date, value = ("WS", wspd))

Hadoop Streaming represents a (key, value) pair as one tab-separated
line "key\\tvalue"; here value itself is a small comma-separated tag so
one reducer group (one date) can hold both DBT and WS records.
"""
import sys
from weather_columns import parse_fields, get_field, IDX

for raw_line in sys.stdin:
    fields = parse_fields(raw_line)
    if fields is None:
        continue

    date = fields[IDX["YearMonthDay"]].strip()

    dry_bulb_temp = get_field(fields, "DryBulbTemp")
    if dry_bulb_temp is not None:
        print(f"{date}\tDBT,{dry_bulb_temp}")

    wind_speed = get_field(fields, "WindSpeed")
    if wind_speed is not None:
        print(f"{date}\tWS,{wind_speed}")
