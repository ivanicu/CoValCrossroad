"""R422 -- the `_08b`/`_08bR` families: did the JUDGE differ, or only the SELECTION?

R419 measured the scoring floor at exactly zero. R420 and R421 measured selection byte-identical for
all four exercised rules. Jointly they force: the two families were produced from DIFFERENT INPUTS.
They do not say WHICH input, and I closed the last report on `_08bR is the outlier` -- a sentence
that smuggles in a verdict about which file is wrong when the evidence supports neither.

⛔ AND MY OWN `NEXT` WAS THE MORE EXPENSIVE ROUTE. It proposed re-running greedy_k and indep_k at
   fit-parity 1 -- ten more CPU invocations -- to take an identification from one rule to three. But
   `select_core.py` emits TWO artifacts per run, `core_*.json` AND `sat_*.npz`, and R420/R421 hashed
   only the first. The second is the EMITTED SATISFACTION, i.e. the judge's own numbers, and both
   families' copies are already committed. The discriminating question is answerable from disk with
   ZERO runs. That is the attack ladder in one line: I proposed rung 5 while rung 2 was uninspected.

⛔ AND THE INVENTORY WAS FIVE PAIRS, NOT TWO. `ls core_*08b*.json` gives oracle_k4, greedy_k4_fit1,
   indep_k4_fit1, topvar_k4 and topwvar_k4 -- four distinct rules across two fit parities, plus a
   singleton `oracle_k4_fit1_08b` with no partner. R421's `n=1 rule` caveat was correct about what
   R421 ran and wrong about what was available.

⭐ THE MECHANISM SEPARATOR. `--full-npz` supplies the satisfaction that gets EMITTED; `--select-npz`
   supplies the satisfaction that RUNS THE RULE, defaulting to the former. So:
     same criterion + same response + DIFFERENT value  => the EMITTING npz differed (a second judge)
     same criterion + same response + IDENTICAL value  => the emitter was the same, and what differed
                                                          is the SELECTION input, not the judge
   The value is a float32 looked up per (prompt, criterion, letter). Nothing else can move it.

⛔ ARITHMETIC TRAP. That two files sharing an emitter carry equal values on shared cells is FORCED by
   the lookup -- it is a derivation, and it is exactly why the test is diagnostic. What is NOT forced
   is whether any criteria are shared at all, nor which branch the real files fall in. A shared set
   that comes back EMPTY makes the test vacuous for that rule, and it is reported as UNVERIFIED
   rather than as agreement -- the empty-population failure would read as W-SAME-EMITTER here.

⚠ AND THE JOIN KEY IS THE WHOLE INSTRUMENT. `meta` is `pid|j|letter` where `j` is the criterion's
  POSITION in the selected set, so the same `j` names DIFFERENT criteria in the two files. Joining on
  `j` would compare unrelated cells and manufacture a difference in every pair. The instrument's unit
  must equal the claim's unit: the claim is about a CRITERION, so the key is (pid, criterion TEXT,
  letter), taken from the core JSON, never the index.

ESTIMAND        (A) for each `_08b`/`_08bR` pair: on criteria present in BOTH cores, do the emitted
                    satisfaction values agree EXACTLY?
                (B) the criterion-level overlap between the two families, per rule -- the quantity
                    that decides whether (A) is computable at all;
                (C) what (A) implies about which input differed.

IDENTIFICATION  (A) exact on the shared-criterion set, for the five committed pairs. NOT identified:
                the mechanism where the shared set is empty; and WHICH selection input differed if
                the emitter is common -- `--select-npz`, `--fit-parity` and the target are not
                separable from these artifacts. Named, not assumed away.

SCOPE           population: 5 committed `_08b`/`_08bR` core+sat pairs (oracle_k4, greedy_k4_fit1,
                indep_k4_fit1, topvar_k4, topwvar_k4) · instrument: exact float equality on values
                joined by (pid, criterion text, letter) · baseline: a pair KNOWN byte-identical
                (R420's topw detA/detB) · regime: committed artifacts only, zero runs.

WORLDS
  W-SAME-EMITTER      shared criteria carry IDENTICAL values wherever the overlap is non-empty. Then
                      one judge produced both families, the difference is in the SELECTION input, and
                      every cross-family comparison this campaign ran compared two selections rather
                      than two judges.
  W-DIFFERENT-EMITTER at least one rule shows a value difference on a shared criterion. Then the
                      emitting npz differed: the families are two JUDGES, the `08b` suffix means what
                      it says, and cross-family numbers are cross-instrument numbers.
  W-NO-OVERLAP        every rule's shared set is empty. Then these artifacts cannot answer it and the
                      next step needs a re-run, not more reasoning.

PREDICTION MATRIX
  W-SAME-EMITTER      -> overlap > 0 somewhere; 0 differing values everywhere
  W-DIFFERENT-EMITTER -> overlap > 0; >= 1 differing value, rule and magnitude named
  W-NO-OVERLAP        -> overlap == 0 for all five

PRE-REGISTERED KILL -- conditional on the controls, and it can fire in either direction.
    if plant_is_caught and g0_reports_none and same_emitter_pair_reports_none
       and (real_emitter_change_is_caught OR that control is UNAVAILABLE and said so):
        all overlaps == 0          -> W-NO-OVERLAP (UNVERIFIED, exit 1)
        any value differs          -> W-DIFFERENT-EMITTER
        else                       -> W-SAME-EMITTER
    else: UNVERIFIED -- never CONFIRMED, never OVERTURNED.

CONTROLS
  PLANT (+)     one value in a copy is perturbed by 1e-3; the comparator MUST report exactly one
                difference. Without it, `0 differences` is silence from an instrument never shown to
                return non-zero. ⚠ This is an INVENTED case and it is the weakest control here.
  g = 0         the SAME comparator on the SAME unperturbed copy must report ZERO. A positive control
                whose criterion is already satisfied before the plant proves nothing, and that is the
                ledger's most-repeated row.
  REAL (=)      `topw_k4` vs `topw_k2` -- two GENUINELY DIFFERENT files (different k, so different
                criteria and different sizes) that share an emitter. Non-empty overlap and ZERO
                differences is a real prediction that could have failed.
                ⚠ I FIRST WROTE THIS AS R420's `detA` vs `detB`, and that is DEGENERATE: those two
                are byte-identical, so zero differences is forced and the control would have been
                the g=0 case wearing a corpus's clothes.
  REAL (+)      `full` vs `full_sham` -- the same criteria scored by a DIFFERENT operation, i.e. an
                emitter change on the real corpus rather than a 1e-3 nudge I invented. It MUST report
                differences. If the two share no criteria the control is UNAVAILABLE, and the round
                says so and rests on the synthetic plant, which is weaker footing and is named as
                such rather than quietly counted as saturation.
  NON-EMPTY     a rule whose shared set is empty is printed UNVERIFIED for that rule, never folded
                into agreement.
  KEY           the join is on (pid, criterion TEXT, letter). Printed, because joining on the index
                would compare different criteria and fabricate W-DIFFERENT-EMITTER.

MULTIPLICITY    5 rule pairs x 1 test, plus 3 controls; every rule printed with its overlap and its
                differing count, including the ones that answer nothing.
SEEDS           none -- this reads committed bytes.
ARTIFACT        results/r422_emitter_or_selector.json with the source hash.

IMPOSSIBLE HERE
  which selection input differed -- `--select-npz` vs `--fit-parity` vs the target are not separable
                                    from artifacts that record no configuration. That is the exact
                                    gap the provenance field closes going forward, and it closes
                                    nothing retroactively.
  what the `08b` suffix was MEANT to denote -- the only `08b`-named npz on disk is a GOLD file
                                    (`a08_gold_08b.npz`), not a satisfaction file, so the suffix's
                                    intent is not recoverable from filenames. Named, not guessed.
  cross-release                   -- one release.

EXIT
    0  the controls hold and a branch is reached
    1  a control misbehaved, or nothing overlaps -- UNVERIFIED
    2  an input is missing -- never a silent pass
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
RES = ROOT / "corebench" / "results"

# the five committed pairs, by their EXACT tag -- constructed from select_core.py's own tag rule,
# never globbed. R421 globbed, and a glob that silently falls back to a stale file is precisely how
# this comparison goes blind.
PAIRS = ("oracle_k4", "greedy_k4_fit1", "indep_k4_fit1", "topvar_k4", "topwvar_k4")


def load(tag):
    """-> {(pid, criterion_text, letter): value}. The key is the CLAIM's unit, not the file's."""
    cj, sz = RES / f"core_{tag}.json", RES / f"sat_{tag}.npz"
    if not (cj.exists() and sz.exists()):
        return None
    texts = json.loads(cj.read_text())
    with np.load(sz, allow_pickle=True) as d:
        meta, sat = list(d["meta"]), np.asarray(d["sat"])
    out = {}
    for m, v in zip(meta, sat):
        pid, j, ltr = str(m).split("|")
        lst = texts.get(pid)
        if lst is None or int(j) >= len(lst):
            continue
        out[(pid, lst[int(j)], ltr)] = float(v)
    return out


def compare(a, b):
    """-> (n_shared, n_differ, worst_gap, an example). Exact float equality; no tolerance, because a
    shared emitter makes the values the SAME LOOKUP and any tolerance would hide a real second judge."""
    ks = a.keys() & b.keys()
    diff = [(k, a[k], b[k]) for k in ks if a[k] != b[k]]
    worst = max((abs(x - y) for _, x, y in diff), default=0.0)
    return len(ks), len(diff), worst, (diff[0] if diff else None)


def main() -> int:
    print("R422 · did the JUDGE differ, or only the SELECTION?\n")
    print("  ⛔ MY OWN `NEXT` PROPOSED TEN CPU RUNS WHILE RUNG 2 WAS UNINSPECTED. select_core.py emits")
    print("     core_*.json AND sat_*.npz; R420/R421 hashed only the first. The second is the JUDGE'S")
    print("     OWN NUMBERS, both families are already committed, and the discriminating question")
    print("     needs zero runs.\n")

    # ---- CONTROLS ---------------------------------------------------------------------------------
    base = load("oracle_k4")
    if base is None:
        print("  UNRUNNABLE: core_oracle_k4.json / sat_oracle_k4.npz absent. Exit 2, never 0.")
        return 2
    same = dict(base)
    n0, d0, _, _ = compare(base, same)
    plant_key = next(iter(base))
    planted = dict(base); planted[plant_key] = base[plant_key] + 1e-3
    n1, d1, w1, _ = compare(base, planted)
    g0_ok = (d0 == 0 and n0 > 0)
    plant_ok = (d1 == 1)

    # REAL (=) -- two genuinely different files that share an emitter
    ra, rb = load("topw_k4"), load("topw_k2")
    rneg_ok, nr, dr = False, 0, None
    if ra and rb:
        nr, dr, _, _ = compare(ra, rb)
        rneg_ok = (nr > 0 and dr == 0)

    # REAL (+) -- the same criteria under a DIFFERENT scoring operation, on the real corpus
    fa, fb = load("full"), load("full_sham")
    rpos_avail, rpos_ok, nf, df = False, False, 0, None
    if fa and fb:
        nf, df, wf, _ = compare(fa, fb)
        rpos_avail = nf > 0
        rpos_ok = (nf > 0 and df > 0)

    print("  CONTROLS")
    print(f"    g = 0      an UNPERTURBED copy reports 0 differences over {n0:,} shared cells: {g0_ok}"
          f"   {'PASS' if g0_ok else 'FAIL — the criterion was satisfied before the plant'}")
    print(f"    PLANT (+)  ONE perturbed value is caught, and exactly one: {d1} of {n1:,}   "
          f"{'PASS' if plant_ok else 'FAIL — a 0 below would be silence, not an acquittal'}")
    print(f"               ⚠ this is an INVENTED case and it is the weakest control in the round")
    print(f"    REAL (=)   topw_k4 vs topw_k2 — DIFFERENT files sharing an emitter: {nr:,} shared, "
          f"{dr} differing   {'PASS' if rneg_ok else 'FAIL/ABSENT'}")
    print(f"               ⚠ I first wrote this as R420's detA/detB — byte-identical, so ZERO is")
    print(f"                 forced and it would have been the g=0 case wearing a corpus's clothes")
    if rpos_avail:
        print(f"    REAL (+)   full vs full_sham — a DIFFERENT scoring of shared criteria: {nf:,} "
              f"shared, {df:,} differing   {'PASS' if rpos_ok else 'FAIL — blind to a real change'}")
    else:
        print(f"    REAL (+)   full vs full_sham share no criteria — UNAVAILABLE. The detection side")
        print(f"               therefore rests on the SYNTHETIC plant alone, which is weaker footing")
        print(f"               and is named rather than counted as saturation.")
    print(f"    KEY        the join is (pid, criterion TEXT, letter). `meta`'s `j` is a POSITION in")
    print(f"               the selected set, so the same j names different criteria in the two files")
    print(f"               and joining on it would fabricate a difference in every pair.")
    if not (g0_ok and plant_ok and rneg_ok) or (rpos_avail and not rpos_ok):
        print("\n  UNVERIFIED — the comparator is not validated in both directions. Exit 1.")
        return 1

    # ---- the measurement ---------------------------------------------------------------------------
    print(f"\n  THE FIVE COMMITTED `_08b` / `_08bR` PAIRS")
    print(f"    {'rule':<16} {'shared crit-cells':>17} {'differing':>10} {'worst gap':>10}   verdict")
    rows, differing_rules, usable = {}, [], []
    for tag in PAIRS:
        A, B = load(f"{tag}_08b"), load(f"{tag}_08bR")
        if A is None or B is None:
            rows[tag] = dict(status="MISSING")
            print(f"    {tag:<16} {'-':>17} {'-':>10} {'-':>10}   MISSING")
            continue
        n, d, w, ex = compare(A, B)
        st = "UNVERIFIED (no overlap)" if n == 0 else ("DIFFERS" if d else "identical")
        rows[tag] = dict(status=st, shared=n, differ=d, worst=w,
                         example=(list(ex[0]) + [ex[1], ex[2]]) if ex else None,
                         n_08b=len(A), n_08bR=len(B))
        if n:
            usable.append(tag)
        if d:
            differing_rules.append(tag)
        print(f"    {tag:<16} {n:>17,} {d:>10,} {w:>10.6f}   {st}")

    print(f"\n    rules with a computable overlap: {len(usable)} of {len(PAIRS)}   {usable or 'none'}")

    print()
    if not usable:
        v = "W_NO_OVERLAP"
        print(f"  W-NO-OVERLAP — no pair shares a single criterion, so these artifacts cannot answer")
        print(f"  it and an empty population must not read as agreement. UNVERIFIED. Exit 1.")
    elif differing_rules:
        v = "W_DIFFERENT_EMITTER"
        print(f"  W-DIFFERENT-EMITTER — {differing_rules} carry DIFFERENT values for the SAME")
        print(f"  criterion on the SAME response. Only the emitting npz can move that number, so the")
        print(f"  two families were scored by different judges: the `08b` suffix means what it says,")
        print(f"  and every cross-family comparison in this campaign is a cross-INSTRUMENT comparison.")
    else:
        v = "W_SAME_EMITTER"
        print(f"  W-SAME-EMITTER — across {len(usable)} rules and every shared criterion, the emitted")
        print(f"  values are EXACTLY equal. One judge produced both families.")
        print(f"  ⛔ SO `_08b` vs `_08bR` IS A DIFFERENCE IN SELECTION, NOT IN THE JUDGE, and the")
        print(f"     sentence I closed the last report with — `_08bR is the outlier, made with")
        print(f"     different inputs` — was right about `different` and wrong to imply an instrument.")
        print(f"  ⚠ WHICH selection input differed is NOT identified here: --select-npz, --fit-parity")
        print(f"    and the target are not separable from artifacts that record no configuration.")

    print(f"\n  ⚠ FIVE PAIRS ON ONE RELEASE, read from committed bytes. This says nothing about pairs")
    print(f"    that were never committed, and nothing about any other release.")

    art = dict(source_sha256=hashlib.sha256(SELF.read_bytes()).hexdigest(), source_name=SELF.name,
               pairs=rows, usable=usable, differing=differing_rules, verdict=v,
               controls=dict(g0_zero=g0_ok, plant_caught=plant_ok, plant_n=d1,
                             real_neg_shared=nr, real_neg_differ=dr, real_neg_ok=rneg_ok,
                             real_pos_available=rpos_avail, real_pos_shared=nf,
                             real_pos_differ=df, real_pos_ok=rpos_ok))
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r422_emitter_or_selector.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0 if usable else 1


if __name__ == "__main__":
    sys.exit(main())
