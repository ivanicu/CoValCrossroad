#!/usr/bin/env python3
"""R548 — row 2's cost says "an install". Its own remedy names two paths, and one is installed.

R547 re-grouped the register by reachability and made row 2 the cheapest reachable entry, cost
"an install". But the row's remedy column reads "quantisation, OR OFFLOAD -- an environment
change to the shared .venv, not a GPU run". Those are two different paths with two different
costs, and the label collapsed them.

ESTIMAND (before method): which of row 2's two named remedies are available in this venv without
  an install.
IDENTIFICATION: fully identified -- a package is importable or it is not.
SCOPE  population: this project's .venv · instrument: importlib.util.find_spec · regime: today.
  ⚠ an environment fact, so it EXPIRES at the next infra event.
WORLDS  A · neither path is available; "an install" is the right cost.
        B · offload is available now, so row 2's cost is "an install (quantisation) OR a slower
              run (offload, already here)" and the single label understates what is reachable.
KILL (pre-registered): accelerate absent kills world B.
POSITIVE CONTROL: packages known present must be found -- torch and transformers were used by
  R540 on this same venv. A prober that cannot see them cannot report an absence.
NEGATIVE CONTROL: an invented module name must NOT resolve, else find_spec matches anything.
NOISE FLOOR: none -- import resolution is exact.
MULTIPLICITY: 7 probes; all printed.
IMPOSSIBLE HERE: whether offload is FAST ENOUGH. That needs a 7B offloaded run through pueue,
  which is a measurement and not an install. Named, not marked planned, and NOT guessed --
  R540/R541/R542 cost three rounds to learn that modelling a runtime is worthless.
"""
import importlib.util as u, json, pathlib, sys

QUANT = ["bitsandbytes", "optimum", "auto_gptq", "awq"]
OFFLOAD = ["accelerate"]
PRESENT_CTRL = ["torch", "transformers"]
ABSENT_CTRL = "zzz_not_a_module_zzz"

def have(m):
    try:
        return u.find_spec(m) is not None
    except Exception:
        return False

def main():
    pos = {m: have(m) for m in PRESENT_CTRL}
    print(f"  POSITIVE CONTROL  packages R540 used on this venv: "
          f"{ {k: v for k, v in pos.items()} } -> {'PASS' if all(pos.values()) else 'FAIL'}")
    if not all(pos.values()):
        print("  -> the prober cannot see known packages; UNVERIFIED."); return 0
    neg = have(ABSENT_CTRL)
    print(f"  NEGATIVE CONTROL  invented module resolves: {neg} -> {'PASS' if not neg else 'FAIL'}")
    if neg: return 0

    q = {m: have(m) for m in QUANT}
    o = {m: have(m) for m in OFFLOAD}
    print(f"\n  quantisation path : " + " · ".join(f"{m}={'YES' if v else 'no'}" for m, v in q.items()))
    print(f"  offload path      : " + " · ".join(f"{m}={'YES' if v else 'no'}" for m, v in o.items()))
    world = "B" if any(o.values()) and not any(q.values()) else "A"
    print(f"\n  WORLD {world} -- " +
          ("row 2 names TWO remedies and one is already installed: quantisation needs an install, "
           "offload does not. The single cost label 'an install' understates what is reachable"
           if world == "B" else "neither path is available; 'an install' is the right cost"))
    print(f"  ⚠ NOT measured: whether offload is fast enough for 15,472 judge calls. That needs a "
          f"7B offloaded run through pueue -- a measurement, not an install, and R540-R542 cost "
          f"three rounds to establish that modelling a runtime is worthless.")
    print(f"  ⚠ ENVIRONMENT FACT: expires at the next infra event.")

    out = pathlib.Path(__file__).parent / "results/row2_remedies.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"quantisation": q, "offload": o, "world": world,
                               "not_measured": "offload throughput on 7B",
                               "expires": "next infra event"}, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
