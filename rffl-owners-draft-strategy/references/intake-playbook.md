# Intake Playbook

Use adaptive triage. The Owner should experience a useful conversation, not an intake form.

## Core rule

Ask one focused question. Wait. Use the answer before asking the next question. A focused question covers one decision domain and has one answer target; do not hide several asks inside one sentence.

Do not send a numbered question block. Do not make the Owner repeat facts that appear in the request, a source JSON, league settings, a linked league, or a supplied screenshot.

The first intake reply contains only the question. Never announce that no prior sheet, configuration, or project data was found. Do not preface the question with a project-search report, confirmed-settings recap, task-mode explanation, budget warning, or process narration.

## Start with evidence

For an existing sheet, read the JSON before asking anything.

For a new sheet, use league settings already present in the request or in material the user explicitly references. Unless the request names a file or prior sheet, do not use Glob, Grep, Read, or repository inspection to look for one. If no settings are supplied, open with this one question:

> Can you send the league settings page or a screenshot? If not, what scoring does the league use: non-PPR, half-PPR, PPR, or custom?

This gives the Owner a fast path. Extract all readable facts from the source before asking about gaps.

Do not ask for the year, the draft date, or task mode when the request makes them clear. Use the current season and the research access date unless the user asks for another season or a dated historical board.

## Question order

Follow this order only for facts that remain unknown. Ask one at a time.

```text
settings source
└─ scoring
   └─ starting lineup
      └─ team count and draft mechanics
         └─ keepers and unavailable players
            └─ draft slot or salary-cap budget
               └─ platform ADP
                  └─ personalized preferences, if requested
```

Rounds, bench size, Team/Owner name, file name, page count, and visual options are output details. Collect them later unless they materially affect the requested strategy. Use `general` as the working Team label until naming is actually required.

## High-signal questions

Use the smallest question that resolves the current uncertainty.

| Unknown | Good next question |
|---|---|
| Scoring | “What scoring does the league use? Include TE premium or unusual QB scoring if it has either.” |
| Starting lineup | “What is the starting lineup?” |
| Team count | “How many Teams are drafting?” |
| Draft mechanics | “Is this snake, third-round reversal, linear, or salary cap?” |
| Availability | “Are there keepers, traded picks, or players already unavailable?” |
| Pick position | “What pick do you have, after any traded-pick changes?” |
| Platform | “Which platform runs the draft? I’ll use its ADP if it is available.” |
| Personalization | “Do you want a value-first board, a safer floor, or more upside?” |

If the user does not care about personal strategy, record `value-based` and stop asking preference questions.

Do not append a second domain to these questions. For example, after asking about the starting lineup, wait before asking about bench size; after asking about keepers, wait before asking for draft slot.

## Scoring branches

### Non-PPR / standard

Treat confirmed non-PPR as zero reception points. Ask about bonuses only when the user names custom scoring or the settings source shows them.

### Half-PPR or PPR

Treat confirmed half-PPR as 0.5 points per reception and PPR as 1.0. Ask only when the user names a custom reception value or exception.

### TE premium

Ask for exact TE reception points and any TE first-down bonus. TE premium can materially change both positional and overall tiers.

### Superflex or 2QB

Ask only missing facts, one per message:

1. Is a second QB allowed or required?
2. Are passing touchdowns worth four or six points?
3. Ask about QB roster limits only when the league has a nonstandard limit.

Do not reuse one-QB overall ranks.

### IDP

Request the IDP settings source. If it is unavailable, ask for enabled slots first, then the missing scoring facts one at a time. Add DL, LB, DB, and IDP/FLEX boards as needed.

## Draft-format branches

### Snake or linear

Ask for draft slot. Ask about traded picks only when the league permits them or the Owner indicates a trade.

### Third-round reversal

Confirm the reversal rule and pick order. Do not treat it as an ordinary snake draft.

### Salary cap

Ask for total budget first. Then ask about minimum bid and keeper costs only if unknown. Ask about preferred build only for a personalized board.

Replace round-window logic with price bands and maximum bids.

## Keeper branch

Ask for the authoritative keeper list or a screenshot first. If that is not available, ask for the next missing keeper fact one at a time: player, owning Team, and keeper cost. Do not ask whether a listed keeper is unavailable. A confirmed keeper is unavailable by default.

Never infer keeper truth from generic platform data when an authoritative league list exists.

## Personal strategy branch

Ask only when the user requests personalization. Begin with draft style: value-first, safer floor, or more upside. Then ask a follow-up only when it changes a decision, such as an explicitly desired early build, a target/fade list, or strong QB/TE timing preference.

Do not turn a weak preference into a hard rule. Label soft preferences as tiebreakers.

## Update intake

Read the existing sheet. Then ask one question: “What do you want to change?” Read locks from the source. Ask only if a lock, variant choice, or research cutoff is absent and changes the requested work.

## Start research

When the material facts are known, state the working assumptions in one short message and begin research. Do not ask for a ceremonial confirmation. Ask one more question only when an unresolved fact would change rankings, tiers, or availability. Store material assumptions in `meta.assumptions`.
