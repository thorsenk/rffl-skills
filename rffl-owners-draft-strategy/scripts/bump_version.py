#!/usr/bin/env python3
"""Bump a cheat-sheet semantic version and append a history entry."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def bump(version: str, part: str) -> str:
    try:
        major, minor, patch = (int(value) for value in version.split("."))
    except Exception as exc:
        raise ValueError(f"Invalid semantic version: {version!r}") from exc
    if part == "major":
        return f"{major + 1}.0.0"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    if part == "patch":
        return f"{major}.{minor}.{patch + 1}"
    raise ValueError(f"Unknown version part: {part}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Bump an RFFL cheat-sheet version.")
    parser.add_argument("source", type=Path)
    parser.add_argument("--part", choices=["major", "minor", "patch"], required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--change-type", choices=["refresh", "strategy", "league", "schema", "variant"], default="refresh")
    parser.add_argument("--output", type=Path, help="Write to a new file instead of modifying the source.")
    args = parser.parse_args()

    with args.source.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    meta = data.setdefault("meta", {})
    old_version = str(meta.get("version", "0.0.0"))
    new_version = bump(old_version, args.part)
    timestamp = now_iso()

    meta["parent_version"] = old_version
    meta["version"] = new_version
    meta["updated_at"] = timestamp
    data.setdefault("history", []).append(
        {
            "version": new_version,
            "created_at": timestamp,
            "change_type": args.change_type,
            "summary": args.summary,
            "parent_version": old_version
        }
    )

    destination = args.output or args.source
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
        handle.write("\n")

    print(f"{old_version} -> {new_version}: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
