---
name: rffl-owners-draft-strategy
description: Builds, updates, versions, and renders RFFL-branded fantasy football draft cheat sheets. Use when a user wants a new or revised consensus/ADP board, positional tiers, keeper-aware draft plan, personalized Owner strategy, saved variant, or printable/uploadable PDF for an RFFL Team.
when_to_use: Trigger for requests such as "make my draft cheat sheet", "update my rankings", "refresh ADP", "build tiers", "keeper strategy", "make another version", or "prepare a cheat sheet for the draft app".
argument-hint: "[new|update|refresh|variant] [optional source-json]"
user-invocable: true
disable-model-invocation: false
---

# RFFL Owners Draft Strategy

Create and maintain a tier-based fantasy football draft cheat sheet for one RFFL Team. The system must also work as a general template for any Team. The canonical source is JSON. The PDF is a generated artifact.

## Non-negotiable rules

1. Inspect before assuming. Read an existing source JSON, league configuration, keeper list, and approved RFFL brand assets when available.
2. Ask only questions that materially change rankings, tiers, availability, or output.
3. Do not rank from memory when current-season research is required. Use current, scoring-specific sources and record dates.
4. Keep ADP, ECR, projections, and user preference separate:
   - ADP = market behavior.
   - ECR = expert recommendation.
   - Projection = expected production under stated scoring.
   - User rank = the final ordered board after strategy adjustments.
5. A tier is a value-equivalence band. Never create fixed-size tiers.
6. Do not edit the PDF directly. Update the JSON, validate it, then render a new PDF.
7. Preserve user-locked ranks, tiers, tags, and notes during data refreshes.
8. Keepers and unavailable players must not appear as live targets.
9. When data conflicts, show the conflict and make the smallest defensible resolution.
10. Continue onto more pages when the pool grows. Never solve capacity by making text unreadable.

## Determine the task mode

Infer the mode from the request. Ask one orientation question only when the mode is unclear:

- `new`: create a new cheat sheet from league settings and research.
- `update`: change strategy, settings, tiers, players, or notes in an existing sheet.
- `refresh`: update time-sensitive data while preserving strategy and locked fields.
- `variant`: save a separate version for another scoring model, draft slot, platform, or strategy.

If an existing JSON path is supplied, read it before asking questions. If only a PDF exists, treat it as a visual reference and create a new JSON source with any uncertain fields labeled.

## Intake workflow

Before the interview, read [references/intake-playbook.md](references/intake-playbook.md).

### Phase 1: Essential league facts

Collect or verify:

1. Season and draft date.
2. New sheet, update, refresh, or variant.
3. League format: redraft, keeper, dynasty startup, rookie-only, or best ball.
4. Scoring: non-PPR, half-PPR, PPR, TE premium, points-per-first-down, bonuses, and other custom rules.
5. Team count.
6. Draft type: snake, linear, third-round reversal, or salary cap.
7. Draft slot or budget.
8. Number of rounds and exact roster slots.
9. Keepers, keeper costs, traded picks, and other unavailable players.
10. Draft platform or desired ADP source.

Do not begin rankings while a material blocker remains unresolved. Present a compact summary with `Confirmed`, `Assumed`, and `Open` before research.

### Phase 2: Personal strategy

Skip this phase for a pure consensus sheet. For a personalized sheet, ask only the branches that matter:

- risk tolerance and injury tolerance
- preferred early-round roster build
- QB and TE timing
- appetite for rookies and volatile players
- stacking preference
- favorite targets, fades, and excluded players
- bye-week preference
- prior strategy or draft-history evidence

Do not force a declared strategy when the user prefers value-based drafting.

## Research workflow

Before research, read:

- [references/fantasy-football-domain.md](references/fantasy-football-domain.md)
- [references/research-policy.md](references/research-policy.md)

Research the exact format. A PPR board is not a non-PPR board. A one-QB board is not a Superflex board. A salary-cap sheet needs AAV and maximum bids rather than only round-based ADP.

Gather enough current evidence to support:

