# Update, Locking, and Versioning

## Update types

### Refresh

Time-sensitive data changes while league settings and strategy remain stable.

Examples:

- ADP update
- ECR update
- injury or depth-chart change
- team transaction
- final keeper availability change

Default version bump: patch.

### Strategy update

The Owner changes rankings, tiers, targets, avoids, or draft rules.

Default version bump: minor.

### League or schema update

Scoring, roster structure, draft format, keeper model, schema, or renderer contract changes.

Default version bump: major.

### Variant

Create a separate branch of the source for another scoring format, draft slot, platform, or strategy. Set `meta.parent_version` and explain the branch in history.

## Locked fields

Each player can define `locked_fields`, for example:

```json
"locked_fields": ["overall_rank", "overall_tier", "tags", "note"]
```

During refresh:

1. import new factual data
2. preserve locked values
3. recalculate only affected unlocked ranks and tiers
4. report any conflict between a lock and current facts

A lock does not permit a false factual statement. Example: a locked target who is ruled out for the season must be marked unavailable, and the conflict must be shown to the user.

## History entry

Append one entry per saved version:

```json
{
  "version": "0.2.1",
  "created_at": "2026-08-26T18:00:00-05:00",
  "change_type": "refresh",
  "summary": "Updated platform ADP and two injury statuses.",
  "parent_version": "0.2.0"
}
```

## File safety

- Save a new version by default.
- Never overwrite the only source file.
- Keep the prior PDF and JSON together.
- Use deterministic filenames.
- Write a change summary that lists material rank, tier, availability, and setting changes.

## Change summary format

```markdown
# Cheat Sheet Changes

## Data refreshed
- ...

## Rankings or tiers changed
- ...

## Preserved locks
- ...

## New warnings or unknowns
- ...
```

## Update validation

Before rendering:

- compare league settings with the prior source
- verify keeper and unavailable changes
- verify locked fields
- check duplicate or missing ranks
- check that tier numbers never move backward as rank increases
- verify source dates and research cutoff
- run the validator in strict mode
