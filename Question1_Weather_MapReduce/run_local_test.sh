#!/usr/bin/env bash
# Local smoke test for all five Question 1 MapReduce jobs.
#
# This does NOT touch Hadoop - it simulates the shuffle-and-sort phase
# with plain Unix pipes (`sort` groups by key exactly like Hadoop does),
# so you can confirm every mapper/reducer pair works before spending
# cluster time on it. Run it from this directory:
#     bash run_local_test.sh
#
# It uses the tiny synthetic file in sample_data/ - swap DATA for your
# real Weather_NDC_2007_04hourly file once you have verified its column
# order matches weather_columns.py.

set -euo pipefail
cd "$(dirname "$0")"

# weather_columns.py lives in this directory; make it importable from
# every subdirectory's mapper/reducer scripts, same as `-file
# weather_columns.py` does on the real Hadoop cluster (see README.md).
export PYTHONPATH="$(pwd):${PYTHONPATH:-}"

DATA="sample_data/sample_weather_ndc_2007_04hourly.csv"

echo "=== Deliverable 1: daily Dry Bulb Temp / Wind Speed stats ==="
python3 q1_daily_stats/mapper.py < "$DATA" \
    | sort -k1,1 \
    | python3 q1_daily_stats/reducer.py
echo

echo "=== Deliverable 2: covariance & correlation ==="
python3 q2_covariance_correlation/mapper.py < "$DATA" \
    | sort -k1,1 \
    | python3 q2_covariance_correlation/reducer.py
echo

echo "=== Deliverable 3: station-level summary stats ==="
python3 q3_station_stats/mapper.py < "$DATA" \
    | sort -k1,1 \
    | python3 q3_station_stats/reducer.py
echo

echo "=== Deliverable 4: simple linear regression (DryBulb ~ DewPoint) ==="
COEFF_LINE=$(python3 q4_simple_regression/mapper_coeff.py < "$DATA" \
    | sort -k1,1 \
    | python3 q4_simple_regression/reducer_coeff.py)
echo "$COEFF_LINE"
SLOPE=$(echo "$COEFF_LINE" | grep -oP 'slope=\K[-0-9.eE]+')
INTERCEPT=$(echo "$COEFF_LINE" | grep -oP 'intercept=\K[-0-9.eE]+')
echo "Using SLOPE=$SLOPE INTERCEPT=$INTERCEPT for stage 2..."
SLOPE="$SLOPE" INTERCEPT="$INTERCEPT" python3 q4_simple_regression/mapper_mse.py < "$DATA" \
    | sort -k1,1 \
    | python3 q4_simple_regression/reducer_mse.py
echo

echo "=== Deliverable 5: two-variable regression (DryBulb ~ DewPoint + RH) ==="
COEFF_LINE=$(python3 q5_multiple_regression/mapper_coeff.py < "$DATA" \
    | sort -k1,1 \
    | python3 q5_multiple_regression/reducer_coeff.py)
echo "$COEFF_LINE"
B0=$(echo "$COEFF_LINE" | grep -oP 'intercept=\K[-0-9.eE]+')
B1=$(echo "$COEFF_LINE" | grep -oP 'coef_DewPointCelsius=\K[-0-9.eE]+')
B2=$(echo "$COEFF_LINE" | grep -oP 'coef_RelativeHumidity=\K[-0-9.eE]+')
echo "Using B0=$B0 B1=$B1 B2=$B2 for stage 2..."
B0="$B0" B1="$B1" B2="$B2" python3 q5_multiple_regression/mapper_mse.py < "$DATA" \
    | sort -k1,1 \
    | python3 q5_multiple_regression/reducer_mse.py
