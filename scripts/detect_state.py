#!/usr/bin/env python3
"""Inspect the persisted workflow state for a spec directory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from spec_runtime import (
    can_advance,
    doc_for_phase,
    infer_phase,
    load_meta,
    next_phase,
    phase_requires_review,
    review_prompt,
)


def summarize(spec_dir: Path) -> dict:
    meta = load_meta(spec_dir)
    recommended_phase = infer_phase(spec_dir, meta)
    current_doc = doc_for_phase(meta, meta["phase"])
    ok_to_advance, reason = can_advance(spec_dir, meta)
    summary = {
        "feature_name": meta["feature_name"],
        "feature_title": meta["feature_title"],
        "variant": meta["variant"],
        "phase": meta["phase"],
        "current_document": current_doc,
        "review_required": phase_requires_review(meta, meta["phase"]),
        "review_prompt": review_prompt(meta["phase"]),
        "approved_documents": meta.get("approvals", {}),
        "next_phase": next_phase(meta["variant"], meta["phase"]),
        "can_advance": ok_to_advance,
        "advance_reason": reason,
        "execution": meta.get("execution", {}),
    }
    if recommended_phase != meta["phase"]:
        summary["recommended_phase"] = recommended_phase
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Print workflow state for a spec directory.")
    parser.add_argument("spec_dir", help="Path to the spec directory")
    parser.add_argument("--json", action="store_true", help="Emit JSON only")
    args = parser.parse_args()

    summary = summarize(Path(args.spec_dir))
    if args.json:
        print(json.dumps(summary, ensure_ascii=True, indent=2))
    else:
        for key, value in summary.items():
            print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
