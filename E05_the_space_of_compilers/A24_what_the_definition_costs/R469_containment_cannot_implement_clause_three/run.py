"""R469 -- containment CANNOT implement ③, and it is a derivation. The UNKNOWN region is permanent.

⛔ RUNG 1 KILLS THE ANNOUNCED CONFUSION MATRIX TWICE, ZERO COMPUTE. R468 closed proposing to run
   "the SELECTOR verdict as reference and containment as candidate, and report the confusion matrix".
   ① UNIT MISMATCH: the selector verdict is per ARM (101 values from `clause3_as_written`);
     containment is per PROMPT (968 values). A confusion matrix between them is ill-typed -- §4's
     unit-equality, this time in my own announced plan.
   ② AND AT ARM LEVEL IT IS FORCED: **every selector in `select_core.py` draws from the prompt's own
     rubric** -- the ③-EXCLUDED ones (`oracle_k`, `indep_k`, `greedy_k`, `topw_k`, `topabs_k`,
     `topwvar_k`) and the ③-ADMITTED ones (`random_k`, `full`, `topvar_k`) alike. So containment is
     ~1.0 for BOTH classes by construction and the matrix is degenerate.
   *Thirty-seventh announced step checked; killed on both counts before any compute.*

⭐ SO THE QUESTION BECOMES SHARPER, AND IT CLOSES THE ARC. If containment is 1.0 for excluded and
   admitted alike, containment does not merely FAIL to validate against ③ -- **it is provably unable
   to implement it**, because it is constant on the very partition ③ makes. That converts R466's
   UNVERIFIED from "not yet decided" into "not decidable BY THIS INSTRUMENT", which is a different
   and more useful statement.

⚠ AND A DERIVATION MUST BE CONFIRMED CHEAPLY RATHER THAN ASSERTED. The premise is a claim about
  `select_core.py`; the confirmation is a measurement over the arms it built, using R468's join so
  the rubric is the RIGHT one for each prompt.

ESTIMAND (named before the method)
    For each arm with criterion texts, using R468's exact id map:
        CONTAIN(arm) = mean over prompts of the fraction of that arm's criteria appearing VERBATIM
                       in that prompt's own rubric.
    Grouped by `clause3_as_written`'s verdict: EXCLUDED / ADMITTED / UNKNOWN.
    ⭐ SEPARATION = |mean CONTAIN(EXCLUDED) - mean CONTAIN(ADMITTED)|. If ~0, containment is constant
      on ③'s partition and cannot implement it -- the derivation, confirmed.

IDENTIFICATION
    Identified: R468's map is total (968 of 968, uniqueness 1.0) so every arm's criteria can be
    checked against the correct rubric. ⚠ NOT identified: whether some OTHER instrument could
    implement ③ -- this round rules out one, and says so.

SCOPE  population : arms with `core_*.json` texts, joined via R468's id_map.json
       instrument : exact verbatim containment in the joined rubric
       baseline   : the released core's committed 0.0779 and the cross-prompt sham's 0.0000
       regime     : whitespace-normalised lowercase, exact match only

WORLDS
    W-DEGENERATE   separation ~0 -> containment is constant on ③'s partition; it cannot implement ③,
                   the 19-arm UNKNOWN region is not decidable by it, and the definition's third
                   verdict is permanent rather than provisional.
    W-SEPARATES    separation is large -> containment DOES track ③ and the UNKNOWN region can be
                   classified, contradicting the derivation above.
    W-INVERTED     EXCLUDED arms have LOWER containment than ADMITTED -> the instrument tracks
                   something real but with the opposite sign, and neither reading survives.

PREDICTION MATRIX
                   separation ~0   large, correct sign   inverted
    W-DEGENERATE        0.90             0.05              0.05
    W-SEPARATES         0.05             0.90              0.05
    W-INVERTED          0.05             0.05              0.90

PRE-REGISTERED KILL -- CONDITIONAL. Binding only if the controls fire.
    separation <= 0.10                         -> W-DEGENERATE
    separation > 0.10 and EXCLUDED higher      -> W-SEPARATES
    separation > 0.10 and ADMITTED higher      -> W-INVERTED
    a control fails                            -> UNVERIFIED

CONTROLS
    ANCHOR    `coval_core` must reproduce its committed containment 0.0779 under the JOINED rubric.
              ⭐ This is a stronger anchor than R466's: R466 read the core from the rubric file's own
              record, so its 0.0778 could not have been wrong. Here the core's texts come from the
              RANKING space and the rubric from the RUBRIC space, joined -- so reproducing 0.0779
              also validates the join a third time, on a third channel.
    FLOOR     a cross-prompt sham must return ~0.0000.
    POSITIVE  `full` -- every rubric criterion -- must return 1.0000. Without it a low number is
              silence: an instrument that never returns 1.0 cannot certify a 0.
    g=0       an arm against its OWN texts returns 1.0 BY CONSTRUCTION -- a DERIVATION.
    SPREAD    the per-arm containment distribution is printed WITHIN each verdict class, because a
              class mean of 1.0 with zero spread is a derivation and a class mean of 1.0 with spread
              is a measurement.

MULTIPLICITY  every arm with texts, grouped into 3 classes; all printed, nothing selected.
ARTIFACT      results/r469_containment_degenerate.json
IMPOSSIBLE HERE, NAMED
    * ruling out every possible ③-instrument -- this rules out ONE, by showing it constant on ③'s
      partition. Another instrument would need its own round.
    * classifying the UNKNOWN arms -- that is precisely what this round shows containment cannot do.
"""
from __future__ import annotations
import json, pathlib, re, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / "results"
SATD = ROOT / "corebench" / "results"
sys.path.insert(0, str(ROOT / "assurance")); sys.path.insert(0, str(ROOT))
MAP = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs" / \
      "R468_the_join_exists_and_is_exact" / "results" / "id_map.json"
