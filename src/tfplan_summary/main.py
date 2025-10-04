#!/usr/bin/env python3

import argparse
import json
import sys
from typing import Any, cast

from rich.console import Console
from rich.table import Table

# https://rich.readthedocs.io/en/stable/appendix/colors.html
COLOR_MAP = {
    "create": "chartreuse3",
    "delete": "red1",
    "update": "yellow",
    "replace": "dark_orange",
    "no-op": "cyan",
    "default": "white",
}


def parse_args() -> argparse.Namespace:
    """Parses command-line arguments provided when running the script.

    Returns:
        An object containing the parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Terraform Plan Summarizer",
        # Add default values to help messages
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-p", "--path", required=True, help="Path to the Terraform plan JSON file")
    parser.add_argument("-c", "--color", action="store_true", help="Display output with colors")
    parser.add_argument(
        "-s",
        "--statistics",
        action="store_true",
        help="Display only the statistics table (if neither -s nor -r is specified, both are shown)",
    )
    parser.add_argument(
        "-r",
        "--resources",
        action="store_true",
        help="Display only the resource changes table (if neither -s nor -r is specified, both are shown)",
    )
    return parser.parse_args()


def validate_file(file_path: str) -> dict[str, Any]:
    """Validates and loads the content of a JSON file.

    Args:
        file_path: The path to the file to validate.

    Returns:
        The parsed JSON data from the file.

    Raises:
        SystemExit: If the file is invalid or cannot be read.
    """
    if not file_path.lower().endswith(".json"):
        sys.exit(f"ERROR: File '{file_path}' is not a JSON file")

    try:
        with open(file_path) as file:
            # FIX: Use `cast` to satisfy mypy's strict checking for `json.load()`
            json_data = cast(dict[str, Any], json.load(file))
        return json_data
    except OSError:
        sys.exit(f"ERROR: Could not read file: {file_path}")
    except json.JSONDecodeError:
        sys.exit(f"ERROR: Invalid JSON format in file '{file_path}'")


def get_effective_action(actions: list[str]) -> str:
    """Determines the single most significant action for a resource.

    Args:
        actions: A list of action strings from a Terraform plan.

    Returns:
        The single, representative action string.
    """
    action_set = set(actions)
    if "delete" in action_set and "create" in action_set:
        return "replace"
    if "create" in action_set:
        return "create"
    if "delete" in action_set:
        return "delete"
    if "update" in action_set:
        return "update"
    if "no-op" in action_set:
        return "no-op"

    return ",".join(sorted(actions)) if actions else "unknown"


def build_summary(resource_changes: list[dict[str, Any]]) -> dict[str, list[str]]:
    """Groups resource addresses by their effective action.

    Args:
        resource_changes: A list of resource change dictionaries from the plan.

    Returns:
        A dictionary mapping actions to lists of resource addresses.
    """
    action_address_map: dict[str, list[str]] = {}
    for resource in resource_changes:
        change_data = resource.get("change", {})
        actions = change_data.get("actions", []) if change_data else []
        address = resource.get("address", "unknown_address")
        effective_action = get_effective_action(actions)
        action_address_map.setdefault(effective_action, []).append(address)
    return action_address_map


def build_statistics_table(summary: dict[str, list[str]], color: bool = False) -> Table:
    """Creates a rich Table summarizing the count of resources per action.

    Args:
        summary: The dictionary mapping actions to resource addresses.
        color: If True, applies colors to the table output.

    Returns:
        A rich Table object ready for printing.
    """
    stats_table = Table(title="Action Statistics")
    stats_table.add_column("Action", style="white", no_wrap=True)
    stats_table.add_column("Count", style="white", justify="right")

    total_resources = 0
    for action in sorted(summary.keys()):
        count = len(summary[action])
        if count == 0:
            continue
        total_resources += count
        action_str, count_str = action, str(count)
        if color:
            action_color = COLOR_MAP.get(action, COLOR_MAP["default"])
            action_str = f"[{action_color}]{action}[/{action_color}]"
            count_str = f"[{action_color}]{count}[/{action_color}]"
        stats_table.add_row(action_str, count_str)

    if total_resources > 0:
        stats_table.add_section()
        total_str, total_count_str = "Total", str(total_resources)
        if color:
            total_str = f"[bold {COLOR_MAP['default']}]{total_str}[/]"
            total_count_str = f"[bold {COLOR_MAP['default']}]{total_count_str}[/]"
        stats_table.add_row(total_str, total_count_str)
    return stats_table


def build_changes_table(summary: dict[str, list[str]], color: bool = False) -> Table:
    """Creates a rich Table listing the resource addresses for each action.

    Args:
        summary: The dictionary mapping actions to resource addresses.
        color: If True, applies colors to the table output.

    Returns:
        A rich Table object ready for printing.
    """
    changes_table = Table(title="Resource Changes")
    changes_table.add_column("Action", style="white", no_wrap=True)
    changes_table.add_column("Addresses", style="white")

    for action in sorted(summary.keys()):
        if action == "no-op" or not summary[action]:
            continue

        action_str = action
        sorted_addresses = sorted(summary[action])
        addresses_str = "\n".join(sorted_addresses)

        if color:
            action_color = COLOR_MAP.get(action, COLOR_MAP["default"])
            action_str = f"[{action_color}]{action}[/{action_color}]"
            addresses_str = "\n".join(f"[{action_color}]{addr}[/{action_color}]" for addr in sorted_addresses)

        changes_table.add_row(action_str, addresses_str)
    return changes_table


def run() -> None:
    """Main execution function for the script."""
    args = parse_args()
    json_data = validate_file(args.path)

    resource_changes = cast(list[dict[str, Any]], json_data.get("resource_changes", []))

    action_summary = build_summary(resource_changes)
    console = Console()

    show_all = not (args.statistics or args.resources)
    show_stats = args.statistics or show_all
    show_resources = args.resources or show_all

    if show_stats:
        stats_table = build_statistics_table(action_summary, color=args.color)
        console.print(stats_table)

    if show_resources:
        changes_table = build_changes_table(action_summary, color=args.color)
        if changes_table.row_count > 0:
            if show_stats:  # Add a blank line between tables if both are shown
                console.print()
            console.print(changes_table)
        elif not show_stats:  # Only show "No changes" if resources was the only table requested
            console.print("[green]No changes.[/green] Your infrastructure matches the configuration.")


if __name__ == "__main__":
    run()
