"""R424 -- BOTH `_08b` families are foreign to the default judge. Which table DID emit them?

R423 repaired R422's join to a set-valued key and measured two things its own three worlds could not
tell apart, because I had not written the world that turned out to be true:

    families vs EACH OTHER   0, 0, 1, 0, 2 disjoint cells of 7,044-8,180   -> <= 0.03%
    families vs the DEFAULT  ~29,700 uncontained values per rule           -> nearly everything

So `_08b` and `_08bR` agree with one another and BOTH disagree with the default npz. R423's printed
`W-MIXED` came from a branch that mixed those two estimands into one condition; the honest reading is
`same emitter as each other, foreign to the default`, and no world of mine predicted it.

⛔ AND THAT IS THE META-SEPARATOR FIRING, NOT A TYPO IN A BRANCH. I asked `did the judge differ
   BETWEEN the families` and never asked `is either family the default judge at all`. The
   decomposition was wrong, so the branch had nowhere correct to land.

⛔ AND R423's `uncontained` IS A COUNT WITHOUT ITS DENOMINATOR, which is not a rate. This round
   reports the denominator with every count -- the ledger has an entry for exactly this and I still
   shipped it.

⭐ SO THE IDENTIFICATION IS NOW POSSIBLE AND CHEAP. `select_core.py` makes ZERO judge calls: every
   emitted value is a lookup. So the emitting table is the one whose values CONTAIN the family's, and
   the repo holds a handful of candidate tables -- `a04_full.npz` (the default), `sat_full_qwen3b`,
   `sat_full_phi`, and whatever else carries the same key set. Testing containment against each names
   the emitter, or shows it is not on disk.

⛔ ARITHMETIC TRAP. Containment of a lookup's output in the table it was looked up from is FORCED --
   a derivation. Its value here is entirely in the CONTRAST: the default contains `topw_k4`
   completely and the `_08b` families barely at all, and only a candidate that reverses that pattern
   identifies anything. A candidate scoring high on everything would be a table so dense it contains
   any value, which is why the round reports a NON-EMITTER's rate as the floor.

ESTIMAND        (A) for each candidate table T and each family F: the share of F's emitted values
                    present in T at the same (pid, criterion text, letter);
                (B) the same for `topw_k4`, whose emitter IS KNOWN to be the default -- the row that
                    turns (A) from a ranking into a measurement;
                (C) which candidate, if any, contains a family at the rate the default contains
                    `topw_k4`.

IDENTIFICATION  Exact for candidates on disk. NOT identified: an emitter whose table was never
                committed -- then every candidate scores low and the answer is `not on disk`, which
                is a real outcome and is reported as such rather than as the best of a bad set.

SCOPE           population: every `*.npz` in the repo (excluding `.venv`) carrying `meta` and `sat`
                whose meta key set EQUALS `sat_full.npz`'s, so `core_full.json` maps its indices ·
                instrument: value-set containment at (pid, criterion text, letter) · baseline: the
                default table's containment of `topw_k4` (must be ~1.0) and of an `_08b` family
                (measured, and it is the floor) · regime: committed artifacts, zero runs.

WORLDS
  W-NAMED       some candidate contains a family at a rate comparable to the default's containment of
                `topw_k4`. Then the emitter is NAMED, the `08b` suffix's referent is established from
                the object rather than from its filename, and every number computed off these arms
                belongs to that instrument.
  W-NOT-ON-DISK no candidate rises above the floor. Then the emitting table was never committed, the
                `_08b` arms cannot be attributed to any instrument in this repo, and every claim
                resting on them is instrument-UNKNOWN -- which is worse than instrument-other and
                must be said in those words.
  W-DENSE       a candidate contains EVERYTHING, including families it cannot have emitted. Then
                containment is not discriminating at this resolution and the test is UNVERIFIED.

PREDICTION MATRIX
  W-NAMED       -> one candidate near 1.0 for a family, others near the floor
  W-NOT-ON-DISK -> all candidates near the floor for both families
  W-DENSE       -> a candidate near 1.0 for BOTH the default-emitted arm and a foreign family

PRE-REGISTERED KILL -- conditional on the two anchors, never on a ranking alone.
    if default_contains_topw_k4 >= 0.99 and default_contains_08b <= 0.10:
        a candidate with >= 0.99 for a family and < 0.99 for topw_k4 -> W-NAMED
        a candidate with >= 0.99 for BOTH                            -> W-DENSE (UNVERIFIED)
        none above 0.10 for either family                            -> W-NOT-ON-DISK
    else: UNVERIFIED -- the anchors ARE the instrument; without them a rate is uninterpretable.

CONTROLS
  ANCHOR (+)   the default table must contain `topw_k4` at >= 0.99. `topw_k4` was emitted from the
               default npz, so anything less means the containment test is broken, not that the file
               is foreign.
  ANCHOR (-)   the default table must contain an `_08b` family at <= 0.10 -- R423 measured ~1%. This
               is the FLOOR, and it is what makes a high rate elsewhere mean something. Both anchors
               are required: the positive alone would pass a table that contains everything.
  KEYSET       a candidate enters only if its meta key set EQUALS `sat_full.npz`'s. Otherwise
               `core_full.json` does not map its indices and the join would compare unrelated cells --
               the same failure R422 shipped, one level up.
  DENOMINATOR  every count is printed with its denominator. R423 printed `29,742 uncontained` with no
               total, and a count without its denominator is not a rate.
  NON-EMPTY    a candidate with zero comparable cells is UNVERIFIED for that candidate, never 0.0.

MULTIPLICITY    candidates x 3 arms (topw_k4, _08b, _08bR); the full table printed, non-survivors
                included, since a candidate near the floor is what makes the anchor readable.
SEEDS           none.
ARTIFACT        results/r424_emitter_identification.json with the source hash.

IMPOSSIBLE HERE
  an emitter never committed -- named as W-NOT-ON-DISK rather than approximated by the closest file.
  WHICH MODEL a named table came from -- the table's filename is a name, not evidence about the
                                         weights that produced it. Naming the TABLE is the claim;
                                         naming the MODEL is not.
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
    """-> {(pid, text, letter): set(values)} using `texts` to resolve meta's positional index."""
    with np.load(npz_path, allow_pickle=True) as d:
        if "meta" not in d.files or "sat" not in d.files:
            return None, None
        meta, sat = list(d["meta"]), np.asarray(d["sat"])
    out, keys = collections.defaultdict(set), set()
    for m, v in zip(meta, sat):
        s = str(m).split("|")
        if len(s) != 3:
            return None, None
        pid, j, ltr = s
        keys.add(str(m))
        lst = texts.get(pid)
        if lst is None or not j.isdigit() or int(j) >= len(lst):
            continue
        out[(pid, lst[int(j)], ltr)].add(float(v))
    return dict(out), keys


