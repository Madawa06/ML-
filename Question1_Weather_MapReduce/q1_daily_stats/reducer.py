#!/usr/bin/env python3
"""
Deliverable 1 - Reducer
Combines the per-record (date, tag, value) triples emitted by the mapper
into one summary row per calendar day.

Hadoop Streaming sorts mapper output by key before it reaches the
reducer, so every value for the same date arrives as one consecutive
block - this lets us keep a running total for "the day we are currently
on" and flush it the instant the date changes, without ever holding the
whole month in memory.

PSEUDOCODE
----------
current_date <- None
reset accumulators
for each (date, tag, number) in sorted input:
    if date != current_date and current_date is not None:
        emit_summary(current_date, accumulators)
        reset accumulators
    current_date <- date
    if tag == "DBT":
        n_dbt += 1 ; sum_dbt += number ; sumsq_dbt += number^2
        min_dbt <- min(min_dbt, number) ; max_dbt <- max(max_dbt, number)
    if tag == "WS":
        n_ws += 1 ; sum_ws += number
        max_ws <- max(max_ws, number)
emit_summary(current_date, accumulators)     # flush the final day

Per the coursework's Statistical Computation Guide, population variance
is used throughout:
    variance = (1/N) * (sum(x^2) - N * mean^2)
"""
import sys
import math


def new_accumulators():
    return {
        "n_dbt": 0, "sum_dbt": 0.0, "sumsq_dbt": 0.0,
        "min_dbt": None, "max_dbt": None,
        "n_ws": 0, "sum_ws": 0.0, "max_ws": None,
    }


def emit_summary(date, acc):
    if acc["n_dbt"] == 0 and acc["n_ws"] == 0:
        return  # no valid readings were seen for this date

    if acc["n_dbt"] > 0:
        mean_dbt = acc["sum_dbt"] / acc["n_dbt"]
        variance_dbt = (acc["sumsq_dbt"] / acc["n_dbt"]) - mean_dbt ** 2
        variance_dbt = max(variance_dbt, 0.0)  # guard tiny fp rounding noise
        std_dbt = math.sqrt(variance_dbt)
        dbt_min, dbt_max = acc["min_dbt"], acc["max_dbt"]
    else:
        mean_dbt = std_dbt = dbt_min = dbt_max = None

    avg_ws = acc["sum_ws"] / acc["n_ws"] if acc["n_ws"] > 0 else None
    max_ws = acc["max_ws"]

    print(f"{date}\t"
          f"DBT_min={dbt_min}\tDBT_max={dbt_max}\t"
          f"DBT_mean={mean_dbt}\tDBT_std={std_dbt}\t"
          f"WindSpeed_avg={avg_ws}\tWindSpeed_max={max_ws}")


current_date = None
acc = new_accumulators()

for raw_line in sys.stdin:
    line = raw_line.rstrip("\n")
    if not line:
        continue
    date, value = line.split("\t", 1)
    tag, number_str = value.split(",", 1)
    number = float(number_str)

    if date != current_date:
        if current_date is not None:
            emit_summary(current_date, acc)
        current_date = date
        acc = new_accumulators()

    if tag == "DBT":
        acc["n_dbt"] += 1
        acc["sum_dbt"] += number
        acc["sumsq_dbt"] += number ** 2
        acc["min_dbt"] = number if acc["min_dbt"] is None else min(acc["min_dbt"], number)
        acc["max_dbt"] = number if acc["max_dbt"] is None else max(acc["max_dbt"], number)
    elif tag == "WS":
        acc["n_ws"] += 1
        acc["sum_ws"] += number
        acc["max_ws"] = number if acc["max_ws"] is None else max(acc["max_ws"], number)

# flush the accumulators for the very last date group
emit_summary(current_date, acc)
