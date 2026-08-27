#!/usr/bin/env python3
"""Render a dynamic RFFL fantasy-football cheat sheet from canonical JSON."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

try:
    from reportlab.lib.colors import HexColor
    from reportlab.lib.pagesizes import landscape, letter
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfbase.pdfmetrics import stringWidth
    from reportlab.pdfgen import canvas
except ImportError as exc:  # pragma: no cover
    raise SystemExit("reportlab is required. Run: python3 -m pip install -r requirements.txt") from exc

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))
from validate_cheat_sheet import validate_data  # noqa: E402

PAGE_W, PAGE_H = landscape(letter)
MARGIN = 26
HEADER_BOTTOM = PAGE_H - 52
CONTENT_BOTTOM = 55
CONTENT_TOP = HEADER_BOTTOM - 13
CONTENT_H = CONTENT_TOP - CONTENT_BOTTOM

DEFAULT_TOKENS = {
    "colors": {
        "background": "#141312",
        "panel": "#1B1C1A",
        "panel_alt": "#202321",
        "ink": "#FBFAF5",
        "soft_ink": "#E8E6DC",
        "muted": "#98978E",
        "accent": "#8FBCC6",
        "accent_2": "#71889A",
        "grid": "#343936",
        "tier": "#2B3333",
        "warning": "#CDAA7D",
        "danger": "#C98686"
    },
    "typography": {
        "font_regular": "Helvetica",
        "font_bold": "Helvetica-Bold",
        "font_wordmark": "Helvetica-BoldOblique"
    }
}

POSITION_DEFAULT_ORDER = ["WR", "RB", "QB", "TE", "DST", "K", "DL", "LB", "DB", "IDP"]
LIVE_AVAILABILITY = {"available", "injured", "suspended"}


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("JSON root must be an object")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def format_scoring(data: dict[str, Any]) -> str:
    scoring = data.get("league", {}).get("scoring", {})
    preset = str(scoring.get("preset", "custom"))
    labels = {
        "non_ppr": "NON-PPR",
        "half_ppr": "HALF-PPR",
        "ppr": "PPR",
        "custom": "CUSTOM"
    }
    label = labels.get(preset, preset.upper())
    te_points = scoring.get("te_reception_points")
    rec_points = scoring.get("reception_points")
    if isinstance(te_points, (int, float)) and isinstance(rec_points, (int, float)) and te_points > rec_points:
        label += " / TE PREMIUM"
    return label


def short_date(value: Any) -> str:
    if not isinstance(value, str) or not value:
        return "-"
    text = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text).strftime("%Y-%m-%d")
    except ValueError:
        return value[:10]


def compact_number(value: Any, digits: int = 1) -> str:
    if value is None:
        return "-"
    if isinstance(value, bool):
        return "-"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return f"{value:.{digits}f}".rstrip("0").rstrip(".")
    return str(value)


def safe_text(value: Any) -> str:
    text = "" if value is None else str(value)
    return text.replace("\u2013", "-").replace("\u2014", "-").replace("\u2022", "-")


def player_marker(player: dict[str, Any]) -> str:
    tags = {str(tag).upper() for tag in player.get("tags", []) if isinstance(tag, str)}
    availability = player.get("availability")
    if availability == "injured" or "INJURY" in tags:
        return "!"
    if "TARGET" in tags:
        return "+"
    if "AVOID" in tags:
        return "x"
    if "VALUE" in tags:
        return "v"
    return ""


def build_tier_note_map(data: dict[str, Any]) -> dict[tuple[str, int], dict[str, Any]]:
    result: dict[tuple[str, int], dict[str, Any]] = {}
    for raw in data.get("tier_notes", []) or []:
        if not isinstance(raw, dict):
            continue
        scope = str(raw.get("scope", "")).upper()
        tier = raw.get("tier")
        if scope and isinstance(tier, int):
            result[(scope, tier)] = raw
    return result


def line_rows(
    players: list[dict[str, Any]],
    tier_getter,
    max_lines: int
) -> list[list[tuple[str, Any, bool]]]:
    """Split players into row chunks. Each tier header consumes one line."""
    chunks: list[list[tuple[str, Any, bool]]] = []
    current: list[tuple[str, Any, bool]] = []
    current_lines = 0
    previous_tier: int | None = None

    for player in players:
        tier = tier_getter(player)
        if not isinstance(tier, int):
            tier = 999
        needs_header = tier != previous_tier
        required = 1 + (1 if needs_header else 0)

        if current and current_lines + required > max_lines:
            chunks.append(current)
            current = []
            current_lines = 0
            # A new chunk always opens with a tier header. It may be a continuation.
            current.append(("tier", tier, tier == previous_tier))
            current_lines += 1
        elif needs_header:
            current.append(("tier", tier, False))
            current_lines += 1

        current.append(("player", player, False))
        current_lines += 1
        previous_tier = tier

    if current:
        chunks.append(current)
    return chunks


class Renderer:
    def __init__(
        self,
        data: dict[str, Any],
        output: Path,
        tokens: dict[str, Any],
        logo: Path | None,
        validation_warnings: list[str]
    ) -> None:
        self.data = data
        self.output = output
        self.tokens = tokens
        self.colors = tokens["colors"]
        self.fonts = tokens.get("typography", {})
        self.font_regular = self.fonts.get("font_regular", "Helvetica")
        self.font_bold = self.fonts.get("font_bold", "Helvetica-Bold")
        self.font_wordmark = self.fonts.get("font_wordmark", "Helvetica-BoldOblique")
        self.logo = logo
        self.validation_warnings = validation_warnings
        self.c = canvas.Canvas(str(output), pagesize=(PAGE_W, PAGE_H))
        self.page_no = 0
        self.tier_notes = build_tier_note_map(data)
        self.player_lookup = {p.get("id"): p for p in data.get("players", []) if isinstance(p, dict)}

    def color(self, name: str) -> HexColor:
        return HexColor(self.colors[name])

    def text(self, x: float, y: float, value: Any, size: float = 6, font: str | None = None,
             color: str = "ink", align: str = "left") -> None:
        self.c.setFont(font or self.font_regular, size)
        self.c.setFillColor(self.color(color))
        value = safe_text(value)
        if align == "right":
            self.c.drawRightString(x, y, value)
        elif align == "center":
            self.c.drawCentredString(x, y, value)
        else:
            self.c.drawString(x, y, value)

    def fit_size(self, value: str, max_width: float, size: float, font: str | None = None, floor: float = 4.3) -> float:
        font_name = font or self.font_regular
        result = size
        while result > floor and stringWidth(safe_text(value), font_name, result) > max_width:
            result -= 0.15
        return result

    def panel(self, x: float, y: float, w: float, h: float, fill: str = "panel", radius: float = 5) -> None:
        self.c.setFillColor(self.color(fill))
        self.c.setStrokeColor(self.color("grid"))
        self.c.setLineWidth(0.5)
        self.c.roundRect(x, y, w, h, radius, fill=1, stroke=1)

    def titlebar(self, x: float, y: float, w: float, title: str) -> None:
        self.c.setFillColor(self.color("accent_2"))
        self.c.roundRect(x, y, w, 14, 3, fill=1, stroke=0)
        self.text(x + w / 2, y + 4.1, title, 7.0, self.font_bold, "ink", "center")

    def page_header(self, subtitle: str) -> None:
        self.page_no += 1
        self.c.setFillColor(self.color("background"))
        self.c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

        if self.logo and self.logo.exists():
            try:
                image = ImageReader(str(self.logo))
                self.c.drawImage(image, MARGIN, PAGE_H - 45, width=52, height=24, preserveAspectRatio=True, mask="auto")
                title_x = MARGIN + 62
            except Exception:
                self.text(MARGIN, PAGE_H - 29, "RFFL", 18, self.font_wordmark, "soft_ink")
                title_x = MARGIN + 55
        else:
            self.text(MARGIN, PAGE_H - 29, "RFFL", 18, self.font_wordmark, "soft_ink")
            title_x = MARGIN + 55

        meta = self.data.get("meta", {})
        team = self.data.get("team", {})
        league = self.data.get("league", {})
        draft = league.get("draft", {})
        team_label = safe_text(team.get("name") or "GENERAL TEMPLATE")
        if team.get("abbr"):
            team_label += f" / {safe_text(team.get('abbr'))}"

        self.text(title_x, PAGE_H - 27, "DRAFT CHEAT SHEET", 15, self.font_bold, "ink")
        self.text(title_x, PAGE_H - 42, subtitle, 7, self.font_bold, "accent")
        self.text(PAGE_W - MARGIN, PAGE_H - 27, team_label.upper(), 7, self.font_bold, "soft_ink", "right")
        details = f"{format_scoring(self.data)} / {league.get('teams', '-')} TEAMS / V{meta.get('version', '-')}"
        if draft.get("slot"):
            details += f" / SLOT {draft.get('slot')}"
        elif draft.get("budget"):
            details += f" / BUDGET {compact_number(draft.get('budget'), 0)}"
        self.text(PAGE_W - MARGIN, PAGE_H - 42, details, 5.9, self.font_regular, "muted", "right")
        self.c.setStrokeColor(self.color("accent"))
        self.c.setLineWidth(1.1)
        self.c.line(MARGIN, HEADER_BOTTOM, PAGE_W - MARGIN, HEADER_BOTTOM)

    def page_footer(self, left: str, right: str = "") -> None:
        meta = self.data.get("meta", {})
        cutoff = short_date(meta.get("research_cutoff"))
        footer_left = f"PAGE {self.page_no} / {left} / RESEARCH {cutoff}"
        self.text(MARGIN, 18, footer_left, 5.1, self.font_bold, "muted")
        if right:
            self.text(PAGE_W - MARGIN, 18, right, 5.1, self.font_regular, "muted", "right")
        self.c.showPage()

    def live_players(self) -> list[dict[str, Any]]:
        include_unavailable = bool(self.data.get("display", {}).get("include_unavailable_on_board"))
        result = []
        for player in self.data.get("players", []) or []:
            if not isinstance(player, dict):
                continue
            if include_unavailable or player.get("availability") in LIVE_AVAILABILITY:
                result.append(player)
        return result

    def position_order(self, positions: Iterable[str]) -> list[str]:
        configured = self.data.get("display", {}).get("position_order") or POSITION_DEFAULT_ORDER
        configured = [str(pos).upper() for pos in configured]
        extras = sorted({str(pos).upper() for pos in positions} - set(configured))
        return [pos for pos in configured if pos in positions] + extras

    def position_blocks(self) -> list[dict[str, Any]]:
        groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for player in self.live_players():
            ranks = player.get("position_rank") or {}
            if not isinstance(ranks, dict):
                continue
            for position, rank in ranks.items():
                if isinstance(rank, int):
                    groups[str(position).upper()].append(player)

        blocks: list[dict[str, Any]] = []
        for position in self.position_order(groups.keys()):
            players = sorted(groups[position], key=lambda p: (p.get("position_rank", {}).get(position, 9999), p.get("name", "")))
            chunks = line_rows(players, lambda p, pos=position: p.get("position_tier", {}).get(pos), max_lines=53)
            for chunk in chunks:
                ranks = [row[1].get("position_rank", {}).get(position) for row in chunk if row[0] == "player"]
                ranks = [r for r in ranks if isinstance(r, int)]
                title = position
                if ranks:
                    title += f" {min(ranks)}-{max(ranks)}"
                blocks.append({"position": position, "title": title, "rows": chunk})
        return blocks

    def draw_position_block(self, x: float, y: float, w: float, h: float, block: dict[str, Any]) -> None:
        self.panel(x, y, w, h)
        self.titlebar(x, y + h - 14, w, block["title"])
        top = y + h - 28
        self.c.setFillColor(self.color("panel_alt"))
        self.c.rect(x + 4, top - 1, w - 8, 10, fill=1, stroke=0)

        draft_type = self.data.get("league", {}).get("draft", {}).get("type")
        salary = draft_type == "salary_cap"
        if salary:
            headers = ["RK", "PLAYER", "TM", "AAV", "MAX"]
            col_x = [x + 6, x + 27, x + w - 65, x + w - 42, x + w - 18]
        else:
            label = safe_text(self.data.get("display", {}).get("adp_label") or "ADP")
            headers = ["RK", "PLAYER", "TM", label]
            col_x = [x + 6, x + 27, x + w - 43, x + w - 18]
        for px, header in zip(col_x, headers):
            self.text(px, top + 1, header, 5.0, self.font_bold, "muted")

        rows = block["rows"]
        row_h = min(8.5, max(6.6, (h - 42) / max(len(rows), 1)))
        yy = top - 8
        position = block["position"]

        for kind, value, continued in rows:
            if kind == "tier":
                tier = int(value)
                self.c.setFillColor(self.color("tier"))
                self.c.rect(x + 4, yy - 2, w - 8, row_h + 1, fill=1, stroke=0)
                label = f"TIER {tier}" + (" (CONT.)" if continued else "")
                self.text(x + 7, yy + 0.2, label, 4.7, self.font_bold, "accent")
                note = self.tier_notes.get((position.upper(), tier), {})
                note_text = note.get("label") or note.get("note") or ""
                if note_text:
                    size = self.fit_size(safe_text(note_text), w - 72, 4.4, self.font_regular, 3.9)
                    self.text(x + w - 7, yy + 0.2, note_text, size, self.font_regular, "muted", "right")
            else:
                player = value
                rank = player.get("position_rank", {}).get(position, "-")
                marker = player_marker(player)
                name = f"{marker} {player.get('name', '')}".strip()
                self.c.setStrokeColor(self.color("grid"))
                self.c.setLineWidth(0.22)
                self.c.line(x + 5, yy - 2, x + w - 5, yy - 2)
                self.text(col_x[0], yy, rank, 4.8, self.font_bold, "muted")
                name_width = (col_x[2] - col_x[1] - 4) if salary else (col_x[2] - col_x[1] - 4)
                name_size = self.fit_size(name, name_width, 5.1, self.font_bold)
                name_color = "warning" if marker == "!" else "ink"
                self.text(col_x[1], yy, name, name_size, self.font_bold, name_color)
                self.text(col_x[2], yy, player.get("nfl_team") or "-", 4.5, self.font_regular, "soft_ink")
                if salary:
                    auction = player.get("auction") or {}
                    self.text(col_x[3], yy, compact_number(auction.get("aav")), 4.5, self.font_regular, "accent")
                    self.text(col_x[4], yy, compact_number(auction.get("max_bid")), 4.5, self.font_bold, "accent")
                else:
                    adp = (player.get("adp") or {}).get("value")
                    self.text(col_x[3], yy, compact_number(adp), 4.5, self.font_regular, "accent")
            yy -= row_h

    def render_position_pages(self) -> None:
        blocks = self.position_blocks()
        if not blocks:
            return
        gap = 8
        col_w = (PAGE_W - 2 * MARGIN - 3 * gap) / 4
        for start in range(0, len(blocks), 4):
            page_blocks = blocks[start:start + 4]
            self.page_header("POSITIONAL BOARD / TIER-BASED / PLAYER-POOL FIRST")
            for index, block in enumerate(page_blocks):
                x = MARGIN + index * (col_w + gap)
                self.draw_position_block(x, CONTENT_BOTTOM, col_w, CONTENT_H, block)
            # Use spare columns for rules and league details rather than shrinking data.
            spare = 4 - len(page_blocks)
            if spare:
                for offset in range(spare):
                    index = len(page_blocks) + offset
                    x = MARGIN + index * (col_w + gap)
                    self.draw_info_panel(x, CONTENT_BOTTOM, col_w, CONTENT_H, offset)
            self.page_footer("POSITIONAL BOARD", "Continuation pages are created automatically.")

    def draw_info_panel(self, x: float, y: float, w: float, h: float, variant: int = 0) -> None:
        self.panel(x, y, w, h)
        title = "TIER LOGIC" if variant % 2 == 0 else "LEAGUE SETTINGS"
        self.titlebar(x, y + h - 14, w, title)
        yy = y + h - 34
        if title == "TIER LOGIC":
            lines = [
                "Tier = similar draft value.",
                "New tier = meaningful value drop.",
                "Do not force equal tier sizes.",
                "ADP is market reference, not rank.",
                "Use notes only for material cliffs.",
                "Add pages instead of shrinking type."
            ]
        else:
            league = self.data.get("league", {})
            draft = league.get("draft", {})
            roster = league.get("roster", []) or []
            roster_text = ", ".join(f"{row.get('slot')}x{row.get('count')}" for row in roster if isinstance(row, dict) and row.get("count"))
            lines = [
                f"League: {league.get('name', '-')}",
                f"Format: {league.get('format', '-')}",
                f"Scoring: {format_scoring(self.data)}",
                f"Teams: {league.get('teams', '-')}",
                f"Draft: {draft.get('type', '-')} / {draft.get('rounds', '-')} rounds",
                f"Platform: {draft.get('platform') or '-'}",
                f"Roster: {roster_text or '-'}"
            ]
        for line in lines:
            self.text(x + 8, yy, f"- {line}", 5.3, self.font_regular, "soft_ink")
            yy -= 14

    def overall_blocks(self) -> list[dict[str, Any]]:
        players = [p for p in self.live_players() if isinstance(p.get("overall_rank"), int)]
        players.sort(key=lambda p: (p.get("overall_rank", 9999), p.get("name", "")))
        chunks = line_rows(players, lambda p: p.get("overall_tier"), max_lines=65)
        blocks = []
        for chunk in chunks:
            ranks = [row[1].get("overall_rank") for row in chunk if row[0] == "player"]
            ranks = [r for r in ranks if isinstance(r, int)]
            title = "OVERALL"
            if ranks:
                title += f" {min(ranks)}-{max(ranks)}"
            blocks.append({"title": title, "rows": chunk})
        return blocks

    def draw_overall_block(self, x: float, y: float, w: float, h: float, block: dict[str, Any]) -> None:
        self.panel(x, y, w, h)
        self.titlebar(x, y + h - 14, w, block["title"])
        top = y + h - 28
        self.c.setFillColor(self.color("panel_alt"))
        self.c.rect(x + 4, top - 1, w - 8, 10, fill=1, stroke=0)

        salary = self.data.get("league", {}).get("draft", {}).get("type") == "salary_cap"
        if salary:
            headers = ["RK", "PLAYER", "POS", "TM", "AAV", "MAX"]
            col_x = [x + 6, x + 29, x + w - 96, x + w - 69, x + w - 42, x + w - 17]
        else:
            label = safe_text(self.data.get("display", {}).get("adp_label") or "ADP")
            headers = ["RK", "PLAYER", "POS", "TM", label]
            col_x = [x + 6, x + 29, x + w - 72, x + w - 43, x + w - 18]
        for px, header in zip(col_x, headers):
            self.text(px, top + 1, header, 5.0, self.font_bold, "muted")

        rows = block["rows"]
        row_h = min(8.0, max(6.1, (h - 42) / max(len(rows), 1)))
        yy = top - 8
        for kind, value, continued in rows:
            if kind == "tier":
                tier = int(value)
                self.c.setFillColor(self.color("tier"))
                self.c.rect(x + 4, yy - 2, w - 8, row_h + 1, fill=1, stroke=0)
                label = f"TIER {tier}" + (" (CONT.)" if continued else "")
                self.text(x + 7, yy + 0.2, label, 4.7, self.font_bold, "accent")
                note = self.tier_notes.get(("OVERALL", tier), {})
                note_text = note.get("label") or note.get("note") or ""
                if note_text:
                    self.text(x + w - 7, yy + 0.2, note_text, self.fit_size(note_text, w - 75, 4.3), self.font_regular, "muted", "right")
            else:
                player = value
                marker = player_marker(player)
                name = f"{marker} {player.get('name', '')}".strip()
                self.c.setStrokeColor(self.color("grid"))
                self.c.setLineWidth(0.22)
                self.c.line(x + 5, yy - 2, x + w - 5, yy - 2)
                self.text(col_x[0], yy, player.get("overall_rank"), 4.8, self.font_bold, "muted")
                name_width = col_x[2] - col_x[1] - 4
                self.text(col_x[1], yy, name, self.fit_size(name, name_width, 5.0, self.font_bold), self.font_bold, "ink")
                self.text(col_x[2], yy, player.get("primary_position") or "-", 4.4, self.font_regular, "soft_ink")
                self.text(col_x[3], yy, player.get("nfl_team") or "-", 4.4, self.font_regular, "soft_ink")
                if salary:
                    auction = player.get("auction") or {}
                    self.text(col_x[4], yy, compact_number(auction.get("aav")), 4.4, self.font_regular, "accent")
                    self.text(col_x[5], yy, compact_number(auction.get("max_bid")), 4.4, self.font_bold, "accent")
                else:
                    self.text(col_x[4], yy, compact_number((player.get("adp") or {}).get("value")), 4.4, self.font_regular, "accent")
            yy -= row_h

    def render_overall_pages(self) -> None:
        if not self.data.get("display", {}).get("include_overall_board", True):
            return
        blocks = self.overall_blocks()
        if not blocks:
            return
        gap = 10
        col_w = (PAGE_W - 2 * MARGIN - 2 * gap) / 3
        for start in range(0, len(blocks), 3):
            page_blocks = blocks[start:start + 3]
            self.page_header("OVERALL DRAFT BOARD / CROSS-POSITION VALUE / TIER CLIFFS")
            for index, block in enumerate(page_blocks):
                x = MARGIN + index * (col_w + gap)
                self.draw_overall_block(x, CONTENT_BOTTOM, col_w, CONTENT_H, block)
            self.page_footer("OVERALL BOARD", "FLEX is a roster slot, not a player position.")

    def strategy_blocks(self) -> list[dict[str, Any]]:
        strategy = self.data.get("strategy", {}) or {}
        blocks: list[dict[str, Any]] = []

        def player_items(section: str, title: str) -> None:
            items = strategy.get(section, []) or []
            rows = []
            for item in items:
                if not isinstance(item, dict):
                    continue
                player = self.player_lookup.get(item.get("player_id"), {})
                rows.append({
                    "name": player.get("name") or item.get("player_id") or "-",
                    "position": player.get("primary_position") or "-",
                    "window": item.get("window") or "-",
                    "reason": item.get("reason") or player.get("note") or "-",
                    "price_cap": item.get("price_cap")
                })
            for start in range(0, len(rows), 10):
                suffix = "" if start == 0 else " (CONT.)"
                blocks.append({"kind": "players", "title": title + suffix, "rows": rows[start:start + 10]})

        player_items("targets", "DRAFT TARGETS")
        player_items("values", "VALUES / FALLERS")
        player_items("avoids", "AVOIDS / PRICE CAPS")

        rules = [safe_text(rule) for rule in strategy.get("rules", []) or [] if safe_text(rule)]
        for start in range(0, len(rules), 10):
            suffix = "" if start == 0 else " (CONT.)"
            blocks.append({"kind": "rules", "title": "LIVE DRAFT RULES" + suffix, "rows": rules[start:start + 10]})

        unavailable = []
        for player in self.data.get("players", []) or []:
            if isinstance(player, dict) and player.get("availability") not in LIVE_AVAILABILITY:
                unavailable.append({
                    "name": player.get("name") or "-",
                    "position": player.get("primary_position") or "-",
                    "status": str(player.get("availability") or "-").upper(),
                    "owner": player.get("owner_team") or "-"
                })
        for start in range(0, len(unavailable), 10):
            suffix = "" if start == 0 else " (CONT.)"
            blocks.append({"kind": "unavailable", "title": "KEEPERS / UNAVAILABLE" + suffix, "rows": unavailable[start:start + 10]})

        if self.validation_warnings:
            for start in range(0, len(self.validation_warnings), 10):
                suffix = "" if start == 0 else " (CONT.)"
                blocks.append({"kind": "rules", "title": "VALIDATION WARNINGS" + suffix, "rows": self.validation_warnings[start:start + 10]})
        return blocks

    def draw_strategy_block(self, x: float, y: float, w: float, h: float, block: dict[str, Any]) -> None:
        self.panel(x, y, w, h)
        self.titlebar(x, y + h - 14, w, block["title"])
        top = y + h - 29
        kind = block["kind"]
        rows = block["rows"]

        if kind == "players":
            self.c.setFillColor(self.color("panel_alt"))
            self.c.rect(x + 4, top - 1, w - 8, 10, fill=1, stroke=0)
            col_x = [x + 7, x + w - 145, x + w - 115, x + w - 78]
            for px, header in zip(col_x, ["PLAYER", "POS", "WINDOW", "REASON"]):
                self.text(px, top + 1, header, 5.0, self.font_bold, "muted")
            yy = top - 9
            row_h = min(15.5, max(9.0, (h - 43) / max(len(rows), 1)))
            for row in rows:
                self.c.setStrokeColor(self.color("grid"))
                self.c.setLineWidth(0.25)
                self.c.line(x + 5, yy - 2, x + w - 5, yy - 2)
                name = safe_text(row.get("name"))
                self.text(col_x[0], yy, name, self.fit_size(name, col_x[1] - col_x[0] - 5, 5.5, self.font_bold), self.font_bold, "ink")
                self.text(col_x[1], yy, row.get("position"), 5.0, self.font_regular, "soft_ink")
                window = row.get("window")
                if row.get("price_cap") is not None:
                    window = f"MAX {compact_number(row.get('price_cap'))}"
                self.text(col_x[2], yy, window, 5.0, self.font_bold, "accent")
                reason = safe_text(row.get("reason"))
                self.text(col_x[3], yy, reason, self.fit_size(reason, x + w - 8 - col_x[3], 4.8), self.font_regular, "soft_ink")
                yy -= row_h
        elif kind == "unavailable":
            self.c.setFillColor(self.color("panel_alt"))
            self.c.rect(x + 4, top - 1, w - 8, 10, fill=1, stroke=0)
            col_x = [x + 7, x + w - 120, x + w - 88, x + w - 45]
            for px, header in zip(col_x, ["PLAYER", "POS", "STATUS", "OWNER"]):
                self.text(px, top + 1, header, 5.0, self.font_bold, "muted")
            yy = top - 9
            row_h = min(15.5, max(9.0, (h - 43) / max(len(rows), 1)))
            for row in rows:
                self.c.setStrokeColor(self.color("grid"))
                self.c.line(x + 5, yy - 2, x + w - 5, yy - 2)
                name = safe_text(row.get("name"))
                self.text(col_x[0], yy, name, self.fit_size(name, col_x[1] - col_x[0] - 5, 5.4, self.font_bold), self.font_bold, "ink")
                self.text(col_x[1], yy, row.get("position"), 4.9, self.font_regular, "soft_ink")
                self.text(col_x[2], yy, row.get("status"), 4.8, self.font_bold, "warning")
                self.text(col_x[3], yy, row.get("owner"), 4.8, self.font_regular, "soft_ink")
                yy -= row_h
        else:
            yy = top - 4
            row_h = min(16.0, max(9.0, (h - 35) / max(len(rows), 1)))
            for index, row in enumerate(rows, 1):
                text = safe_text(row)
                self.text(x + 8, yy, f"{index}. {text}", self.fit_size(text, w - 30, 5.5), self.font_regular, "soft_ink")
                yy -= row_h

    def render_strategy_pages(self) -> None:
        if not self.data.get("display", {}).get("include_strategy_page", True):
            return
        blocks = self.strategy_blocks()
        if not blocks:
            return
        gap = 10
        col_w = (PAGE_W - 2 * MARGIN - gap) / 2
        block_h = (CONTENT_H - 2 * gap) / 3
        for start in range(0, len(blocks), 6):
            page_blocks = blocks[start:start + 6]
            self.page_header("OPTIONAL OWNER STRATEGY / TARGETS / VALUES / AVAILABILITY")
            for index, block in enumerate(page_blocks):
                col = index % 2
                row = index // 2
                x = MARGIN + col * (col_w + gap)
                y = CONTENT_TOP - (row + 1) * block_h - row * gap
                self.draw_strategy_block(x, y, col_w, block_h, block)
            self.page_footer("OWNER STRATEGY", "This layer never reduces core player-board capacity.")

    def render(self) -> int:
        self.render_position_pages()
        self.render_overall_pages()
        self.render_strategy_pages()
        if self.page_no == 0:
            self.page_header("EMPTY SCAFFOLD / ADD PLAYERS BEFORE DRAFT USE")
            self.draw_info_panel(MARGIN, CONTENT_BOTTOM, PAGE_W - 2 * MARGIN, CONTENT_H, 0)
            self.page_footer("EMPTY SCAFFOLD")
        self.c.save()
        return self.page_no


def count_position_players(data: dict[str, Any]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    include_unavailable = bool(data.get("display", {}).get("include_unavailable_on_board"))
    for player in data.get("players", []) or []:
        if not isinstance(player, dict):
            continue
        if not include_unavailable and player.get("availability") not in LIVE_AVAILABILITY:
            continue
        for pos, rank in (player.get("position_rank") or {}).items():
            if isinstance(rank, int):
                counts[str(pos).upper()] += 1
    return dict(sorted(counts.items()))


def count_tiers(data: dict[str, Any]) -> dict[str, int]:
    tiers: dict[str, set[int]] = defaultdict(set)
    for player in data.get("players", []) or []:
        if not isinstance(player, dict):
            continue
        if isinstance(player.get("overall_tier"), int):
            tiers["OVERALL"].add(player["overall_tier"])
        for pos, tier in (player.get("position_tier") or {}).items():
            if isinstance(tier, int):
                tiers[str(pos).upper()].add(tier)
    return {scope: len(values) for scope, values in sorted(tiers.items())}


def main() -> int:
    parser = argparse.ArgumentParser(description="Render an RFFL cheat-sheet PDF from JSON.")
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--tokens", type=Path, help="Optional approved brand-token JSON.")
    parser.add_argument("--logo", type=Path, help="Optional approved PNG/JPG RFFL logo.")
    parser.add_argument("--manifest", type=Path, help="Optional manifest path. Defaults beside the PDF.")
    parser.add_argument("--allow-validation-errors", action="store_true", help="Render even when validation finds errors.")
    args = parser.parse_args()

    try:
        data = read_json(args.source)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    errors, warnings = validate_data(data, strict=True)
    if errors and not args.allow_validation_errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print("Rendering stopped. Fix validation errors or use --allow-validation-errors for a diagnostic render.", file=sys.stderr)
        return 1

    token_path = args.tokens or (SKILL_DIR / "assets" / "rffl-brand-tokens.json")
    tokens = DEFAULT_TOKENS
    if token_path.exists():
        try:
            tokens = deep_merge(DEFAULT_TOKENS, read_json(token_path))
        except Exception as exc:
            print(f"WARNING: could not read token file {token_path}: {exc}", file=sys.stderr)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    renderer = Renderer(data, args.output, tokens, args.logo, warnings + errors)
    page_count = renderer.render()

    manifest_path = args.manifest or args.output.with_suffix(".manifest.json")
    manifest = {
        "schema_version": "1.0.0",
        "generated_at": iso_now(),
        "source": {
            "path": str(args.source),
            "sha256": sha256_file(args.source)
        },
        "pdf": {
            "path": str(args.output),
            "sha256": sha256_file(args.output),
            "pages": page_count
        },
        "version": data.get("meta", {}).get("version"),
        "season": data.get("meta", {}).get("season"),
        "scoring": format_scoring(data),
        "team": data.get("team", {}).get("name") or "general",
        "research_cutoff": data.get("meta", {}).get("research_cutoff"),
        "players_by_position": count_position_players(data),
        "overall_player_count": sum(1 for p in data.get("players", []) or [] if isinstance(p, dict) and isinstance(p.get("overall_rank"), int) and (data.get("display", {}).get("include_unavailable_on_board") or p.get("availability") in LIVE_AVAILABILITY)),
        "tier_counts": count_tiers(data),
        "validation": {
            "errors": errors,
            "warnings": warnings
        },
        "token_file": str(token_path),
        "logo_file": str(args.logo) if args.logo else None
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)
        handle.write("\n")

    print(args.output)
    print(manifest_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