- player availability and team
- scoring-specific ECR or consensus ranks
- platform-specific or consensus ADP
- projections when useful
- injury, suspension, holdout, and depth-chart changes
- keeper removals and league-specific availability

Record every material source in `sources[]` with publisher, title, URL, updated date when available, and access date.

## Build the board

Before tiering, read [references/tier-logic.md](references/tier-logic.md).

1. Create positional ranks for every enabled position.
2. Create an overall draft board for the relevant format.
3. Assign positional and overall tiers from meaningful value cliffs.
4. Compare the user's rank against ADP. Do not let ADP become the rank by default.
5. Add short notes only when they change a draft decision.
6. Put personalization in the optional strategy layer. Do not reduce core player capacity to make room for prose.
7. Exclude unavailable players from the live board by default. Preserve them in the source and list them in the unavailable/keeper module.

## Output contract

Before writing files, read:

- [references/output-contract.md](references/output-contract.md)
- [references/update-versioning.md](references/update-versioning.md)

Create these artifacts:

1. Canonical source JSON.
2. Versioned RFFL-branded PDF.
3. Render manifest JSON.
4. Change summary Markdown for updates, refreshes, and variants.

Use the bundled scripts:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/validate_cheat_sheet.py" <source.json> --strict
python3 "${CLAUDE_SKILL_DIR}/scripts/render_cheat_sheet.py" <source.json> --output <output.pdf>
```

Optional approved assets:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/render_cheat_sheet.py" <source.json> \
  --output <output.pdf> \
  --tokens <approved-brand-tokens.json> \
  --logo <approved-rffl-logo.png>
```

Use an approved repository logo when available. Never recreate a logo from a screenshot. The bundled token file is a fallback, not a higher authority than the active RFFL design system.

## Update and refresh behavior

1. Read the latest JSON and its history.
2. Identify whether the change is data-only, strategy, league configuration, or schema/layout.
3. Refresh only the stale fields.
4. Reapply `locked_fields` after importing new data.
5. Recalculate affected ranks and tiers. Do not reorder unaffected locked sections.
6. Bump the semantic version:
   - patch: current-data refresh or small note correction
   - minor: strategy, ranks, tiers, or meaningful output change
   - major: league format, schema, or renderer contract change
7. Append a concise history entry.
8. Validate, render, and inspect the result.
9. Save a new version. Do not overwrite the prior version unless the user explicitly requests it.

## Quality gate

Do not call the artifact complete until:

- league scoring and roster match the confirmed settings
- all player ranks are unique in their scope
- tiers are monotonic and evidence-based
- ADP/ECR dates are recorded
- keepers and unavailable players are handled correctly
- no locked field changed without user approval
- the PDF has no clipped or overlapping text
- continuation pages are used when capacity is exceeded
- the PDF and manifest point to the same source version

## Bundled resources

- [README.md](README.md): install and quick-start instructions
- [references/intake-playbook.md](references/intake-playbook.md): adaptive interview and question branches
- [references/fantasy-football-domain.md](references/fantasy-football-domain.md): canonical fantasy-football concepts
- [references/research-policy.md](references/research-policy.md): source hierarchy and freshness rules
- [references/tier-logic.md](references/tier-logic.md): tier method and confidence labels
- [references/output-contract.md](references/output-contract.md): JSON and PDF rules
- [references/update-versioning.md](references/update-versioning.md): update, locking, and versioning workflow
- [schemas/cheat-sheet.schema.json](schemas/cheat-sheet.schema.json): machine-readable schema
- [assets/RFFL-general-tiered-cheat-sheet-template-v2.pdf](assets/RFFL-general-tiered-cheat-sheet-template-v2.pdf): visual reference only
- [assets/rffl-brand-tokens.json](assets/rffl-brand-tokens.json): fallback rendering tokens
- [examples/sample-cheat-sheet.json](examples/sample-cheat-sheet.json): high-capacity sample data
- [examples/test-prompts.md](examples/test-prompts.md): manual evaluation prompts
