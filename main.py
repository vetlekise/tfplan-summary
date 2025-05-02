#!/usr/bin/env python3

import argparse
import os
import json
import sys

from typing import List, Dict
from rich.console import Console
from rich.table import Table


# https://rich.readthedocs.io/en/stable/appendix/colors.html
COLOR_MAP = {
    "create": "chartreuse3",
    "delete": "red1",
    "update": "yellow",
    "replace": "dark_orange",
    "no-op": "cyan",
    "default": "white"
}

def parse_args():
    """
    Parses command-line arguments provided when running the script.

    Returns:
        argparse.Namespace: An object containing the parsed arguments.
    """
    
    parser = argparse.ArgumentParser(
        description="Terraform Plan Summarizer",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter # add default values to help messages
        )
    parser.add_argument(
        "-p", "--path",
        required=True,
        help="Path to the Terraform plan JSON file"
    )
    parser.add_argument(
        "-c", "--color",
        action='store_true',
        help="Display output with colors"
    )
    parser.add_argument(
        "-s", "--statistics",
        action='store_true',
        help="Display only the statistics table (if neither -s nor -r is specified, both are shown)"
    )
    parser.add_argument(
        "-r", "--resources",
        action='store_true',
        help="Display only the resource changes table (if neither -s nor -r is specified, both are shown)"
    )
    return parser.parse_args()


def validate_file(file_path):
    """
    Validates if the provided file path points to a readable JSON file
    and loads its content.

    Args:
        file_path (str): The path to the file to validate.

    Returns:
        dict: The parsed JSON data from the file.

    Raises:
        SystemExit: If the file doesn't exist, isn't a JSON file,
                    or contains invalid JSON data. The script terminates.
    """
    
    allowed_ext = [".json"]
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext not in allowed_ext:
        sys.exit(f"ERROR: File '{file_path}' is not a JSON file")

    try:
        with open(file_path, 'r') as file:
            json_data = json.load(file)
        return json_data
    except OSError:
        sys.exit(f"ERROR: Could not read file: {file_path}")
    except json.JSONDecodeError:
        sys.exit(f"ERROR: Invalid JSON format in file '{file_path}'")


def get_effective_action(actions: List[str]) -> str:
    """
    Determines the single most significant action for a resource based on
    the list of actions provided by Terraform.

    Terraform plans might list multiple actions for a single resource (e.g.,
    ["delete", "create"] for a replacement). This function simplifies that
    list into a single representative action string (e.g., "replace").

    Args:
        actions (List[str]): A list of action strings from the Terraform plan
                             for a single resource (e.g., ["create"], ["update"],
                             ["delete", "create"]).

    Returns:
        str: The single, representative action string ("create", "delete",
             "update", "replace", "no-op", or "unknown").
    """
    
    action_set = set(actions)

    if "delete" in action_set and "create" in action_set:
        return "replace"
    elif "create" in action_set:
        return "create"
    elif "delete" in action_set:
        return "delete"
    elif "update" in action_set:
        return "update"
    elif "no-op" in action_set:
        return "no-op"
    else:
        return ",".join(sorted(actions)) if actions else "unknown"


def build_summary(resource_changes: List[dict]) -> Dict[str, List[str]]:
    """
    Processes the list of resource changes from the Terraform plan JSON
    and groups the resource addresses by their effective action.

    Args:
        resource_changes (List[dict]): A list of dictionaries, where each
                                       dictionary represents a resource change
                                       from the Terraform plan JSON. Expected keys
                                       include 'address' and 'change' (which
                                       contains 'actions').

    Returns:
        Dict[str, List[str]]: A dictionary where keys are the effective action
                              strings (e.g., "create", "delete") and values are
                              lists of resource addresses (e.g., "aws_instance.my_vm")
                              associated with that action.
                              Example: {"create": ["aws_s3_bucket.my_bucket"],
                                        "delete": ["aws_iam_user.old_user"]}
    """
    
    action_address_map = {}
    for resource in resource_changes:
        change_data = resource.get("change", {})
        actions = change_data.get("actions", []) if change_data else []
        address = resource.get("address", "unknown_address")

        effective_action = get_effective_action(actions)

        action_address_map.setdefault(effective_action, []).append(address)

    return action_address_map

