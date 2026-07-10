"""
Shared column configuration for the real "Weather_NCDC_2007_04hourly.txt"
dataset (hourly surface weather observations, April 2007), as supplied
in the DSM010 "Data Sets" folder.

This module is shipped to every mapper/reducer with Hadoop Streaming's
`-file weather_columns.py` option so that every job agrees on where each
weather variable lives in the comma-separated input line, and shares one
implementation of the "is this value missing?" and "is this the header
row?" logic instead of duplicating it five times.

Column order was read directly from the real file with:
    head -1 Weather_NCDC_2007_04hourly.txt
which printed:
    Wban Number, YearMonthDay, Time, Station Type, Maintenance Indicator,
    Sky Conditions, Visibility, Weather Type, Dry Bulb Temp, Dew Point
    Temp, Wet Bulb Temp, % Relative Humidity, Wind Speed (kt), Wind
    Direction, Wind Char. Gusts (kt), Val for Wind Char., Station
    Pressure, Pressure Tendency, Sea Level Pressure, Record Type,
    Precip. Total

COLUMN_NAMES below uses short Python-friendly identifiers for the same
21 columns, in the same left-to-right order - the identifiers do not
need to match the header text exactly, only the *position* matters,
since every mapper/reducer looks columns up by name through IDX/
get_field() rather than by re-parsing the header at run time.
"""

# Column order for Weather_NCDC_2007_04hourly.txt (21 columns).
COLUMN_NAMES = [
    "WbanNumber",           # 0  station id, e.g. "14732"
    "YearMonthDay",         # 1  e.g. "20070401"
    "Time",                 # 2  e.g. "0053"
    "StationType",          # 3
    "MaintenanceIndicator", # 4
    "SkyConditions",        # 5
    "Visibility",           # 6
    "WeatherType",          # 7
    "DryBulbTemp",          # 8
    "DewPointTemp",         # 9
    "WetBulbTemp",          # 10
    "RelativeHumidity",     # 11
    "WindSpeed",            # 12
    "WindDirection",        # 13
    "WindCharGusts",        # 14
    "ValForWindChar",       # 15
    "StationPressure",      # 16
    "PressureTendency",     # 17
    "SeaLevelPressure",     # 18
    "RecordType",           # 19
    "PrecipTotal",          # 20
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
    None if the line is the CSV header row or is too short to be a real
    data record (both cases should simply be skipped by the mapper)."""
    fields = line.strip().split(",")
    if len(fields) < len(COLUMN_NAMES):
        return None
    # The header row's first field reads "Wban Number" (text) instead of
    # a numeric station id - skip it instead of trying to parse it.
    if fields[IDX["WbanNumber"]].strip().lower().startswith("wban"):
        return None
    return fields


def get_field(fields, name):
    """Look up a named column in an already-split row and convert it to
    float, or return None if it is missing/unparseable."""
    return safe_float(fields[IDX[name]])
