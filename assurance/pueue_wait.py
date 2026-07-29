"""Wait for pueue tasks matching a label substring. Tested, unlike the grep it replaces.

Entry 63. I waited on nine jobs with

    until [ "$(pueue status | grep -c 'r26-.*-rename.*Running')" = "0" ]; do sleep 30; done

`pueue status` prints the STATUS COLUMN BEFORE THE LABEL, so that pattern could
never match. grep returned 0 on the first evaluation, the loop exited at once,
and the verification after it read pre-run files and reported them as results.
No error was raised, because nothing failed: a pattern matching nothing is not an
error and a loop running zero times is not an error.

This reads `pueue status --json` and inspects the status field, so it cannot be
fooled by column order. It also REFUSES to return success when it matched no
tasks at all -- because "no tasks outstanding" and "no tasks observed" are the
two states entry 63 is about, and a waiter that cannot tell them apart is the
bug rather than the fix.

    python assurance/pueue_wait.py <label-substring> [--timeout SECONDS]
      exit 0  every matching task finished
      exit 2  nothing matched the label  (NOT success)
      exit 3  timed out with tasks still running
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time


def snapshot():
    out = subprocess.run(["pueue", "status", "--json"], capture_output=True, text=True)
    if out.returncode != 0:
        return None
    try:
        return json.loads(out.stdout)["tasks"]
    except (json.JSONDecodeError, KeyError):
        return None


def classify(tasks, needle):
    hit = {k: v for k, v in tasks.items() if needle in str(v.get("label") or "")}
    pending = {k: v for k, v in hit.items()
               if not (isinstance(v.get("status"), dict) and "Done" in v["status"])}
    done = {k: v for k, v in hit.items()
            if isinstance(v.get("status"), dict) and "Done" in v["status"]}
    return hit, pending, done


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("label")
    ap.add_argument("--timeout", type=int, default=7200)
    ap.add_argument("--poll", type=int, default=20)
    a = ap.parse_args()

    t0 = time.time()
    while True:
        tasks = snapshot()
        if tasks is None:
            print("pueue unreachable -- cannot distinguish finished from unobserved")
            return 2
        hit, pending, done = classify(tasks, a.label)
        if not hit:
            print(f"NO TASK MATCHED '{a.label}'. This is exit 2, not success: "
                  f"'nothing outstanding' and 'nothing observed' are different states "
                  f"(entry 63).")
            return 2
        if not pending:
            results = sorted({v["status"]["Done"]["result"] if isinstance(
                v["status"]["Done"].get("result"), str) else str(
                v["status"]["Done"].get("result")) for v in done.values()})
            print(f"{len(done)} task(s) matching '{a.label}' finished: {results}")
            return 0
        if time.time() - t0 > a.timeout:
            print(f"TIMED OUT after {a.timeout}s with {len(pending)} still running")
            return 3
        time.sleep(a.poll)


if __name__ == "__main__":
    sys.exit(main())
