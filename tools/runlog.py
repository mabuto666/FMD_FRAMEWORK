#!/usr/bin/env python3
"""
Minimal runlog writer for agent executions.

Usage:
  python tools/runlog.py --intent "..." --result pass|fail --out docs/99-ops/runlog/<ts>.json \
    --cmd "cmd string" --exit 0 --note "optional"
"""
import argparse, json, os
from datetime import datetime, timezone

def utc_ts():
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--intent", required=True)
    ap.add_argument("--result", required=True, choices=["pass","fail","continue"])
    ap.add_argument("--out", default="")
    ap.add_argument("--cmd", action="append", default=[])
    ap.add_argument("--exit", action="append", default=[])
    ap.add_argument("--note", action="append", default=[])
    args = ap.parse_args()

    out = args.out.strip()
    if not out:
        out = os.path.join("docs","99-ops","runlog", f"{utc_ts()}.json")

    os.makedirs(os.path.dirname(out), exist_ok=True)

    commands = []
    # Allow multiple --cmd/--exit pairs; pad as needed
    exits = [int(x) for x in args.exit] if args.exit else []
    while len(exits) < len(args.cmd):
        exits.append(-1)
    notes = args.note or []

    for i, c in enumerate(args.cmd):
        commands.append({"cmd": c, "exit_code": exits[i]})

    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),
        "intent": args.intent,
        "result": args.result,
        "commands": commands,
        "notes": notes,
    }

    with open(out, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")

    print(out)

if __name__ == "__main__":
    main()
