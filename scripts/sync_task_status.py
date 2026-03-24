#!/usr/bin/env python3
"""Sync task execution state with tasks.md and optionally set the active task."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from spec_runtime import (
    append_history,
    choose_next_task,
    find_task,
    load_meta,
    load_tasks,
    save_meta,
    sync_execution_state,
    task_children,
)


def resolve_requested_task(items: list[dict[str, object]], requested: str) -> dict[str, object] | None:
    chosen = find_task(items, requested)
    if not chosen:
        return None
    children = task_children(items)
    if requested in children:
        for child in children[requested]:
            if not child["done"]:
                return child
    return chosen


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync task execution state with tasks.md.")
    parser.add_argument("spec_dir", help="Path to the spec directory")
    parser.add_argument("--set-current", help="Task number to mark as the active task")
    parser.add_argument("--clear-current", action="store_true", help="Clear the active task")
    args = parser.parse_args()

    spec_dir = Path(args.spec_dir)
    meta = load_meta(spec_dir)
    items = load_tasks(spec_dir, meta)
    if not items:
        print("No tasks found.")
        return 1

    sync_execution_state(meta, items)

    if args.set_current:
        if meta["phase"] != "execute":
            print(f"cannot set current task while phase is {meta['phase']}")
            return 1
        chosen = resolve_requested_task(items, args.set_current)
        if not chosen:
            print(f"unknown task: {args.set_current}")
            return 1
        if chosen["done"]:
            print(f"task {chosen['num']} is already completed")
            return 1
        meta["execution"]["current_task"] = str(chosen["num"])
        append_history(meta, "start-task", f"current task set to {chosen['num']}")

    if args.clear_current:
        meta["execution"]["current_task"] = None
        append_history(meta, "clear-task", "cleared current task")

    sync_execution_state(meta, items)
    if not meta["execution"].get("current_task"):
        next_item = choose_next_task(items)
        if next_item and meta["phase"] == "execute":
            meta["execution"]["current_task"] = str(next_item["num"])

    save_meta(spec_dir, meta)
    print(json.dumps(meta["execution"], ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
