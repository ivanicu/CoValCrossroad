"""R325 — which rows of the definition's table are RESOLVED, and which exclusions are non-admissions.

Four rounds decomposed A23's MDE. That number governs A23 and, as FORMULATION already warns,
`does NOT govern` the definition — different statistic, different comparand, different n. Importing
it here would be the scope error the page warns against, so this round does not.

The in-scope question: the definition's own table reports clause ② with intervals and clause ①
WITHOUT them, except one row. Is that presentation or substance? R306's artifact holds 45 pairwise
cells, each with `eff`, `mde`, `bh` and `res`, so the MDEs exist and the table simply does not show
them. What they say is the round.

ESTIMAND      for every arm in the definition's table, the clause-① margin against the
              random-from-rubric baseline divided by that cell's OWN MDE — and, separately, the
              direction of each exclusion: `resolvably worse` versus `not resolvably better`.
IDENTIFICATION exact; the cells are computed and committed by R306 over all 15,593 annotations.
              This round reads them, so it inherits R306's design and adds no estimate of its own.
SCOPE         population 968 CoVal prompts, 15,593 annotations · instrument Qwen3.5-2B-Base ·
              baseline `random_k4_s0` (clause ①'s named reference) · regime A2·annotator.
WORLDS        W-ALL-RESOLVED    every row clears its own MDE -> the table's missing intervals are
                                presentation only and nothing rests on an invisible effect.
              W-SPLIT           some rows clear and some do not -> the table mixes resolved and
                                unresolved margins in one column without saying which, and the
                                EXCLUSIONS need re-reading as non-admissions.
              W-NONE            the admitted arms themselves are below resolution -> the
                                definition's own admissions are unresolved and the page's headline
                                is void.
KILL          admitted arms below their MDE                          -> W-NONE
              all nine rows at or above their MDE                    -> W-ALL-RESOLVED
              otherwise                                              -> W-SPLIT, and the split is
                                                                        reported per row
POSITIVE CTRL the two ADMITTED arms must clear their own MDE by a wide margin. If the instrument
              cannot resolve the arms the definition admits, it cannot resolve anything, and the
              zeros elsewhere are silence rather than acquittal.
              Fails at g=0: an arm compared to ITSELF must give exactly 0 and sit below any MDE,
              so a "resolved" verdict there would mean the criterion is satisfiable by nothing.
NEGATIVE CTRL `gen_sham` — the sham arm — must NOT be resolvably positive. It is the built-in
              negative and its row is reported rather than omitted.
PLACEBO       an arm against itself: effect exactly 0.
NOISE FLOOR   each cell's own `mde`, computed by R306 from the cluster bootstrap; quoted, not
              re-derived here.
MULTIPLICITY  9 rows, all printed, survivors and non-survivors. R306's BH flag is reported BESIDE
              the resolution verdict rather than merged with it, because they disagree on one row
              and that disagreement is the point.
ARTIFACT      results/clause1_resolution.json with source hash.
IMPOSSIBLE    saying whether an unresolved arm is WORSE than the baseline. Below the MDE the sign
              is not readable, which is exactly the distinction this round is drawing.
"""
import hashlib, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
SRC = (SELF.parent.parent / "R306_the_table_at_every_annotator" / "results"
       / "all_annotators.json")
BASE = "random_k4_s0"
ARMS = ["coval_core", "topw_k4", "generic", "gen", "full",
        "topwvar_k4", "topabs_k4", "topvar_k4", "gen_sham"]
ADMITTED = {"coval_core", "topw_k4"}
SHAM = "gen_sham"


