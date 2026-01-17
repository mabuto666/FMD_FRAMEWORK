#!/usr/bin/env python3
import os, sys, subprocess, json
from datetime import datetime, timezone
from pathlib import Path

DISPATCH_PATH = os.getenv("DISPATCH_PATH", "contracts/dispatch.json")
RUNLOG_DIR = os.getenv("RUNLOG_DIR", "docs/99-ops/runlog")

def utc_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def sh(cmd: str) -> int:
    p = subprocess.run(cmd, shell=True)
    return p.returncode

def write_runlog(intent: str, result: str, notes=None):
    Path(RUNLOG_DIR).mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out = Path(RUNLOG_DIR) / f"{ts}.json"
    payload = {
        "timestamp": utc_iso(),
        "intent": intent,
        "result": result,   # pass|fail|continue
        "notes": notes or [],
    }
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return str(out)

def load_dispatch(path: str):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)
    return json.loads(p.read_text(encoding="utf-8"))

def main():
    try:
        d = load_dispatch(DISPATCH_PATH)
    except Exception as e:
        path = write_runlog("ralph_load_dispatch", "fail", [f"Failed to load dispatch: {e}", f"path={DISPATCH_PATH}"])
        print(f"FAIL (dispatch load). Runlog: {path}", file=sys.stderr)
        sys.exit(2)

    wos = d.get("work_orders") or []
    if not isinstance(wos, list):
        path = write_runlog("ralph_dispatch_shape", "fail", [f"work_orders is not a list (got {type(wos).__name__})"])
        print(f"FAIL (dispatch shape). Runlog: {path}", file=sys.stderr)
        sys.exit(2)

    next_wo = None
    for wo in wos:
        if isinstance(wo, dict) and wo.get("ready") and not wo.get("done"):
            next_wo = wo
            break

    # No pending work orders: evaluate DoD checks
    if next_wo is None:
        checks = ((d.get("definition_of_done") or {}).get("checks")) or []
        for c in checks:
            cmd = c.get("cmd")
            expect = int(c.get("expect_exit", 0))
            if not cmd:
                continue
            rc = sh(cmd)
            if rc != expect:
                path = write_runlog("ralph_dod_check", "continue", [f"Check failed: {cmd} rc={rc} expected={expect}"])
                print(f"CONTINUE (DoD not met). Runlog: {path}")
                sys.exit(1)
        path = write_runlog("ralph_dod_check", "pass", ["No work orders pending; DoD checks passed"])
        print(f"DONE. Runlog: {path}")
        sys.exit(0)

    path = write_runlog(
        "ralph_pending_work_order",
        "continue",
        [f"Pending work order: {next_wo.get('id')} {next_wo.get('title')}"]
    )
    print(f"CONTINUE (pending work order). Runlog: {path}")
    sys.exit(1)

if __name__ == "__main__":
    main()
