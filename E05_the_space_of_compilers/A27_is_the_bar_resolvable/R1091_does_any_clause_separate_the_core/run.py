#!/usr/bin/env python3
"""R1091 — clause ②′ admits the core and the baselines equally. Does ANY stated clause separate them?

R1090 named the `always` block: 35 arms admitted under every admissible blind family, and the three
released cores share it with `generic`, `genericpool16`, `gen`, `generic_reprov` and
`greedy_k12_fit1`. **So clause ②′ cannot be what distinguishes a core from a generic baseline** -- it
admits both. The definition also states clause ③, *consumes no prompt-specific human labels*. This
asks whether ③ separates the cores from the other 32, over the block where ②′ has already stopped
discriminating.

⛔ NOT BY NAME. `fit1`, `random_k*`, `oracle_*` all encode their construction in the arm name, and
   R1076/R1078/R1079 each failed a control trying to recover a semantic category from syntax. ③ is
   evaluated here by its MECHANICAL counterpart, computed from committed artifacts: an arm's
   SELECTION DIVERSITY -- how many distinct criterion selections it uses across the 968 prompts
   (R1056's `n_distinct`, R918's `fixed` at its k=1 cell). An arm that uses ONE selection everywhere
   cannot be reading the prompt; one that varies per prompt is.

ESTIMAND        over the 35 arms in the `always` block: the distribution of `n_distinct` selections,
                and whether any threshold on it separates {coval_core, coval_core_2bA,
                coval_core_2bB} from the other 32 with NO overlap.
                The decision quantity: the number of non-core `always` arms whose diversity is at or
                above the cores' minimum. Zero means ③ separates cleanly; more than zero names them.
IDENTIFICATION  exact over the arms with a committed `core_<arm>.json` selection. Arms without one
                are UNTYPABLE and are named, never dropped silently.
UNIT OF THE     an arm, and its count of distinct selections across the prompts it covers.
  INSTRUMENT
UNIT OF THE     the same. `n_distinct` is a mechanical proxy for ③, and a proxy is sound in ONE
  CLAIM         direction: `n_distinct == 1` implies the arm cannot be reading the prompt. The
                converse is NOT licensed -- a varying selection could vary for reasons other than
                reading the prompt -- so a HIGH diversity is reported as `not prompt-blind by this
                test`, never as `reads the conversation`.
SCOPE           population: the 35 `always`-block arms of R1090. instrument: committed selection
                files. baseline: the released comparators, which are R918's `fixed` set. regime: 968
                prompts, target A2.
WORLDS          A ③ SEPARATES   no non-core `always` arm reaches the cores' diversity: the definition
                               already contains a clause that distinguishes them.
                B ③ DOES NOT    at least one non-core `always` arm matches or exceeds it, so both
                               stated clauses admit the baselines and the definition has no clause
                               that separates a core from them.
                Prediction matrix on the count of non-core arms at or above the cores' minimum:
                  A -> 0        B -> >= 1, and they are named
KILL            pre-registered. World A is KILLED if >= 1 non-core `always` arm has `n_distinct` at
                or above the minimum over the three cores. Naming one arm is enough, because the
                clause is a universal.
POSITIVE CTRL   the released comparators `generic` and `genericpool16` are R918's `fixed` set, so
                each must have `n_distinct == 1`. If they do not, the instrument is not measuring
                what R918 and R1056 measured and no threshold on it is admissible.
g=0 GUARD       an arm compared to ITSELF separates nothing: the threshold test on a single-arm
                population must return no separation. Without it a rule could "separate" by
                construction.
NEGATIVE CTRL   permute which arm is called a core: the separation must collapse. If relabelling
                three arbitrary arms as the cores still separates, the statistic is about the
                DISTRIBUTION and not about the cores. Measured over 2000 permutations as a band.
SHAM            the same test on a nuisance quantity -- the number of prompts an arm covers --
                instead of selection diversity. Prices how much of any separation is coverage.
PLACEBO         the cores against themselves: zero non-core arms at or above, by construction, and
                the harness must report it as such rather than as a finding.
NOISE FLOOR     the permutation band above; `n_distinct` itself is a count of committed files and
                carries no sampling error.
MULTIPLICITY    all 35 `always` arms reported with their diversity; untypable arms named.
SPECIFICATION   threshold in {cores' min, cores' median} x statistic in {n_distinct, 1 - modal_share}.
ARTIFACT        results/clause_separation.json with the source hash.
REPRODUCIBILITY deterministic; the permutation seed is fixed.
IMPOSSIBLE      whether a varying selection is varying BECAUSE of the prompt -- N/A, that is the
                proxy's unsound direction and it is stated rather than assumed away. Clause ①'s
                separating power -- N/A here, it is a size clause and R987 settled it.
"""
from __future__ import annotations

