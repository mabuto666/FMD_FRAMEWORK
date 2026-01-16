# Copilot Agent Instructions — FMD_FRAMEWORK

## Mission
Make safe, minimal, version-controlled improvements to this repository.
Prefer config/metadata changes over code changes.

## Non-negotiables (guardrails)
- No UI-only fixes. Use scripts, CLI, or repo changes.
- No destructive actions by default (no deletes). Only if explicitly requested AND `ALLOW_DESTRUCTIVE=true`.
- Be idempotent: rerunning commands must not break state.
- Discover-before-change: never hardcode IDs/paths if they can be queried.
- Avoid guesswork: if an API/CLI call fails, capture the error and stop.

## Evidence required for every change
- Update `docs/99-ops/status.md` with what you did and how you verified.
- Write a runlog JSON under `docs/99-ops/runlog/<timestamp>.json` capturing:
  - intent / work order id (if any)
  - commands executed + exit codes
  - key outputs or file paths to logs
  - errors (if any)

## Repo map (source of truth)
- `config/`    : configuration and deployment inputs (authoritative)
- `setup/`     : bootstrapping / install scripts
- `src/`       : framework runtime code
- `demodata/`  : samples / demo content
If unsure, search the repo before adding new files.

## Change style
- Keep diffs small.
- Prefer adding docs and scripts over refactors.
- When adding automation, include a dry-run mode.
