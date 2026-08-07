"""R242 -- score E05's own rounds against realstat §5, BEHAVIOURALLY rather than by grep.

Twenty-two rounds have audited CoVal. Nothing has audited E05 against the standard E05 applies.
Constitution L03: "I apply every law to the system and none to the document that designed it."

⚠ THE OBVIOUS WAY TO DO THIS IS BROKEN. Grepping a docstring for "POSITIVE CTRL" measures whether I
   TYPED THE WORDS, not whether the round did the thing. A prior audit of three projects on this
   machine scored 6-49% and recorded that near-100% is the signature of a broken detector, not of a
   good project. So every item below has a BEHAVIOURAL check next to its textual one, and the gap
   between them is reported as its own number -- that gap is the measurement.

ESTIMAND        for each round x each §5 item: (declared in the docstring?) and (evidenced in the
                code or the persisted output?), and the DECLARED-BUT-NOT-EVIDENCED rate.
IDENTIFICATION  exact for the textual half. The behavioural half is a PROXY and is sound in one
                direction only: evidence of the behaviour is evidence; absence of the pattern is not
                evidence of absence. Reported as such, never as a violation count.
SCOPE           every round directory under E05_the_space_of_compilers with a run.py.
KILL            if the declared-but-not-evidenced rate is near zero, the detector is not detecting.
                A self-audit that finds nothing has not audited.
POSITIVE CTRL   a synthetic round is planted -- docstring declaring every item, code doing none --
                and the audit must score it high on text and near-zero on behaviour.
NEGATIVE CTRL   the same synthetic with an EMPTY docstring must score zero on both.
IMPOSSIBLE      whether a declared item was done CORRECTLY. This measures presence, never quality;
                R238 declared and implemented a positive control that was worthless, and this audit
                would score that round as compliant. Named because it is the audit's own ceiling.
"""
from __future__ import annotations
import json, pathlib, re, sys, collections

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"
E05 = ROOT / "E05_the_space_of_compilers"

# item -> (docstring marker, behavioural evidence in code/results)
ITEMS = {
    "ESTIMAND":       (r"ESTIMAND",       None),
    "IDENTIFICATION": (r"IDENTIFICATION", None),
    "SCOPE":          (r"SCOPE",          None),
    "WORLDS":         (r"WORLDS",         None),
    "KILL":           (r"KILL",           r"verdict|REFUTED|SUPPORTED|UNVERIFIED"),
    "POSITIVE_CTRL":  (r"POSITIVE",       r"POSITIVE|positive control|pos_ok|pos_fires"),
    "NEGATIVE_CTRL":  (r"NEGATIVE",       r"NEGATIVE|shuffl|permut|neg_ok"),
    "PLACEBO":        (r"PLACEBO",        r"PLACEBO|placebo"),
    "NOISE_FLOOR":    (r"NOISE FLOOR|FLOOR", r"floor|spread"),
    "MULTIPLICITY":   (r"MULTIPLICITY",   r"Bonferroni|alpha|whole grid|cells"),
    "SPECIFICATION":  (r"SPECIFICATION",  r"for .* in (KS|EPS|LEVELS|RS|SPARSITY|DRAWS)"),
    "SEEDS":          (r"SEEDS",          r"SEEDS\s*=\s*\[[^\]]*,[^\]]*,"),
    "ARTIFACT":       (r"ARTIFACT",       None),
    "IMPOSSIBLE":     (r"IMPOSSIBLE|register", None),
}


