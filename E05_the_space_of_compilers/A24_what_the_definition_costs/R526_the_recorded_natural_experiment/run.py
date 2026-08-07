#!/usr/bin/env python3
"""R526 — does --select-npz actually change identity, where the invocation IS recorded?

R525 inferred that three home-judge variant pairs were "failed runs" because their rule consumes
satisfaction and they came out byte-identical. That inference rests on an UNRECORDED invocation.
⛔ My closing line then said the only place that could settle the remaining tags is "whatever
produced them" -- fifth wall of that shape, and false: corebench/rebuild_selection_08b.sh
records a natural experiment for exactly this mechanism.

  frozen() { select_core.py --full-npz 0.8B --select-npz 2B --tag-suffix _08b  ... }
  rerun()  { select_core.py --full-npz 0.8B                 --tag-suffix _08bR ... }

Five arms get BOTH treatments, and all five are satisfaction-CONSUMING rules. The source says
those "change IDENTITY, not just score" when the rule is re-run under a different judge. So
_08b and _08bR must differ for all five.

ESTIMAND (before method): the number of the five paired arms whose _08b and _08bR artifacts are
  byte-identical -- i.e. where re-running the rule under a different judge changed nothing.
IDENTIFICATION: fully identified. Both artifacts exist; the invocations are in the shell script.
SCOPE  population: the 5 arms run under both treatments · instrument: exact array equality ·
  baseline: the source's prediction that all five differ · regime: second release, 0.8B judge.
WORLDS  A · all five differ. The flag works, so R525's home-judge identities really are failed
              runs -- something was omitted there, not broken here.
        B · some are identical. Then --select-npz does not do what its help text says, and
              R525's "failed run" reading becomes "the mechanism does not fire".
KILL (pre-registered): >=1 identical pair kills world A.
POSITIVE CONTROL: the two treatments must differ for at least the arm where the difference is
  largest by construction -- and, more sharply, _08b must differ from the HOME-judge arm of the
  same name, since a different judge changed the scoring. If even that is identical, the whole
  _08b family is a mislabelled copy and nothing here is admissible.
NEGATIVE CONTROL: an artifact against itself must compare equal; a shuffled copy must not.
NOISE FLOOR: none -- exact equality, as in R523/R524/R525.
MULTIPLICITY: 5 pairs, each compared once; all reported.
IMPOSSIBLE HERE: the home-judge A/B invocations, which are genuinely unrecorded. This round
  tests the MECHANISM on a recorded case; it cannot recover what was typed elsewhere.
"""
import json, pathlib, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
RES = ROOT / "corebench/results"
PAIRS = ["greedy_k4_fit1", "indep_k4_fit1", "oracle_k4", "topvar_k4", "topwvar_k4"]

def sig(tag):
    d = np.load(RES / f"sat_{tag}.npz", allow_pickle=True)
    m = np.array([str(k) for k in d["meta"]]); s = np.asarray(d["sat"], dtype=float)
    o = np.argsort(m, kind="stable"); return m[o], s[o]

def same(a, b):
    ma, sa = a; mb, sb = b
    return len(ma) == len(mb) and bool((ma == mb).all()) and np.array_equal(sa, sb)

def main():
    sh = (ROOT / "corebench/rebuild_selection_08b.sh").read_text()
    ok_sh = "--select-npz" in sh and "_08bR" in sh
    print(f"  SOURCE READ  the two invocations are recorded in rebuild_selection_08b.sh -> "
          f"{'PASS' if ok_sh else 'FAIL'}")
    if not ok_sh:
        print("  invocation not recorded -> UNRUNNABLE"); return 2

    # NEGATIVE CONTROL
    a = sig("oracle_k4_08b")
    m, s = a
    neg1 = same(a, a); neg2 = not same(a, (m, s[np.random.default_rng(3).permutation(len(s))]))
    print(f"  NEGATIVE CONTROL  self-equal {neg1} · order-sensitive {neg2} -> "
          f"{'PASS' if neg1 and neg2 else 'FAIL'}")
    if not (neg1 and neg2): return 0

    # POSITIVE CONTROL: the 08b family must differ from the home-judge arm of the same name
    pos = []
    for t in PAIRS:
        try:
            pos.append((t, not same(sig(t), sig(f"{t}_08b"))))
        except Exception as e:
            pos.append((t, None))
    npos = sum(1 for _, v in pos if v)
    print(f"  POSITIVE CONTROL  _08b differs from the HOME-judge arm of the same name: "
          f"{npos}/{len([1 for _, v in pos if v is not None])} -> "
          f"{'PASS -- the judge swap really changed the artifacts' if npos else 'FAIL'}")
    if not npos:
        print("  -> the _08b family is a mislabelled copy; nothing admissible. UNVERIFIED."); return 0

    print(f"\n  {'arm':<20}{'_08b vs _08bR':>16}  reading")
    rows, ident = {}, []
    for t in PAIRS:
        eq = same(sig(f"{t}_08b"), sig(f"{t}_08bR"))
        rows[t] = {"identical": bool(eq)}
        if eq: ident.append(t)
        print(f"  {t:<20}{('IDENTICAL' if eq else 'differ'):>16}  "
              f"{'the rerun changed nothing' if eq else 'the rule re-ran, as documented'}")

    world = "B" if ident else "A"
    print(f"\n  identical pairs: {len(ident)}/{len(PAIRS)}  (kill: >=1 kills world A)")
    print(f"  WORLD {world} -- " +
          ("--select-npz does not change identity even where the invocation is recorded, so "
           "R525's 'failed run' reading must be downgraded to 'the mechanism does not fire'"
           if world == "B" else
           "the flag works where invoked correctly, so R525's home-judge identities really are "
           "runs where the variant treatment was never applied"))

    out = pathlib.Path(__file__).parent / "results/recorded_experiment.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"pairs": rows, "n_identical": len(ident), "identical": ident,
                               "positive_control_08b_differs_from_home": npos,
                               "world": world}, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
