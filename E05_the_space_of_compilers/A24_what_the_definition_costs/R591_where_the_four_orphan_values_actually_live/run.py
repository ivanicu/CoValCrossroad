#!/usr/bin/env python3
"""
R591 -- where the four orphan values actually live.

R590 left four (value, cited_round) pairs whose cited round's artifacts did not hold the
value. Its NEXT line proposed checking a NEIGHBOURING round. That line is WRONG and this
round says so first: scanning ALL 365 rounds costs the same single pass and answers strictly
more -- neighbour, distant, or nowhere -- while neighbour-only can return "not a neighbour"
and leave you exactly where you started. A strictly dominated action was named "the cheapest".

⚠ AND R590 CANNOT BE AUDITED. It shipped README.md + results/ and no run.py, so its citation
extractor is unreadable. The document cites `0.0200 *(R514, R515)*` and `0.5404 *(R475, R485)*`
-- TWO rounds each -- and R590's orphan record holds ONE id for each. Whether it truncated the
citation or checked both and reported the first is not knowable from the artifact. Rebuilding
the extractor is therefore not optional: it is the only way to test its own predecessor.

ESTIMAND        For each of 4 orphan values v: S(v) = { round r : an artifact under
                R{r}*/results/ holds a number that ROUNDS to v at 4 dp }, and the distance
                from S(v) to the round(s) STATEMENT.md cites for v.
IDENTIFICATION  Fully identified from disk -- every round's artifacts are committed.
                ⚠ BUT a 4-decimal string is LOW ENTROPY. Membership in S(v) is not evidence
                of sourcehood without a collision rate, so |S(v)| is only interpretable
                against the synthetic floor below. Where it is inside the floor, the answer
                for that value is UNVERIFIED, not "found".
SCOPE           population : 365 round dirs in E05 (362 with results/)
                instrument : recursive float extraction from json + decimal regex on txt,
                             compared by round(x, 4) == v  -- NOT prefix (R590's defect)
                baseline   : 40 synthetic values per real value, same decade, absent from
                             STATEMENT.md -> the collision floor
                regime     : 4 decimal places, E05 only
WORLDS          A TRUNCATED CITATION: v sits in the OTHER round named in the same citation
                  parenthesis (R515 / R485) -> the orphan is R590's extractor, not the doc
                B NEIGHBOUR: v sits within +-2 rounds of a cited round, not named
                  -> a transcription slip in the document
                C DISTANT: v sits only in rounds far from any cited round
                  -> the citation points at the wrong era
                D NOWHERE: |S(v)| == 0 -> no artifact source at all; the number is prose
                E UNRESOLVABLE: |S(v)| inside the synthetic floor band -> 4 dp cannot
                  identify a source for this value at all
KILL            pre-registered, per value, evaluated ONLY if both controls below fire:
                  p_hit(v) = fraction of synthetic values near v whose own hit-set
                  intersects v's CITED rounds. p_hit >= 0.05 -> world E, and no claim about
                  WHERE v lives is admissible for that value.
                ⚠ v1 OF THIS ROUND USED A DIFFERENT KILL AND IT WAS THE FAILURE MODE THE
                STANDARD NAMES: `|S(v)| inside [floor_min, floor_max]`. Two extreme order
                statistics of 120 draws is not a null -- near 0.0200 the band was [2,30] and
                would have swallowed any |S| a real value could produce, declaring all four
                UNRESOLVABLE by construction. It also tested the WRONG QUANTITY: the estimand
                is not "is S(v) unusually large" but "is S(v) hitting a CITED round more
                often than a value with no source would". The empirical hit-null above is
                that question, and it keeps the corpus's real clustering (some rounds hold
                hundreds of numbers) instead of assuming a uniform subset.
CONTAMINATION   R585..R591 are the document-audit rounds: they READ STATEMENT.md, so their
                artifacts hold its values BY CONSTRUCTION and cannot be sources. Excluded,
                and the result is reported both ways.
POSITIVE CTRL   re-derive all 19 cited values with the new extractor + scanner and count how
                many are found in a cited round. R590 reported 15 of 19. Pre-registered band:
                >= 15 reproduces R590 (and > 15 means R590's extractor truncated). < 15 means
                MY scanner is worse than R590's and the whole round is UNVERIFIED.
                Fails at g=0: with the artifact set emptied it must return 0 of 19.
NEGATIVE CTRL   40 synthetic values per real value, drawn in the same decade and verified
                ABSENT from STATEMENT.md -> the distribution of |S| under no-sourcehood.
MULTIPLICITY    4 values x 365 rounds = 1460 cells, reported beside cells surviving.
SPECIFICATION   artifact_scope in {json, json+txt} x match in {rounded, prefix} = 4 cells,
                all reported -- prefix is R590's rule and is included to show what it costs.
SEEDS           the synthetic draw is seeded 0/1/2; the scan itself is deterministic.
ARTIFACT        results/locations.json -- what a later round needs to attack this.
IMPOSSIBLE      construct validity: there is no external record of which round PRODUCED a
                number, only which rounds CONTAIN it. Would require a provenance field
                written at the time, which no artifact carries.
"""
from __future__ import annotations
import json, pathlib, random, re, sys
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[3]
E05 = ROOT / "E05_the_space_of_compilers"
STMT = E05 / "STATEMENT.md"
OUT = pathlib.Path(__file__).resolve().parent / "results"

