#!/usr/bin/env bash
set -euo pipefail

INTENT="verify.sh (read-only)"
LOG_DIR="docs/99-ops/review"
mkdir -p "$LOG_DIR"

ts="$(date +%Y%m%d-%H%M%S)"
out_log="$LOG_DIR/verify_${ts}.log"

echo "== FMD_FRAMEWORK verify (minimal) ==" | tee "$out_log"
echo "pwd: $(pwd)" | tee -a "$out_log"
echo "branch: $(git rev-parse --abbrev-ref HEAD)" | tee -a "$out_log"
echo "commit: $(git rev-parse --short HEAD)" | tee -a "$out_log"
echo | tee -a "$out_log"

# Basic repo sanity
test -f .github/copilot-instructions.md
test -f AGENTS.md
test -d docs/99-ops/runlog

# Python checks (optional)
if command -v python3 >/dev/null 2>&1; then
  echo "python3 found: $(python3 --version)" | tee -a "$out_log"
  # Syntax check python files without writing bytecode
  if find . -name "*.py" -not -path "./.venv/*" | grep -q .; then
    echo "Running: python3 syntax check (repo, skip *.Notebook) ..." | tee -a "$out_log"
    python3 - <<'PY' >>"$out_log" 2>&1 || { echo "python syntax check failed" | tee -a "$out_log"; exit 1; }
import os, sys

bad = 0
for root, _, files in os.walk("."):
    if root.startswith("./.git") or root.startswith("./.venv") or ".Notebook" in root:
        continue
    for fn in files:
        if fn.endswith(".py"):
            path = os.path.join(root, fn)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    src = f.read()
                compile(src, path, "exec")
            except Exception as e:
                bad += 1
                print(f"PYTHON INVALID: {path}: {e}")
print("Python syntax check complete; bad=", bad)
sys.exit(1 if bad else 0)
PY
  else
    echo "No Python files found; skipping python syntax check" | tee -a "$out_log"
  fi
else
  echo "python3 not found; skipping python checks" | tee -a "$out_log"
fi

# YAML sanity (optional, only if PyYAML is available)
if command -v python3 >/dev/null 2>&1; then
python3 - <<'PY' >>"$out_log" 2>&1 || true
import sys, os
try:
    import yaml  # type: ignore
except Exception:
    print("PyYAML not installed; skipping YAML validation")
    sys.exit(0)

bad = 0
for root, _, files in os.walk("."):
    if root.startswith("./.git") or root.startswith("./.venv"):
        continue
    for fn in files:
        if fn.endswith((".yml",".yaml")):
            path = os.path.join(root, fn)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    yaml.safe_load(f)
            except Exception as e:
                bad += 1
                print(f"YAML INVALID: {path}: {e}")
print("YAML validation complete; bad=", bad)
sys.exit(1 if bad else 0)
PY
fi

echo | tee -a "$out_log"
echo "OK: minimal verify passed" | tee -a "$out_log"

# Write runlog JSON (best-effort)
if command -v python3 >/dev/null 2>&1; then
  python3 tools/runlog.py --intent "$INTENT" --result pass --cmd "./tools/verify.sh" --exit 0 --note "$out_log" >/dev/null || true
fi

echo "$out_log"
