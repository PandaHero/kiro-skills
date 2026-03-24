#!/usr/bin/env python3
"""Advance the workflow to the next phase if prerequisites are satisfied."""

from __future__ import annotations

import argparse
from pathlib import Path

from spec_runtime import append_history, can_advance, load_meta, next_phase, save_meta


def main() -> int:
    parser = argparse.ArgumentParser(description="Advance a spec workflow to its next phase.")
    parser.add_argument("spec_dir", help="Path to the spec directory")
    args = parser.parse_args()

    spec_dir = Path(args.spec_dir)
    meta = load_meta(spec_dir)
    ok, reason = can_advance(spec_dir, meta)
    if not ok:
        print(reason)
        return 1

    new_phase = next_phase(meta["variant"], meta["phase"])
    if not new_phase:
        print("no further phase available")
        return 1

    old_phase = meta["phase"]
    meta["phase"] = new_phase
    append_history(meta, "advance", f"{old_phase} -> {new_phase}")
    save_meta(spec_dir, meta)
    print(f"advanced {old_phase} -> {new_phase}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
