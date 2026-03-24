#!/usr/bin/env python3
"""Scaffold a Kiro-style spec directory from bundled templates."""

from __future__ import annotations

import argparse
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent.parent
REFERENCE_DIR = SKILL_DIR / "references"
DEFAULT_SPEC_ROOT = Path(".kiro/specs")


def load_template(name: str) -> str:
    return (REFERENCE_DIR / name).read_text(encoding="utf-8")


def title_case(feature_name: str) -> str:
    return " ".join(part.capitalize() for part in feature_name.replace("_", "-").split("-") if part)


def render(template: str, feature_name: str, feature_title: str) -> str:
    return (
        template.replace("{{FEATURE_NAME}}", feature_name)
        .replace("{{FEATURE_TITLE}}", feature_title)
    )


def write_file(path: Path, content: str, overwrite: bool) -> str:
    if path.exists() and not overwrite:
        return f"skip {path}"
    path.write_text(content, encoding="utf-8")
    return f"write {path}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create .kiro/specs/<feature-name>/ from bundled templates."
    )
    parser.add_argument("feature_name", help="kebab-case feature name, for example user-authentication")
    parser.add_argument(
        "--spec-root",
        default=str(DEFAULT_SPEC_ROOT),
        help="spec root directory, default: .kiro/specs",
    )
    parser.add_argument("--title", help="optional human-readable feature title")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="overwrite existing files instead of skipping them",
    )
    args = parser.parse_args()

    feature_name = args.feature_name.strip()
    feature_title = args.title.strip() if args.title else title_case(feature_name)
    spec_dir = Path(args.spec_root) / feature_name
    spec_dir.mkdir(parents=True, exist_ok=True)

    files = {
        "requirements.md": render(
            load_template("requirements-template.md"), feature_name, feature_title
        ),
        "design.md": render(load_template("design-template.md"), feature_name, feature_title),
        "tasks.md": render(load_template("tasks-template.md"), feature_name, feature_title),
    }

    for name, content in files.items():
        result = write_file(spec_dir / name, content, args.overwrite)
        print(result)

    print(f"spec directory ready: {spec_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
