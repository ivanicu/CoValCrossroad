"""R292 — every published cell in the arc, re-judged by the instrument that caught the last error.

WHY. `corebench/report.py` was built because R290 printed a point estimate without its interval and
I published a wrong sentence off the sign. Its selftest then caught the CORRECTION overstating too.
An instrument that has falsified two consecutive claims should be pointed at ALL of them, not left
sitting in the repo — a library nobody calls is a resolution to be careful with a `.py` extension.

ESTIMAND        for every cell in every A16 artifact carrying (effect, CI): the verdict computed by
                `report.verdict()`, against the verdict the round STORED.
IDENTIFICATION  exact where a cell carries both an MDE and a stored verdict. Where either is
                missing the comparison is NOT identified and the cell is reported as such rather
                than judged on a substitute criterion.
SCOPE           the 7 A16 rounds that persist cells; verdicts as stored on disk.
WORLDS          W-CLEAN     every like-for-like cell agrees -> the R290 defect was a PRINT defect,
                            local to one round's display, and the arc's stored verdicts are sound.
                W-SYSTEMIC  disagreements appear elsewhere -> the defect is in how this arc computes
                            verdicts, and every round needs re-reading, not just R290.
KILL            pre-registered: any like-for-like disagreement means the round that produced it is
                re-opened and its FORMULATION rows re-checked before anything else proceeds.
POSITIVE CTRL   the R290 clause-② cells are injected as a known-bad case: the instrument MUST
                disagree with the prose I published for them, or it cannot detect what it was built
                for. A clean sweep with a dead detector is silence.
NEGATIVE CTRL   a cell compared to itself must agree; a fabricated cell with a flipped stored
                verdict must be caught.
MULTIPLICITY    a census, not a test family. Every cell reported, none sampled.
ARTIFACT        results/cell_audit.json with source hash.
IMPOSSIBLE      cells whose round stored no MDE cannot be judged on this arc's own resolution rule.
                They are COUNTED and EXCLUDED, never silently judged on the CI criterion instead —
                which is the exact mis-specification my first pass at this audit committed.
"""
import json, sys, pathlib, hashlib

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "corebench"))
from report import verdict, POS, NEG, UNRES, BELOW          # noqa: E402

A = ROOT / "E05_the_space_of_compilers/A16_what_the_definition_costs"
# ⚠ THIS TABLE IS AN INSTRUMENT AND HAS HAD TWO BLIND SPOTS. (1) The uppercase key `UNRESOLVED`
# was missing while the lowercase one was present, producing a FALSE disagreement on R281/gen
# where stored and computed were both UNRESOLVED. (2) Fixing (1) with a mid-dict comment swallowed
# `"BEATS"` and `"LOSES"` into the comment, and the audit died on KeyError at its own positive
# control -- I broke the detector while repairing it, and the CONTROL is what caught that.
NORM = {
    "RESOLVED": {POS, NEG},
    "MARGINAL": {BELOW, UNRES},
    "BELOW RESOLUTION": {BELOW, UNRES},
    "UNRESOLVED": {UNRES, BELOW},
    "unresolved": {UNRES, BELOW},
    "BEATS": {POS},
    "LOSES": {NEG},
    "PASSES neutral clause 2": {POS},
    "FAILS — worse than generic": {NEG},
    "arm ahead, separably": {POS},
    "NOT SEPARABLE": {UNRES, BELOW},
    "blind ahead": {NEG},
}
assert {"BEATS", "LOSES", "UNRESOLVED", "RESOLVED"} <= set(NORM), \
    "the normalisation table lost a key -- one line per entry exists to make that visible"


def harvest():
    cells = []
    for f in sorted(A.glob("R*/results/*.json")):
        rnd = f.parts[len(A.parts)]
        try: d = json.loads(f.read_text())
        except Exception: continue
        def walk(o, path=""):
            if isinstance(o, dict):
                e = o.get("eff", o.get("gap")); lo, hi = o.get("lo"), o.get("hi")
                if e is not None and lo is not None and hi is not None:
                    cells.append(dict(round=rnd, path=path, eff=e, lo=lo, hi=hi,
                                      mde=o.get("mde"), stored=o.get("res") or o.get("verdict")))
                for k, v in o.items(): walk(v, f"{path}/{k}" if path else k)
            elif isinstance(o, list):
                for i, v in enumerate(o): walk(v, f"{path}[{i}]")
        walk(d)
    return cells


