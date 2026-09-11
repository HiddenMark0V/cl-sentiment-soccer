"""Tests for the Sportschau JSON loader."""

import json
from pathlib import Path

import pandas as pd
import pytest

from src.load_data import load_data, parse_filename


def write_segments(path: Path, segments: list[dict[str, object]]) -> None:
    """Write test segments to a temporary JSON file."""
    path.write_text(json.dumps(segments), encoding="utf-8")


def test_parse_filename_with_numeric_prefix() -> None:
    assert parse_filename("47_NED_TUR_first_half.json") == ("NED_TUR", 1)


def test_parse_filename_without_numeric_prefix() -> None:
    assert parse_filename("NED_TUR_second_half.json") == ("NED_TUR", 2)


def test_parse_filename_rejects_invalid_name() -> None:
    with pytest.raises(ValueError):
        parse_filename("invalid.json")


def test_load_data_calculates_time_mid(tmp_path: Path) -> None:
    write_segments(
        tmp_path / "01_ABC_DEF_first_half.json",
        [{"start": 10.0, "end": 14.0, "text": "Example"}],
    )

    dataframe, issues = load_data(tmp_path)

    assert dataframe.loc[0, "time_mid"] == 12.0
    assert dataframe.loc[0, "time_continuous"] == 12.0
    assert issues.empty


def test_end_before_start_keeps_values_and_reports_issue(tmp_path: Path) -> None:
    write_segments(
        tmp_path / "01_ABC_DEF_first_half.json",
        [{"start": 14.0, "end": 10.0, "text": "Example"}],
    )

    dataframe, issues = load_data(tmp_path)

    assert dataframe.loc[0, "start"] == 14.0
    assert dataframe.loc[0, "end"] == 10.0
    assert pd.isna(dataframe.loc[0, "time_mid"])
    assert pd.isna(dataframe.loc[0, "time_continuous"])
    assert "end is smaller than start" in issues["issue"].tolist()


def test_missing_text_keeps_segment_and_reports_issue(tmp_path: Path) -> None:
    write_segments(
        tmp_path / "01_ABC_DEF_first_half.json",
        [{"start": 10.0, "end": 14.0}],
    )

    dataframe, issues = load_data(tmp_path)

    assert len(dataframe) == 1
    assert pd.isna(dataframe.loc[0, "text"])
    assert "missing key: text" in issues["issue"].tolist()


def test_second_half_uses_first_half_end_as_offset(tmp_path: Path) -> None:
    write_segments(
        tmp_path / "47_NED_TUR_first_half.json",
        [{"start": 2798.0, "end": 2800.0, "text": "First half"}],
    )
    write_segments(
        tmp_path / "47_NED_TUR_second_half.json",
        [{"start": 8.0, "end": 12.0, "text": "Second half"}],
    )

    dataframe, _ = load_data(tmp_path)
    second_half = dataframe.loc[dataframe["half"] == 2].iloc[0]

    assert second_half["time_mid"] == 10.0
    assert second_half["time_continuous"] == 2810.0


def test_second_half_uses_minimum_offset_of_2700(tmp_path: Path) -> None:
    write_segments(
        tmp_path / "47_NED_TUR_first_half.json",
        [{"start": 99.0, "end": 100.0, "text": "First half"}],
    )
    write_segments(
        tmp_path / "47_NED_TUR_second_half.json",
        [{"start": 8.0, "end": 12.0, "text": "Second half"}],
    )

    dataframe, _ = load_data(tmp_path)
    second_half = dataframe.loc[dataframe["half"] == 2].iloc[0]

    assert second_half["time_continuous"] == 2710.0


def test_second_half_uses_fallback_without_valid_first_half(tmp_path: Path) -> None:
    write_segments(
        tmp_path / "47_NED_TUR_second_half.json",
        [{"start": 8.0, "end": 12.0, "text": "Second half"}],
    )

    dataframe, _ = load_data(tmp_path)

    assert dataframe.loc[0, "time_continuous"] == 2710.0


def test_load_data_combines_files_and_sorts_reproducibly(tmp_path: Path) -> None:
    write_segments(
        tmp_path / "47_NED_TUR_second_half.json",
        [
            {"start": 20.0, "end": 22.0, "text": "Later"},
            {"start": 2.0, "end": 4.0, "text": "Earlier"},
        ],
    )
    write_segments(
        tmp_path / "47_NED_TUR_first_half.json",
        [{"start": 5.0, "end": 7.0, "text": "First half"}],
    )

    first_result, first_issues = load_data(tmp_path)
    second_result, second_issues = load_data(tmp_path)

    assert len(first_result) == 3
    assert first_result["match_id"].tolist() == ["NED_TUR"] * 3
    assert first_result["half"].tolist() == [1, 2, 2]
    assert first_result["file"].tolist() == [
        "47_NED_TUR_first_half.json",
        "47_NED_TUR_second_half.json",
        "47_NED_TUR_second_half.json",
    ]
    assert first_result["segment_id"].tolist() == [0, 1, 0]
    assert first_result["start"].tolist() == [5.0, 2.0, 20.0]
    assert first_result["time_continuous"].tolist() == [6.0, 2703.0, 2721.0]
    pd.testing.assert_frame_equal(first_result, second_result)
    pd.testing.assert_frame_equal(first_issues, second_issues)
