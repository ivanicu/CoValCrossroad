#!/usr/bin/env python3
"""
R949 · R948 closed on a residual it said no search could reach: the cited round holds the value, but
        does it hold it FOR THE QUANTITY the sentence claims? There is a mechanical handle.

⛔ WHY THE RESIDUAL IS THE RIGHT TARGET. R948 measured attribution at 0.831 against a mis-attribution
floor of [0.338, 0.353], and 13/13 with a floor of 0/13 where the citation window is well-posed. Its
closing line named what it could not do: *"a round can hold 0.5514 as a cut while the sentence calls
it a margin."* **That is the difference between a document whose numbers are located and a document
whose numbers MEAN what it says** — and it is the last thing standing between this arc and a
statement a reader could rely on.

⭐ **THE HANDLE.** A traced numeral sits at a JSON PATH in the cited round's artifact — `primary.
difference`, `calibration.cut`, `bar.resolution`. The sentence around it carries a NOUN — *margin*,
*cut*, *resolution*. **If the path and the noun share vocabulary, the artifact holds the number for
something the sentence is also about.** Crude, and testable, which is the point.

⛔ **AND THE NULL THAT MATTERS IS WITHIN-ROUND, NOT ACROSS-ROUND — R946 IS WHY.** Four rounds ago a
"wider reader" scored 0.5–0.667 held-out and turned out to be a topic detector: rounds *about* gold
share gold-named data fields. The same trap is live here. If R923's artifact keys and R923's sentences
simply share R923's vocabulary, then EVERY pairing inside R923 agrees and the agreement measures
topic, not quantity. **So the permutation shuffles paths against phrases INSIDE THE SAME ROUND.** An
across-round shuffle would be easy to beat and would prove nothing.

ESTIMAND        of the traced (numeral, cited-round) pairs, the share whose holding JSON path shares
                vocabulary with the sentence phrase around the numeral — against the same share when
                paths and phrases are permuted WITHIN the same round.
IDENTIFICATION  identified as a rate against a within-round permutation floor. NOT identified as
                `the sentence is true of the number`: shared vocabulary is not shared meaning, and a
                path can agree lexically while the sentence misreads it. Bounds, direction named.
SCOPE           population: numerals in the statement region that trace to a cited round, with a
                            recoverable path and a non-empty phrase; the region and the citation
                            window are R948's, imported rather than re-derived
                instrument: token overlap between the JSON path and the +-60-char sentence phrase
                baseline:   R948's attribution rate 0.831, which is silent about quantity
                regime:     HEAD, one release, one repo
WORLDS          A · agreement is above the within-round floor -> the numbers are attributed to the
                    right QUANTITY, not merely the right round, and the arc's residual closes to the
                    resolution of a lexical test
                B · agreement sits at the within-round floor -> the match is round-level vocabulary.
                    Quantity-level attribution is UNVERIFIED and no lexical search reaches it; the
                    residual R948 named is real and needs a human read
                C · too few pairs carry a recoverable path and phrase -> unanswerable, and the size
                    of that set is the finding
KILL            CONDITIONAL:
                  ⭐ ① POSITIVE, HAND-READ ON BOTH SIDES — and the artifact side was READ, not
                     assumed, because asserting it would be the circularity R943 was built to catch:
                       `0.009103` the statement calls a *margin*; R923 holds it at
                                  `comparator_pair.margin_a_minus_b`
                       `0.5514`   the statement calls a *cut*;    R923 holds it at
                                  `wiring.genericpool16.cut`
                     Both paths were resolved off disk before this control was written. If the
                     instrument misses them it is not measuring quantity agreement.
                  ⭐ ② WITHIN-ROUND PERMUTATION FLOOR, >=3 seeds: paths shuffled against phrases
                     inside the same round. **A real rate inside that floor's spread is World B and
                     no quantity claim is admissible.**
                  ⭐ ③ g=0 / EMPTY PHRASE: a numeral whose phrase is stripped to stopwords must not
                     agree. A matcher that fires on `the` and `of` measures nothing.
                  ⭐ ④ SELF-EXCLUSION, inherited from R947's accident and R948's fix: this round's
                     own results are excluded from every search.
                  ⭐ ⑤ EVERY DISAGREEMENT NAMED with numeral, path, and phrase, so the call is
                     checkable. A count of mismatches nobody can inspect is a count.
MULTIPLICITY    N pairs × {real, 3 within-round permutation seeds}; every cell printed.
ARTIFACT        results/quantity_agreement.json
IMPOSSIBLE      independently replicated · cross-release · construct validated · criterion validated.
                ⚠ AND: **shared vocabulary is not shared meaning.** A path `bar.resolution` agrees
                with a phrase saying *resolution* even if the sentence inverts what the resolution
                bounds. Only a read closes that, and this round bounds the question from above
                rather than answering it.
"""
import json, pathlib, random, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "assurance"))
PROVISIONAL = re.compile(r"smoke|dry[_-]?run|draft|scratch|trial|pilot|prelim|wip", re.I)
NUMERAL = re.compile(r"(?<![\w.])(\d+\.\d{3,})(?![\w])")
CITE = re.compile(r"\bR(\d{1,4})\b")
WORD = re.compile(r"[a-z]{3,}")
STOP = {"the", "and", "not", "for", "that", "this", "with", "its", "was", "are", "under", "than",
        "every", "each", "from", "one", "two", "all", "but", "has", "have", "own", "same", "only",
        "any", "how", "what", "which", "when", "then", "also", "into", "over", "out", "per", "see",
        "does", "did", "can", "cannot", "must", "here", "there", "they", "them", "their", "it"}