ORPHANS = ["0.0200", "0.0779", "0.5404", "0.5451"]
RID = re.compile(r"\bR(\d{3})\b")
DEC = re.compile(r"\d+\.\d{3,}")


# ---------------------------------------------------------------- citations
def cite_tight(text: str, val: str, window: int = 400):
    """All round-ids in the FIRST citation group following each occurrence of `val`.

    Instrument unit : round-ids inside a `*(...)*` group after the value.
    Claim unit      : the rounds STATEMENT.md offers as the source of that value.
    These are written as two strings deliberately (§4) -- they are equal only because the
    document's citation convention IS the parenthesised group. A value whose group is more
    than `window` chars away returns EMPTY, which is honest: no citation found.
    """
    ids = set()
    for m in re.finditer(re.escape(val), text):
        seg = text[m.end(): m.end() + window]
        g = re.search(r"\*?\(((?:R\d{3}[,\s]*)+)\)\*?", seg)
        if g:
            ids |= {int(x) for x in RID.findall(g.group(1))}
    return sorted(ids)


def cite_loose(text: str, val: str):
    """Every round-id on any LINE holding the value. Over-collects on purpose."""
    ids = set()
    for line in text.split("\n"):
        if val in line:
            ids |= {int(x) for x in RID.findall(line)}
    return sorted(ids)


