# Tier Logic

A tier is a decision tool. Players inside one tier are close enough in draft value that roster construction, risk preference, or ADP can break the tie. A new tier begins after a meaningful value cliff.

## Required properties

- Tier sizes are uneven.
- Tiers are monotonic as ranks increase.
- A tier boundary must have a reason.
- ADP can inform timing but cannot define tiers by itself.
- Positional tiers and overall tiers can differ.
- A player may be in Position Tier 1 but Overall Tier 3.

## Evidence for a tier boundary

Use one or more of these signals:

1. meaningful projection drop
2. consensus-rank gap or clustering break
3. role or workload certainty change
4. positional replacement-value drop
5. injury or suspension risk change
6. scarcity created by league size or roster requirements
7. market-cost jump that changes realistic availability
8. a strategy pivot, such as the end of an elite TE group

## Suggested method

### Step 1: Build the factual order

Create a scoring-specific baseline from current ECR, projections, and role information.

### Step 2: Adjust for the league

Apply league size, roster depth, FLEX/Superflex requirements, keeper removals, and draft format.

### Step 3: Apply the Owner strategy

Use risk, roster-construction, and player preferences as tiebreakers or explicit adjustments. Do not hide the adjustment.

### Step 4: Mark cliffs

For each boundary, record:

- scope: overall or position
- tier number
- label
- short cliff note
- confidence
- evidence references

### Step 5: Validate

Ask:

- Would the user be comfortable taking any player in this tier at roughly the same opportunity cost?
- Does the next tier require a different decision or risk tradeoff?
- Is the boundary still valid after current keeper removals and platform ADP?

## Provisional tiers

When only ADP or one weak source exists, label the method `provisional` and confidence `low` or `medium`. Do not present the tiers as fully researched.

## Tier data example

```json
{
  "scope": "WR",
  "tier": 3,
  "label": "Stable WR2 targets",
  "note": "Target certainty drops after this group.",
  "confidence": "medium",
  "evidence_source_ids": ["fantasypros-ecr-2026-08-26"]
}
```

## Live-draft use

Tier depletion changes urgency:

- many players remain in the tier: wait when the room allows
- one player remains in the tier: consider acting before the cliff
- tier exhausted: pivot rather than reaching backward

Do not state this as an absolute rule. Draft slot, roster needs, and alternative tiers still matter.
