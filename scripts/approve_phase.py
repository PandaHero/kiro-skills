#!/usr/bin/env python3
"""Record explicit approval for the current phase."""

from __future__ import annotations

import argparse
from pathlib import Path

from spec_runtime import doc_for_phase, load_meta, mark_phase_approved, save_meta


def main() -> int:
    parser = argparse.ArgumentParser(description="Approve the current workflow phase.")
    parser.add_argument("spec_dir", help="Path to the spec directory")
    parser.add_argument("phase", help="Phase to approve")
    parser.add_argument("--actor", default="user", help="Approver recorded in history")
    args = parser.parse_args()

    spec_dir = Path(args.spec_dir)
    meta = load_meta(spec_dir)

    if args.phase != meta["phase"]:
        print(f"cannot approve {args.phase}: current phase is {meta['phase']}")
        return 1

    doc_name = doc_for_phase(meta, args.phase)
    if not doc_name:
        print(f"phase {args.phase} is not a reviewable document phase")
        return 1

    if not (spec_dir / doc_name).exists():
        print(f"missing file: {spec_dir / doc_name}")
        return 1

    mark_phase_approved(meta, args.phase, args.actor)
    save_meta(spec_dir, meta)
    print(f"approved {args.phase}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
