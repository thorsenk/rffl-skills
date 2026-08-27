# Research and Source Policy

Use current information for the target season. Do not rely on model memory for time-sensitive rankings, ADP, injuries, depth charts, suspensions, holdouts, or role changes.

## Source hierarchy

1. **League authority**
   - confirmed user answers
   - current RFFL rulebook or season configuration
   - final draft order
   - final keeper decisions and traded picks
2. **Primary football facts**
   - official NFL club transactions and depth-chart information
   - official injury designations and league discipline
3. **Scoring-specific fantasy data**
   - current ECR or consensus rankings
   - current platform-specific ADP
   - current projections built for the stated scoring system
4. **Analysis and inference**
   - beat reporting and reputable fantasy analysis
   - agent interpretation, clearly labeled

League authority overrides generic platform assumptions. A player shown as available in public ADP can still be unavailable because of a keeper.

## Minimum research record

For every material source, store:

- publisher
- title or dataset name
- URL
- data type: ADP, ECR, projection, injury, depth chart, news, or league authority
- scoring format
- platform when applicable
- published or updated date when available
- access date and time

## Consensus rules

When the user asks for consensus:

- Prefer a recognized multi-expert consensus source.
- Record how many experts or feeds are represented when the source exposes it.
- Do not average incompatible formats.
- Do not combine one-QB and Superflex data.
- Do not combine PPR and non-PPR ranks without normalization and an explicit explanation.

## ADP rules

Use platform-specific ADP when the draft platform is known. Otherwise use a clearly labeled consensus ADP.

Do not treat ADP as truth. It is useful for:

- estimating availability
- detecting market value or overpricing
- selecting realistic target windows
- understanding positional runs

## Freshness rules

Use the draft date to set urgency:

- More than 30 days out: broad rankings and role research are acceptable.
- 8-30 days out: refresh ADP, injuries, camp role, and depth-chart changes.
- 0-7 days out: refresh all material current data and recheck unavailable players.
- Draft day: record a final cutoff time and time zone.

These are defaults, not guarantees. A major injury, trade, suspension, or role change requires an immediate refresh regardless of the schedule.

## Conflict handling

When sources disagree:

1. Verify that scoring and format match.
2. Check update dates.
3. Prefer primary facts for availability and role changes.
4. Preserve separate ADP and ECR values.
5. Use the user's strategy only after the factual base is clear.
6. Record the disagreement in `research_conflicts[]` when it changes a tier or target decision.

## Confidence

Use:

- `high`: strong current evidence with little material disagreement
- `medium`: credible evidence with meaningful uncertainty
- `low`: sparse, stale, conflicting, or inference-heavy evidence

Confidence does not replace a source citation.

## Prohibited shortcuts

- ranking from last season without current validation
- using an overall board from a different scoring format
- silently substituting platform ADP for consensus ADP
- inventing bye weeks, team assignments, injuries, or keeper costs
- calling a player a sleeper only because the agent likes the player
- creating a target window without comparing it with current ADP
