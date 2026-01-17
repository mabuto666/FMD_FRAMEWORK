#!/usr/bin/env python3
import os, sys, subprocess, json
from datetime import datetime, timezone

try:
    import yaml  # type: ignore
except Exception:
    print("Ralph requires PyYAML. Install with: python3 -m pip install pyyaml", file=sys.stderr)
    sys.exit(2)

DISPATCH_PATH = os.getenv("DISPATCH_PATH", "contracts/dispatch.yaml")
RUNLOG_DIR = os.getenv("RUNLOG_DIR", "docs/99-ops/runlog")

def utc_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00","Z")

def sh(cmd: str) -> int:
    p = subprocess.run(cmd, shell=True)
    return p.returncode

def write_runlog(intent: str, result: str, notes=None):
    os.makedirs(RUNLOG_DIR, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out = os.path.join(RUNLOG_DIR, f"{ts}.json")
    payload = {
        "timestamp": utc_iso(),
        "intent": intent,
        "result": result,
        "notes": notes or [],
    }
    with open(out, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")
    return out

def main():
    if not os.path.exists(DISPATCH_PATH):
        print(f"Missing {DISPATCH_PATH}", file=sys.stderr)
        sys.exit(2)

    with open(DISPATCH_PATH, "r", encoding="utf-8") as f:
        d = yaml.safe_load(f) or {}

    # Find first ready work order not marked done
    wos = d.get("work_orders") or []
    next_wo = None
    for wo in wos:
        if wo.get("ready") and not wo.get("done"):
            next_wo = wo
            break

    if next_wo is None:
        # No ready work orders—check DoD anyway
        checks = ((d.get("definition_of_done") or {}).get("checks")) or []
        for c in checks:
            cmd = c.get("cmd")
            expect = int(c.get("expect_exit", 0))
            rc = sh(cmd)
            if rc != expect:
                path = write_runlog("ralph_dod_check", "continue", [f"Check failed: {cmd} rc={rc} expected={expect}"])
                print(f"CONTINUE (DoD not met). Runlog: {path}")
                sys.exit(1)
        path = write_runlog("ralph_dod_check", "pass", ["No work orders pending; DoD checks passed"])
        print(f"DONE. Runlog: {path}")
        sys.exit(0)

    # If there is a work order pending, we're not done.
    path = write_runlog("ralph_pending_work_order", "continue", [f"Pending work order: {next_wo.get('id')} {next_wo.get('title')}"])
    print(f"CONTINUE (pending work order). Runlog: {path}")
    sys.exit(1)

if __name__ == "__main__":
    main()
