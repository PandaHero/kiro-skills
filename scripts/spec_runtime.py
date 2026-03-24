#!/usr/bin/env python3
"""Shared helpers for the Kiro-inspired workflow runtime."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path


VARIANT_CONFIG = {
    "feature": {
        "phases": ["requirements", "design", "tasks", "execute", "completed"],
        "docs": {
            "requirements": "requirements.md",
            "design": "design.md",
            "tasks": "tasks.md",
        },
    },
    "design-first": {
        "phases": ["design", "tasks", "execute", "completed"],
        "docs": {
            "design": "design.md",
            "tasks": "tasks.md",
        },
    },
    "bugfix": {
        "phases": ["bugfix", "design", "tasks", "execute", "completed"],
        "docs": {
            "bugfix": "bugfix.md",
            "design": "design.md",
            "tasks": "tasks.md",
        },
    },
}

REVIEW_PROMPTS = {
    "requirements": "Do the requirements look good? If so, we can move on to the design.",
    "bugfix": "Does the bugfix analysis look good? If so, we can move on to the design.",
    "design": "Does the design look good? If so, we can move on to the implementation plan.",
    "tasks": "Do the tasks look good?",
}

CHECKBOX_PATTERN = re.compile(
    r"^(?P<indent>\s*)-\s\[(?P<done>[ xX])\]\s+(?P<num>\d+(?:\.\d+)?)\.?\s+(?P<desc>.+)$"
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def normalize_feature_name(name: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", name.strip().lower())
    normalized = re.sub(r"-{2,}", "-", normalized).strip("-")
    return normalized or "new-feature"


def title_case(feature_name: str) -> str:
    parts = feature_name.replace("_", "-").split("-")
    return " ".join(part.capitalize() for part in parts if part)


def default_meta(feature_name: str, variant: str = "feature", feature_title: str | None = None) -> dict:
    config = VARIANT_CONFIG[variant]
    docs = {phase: filename for phase, filename in config["docs"].items()}
    return {
        "schema_version": 2,
        "feature_name": feature_name,
        "feature_title": feature_title or title_case(feature_name),
        "variant": variant,
        "phase": config["phases"][0],
        "approvals": {phase: False for phase in docs},
        "docs": docs,
        "execution": {
            "current_task": None,
            "last_completed_task": None,
            "pending_tasks": [],
            "completed_tasks": [],
        },
        "history": [
            {
                "timestamp": utc_now(),
                "action": "init",
                "detail": f"Initialized {variant} workflow",
            }
        ],
    }


def append_history(meta: dict, action: str, detail: str) -> None:
    meta.setdefault("history", []).append(
        {"timestamp": utc_now(), "action": action, "detail": detail}
    )


def spec_meta_path(spec_dir: Path) -> Path:
    return spec_dir / "meta.json"


def detect_variant(spec_dir: Path) -> str:
    if (spec_dir / "meta.json").exists():
        meta = json.loads((spec_dir / "meta.json").read_text(encoding="utf-8"))
        variant = meta.get("variant")
        if variant in VARIANT_CONFIG:
            return variant
    if (spec_dir / "bugfix.md").exists():
        return "bugfix"
    if (spec_dir / "requirements.md").exists():
        return "feature"
    return "design-first"


def infer_phase(spec_dir: Path, meta: dict) -> str:
    variant = meta["variant"]
    config = VARIANT_CONFIG[variant]
    docs = meta.get("docs", config["docs"])
    approvals = meta.get("approvals", {})

    for phase in config["phases"]:
        if phase in docs:
            path = spec_dir / docs[phase]
            if not path.exists():
                return phase
            if not approvals.get(phase, False):
                return phase
        elif phase == "execute":
            tasks_phase = "tasks" if "tasks" in docs else None
            if tasks_phase and approvals.get(tasks_phase, False):
                return "execute"
        elif phase == "completed":
            return "completed"
    return config["phases"][-1]


def load_meta(spec_dir: Path) -> dict:
    meta_path = spec_meta_path(spec_dir)
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        variant = meta.get("variant", detect_variant(spec_dir))
        if variant not in VARIANT_CONFIG:
            variant = "feature"
        meta["variant"] = variant
        meta.setdefault("docs", dict(VARIANT_CONFIG[variant]["docs"]))
        meta.setdefault("approvals", {phase: False for phase in meta["docs"]})
        meta.setdefault("execution", {})
        meta["execution"].setdefault("current_task", None)
        meta["execution"].setdefault("last_completed_task", None)
        meta["execution"].setdefault("pending_tasks", [])
        meta["execution"].setdefault("completed_tasks", [])
        meta.setdefault("history", [])
        meta.setdefault("feature_name", spec_dir.name)
        meta.setdefault("feature_title", title_case(meta["feature_name"]))
        meta.setdefault("schema_version", 2)
        meta.setdefault("phase", infer_phase(spec_dir, meta))
        return meta

    feature_name = normalize_feature_name(spec_dir.name)
    meta = default_meta(feature_name, detect_variant(spec_dir), title_case(feature_name))
    meta["phase"] = infer_phase(spec_dir, meta)
    return meta


def save_meta(spec_dir: Path, meta: dict) -> Path:
    path = spec_meta_path(spec_dir)
    path.write_text(json.dumps(meta, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return path


def phases_for_variant(variant: str) -> list[str]:
    return list(VARIANT_CONFIG[variant]["phases"])


def next_phase(variant: str, phase: str) -> str | None:
    phases = phases_for_variant(variant)
    try:
        index = phases.index(phase)
    except ValueError:
        return None
    if index + 1 >= len(phases):
        return None
    return phases[index + 1]


def previous_phase(variant: str, phase: str) -> str | None:
    phases = phases_for_variant(variant)
    try:
        index = phases.index(phase)
    except ValueError:
        return None
    if index == 0:
        return None
    return phases[index - 1]


def doc_for_phase(meta: dict, phase: str) -> str | None:
    return meta.get("docs", {}).get(phase)


def phase_requires_review(meta: dict, phase: str) -> bool:
    return phase in meta.get("docs", {})


def review_prompt(phase: str) -> str | None:
    return REVIEW_PROMPTS.get(phase)


def parse_tasks(text: str) -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    for raw_line in text.splitlines():
        match = CHECKBOX_PATTERN.match(raw_line)
        if match:
            current = {
                "num": match.group("num"),
                "done": match.group("done").lower() == "x",
                "desc": match.group("desc").strip(),
                "indent": len(match.group("indent")),
                "details": [],
            }
            items.append(current)
            continue
        if current is not None:
            current["details"].append(raw_line.rstrip())
    return items


def load_tasks(spec_dir: Path, meta: dict) -> list[dict[str, object]]:
    tasks_file = doc_for_phase(meta, "tasks")
    if not tasks_file:
        return []
    path = spec_dir / tasks_file
    if not path.exists():
        return []
    return parse_tasks(path.read_text(encoding="utf-8"))


def task_children(items: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    mapping: dict[str, list[dict[str, object]]] = {}
    for item in items:
        num = str(item["num"])
        if "." in num:
            parent = num.split(".", 1)[0]
            mapping.setdefault(parent, []).append(item)
    return mapping


def choose_next_task(items: list[dict[str, object]], current_task: str | None = None) -> dict[str, object] | None:
    if current_task:
        for item in items:
            if str(item["num"]) == current_task and not item["done"]:
                return item

    children = task_children(items)
    top_level = [item for item in items if "." not in str(item["num"])]
    for item in top_level:
        num = str(item["num"])
        if num in children:
            for child in children[num]:
                if not child["done"]:
                    return child
            if not item["done"]:
                return item
        elif not item["done"]:
            return item
    return None


def find_task(items: list[dict[str, object]], task_number: str) -> dict[str, object] | None:
    for item in items:
        if str(item["num"]) == task_number:
            return item
    return None


def sync_execution_state(meta: dict, items: list[dict[str, object]]) -> None:
    completed = [str(item["num"]) for item in items if item["done"]]
    pending = [str(item["num"]) for item in items if not item["done"]]
    current = meta.setdefault("execution", {}).get("current_task")
    if current and current not in pending:
        meta["execution"]["last_completed_task"] = current
        meta["execution"]["current_task"] = None
    meta["execution"]["pending_tasks"] = pending
    meta["execution"]["completed_tasks"] = completed


def mark_phase_approved(meta: dict, phase: str, actor: str = "user") -> None:
    meta.setdefault("approvals", {})[phase] = True
    append_history(meta, "approve", f"{actor} approved {phase}")


def can_advance(spec_dir: Path, meta: dict) -> tuple[bool, str]:
    phase = meta["phase"]
    if phase == "completed":
        return False, "Workflow is already completed."
    if phase == "execute":
        items = load_tasks(spec_dir, meta)
        if any(not item["done"] for item in items):
            return False, "Pending tasks remain, so execution is not complete."
        return True, "Execution is complete."

    doc_name = doc_for_phase(meta, phase)
    if not doc_name:
        return False, f"Phase '{phase}' is not a document phase."
    if not (spec_dir / doc_name).exists():
        return False, f"Missing {doc_name}."
    if not meta.get("approvals", {}).get(phase, False):
        return False, f"Phase '{phase}' is not approved."
    return True, f"Phase '{phase}' is approved."
