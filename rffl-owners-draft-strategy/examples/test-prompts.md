# Manual Skill Evaluation Prompts

Use these prompts after installing the skill. A successful run should ask only material questions, separate facts from assumptions, preserve tier logic, and produce JSON plus PDF.

## 1. New basic sheet

```text
/rffl-owners-draft-strategy new
Build a consensus cheat sheet for a 12-team half-PPR snake draft.
```

Expected behavior:

- asks for draft date, slot, rounds, roster, platform, and keepers
- does not ask personal-strategy questions unless the user chooses personalization
- researches half-PPR data rather than PPR or non-PPR data

## 2. Keeper branch

```text
Build my keeper cheat sheet. We have 16 rounds and two keepers, but I still need the board to show all 16 rounds.
```

Expected behavior:

- distinguishes board rounds from live selections
- asks for each keeper and cost
- removes unavailable keepers from live targets

## 3. Scoring correction

```text
Make me a standard league sheet. Receptions score 0.5 and tight ends score 1.0 per catch.
```

Expected behavior:

- corrects the terminology to half-PPR with TE premium
- uses the exact scoring instead of the word "standard"

## 4. Superflex branch

```text
Create a 14-team PPR Superflex board with six-point passing touchdowns.
```

Expected behavior:

- asks QB roster-limit and starting-slot questions
- does not reuse one-QB overall ranks
- creates QB tiers that reflect scarcity

## 5. Salary-cap branch

```text
Make an auction version of my current sheet with a $200 budget.
```

Expected behavior:

- treats the canonical term as salary cap
- asks for minimum bid and keeper salaries
- renders AAV, target price, and hard maximum price

## 6. Data refresh with locks

```text
/rffl-owners-draft-strategy refresh output/my-team.json
Refresh current ADP and injuries. Do not change my locked top 25 or my target tags.
```

Expected behavior:

- reads the file first
- updates stale facts only
- preserves locked fields
- creates a patch version and change summary

## 7. Variant

```text
Save a non-PPR variant of this half-PPR sheet without overwriting it.
```

Expected behavior:

- creates a separate source and PDF
- records parent version
- rebuilds ranks and tiers for non-PPR rather than changing only the label

## 8. Capacity and tier test

```text
Include 70 wide receivers, 70 running backs, 40 quarterbacks, 40 tight ends, 24 defenses, and 24 kickers. Do not reduce the font to fit.
```

Expected behavior:

- creates continuation columns and pages
- keeps tier headers visible
- does not cap the player pool at the visual reference's placeholder counts

## 9. Update from PDF only

```text
Update this cheat sheet PDF. I do not have the JSON source.
```

Expected behavior:

- treats the PDF as a reference
- creates a new JSON source
- labels uncertain imported fields
- does not pretend the PDF is safely editable source data

## 10. Pure consensus

```text
I do not want personalized strategy. Just produce a clean consensus board with tiers.
```

Expected behavior:

- skips preference grilling
- still asks material league questions
- omits the strategy page when empty
