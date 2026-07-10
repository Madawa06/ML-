# Question 1 — Distributed Weather Data Analysis and Predictive Modelling

**Dataset:** `Weather_NCDC_2007_04hourly` (NCDC hourly surface weather
observations, April 2007).

All five deliverables are implemented as classic **Hadoop Streaming**
mapper/reducer pairs: plain Python reading `sys.stdin` line by line and
writing `key\tvalue` to `sys.stdout`, exactly what `hadoop jar
hadoop-streaming.jar` expects. No pandas/numpy/scipy statistics or
regression routines are used anywhere — every mean, variance, covariance
and regression coefficient is built up from running sums (`sum`, `sum of
squares`, `count`, ...), which is what makes the computation genuinely
distributable across mappers/reducers.

## Files

```
weather_columns.py             shared column lookup + missing-value handling
q1_daily_stats/                Deliverable 1: daily Dry Bulb Temp + Wind Speed stats
q2_covariance_correlation/     Deliverable 2: covariance & correlation
q3_station_stats/               Deliverable 3: per-station summary stats
q4_simple_regression/           Deliverable 4: 1-variable regression + MSE
q5_multiple_regression/         Deliverable 5: 2-variable regression + MSE
sample_data/                    tiny synthetic CSV matching the dataset's columns
run_local_test.sh               runs all five jobs locally with Unix pipes
```

`weather_columns.py` is imported by every mapper/reducer, so it must be
shipped alongside them with Hadoop Streaming's `-file` option (see
commands below) or placed on `PYTHONPATH` for local testing.

## Dataset format

Before running on the cluster, check your actual file's header:

```bash
head -1 Weather_NCDC_2007_04hourly.txt
```

`weather_columns.py`'s `COLUMN_NAMES` list encodes the real 21-column
order confirmed from the dataset supplied for this coursework
(`WbanNumber, YearMonthDay, Time, ..., DryBulbTemp, DewPointTemp,
WetBulbTemp, RelativeHumidity, WindSpeed, ...`). If your copy differs,
edit that one list — every job looks columns up by name
(`get_field(fields, "DryBulbTemp")`), so a single edit fixes all five
deliverables. Missing readings (marked `M` or left blank) are
automatically skipped rather than crashing the job or being parsed as `0`.

## Deliverable 1 — Daily Dry Bulb Temp stats + daily Wind Speed stats

**Pseudocode**
```
Mapper:
  for each record:
    if valid DryBulbTemp: emit(date, ("DBT", temp))
    if valid WindSpeed:   emit(date, ("WS", speed))

Reducer (per date, values arrive sorted/grouped by Hadoop):
  accumulate n, sum, sum_of_squares, min, max for DBT
  accumulate n, sum, max for WS
  mean = sum / n
  variance = sum_of_squares/n - mean^2      (population variance)
  std = sqrt(variance)
  emit(date, DBT_min, DBT_max, DBT_mean, DBT_std, WindSpeed_avg, WindSpeed_max)
```
Code: `q1_daily_stats/mapper.py`, `q1_daily_stats/reducer.py`

## Deliverable 2 — Covariance & correlation

Chosen variables: **Dew Point Temp** and **Relative Humidity** against
Dry Bulb Temp (edit the two `get_field(...)` calls in the mapper to pick
different variables, e.g. `WetBulbTemp` or `WindSpeed`).

**Pseudocode**
```
Mapper:
  for each record with valid (DBT, DewPoint): emit("DBT_vs_DewPoint", (dbt, dew))
  for each record with valid (DBT, RH):       emit("DBT_vs_RH", (dbt, rh))

Reducer (per key):
  accumulate n, Sx, Sy, Sxx, Syy, Sxy
  mean_x = Sx/n ; mean_y = Sy/n
  covariance = Sxy/n - mean_x*mean_y
  variance_x = Sxx/n - mean_x^2 ; variance_y = Syy/n - mean_y^2
  correlation = covariance / (sqrt(variance_x) * sqrt(variance_y))
```
Code: `q2_covariance_correlation/mapper.py`, `.../reducer.py`

