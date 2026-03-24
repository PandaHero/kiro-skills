#!/usr/bin/env python3
"""Validate a Kiro-style spec directory."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from spec_runtime import VARIANT_CONFIG, load_meta, phases_for_variant


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


def validate_meta(spec_dir: Path, meta: dict, result: ValidationResult) -> None:
    meta_path = spec_dir / "meta.json"
    if not meta_path.exists():
        result.errors.append("Missing file: meta.json")
        return

    variant = meta.get("variant")
    if variant not in VARIANT_CONFIG:
        result.errors.append(f"meta.json has invalid variant: {variant}")
        return

    phases = phases_for_variant(variant)
    phase = meta.get("phase")
    if phase not in phases:
        result.errors.append(f"meta.json has invalid phase: {phase}")

    expected_docs = set(VARIANT_CONFIG[variant]["docs"])
    meta_docs = set(meta.get("docs", {}))
    if expected_docs != meta_docs:
        result.errors.append(
            f"meta.json docs do not match variant '{variant}'. Expected {sorted(expected_docs)}, got {sorted(meta_docs)}"
        )

    approvals = meta.get("approvals", {})
    if phase in phases:
        phase_index = phases.index(phase)
        for prior_phase in phases[:phase_index]:
            if prior_phase in expected_docs and not approvals.get(prior_phase, False):
                result.errors.append(
                    f"meta.json moved past unapproved phase '{prior_phase}'."
                )

    execution = meta.get("execution", {})
    current_task = execution.get("current_task")
    if current_task and phase != "execute":
        result.errors.append("meta.json has an active task while phase is not 'execute'.")


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


def validate_bugfix(path: Path, result: ValidationResult) -> None:
    text = read(path, result)
    if not text:
        return

    for heading in [
        "# Bugfix Analysis",
        "## Summary",
        "## Reproduction",
        "## Root-Cause Hypothesis",
        "## Acceptance Criteria",
    ]:
        if heading not in text:
            result.errors.append(f"{path.name} is missing heading: {heading}")

    if PLACEHOLDER_PATTERN.search(text):
        result.warnings.append(f"{path.name} still contains template placeholders.")

    criteria_match = re.search(r"## Acceptance Criteria\s*$([\s\S]*?)(?=^## |\Z)", text, flags=re.MULTILINE)
    if not criteria_match:
        result.errors.append(f"{path.name} is missing acceptance criteria.")
        return

    criteria_lines = re.findall(r"^\d+\.\s+(.+)$", criteria_match.group(1), flags=re.MULTILINE)
    if not criteria_lines:
        result.errors.append(f"{path.name} has no numbered acceptance criteria.")
        return

    for idx, line in enumerate(criteria_lines, start=1):
        req_id = f"1.{idx}"
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


def validate_tasks(path: Path, meta: dict, result: ValidationResult) -> None:
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
            if meta["variant"] == "design-first":
                if "Design References:" not in details and "Requirements:" not in details:
                    result.errors.append(
                        f"{path.name} task {num} is missing Design References metadata."
                    )
                refs = set(REQ_REF_PATTERN.findall(details))
                if refs:
                    result.referenced_ids.update(refs)
            else:
                if "Requirements:" not in details:
                    result.errors.append(f"{path.name} task {num} is missing a Requirements reference.")
                else:
                    refs = set(REQ_REF_PATTERN.findall(details))
                    if not refs and result.requirement_ids:
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

    if result.requirement_ids:
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
    elif meta["variant"] == "design-first":
        result.warnings.append(
            f"{path.name} is being validated in design-first mode, so requirement traceability is advisory only."
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a .kiro/specs/<feature-name> directory.")
    parser.add_argument("spec_dir", help="Path to the spec directory")
    args = parser.parse_args()

    spec_dir = Path(args.spec_dir)
    meta = load_meta(spec_dir)
    result = ValidationResult()

    validate_meta(spec_dir, meta, result)

    if meta["variant"] == "feature":
        validate_requirements(spec_dir / meta["docs"]["requirements"], result)
    elif meta["variant"] == "bugfix":
        validate_bugfix(spec_dir / meta["docs"]["bugfix"], result)

    validate_design(spec_dir / meta["docs"]["design"], result)
    validate_tasks(spec_dir / meta["docs"]["tasks"], meta, result)

    return result.emit()


if __name__ == "__main__":
    sys.exit(main())
