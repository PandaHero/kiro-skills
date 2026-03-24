#!/usr/bin/env python3
"""Recommend the next executable task from a tasks.md file."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


CHECKBOX_PATTERN = re.compile(
    r"^(?P<indent>\s*)-\s\[(?P<done>[ xX])\]\s+(?P<num>\d+(?:\.\d+){0,1})\.?\s+(?P<desc>.+)$"
)


def parse_items(text: str) -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    for line in text.splitlines():
        match = CHECKBOX_PATTERN.match(line)
        if match:
            current = {
                "num": match.group("num"),
                "done": match.group("done").lower() == "x",
                "desc": match.group("desc").strip(),
                "details": [],
            }
            items.append(current)
            continue
        if current is not None:
            current["details"].append(line.rstrip())
    return items


def choose_next(items: list[dict[str, object]]) -> dict[str, object] | None:
    top_level = [item for item in items if str(item["num"]).count(".") == 0]
    by_parent: dict[str, list[dict[str, object]]] = {}
    for item in items:
        num = str(item["num"])
        if "." in num:
            parent = num.split(".", 1)[0]
            by_parent.setdefault(parent, []).append(item)

    for item in top_level:
        num = str(item["num"])
        children = by_parent.get(num, [])
        if children:
            for child in children:
                if not child["done"]:
                    return child
            if not item["done"]:
                return item
        elif not item["done"]:
            return item
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Print the next pending task from tasks.md.")
    parser.add_argument("tasks_file", help="Path to tasks.md")
    args = parser.parse_args()

    tasks_file = Path(args.tasks_file)
    if not tasks_file.exists():
        print(f"missing file: {tasks_file}")
        return 1

    items = parse_items(tasks_file.read_text(encoding="utf-8"))
    next_item = choose_next(items)
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
