# Output Contract

## Source of truth

The canonical artifact is a JSON file that conforms to `schemas/cheat-sheet.schema.json`.

Do not hand-edit the rendered PDF. Every update must modify the JSON and regenerate the PDF.

## Required artifacts

For each completed version, produce:

```text
<base>.json
<base>.pdf
<base>.manifest.json
<base>-changes.md        # required for update, refresh, or variant
```

Recommended base name:

```text
rffl-cheat-sheet--<team-or-general>--<season>--<scoring>--v<version>--<YYYYMMDD>
```

## PDF structure

The renderer is dynamic. It must paginate instead of enforcing fixed player counts.

```text
Position pages
-> one or more columns per position
-> tier headers consume their own row
-> continuation columns/pages when needed

Overall pages
-> cross-position draft order
-> explicit overall tier headers
-> continuation pages when needed

Optional strategy page
-> targets
-> values/fallers
-> avoids/price caps
-> live draft rules
-> keepers and unavailable players
```

The strategy page is optional. It must never reduce the capacity of the core player boards.

## Position rules

- FLEX is not a player position.
- Superflex changes the overall board but is not a player position.
- Add IDP boards only when the league uses them.
- Exclude keepers and unavailable players from live boards by default.
- Include a player in each eligible position board only when the league or data provider recognizes that eligibility.

## Draft-format columns

### Snake, linear, or third-round reversal

Use rank, player, NFL team, bye when space permits, and ADP.

### Salary cap

Use rank, player, NFL team, AAV, target price, and hard maximum price. Round-window advice becomes price-band advice.

## Notes and tags

- Keep notes short and decision-relevant.
- Use no more than three tags per player.
- Recommended tags: `TARGET`, `VALUE`, `SLEEPER`, `UPSIDE`, `SAFE`, `HANDCUFF`, `INJURY`, `VOLATILE`, `AVOID`, `KEEPER`, `UNAVAILABLE`.
- Do not rely on color alone. Text labels remain authoritative.

## Brand rules

- Prefer approved RFFL repository tokens and logo assets.
- The bundled token file is a fallback.
- Never trace or recreate a logo from a screenshot.
- Do not bundle or redistribute font files.
- Use readable system-font fallbacks when approved fonts are unavailable.
- Preserve the RFFL dark, compact, data-first visual language.

## Capacity rules

- Minimum body text target: approximately 5 points in dense tables.
- Do not shrink below the renderer's legibility floor.
- Add pages when player count or tier rows exceed capacity.
- Keep tier headers with at least one player row when possible.
- Mark a tier as `(CONT.)` when it spans a column or page.

## Manifest

The renderer writes a manifest containing:

- source JSON path and SHA-256
- output PDF path and SHA-256
- version
- season and scoring
- generated time
- player counts by position
- overall-player count
- tier counts
- validation warnings
- research cutoff