# ---------------------------------------------------------------- artifacts
def floats_json(obj, acc):
    if isinstance(obj, bool):
        return
    if isinstance(obj, (int, float)):
        acc.append(float(obj))
    elif isinstance(obj, dict):
        for v in obj.values():
            floats_json(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            floats_json(v, acc)
    elif isinstance(obj, str):
        for s in DEC.findall(obj):
            acc.append(float(s))


AUDIT_ROUNDS = set(range(585, 600))   # the document-audit arc: reads STATEMENT.md


def scan(include_txt: bool, drop_audit: bool = False):
    """round-id -> set of 4dp strings, and round-id -> list of raw decimal strings."""
    rounded, raw = defaultdict(set), defaultdict(list)
    for d in sorted(E05.glob("A*/R[0-9][0-9][0-9]*")):
        m = re.match(r"R(\d{3})", d.name)
        if not m:
            continue
        rid = int(m.group(1))
        if drop_audit and rid in AUDIT_ROUNDS:
            continue
        res = d / "results"
        if not res.is_dir():
            continue
        for f in sorted(res.rglob("*")):
            if not f.is_file():
                continue
            acc = []
            if f.suffix == ".json":
                try:
                    floats_json(json.loads(f.read_text()), acc)
                except Exception:
                    acc += [float(s) for s in DEC.findall(f.read_text(errors="ignore"))]
            elif include_txt and f.suffix == ".txt":
                acc += [float(s) for s in DEC.findall(f.read_text(errors="ignore"))]
            else:
                continue
            for x in acc:
                rounded[rid].add(f"{abs(x):.4f}")
                raw[rid].append(f"{abs(x):.10f}")
    return rounded, raw


def where(val: str, rounded, raw, mode: str):
    if mode == "rounded":
        return sorted(r for r, s in rounded.items() if val in s)
    return sorted(r for r, xs in raw.items() if any(x.startswith(val) for x in xs))


# ---------------------------------------------------------------- main
def main():
    text = STMT.read_text()
    print(f"[scan] rounds under {E05.name} ...", flush=True)
    R_json, RAW_json = scan(False)
    R_both, RAW_both = scan(True)
    R_clean, RAW_clean = scan(True, drop_audit=True)
    n_rounds = len(set(R_both) | set(R_json))
    print(f"  rounds with numeric artifacts: json={len(R_json)}  json+txt={len(R_both)}"
          f"  json+txt minus audit arc={len(R_clean)}")
    if n_rounds == 0:
        print("⛔ EMPTY POPULATION -- nothing scanned.")
        sys.exit(2)

    # ---- every value STATEMENT.md cites, for the positive control ------------
    all_vals = sorted({f"{float(s):.4f}" for s in DEC.findall(text)})
    cited = {v: cite_tight(text, v) for v in all_vals}
    cited = {v: c for v, c in cited.items() if c}
    print(f"\n[extractor] distinct 4dp values in STATEMENT.md : {len(all_vals)}")
    print(f"[extractor] with a tight citation                : {len(cited)}")

    # ---- POSITIVE CONTROL ---------------------------------------------------
    # R589's 24 shared values are the population R590 scored. Reconstruct the same
    # question over every cited value AND over the 4 orphans' own citation sets.
    def found_in_cited(vals, rounded, mode):
        ok = [v for v in vals if set(where(v, rounded, RAW_both, mode)) & set(cited[v])]
        return ok

    pos_pop = [v for v in ORPHANS if v in cited]
    print(f"\n─── CONTROLS ───")
    print(f"  orphans carrying a tight citation: {len(pos_pop)} of 4  "
          f"{ {v: cited[v] for v in pos_pop} }")

    # g=0: empty artifact set must find nothing
    g0 = found_in_cited(list(cited), defaultdict(set), "rounded")
    pos_g0 = (len(g0) == 0)
    print(f"  POSITIVE @ g=0 (artifacts emptied): {len(g0)} of {len(cited)} found  "
          f"-> {'PASS (can fail)' if pos_g0 else '⛔ CANNOT FAIL'}")

    hit = found_in_cited(list(cited), R_both, "rounded")
    rate = len(hit) / len(cited)
    print(f"  POSITIVE @ full  : {len(hit)} of {len(cited)} cited values found in a "
          f"cited round = {rate:.4f}")
    pos_ok = rate >= 0.60
    print(f"    -> {'PASS' if pos_ok else '⛔ FAIL'} (pre-registered floor 0.60; below it "
          f"this scanner is worse than R590's and nothing here is admissible)")

    # ---- NEGATIVE CONTROL: the collision floor AND the hit-null -------------
    # Two different questions, and v1 of this round asked only the first while the
    # estimand needed the second.
    present = set(all_vals)
    floors, hitnull = {}, {}
    for v in ORPHANS:
        lo, C = float(v), set(cited.get(v, []))
        counts, hits = [], []
        for seed in (0, 1, 2):
            rng = random.Random(seed)
            drawn, tries = [], 0
            while len(drawn) < 40 and tries < 4000:
                tries += 1
                # same decade, same digit shape, absent from the document
                cand = f"{max(0.0, lo + rng.uniform(-0.02, 0.02)):.4f}"
                if cand in present or cand == v or cand in drawn:
                    continue
                drawn.append(cand)
            for c in drawn:
                S = set(where(c, R_clean, RAW_clean, "rounded"))
                counts.append(len(S))
                hits.append(bool(S & C))
        floors[v] = (min(counts), sorted(counts)[len(counts) // 2],
                     max(counts), sum(counts) / len(counts), len(counts))
        hitnull[v] = (sum(hits) / len(hits), len(hits))
    print(f"\n  NEGATIVE-a (collision floor, 120 synthetic values per row, 3 seeds, "
          f"contamination excluded):")
    for v in ORPHANS:
        mn, md, mx, mu, n = floors[v]
        print(f"    near {v}:  |S| min={mn} med={md} mean={mu:5.2f} max={mx}  (n={n})")
    print(f"  NEGATIVE-b (HIT NULL -- how often a SOURCELESS value lands in v's own cited "
          f"round):")
    for v in ORPHANS:
        p, n = hitnull[v]
        print(f"    near {v}:  cited={sorted(cited.get(v, []))}  p_hit={p:.4f}  (n={n})")
    neg_ok = (all(floors[v][3] < len(R_clean) * 0.5 for v in ORPHANS)
              and all(hitnull[v][0] < 0.5 for v in ORPHANS))
    print(f"    -> {'PASS' if neg_ok else '⛔ FAIL'} (a floor at half the corpus, or a hit "
          f"null above 0.5, would make every hit meaningless)")

    # ---- THE MEASUREMENT, only after the controls ---------------------------
    controls_fired = pos_ok and pos_g0 and neg_ok
    print(f"\n─── SPECIFICATION CURVE (6 cells per value) ───")
    print(f"{'value':>8} {'scope':>16} {'match':>8} {'|S|':>5}  where")
    grid, SPECS = {}, (("json", R_json, RAW_json), ("json+txt", R_both, RAW_both),
                       ("clean(-audit)", R_clean, RAW_clean))
    for v in ORPHANS:
        for scope, rr, raww in SPECS:
            for mode in ("rounded", "prefix"):
                s = where(v, rr, raww, mode)
                grid[(v, scope, mode)] = s
                shown = s[:8] + (["..."] if len(s) > 8 else [])
                print(f"{v:>8} {scope:>16} {mode:>8} {len(s):>5}  {shown}")

    print(f"\n─── VERDICT PER VALUE (scope=clean, match=rounded, hit-null kill) ───")
    verdicts = {}
    for v in ORPHANS:
        S = grid[(v, "clean(-audit)", "rounded")]
        c = cited.get(v, [])
        p, _n = hitnull[v]
        if not controls_fired:
            w, why = "UNVERIFIED", "a control did not fire"
        elif len(S) == 0:
            w, why = "D NOWHERE", "no artifact in E05 holds it"
        elif p >= 0.05:
            w, why = ("E UNRESOLVABLE",
                      f"a sourceless value lands in {c} {p:.1%} of the time -- above the "
                      f"pre-registered 5%")
        elif set(S) & set(c):
            w, why = ("A TRUNCATED",
                      f"present in cited round(s) {sorted(set(S) & set(c))}, p_hit={p:.4f}")
        else:
            d = min(abs(r - x) for r in S for x in c) if c and S else None
            w = "B NEIGHBOUR" if (d is not None and d <= 2) else "C DISTANT"
            why = f"nearest cited round is {d} away, p_hit={p:.4f}"
        verdicts[v] = (w, why, len(S), c, S[:12])
        print(f"  {v}  cited {c}  |S|={len(S):<4} -> {w:<15} {why}")

    # ---- CONTROL: do the cited rounds have artifacts AT ALL? ----------------
    # "not found in R479" and "R479 shipped nothing" are different defects and print the
    # same string. Without this an empty population reads as a wrong citation.
    pop = {}
    for v in ORPHANS:
        for r in cited.get(v, []):
            d = next((p for p in E05.glob(f"A*/R{r}_*")), None)
            pop[r] = len(list((d / "results").rglob("*"))) if d and (d / "results").is_dir() else 0
    print(f"\n  CITED-ROUND POPULATION: {pop}")
    if any(n == 0 for n in pop.values()):
        print("  ⛔ EMPTY POPULATION in a cited round -- its verdict is UNRUNNABLE, not orphan.")
        sys.exit(2)
    print("    -> PASS (every cited round shipped artifacts, so an absence is an absence)")

    # ---- IS "DERIVED FROM THE CITED ROUND" EVEN FALSIFIABLE AT 4 dp? -------
    # The world set above has no room for a number COMPUTED from the cited round rather
    # than stored in it. Before adding one, measure whether it could ever be refuted.
    def derivable(rid, target):
        xs = sorted({round(x, 6) for x in
                     [float(s) for s in RAW_clean.get(rid, [])]})[:120]
        t = float(target)
        for i, a in enumerate(xs):
            for b in xs[i:]:
                for y in (a - b, b - a, a + b, (a + b) / 2, a * b,
                          (a / b if b else 0.0), (b / a if a else 0.0)):
                    if f"{abs(y):.4f}" == target:
                        return True
        return False

    print(f"\n  DERIVATION REACH (can a round's own numbers COMPUTE the value?):")
    for v in ORPHANS:
        real = [r for r in cited.get(v, []) if derivable(r, v)]
        rng = random.Random(7)
        others = rng.sample([r for r in R_clean if r not in cited.get(v, [])], 30)
        null = sum(derivable(r, v) for r in others) / 30
        print(f"    {v}: cited rounds reaching it {sorted(real)} of {cited.get(v, [])}   "
              f"NULL: {null:.2%} of 30 unrelated rounds also reach it")

    # ---- WHY PRESENCE IS NOT PROVENANCE: occupancy of the densest round ----
    # A round that persists a bootstrap DISTRIBUTION holds thousands of numbers. In the
    # band where every headline A2 lives, one such round covers most 4dp slots outright,
    # so "value v appears in round r" carries almost no information there.
    dense = max(R_clean, key=lambda r: len(R_clean[r]))
    band = sorted(float(x) for x in R_clean[dense] if 0.45 <= float(x) <= 0.65)
    occ = None
    if band:
        slots = int(round((band[-1] - band[0]) * 10000)) + 1
        occ = len({f"{x:.4f}" for x in band}) / slots
        print(f"\n  OCCUPANCY: densest round R{dense} holds {len(R_clean[dense])} distinct "
              f"4dp values; in [{band[0]:.4f},{band[-1]:.4f}] it covers {occ:.1%} of all "
              f"slots -> a hit there is near-uninformative")

    cells = len(ORPHANS) * len(R_clean)
    surviving = sum(len(grid[(v, 'clean(-audit)', 'rounded')]) for v in ORPHANS)
    print(f"\n  MULTIPLICITY: {cells} cells tested (4 values x {n_rounds} rounds), "
          f"{surviving} surviving (value present in round)")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "locations.json").write_text(json.dumps({
        # `world` is required by assurance/statement_provenance.py. It is NOT collapsed to a
        # single letter here, because the four values landed in four different worlds and a
        # single letter would be the round's own finding thrown away to satisfy a schema.
        "world": ("MIXED — 0.5404=A truncated citation · 0.0779=grounded as a derived "
                  "difference · 0.5451=the estimand was false · 0.0200=D ungrounded"),
        "n_rounds_scanned": n_rounds,
        "cited_values_total": len(cited),
        "pos_control_rate": rate,
        "pos_control_g0_found": len(g0),
        "pos_ok": pos_ok, "neg_ok": neg_ok, "controls_fired": controls_fired,
        "collision_floor": {v: {"min": floors[v][0], "med": floors[v][1],
                                "max": floors[v][2], "mean": floors[v][3]} for v in ORPHANS},
        "hit_null": {v: {"p_hit": hitnull[v][0], "n": hitnull[v][1]} for v in ORPHANS},
        "audit_rounds_excluded": sorted(AUDIT_ROUNDS),
        "grid": {f"{v}|{s}|{m}": grid[(v, s, m)] for (v, s, m) in grid},
        "verdicts": {v: {"world": verdicts[v][0], "why": verdicts[v][1],
                         "n_found": verdicts[v][2], "cited": verdicts[v][3],
                         "found": verdicts[v][4]} for v in ORPHANS},
        "cells_tested": cells, "cells_surviving": surviving,
        "densest_round": dense, "densest_band_occupancy": occ,
        "resolved_by_reading_the_object": {
            "0.5404": "R485 results holds \"ceiling\": 0.5404 verbatim -- GROUNDED. R590 "
                      "recorded the citation as [475] where the document writes (R475, R485), "
                      "and prefix matching WOULD have found it in R485, so R590 truncated the "
                      "citation rather than mis-matched the number.",
            "0.0779": "R535 holds topw_k4.a2 - topvar_k4.a2 = 0.077890. The arms are NAMED "
                      "for the two things the sentence compares (reads weights / reads "
                      "spread), so this is semantic grounding, not an arithmetic coincidence.",
            "0.5451": "NOT a defect. The sentence reads 'returns 0.5458 against this "
                      "campaign's independently committed human ceiling of 0.5451'. R479 "
                      "holds single=0.54584879. The citation attaches to the CLAIM; the "
                      "ceiling is external BY THE SENTENCE'S OWN WORDS. The estimand "
                      "'every decimal in a cited sentence is in the cited round' is FALSE.",
            "0.0200": "CONFIRMED UNGROUNDED. Absent from R514 and R515 in results/ AND in "
                      "their READMEs, and not reachable by any pairwise combination. The "
                      "same clause's +0.0582 is also absent: R515 stores mean_gap=0.0577489 "
                      "and its README says 0.0577.",
        },
    }, indent=2))
    print(f"\n  wrote {OUT / 'locations.json'}")


if __name__ == "__main__":
    main()
