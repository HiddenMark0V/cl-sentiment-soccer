"""Load Sportschau transcript segments into pandas DataFrames."""

from __future__ import annotations

import json
import math
import re
from numbers import Real
from pathlib import Path

import pandas as pd


DATA_COLUMNS = [
    "match_id",
    "half",
    "file",
    "segment_id",
    "start",
    "end",
    "time_mid",
    "time_continuous",
    "text",
]
ISSUE_COLUMNS = ["file", "segment_id", "issue"]
FILENAME_PATTERN = re.compile(
    r"^(?:\d+_)?(?P<match_id>[A-Z]{3}_[A-Z]{3})_"
    r"(?P<half>first|second)_half\.json$",
    re.IGNORECASE,
)


def parse_filename(filename: str | Path) -> tuple[str, int]:
    """Return the match identifier and half encoded in a JSON filename."""
    name = Path(filename).name
    match = FILENAME_PATTERN.fullmatch(name)
    if match is None:
        raise ValueError(
            f"Invalid Sportschau filename {name!r}. Expected, for example, "
            "'47_NED_TUR_first_half.json' or 'NED_TUR_second_half.json'."
        )

    match_id = match.group("match_id").upper()
    half = 1 if match.group("half").lower() == "first" else 2
    return match_id, half


def _is_valid_time(value: object) -> bool:
    """Return whether a value is a finite number, explicitly excluding bool."""
    return isinstance(value, Real) and not isinstance(value, bool) and math.isfinite(value)


def _is_valid_interval(start: object, end: object) -> bool:
    """Return whether start and end form a finite, non-negative interval."""
    return (
        _is_valid_time(start)
        and _is_valid_time(end)
        and start >= 0
        and end >= start
    )


def _add_issue(
    issues: list[dict[str, object]],
    file: str,
    segment_id: int,
    issue: str,
) -> None:
    """Append one validation issue in the common output format."""
    issues.append({"file": file, "segment_id": segment_id, "issue": issue})


def _validate_segment(
    segment: object,
    file: str,
    segment_id: int,
    issues: list[dict[str, object]],
) -> tuple[object, object, object]:
    """Extract a segment's values while recording validation problems."""
    if not isinstance(segment, dict):
        _add_issue(issues, file, segment_id, "segment is not a JSON object")
        for key in ("start", "end", "text"):
            _add_issue(issues, file, segment_id, f"missing key: {key}")
        return None, None, None

    values: dict[str, object] = {}
    for key in ("start", "end", "text"):
        if key not in segment:
            _add_issue(issues, file, segment_id, f"missing key: {key}")
            values[key] = None
        else:
            values[key] = segment[key]
            if segment[key] is None:
                _add_issue(issues, file, segment_id, f"missing value: {key}")

    start, end, text = values["start"], values["end"], values["text"]

    for key, value in (("start", start), ("end", end)):
        if value is None:
            continue
        if not isinstance(value, Real) or isinstance(value, bool):
            _add_issue(issues, file, segment_id, f"non-numeric time: {key}")
        elif not math.isfinite(value):
            _add_issue(issues, file, segment_id, f"non-finite time: {key}")
        elif value < 0:
            _add_issue(issues, file, segment_id, f"negative time: {key}")

    if _is_valid_time(start) and _is_valid_time(end) and end < start:
        _add_issue(issues, file, segment_id, "end is smaller than start")

    if isinstance(text, str):
        if not text.strip():
            _add_issue(issues, file, segment_id, "empty text")
    elif text is not None:
        _add_issue(issues, file, segment_id, "text is not a string")

    return start, end, text


def _add_continuous_time(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Add a reproducible transcript timeline across both halves."""
    first_half_end_max: dict[str, float] = {}
    for row in dataframe.itertuples(index=False):
        if row.half == 1 and _is_valid_interval(row.start, row.end):
            current_max = first_half_end_max.get(row.match_id)
            if current_max is None or row.end > current_max:
                first_half_end_max[row.match_id] = float(row.end)

    continuous_times: list[float | None] = []
    for row in dataframe.itertuples(index=False):
        if pd.isna(row.time_mid):
            continuous_times.append(None)
        elif row.half == 1:
            continuous_times.append(row.time_mid)
        else:
            offset = max(2700.0, first_half_end_max.get(row.match_id, 2700.0))
            continuous_times.append(row.time_mid + offset)

    # This is a continuous transcript timeline, not an exact official match clock.
    dataframe["time_continuous"] = continuous_times
    return dataframe


def _build_data_frame(records: list[dict[str, object]]) -> pd.DataFrame:
    """Build and stably sort the data frame without changing source values."""
    dataframe = pd.DataFrame.from_records(records, columns=DATA_COLUMNS)
    if dataframe.empty:
        return dataframe

    # Reassign as object columns so pandas does not coerce integer source values
    # to floats merely because another segment contains a missing value.
    for column in ("start", "end", "text"):
        dataframe[column] = pd.Series(
            [record[column] for record in records], dtype="object"
        )

    # Invalid times remain in the result and sort after valid numeric times.
    dataframe["_start_invalid"] = [
        not _is_valid_time(value) for value in dataframe["start"]
    ]
    dataframe["_start_sort"] = [
        float(value) if _is_valid_time(value) else 0.0
        for value in dataframe["start"]
    ]
    dataframe["_end_invalid"] = [
        not _is_valid_time(value) for value in dataframe["end"]
    ]
    dataframe["_end_sort"] = [
        float(value) if _is_valid_time(value) else 0.0
        for value in dataframe["end"]
    ]

    dataframe = dataframe.sort_values(
        by=[
            "match_id",
            "half",
            "_start_invalid",
            "_start_sort",
            "_end_invalid",
            "_end_sort",
            "segment_id",
        ],
        kind="stable",
    )
    dataframe = dataframe.drop(
        columns=["_start_invalid", "_start_sort", "_end_invalid", "_end_sort"]
    ).reset_index(drop=True)
    return _add_continuous_time(dataframe)


def load_data(
    input_dir: str | Path,
    output_csv: str | Path | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load all JSON files in a directory and return data and issue frames."""
    directory = Path(input_dir)
    if not directory.is_dir():
        raise NotADirectoryError(f"Input directory does not exist: {directory}")

    paths = sorted(directory.glob("*.json"), key=lambda path: path.name.casefold())
    records: list[dict[str, object]] = []
    issues: list[dict[str, object]] = []

    for path in paths:
        match_id, half = parse_filename(path.name)
        try:
            with path.open("r", encoding="utf-8") as handle:
                segments = json.load(handle)
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise ValueError(f"Could not read valid JSON from {path}: {error}") from error

        if not isinstance(segments, list):
            raise ValueError(f"Expected a list of segments in {path}")

        for segment_id, segment in enumerate(segments):
            start, end, text = _validate_segment(
                segment, path.name, segment_id, issues
            )
            time_mid = (
                (start + end) / 2
                if _is_valid_interval(start, end)
                else None
            )
            records.append(
                {
                    "match_id": match_id,
                    "half": half,
                    "file": path.name,
                    "segment_id": segment_id,
                    "start": start,
                    "end": end,
                    # Source times and time_mid remain half-relative seconds.
                    "time_mid": time_mid,
                    "time_continuous": None,
                    "text": text,
                }
            )

    dataframe = _build_data_frame(records)
    issues_dataframe = pd.DataFrame.from_records(issues, columns=ISSUE_COLUMNS)

    if output_csv is not None:
        output_path = Path(output_csv)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        dataframe.to_csv(output_path, index=False)

    return dataframe, issues_dataframe
