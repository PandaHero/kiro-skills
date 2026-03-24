#!/usr/bin/env python3
"""Heuristic router for spec workflow requests."""

from __future__ import annotations

import argparse
import json
import re


CREATE_PATTERNS = [
    r"\bspec\b",
    r"\bspecification\b",
    r"\brequirements?\b",
    r"\bimplementation plan\b",
    r"\bdesign doc(?:ument)?\b",
    r"需求文档",
    r"设计文档",
    r"实现计划",
    r"规格",
]

EXECUTE_PATTERNS = [
    r"\bstart task\b",
    r"\bexecute task\b",
    r"\bimplement task\b",
    r"\bnext task\b",
    r"\btask\s+\d+(?:\.\d+)?\b",
    r"执行任务",
    r"开始任务",
    r"下一个任务",
]

EDIT_PATTERNS = [
    r"\brevise spec\b",
    r"\bupdate (?:requirements|design|tasks)\b",
    r"\bedit (?:requirements|design|tasks)\b",
    r"修改需求",
    r"修改设计",
    r"修改任务",
]


def classify(text: str) -> dict:
    lowered = text.strip().lower()
    create_matches = [pattern for pattern in CREATE_PATTERNS if re.search(pattern, lowered, re.IGNORECASE)]
    execute_matches = [pattern for pattern in EXECUTE_PATTERNS if re.search(pattern, lowered, re.IGNORECASE)]
    edit_matches = [pattern for pattern in EDIT_PATTERNS if re.search(pattern, lowered, re.IGNORECASE)]
    matched = []
    action = "do"
    confidence = 0.7
    sequence: list[str] = []

    if create_matches and execute_matches:
        action = "mixed-spec-request"
        confidence = 0.99
        matched = create_matches + execute_matches
        sequence = ["create-spec", "execute-task"]
    elif execute_matches:
        action = "execute-task"
        confidence = 0.98
        matched = execute_matches
    elif edit_matches:
        action = "revise-spec"
        confidence = 0.92
        matched = edit_matches
    elif create_matches:
        action = "create-spec"
        confidence = 0.9
        matched = create_matches

    mode = "spec" if action != "do" else "do"
    result = {
        "mode": mode,
        "action": action,
        "confidence": confidence,
        "matched_patterns": matched,
    }
    if sequence:
        result["suggested_sequence"] = sequence
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify a request into do/spec workflow modes.")
    parser.add_argument("text", nargs="+", help="Request text to classify")
    args = parser.parse_args()

    result = classify(" ".join(args.text))
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
