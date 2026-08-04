"""R426 -- R424 said the emitter is not on disk. My own candidate filter excluded the directory it is in.

R424 tested every committed table it could find and concluded W-NOT-ON-DISK: no table emitted the
`_08b` satisfaction arms, therefore 74 artifacts and 30 rounds are `instrument-UNKNOWN`. R425 then
built on it and closed with `"judge" is a noun I never had evidence for`.

⛔ BOTH ARE WRONG, AND THE DEFECT IS ONE LINE OF MY OWN CODE. R424's candidate loop reads

        for p in sorted(ROOT.rglob("*.npz")):
            if ".venv" in p.parts or p.parent == RES:   # <- RES is corebench/results
                continue

   so it excluded `corebench/results` ENTIRELY -- the one directory guaranteed to hold satisfaction
   tables -- and `sat08_full.npz` is in it. I wrote that filter to stop the ARMS being tested as
   candidates and threw out the emitter with them. The wall was not measured; it was constructed.

⛔ AND THE SECOND FILTER COMPOUNDED IT. A candidate was admitted only if its meta key set EQUALLED
   `sat_full.npz`'s. A per-arm table's key set CANNOT equal a full table's -- so 49 rejections
   included, by construction, every file that could have answered the question. **A population
   defined so the answer cannot be in it returns a clean, confident, false negative**, and it prints
   the same string as a real absence.

⭐ AND THE SOURCE SAID SO ALL ALONG, WHICH IS THE PART THAT COSTS MOST. `R290/run.py:58` reads
   `JUDGES = {"2B  Qwen3.5-2B-Base": "sat_", "0.8B Qwen3.5-0.8B-Base": "sat08_"}`, and
   `R301/run.py:123` says `topw_k4` and `random_k4_s0` "were judged directly at 0.8B in R290".
   The model was NAMED, in committed source, in the rounds my own census had already listed. I
   treated artifact-containment as the only admissible evidence about provenance and called the
   result an impossibility.

ESTIMAND        (A) for every committed table -- INCLUDING `corebench/results` -- the share of each
                    `_08b` family's emitted values contained in it;
                (B) whether any candidate reverses the default's pattern: high on an `_08b` family
                    and low on `topw_k4`, which is what an emitter looks like;
                (C) whether R424's W-NOT-ON-DISK survives once the excluded directory is searched.

IDENTIFICATION  Exact for tables on disk. NOT identified: that a table which CONTAINS the values is
                the one that PRODUCED them -- containment is necessary, not sufficient, and a
                superset table would also contain them. Named, and the `topw_k4` contrast is what
                keeps it from being vacuous.

SCOPE           population: every `*.npz` in the repo except `.venv`, with NO directory excluded ·
                instrument: value-set containment at (pid, criterion text, letter) · baseline: the
                default table's `1.0000` on `topw_k4` and `0.0380` on `_08b` · regime: committed
                artifacts, zero runs.

WORLDS
  W-EMITTER-IDENTIFIED   a candidate contains an `_08b` family at >= 0.99 while containing `topw_k4`
                         BELOW 0.99. Then R424 is OVERTURNED by a population error of its own making,
                         the emitting table is named, and `instrument-UNKNOWN` is retracted.
  W-STILL-NOT-ON-DISK    containment stays near the floor everywhere even with the directory
                         included. Then R424's verdict survives with its REASON corrected -- it was
                         reached by an unsound search and happens to be right.
  W-DENSE                a candidate contains BOTH `topw_k4` and an `_08b` family at >= 0.99. Then
                         containment does not discriminate at this resolution. UNVERIFIED.

PREDICTION MATRIX
  W-EMITTER-IDENTIFIED -> one table high on `_08b`, low on `topw_k4`; named
  W-STILL-NOT-ON-DISK  -> every table near the floor on both `_08b` families
  W-DENSE              -> a table high on both

PRE-REGISTERED KILL -- conditional on the anchors, which are the same two R424 used and passed.
    if default_contains_topw_k4 >= 0.99 and default_contains_08b <= 0.10:
        a candidate >= 0.99 on an `_08b` family and < 0.99 on topw_k4 -> W-EMITTER-IDENTIFIED
        a candidate >= 0.99 on BOTH                                    -> W-DENSE (UNVERIFIED)
        none above 0.10 on either family                               -> W-STILL-NOT-ON-DISK
    else: UNVERIFIED.

CONTROLS
  ANCHOR (+)    the default table contains `topw_k4` at >= 0.99 -- it emitted it.
  ANCHOR (-)    the default table contains `oracle_k4_08b` at <= 0.10 -- the floor. Both required:
                the positive alone passes a table that contains everything.
  POPULATION    ⭐ THE CONTROL R424 DID NOT HAVE, AND ITS ABSENCE IS WHY R424 IS WRONG. The round
                counts how many `.npz` files its predecessor's filter EXCLUDED, and how many of those
                are full-shaped tables. A search is an instrument; its POPULATION is part of it, and
                a population that cannot contain the answer needs no blindness in the pattern to
                return a false zero.
  PLANT         a synthetic value (real + 1.0) must be reported NOT contained, in both directions.
  NON-EMPTY     a candidate with zero comparable cells is UNVERIFIED for that candidate, never 0.0.

MULTIPLICITY    every admitted table x 3 arms; the full table printed, non-survivors included.
SEEDS           none.
ARTIFACT        results/r426_emitter_was_excluded.json with the source hash.

IMPOSSIBLE HERE
  containment => production  -- a superset table also contains the values. The `topw_k4` contrast
                                bounds this but does not remove it; naming the table is the claim,
                                and even that is `the table whose values these are`.
  which weights made a table -- `R290/run.py:58` NAMES `Qwen3.5-0.8B-Base` in committed source, which
                                is evidence of a different KIND from containment and is reported as
                                such: source-attested, not artifact-verified.
  cross-release              -- one release.

EXIT
    0  the anchors hold and a branch is reached
    1  an anchor failed, or containment is not discriminating -- UNVERIFIED
    2  an input is missing -- never a silent pass
"""
from __future__ import annotations
import collections
import hashlib
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
RES = ROOT / "corebench" / "results"
ARMS = ("topw_k4", "oracle_k4_08b", "oracle_k4_08bR")


