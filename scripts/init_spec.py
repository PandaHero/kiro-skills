#!/usr/bin/env python3
"""Scaffold a Kiro-style spec directory from bundled templates."""

from __future__ import annotations

import argparse
from pathlib import Path

from spec_runtime import VARIANT_CONFIG, default_meta, normalize_feature_name, save_meta, title_case


SKILL_DIR = Path(__file__).resolve().parent.parent
REFERENCE_DIR = SKILL_DIR / "references"
DEFAULT_SPEC_ROOT = Path(".kiro/specs")
TEMPLATES = {
    "feature": {
        "requirements": "requirements-template.md",
        "design": "design-template.md",
        "tasks": "tasks-template.md",
    },
    "design-first": {
        "design": "design-template.md",
        "tasks": "tasks-design-first-template.md",
    },
    "bugfix": {
        "bugfix": "bugfix-template.md",
        "design": "design-template.md",
        "tasks": "tasks-bugfix-template.md",
    },
}


def load_template(name: str) -> str:
    return (REFERENCE_DIR / name).read_text(encoding="utf-8")


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
    parser.add_argument("feature_name", help="Feature name, for example user-authentication")
    parser.add_argument(
        "--spec-root",
        default=str(DEFAULT_SPEC_ROOT),
        help="Spec root directory, default: .kiro/specs",
    )
    parser.add_argument("--title", help="Optional human-readable feature title")
    parser.add_argument(
        "--variant",
        choices=sorted(VARIANT_CONFIG),
        default="feature",
        help="Workflow variant to initialize",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files instead of skipping them",
    )
    args = parser.parse_args()

    feature_name = normalize_feature_name(args.feature_name)
    feature_title = args.title.strip() if args.title else title_case(feature_name)
    spec_dir = Path(args.spec_root) / feature_name
    spec_dir.mkdir(parents=True, exist_ok=True)

    meta = default_meta(feature_name, args.variant, feature_title)
    for phase, filename in meta["docs"].items():
        template_name = TEMPLATES[args.variant][phase]
        content = render(load_template(template_name), feature_name, feature_title)
        result = write_file(spec_dir / filename, content, args.overwrite)
        print(result)

    save_meta(spec_dir, meta)
    print(f"write {spec_dir / 'meta.json'}")
    print(f"spec directory ready: {spec_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