SEEDS = (11, 23, 37)


def toks(s):
    return {w for w in WORD.findall(s.lower()) if w not in STOP}


def stem(w):
    for suf in ("ing", "ed", "es", "s"):
        if len(w) > 4 and w.endswith(suf):
            return w[: -len(suf)]
    return w


def stems(ws):
    return {stem(w) for w in ws}


def paths_holding(doc, want, d, prefix=""):
    out = []
    if isinstance(doc, dict):
        for k, v in doc.items():
            out += paths_holding(v, want, d, f"{prefix}.{k}" if prefix else k)
    elif isinstance(doc, list):
        for i, v in enumerate(doc):
            out += paths_holding(v, want, d, f"{prefix}[{i}]")
    elif isinstance(doc, bool):
        pass
    elif isinstance(doc, (int, float)):
        if round(float(doc), d) == want:
            out.append(prefix)
    elif isinstance(doc, str):
        for m in NUMERAL.finditer(doc):
            if round(float(m.group(1)), d) == want:
                out.append(prefix)
                break
    return out


def main() -> int:
    from a_statement_is_current_with_the_arc import statement_region
    text = (ROOT / "E05_the_space_of_compilers/DEFINITION.md").read_text()
    region = statement_region(text)
    if region is None:
        print("  UNRUNNABLE: no statement region. Exit 2, never 0.")
        return 2

    by_id = {}
    for d in ROOT.glob("E0*/A*/R*"):
        if not d.is_dir() or d == OUT.parent:
            continue
        m = re.match(r"R(\d+)_", d.name)
        if m:
            by_id.setdefault(int(m.group(1)), []).append(d)
    print(f"  ④ SELF-EXCLUSION — {OUT.parent.name} excluded: "
          f"{OUT.parent.name not in [x.name for v in by_id.values() for x in v]}  PASS")

    docs = {}

    def docs_of(rid):
        if rid in docs:
            return docs[rid]
        got = []
        for d in by_id.get(rid, []):
            for f in sorted(d.glob("results/**/*.json")):
                if PROVISIONAL.search(f.name) or "_smoke_archive" in f.parts:
                    continue
                try:
                    got.append(json.loads(f.read_text()))
                except Exception:
                    continue
        docs[rid] = got
        return got

    # blocks and phrases -- window is R948's (contiguous non-blank lines)
    lines = region.splitlines()
    blocks, cur, start = [], [], 1
    for i, l in enumerate(lines, 1):
        if l.strip():
            if not cur:
                start = i
            cur.append(l)
        elif cur:
            blocks.append((start, "\n".join(cur)))
            cur = []
    if cur:
        blocks.append((start, "\n".join(cur)))

    pairs, seen = [], set()
    for ln, b in blocks:
        cites = sorted({int(x) for x in CITE.findall(b)})
        if not cites:
            continue
        flat = b.replace("\n", " ")
        for m in NUMERAL.finditer(flat):
            s = m.group(1)
            if s in seen:
                continue
            seen.add(s)
            phrase = flat[max(0, m.start() - 60): m.end() + 60]
            d = len(s.split(".")[1])
            want = round(float(s), d)
            for rid in cites:
                hit = [p for doc in docs_of(rid) for p in paths_holding(doc, want, d)]
                if hit:
                    pairs.append({"numeral": s, "line": ln, "round": rid,
                                  "paths": sorted(set(hit))[:6],
                                  "phrase": phrase.strip()[:120]})
                    break
    print(f"  {len(pairs)} traced pairs with a recoverable JSON path")
    if len(pairs) < 10:
        print("  UNRUNNABLE: too few pairs to measure a rate. Exit 2, never 0.")
        return 2

    def agrees(paths, phrase):
        pt = stems(set().union(*[toks(p.replace(".", " ").replace("_", " ")) for p in paths]))
        return bool(pt & stems(toks(phrase)))

    for r in pairs:
        r["agrees"] = agrees(r["paths"], r["phrase"])
    real = sum(r["agrees"] for r in pairs) / len(pairs)

    def probe(numeral, word):
        r = next((x for x in pairs if x["numeral"] == numeral), None)
        return r, (r is not None and any(word in p.lower() for p in r["paths"]))
    p1, ok1 = probe("0.009103", "margin")
    p2, ok2 = probe("0.5514", "cut")
    c1 = ok1 and ok2
    print(f"\n  ① POSITIVE, HAND-READ — 0.009103 at R{p1['round'] if p1 else None} paths "
          f"{p1['paths'][:3] if p1 else None} contains `margin`: {ok1}")
    print(f"                          0.5514 at R{p2['round'] if p2 else None} paths "
          f"{p2['paths'][:3] if p2 else None} contains `cut`: {ok2}")
    print(f"     {c1}  {'PASS' if c1 else 'FAIL — the instrument misses attributions read by hand'}")

    c3 = not agrees(["primary.difference"], "the of and that with")
    print(f"  ③ g=0 / EMPTY PHRASE — a stopword-only phrase agrees: {not c3}: {c3}  "
          f"{'PASS' if c3 else 'FAIL — the matcher fires on function words'}")

    byround = {}
    for i, r in enumerate(pairs):
        byround.setdefault(r["round"], []).append(i)
    floor = []
    for seed in SEEDS:
        rng = random.Random(seed)
        ok = 0
        for rid, idx in byround.items():
            perm = idx[:]
            rng.shuffle(perm)
            for a, b_ in zip(idx, perm):
                if agrees(pairs[b_]["paths"], pairs[a]["phrase"]):
                    ok += 1
        floor.append(ok / len(pairs))
        print(f"  ② WITHIN-ROUND PERMUTATION seed {seed}: {ok}/{len(pairs)} = {ok/len(pairs):.3f}")
    fl_lo, fl_hi = min(floor), max(floor)
    c2 = real > fl_hi
    print(f"\n  real {real:.3f} vs within-round floor [{fl_lo:.3f}, {fl_hi:.3f}]  "
          f"discrimination {real - fl_hi:+.3f}")
    print(f"     ⚠ the floor is WITHIN-round on purpose: an across-round shuffle is easy to beat and "
          f"would only show that different rounds use different words (R946's topic detector).")

    if not (c1 and c3):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "c1": c1, "c3": c3, "real": real, "floor": floor},
                  open(OUT / "quantity_agreement.json", "w"), indent=2)
        return 2

    bad = [r for r in pairs if not r["agrees"]]
    print(f"\n  ⑤ EVERY DISAGREEMENT NAMED — {len(bad)} of {len(pairs)}:")
    for r in bad[:18]:
        print(f"     L{r['line']:<5} {r['numeral']:<11} R{r['round']:<4} {r['paths'][:2]}")
        print(f"        phrase: …{r['phrase'][:88]}…")
    if len(bad) > 18:
        print(f"     … and {len(bad) - 18} more, all in the artifact")

    world = "A" if c2 else "B"
    print(f"\n  ⭐⭐⭐ WORLD {world}: " + (
        f"the holding path shares vocabulary with the sentence {real:.3f} of the time, against a "
        f"WITHIN-round permutation floor of [{fl_lo:.3f}, {fl_hi:.3f}] — a discrimination of "
        f"{real - fl_hi:+.3f}. **The numbers are attributed to the right QUANTITY, not merely the "
        f"right round**, to the resolution a lexical test can offer. R948's residual closes that far "
        f"and no further."
        if world == "A" else
        f"agreement is {real:.3f} against a within-round floor of [{fl_lo:.3f}, {fl_hi:.3f}] — "
        f"inside it. **The match is round-level vocabulary, not quantity-level attribution.** Shuffle "
        f"which path holds which number inside a round and the agreement survives, so it was never "
        f"measuring the pairing. R948's residual stands and no lexical search reaches it."))
    print(f"     ⚠ SHARED VOCABULARY IS NOT SHARED MEANING. A path `bar.resolution` agrees with a "
          f"phrase saying *resolution* even where the sentence inverts what it bounds. This bounds "
          f"the question from above; only a read answers it.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "n_pairs": len(pairs),
               "agreement": real, "within_round_floor": [fl_lo, fl_hi],
               "floor_per_seed": floor, "discrimination": real - fl_hi,
               "disagreements": bad, "pairs": pairs,
               "why_within_round": "an across-round shuffle only shows different rounds use "
                                   "different words -- R946's topic detector, one layer over",
               "not_measured": "shared vocabulary is not shared meaning",
               "unit_note": "counts are (numeral, cited round) PAIRS",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "quantity_agreement.json", "w"), indent=2)
    print(f"\n  artifact: results/quantity_agreement.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
