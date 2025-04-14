import pytest
import json
import sys
from argparse import Namespace
from rich.table import Table


from main import (
    parse_args,
    validate_file,
    get_effective_action,
    build_summary,
    build_statistics_table,
    build_changes_table,
)


def test_parse_args_flags(monkeypatch):
    """Test parsing with flags enabled."""
    test_path = "plan_with_flags.json"
    monkeypatch.setattr(sys, 'argv', ['script_name', '--path', test_path, '--color', '--statistics', '--resources'])
    args = parse_args()
    assert args.path == test_path
    assert args.color
    assert args.statistics
    assert args.resources


def test_validate_file_valid_json(tmp_path):
    """Test reading a valid JSON file."""
    file_path = tmp_path / "valid.json"
    data = {"status": "ok", "resource_changes": []}
    file_path.write_text(json.dumps(data))
    result = validate_file(str(file_path))
    assert result == data


def test_validate_file_invalid_json(tmp_path):
    """Test reading a file with invalid JSON, expecting SystemExit."""
    file_path = tmp_path / "invalid.json"
    file_path.write_text("{")
    with pytest.raises(SystemExit) as excinfo:
        validate_file(str(file_path))
    # Check that the error message indicates invalid JSON
    assert "Invalid JSON format" in str(excinfo.value)


def test_validate_file_not_found():
    """Test reading a non-existent file, expecting SystemExit."""
    non_existent_path = "no_such_file_here.json"
    with pytest.raises(SystemExit) as excinfo:
        validate_file(non_existent_path)
    # Adjust assertion to match the actual error message from the traceback
    assert "Could not read file" in str(excinfo.value)
    assert non_existent_path in str(excinfo.value)


def test_get_effective_action():
    """Test calculating the effective action from a list of actions."""
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
    """Test building the summary dictionary from resource changes."""
    # Using the same input as before
    resource_changes = [
        {"address": "resource.a", "change": {"actions": ["create"]}},
        {"address": "resource.b", "change": {"actions": ["delete"]}},
        {"address": "resource.c", "change": {"actions": ["create", "delete"]}}, # replace
        {"address": "resource.d", "change": {"actions": ["update"]}},
        {"address": "resource.e"}, # Missing 'change' -> unknown
    ]
    
    # expected return value of build_summary
    expected_summary = {
        'create': ['resource.a'],
        'delete': ['resource.b'],
        'replace': ['resource.c'],
        'update': ['resource.d'],
        'unknown': ['resource.e'],
    }

    summary = build_summary(resource_changes)

    # sort summaries for consistency
    for key in summary:
        summary[key].sort()
    for key in expected_summary:
        expected_summary[key].sort()

    assert summary == expected_summary


def test_build_statistics_table_runs():
    """Check if statistics table builds without errors."""
    summary = {'create': ['resource.a'], 'delete': ['resource.b', 'resource.c']}
    try:
        table = build_statistics_table(summary, color=False)
        assert isinstance(table, Table) # Check if it returns a Table instance/object of Rich
    except Exception as e:
        pytest.fail(f"build_statistics_table raised an exception: {e}")

def test_build_changes_table_runs():
    """Check if changes table builds without errors."""
    summary = {'create': ['resource.a'], 'delete': ['resource.b', 'resource.c']}
    try:
        table = build_changes_table(summary, color=True)
        assert isinstance(table, Table) # Check if it returns a Table instance/object of Rich
    except Exception as e:
        pytest.fail(f"build_changes_table raised an exception: {e}")