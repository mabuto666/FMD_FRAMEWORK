# AGENTS — FMD_FRAMEWORK

This repo is optimized for autonomous agent work (GitHub Copilot Agent).

## How to work in this repo
1) Read `.github/copilot-instructions.md`
2) Make the smallest change that achieves the objective
3) Record evidence:
   - update `docs/99-ops/status.md`
   - write a runlog JSON to `docs/99-ops/runlog/`

## Verification (until full runners exist)
Use the provided minimal runner:
- `./tools/verify.sh` (read-only checks; safe to rerun)
- If Python is present, it runs `python -m compileall`
- It also validates YAML if `python` and `pyyaml` are available (optional)

## Repo structure (expected)
- `config/`    : configuration
- `setup/`     : bootstrap scripts
- `src/`       : runtime code
- `demodata/`  : demo data
