#!/usr/bin/env python3
"""
Deliverable 3 - Reducer
Keys look like "<station>_DBT" or "<station>_WS". Because Hadoop sorts
mapper output by key before the shuffle, every reading for one station +
variable combination arrives at the reducer as one consecutive block, so
count/mean/variance/std/min/max can all be computed in a single
streaming pass with five running totals - the reducer never needs to
hold a station's full reading history in memory.

    variance = (1/N) * (sum(x^2) - N * mean^2)      [population variance,
                                                       per the coursework brief]
"""
import sys
import math


def new_accumulators():
    return {"n": 0, "sum": 0.0, "sumsq": 0.0, "min": None, "max": None}


def emit_result(key, acc):
    n = acc["n"]
    if n == 0:
        return
    mean = acc["sum"] / n
    variance = max((acc["sumsq"] / n) - mean ** 2, 0.0)
    std = math.sqrt(variance)
    print(f"{key}\tcount={n}\tmean={mean}\tvariance={variance}\t"
          f"std={std}\tmin={acc['min']}\tmax={acc['max']}")


current_key = None
acc = new_accumulators()

for raw_line in sys.stdin:
    line = raw_line.rstrip("\n")
    if not line:
        continue
    key, value = line.split("\t", 1)
    x = float(value)

    if key != current_key:
        if current_key is not None:
            emit_result(current_key, acc)
        current_key = key
        acc = new_accumulators()

    acc["n"] += 1
    acc["sum"] += x
    acc["sumsq"] += x ** 2
    acc["min"] = x if acc["min"] is None else min(acc["min"], x)
    acc["max"] = x if acc["max"] is None else max(acc["max"], x)

emit_result(current_key, acc)
