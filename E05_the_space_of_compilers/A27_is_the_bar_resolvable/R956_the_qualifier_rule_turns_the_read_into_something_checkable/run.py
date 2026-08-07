#!/usr/bin/env python3
"""
R956 · R955 left 220 candidate pairs at t=4 and said only a read closes them. A read by the author
        of the document is the weakest evidence there is — so turn the read into a RULE.

⛔ WHY NOT SIMPLY READ THEM. Door ③: my judgement about my own document is self-review, and this
session cannot dispatch an independent reader. **A verdict I produce by reading is exactly the kind
of evidence this programme has retracted most often.** But R955's own confound is mechanizable, and
that is the way through.

⭐ **THE CONFOUND BECOMES THE FILTER.** R955 named it before running: the statement says *"cut
0.5514 (28 admitted) under `genericpool16`; 0.5593 (24) under `generic`"* — two values, near-identical
vocabulary, **both correct**, separated only by a QUALIFIER. So the question for each candidate pair
is decidable without judgement:
  · qualifiers DIFFER  -> the values SHOULD differ. **EXPLAINED**, not a contradiction.
  · qualifiers MATCH   -> same scoped quantity, different value. **REAL CANDIDATE**.
  · no qualifier on either side -> **UNDECIDABLE**, and it stays its own category.
Three-valued, because folding UNDECIDABLE into EXPLAINED would manufacture a clean document and
folding it into REAL would manufacture a crisis. Both are false acquittals in opposite directions.

⚠ **THE QUALIFIER IS READ AS BACKTICKED IDENTIFIERS AND `k=` VALUES**, which is what this document
uses for arm names, comparators and sizes — `generic`, `genericpool16`, `coval_core`, `k = 4`. That is
a property of the file's own notation, not a vocabulary I invented, and control ① checks it on the
pair I can point at in the statement.

ESTIMAND        of R955's 220 disagreeing pairs at t=4, the split into EXPLAINED (qualifiers differ),
                REAL CANDIDATE (qualifiers match) and UNDECIDABLE (no qualifier either side).
IDENTIFICATION  the split is exact given the qualifier extraction. `REAL CANDIDATE` is NOT identified
                as `contradiction`: two phrases can share every backticked token and still scope
                different quantities by prose alone. Bounds, and the direction is named.
SCOPE           population: the t=4 disagreeing pairs, RECOMPUTED here and required to reproduce
                            R955's committed counts (231 pairs, 11 agree, 220 disagree)
                instrument: backticked identifiers and `k=<n>` in the ±70-char window
                baseline:   R955's undifferentiated 220
                regime:     HEAD, one file
WORLDS          A · most pairs are EXPLAINED -> R955's 220 collapses to a small nameable residue and
                    the document is largely self-consistent where this instrument can see
                B · most are REAL CANDIDATES -> the document carries many same-scope value conflicts
                C · most are UNDECIDABLE -> the qualifier rule does not apply at this window, the
                    read cannot be mechanized, and R955's price stands unpaid
KILL            CONDITIONAL:
                  ⭐ ① POSITIVE, HAND-READ FROM THE STATEMENT: the pair `0.5514`/`0.5593` — which the
                     statement itself presents as two correct cuts under two named comparators —
                     must classify EXPLAINED. If the rule cannot recognise the case it was built
                     from, it recognises nothing.
                  ⭐ ② POSITIVE, PLANTED, OTHER DIRECTION: a synthetic pair with IDENTICAL
                     qualifiers and different values must classify REAL CANDIDATE. One direction
                     alone would only confirm the answer I expect.
                  ⭐ ③ REPRODUCTION: the recomputed t=4 counts must equal R955's committed
                     231/11/220. A round that recomputes its own population can move it.
                  ⭐ ④ THREE-VALUED: UNDECIDABLE is reported as its own number and never folded.
                  ⭐ ⑤ EVERY REAL CANDIDATE NAMED with both phrases and both qualifier sets.
MULTIPLICITY    220 pairs × {explained, real, undecidable}; all printed, all three counts reported.
ARTIFACT        results/qualifier_split.json
IMPOSSIBLE      independently replicated · cross-release · construct validated. ⚠ AND: **a matching
                qualifier set does not prove the same quantity.** Two phrases can name `generic` and
                still be about different statistics of it. The REAL CANDIDATE count bounds the
                contradiction count from ABOVE, and the residue still needs a reader — but a
                20-item residue is a different object from a 220-item one, which is the whole point.
"""
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "assurance"))
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"
DOC = ROOT / "E05_the_space_of_compilers/DEFINITION.md"
NUM = re.compile(r"(?<![\w.])(\d+\.\d{3,})(?![\w])")
WORD = re.compile(r"[a-z]{3,}")
QUAL = re.compile(r"`([^`\s]{2,32})`|\bk\s*=\s*(\d+)")
STOP = {"the", "and", "not", "for", "that", "this", "with", "its", "was", "are", "under", "than",
        "every", "each", "from", "one", "two", "all", "but", "has", "have", "own", "same", "only",
        "any", "how", "what", "which", "when", "then", "also", "into", "over", "out", "per", "see",
        "does", "did", "can", "cannot", "must", "here", "there", "they", "them", "their", "it"}