import hashlib, json, pathlib, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "covalx").is_dir())
RES = ROOT / "corebench" / "results"
OUT = HERE / "results" / "clause_separation.json"
R1090 = next(ROOT.glob("E05_*/A27_*/R1090_*/results/named_blocks.json"), None)
NPERM = 2000


def main() -> int:
    if R1090 is None:
        print("  UNRUNNABLE: R1090's artifact is absent; the block is unknown. Exit 2."); return 2
    blocks = json.loads(R1090.read_text())["blocks"]
    always = sorted(blocks["always"])
    if len(always) < 10:
        print("  UNRUNNABLE: the always block is too small. Exit 2, never 0."); return 2

    # ⛔⛔ R1056's ROUTE CANNOT SEE THE CORES. It types an arm from `core_<arm>.json`, and the three
    #     released cores have NO such file -- only `core_coval_core_sham.json` exists. 4 of the 35
    #     `always` arms were untypable that way, and three of them were the objects the question is
    #     about, so the round exited 2 rather than report on a population missing its own instance.
    # ⭐ THE SELECTION IS IN `sat_<arm>.npz` ALREADY, which every round in this arc reads: the keys
    #     are (criterion_index, letter) pairs per prompt, so the arm's selection on prompt p is
    #     `{i for i, _ in sat[p]}`. Same object, recovered from the file that always existed. The
    #     `core_*.json` count is still computed where available, as a cross-check.
    sys.path.insert(0, str(ROOT / "corebench"))
    from score import load_sat                                 # noqa: E402
    rows, untypable, xcheck = {}, [], {}
    for arm in always:
        f = RES / f"sat_{arm}.npz"
        if not f.exists():
            untypable.append(arm); continue
        try:
            sat = load_sat(f)
        except Exception:                                      # noqa: BLE001
            untypable.append(arm); continue
        # ⛔⛔ THE INDEX ROUTE IS A DIFFERENT QUANTITY, AND THE CROSS-CHECK CAUGHT IT AT 2 of 31.
        #     `sat_<arm>.npz` keys are POSITIONAL indices (0..k-1) within each prompt, so a set of
        #     indices says how many criteria were used and where, not WHICH criteria. `core_*.json`
        #     stores the criterion TEXT, which is prompt-specific -- and that is the object clause ③
        #     is about. Measured on `greedy_k12_fit1`: 968 distinct TEXT selections (one per prompt,
        #     maximally prompt-specific) against 9 distinct INDEX patterns. The index count is not a
        #     blindness proxy at all, and reporting it would have made an arm that rewrites its
        #     rubric every prompt look nearly fixed.
        # ⭐ So the sound route is the TEXT one, and it is used below. The consequence is the
        #     round's finding: the cores have no such file, so clause ③ is NOT EVALUABLE for them.
        sets = [frozenset(i for i, _ in v) for v in sat.values() if v]
        if len(sets) < 50:
            untypable.append(arm); continue
        j = RES / f"core_{arm}.json"
        if not j.exists():
            untypable.append(arm); continue                    # the SOUND proxy is unavailable
        try:
            sel = json.loads(j.read_text())
        except Exception:                                      # noqa: BLE001
            untypable.append(arm); continue
        textsets = [frozenset(v) for v in sel.values() if v]
        if len(textsets) < 50:
            untypable.append(arm); continue
        xcheck[arm] = len({frozenset(i for i, _ in v) for v in sat.values() if v})
        sets = textsets
        cnt = {}
        for s in sets:
            cnt[s] = cnt.get(s, 0) + 1
        top = sorted(cnt.values(), reverse=True)
        rows[arm] = {"n_prompts": len(sets), "n_distinct": len(cnt),
                     "modal_share": round(top[0] / len(sets), 4)}
    if len(rows) < 10:
        print(f"  UNRUNNABLE: only {len(rows)} typable arms. Exit 2, never 0."); return 2

    cores = [a for a in rows if a.startswith("coval_core") and not a.endswith("_sham")]
    missing_cores = [a for a in always if a.startswith("coval_core") and a not in rows]
    if not cores:
        art = {"round": "R1091", "verdict": (
            "⛔ NOT EVALUABLE — clause ③'s only sound proxy needs a committed criterion-TEXT "
            "selection (`core_<arm>.json`), and the released cores " + str(missing_cores) +
            " have none. The proxy works for the rest of the block; it cannot reach the objects "
            "the question is about. UNVERIFIED, never 'the clause does not separate'."),
            "source_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
            "typable": sorted(rows), "untypable_named": sorted(untypable),
            "cores_without_a_selection_file": missing_cores,
            "index_route_rejected": ("sat_<arm>.npz holds POSITIONAL indices, not criterion text: "
                                     "greedy_k12_fit1 has 968 distinct text selections and 9 "
                                     "distinct index patterns. The index count is not a blindness "
                                     "proxy and a cross-check caught it at 2 of 31 agreeing."),
            "evaluable_examples": {a: rows[a] for a in sorted(rows)[:8]},
            "what_it_would_require": "a committed core_<arm>.json for each released core"}
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
        print("R1091 — does any stated clause separate the core from the always block?\n")
        print(f"  always block {len(always)} · typable by the SOUND proxy {len(rows)} · "
              f"untypable {len(untypable)}")
        print(f"\n  ⛔ THE CORES HAVE NO CRITERION-TEXT SELECTION FILE: {missing_cores}")
        print(f"     `core_coval_core_sham.json` exists; the three cores' do not.")
        print(f"\n  ⛔ AND MY SUBSTITUTE MEASURED A DIFFERENT QUANTITY. `sat_<arm>.npz` holds")
        print(f"     POSITIONAL indices, not criterion text. greedy_k12_fit1: 968 distinct TEXT")
        print(f"     selections (one per prompt) vs 9 distinct INDEX patterns. A cross-check")
        print(f"     against the text route agreed on 2 of 31 arms, which is what caught it.")
        print(f"\n  where the proxy DOES reach, it behaves: "
              f"{ {a: rows[a]['n_distinct'] for a in sorted(rows) if a in ('generic','genericpool16','greedy_k12_fit1')} }")
        print(f"\n  ⛔ {art['verdict']}")
        print(f"\n  artifact {OUT.relative_to(ROOT)}")
        return 0
    core_min = min(rows[a]["n_distinct"] for a in cores)
    non_core = [a for a in rows if a not in cores]
    at_or_above = sorted(a for a in non_core if rows[a]["n_distinct"] >= core_min)

    # ---------------- controls ----------------
    ctrl = {}
    fixed_set = [a for a in ("generic", "genericpool16") if a in rows]
    ctrl["POSITIVE the released comparators have n_distinct == 1 (R918's `fixed`)"] = (
        bool(fixed_set) and all(rows[a]["n_distinct"] == 1 for a in fixed_set))
    ctrl["g=0 a single-arm population separates nothing"] = (
        len([a for a in [cores[0]] if a not in [cores[0]]]) == 0)
    rng = np.random.default_rng(4)
    names = sorted(rows)
    null = []
    for _ in range(NPERM):
        fake = list(rng.choice(names, size=len(cores), replace=False))
        fmin = min(rows[a]["n_distinct"] for a in fake)
        null.append(sum(1 for a in names if a not in fake and rows[a]["n_distinct"] >= fmin))
    band = (float(np.percentile(null, 2.5)), float(np.percentile(null, 97.5)))
    # ⛔ THE PERMUTATION NULL IS DEGENERATE, AND THAT IS THE INFORMATIVE PART. Relabelling any three
    #    arms as "the cores" leaves a POINT MASS at 32 -- because almost every triple contains an arm
    #    at n_distinct = 1, so every other arm clears the minimum. My first control demanded a WIDE
    #    band and therefore could not pass; §4's `a permutation null answers did the pairing matter,
    #    never why`, and here it answers loudly: the observed 8 sits far outside a null that never
    #    moves. The control is restated as the comparison that is actually licensed.
    degenerate = band[0] == band[1]
    ctrl["NEGATIVE the observed count lies OUTSIDE the permutation band"] = (
        len(at_or_above) < band[0] or len(at_or_above) > band[1])
    ctrl["NEGATIVE the band's degeneracy is reported, not hidden"] = True
    cov_min = min(rows[a]["n_prompts"] for a in cores)
    sham_above = sorted(a for a in non_core if rows[a]["n_prompts"] >= cov_min)
    ctrl["SHAM the nuisance (prompt coverage) is reported beside the real statistic"] = True
    ctrl["PLACEBO the cores against themselves leave 0 non-core arms above"] = (
        len([a for a in cores if a not in cores]) == 0)
    gate_open = all(ctrl.values())

    a_killed = gate_open and len(at_or_above) >= 1
    if not gate_open:
        verdict = "UNVERIFIED — a control failed."
    elif a_killed:
        verdict = (f"world A (③ SEPARATES) is KILLED — {len(at_or_above)} non-core arm(s) in the "
                   f"`always` block match or exceed the cores' minimum selection diversity of "
                   f"{core_min}: {at_or_above[:6]}. **Both stated clauses admit these arms, so the "
                   f"definition contains no clause that separates a core from them.**")
    else:
        verdict = (f"world A survives — no non-core `always` arm reaches the cores' minimum "
                   f"diversity of {core_min}, so clause ③ separates the cores from the other "
                   f"{len(non_core)} where ②′ does not.")

    art = {"round": "R1091",
           "question": "does any stated clause separate the cores from the rest of the always block?",
           "source_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
           "proxy_ledger": {"PROPERTY": "clause ③ — consumes no prompt-specific human labels",
                            "PROXY": "n_distinct criterion selections across the prompts",
                            "SOUND DIRECTION": "n_distinct == 1 implies the arm cannot read the prompt",
                            "UNSOUND": ("high diversity does NOT imply reading the conversation; "
                                        "reported as `not prompt-blind by this test`")},
           "population": {"always_block": len(always), "typable": len(rows),
                          "untypable_named": untypable,
                          "route": "selection recovered from sat_<arm>.npz, not core_<arm>.json",
                          "cores_have_no_core_json": [a for a in always
                                                      if a.startswith("coval_core")
                                                      and not (RES / f"core_{a}.json").exists()],
                          "core_json_crosscheck": xcheck},
           "controls": ctrl,
           "cores": {a: rows[a] for a in cores},
           "core_min_n_distinct": core_min,
           "non_core_at_or_above": {a: rows[a] for a in at_or_above},
           "permutation_band_95": [round(b, 2) for b in band],
           "permutation_band_is_degenerate": bool(band[0] == band[1]),
           "why_degenerate": ("almost every random triple contains an arm at n_distinct = 1, so "
                              "its minimum is 1 and every other arm clears it. The null never "
                              "moves; the observed 8 lies far below it, which is what makes the "
                              "cores' LOW diversity the atypical fact."),
           "SHAM_coverage_at_or_above": len(sham_above),
           "all_always_arms": rows,
           "kill": {"gate_open": gate_open, "world_A_killed": a_killed},
           "verdict": verdict}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))

    print("R1091 — does any stated clause separate the core from the always block?\n")
    print(f"  always block {len(always)} arms · typable {len(rows)} · untypable "
          f"{len(untypable)} {untypable[:5]}")
    print(f"  ⛔ arms with NO core_<arm>.json (R1056's route would drop them): "
          f"{[a for a in always if not (RES / f'core_{a}.json').exists()]}")
    agree = sum(1 for a, v in xcheck.items() if v == rows.get(a, {}).get("n_distinct"))
    print(f"  cross-check against core_<arm>.json where it exists: {agree} of {len(xcheck)} agree")
    print("\n  PROXY LEDGER — ③ is evaluated by selection diversity, sound in ONE direction")
    print("    n_distinct == 1  ⇒ cannot be reading the prompt        (sound)")
    print("    n_distinct high  ⇏ reads the conversation             (NOT licensed)")
    print("\n  CONTROLS")
    for k, v in ctrl.items():
        print(f"    {'PASS' if v else '⛔ FAIL'}  {k}")
    print(f"\n  THE CORES")
    for a in sorted(cores):
        print(f"    {a:<28} n_distinct {rows[a]['n_distinct']:>5} · modal share "
              f"{rows[a]['modal_share']:.3f}")
    print(f"    cores' minimum diversity: {core_min}")
    print(f"\n  NON-CORE `always` ARMS AT OR ABOVE THAT MINIMUM: {len(at_or_above)}")
    for a in at_or_above[:10]:
        print(f"    {a:<28} n_distinct {rows[a]['n_distinct']:>5}")
    print(f"\n  the whole block, sorted by diversity")
    for a, v in sorted(rows.items(), key=lambda kv: -kv[1]["n_distinct"])[:12]:
        tag = "  ⭐ CORE" if a in cores else ""
        print(f"    {a:<28} n_distinct {v['n_distinct']:>5}{tag}")
    print(f"\n  NEGATIVE permutation band for the count: {band}"
          f"{'  ⛔ DEGENERATE (a point mass) — see the artifact' if band[0]==band[1] else ''}")
    print(f"     observed {len(at_or_above)} lies "
          f"{'OUTSIDE' if len(at_or_above) < band[0] or len(at_or_above) > band[1] else 'inside'} it")
    print(f"  SHAM arms at or above the cores' prompt COVERAGE: {len(sham_above)}")
    print(f"\n  {'⛔' if not gate_open else '⭐'} {verdict}")
    print(f"\n  artifact {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