**Interpretation guide for the report:** correlation is in `[-1, 1]`.
`|r| > 0.7` = strong, `0.3–0.7` = moderate, `< 0.3` = weak; the sign
gives direction. Relative Humidity is typically strongly *negatively*
correlated with Dry Bulb Temp (warmer air holds relatively less
moisture at a fixed dew point), which the sample run below reproduces.

## Deliverable 3 — Station-level summary statistics

**Pseudocode**
```
Mapper:
  for each record:
    if valid DBT:  emit(station + "_DBT", temp)
    if valid WS:   emit(station + "_WS",  speed)

Reducer (per station+variable key):
  accumulate n, sum, sum_of_squares, min, max
  mean = sum/n ; variance = sum_of_squares/n - mean^2 ; std = sqrt(variance)
  emit(key, count, mean, variance, std, min, max)
```
Code: `q3_station_stats/mapper.py`, `.../reducer.py`

## Deliverable 4 — Simple linear regression (Dry Bulb Temp ~ Dew Point Temp)

Two MapReduce jobs, run in sequence: **stage 1** fits the model,
**stage 2** evaluates it (MSE needs the fitted slope/intercept as
input, so it cannot be computed in the same pass as the fit).

**Pseudocode**
```
Stage 1 mapper:  emit("constant_identifier", (x=DewPoint, y=DryBulbTemp))
Stage 1 reducer: accumulate n, Sx, Sy, Sxx, Sxy
                 slope     = (n*Sxy - Sx*Sy) / (n*Sxx - Sx^2)
                 intercept = (Sy - slope*Sx) / n

Stage 2 mapper:  y_hat = slope*x + intercept
                 emit("mse", (y - y_hat)^2)
Stage 2 reducer: MSE = average of all squared errors received
```
Code: `q4_simple_regression/{mapper_coeff,reducer_coeff,mapper_mse,reducer_mse}.py`

## Deliverable 5 — Two-variable regression (+ Relative Humidity)

Same two-stage pattern as Deliverable 4, but the model is
`DryBulbTemp = b0 + b1*DewPoint + b2*RelativeHumidity`.

**Pseudocode**
```
Stage 1 mapper:  emit("constant_identifier", (x1=DewPoint, x2=RH, y=DryBulbTemp))
Stage 1 reducer: accumulate n, Sx1, Sx2, Sy, Sx1x1, Sx2x2, Sx1x2, Sx1y, Sx2y
                 solve the 3x3 normal-equation system for (b0, b1, b2)
                 using Cramer's rule (hand-coded 3x3 determinants)

Stage 2 mapper:  y_hat = b0 + b1*x1 + b2*x2
                 emit("mse", (y - y_hat)^2)
Stage 2 reducer: MSE = average of all squared errors received
```
Code: `q5_multiple_regression/{mapper_coeff,reducer_coeff,mapper_mse,reducer_mse}.py`

**Why this is still "distributed":** the nine sums above are computed by
streaming every record through mappers and one reducer, exactly like the
one-variable case — that part scales to arbitrarily large input. Only
the final step (solving a fixed 3-unknown, 3-equation system from those
nine numbers) is done centrally, because it is O(1) work independent of
data size and has nothing left to parallelise.

**Compare the two models** by putting Deliverable 4's MSE next to
Deliverable 5's MSE in the report — a lower MSE for the two-variable
model shows Relative Humidity adds predictive power beyond Dew Point
Temp alone.

## Running locally (before using cluster time)

```bash
bash run_local_test.sh
```