CORE_COMMITTED = 0.0779


def nrm(s): return re.sub(r"\s+", " ", str(s)).strip().lower()


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    from clause3_as_written import partition
    print("R469 · containment CANNOT implement ③ — and it is a DERIVATION\n")
    print("  ⛔ RUNG 1 killed the announced confusion matrix TWICE, zero compute:")
    print("     ① UNIT MISMATCH — selector verdict is per ARM, containment per PROMPT.")
    print("     ② FORCED — every selector in select_core.py draws from the prompt's OWN rubric,")
    print("        the ③-excluded ones AND the ③-admitted ones, so containment is ~1.0 for both")
    print("        classes by construction. Thirty-seventh step checked.\n")

    if not MAP.exists():
        print("  UNRUNNABLE: R468's id_map.json absent. Exit 2, never 0."); return 2
    idmap = json.loads(MAP.read_text())
    RUB = {}
    with (ROOT / "data" / "conversation_rubrics.jsonl").open() as fh:
        for line in fh:
            r = json.loads(line); cid = (r.get("conversation") or {}).get("id")
            cs = {nrm(x["criterion"]) for x in r.get("coval_full", []) if x.get("criterion")}
            if cid and cs: RUB[cid] = cs
    print(f"  id map {len(idmap)} pairs;  rubric records {len(RUB)}")

    arms = {}
    for f in sorted(SATD.glob("core_*.json")):
        nm = f.name[5:-5]
        try:
            d = json.loads(f.read_text())
        except Exception:
            continue
        if isinstance(d, dict) and d:
            arms[nm] = {k: [nrm(x) for x in v] for k, v in d.items() if isinstance(v, list)}
    print(f"  arms with criterion texts: {len(arms)}")
    if len(arms) < 5:
        print("  UNRUNNABLE: too few arms carry texts. Exit 2."); return 2

    def contain(a, wrong=False, off=1):
        vals = []
        pids = sorted(arms[a])
        for i, p in enumerate(pids):
            q = pids[(i + off) % len(pids)] if wrong else p
            r = idmap.get(q)
            if r is None or r not in RUB: continue
            ts = arms[a][p]
            if ts: vals.append(np.mean([t in RUB[r] for t in ts]))
        return float(np.mean(vals)) if vals else float("nan"), len(vals)

    exc, adm, unk = partition(list(arms))
    print("\n  CONTROLS")
    # ⛔ THE ANCHOR AS DESIGNED IS UNAVAILABLE, AND THAT IS REPORTED RATHER THAN WORKED AROUND.
    #    It was to read the core's texts from the RANKING space and the rubric from the RUBRIC
    #    space, so reproducing 0.0779 would have validated R468's join a THIRD time on a third
    #    channel. But there is no `core_coval_core.json`: the released core's texts exist ONLY in
    #    conversation_rubrics.jsonl, in rubric space. The anchor therefore runs WITHIN one space and
    #    validates the containment instrument WITHOUT validating the join. Weaker than designed,
    #    stated as such, and the round's first version correctly exited 2 rather than proceed.
    CORE_R = {}
    with (ROOT / "data" / "conversation_rubrics.jsonl").open() as fh:
        for line in fh:
            r = json.loads(line); cid = (r.get("conversation") or {}).get("id")
            cs = [nrm(x["criterion"]) for x in r.get("coval_core", []) if x.get("criterion")]
            if cid and cs: CORE_R[cid] = cs
    vals = [np.mean([t_ in RUB[cid] for t_ in ts]) for cid, ts in CORE_R.items() if cid in RUB]
    c = float(np.mean(vals)); a_ok = abs(c - CORE_COMMITTED) < 0.01
    print(f"    ANCHOR    `coval_core` containment {c:.4f} vs committed {CORE_COMMITTED} "
          f"(n={len(vals)})   {'PASS' if a_ok else '⛔ FAIL'}")
    print(f"              ⚠ WITHIN the rubric space -- there is no `core_coval_core.json`, so this")
    print(f"                validates the INSTRUMENT and NOT the join, which is weaker than the")
    print(f"                third-channel check this round was designed to run")
    ids = sorted(CORE_R)
    sv = [np.mean([t_ in RUB[ids[(i + 1) % len(ids)]] for t_ in CORE_R[cid]])
          for i, cid in enumerate(ids) if ids[(i + 1) % len(ids)] in RUB]
    s = float(np.mean(sv)); f_ok = s < 0.01
    print(f"    FLOOR     cross-prompt sham {s:.4f}   {'PASS' if f_ok else '⛔ FAIL'}")

    if "full" in arms:
        p_, _ = contain("full")
        p_ok = p_ > 0.95
        print(f"    POSITIVE  `full` (every rubric criterion) {p_:.4f}   "
              f"{'PASS' if p_ok else '⛔ FAIL — a low number would be silence'}")
    else:
        p_, p_ok = float("nan"), False
        print("    ⛔ `full` absent — the positive control cannot run.")
    print(f"    g=0       an arm against its OWN texts is 1.0 BY CONSTRUCTION — a DERIVATION")

    print("\n  ⭐ CONTAINMENT BY ③'s OWN VERDICT CLASS")
    res = {}
    for nm, group in (("EXCLUDED", exc), ("ADMITTED", adm), ("UNKNOWN", unk)):
        vs = []
        for a in group:
            if a in arms:
                c, _ = contain(a)
                if np.isfinite(c): vs.append((a, c))
        if not vs:
            res[nm] = None; print(f"    {nm:<9} (no arms with texts)"); continue
        m = float(np.mean([c for _, c in vs])); sd = float(np.std([c for _, c in vs]))
        res[nm] = {"n": len(vs), "mean": m, "sd": sd,
                   "min": float(min(c for _, c in vs)), "max": float(max(c for _, c in vs))}
        print(f"    {nm:<9} n={len(vs):>3}  mean {m:.4f}  sd {sd:.4f}  "
              f"[{res[nm]['min']:.4f},{res[nm]['max']:.4f}]")

    ctrl_ok = a_ok and f_ok and p_ok
    if not ctrl_ok or res["EXCLUDED"] is None or res["ADMITTED"] is None:
        world = "UNVERIFIED"
    else:
        sep = res["EXCLUDED"]["mean"] - res["ADMITTED"]["mean"]
        print(f"\n    SEPARATION  EXCLUDED - ADMITTED = {sep:+.4f}")
        if abs(sep) <= 0.10: world = "W-DEGENERATE"
        elif sep > 0: world = "W-SEPARATES"
        else: world = "W-INVERTED"
    print(f"\n  WORLD: {world}")
    if world == "W-DEGENERATE":
        print(f"    ⭐ THE DERIVATION IS CONFIRMED. Containment is essentially CONSTANT on ③'s own")
        print(f"       partition, so it cannot implement ③ — not 'unvalidated', **provably unable**.")
        print(f"    ⭐ That converts R466's UNVERIFIED from 'not yet decided' into 'NOT DECIDABLE BY")
        print(f"       THIS INSTRUMENT', and it makes the definition's THIRD VERDICT permanent for")
        print(f"       the 19-arm UNKNOWN region rather than provisional.")
        print(f"    ⚠ It rules out ONE instrument. Another would need its own round.")

    sha = subprocess.run(["git", "hash-object", __file__], capture_output=True, text=True).stdout.strip()
    out = {"source_sha": sha, "world": world, "n_arms": len(arms), "classes": res,
           "anchor_core": c, "committed": CORE_COMMITTED, "floor_sham": s, "positive_full": p_,
           "n_map": len(idmap)}
    (RES / "r469_containment_degenerate.json").write_text(json.dumps(out, indent=2))
    print(f"\n  artifact: {RES/'r469_containment_degenerate.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
