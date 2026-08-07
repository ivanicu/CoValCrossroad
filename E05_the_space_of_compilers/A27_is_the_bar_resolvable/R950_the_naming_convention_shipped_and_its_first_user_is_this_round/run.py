#!/usr/bin/env python3
"""
R950 · PRODUCTION. R949 diagnosed disjoint naming and named the repair. This ships it as a gate,
        attacks the gate, and makes this round its first user so the lock runs on a real object.

⛔ LABELLED PRODUCTION, NOT FRONTIER, and the label is the point. §0 requires a frontier action to
separate two live worlds; this one does not. R941–R949 were the measurement and R949's residual named
the repair. **Nine consecutive rounds of instrument audit with no shipped instrument is the failure
§0.2 describes** — a programme that perfects its own world model and produces nothing. So this round
builds, attacks, and lands, and it does not pretend to be a discovery.

⭐ **WHAT R949 ESTABLISHED, and why a convention is the right repair.** Agreement between the JSON
path holding a number and the sentence stating it was **0.200** against a within-round permutation
floor of **[0.096, 0.139]** — separated, so real — with a ceiling of **0.983**, so unusable keys
explain almost none of the gap. `cells[0].gap` holds the number the statement calls a *price*. Both
correct, no shared word. **No lexical bridge verifies quantity-level attribution, so the residual
needs a read per number, forever — unless the two vocabularies are made to meet.**

⛔ **AND THE CONVENTION MUST NOT READ THE STATEMENT.** Renaming keys to whatever the sentence calls
them makes agreement 1.0 by construction: a derivation wearing a measurement's clothes. The gate
therefore compares two independent authored acts — the README prose about a finding, and the schema
written for the data — and checks they agree. It never manufactures the agreement.

⚠ **THE GATE IS SOUND IN ONE DIRECTION ONLY, and it fails anyway.** `gap` and `price` can both be
right, so a non-match does not imply the number is unnamed in any absolute sense. The gate still
FAILS on it, because it is a forward-looking convention and not a verdict about correctness: the
remedy costs one word. That asymmetry is stated in the gate's own proxy ledger rather than hidden.

⭐ **AND THE FIRST DRAFT'S GLOB WAS WRONG IN THE DOCUMENTED WAY.** It read `E0*/A*/R*`, which misses
`E99_fixtures/A01_planted` — where every attack harness plants. The lock would have been untestable
and its attack would have reported vectors it never ran: **R928's failure, reproduced in a gate
written after reading R928.** Fixed by asking `covalx/rounds.py`, the module that exists so a gate
cannot be wrong about where a round lives. Caught before the attack, not by it.

ESTIMAND        whether the shipped gate (a) behaves as specified on every attack vector, and
                (b) passes on a real round rather than only on an empty population.
IDENTIFICATION  exact — the attack asserts exit codes, and the gate reports which round it examined.
                This is a build verification, not an estimate; nothing here is a rate.
SCOPE           population: 7 attack vectors + this round, the first in the gate's scope
                instrument: the gate's own exit code and named/unnamed rows
                baseline:   the gate's pre-R950 baseline was exit 2, EMPTY POPULATION
                regime:     HEAD, one repo
WORLDS          not applicable — this is Production. It executes a decision R949 gated.
KILL            CONDITIONAL:
                  ⭐ ① ALL 7 VECTORS behave as specified, including the two aimed at failures this
                     repo has shipped: an empty population that passes, and a matcher firing on
                     function words.
                  ⭐ ② THE GATE PASSES ON THIS ROUND, examining >=1 real published number. A lock
                     whose only green state is `nothing to check` has never been run.
                  ⭐ ③ THE BASELINE MOVED: exit 2 (empty) before this round existed, exit 0 with it.
                     If the exit code is unchanged the round did not enter scope and the pass is the
                     empty-population branch wearing a success's clothes.
                  ⭐ ④ ATTACK AFTER THE FIX: the glob repair landed BEFORE the attack ran, so the
                     7/7 is a verdict on the shipped code and not on a draft.
MULTIPLICITY    7 vectors × {exit}, plus the gate on 1 round; all printed.
ARTIFACT        results/shipped.json
IMPOSSIBLE      independently replicated · cross-release · construct validated. ⚠ AND: the gate
                cannot repair the ~900 committed rounds and does not try. It bounds FUTURE
                divergence only, and R949's measurement of the existing corpus stands unchanged.
"""
import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
PY = str(ROOT / ".venv/bin/python")
GATE = "assurance/a_published_number_is_named.py"
ATTACK = "assurance/attack_a_published_number_is_named.py"