This pipes the bundled synthetic sample (`sample_data/`) through every
mapper → `sort` (which reproduces Hadoop's shuffle/group-by-key step
locally) → reducer, for all five deliverables, and even extracts the
stage-1 regression coefficients automatically to feed into stage 2 — the
same two-stage pattern you'll use on the cluster. Swap in the real
dataset once you've confirmed the column order matches
`weather_columns.py`.

## Running on the Hadoop cluster

Upload the data first:
```bash
hdfs dfs -mkdir -p /user/$USER/weather
hdfs dfs -put Weather_NCDC_2007_04hourly.txt /user/$USER/weather/
```

**Deliverable 1:**
```bash
hadoop jar $HADOOP_STREAMING_JAR \
  -files q1_daily_stats/mapper.py,q1_daily_stats/reducer.py,weather_columns.py \
  -mapper mapper.py -reducer reducer.py \
  -input /user/$USER/weather/Weather_NCDC_2007_04hourly.txt \
  -output /user/$USER/weather/out_q1_daily_stats
hdfs dfs -cat /user/$USER/weather/out_q1_daily_stats/part-* | head
```
Deliverables 2 and 3 follow the identical pattern — just swap the
`-files`/`-mapper`/`-reducer` paths and `-output` directory for
`q2_covariance_correlation` / `q3_station_stats`.

**Deliverable 4 (two stages):**
```bash
# Stage 1: fit the model
hadoop jar $HADOOP_STREAMING_JAR \
  -files q4_simple_regression/mapper_coeff.py,q4_simple_regression/reducer_coeff.py,weather_columns.py \
  -mapper mapper_coeff.py -reducer reducer_coeff.py \
  -input /user/$USER/weather/Weather_NCDC_2007_04hourly.txt \
  -output /user/$USER/weather/out_q4_coeff
hdfs dfs -cat /user/$USER/weather/out_q4_coeff/part-*
# note the printed slope=... and intercept=... values, then:

# Stage 2: evaluate MSE using the coefficients from stage 1
hadoop jar $HADOOP_STREAMING_JAR \
  -files q4_simple_regression/mapper_mse.py,q4_simple_regression/reducer_mse.py,weather_columns.py \
  -mapper mapper_mse.py -reducer reducer_mse.py \
  -cmdenv SLOPE=<value from stage 1> -cmdenv INTERCEPT=<value from stage 1> \
  -input /user/$USER/weather/Weather_NCDC_2007_04hourly.txt \
  -output /user/$USER/weather/out_q4_mse
hdfs dfs -cat /user/$USER/weather/out_q4_mse/part-*
```

**Deliverable 5** follows the same two-stage pattern with
`q5_multiple_regression/*.py` and `-cmdenv B0=... -cmdenv B1=...
-cmdenv B2=...` for stage 2.

Take a screenshot of each `hadoop jar ...` run and the corresponding
`hdfs dfs -cat` output for the report's "evidence of Hadoop/HDFS
execution" requirement.

## Sample output (from `run_local_test.sh` on the bundled synthetic data)

```
=== Deliverable 1 ===
20070401  DBT_min=10.6  DBT_max=21.7  DBT_mean=15.75  DBT_std=4.07  WindSpeed_avg=10.33  WindSpeed_max=15.0
20070402  DBT_min=10.0  DBT_max=20.0  DBT_mean=15.56  DBT_std=3.39  WindSpeed_avg=10.4   WindSpeed_max=18.0

=== Deliverable 2 ===
DBT_vs_DewPoint          n=10  covariance=-0.70   correlation=-0.21
DBT_vs_RelativeHumidity  n=10  covariance=-50.71  correlation=-0.99

=== Deliverable 4 ===
slope=-0.96  intercept=21.74   ->  MSE=14.77

=== Deliverable 5 ===
intercept=32.60  coef_DewPoint=0.20  coef_RH=-0.30  ->  MSE=0.33
```
(Numbers are illustrative only — they come from the 11-row synthetic
sample, not the real April 2007 dataset, and exist purely to prove the
pipeline runs correctly end to end.)