WIN, T = 70, 4


def stem(w):
    for s in ("ing", "ed", "es", "s"):
        if len(w) > 4 and w.endswith(s):
            return w[: -len(s)]
    return w


def toks(s):
    return {stem(w) for w in WORD.findall(s.lower()) if w not in STOP}


def quals(s):
    out = set()
    for m in QUAL.finditer(s):
        v = m.group(1) or (f"k={m.group(2)}" if m.group(2) else None)
        if v and not NUM.fullmatch(v):
            out.add(v)
    return out


def occurrences(text):
    flat = " ".join(text.splitlines())
    return [{"num": m.group(1),
             "phrase": flat[max(0, m.start() - WIN): m.end() + WIN].strip(),
             "tok": toks(flat[max(0, m.start() - WIN): m.end() + WIN])}
            for m in NUM.finditer(flat)]


def classify(a, b):
    qa, qb = quals(a["phrase"]), quals(b["phrase"])
    if not qa and not qb:
        return "UNDECIDABLE", qa, qb
    if qa and qb and qa != qb:
        return "EXPLAINED", qa, qb
    if qa == qb:
        return "REAL CANDIDATE", qa, qb
    return "UNDECIDABLE", qa, qb          # one side qualified, the other not


def main() -> int:
    from a_statement_is_current_with_the_arc import statement_region
    text = DOC.read_text()
    reg = statement_region(text)
    rec = text.replace(reg, "", 1)
    S, R = occurrences(reg), occurrences(rec)

    ag, dis = [], []
    for a in S:
        for b in R:
            if len(a["tok"] & b["tok"]) >= T:
                (ag if a["num"] == b["num"] else dis).append((a, b))
    prior = json.loads(next(A27.glob("R955_*/results/self_contradiction.json")).read_text())
    want = prior["curve"][str(T)]
    c3 = (len(ag) + len(dis) == want["n_pairs"] and len(ag) == want["agree"]
          and len(dis) == want["disagree"])
    print(f"  ③ REPRODUCTION — recomputed t={T}: {len(ag)+len(dis)} pairs, {len(ag)} agree, "
          f"{len(dis)} disagree; R955 committed {want['n_pairs']}/{want['agree']}/"
          f"{want['disagree']}: {c3}  {'PASS' if c3 else 'FAIL — the population moved'}")

    def mk(ph):
        return {"num": NUM.search(ph).group(1), "phrase": ph, "tok": toks(ph)}
    p_a = mk("**Calibration:** cut **0.5514** (28 admitted) under `genericpool16`")
    p_b = mk("cut **0.5593** (24) under `generic`. A cut quoted without its comparator")
    k1, qa1, qb1 = classify(p_a, p_b)
    c1 = k1 == "EXPLAINED"
    print(f"\n  ① POSITIVE, HAND-READ — the statement's own two correct cuts, "
          f"0.5514 under {sorted(qa1)} vs 0.5593 under {sorted(qb1)} -> {k1}: {c1}  "
          f"{'PASS' if c1 else 'FAIL — the rule cannot recognise the case it was built from'}")

    q_a = mk("the margin under `generic` is **0.111111** on this release")
    q_b = mk("the margin under `generic` is **0.222222** on this release")
    k2, _, _ = classify(q_a, q_b)
    c2 = k2 == "REAL CANDIDATE"
    print(f"  ② POSITIVE, PLANTED — identical qualifier `generic`, values 0.111111 vs 0.222222 "
          f"-> {k2}: {c2}  {'PASS' if c2 else 'FAIL — the rule only fires one way'}")

    if not (c1 and c2 and c3):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "c1": c1, "c2": c2, "c3": c3},
                  open(OUT / "qualifier_split.json", "w"), indent=2)
        return 2

    counts, real, seen = {"EXPLAINED": 0, "REAL CANDIDATE": 0, "UNDECIDABLE": 0}, [], set()
    for a, b in dis:
        k, qa, qb = classify(a, b)
        counts[k] += 1
        if k == "REAL CANDIDATE":
            key = (a["num"], b["num"], tuple(sorted(qa)))
            if key not in seen:
                seen.add(key)
                real.append({"statement_value": a["num"], "record_value": b["num"],
                             "qualifiers": sorted(qa),
                             "statement_phrase": a["phrase"][:130],
                             "record_phrase": b["phrase"][:130]})
    n = len(dis)
    print(f"\n  ④ THREE-VALUED, none folded — of {n} disagreeing pairs at t={T}:")
    for k in ("EXPLAINED", "REAL CANDIDATE", "UNDECIDABLE"):
        print(f"     {k:<16}{counts[k]:>5}   {counts[k]/n:.3f}")

    print(f"\n  ⑤ EVERY REAL CANDIDATE NAMED — {len(real)} distinct:")
    for r in real[:12]:
        print(f"     {r['statement_value']} vs {r['record_value']}   qualifiers {r['qualifiers']}")
        print(f"        S: …{r['statement_phrase'][:100]}…")
        print(f"        R: …{r['record_phrase'][:100]}…")
    if len(real) > 12:
        print(f"     … and {len(real) - 12} more, all in the artifact")

    top = max(counts, key=counts.get)
    world = {"EXPLAINED": "A", "REAL CANDIDATE": "B", "UNDECIDABLE": "C"}[top]
    print(f"\n  ⭐⭐⭐ WORLD {world}: " + (
        f"{counts['EXPLAINED']} of {n} disagreeing pairs ({counts['EXPLAINED']/n:.3f}) are EXPLAINED "
        f"— the two phrases name different qualifiers, so the values SHOULD differ. R955's "
        f"undifferentiated 220 collapses to **{len(real)} distinct real candidates**, every one "
        f"named above, plus {counts['UNDECIDABLE']} undecidable. A residue that size is a work item; "
        f"220 was a restatement of the problem."
        if world == "A" else
        f"{counts['REAL CANDIDATE']} of {n} pairs ({counts['REAL CANDIDATE']/n:.3f}) share their "
        f"qualifiers and still differ in value. **The document carries many same-scope conflicts**, "
        f"and {len(real)} distinct ones are named above."
        if world == "B" else
        f"{counts['UNDECIDABLE']} of {n} pairs ({counts['UNDECIDABLE']/n:.3f}) carry no usable "
        f"qualifier at this window, so the rule does not apply and **the read cannot be "
        f"mechanized**. R955's price stands unpaid, and the honest output is the three counts."))
    print(f"     ⚠ A MATCHING QUALIFIER SET DOES NOT PROVE THE SAME QUANTITY. Two phrases can both "
          f"name `generic` and still be about different statistics of it, so the real-candidate "
          f"count bounds contradictions from ABOVE and the residue still needs a reader.")
    print(f"     ⚠ AND THIS RULE IS MINE. It is checkable by anyone — the qualifiers are printed "
          f"beside every call — which is the property a read by the document's own author lacks.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "threshold": T,
               "n_disagreeing": n, "counts": counts,
               "n_distinct_real_candidates": len(real), "real_candidates": real,
               "reproduced_r955": bool(c3),
               "rule": "qualifiers differ -> EXPLAINED; qualifiers match -> REAL CANDIDATE; "
                       "no qualifier either side, or one side only -> UNDECIDABLE",
               "bound": "a matching qualifier set does not prove the same quantity; REAL CANDIDATE "
                        "bounds contradictions from ABOVE",
               "unit_note": "counts are PAIR INSTANCES; the named list is DISTINCT value+qualifier "
                            "triples, never summed",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "qualifier_split.json", "w"), indent=2)
    print(f"\n  artifact: results/qualifier_split.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
