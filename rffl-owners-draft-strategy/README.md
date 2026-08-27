# rffl-owners-draft-strategy

A Claude Code skill for creating, researching, updating, versioning, and rendering RFFL-branded fantasy football draft cheat sheets.

## What this bundle does

The skill interviews an Owner for league settings and draft preferences, researches current scoring-specific player data, creates positional and overall tiers, and produces a versioned PDF from a canonical JSON source.

The bundle supports:

- non-PPR, half-PPR, PPR, TE-premium, and custom scoring
- snake, linear, third-round-reversal, and salary-cap drafts
- redraft, keeper, dynasty startup, rookie-only, and best-ball contexts
- one-QB, Superflex/2QB, FLEX, DST, K, and IDP position sets
- platform-specific or consensus ADP
- keepers, traded picks, unavailable players, and manual locks
- new sheets, updates, live-data refreshes, and saved variants
- dynamic player counts and continuation pages
- uneven tiers based on meaningful value cliffs

## Install in one project

Copy the entire `rffl-owners-draft-strategy` folder to:

```text
<project>/.claude/skills/rffl-owners-draft-strategy/
```

## Install for all projects

Copy the folder to:

```text
~/.claude/skills/rffl-owners-draft-strategy/
```

Install the renderer dependency:

```bash
python3 -m pip install -r ~/.claude/skills/rffl-owners-draft-strategy/requirements.txt
```

For a project install, use the equivalent path inside `.claude/skills/`.

## Invoke

```text
/rffl-owners-draft-strategy new
/rffl-owners-draft-strategy update path/to/team-cheat-sheet.json
/rffl-owners-draft-strategy refresh path/to/team-cheat-sheet.json
/rffl-owners-draft-strategy variant path/to/team-cheat-sheet.json
```

Plain-language requests can also trigger the skill, such as:

```text
Build my 12-team half-PPR keeper cheat sheet.
Refresh my ADP and injury data without changing my locked tiers.
Save a non-PPR variant for the same draft slot.
```

## Canonical workflow

```text
League and Owner intake
-> current research
-> source JSON
-> validation
-> PDF render
-> visual check
-> versioned archive
```

The JSON is authoritative. The PDF is regenerated from it. Do not hand-edit the PDF.

## Quick technical test

From the skill folder:

```bash
bash scripts/smoke_test.sh
```

This validates the sample source, renders a stress-test PDF, and writes a manifest.

## Core commands

Create a blank source:

```bash
python3 scripts/scaffold_cheat_sheet.py \
  --output work/my-team.json \
  --season 2026 \
  --teams 12 \
  --scoring half_ppr \
  --draft-type snake \
  --rounds 16
```

Validate:

```bash
python3 scripts/validate_cheat_sheet.py work/my-team.json --strict
```

Render:

```bash
python3 scripts/render_cheat_sheet.py \
  work/my-team.json \
  --output output/my-team-v0.1.0.pdf
```

Create a version bump:

```bash
python3 scripts/bump_version.py \
  work/my-team.json \
  --part patch \
  --summary "Refreshed ADP and injury status"
```

## Files

```text
rffl-owners-draft-strategy/
├── SKILL.md
├── README.md
├── CHANGELOG.md
├── requirements.txt
├── assets/
├── references/
├── schemas/
├── scripts/
└── examples/
```

## Output naming

Recommended pattern:

```text
rffl-cheat-sheet--<team-or-general>--<season>--<scoring>--v<version>--<YYYYMMDD>.pdf
```

Use `general` when the sheet is not personalized to one Team.

## Draft-app import boundary

Until the RFFL Draft app defines a structured import contract, treat the generated PDF as the upload artifact and the JSON as the editable source of truth. When the app exposes an import schema, update the renderer contract rather than creating a second competing data model.