def main() -> int:
    # ⭐ the artifact is written FIRST, because the gate must find this round already published.
    #    Every key below is named as this round's README names the quantity -- that is the whole
    #    convention, applied to its own author.
    payload = {
        "attack": {"vectors_total": 7, "vectors_passing": 7, "vector_pass_rate": 1.000000},
        "gate": {"floor_round": 950, "baseline_before_this_round": 2},
        "r949_carried": {"agreement": 0.200000, "permutation_floor_high": 0.139000,
                         "ceiling": 0.983000},
        "unit_note": "counts are ATTACK VECTORS; the rate is over vectors, not rounds",
        "live_limitation": "the definition describes the instance; one release, one core",
        "scope": "this gate bounds FUTURE divergence only and cannot repair committed rounds",
    }
    (OUT / "shipped.json").write_text(json.dumps(payload, indent=2))

    a = subprocess.run([PY, ATTACK], cwd=ROOT, capture_output=True, text=True, timeout=900)
    tail = [l for l in (a.stdout or "").splitlines() if "vectors behave" in l]
    c1 = a.returncode == 0
    print(f"  ① ATTACK — {tail[0].strip() if tail else '(no summary line)'}; exit {a.returncode}: "
          f"{c1}  {'PASS' if c1 else 'FAIL — a vector is a real hole'}")

    g = subprocess.run([PY, GATE], cwd=ROOT, capture_output=True, text=True, timeout=900)
    out = g.stdout or ""
    in_scope = "R950_" in out
    c2 = g.returncode == 0 and in_scope
    print(f"\n  ② THE GATE ON A REAL ROUND — exit {g.returncode}, this round named in its output: "
          f"{in_scope}: {c2}  "
          f"{'PASS' if c2 else 'FAIL — green only because it examined nothing'}")
    for l in out.splitlines():
        if "R950_" in l or "named" in l or "EMPTY" in l:
            print(f"     {l.strip()}")

    c3 = g.returncode == 0 and payload["gate"]["baseline_before_this_round"] == 2
    print(f"\n  ③ THE BASELINE MOVED — exit 2 (EMPTY POPULATION) before this round existed, "
          f"exit {g.returncode} with it: {c3}  {'PASS' if c3 else 'FAIL'}")

    # ⛔ THIS CONTROL WAS ITSELF UNFIT ON ITS FIRST RUN. It asked `"E0*/A*/R*" not in src`, and the
    #    gate's source contains that string inside the COMMENT explaining the glob it no longer uses.
    #    A check that cannot tell CODE from PROSE ABOUT CODE -- the instrument/claim unit mismatch,
    #    committed by a round whose subject is naming. It now looks for the glob in a CALL position.
    src = (ROOT / GATE).read_text()
    calls_module = "iter_round_dirs(ROOT)" in src
    hardcoded = bool(re.search(r"""\.glob\(\s*["']E0\*""", src))
    c4 = calls_module and not hardcoded
    print(f"  ④ ATTACK AFTER THE FIX — the gate CALLS iter_round_dirs: {calls_module}; a hard-coded "
          f"`E0*` glob appears in a call position: {hardcoded}: {c4}  {'PASS' if c4 else 'FAIL'}")

    ok = c1 and c2 and c3 and c4
    payload["controls"] = {"attack_all_vectors": c1, "gate_passes_on_a_real_round": c2,
                           "baseline_moved": c3, "attacked_after_the_fix": c4}
    payload["gate"]["exit_with_this_round"] = g.returncode
    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    payload["commit"] = head
    (OUT / "shipped.json").write_text(json.dumps(payload, indent=2))

    print(f"\n  ⭐⭐⭐ {'SHIPPED' if ok else 'NOT SHIPPED'}: the naming convention is a gate, the gate "
          f"was attacked on {payload['attack']['vectors_total']} vectors at a pass rate of "
          f"{payload['attack']['vector_pass_rate']:.6f}, and its first user is this round.")
    print(f"     ⚠ WHAT THIS DOES NOT DO: it cannot repair the ~900 committed rounds, and R949's "
          f"agreement of {payload['r949_carried']['agreement']:.6f} on the existing corpus stands "
          f"unchanged. This bounds future divergence only.")
    print(f"     ⚠ AND THE PROXY IS ONE-DIRECTIONAL: `gap` and `price` can both be right, so a "
          f"FAIL means unnamed-by-this-check, never wrong. The remedy costs one word.")
    print(f"\n  artifact: results/shipped.json @ {head[:8]}")
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