def contained(arm, table):
    ks = [k for k in arm if k in table]
    if not ks:
        return None, 0, 0
    ok = sum(1 for k in ks if arm[k] & table[k])
    return ok / len(ks), ok, len(ks)


def main() -> int:
    full_texts = texts_of("full")
    if full_texts is None:
        print("  UNRUNNABLE: core_full.json absent. Exit 2, never 0."); return 2
    dflt_tbl, dflt_keys = sets_from(RES / "sat_full.npz", full_texts)
    if dflt_tbl is None:
        print("  UNRUNNABLE: sat_full.npz unreadable. Exit 2, never 0."); return 2

    print("R424 · both `_08b` families are foreign to the default. Which table DID emit them?\n")
    print("  ⛔ R423's THREE WORLDS DID NOT INCLUDE THE ONE THAT WAS TRUE. I asked whether the judge")
    print("     differed BETWEEN the families and never asked whether either IS the default. The")
    print("     decomposition was wrong, so the branch had nowhere correct to land.\n")

    arms = {}
    for a in ARMS:
        t = texts_of(a)
        s, _ = sets_from(RES / f"sat_{a}.npz", t) if t else (None, None)
        if s:
            arms[a] = s
    if len(arms) < len(ARMS):
        print(f"  UNRUNNABLE: missing arm(s) {[a for a in ARMS if a not in arms]}. Exit 2.")
        return 2

    # ---- ANCHORS ----------------------------------------------------------------------------------
    r_pos, n_pos, d_pos = contained(arms["topw_k4"], dflt_tbl)
    r_neg, n_neg, d_neg = contained(arms["oracle_k4_08b"], dflt_tbl)
    a_pos = r_pos is not None and r_pos >= 0.99
    a_neg = r_neg is not None and r_neg <= 0.10
    print("  ANCHORS — the instrument, not decoration")
    print(f"    ANCHOR (+)  default table contains topw_k4 (KNOWN default-emitted): "
          f"{r_pos:.4f}  ({n_pos:,} of {d_pos:,})   {'PASS' if a_pos else 'FAIL'}")
    print(f"    ANCHOR (-)  default table contains oracle_k4_08b: "
          f"{r_neg:.4f}  ({n_neg:,} of {d_neg:,})   {'PASS' if a_neg else 'FAIL'}")
    print(f"                this is the FLOOR — the positive anchor alone would pass a table that")
    print(f"                contains everything, so both are required")
    print(f"    DENOMINATOR every count above carries its total. R423 printed `29,742 uncontained`")
    print(f"                with none, and a count without its denominator is not a rate.")
    if not (a_pos and a_neg):
        print("\n  UNVERIFIED — the anchors are the instrument; without them a rate is")
        print("  uninterpretable. Exit 1."); return 1

    # ---- candidate tables --------------------------------------------------------------------------
    cands, skipped = [], []
    for p in sorted(ROOT.rglob("*.npz")):
        if ".venv" in p.parts or p.parent == RES:
            continue
        try:
            tbl, keys = sets_from(p, full_texts)
        except Exception as e:
            skipped.append((str(p.relative_to(ROOT)), f"{type(e).__name__}")); continue
        if tbl is None:
            skipped.append((str(p.relative_to(ROOT)), "no meta/sat or wrong meta shape")); continue
        if keys != dflt_keys:
            skipped.append((str(p.relative_to(ROOT)), f"key set differs ({len(keys):,} keys)"))
            continue
        cands.append((p, tbl))
    cands.insert(0, (RES / "sat_full.npz", dflt_tbl))

    print(f"\n  CANDIDATE TABLES — a candidate enters only if its meta KEY SET equals sat_full's,")
    print(f"  because otherwise core_full.json does not map its indices and the join would compare")
    print(f"  unrelated cells: R422's failure, one level up.")
    print(f"    admitted {len(cands)} · rejected {len(skipped)} on the key-set precondition\n")
    print(f"    {'table':<58} {'topw_k4':>9} {'_08b':>9} {'_08bR':>9}")
    rows, named = {}, []
    for p, tbl in cands:
        rel = str(p.relative_to(ROOT))
        r = {}
        for a in ARMS:
            rate, ok, tot = contained(arms[a], tbl)
            r[a] = dict(rate=rate, ok=ok, total=tot)
        rows[rel] = r
        f = lambda a: ("  n/a  " if r[a]["rate"] is None else f"{r[a]['rate']:.4f}")
        print(f"    {rel[-58:]:<58} {f('topw_k4'):>9} {f('oracle_k4_08b'):>9} "
              f"{f('oracle_k4_08bR'):>9}")
        hi = [a for a in ("oracle_k4_08b", "oracle_k4_08bR")
              if r[a]["rate"] is not None and r[a]["rate"] >= 0.99]
        if hi:
            named.append((rel, hi, r["topw_k4"]["rate"]))

    if skipped:
        print(f"\n    rejected on the key-set precondition (printed, never silently dropped):")
        for s, why in skipped[:8]:
            print(f"      {s[-70:]:<70} {why}")
        if len(skipped) > 8:
            print(f"      … and {len(skipped) - 8} more")

    print()
    dense = [n for n in named if n[2] is not None and n[2] >= 0.99 and n[0] != "corebench/results/sat_full.npz"]
    if dense:
        v = "W_DENSE"
        print(f"  W-DENSE — {[d[0] for d in dense]} contains BOTH a default-emitted arm and a foreign")
        print(f"  family at >= 0.99. Containment is not discriminating at this resolution. UNVERIFIED.")
    elif named:
        v = "W_NAMED"
        for rel, hi, tw in named:
            print(f"  W-NAMED — `{rel}` contains {hi} at >= 0.99 while containing topw_k4 at "
                  f"{('n/a' if tw is None else f'{tw:.4f}')}.")
        print(f"  The emitting TABLE is named from the object rather than from a filename, and every")
        print(f"  number computed off these arms belongs to that instrument.")
        print(f"  ⚠ NAMING THE TABLE IS THE CLAIM. Which MODEL produced that table is a different")
        print(f"    question and its filename is a name, not evidence about the weights.")
    else:
        v = "W_NOT_ON_DISK"
        print(f"  W-NOT-ON-DISK — no admitted table contains either `_08b` family above the floor.")
        print(f"  The emitting table was never committed, so these arms cannot be attributed to any")
        print(f"  instrument in this repo.")
        print(f"  ⛔ THAT IS WORSE THAN instrument-OTHER AND MUST BE SAID IN THOSE WORDS: every claim")
        print(f"     resting on an `_08b` arm is instrument-UNKNOWN, not instrument-0.8B. The suffix")
        print(f"     is a filename, and R423 already measured that it is not the default.")

    print(f"\n  ⚠ ONE RELEASE, committed bytes only. An emitter outside this repo is outside this test.")

    art = dict(source_sha256=hashlib.sha256(SELF.read_bytes()).hexdigest(), source_name=SELF.name,
               anchors=dict(pos_rate=r_pos, pos_n=n_pos, pos_total=d_pos,
                            neg_rate=r_neg, neg_n=n_neg, neg_total=d_neg),
               candidates=rows, skipped=skipped, named=named, verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r424_emitter_identification.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0 if v != "W_DENSE" else 1


if __name__ == "__main__":
    sys.exit(main())
