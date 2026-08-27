# Intake Playbook

Use adaptive triage. Do not ask every question blindly. Read existing files first and skip anything already known.

## Opening

When the task mode is unclear, ask:

> Are we creating a new cheat sheet, updating an existing one, refreshing current data, or saving a separate variant?

When the mode is clear, begin with the essential intake.

## Essential intake

Ask these in one compact numbered block unless the user prefers one question at a time.

1. **Season and draft date:** What season is this for, and when is the draft?
2. **League format:** Redraft, keeper, dynasty startup, rookie-only, or best ball?
3. **Scoring:** Non-PPR, half-PPR, PPR, or custom? Ask for TE premium, points per first down, passing-TD value, yardage bonuses, and return-yard scoring when relevant.
4. **League size:** How many Teams?
5. **Draft format:** Snake, linear, third-round reversal, or salary cap?
6. **Draft position:** What slot, or what salary-cap budget?
7. **Roster and rounds:** Exact starting slots, bench/IR/taxi slots, and total board rounds.
8. **Keepers and unavailable players:** Who is kept, at what cost, and which players are already unavailable?
9. **Draft platform:** Which platform will run the draft? Use its ADP when available.
10. **Output goal:** Pure consensus, personalized strategy, or both?

### Important distinction

`Rounds` means the number of board rounds. `Live selections` may be lower when keepers prefill cells. Example: a 16-round board with two prefilled keepers has 14 live selections for that Team.

## Scoring branches

### Non-PPR / standard

Confirm that receptions score zero. Ask whether long-touchdown or yardage bonuses materially change deep-threat and touchdown-dependent players.

### Half-PPR or PPR

Confirm reception points exactly. Do not assume every platform uses the same defaults.

### TE premium

Ask for exact TE reception points and any TE first-down bonus. TE premium can materially change both positional and overall tiers.

### Superflex or 2QB

Ask:

- Is a second QB allowed or required?
- How many QBs may be rostered?
- How many Teams are in the league?
- Are passing touchdowns worth four or six points?

Do not reuse one-QB overall ranks.

### IDP

Ask for enabled slots and scoring for tackles, assists, sacks, interceptions, passes defended, forced fumbles, fumble recoveries, and return touchdowns. Add DL, LB, DB, and IDP/FLEX boards as needed.

## Draft-format branches

### Snake or linear

Ask for draft slot and whether picks were traded.

### Third-round reversal

Confirm the reversal rule and pick order. Do not treat it as an ordinary snake draft.

### Salary cap

Ask for:

- total budget
- minimum bid
- keeper costs
- nomination order if known
- desired build: balanced, stars-and-scrubs, or value-only
- whether the user wants AAV, target price, and hard maximum price

Replace round-window logic with price bands and maximum bids.

## Keeper branches

Ask for each keeper:

- player
- Team that owns the keeper
- keeper cost: round, pick, or salary
- whether the player is completely unavailable to the user
- whether the cost changes due to trades or prior-year rules

Never infer keeper truth from generic platform data when an authoritative league list exists.

## Personal strategy branches

Ask only when the user wants personalization.

1. **Risk:** Conservative, balanced, or ceiling-first?
2. **Injuries:** How much injury or role uncertainty is acceptable?
3. **Early build:** Value-only, RB-heavy, WR-heavy, anchor RB, hero RB, zero RB, elite QB, elite TE, or no fixed structure?
4. **QB timing:** Pay for an elite difference-maker, wait for value, or stream?
5. **TE timing:** Premium TE at value, middle-tier target, or late-round approach?
6. **Rookies:** Prefer, neutral, or discount?
7. **Stacking:** Actively seek QB-pass-catcher stacks, use only as a tiebreaker, or ignore?
8. **Bye weeks:** Ignore, avoid concentration, or apply only as a late tiebreaker?
9. **Favorites and fades:** Which players or NFL Teams should be targeted, avoided, or treated neutrally?
10. **Evidence:** Should prior draft behavior or league history influence the board?

Do not turn a weak preference into a hard rule. Label soft preferences as tiebreakers.

## Update intake

When updating an existing sheet, ask only:

1. What changed: data, league settings, strategy, draft slot, keepers, or output layout?
2. Which fields are locked and must remain untouched?
3. Should this replace the current working version or become a separate variant?
4. What research cutoff is required?

## Confirmation gate

Before research, show:

```text
Confirmed
- ...

Assumed
- ...

Open
- ...
```

Proceed when all open items that materially affect ranks, tiers, or availability are resolved. When the user accepts assumptions, store them in `meta.assumptions`.
