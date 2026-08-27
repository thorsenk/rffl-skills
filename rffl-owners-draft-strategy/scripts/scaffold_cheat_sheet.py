#!/usr/bin/env python3
"""Create a blank RFFL cheat-sheet JSON scaffold."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROSTER_DEFAULT = [
    {"slot": "QB", "count": 1, "eligible_positions": ["QB"]},
    {"slot": "RB", "count": 2, "eligible_positions": ["RB"]},
    {"slot": "WR", "count": 2, "eligible_positions": ["WR"]},
    {"slot": "TE", "count": 1, "eligible_positions": ["TE"]},
    {"slot": "FLEX", "count": 1, "eligible_positions": ["RB", "WR", "TE"]},
    {"slot": "DST", "count": 1, "eligible_positions": ["DST"]},
    {"slot": "K", "count": 1, "eligible_positions": ["K"]},
    {"slot": "BENCH", "count": 7, "eligible_positions": ["QB", "RB", "WR", "TE", "DST", "K"]}
]

RECEPTION_POINTS = {
    "non_ppr": 0.0,
    "half_ppr": 0.5,
    "ppr": 1.0,
    "custom": 0.0
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a blank RFFL cheat-sheet JSON scaffold.")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--season", required=True, type=int)
    parser.add_argument("--teams", required=True, type=int)
    parser.add_argument("--scoring", choices=sorted(RECEPTION_POINTS), required=True)
    parser.add_argument("--draft-type", choices=["snake", "linear", "third_round_reversal", "salary_cap"], required=True)
    parser.add_argument("--rounds", required=True, type=int)
    parser.add_argument("--league-format", choices=["redraft", "keeper", "dynasty_startup", "rookie_only", "best_ball"], default="redraft")
    parser.add_argument("--league-name", default="RFFL")
    parser.add_argument("--team-name", default="")
    parser.add_argument("--team-abbr", default="")
    parser.add_argument("--slot", type=int)
    parser.add_argument("--budget", type=float)
    parser.add_argument("--platform", default="")
    parser.add_argument("--draft-date", default=None, help="ISO-8601 date-time when known.")
    args = parser.parse_args()

    if args.draft_type == "salary_cap" and not args.budget:
        parser.error("--budget is required for salary_cap drafts")
    if args.draft_type != "salary_cap" and args.slot is not None and not 1 <= args.slot <= args.teams:
        parser.error("--slot must be within the number of Teams")

    timestamp = now_iso()
    data = {
        "meta": {
            "schema_version": "1.0.0",
            "title": "RFFL Draft Cheat Sheet",
            "season": args.season,
            "version": "0.1.0",
            "status": "draft",
            "mode": "consensus",
            "created_at": timestamp,
            "updated_at": timestamp,
            "research_cutoff": None,
            "parent_version": None,
            "assumptions": []
        },
        "team": {
            "name": args.team_name,
            "abbr": args.team_abbr,
            "owner_names": []
        },
        "league": {
            "name": args.league_name,
            "format": args.league_format,
            "teams": args.teams,
            "scoring": {
                "preset": args.scoring,
                "reception_points": RECEPTION_POINTS[args.scoring],
                "te_reception_points": RECEPTION_POINTS[args.scoring],
                "passing_td_points": 4,
                "interception_points": -2,
                "points_per_first_down": 0,
                "bonuses": [],
                "notes": []
            },
            "draft": {
                "type": args.draft_type,
                "rounds": args.rounds,
                "slot": args.slot,
                "budget": args.budget,
                "minimum_bid": 1 if args.draft_type == "salary_cap" else None,
                "platform": args.platform or None,
                "date": args.draft_date,
                "time_zone": None
            },
            "roster": ROSTER_DEFAULT,
            "keepers": [],
            "traded_picks": [],
            "position_limits": {}
        },
        "display": {
            "include_overall_board": True,
            "include_strategy_page": True,
            "include_unavailable_on_board": False,
            "position_order": ["WR", "RB", "QB", "TE", "DST", "K", "DL", "LB", "DB"],
            "adp_label": "ADP"
        },
        "players": [],
        "tier_notes": [],
        "strategy": {
            "profile": {},
            "targets": [],
            "values": [],
            "avoids": [],
            "rules": []
        },
        "sources": [],
        "research_conflicts": [],
        "history": [
            {
                "version": "0.1.0",
                "created_at": timestamp,
                "change_type": "initial",
                "summary": "Created blank cheat-sheet scaffold.",
                "parent_version": None
            }
        ]
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
        handle.write("\n")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
