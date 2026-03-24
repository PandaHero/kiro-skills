#!/usr/bin/env python3
"""Validate a Kiro-style spec directory."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


REQUIRED_DESIGN_SECTIONS = [
    "Overview",
    "Architecture",
    "Components and Interfaces",
    "Data Models",
    "Error Handling",
    "Testing Strategy",
]

EARS_PATTERN = re.compile(
    r"^(WHEN|IF|WHILE|WHERE|WHENEVER|IN CASE|IN THE EVENT OF|THE SYSTEM SHALL)\b",
    re.IGNORECASE,
)
CHECKBOX_PATTERN = re.compile(
    r"^(?P<indent>\s*)-\s\[(?P<done>[ xX])\]\s+(?P<num>\d+(?:\.\d+){0,1})\.?\s+(?P<desc>.+)$"
)
REQ_REF_PATTERN = re.compile(r"\b\d+\.\d+\b")
PLACEHOLDER_PATTERN = re.compile(
    r"\[role\]|\[feature\]|\[benefit\]|\[event\]|\[system\]|\[response\]|src/\.\.\.|tests/\.\.\.|{{[A-Z_]+}}"
)
BANNED_TASK_TERMS = [
    "deploy",
    "staging",
    "production",
    "user acceptance",
    "manual test",
    "marketing",
    "training",
    "business process",
    "documentation only",
]


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    requirement_ids: set[str] = field(default_factory=set)
    referenced_ids: set[str] = field(default_factory=set)

    def emit(self) -> int:
        if self.errors:
            print("ERRORS:")
            for item in self.errors:
                print(f"- {item}")
        if self.warnings:
            print("WARNINGS:")
            for item in self.warnings:
                print(f"- {item}")
        if not self.errors and not self.warnings:
            print("Spec is valid.")
        elif not self.errors:
            print("Spec is valid with warnings.")
        return 1 if self.errors else 0


def read(path: Path, result: ValidationResult) -> str:
    if not path.exists():
        result.errors.append(f"Missing file: {path}")
        return ""
    return path.read_text(encoding="utf-8")


def validate_requirements(path: Path, result: ValidationResult) -> None:
    text = read(path, result)
    if not text:
        return

    for heading in ["# Requirements Document", "## Introduction", "## Requirements"]:
        if heading not in text:
            result.errors.append(f"{path.name} is missing heading: {heading}")

    if PLACEHOLDER_PATTERN.search(text):
        result.warnings.append(f"{path.name} still contains template placeholders.")

    requirement_blocks = re.findall(
        r"^### Requirement (\d+)\s*$([\s\S]*?)(?=^### Requirement \d+\s*$|\Z)",
        text,
        flags=re.MULTILINE,
    )
    if not requirement_blocks:
        result.errors.append(f"{path.name} does not contain any '### Requirement N' sections.")
        return

    for req_num, block in requirement_blocks:
        if "**User Story:**" not in block:
            result.errors.append(f"{path.name} Requirement {req_num} is missing a user story.")
        criteria_match = re.search(
            r"#### Acceptance Criteria\s*$([\s\S]*?)(?=^### Requirement \d+\s*$|\Z)",
            block,
            flags=re.MULTILINE,
        )
        if not criteria_match:
            result.errors.append(f"{path.name} Requirement {req_num} is missing acceptance criteria.")
            continue

        criteria_lines = re.findall(r"^\d+\.\s+(.+)$", criteria_match.group(1), flags=re.MULTILINE)
        if not criteria_lines:
            result.errors.append(f"{path.name} Requirement {req_num} has no numbered acceptance criteria.")
            continue

        for idx, line in enumerate(criteria_lines, start=1):
            req_id = f"{req_num}.{idx}"
            result.requirement_ids.add(req_id)
            if not EARS_PATTERN.match(line.strip()):
                result.errors.append(
                    f"{path.name} acceptance criterion {req_id} does not appear to use EARS syntax."
                )


def validate_design(path: Path, result: ValidationResult) -> None:
    text = read(path, result)
    if not text:
        return

    for section in REQUIRED_DESIGN_SECTIONS:
        heading = f"## {section}"
        if heading not in text:
            result.errors.append(f"{path.name} is missing section: {heading}")

    if PLACEHOLDER_PATTERN.search(text):
        result.warnings.append(f"{path.name} still contains template placeholders.")


def parse_task_blocks(text: str) -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    for raw_line in text.splitlines():
        match = CHECKBOX_PATTERN.match(raw_line)
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
            current["details"].append(raw_line.rstrip())
    return items


def validate_tasks(path: Path, result: ValidationResult) -> None:
    text = read(path, result)
    if not text:
        return

    if "# Implementation Plan" not in text:
        result.errors.append(f"{path.name} is missing heading: # Implementation Plan")

    items = parse_task_blocks(text)
    if not items:
        result.errors.append(f"{path.name} does not contain any checkbox tasks.")
        return

    child_map: dict[str, list[dict[str, object]]] = {}
    for item in items:
        num = str(item["num"])
        if "." in num:
            parent = num.split(".", 1)[0]
            child_map.setdefault(parent, []).append(item)

    if PLACEHOLDER_PATTERN.search(text):
        result.warnings.append(f"{path.name} still contains template placeholders.")

    for item in items:
        num = str(item["num"])
        desc = str(item["desc"])
        details = "\n".join(item["details"])
        has_children = num in child_map

        if num.count(".") > 1:
            result.errors.append(
                f"{path.name} task {num} exceeds the allowed hierarchy depth of two levels."
            )

        if not has_children:
            if "Requirements:" not in details:
                result.errors.append(f"{path.name} task {num} is missing a Requirements reference.")
            else:
                refs = set(REQ_REF_PATTERN.findall(details))
                if not refs:
                    result.errors.append(f"{path.name} task {num} has an empty Requirements reference.")
                else:
                    result.referenced_ids.update(refs)

            if "Files/Components:" not in details:
                result.warnings.append(f"{path.name} task {num} is missing Files/Components metadata.")

        lowered = f"{desc}\n{details}".lower()
        for term in BANNED_TASK_TERMS:
            if term in lowered:
                result.warnings.append(
                    f"{path.name} task {num} appears to include non-coding work: '{term}'."
                )

    missing = sorted(result.requirement_ids - result.referenced_ids)
    if missing:
        result.errors.append(
            f"{path.name} does not cover all acceptance criteria. Missing references for: {', '.join(missing)}"
        )

    unknown = sorted(result.referenced_ids - result.requirement_ids)
    if unknown:
        result.errors.append(
            f"{path.name} references unknown acceptance criteria: {', '.join(unknown)}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a .kiro/specs/<feature-name> directory.")
    parser.add_argument("spec_dir", help="Path to the spec directory")
    args = parser.parse_args()

    spec_dir = Path(args.spec_dir)
    result = ValidationResult()

    validate_requirements(spec_dir / "requirements.md", result)
    validate_design(spec_dir / "design.md", result)
    validate_tasks(spec_dir / "tasks.md", result)

    return result.emit()


if __name__ == "__main__":
    sys.exit(main())
