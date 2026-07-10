"""
Shared column configuration for the NCDC "Weather_NDC_2007_04hourly"
dataset (hourly surface weather observations, April 2007).

This module is shipped to every mapper/reducer with Hadoop Streaming's
`-file weather_columns.py` option so that every job agrees on where each
weather variable lives in the comma-separated input line, and shares one
implementation of the "is this value missing?" and "is this the header
row?" logic instead of duplicating it five times.

IMPORTANT - before running anything on the cluster, run:
    head -1 Weather_NDC_2007_04hourly.txt
and compare it against COLUMN_NAMES below. NCDC hourly extracts are
occasionally exported with columns re-ordered or a subset of columns
missing; if yours differs, edit COLUMN_NAMES to match your file. Every
mapper/reducer in this coursework looks up columns by name through
IDX/get_field(), so a single edit here fixes all of them.
"""

# Column order for the NCDC/QCLCD-style hourly surface observation file.
COLUMN_NAMES = [
    "Wban", "YearMonthDay", "Time", "StationType",
    "SkyCondition", "SkyConditionFlag", "Visibility", "VisibilityFlag",
    "WeatherType", "WeatherTypeFlag",
    "DryBulbFarenheit", "DryBulbFarenheitFlag",
    "DryBulbCelsius", "DryBulbCelsiusFlag",
    "WetBulbFarenheit", "WetBulbFarenheitFlag",
    "WetBulbCelsius", "WetBulbCelsiusFlag",
    "DewPointFarenheit", "DewPointFarenheitFlag",
    "DewPointCelsius", "DewPointCelsiusFlag",
    "RelativeHumidity", "RelativeHumidityFlag",
    "WindSpeed", "WindSpeedFlag",
    "WindDirection", "WindDirectionFlag",
    "ValueForWindCharacter", "ValueForWindCharacterFlag",
    "StationPressure", "StationPressureFlag",
    "PressureTendency", "PressureTendencyFlag",
    "PressureChange", "PressureChangeFlag",
    "SeaLevelPressure", "SeaLevelPressureFlag",
    "RecordType", "RecordTypeFlag",
    "HourlyPrecip", "HourlyPrecipFlag",
    "Altimeter", "AltimeterFlag",
]

IDX = {name: position for position, name in enumerate(COLUMN_NAMES)}

# NCDC hourly extracts mark a missing reading with "M" (or leave it
# blank) rather than omitting the field, so both must be treated as
# "no value" instead of being parsed as data.
MISSING_MARKERS = {"", "M", "m", "MM", "-9999", "NA"}


def safe_float(value):
    """Convert one raw CSV field to float; return None if it is missing,
    blank, or not a valid number (e.g. a flag letter or header text)."""
    if value is None:
        return None
    value = value.strip()
    if value in MISSING_MARKERS:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def parse_fields(line):
    """Split one raw input line on commas and return the field list, or
    None if the line is a CSV header row or is too short to be a real
    data record (both cases should simply be skipped by the mapper)."""
    fields = line.strip().split(",")
    if len(fields) < len(COLUMN_NAMES):
        return None
    if fields[IDX["Wban"]].strip().lower() == "wban":
        return None  # header row (may reappear once per input split)
    return fields


def get_field(fields, name):
    """Look up a named column in an already-split row and convert it to
    float, or return None if it is missing/unparseable."""
    return safe_float(fields[IDX[name]])
