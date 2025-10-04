import json
import sys
from pathlib import Path

import pytest
from pytest import MonkeyPatch
from rich.table import Table

from tfplan_summary.main import (
    build_changes_table,
    build_statistics_table,
    build_summary,
    get_effective_action,
    parse_args,
    validate_file,
)


# Add the 'MonkeyPatch' type hint
def test_parse_args_flags(monkeypatch: MonkeyPatch):
    """Verifies argument parsing with all command-line flags enabled.

    Args:
        monkeypatch: The pytest fixture for modifying or patching modules.
    """
    test_path = "plan_with_flags.json"
    monkeypatch.setattr(
        sys,
        "argv",
        ["script_name", "--path", test_path, "--color", "--statistics", "--resources"],
    )
    args = parse_args()
    assert args.path == test_path
    assert args.color
    assert args.statistics
    assert args.resources


# Add the 'Path' type hint
def test_validate_file_valid_json(tmp_path: Path):
    """Ensures a valid JSON file is read and parsed correctly.

    Args:
        tmp_path: The pytest fixture for creating temporary files and directories.
    """
    file_path = tmp_path / "valid.json"
    data = {"status": "ok", "resource_changes": []}
    file_path.write_text(json.dumps(data))
    result = validate_file(str(file_path))
    assert result == data


# Add the 'Path' type hint
def test_validate_file_invalid_json(tmp_path: Path):
    """Verifies that a file with invalid JSON content raises SystemExit.

    Args:
        tmp_path: The pytest fixture for creating temporary files and directories.
    """
    file_path = tmp_path / "invalid.json"
    file_path.write_text("{")
    with pytest.raises(SystemExit) as excinfo:
        validate_file(str(file_path))
    assert "Invalid JSON format" in str(excinfo.value)


def test_validate_file_not_found():
    """Verifies that a non-existent file path raises SystemExit."""
    non_existent_path = "no_such_file_here.json"
    with pytest.raises(SystemExit) as excinfo:
        validate_file(non_existent_path)
    assert "Could not read file" in str(excinfo.value)
    assert non_existent_path in str(excinfo.value)


def test_get_effective_action():
    """Checks that the correct effective action is derived from a list of actions."""
    test_cases = [
        (["create"], "create"),
        (["delete"], "delete"),
        (["update"], "update"),
        (["delete", "create"], "replace"),
        (["create", "delete"], "replace"),
        (["no-op"], "no-op"),
        (["read"], "read"),
        ([], "unknown"),
        (["invalid-action"], "invalid-action"),
    ]
    for actions, expected in test_cases:
        assert get_effective_action(actions) == expected


def test_build_summary():
    """Ensures the summary dictionary is built correctly from resource changes."""
    resource_changes = [
        {"address": "resource.a", "change": {"actions": ["create"]}},
        {"address": "resource.b", "change": {"actions": ["delete"]}},
        {"address": "resource.c", "change": {"actions": ["create", "delete"]}},
        {"address": "resource.d", "change": {"actions": ["update"]}},
        {"address": "resource.e"},
    ]

    expected_summary = {
        "create": ["resource.a"],
        "delete": ["resource.b"],
        "replace": ["resource.c"],
        "update": ["resource.d"],
        "unknown": ["resource.e"],
    }

    summary = build_summary(resource_changes)

    for key in summary:
        summary[key].sort()
    for key in expected_summary:
        expected_summary[key].sort()

    assert summary == expected_summary


def test_build_statistics_table_runs():
    """Verifies the statistics table builds without errors for valid data."""
    summary = {"create": ["resource.a"], "delete": ["resource.b", "resource.c"]}
    try:
        table = build_statistics_table(summary, color=False)
        assert isinstance(table, Table)
    except Exception as e:
        pytest.fail(f"build_statistics_table raised an exception: {e}")


def test_build_changes_table_runs():
    """Verifies the resource changes table builds without errors for valid data."""
    summary = {"create": ["resource.a"], "delete": ["resource.b", "resource.c"]}
    try:
        table = build_changes_table(summary, color=True)
        assert isinstance(table, Table)
    except Exception as e:
        pytest.fail(f"build_changes_table raised an exception: {e}")
