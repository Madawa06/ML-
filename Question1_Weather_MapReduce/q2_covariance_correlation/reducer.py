#!/usr/bin/env python3
"""
Deliverable 2 - Reducer
For each key ("DBT_vs_DewPoint" or "DBT_vs_RelativeHumidity") we keep
five running sums as the (x, y) pairs stream past:
    n, Sx = sum(x), Sy = sum(y), Sxx = sum(x^2), Syy = sum(y^2), Sxy = sum(x*y)

Those five numbers are all that is needed - no raw data has to be held
in memory - to compute, once the group is finished:

    mean_x = Sx / n ; mean_y = Sy / n
    covariance(x, y) = Sxy/n - mean_x * mean_y
    variance(x)      = Sxx/n - mean_x^2      (population variance)
    variance(y)       = Syy/n - mean_y^2
    correlation(x, y) = covariance(x, y) / (sqrt(variance(x)) * sqrt(variance(y)))

Correlation is bounded in [-1, 1]: values near +1/-1 indicate a strong
positive/negative linear relationship, and values near 0 indicate a
weak (or no) linear relationship - interpret the printed numbers using
this rule of thumb in the report.
"""
import sys
import math


def new_accumulators():
    return {"n": 0, "Sx": 0.0, "Sy": 0.0, "Sxx": 0.0, "Syy": 0.0, "Sxy": 0.0}


def emit_result(key, acc):
    n = acc["n"]
    if n == 0:
        return
    mean_x = acc["Sx"] / n
    mean_y = acc["Sy"] / n
    covariance = acc["Sxy"] / n - mean_x * mean_y
    variance_x = max(acc["Sxx"] / n - mean_x ** 2, 0.0)
    variance_y = max(acc["Syy"] / n - mean_y ** 2, 0.0)
    std_x, std_y = math.sqrt(variance_x), math.sqrt(variance_y)
    correlation = covariance / (std_x * std_y) if std_x > 0 and std_y > 0 else float("nan")
    print(f"{key}\tn={n}\tcovariance={covariance}\tcorrelation={correlation}")


current_key = None
acc = new_accumulators()

for raw_line in sys.stdin:
    line = raw_line.rstrip("\n")
    if not line:
        continue
    key, value = line.split("\t", 1)
    x_str, y_str = value.split(",", 1)
    x, y = float(x_str), float(y_str)

    if key != current_key:
        if current_key is not None:
            emit_result(current_key, acc)
        current_key = key
        acc = new_accumulators()

    acc["n"] += 1
    acc["Sx"] += x
    acc["Sy"] += y
    acc["Sxx"] += x ** 2
    acc["Syy"] += y ** 2
    acc["Sxy"] += x * y

emit_result(current_key, acc)