def build_statistics_table(summary: Dict[str, List[str]], color: bool = False) -> Table:
    """
    Creates a 'rich' Table object summarizing the count of resources per action.

    Args:
        summary (Dict[str, List[str]]): The dictionary created by `build_summary`,
                                        mapping actions to lists of resource addresses.
        color (bool, optional): If True, applies colors to the table output
                                based on the COLOR_MAP. Defaults to False.

    Returns:
        Table: A `rich.table.Table` object ready to be printed to the console.
    """
    
    stats_table = Table(title="Action Statistics")
    stats_table.add_column("Action", style="white", no_wrap=True)
    stats_table.add_column("Count", style="white", justify="right")

    sorted_actions = sorted(summary.keys())
    total_resources = 0

    for action in sorted_actions:
        count = len(summary[action])
        if count == 0:
            continue
        total_resources += count

        action_str = action
        count_str = str(count)

        if color:
            action_color = COLOR_MAP.get(action, COLOR_MAP["default"])
            action_str = f"[{action_color}]{action}[/{action_color}]"
            count_str = f"[{action_color}]{count}[/{action_color}]"

        stats_table.add_row(action_str, count_str)

    if total_resources > 0:
        stats_table.add_section()
        total_str = "Total"
        total_count_str = str(total_resources)
        if color:
             total_str = f"[bold {COLOR_MAP['default']}]{total_str}[/]"
             total_count_str = f"[bold {COLOR_MAP['default']}]{total_count_str}[/]"
        stats_table.add_row(total_str, total_count_str)

    return stats_table


def build_changes_table(summary: Dict[str, List[str]], color: bool = False) -> Table:
    """
    Creates a 'rich' Table object listing the resource addresses for each action type,
    excluding "no-op" actions.

    Args:
        summary (Dict[str, List[str]]): The dictionary created by `build_summary`,
                                        mapping actions to lists of resource addresses.
        color (bool, optional): If True, applies colors to the table output
                                based on the COLOR_MAP. Defaults to False.

    Returns:
        Table: A `rich.table.Table` object ready to be printed to the console.
    """
    
    changes_table = Table(title="Resource Changes")
    changes_table.add_column("Action", style="white", no_wrap=True)
    changes_table.add_column("Addresses", style="white")

    sorted_actions = sorted(summary.keys())

    for action in sorted_actions:
        # Skip the 'no-op' action for the resource changes table
        if action == "no-op":
            continue

        addresses = summary[action]
        if not addresses: # Also skip actions with no addresses (though build_summary shouldn't produce these)
            continue

        action_str = action
        
        colored_addresses = sorted(addresses)

        if color:
            action_color = COLOR_MAP.get(action, COLOR_MAP["default"])
            action_str = f"[{action_color}]{action}[/{action_color}]"
            colored_addresses = [f"[{action_color}]{addr}[/{action_color}]" for addr in sorted(addresses)] # Apply color after sorting

        changes_table.add_row(action_str, "\n".join(colored_addresses))

    return changes_table


def main():
    """
    - Parses command-line arguments to get the path to the Terraform plan
    JSON file and display options (color, specific tables). 
    
    - Validates the input file, processes the JSON data to summarize resource changes,
    and prints formatted summary tables (statistics and/or resource changes)
    to the console using the 'rich' library based on the provided arguments.
    
    - If only resource changes are requested and none exist (excluding no-op),
    it prints a confirmation message.
    """
    
    args = parse_args()
    json_data = validate_file(args.path)
    resource_changes = json_data.get("resource_changes", [])

    action_summary = build_summary(resource_changes)
    console = Console()

    stats_flag = args.statistics     # True if user specified -s, False otherwise
    resources_flag = args.resources # True if user specified -r, False otherwise

    # If neither flag is specified, show both. Otherwise, show based on flags.
    explicitly_requested = stats_flag or resources_flag
    show_stats = stats_flag or not explicitly_requested
    show_resources = resources_flag or not explicitly_requested

    if show_resources:
        # Add a blank line between tables if both are shown
        if show_stats:
            console.print() 
        changes_table = build_changes_table(action_summary, color=args.color)
        # Only print the table if it has rows (i.e., if there were changes other than no-op)
        if changes_table.row_count > 0:
            console.print(changes_table)
        # If only resources were requested (-r) and there are no changes (excluding no-op)
        elif explicitly_requested and not show_stats:
            if args.color:
                console.print("[green]No changes.[/green] [white]Your infrastructure matches the configuration.[/white]")
            else:
                console.print("No changes. Your infrastructure matches the configuration.")
             
    # Print Statistics table if shown
    if show_stats:
        stats_table = build_statistics_table(action_summary, color=args.color)
        console.print(stats_table)

if __name__ == "__main__":
    main()
