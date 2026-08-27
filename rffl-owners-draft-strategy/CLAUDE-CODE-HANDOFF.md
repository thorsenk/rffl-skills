# Claude Code Handoff

Use this bundle as a project-level Claude Code skill.

## Installation task

1. Place this folder at `.claude/skills/rffl-owners-draft-strategy/` in the target repository.
2. Read `SKILL.md` and `README.md`.
3. Install `requirements.txt` in the project's Python environment.
4. Run `bash scripts/smoke_test.sh` from the skill folder.
5. Confirm that `examples/sample-output.pdf` renders without clipped text.
6. Do not redesign the visual system during installation.

## First test

Invoke:

```text
/rffl-owners-draft-strategy new
```

Then provide a real league profile. The skill should interview the user, create a JSON source, validate it, and render a versioned PDF.

## Test success criteria

- The interview distinguishes non-PPR, half-PPR, PPR, and custom scoring.
- It asks for Team count, rounds, roster slots, keepers, draft type, slot/budget, and platform.
- It asks detailed follow-ups only when the answers require them.
- The player pool expands through continuation pages.
- Tiers are uneven and based on value cliffs.
- The source JSON remains authoritative.
- Updates preserve locked fields and save a new version.
- The PDF uses approved RFFL assets when the repository provides them.

## Suggested prompt to Claude Code

```text
Install and inspect this skill bundle. Run its smoke test. Do not change the design or schema unless a test fails. Then invoke /rffl-owners-draft-strategy new and begin the adaptive league intake with me.
```
