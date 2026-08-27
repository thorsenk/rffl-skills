#!/usr/bin/env python3
"""Validate an RFFL draft cheat-sheet JSON file.

This intentionally uses only the Python standard library so validation works
before optional rendering dependencies are installed.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

ALLOWED_FORMATS = {"redraft", "keeper", "dynasty_startup", "rookie_only", "best_ball"}
ALLOWED_SCORING = {"non_ppr", "half_ppr", "ppr", "custom"}
ALLOWED_DRAFT_TYPES = {"snake", "linear", "third_round_reversal", "salary_cap"}
ALLOWED_AVAILABILITY = {"available", "keeper", "unavailable", "injured", "suspended", "retired"}
ALLOWED_CONFIDENCE = {"high", "medium", "low", None}
TARGET_LIKE_TAGS = {"TARGET", "VALUE", "SLEEPER", "UPSIDE", "SAFE"}
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _parse_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _duplicates(values: Iterable[Any]) -> set[Any]:
    seen: set[Any] = set()
    dupes: set[Any] = set()
    for value in values:
        if value in seen:
            dupes.add(value)
        else:
            seen.add(value)
    return dupes


def validate_data(data: Any, strict: bool = False) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(data, dict):
        return ["Root value must be a JSON object."], warnings

    meta = _as_dict(data.get("meta"))
    league = _as_dict(data.get("league"))
    players = _as_list(data.get("players"))
    sources = _as_list(data.get("sources"))

    # Meta
    season = meta.get("season")
    if not isinstance(season, int) or not 2000 <= season <= 2100:
        errors.append("meta.season must be an integer from 2000 through 2100.")

    version = meta.get("version")
    if not isinstance(version, str) or not VERSION_RE.match(version):
        errors.append("meta.version must use semantic version format, for example 0.1.0.")

    if meta.get("mode") not in {"consensus", "personalized"}:
        errors.append("meta.mode must be consensus or personalized.")

    for field in ("created_at", "updated_at"):
        if _parse_datetime(meta.get(field)) is None:
            errors.append(f"meta.{field} must be an ISO-8601 date-time string.")

    cutoff = meta.get("research_cutoff")
    if cutoff is not None and _parse_datetime(cutoff) is None:
        errors.append("meta.research_cutoff must be null or an ISO-8601 date-time string.")

    # League
    if league.get("format") not in ALLOWED_FORMATS:
        errors.append(f"league.format must be one of: {', '.join(sorted(ALLOWED_FORMATS))}.")

    teams = league.get("teams")
    if not isinstance(teams, int) or not 2 <= teams <= 32:
        errors.append("league.teams must be an integer from 2 through 32.")

    scoring = _as_dict(league.get("scoring"))
    preset = scoring.get("preset")
    if preset not in ALLOWED_SCORING:
        errors.append(f"league.scoring.preset must be one of: {', '.join(sorted(ALLOWED_SCORING))}.")

    reception_points = scoring.get("reception_points")
    if not isinstance(reception_points, (int, float)) or reception_points < 0:
        errors.append("league.scoring.reception_points must be a non-negative number.")
    elif preset == "non_ppr" and reception_points != 0:
        warnings.append("Scoring preset is non_ppr but reception_points is not 0.")
    elif preset == "half_ppr" and reception_points != 0.5:
        warnings.append("Scoring preset is half_ppr but reception_points is not 0.5.")
    elif preset == "ppr" and reception_points != 1:
        warnings.append("Scoring preset is ppr but reception_points is not 1.0.")

    draft = _as_dict(league.get("draft"))
    draft_type = draft.get("type")
    if draft_type not in ALLOWED_DRAFT_TYPES:
        errors.append(f"league.draft.type must be one of: {', '.join(sorted(ALLOWED_DRAFT_TYPES))}.")

    rounds = draft.get("rounds")
    if not isinstance(rounds, int) or not 1 <= rounds <= 60:
        errors.append("league.draft.rounds must be an integer from 1 through 60.")

    if draft_type == "salary_cap":
        budget = draft.get("budget")
        if not isinstance(budget, (int, float)) or budget <= 0:
            errors.append("Salary-cap drafts require a positive league.draft.budget.")
    else:
        slot = draft.get("slot")
        if slot is not None and (not isinstance(slot, int) or slot < 1 or (isinstance(teams, int) and slot > teams)):
            errors.append("league.draft.slot must be null or a valid Team slot.")

    roster = _as_list(league.get("roster"))
    if not roster:
        errors.append("league.roster must contain at least one slot.")
    for index, row in enumerate(roster):
        item = _as_dict(row)
        if not isinstance(item.get("slot"), str) or not item.get("slot", "").strip():
            errors.append(f"league.roster[{index}].slot must be a non-empty string.")
        count = item.get("count")
        if not isinstance(count, int) or count < 0:
            errors.append(f"league.roster[{index}].count must be a non-negative integer.")

    # Sources
    source_ids: list[str] = []
    for index, raw_source in enumerate(sources):
        source = _as_dict(raw_source)
        sid = source.get("id")
        if not isinstance(sid, str) or not sid.strip():
            errors.append(f"sources[{index}].id must be a non-empty string.")
        else:
            source_ids.append(sid)
        for field in ("publisher", "title", "data_type"):
            if not isinstance(source.get(field), str) or not source.get(field, "").strip():
                errors.append(f"sources[{index}].{field} must be a non-empty string.")
        if _parse_datetime(source.get("accessed_at")) is None:
            errors.append(f"sources[{index}].accessed_at must be an ISO-8601 date-time string.")
    for sid in sorted(_duplicates(source_ids)):
        errors.append(f"Duplicate source id: {sid}.")

    known_source_ids = set(source_ids)

    # Players
    player_ids: list[str] = []
    overall_ranks: list[int] = []
    position_ranks: dict[str, list[int]] = defaultdict(list)
    tier_sequences: dict[str, list[tuple[int, int]]] = defaultdict(list)
    overall_tier_sequence: list[tuple[int, int]] = []

    for index, raw_player in enumerate(players):
        player = _as_dict(raw_player)
        prefix = f"players[{index}]"
        pid = player.get("id")
        name = player.get("name")

        if not isinstance(pid, str) or not pid.strip():
            errors.append(f"{prefix}.id must be a non-empty string.")
        else:
            player_ids.append(pid)
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{prefix}.name must be a non-empty string.")

        positions = _as_list(player.get("positions"))
        if not positions or any(not isinstance(p, str) or not p.strip() for p in positions):
            errors.append(f"{prefix}.positions must contain at least one non-empty position.")

        primary = player.get("primary_position")
        if not isinstance(primary, str) or not primary.strip():
            errors.append(f"{prefix}.primary_position must be a non-empty string.")
        elif positions and primary not in positions:
            warnings.append(f"{prefix}.primary_position is not present in positions.")

        availability = player.get("availability")
        if availability not in ALLOWED_AVAILABILITY:
            errors.append(f"{prefix}.availability is invalid.")

        confidence = player.get("confidence")
        if confidence not in ALLOWED_CONFIDENCE:
            errors.append(f"{prefix}.confidence must be high, medium, or low.")

        tags = _as_list(player.get("tags"))
        if len(tags) > 3:
            errors.append(f"{prefix}.tags cannot contain more than three tags.")
        normalized_tags = {str(tag).upper() for tag in tags}
        if availability in {"keeper", "unavailable", "retired"} and normalized_tags & TARGET_LIKE_TAGS:
            errors.append(f"{prefix} is unavailable but has a live-target tag.")

        locked_fields = _as_list(player.get("locked_fields"))
        if any(not isinstance(field, str) for field in locked_fields):
            errors.append(f"{prefix}.locked_fields must contain strings only.")

        overall_rank = player.get("overall_rank")
        overall_tier = player.get("overall_tier")
        if overall_rank is not None:
            if not isinstance(overall_rank, int) or overall_rank < 1:
                errors.append(f"{prefix}.overall_rank must be null or a positive integer.")
            else:
                overall_ranks.append(overall_rank)
                if overall_tier is None:
                    warnings.append(f"{prefix} has an overall rank but no overall tier.")
                elif not isinstance(overall_tier, int) or overall_tier < 1:
                    errors.append(f"{prefix}.overall_tier must be null or a positive integer.")
                else:
                    overall_tier_sequence.append((overall_rank, overall_tier))

        pranks = _as_dict(player.get("position_rank"))
        ptiers = _as_dict(player.get("position_tier"))
        for position, rank in pranks.items():
            if not isinstance(rank, int) or rank < 1:
                errors.append(f"{prefix}.position_rank.{position} must be a positive integer.")
                continue
            position_ranks[position].append(rank)
            tier = ptiers.get(position)
            if tier is None:
                warnings.append(f"{prefix} has {position} rank {rank} but no {position} tier.")
            elif not isinstance(tier, int) or tier < 1:
                errors.append(f"{prefix}.position_tier.{position} must be a positive integer.")
            else:
                tier_sequences[position].append((rank, tier))

        for metric_name in ("adp", "ecr", "projection"):
            metric = _as_dict(player.get(metric_name))
            if metric and metric.get("value") is not None:
                if not isinstance(metric.get("value"), (int, float)):
                    errors.append(f"{prefix}.{metric_name}.value must be numeric or null.")
                if not metric.get("source"):
                    warnings.append(f"{prefix}.{metric_name} has a value but no source.")
                if metric.get("as_of") and _parse_datetime(metric.get("as_of")) is None:
                    errors.append(f"{prefix}.{metric_name}.as_of must be ISO-8601 when present.")

        for sid in _as_list(player.get("source_ids")):
            if sid not in known_source_ids:
                warnings.append(f"{prefix} references unknown source id {sid!r}.")

    for pid in sorted(_duplicates(player_ids)):
        errors.append(f"Duplicate player id: {pid}.")
    for rank in sorted(_duplicates(overall_ranks)):
        errors.append(f"Duplicate overall rank: {rank}.")
    for position, ranks in sorted(position_ranks.items()):
        for rank in sorted(_duplicates(ranks)):
            errors.append(f"Duplicate {position} position rank: {rank}.")

    def check_monotonic(sequence: list[tuple[int, int]], label: str) -> None:
        last_tier = 0
        for rank, tier in sorted(sequence):
            if tier < last_tier:
                errors.append(f"{label} tiers move backward at rank {rank}: tier {tier} follows tier {last_tier}.")
                return
            last_tier = tier

    check_monotonic(overall_tier_sequence, "Overall")
    for position, sequence in sorted(tier_sequences.items()):
        check_monotonic(sequence, position)

    # Strategy references
    player_id_set = set(player_ids)
    strategy = _as_dict(data.get("strategy"))
    for section in ("targets", "values", "avoids"):
        for index, raw_item in enumerate(_as_list(strategy.get(section))):
            item = _as_dict(raw_item)
            pid = item.get("player_id")
            if not isinstance(pid, str) or not pid:
                errors.append(f"strategy.{section}[{index}].player_id must be a non-empty string.")
            elif pid not in player_id_set:
                warnings.append(f"strategy.{section}[{index}] references unknown player id {pid!r}.")

    # Tier notes
    tier_note_keys: list[tuple[str, int]] = []
    for index, raw_note in enumerate(_as_list(data.get("tier_notes"))):
        note = _as_dict(raw_note)
        scope = note.get("scope")
        tier = note.get("tier")
        if not isinstance(scope, str) or not scope.strip():
            errors.append(f"tier_notes[{index}].scope must be a non-empty string.")
        if not isinstance(tier, int) or tier < 1:
            errors.append(f"tier_notes[{index}].tier must be a positive integer.")
        if isinstance(scope, str) and isinstance(tier, int):
            tier_note_keys.append((scope, tier))
    for key in sorted(_duplicates(tier_note_keys)):
        errors.append(f"Duplicate tier note for scope {key[0]} tier {key[1]}.")

    # Freshness warning
    cutoff_dt = _parse_datetime(meta.get("research_cutoff"))
    draft_dt = _parse_datetime(draft.get("date"))
    if cutoff_dt and draft_dt:
        days = (draft_dt - cutoff_dt).total_seconds() / 86400
        if days < 0:
            warnings.append("research_cutoff occurs after the draft date.")
        elif days <= 7:
            pass
        elif days <= 30:
            warnings.append(f"Research cutoff is {days:.0f} days before the draft; refresh injuries and ADP closer to draft day.")
        else:
            warnings.append(f"Research cutoff is {days:.0f} days before the draft and is likely stale.")

    if strict:
        if players and not sources:
            errors.append("Strict mode requires at least one source when players are present.")
        if players and not cutoff_dt:
            errors.append("Strict mode requires meta.research_cutoff when players are present.")
        if not players:
            warnings.append("No players are present. The file is a valid scaffold, not a usable cheat sheet.")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an RFFL cheat-sheet JSON file.")
    parser.add_argument("source", type=Path)
    parser.add_argument("--strict", action="store_true", help="Treat missing research metadata as errors.")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Print machine-readable results.")
    args = parser.parse_args()

    try:
        with args.source.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        print(f"ERROR: file not found: {args.source}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON: {exc}", file=sys.stderr)
        return 2

    errors, warnings = validate_data(data, strict=args.strict)

    if args.json_output:
        print(json.dumps({"valid": not errors, "errors": errors, "warnings": warnings}, indent=2))
    else:
        for warning in warnings:
            print(f"WARNING: {warning}")
        for error in errors:
            print(f"ERROR: {error}")
        if not errors:
            print(f"VALID: {args.source} ({len(warnings)} warning(s))")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
