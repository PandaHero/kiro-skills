#!/usr/bin/env python3
"""Recommend the next executable task from a spec directory or tasks.md file."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from spec_runtime import choose_next_task, load_meta, load_tasks, save_meta, sync_execution_state


def resolve_spec_dir(path_str: str) -> Path:
    path = Path(path_str)
    if path.name == "tasks.md":
        return path.parent
    return path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print the next pending task from a spec directory or tasks.md file."
    )
    parser.add_argument("path", help="Path to spec directory or tasks.md")
    args = parser.parse_args()

    spec_dir = resolve_spec_dir(args.path)
    if not spec_dir.exists():
        print(f"missing path: {spec_dir}")
        return 1

    meta = load_meta(spec_dir)
    items = load_tasks(spec_dir, meta)
    if not items:
        print("No tasks found.")
        return 1

    sync_execution_state(meta, items)
    save_meta(spec_dir, meta)

    next_item = choose_next_task(items, meta["execution"].get("current_task"))
    if not next_item:
        print("No pending tasks found.")
        return 1

    print(f"Next task: {next_item['num']} {next_item['desc']}")
    details = [line.strip() for line in next_item["details"] if line.strip()]
    for line in details:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