def audit(src: str, resdir: pathlib.Path):
    """⚠ THE FIRST VERSION SEARCHED THE WHOLE SOURCE for behavioural evidence, docstring included.
    Its own positive plant -- a docstring declaring every item over a body of `pass` -- scored 3/14
    on BEHAVIOUR, because the words "positive control", "placebo" and "floor" in the docstring
    satisfied the patterns meant to detect the CODE doing those things. The audit built to separate
    typing from doing was reading the typing as the doing.
    The docstring is now stripped before any behavioural search, so `code` contains no prose."""
    doc = src.split('"""')[1] if src.count('"""') >= 2 else ""
    code = src.replace(doc, "", 1) if doc else src
    out = {}
    for k, (dpat, bpat) in ITEMS.items():
        declared = bool(re.search(dpat, doc))
        if k == "ARTIFACT":
            ev = any(f.stat().st_size > 1024 for f in resdir.glob("*")) if resdir.is_dir() else False
        elif bpat is None:
            ev = None
        else:
            ev = bool(re.search(bpat, code))
        out[k] = (declared, ev)
    return out


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rounds = sorted(p for p in E05.glob("A*/R*/run.py"))
    if not rounds:
        print("no rounds found -- exit 2, not 0"); return 2

    # ---- controls, planted before anything real is read
    plant_hi = '"""\n' + "\n".join("%s all of it" % k.replace("_", " ") for k in ITEMS) + '\n"""\npass\n'
    plant_lo = '"""\n"""\npass\n'
    tmp = OUT / "_ctrl"; tmp.mkdir(exist_ok=True)
    a_hi, a_lo = audit(plant_hi, tmp), audit(plant_lo, tmp)
    hi_txt = sum(1 for d, _ in a_hi.values() if d)
    hi_beh = sum(1 for _, e in a_hi.values() if e)
    lo_txt = sum(1 for d, _ in a_lo.values() if d)
    print("=== controls ===")
    print(" POSITIVE plant: declares everything, does nothing -> text %d/%d, behaviour %d/%d  %s"
          % (hi_txt, len(ITEMS), hi_beh, len(ITEMS),
             "OK" if hi_txt >= len(ITEMS) - 2 and hi_beh <= 1 else "DETECTOR BROKEN"))
    print(" NEGATIVE plant: empty docstring                  -> text %d/%d  %s"
          % (lo_txt, len(ITEMS), "OK" if lo_txt == 0 else "FALSE POSITIVE"))

    per, tally = {}, collections.Counter()
    for rp in rounds:
        a = audit(rp.read_text(), rp.parent / "results")
        per[rp.parent.name] = {k: [bool(d), (None if e is None else bool(e))]
                               for k, (d, e) in a.items()}
        for k, (d, e) in a.items():
            tally[(k, "declared")] += int(d)
            if e is not None:
                tally[(k, "evidenced")] += int(e)
                tally[(k, "checkable")] += 1
                if d and not e:
                    tally[(k, "GAP")] += 1

    n = len(rounds)
    print("\n=== E05: %d rounds against realstat §5 ===" % n)
    print("%-16s %10s %12s %12s" % ("item", "declared", "evidenced", "declared-not-ev"))
    gaps = 0
    for k in ITEMS:
        d = tally[(k, "declared")]
        if tally[(k, "checkable")]:
            e = tally[(k, "evidenced")]; g = tally[(k, "GAP")]; gaps += g
            print("%-16s %8d/%-2d %10d/%-2d %12d" % (k, d, n, e, n, g))
        else:
            print("%-16s %8d/%-2d %12s %12s" % (k, d, n, "(text only)", "-"))

    declared_total = sum(tally[(k, "declared")] for k in ITEMS)
    print("\n declared overall            %d/%d = %.1f%%"
          % (declared_total, n * len(ITEMS), 100 * declared_total / (n * len(ITEMS))))
    checkable = sum(tally[(k, "checkable")] for k in ITEMS)
    evidenced = sum(tally[(k, "evidenced")] for k in ITEMS)
    print(" evidenced where checkable   %d/%d = %.1f%%"
          % (evidenced, checkable, 100 * evidenced / checkable if checkable else 0))
    print(" DECLARED BUT NOT EVIDENCED  %d  <- the number this round exists to produce" % gaps)

    worst = sorted(per.items(),
                   key=lambda kv: sum(1 for d, e in kv[1].values() if d and e is False))[::-1][:5]
    print("\n rounds with the most declared-but-not-evidenced items:")
    for nm, a in worst:
        miss = [k for k, (d, e) in a.items() if d and e is False]
        print("   %-42s %d  %s" % (nm[:42], len(miss), ", ".join(miss) or "-"))

    print("\n" + "=" * 78); print("KILL"); print("=" * 78)
    ok = hi_txt >= len(ITEMS) - 2 and hi_beh <= 1 and lo_txt == 0
    if not ok:
        v = "UNVERIFIED -- the detector failed its own plants"
    elif gaps == 0:
        v = ("SUSPECT: zero declared-but-not-evidenced across %d rounds. A prior audit on this "
             "machine scored three projects at 6-49%% and recorded that near-100%% is the signature "
             "of a broken detector. Treat this as UNVERIFIED until the patterns are attacked."
             % n)
    else:
        v = ("%d declared-but-not-evidenced items across %d rounds (%.1f%% of checkable cells). The "
             "audit detects, and its ceiling is named: it measures PRESENCE, never QUALITY -- R238 "
             "declared and implemented a positive control that was worthless, and this scores that "
             "round compliant." % (gaps, n, 100 * gaps / checkable if checkable else 0))
    print("\n  " + v)
    json.dump({"rounds": n, "per_round": per, "gaps": gaps, "declared_total": declared_total,
               "checkable": checkable, "evidenced": evidenced, "verdict": v},
              open(OUT / "self_audit.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