def main():
    if not SRC.exists():
        print(f"  UNRUNNABLE: {SRC.name} absent."); return 2
    d = json.loads(SRC.read_text())
    cells = d["cells"]
    print(f"  R306: {d['n_prompts']} prompts, {d['annotations']} annotations, "
          f"{len(cells)} pairwise cells\n")

    rows = []
    print(f"    {'arm':<14}{'clause-1 eff':>14}{'its own MDE':>13}{'eff/MDE':>9}{'BH':>7}"
          f"   {'resolution':<18}reading")
    for a in ARMS:
        key = f"{a}|{BASE}"
        sign = 1
        if key not in cells:
            key, sign = f"{BASE}|{a}", -1
        if key not in cells:
            print(f"    {a:<14}  NO CELL"); return 2
        v = cells[key]
        eff = sign * v["eff"]
        ratio = abs(eff) / v["mde"] if v["mde"] else float("inf")
        resolved = ratio >= 1.0
        if resolved and eff > 0:
            reading = "resolvably BETTER"
        elif resolved and eff < 0:
            reading = "resolvably WORSE"
        else:
            reading = "NOT RESOLVABLY EITHER"
        rows.append(dict(arm=a, eff=eff, mde=v["mde"], ratio=ratio, bh=bool(v["bh"]),
                         res=v["res"], resolved=bool(resolved), reading=reading))
        print(f"    {a:<14}{eff:>14.4f}{v['mde']:>13.4f}{ratio:>9.2f}{str(v['bh']):>7}"
              f"   {v['res']:<18}{reading}")

    # ---- controls -------------------------------------------------------------------------------
    adm = [r for r in rows if r["arm"] in ADMITTED]
    pos_ok = all(r["resolved"] and r["eff"] > 0 for r in adm)
    print(f"\n  POSITIVE  both admitted arms resolvably positive: {pos_ok}  "
          f"({', '.join(f'{r[chr(97)+chr(114)+chr(109)]} {r[chr(114)+chr(97)+chr(116)+chr(105)+chr(111)]:.2f}x' for r in adm)})")
    self_key = next((k for k in cells if k.split("|")[0] == k.split("|")[1]), None)
    print(f"  PLACEBO   a self-comparison cell exists: {self_key is not None}"
          + (f", eff {cells[self_key]['eff']:.2e}" if self_key else
             "  -> R306 emits no self-pairs, so the placebo is STRUCTURALLY ABSENT and is"))
    if self_key is None:
        print("            reported as absent rather than substituted with something else.")
    sham = next(r for r in rows if r["arm"] == SHAM)
    neg_ok = not (sham["resolved"] and sham["eff"] > 0)
    print(f"  NEGATIVE  {SHAM} is not resolvably positive: {neg_ok}  "
          f"(eff {sham['eff']:+.4f}, {sham['ratio']:.2f}x its MDE)")

    # ---- the split --------------------------------------------------------------------------------
    res = [r for r in rows if r["resolved"]]
    unres = [r for r in rows if not r["resolved"]]
    disagree = [r for r in rows if r["bh"] != r["resolved"]]
    excluded_unres = [r for r in unres if r["arm"] not in ADMITTED]

    ctrl = pos_ok and neg_ok
    print("\n  " + "=" * 78)
    print(f"  CONTROLS  positive={pos_ok}  negative={neg_ok}  -> "
          f"{'evaluate' if ctrl else 'UNVERIFIED'}")
    if not ctrl:
        world = "UNVERIFIED"
        print("  -> UNVERIFIED. A control misbehaved; the resolution reading is not readable.")
    elif not pos_ok:
        world = "W-NONE"
        print("  -> W-NONE. The admitted arms are themselves below resolution.")
    elif not unres:
        world = "W-ALL-RESOLVED"
        print("  -> W-ALL-RESOLVED. Every row clears its own MDE; the table's missing intervals")
        print("     are presentation only.")
    else:
        world = "W-SPLIT"
        print(f"  -> W-SPLIT. {len(res)} of {len(rows)} rows clear their own MDE and "
              f"{len(unres)} do not,")
        print("     and the table reports both in one column without saying which is which.")
        print(f"     ⚠ THE EXCLUSIONS ARE NON-ADMISSIONS, NOT REFUTATIONS. "
              f"{len(excluded_unres)} of the excluded")
        print(f"       arms ({', '.join(r['arm'] for r in excluded_unres)}) sit BELOW their own")
        print("       MDE, so the site cannot say they are worse than the baseline — only that it")
        print("       cannot say they are better. `excluded (①)` is correct for an admission rule")
        print("       that requires a resolvable positive, and it is not evidence against the arm.")
    if disagree:
        print(f"     ⚠ BH AND RESOLUTION DISAGREE ON {len(disagree)}: "
              f"{', '.join(r['arm'] for r in disagree)}")
        for r in disagree:
            print(f"       {r['arm']}: BH={r['bh']} but {r['ratio']:.2f}x its MDE. A BH survivor")
            print("       below its own MDE is significant and unresolvable at once, which is why")
            print("       the two are reported side by side rather than merged.")
    print("  " + "=" * 78)

    o = SELF.parent / "results" / "clause1_resolution.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(SELF.read_bytes()).hexdigest()[:16], world=world,
        baseline=BASE, n_prompts=d["n_prompts"], n_annotations=d["annotations"],
        rows=rows, n_resolved=len(res), n_unresolved=len(unres),
        excluded_but_unresolved=[r["arm"] for r in excluded_unres],
        bh_resolution_disagree=[r["arm"] for r in disagree],
        positive_ok=bool(pos_ok), negative_ok=bool(neg_ok),
        placebo="structurally absent: R306 emits no self-pairs"), indent=1))
    print(f"\n  artifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