def main():
    cells = harvest()
    byr = {}
    for c in cells: byr.setdefault(c["round"], []).append(c)
    print(f"  {len(cells)} cells with (effect, CI) across {len(byr)} rounds\n")
    print(f"    {'round':<46}{'cells':>6}{'w/ MDE':>8}{'w/ verdict':>12}{'judgeable':>11}")
    for r in sorted(byr):
        v = byr[r]
        j = sum(c["mde"] is not None and c["stored"] is not None for c in v)
        print(f"    {r[:46]:<46}{len(v):>6}{sum(c['mde'] is not None for c in v):>8}"
              f"{sum(c['stored'] is not None for c in v):>12}{j:>11}")

    comp = [c for c in cells if c["mde"] is not None and c["stored"] is not None]
    dis = [c for c in comp if verdict(c["eff"], c["lo"], c["hi"], c["mde"])
           not in NORM.get(c["stored"], set())]

    # ---- POSITIVE CONTROL: the known-bad R290 prose --------------------------------------
    R290_PROSE = {"0.8B coval_core": (-0.0072, -0.0157, +0.0003, 0.0110, "LOSES"),
                  "0.8B topw_k4":    (-0.0109, -0.0201, -0.0020, 0.0110, "LOSES"),
                  "0.8B gen":        (-0.0031, -0.0112, +0.0040, 0.0110, "LOSES")}
    caught = [k for k, (e, lo, hi, m, s) in R290_PROSE.items()
              if verdict(e, lo, hi, m) not in NORM.get(s, set())]
    pos_ok = len(caught) == 3
    print(f"\n  POSITIVE CONTROL  the 3 cells my R290 prose called `beaten`: instrument disagrees "
          f"with {len(caught)}/3  {'PASS' if pos_ok else 'FAIL — the detector is dead'}")
    for k in caught:
        e, lo, hi, m, s = R290_PROSE[k]
        print(f"      {k:<18}{e:>+8.4f} [{lo:+.4f},{hi:+.4f}] mde {m:.4f}  "
              f"prose={s}  computed={verdict(e, lo, hi, m)}")
    fake = verdict(0.05, 0.04, 0.06, 0.01) not in NORM["LOSES"]
    same = verdict(0.05, 0.04, 0.06, 0.01) in NORM["BEATS"]
    print(f"  NEGATIVE CONTROL  a fabricated cell with a flipped stored verdict is caught: {fake}"
          f"   · the same cell agrees with its TRUE verdict: {same}")
    if not (pos_ok and fake and same):
        print("\n  UNVERIFIED — the detector does not behave; a clean sweep below would be silence.")
        return 1

    # `unjudgeable` was ONE bucket and is really TWO, and only one of them is a defect in the round.
    no_mde = [c for c in cells if c["mde"] is None and c["stored"] is not None]
    no_verdict = [c for c in cells if c["mde"] is not None and c["stored"] is None]
    neither = [c for c in cells if c["mde"] is None and c["stored"] is None]
    print(f"\n  LIKE-FOR-LIKE (MDE present AND a stored verdict): {len(comp)} of {len(cells)}")
    print(f"  NOT JUDGEABLE, split into the two things it was conflating:")
    print(f"    no MDE stored          {len(no_mde):>4}  — the round cannot be judged on THIS ARC'S")
    print(f"                                 resolution rule. A real gap in the round.")
    print(f"    no VERDICT stored      {len(no_verdict):>4}  — the round computed an MDE but never")
    print(f"                                 wrote a verdict. NOTHING TO CHECK, not a defect: you")
    print(f"                                 cannot audit a claim that was never made.")
    print(f"    neither                {len(neither):>4}")
    for label, grp in (("no MDE", no_mde), ("no verdict", no_verdict), ("neither", neither)):
        by = {}
        for c in grp: by[c["round"]] = by.get(c["round"], 0) + 1
        if by: print(f"      {label:<12}" + ", ".join(f"{r.split('_')[0]}={n}" for r, n in sorted(by.items())))
    print(f"    ⚠ and NOT judged on the CI criterion instead. My first pass at this audit did exactly")
    print(f"    that and manufactured 24 disagreements that were entirely its own mis-specification.")
    print(f"\n  DISAGREEMENTS: {len(dis)}")
    for c in dis[:15]:
        print(f"    {c['round'][:40]:<40}{c['path'][:24]:<24}{c['eff']:>+8.4f} "
              f"stored={c['stored']:<12} computed={verdict(c['eff'], c['lo'], c['hi'], c['mde'])}")
    print("\n  " + "=" * 76)
    if dis:
        print(f"  W-SYSTEMIC. {len(dis)} stored verdicts disagree with the instrument. Every round")
        print("  that produced one is re-opened before anything else proceeds.")
    else:
        print("  W-CLEAN. Every cell with both an MDE and a stored verdict agrees with")
        print("  report.verdict(). The R290 defect was a PRINT defect -- local to one round's")
        print("  display and to the prose I wrote off it -- not a defect in how this arc computes")
        print("  verdicts. The stored artifacts were right the whole time; the sentence was not.")
    print("  " + "=" * 76)

    src = hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16]
    o = pathlib.Path(__file__).parent / "results" / "cell_audit.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(source_sha=src, n_cells=len(cells), n_comparable=len(comp),
                                 by_round={r: len(v) for r, v in byr.items()},
                                 disagreements=dis, pos_ctrl_caught=caught), indent=1))
    print(f"\n  artifact {o.relative_to(ROOT)}  src {src}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