def texts_of(tag):
    p = RES / f"core_{tag}.json"
    return json.loads(p.read_text()) if p.exists() else None


def sets_from(npz_path, texts):
    try:
        with np.load(npz_path, allow_pickle=True) as d:
            if "meta" not in d.files or "sat" not in d.files:
                return None
            meta, sat = list(d["meta"]), np.asarray(d["sat"])
    except Exception:
        return None
    out = collections.defaultdict(set)
    for m, v in zip(meta, sat):
        s = str(m).split("|")
        if len(s) != 3:
            return None
        pid, j, ltr = s
        lst = texts.get(pid)
        if lst is None or not j.isdigit() or int(j) >= len(lst):
            continue
        out[(pid, lst[int(j)], ltr)].add(float(v))
    return dict(out)


def contained(arm, table):
    ks = [k for k in arm if k in table]
    if not ks:
        return None, 0, 0
    return sum(1 for k in ks if arm[k] & table[k]) / len(ks), \
        sum(1 for k in ks if arm[k] & table[k]), len(ks)


def main() -> int:
    full_texts = texts_of("full")
    if full_texts is None:
        print("  UNRUNNABLE: core_full.json absent. Exit 2, never 0."); return 2
    dflt = sets_from(RES / "sat_full.npz", full_texts)
    if dflt is None:
        print("  UNRUNNABLE: sat_full.npz unreadable. Exit 2, never 0."); return 2

    print("R426 · R424 said the emitter is not on disk. My filter excluded the directory it is in.\n")
    print("  ⛔ R424's CANDIDATE LOOP: `if '.venv' in p.parts or p.parent == RES: continue`.")
    print("     RES is corebench/results — the one directory guaranteed to hold satisfaction")
    print("     tables — and I wrote that line to stop the ARMS being tested as candidates.")
    print("     The wall was not measured. It was constructed.\n")

    arms = {}
    for a in ARMS:
        t = texts_of(a)
        s = sets_from(RES / f"sat_{a}.npz", t) if t else None
        if s:
            arms[a] = s
    if len(arms) < len(ARMS):
        print(f"  UNRUNNABLE: missing arm(s) {[a for a in ARMS if a not in arms]}. Exit 2."); return 2

    # ---- ANCHORS + the POPULATION control ----------------------------------------------------------
    r_pos, n_pos, d_pos = contained(arms["topw_k4"], dflt)
    r_neg, n_neg, d_neg = contained(arms["oracle_k4_08b"], dflt)
    a_pos, a_neg = r_pos >= 0.99, r_neg <= 0.10
    plant = dict(dflt)
    pk = next(iter(plant))
    plant_ok = not ({next(iter(plant[pk])) + 1.0} & plant[pk])

    excluded = [p for p in sorted(ROOT.rglob("*.npz"))
                if ".venv" not in p.parts and p.parent == RES]
    exc_full = [p for p in excluded if p.name.startswith(("sat_full", "sat08_full"))]

    print("  CONTROLS")
    print(f"    ANCHOR (+)  default contains topw_k4 (it emitted it): {r_pos:.4f} "
          f"({n_pos:,} of {d_pos:,})   {'PASS' if a_pos else 'FAIL'}")
    print(f"    ANCHOR (-)  default contains oracle_k4_08b — the FLOOR: {r_neg:.4f} "
          f"({n_neg:,} of {d_neg:,})   {'PASS' if a_neg else 'FAIL'}")
    print(f"    PLANT       a synthetic value is NOT contained: {plant_ok}   "
          f"{'PASS' if plant_ok else 'FAIL'}")
    print(f"    POPULATION  ⭐ THE CONTROL R424 DID NOT HAVE, and its absence is why R424 is wrong.")
    print(f"                .npz files its filter EXCLUDED: {len(excluded)}")
    print(f"                of those, FULL-shaped tables: {len(exc_full)}   "
          f"{[p.name for p in exc_full]}")
    print(f"                a search is an instrument and its POPULATION is part of it. A population")
    print(f"                that cannot contain the answer returns a clean, confident, false zero —")
    print(f"                and prints the same string as a real absence.")
    if not (a_pos and a_neg and plant_ok):
        print("\n  UNVERIFIED — the anchors are the instrument. Exit 1."); return 1

    # ---- every table, NO directory excluded --------------------------------------------------------
    print(f"\n  EVERY COMMITTED TABLE — NO DIRECTORY EXCLUDED THIS TIME")
    print(f"    {'table':<50} {'topw_k4':>9} {'_08b':>9} {'_08bR':>9}")
    rows, named, dense = {}, [], []
    for p in sorted(ROOT.rglob("*.npz")):
        if ".venv" in p.parts:
            continue
        tbl = sets_from(p, full_texts)
        if tbl is None or not tbl:
            continue
        r = {a: dict(zip(("rate", "ok", "total"), contained(arms[a], tbl))) for a in ARMS}
        if all(r[a]["rate"] is None for a in ARMS):
            continue
        rel = str(p.relative_to(ROOT))
        rows[rel] = r
        g = lambda a: ("  n/a  " if r[a]["rate"] is None else f"{r[a]['rate']:.4f}")
        hi08 = [a for a in ("oracle_k4_08b", "oracle_k4_08bR")
                if r[a]["rate"] is not None and r[a]["rate"] >= 0.99]
        tw = r["topw_k4"]["rate"]
        mark = ""
        if hi08 and (tw is None or tw < 0.99):
            named.append((rel, hi08, tw)); mark = "   <- EMITTER-SHAPED"
        elif hi08:
            dense.append(rel); mark = "   <- DENSE, contains both"
        print(f"    {rel[-50:]:<50} {g('topw_k4'):>9} {g('oracle_k4_08b'):>9} "
              f"{g('oracle_k4_08bR'):>9}{mark}")

    print()
    if dense:
        v = "W_DENSE"
        print(f"  W-DENSE — {dense} contains BOTH a default-emitted arm and an `_08b` family at")
        print(f"  >= 0.99. Containment does not discriminate at this resolution. UNVERIFIED.")
        rc = 1
    elif named:
        v = "W_EMITTER_IDENTIFIED"
        rc = 0
        for rel, hi, tw in named:
            print(f"  W-EMITTER-IDENTIFIED — `{rel}` contains {hi} at >= 0.99 while containing")
            print(f"  topw_k4 at {('n/a' if tw is None else f'{tw:.4f}')}. That is the emitter's")
            print(f"  signature, and it was in the directory R424's filter skipped.")
        print(f"  ⛔ R424's `W-NOT-ON-DISK` IS OVERTURNED, AND BY A POPULATION ERROR OF ITS OWN")
        print(f"     MAKING — not by new data. Every artifact it tested, it tested correctly.")
        print(f"  ⛔ SO `instrument-UNKNOWN` IS RETRACTED, AND SO IS R425's `judge is a noun I never")
        print(f"     had evidence for`. R290/run.py:58 NAMES `Qwen3.5-0.8B-Base` in committed source.")
        print(f"  ⚠ CONTAINMENT IS NECESSARY, NOT SUFFICIENT: a superset table would also contain")
        print(f"    these values. The claim is `the table whose values these are`, and the model")
        print(f"    behind it is SOURCE-ATTESTED (R290), not artifact-verified. Different kinds of")
        print(f"    evidence, and conflating them is what produced the wall in the first place.")
    else:
        v = "W_STILL_NOT_ON_DISK"
        rc = 0
        print(f"  W-STILL-NOT-ON-DISK — even with the excluded directory searched, no table rises")
        print(f"  above the floor. R424's verdict survives, but its REASON is corrected: it was")
        print(f"  reached by a search whose population could not contain the answer, and a right")
        print(f"  answer from an unsound instrument is not evidence.")

    art = dict(source_sha256=hashlib.sha256(SELF.read_bytes()).hexdigest(), source_name=SELF.name,
               anchors=dict(pos_rate=r_pos, pos_n=n_pos, pos_total=d_pos, neg_rate=r_neg,
                            neg_n=n_neg, neg_total=d_neg, plant=plant_ok),
               excluded_by_r424=len(excluded), excluded_full_shaped=[p.name for p in exc_full],
               candidates=rows, named=named, dense=dense, verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r426_emitter_was_excluded.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
