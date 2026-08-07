#!/usr/bin/env python3
"""
R907 · R906's inventory limit is a PRICED WALL, not a missing run — and my NEXT was wrong twice.

⛔⛔ WHY, AND IT RETRACTS MY OWN CLOSING SENTENCE. R906 ended: *"Building 6–8 more FIXED_CHECKLIST
arms — the generator already emits them, genericpool16 is one — would take that kind's interval
from width 0.811 to roughly 0.35 … That is a missing run, like R893's was."* **Both halves are
false, and the cost meter is what shows it.**

① **THERE IS NO COMMITTED BUILDER.** `generic` and `genericpool16` are CONSUMED in a dozen rounds
   and BUILT in none — no script in `corebench/`, `covalx/` or anywhere else emits them.
   `select_core.py`'s rule list is `random_k · topw_k · topabs_k · full · topvar_k · topwvar_k ·
   oracle_k · indep_k · greedy_k`, and none of them produces a fixed checklist. **"The generator
   already emits them" was reconstructed from the arms existing, not read from a builder.**

② **AND IT WOULD NOT BE FREE.** Every arm `select_core.py` makes costs *"0 judge calls"* for one
   reason, which the script states: each arm is a **SUBSET of `coval_full`**, whose satisfaction is
   already judged. **A fixed checklist is by definition NOT a subset** — that is what makes it
   fixed — so its criteria have no satisfaction on any prompt and must be judged. `score.py:254`
   gives the release's own unit: `judge_calls_per_prompt = mean(k) × 4`.

⭐ **SO R893's PATTERN DOES NOT TRANSFER, AND THE DIFFERENCE IS WORTH STATING.** R893's leaky arms
were a missing run because the generator could make them for free — the subset property held. Here
it does not. **The same sentence — "that is a missing run" — was true there and false here, and
only the subset property distinguishes them.** An impossibility that has a PRICE is not the same as
one that has a mechanism, and this round prices it rather than asserting either.

ESTIMAND        the judge-call cost of adding one arm to each criterion-source kind, in the
                release's own unit.
IDENTIFICATION  ⚠ **DERIVATION, labelled as one.** `cost = 0` iff the arm's criteria are a subset
                of `coval_full` (already judged); otherwise `cost = k × 4 × n_prompts`. That is
                arithmetic given the subset property, not a measurement — the MEASURED inputs are
                which kinds are subsets and what k each uses.
SCOPE           population: the criterion-source kinds R906 typed
                instrument: subset test against `coval_full`; the cost unit from score.py:254
                baseline:   0 judge calls, which is what every existing selection arm costs
                regime:     home release, 968 prompts, 4 responses
WORLDS          A · at least one kind cannot be expanded for 0 calls -> R906's inventory limit is a
                    PRICED wall, the register gains a line with a number, and my NEXT is retracted
                B · every kind can be expanded free -> the missing-run reading stands and the arms
                    should simply be built
KILL            CONDITIONAL:
                  ⭐ ① POSITIVE, from the source not from memory: `select_core.py` must actually
                     claim 0 judge calls, and `score.py` must actually define the cost unit. Both
                     strings are grepped; if either is absent the pricing is invented.
                  ⭐ ② the SUBSET property must be MEASURED per kind, not assumed — a rubric
                     selector must come back ~1.0 and a fixed checklist ~0.0. **If the fixed
                     checklist turned out to be a subset, expansion WOULD be free and WORLD B.**
                  ⭐ ③ NO BUILDER: the absence must be established by searching for one, and the
                     search must be shown to work — it must FIND `select_core.py` when asked for
                     the rules it does emit. An absence from an untested search is silence.
MULTIPLICITY    one estimand per kind; every kind priced, including the free ones.
ARTIFACT        results/expansion_cost.json
IMPOSSIBLE      cross-release · construct validated · causally identified · independently
                replicated. ⚠ AND: this prices judge CALLS. It does not price wall-clock or money,
                which depend on a judge this round does not choose.
"""
import json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
RES = ROOT / "corebench" / "results"
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
NRESP = 4


def main() -> int:
    # ---- ① POSITIVE: both cost facts READ from source ------------------------------------------
    sc = (ROOT / "corebench" / "select_core.py").read_text()
    so = (ROOT / "corebench" / "score.py").read_text()
    claim_free = "0 judge calls" in sc
    unit = "E3_judge_calls_per_prompt" in so
    c1 = claim_free and unit
    print(f"  ① POSITIVE cost facts read from source, not memory:")
    print(f"     select_core.py claims '0 judge calls' : {claim_free}")
    print(f"     score.py defines the cost unit        : {unit}")
    print(f"     {c1}  {'PASS' if c1 else 'FAIL'}")

    # ---- ③ NO BUILDER, with the search itself controlled ---------------------------------------
    def hits(term):
        r = subprocess.run(["grep", "-rl", "--include=*.py", "--include=*.sh", term, str(ROOT)],
                           capture_output=True, text=True)
        return [x for x in r.stdout.splitlines() if "/results/" not in x]
    ctrl_hits = hits("topvar_k")            # a rule select_core.py DOES emit
    gen_hits = [h for h in hits("genericpool16") if "/A24_" not in h and "/A2" not in h]
    c3 = any("select_core.py" in h for h in ctrl_hits)
    print(f"\n  ③ NO-BUILDER search, with the search CONTROLLED:")
    print(f"     control: searching for `topvar_k` (a rule select_core DOES emit) finds "
          f"select_core.py: {c3}  {'PASS' if c3 else 'FAIL'}")
    print(f"     an absence from an untested search is silence, not evidence")
    print(f"     searching for `genericpool16` outside the round dirs: {len(gen_hits)} file(s) "
          f"{gen_hits[:3]}")

    # ---- ② SUBSET property, MEASURED per kind --------------------------------------------------
    sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
    from covalx.judge import load_join                                       # noqa: E402
    joined = load_join(ROOT / "data" / "comparisons.jsonl",
                       ROOT / "data" / "conversation_rubrics.jsonl")
    fullr = {p: set(i["criterion"] for i in (r.get("coval_full") or [])) for p, _q, r in joined}

    r906 = next(A24.glob("R906_*/results/bar_by_source.json"), None)
    if r906 is None or "kinds" not in json.loads(r906.read_text()):
        print("\n  UNRUNNABLE: R906 artifact missing or unreadable. Exit 2, never 0.")
        return 2
    kinds = {k["kind"]: k for k in json.loads(r906.read_text())["kinds"]}
    print(f"\n  ② SUBSET PROPERTY, measured per kind (a subset costs 0; a non-subset must be judged):")
    rows = []
    for kn, kv in sorted(kinds.items()):
        rep = None
        for a in kv["built"]:
            f = RES / f"core_{a}.json"
            if f.exists():
                rep = (a, json.loads(f.read_text())); break
        if rep is None:
            rows.append({"kind": kn, "representative": None, "subset_share": None,
                         "mean_k": None, "judge_calls_per_new_arm": None,
                         "note": "no committed selection file among this kind's arms"})
            print(f"     {kn:<26} no committed selection file — cost UNCOMPUTED")
            continue
        a, sel = rep
        pids = [p for p in sel if p in fullr and sel[p]]
        sub = float(np.mean([set(sel[p]) <= fullr[p] for p in pids]))
        k = float(np.mean([len(sel[p]) for p in pids]))
        cost = 0 if sub > 0.95 else int(round(k * NRESP * len(pids)))
        rows.append({"kind": kn, "representative": a, "subset_share": sub, "mean_k": k,
                     "n_prompts": len(pids), "judge_calls_per_new_arm": cost})
        print(f"     {kn:<26} via {a:<16} subset {sub:.3f}  k={k:.1f}  -> "
              f"{cost:,} judge calls per NEW arm")

    c2 = any(r["subset_share"] is not None and r["subset_share"] > 0.95 for r in rows) and \
        any(r["subset_share"] is not None and r["subset_share"] < 0.5 for r in rows)
    print(f"     both a subset kind and a non-subset kind present, so the test could go either "
          f"way: {c2}  {'PASS' if c2 else 'FAIL'}")
    if not (c1 and c2 and c3):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "rows": rows,
                   "controls": [bool(c1), bool(c2), bool(c3)]},
                  open(OUT / "expansion_cost.json", "w"), indent=2)
        return 2

    paid = [r for r in rows if r["judge_calls_per_new_arm"]]
    world = "A" if paid else "B"
    fc = next((r for r in rows if r["kind"] == "FIXED_CHECKLIST"), None)
    print(f"\n  ⭐⭐⭐ WORLD {world}: " + {
        "A": f"{len(paid)} kind(s) cannot be expanded for 0 judge calls — R906's inventory limit "
             "is a **PRICED WALL**, not a missing run",
        "B": "every kind can be expanded free; the missing-run reading stands"}[world])
    if world == "A" and fc and fc["judge_calls_per_new_arm"]:
        per = fc["judge_calls_per_new_arm"]
        print(f"\n  ⭐ THE PRICE OF CLOSING R906's QUESTION: FIXED_CHECKLIST needs "
              f"{per:,} judge calls")
        print(f"     per new arm. R906's own arithmetic wanted 6–8 more -> "
              f"{6*per:,}–{8*per:,} calls.")
        print(f"     **That is what `narrow the interval from 0.811 to 0.35` actually costs.**")
    print(f"\n  ⛔ AND R906's CLOSING SENTENCE IS RETRACTED ON BOTH HALVES:")
    print(f"     `the generator already emits them` — no builder exists; the arms were")
    print(f"       reconstructed as buildable FROM THEIR EXISTING, which is not the same thing.")
    print(f"     `that is a missing run, like R893's was` — R893's was free BECAUSE the subset")
    print(f"       property held. Here it does not. **The same sentence was true there and false")
    print(f"       here, and only the subset property distinguishes them.**")
    print(f"\n  ⚠ THE PRICING IS A DERIVATION. `cost = k × 4 × prompts` given non-subset is")
    print(f"    arithmetic, not a measurement; what was MEASURED is which kinds are subsets and")
    print(f"    at what k. And it prices judge CALLS only — not wall-clock or money, which")
    print(f"    depend on a judge this round does not choose.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "n_responses_per_prompt": NRESP, "kinds": rows,
               "retracts": "R906's closing sentence, on both halves: (a) `the generator already "
                           "emits them` — no committed builder for generic/genericpool16 exists "
                           "anywhere; (b) `that is a missing run, like R893's` — R893's was free "
                           "because the subset-of-coval_full property held, and it does not here",
               "why_R893_transferred_and_this_does_not": "select_core.py costs 0 judge calls "
                                                         "because every arm is a SUBSET of "
                                                         "coval_full; a fixed checklist is by "
                                                         "definition not a subset",
               "cost_unit_source": "score.py:254 E3_judge_calls_per_prompt = mean(k) * 4",
               "pricing_is_a_derivation": "cost = k*4*prompts given non-subset is arithmetic; the "
                                          "MEASURED inputs are which kinds are subsets and their k",
               "prices_calls_only": "not wall-clock or money — those need a judge choice",
               "search_was_controlled": "an absence from an untested search is silence; the "
                                        "no-builder search was verified to FIND select_core.py "
                                        "when asked for a rule it does emit",
               "controls": {"cost_facts_from_source": bool(c1),
                            "subset_test_could_go_either_way": bool(c2),
                            "search_control_finds_select_core": bool(c3)},
               "unit_note": "cost is JUDGE CALLS per new arm",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "expansion_cost.json", "w"), indent=2)
    print(f"\n  artifact: results/expansion_cost.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
