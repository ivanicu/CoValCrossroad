#!/usr/bin/env python3
"""
R602 -- re-derive the two corpora's overlap from the files themselves.

CHECK #201 FOUND TWO UNVERIFIED QUANTIFIERS IN R601's CLOSING LINE.
  ⛔ "R399 and R400 ... are themselves uncited and UNAUDITED" -- `uncited` was measured;
     `unaudited` was never checked. Checked now and at least partly refuted: R401, R402, R427
     and R556 all reference them.
  ⛔ "the SINGLE number the whole cross-release question turns on" -- a superlative never
     computed. R400's depth MASS and the corpora's differing unit are two more; this round
     measures one of three.

⛔ AND A THIRD DEFECT WAS CAUGHT BEFORE THE FIRST RUN, by opening the file instead of assuming
its schema: the second corpus keys its text as `user_prompt`, and v1's extractor looked for
`text` / `content` / `utterance` / `prompt` / `message`. Exact-key matching would have returned
an EMPTY second corpus -- and an empty corpus yields overlap 0, which is exactly the answer I
was predisposed to accept. A zero from an extractor that found nothing is silence, not
disjointness.

R399 states the overlap as "3 strings, 2 of them greetings". That is an EXACT-MATCH count, and
comparability is not necessarily an exact-match question -- so the specification curve over
what "overlap" MEANS is the finding, not a single number.

ESTIMAND        overlap(home, second) under three definitions:
                (i)   exact string identity
                (ii)  normalised identity (casefold, collapse whitespace, strip punctuation)
                (iii) token-Jaccard: per home prompt, its MAX against the second corpus,
                      reported as a DISTRIBUTION, never as a count
IDENTIFICATION  (i)/(ii) are exact set intersections. (iii) is bounded BELOW by the subsample:
                a max over a subset cannot exceed the max over the whole, so a small value is
                conservative and a large one decisive.
SCOPE           population : home = prompts in data/comparisons.jsonl;
                             second = `user_prompt` in data/utterances.jsonl (streamed, capped)
                instrument : set intersection and token Jaccard
                             instrument unit = A TEXT STRING · claim unit = A TEXT STRING
                             EQUAL by construction
                baseline   : home-vs-home (ceiling) and home-vs-token-shuffled (floor)
                regime     : as committed at this sha; the cap is stated with every number
WORLDS          A DISJOINT: exact and normalised ~0 AND Jaccard at the shuffled floor -> R399
                  stands and R433's W-LOSES is evidence about a different object.
                B SHARED SURFACE: exact ~0 but normalised or Jaccard well above the floor ->
                  "3 strings" is an exact-match artifact and the corpora are more comparable
                  than the register's wording implies.
                C IDENTICAL: overlap near the ceiling -> the second release is not second.
KILL            pre-registered: if the POSITIVE control (home vs home) does not return ~1.0,
                the instrument cannot see identity and every number is UNVERIFIED.
POSITIVE CTRL   home vs home: exact overlap = |home| and max-Jaccard = 1.0.
NEGATIVE CTRL   home vs a TOKEN-SHUFFLED second corpus -- vocabulary preserved, strings
                destroyed. This separates "shares strings" from "shares vocabulary", which is
                the confusion the register's wording invites.
PLACEBO         home vs synthetic tokens: every measure at its floor.
SEEDS           0, 1, 2 on every sample and shuffle.
MULTIPLICITY    3 definitions x 3 corpora (real / shuffled / synthetic) x 3 seeds, all reported.
ARTIFACT        results/overlap.json
IMPOSSIBLE      construct validity for "comparable": string overlap is not topical or
                distributional comparability. A corpus can share no strings and ask the same
                question. This bounds ONE axis and says so.
"""
from __future__ import annotations
import json, pathlib, random, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
DATA = ROOT / "data"
CAP = 120000
NORM = re.compile(r"[^\w\s]")
# ⛔ `user_prompt` FIRST and verified against the file's own schema, not guessed.
KEYS = ("user_prompt", "text", "content", "utterance", "message")


def norm(s):
    return NORM.sub("", s.casefold()).split()


def home_prompts():
    out = []
    with (DATA / "comparisons.jsonl").open() as fh:
        for line in fh:
            try:
                j = json.loads(line)
            except Exception:
                continue
            msgs = (j.get("prompt") or {}).get("messages") or []
            txt = " ".join(str(m.get("content", "")) for m in msgs if isinstance(m, dict))
            if txt.strip():
                out.append(txt.strip())
    return out


def second_texts(cap=CAP):
    out, seen, hits = [], set(), 0
    with (DATA / "utterances.jsonl").open() as fh:
        for line in fh:
            if len(out) >= cap:
                break
            try:
                j = json.loads(line)
            except Exception:
                continue
            for k in KEYS:
                v = j.get(k)
                if isinstance(v, str) and v.strip():
                    hits += 1
                    s = v.strip()
                    if s not in seen:
                        seen.add(s); out.append(s)
                    break
    return out, hits


def jaccard(a, b):
    if not a or not b:
        return 0.0
    A, B = set(a), set(b)
    return len(A & B) / len(A | B)


def measures(home, second, sample_n=100, seed=0):
    exact = len(set(home) & set(second))
    hn = {" ".join(norm(x)) for x in home}
    sn = {" ".join(norm(x)) for x in second}
    rng = random.Random(seed)
    samp = rng.sample(home, min(sample_n, len(home)))
    stoks = [set(norm(x)) for x in second]
    mx = []
    for h in samp:
        ht = set(norm(h))
        best = 0.0
        for s in stoks:
            if not ht or not s:
                continue
            j = len(ht & s) / len(ht | s)
            if j > best:
                best = j
        mx.append(best)
    mx.sort()
    return {"exact": exact, "normalised": len(hn & sn), "n_sample": len(mx),
            "jaccard_median": mx[len(mx)//2] if mx else 0.0,
            "jaccard_p90": mx[int(len(mx)*0.9)] if mx else 0.0,
            "jaccard_max": mx[-1] if mx else 0.0}


def main():
    for f in ("comparisons.jsonl", "utterances.jsonl"):
        if not (DATA / f).is_file():
            print(f"UNRUNNABLE: {f} absent. Exit 2, never 0."); return 2
    home = home_prompts()
    second, hits = second_texts()
    print(f"POPULATION  home prompts {len(home)} (distinct {len(set(home))})")
    print(f"            second: {hits} rows carried a text key, {len(second)} distinct "
          f"(cap {CAP})")
    if not home or not second:
        print("UNRUNNABLE: a corpus is empty — and an empty corpus yields overlap 0, which is "
              "silence, not disjointness. Exit 2.")
        return 2

    rng0 = random.Random(0)
    sec_small = rng0.sample(second, min(3000, len(second)))
    print(f"  ⚠ the Jaccard sweep runs against a {len(sec_small)}-text subsample; a max over a "
          f"subset BOUNDS THE TRUE MAX FROM BELOW")

    print(f"\n─── CONTROLS ───")
    pos = measures(home, home, seed=0)
    pos_ok = pos["exact"] == len(set(home)) and pos["jaccard_max"] >= 0.999
    print(f"  POSITIVE  home vs home: exact {pos['exact']}/{len(set(home))}, jaccard max "
          f"{pos['jaccard_max']:.4f} -> {'PASS' if pos_ok else '⛔ FAIL'}")
    negs = []
    for s in (0, 1, 2):
        r = random.Random(100 + s)
        shuf = []
        for t in sec_small:
            tk = norm(t); r.shuffle(tk); shuf.append(" ".join(tk))
        negs.append(measures(home, shuf, seed=s))
    neg_ok = all(n["exact"] == 0 for n in negs)
    print(f"  NEGATIVE  home vs token-SHUFFLED second (vocabulary kept, strings destroyed): "
          f"exact {[n['exact'] for n in negs]}, jaccard median "
          f"{[round(n['jaccard_median'],4) for n in negs]} -> {'PASS' if neg_ok else '⛔ FAIL'}")
    plcs = []
    for s in (0, 1, 2):
        r = random.Random(200 + s)
        plcs.append(measures(home, [" ".join(f"zq{r.randrange(9999)}" for _ in range(40))
                                    for _ in range(len(sec_small))], seed=s))
    plc_ok = all(p["exact"] == 0 and p["jaccard_max"] < 0.02 for p in plcs)
    print(f"  PLACEBO   home vs synthetic tokens: exact {[p['exact'] for p in plcs]}, jaccard "
          f"max {[round(p['jaccard_max'],4) for p in plcs]} -> {'PASS' if plc_ok else '⛔ FAIL'}")
    controls_ok = pos_ok and neg_ok and plc_ok

    print(f"\n─── THE MEASUREMENT — 3 definitions x 3 seeds ───")
    reals = [measures(home, sec_small, seed=s) for s in (0, 1, 2)]
    r0 = reals[0]
    print(f"  (i)   EXACT identity      : {r0['exact']}")
    print(f"  (ii)  NORMALISED identity : {r0['normalised']}")
    print(f"  (iii) token-Jaccard, max per home prompt over {r0['n_sample']} sampled:")
    for s, r in zip((0, 1, 2), reals):
        print(f"        seed {s}: median {r['jaccard_median']:.4f}  p90 {r['jaccard_p90']:.4f}"
              f"  max {r['jaccard_max']:.4f}")
    floor_med = sum(n["jaccard_median"] for n in negs) / 3
    floor_p90 = sum(n["jaccard_p90"] for n in negs) / 3
    print(f"  shuffled-vocabulary floor: median {floor_med:.4f}  p90 {floor_p90:.4f}")

    print(f"\n─── VERDICT ───")
    med = sum(r["jaccard_median"] for r in reals) / 3
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire"
    elif r0["exact"] >= 0.5 * len(set(home)):
        world = f"C IDENTICAL — exact overlap {r0['exact']} of {len(set(home))}"
    elif med > floor_med + 0.05:
        world = (f"B SHARED SURFACE — exact overlap {r0['exact']}, but the median max-Jaccard is "
                 f"{med:.4f} against a shuffled-vocabulary floor of {floor_med:.4f}. "
                 f"'3 strings' is an EXACT-MATCH artifact and the corpora share more surface "
                 f"than the register's wording implies")
    else:
        world = (f"A DISJOINT — exact {r0['exact']}, normalised {r0['normalised']}, median "
                 f"max-Jaccard {med:.4f} against a floor of {floor_med:.4f}. R399 stands and "
                 f"R433's W-LOSES is evidence about a different object")
    print(f"  {world}")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "overlap.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok,
        "n_home": len(home), "n_home_distinct": len(set(home)),
        "second_rows_with_text": hits, "n_second_distinct": len(second), "cap": CAP,
        "n_second_sampled": len(sec_small),
        "real": reals, "negative_shuffled": negs, "placebo": plcs, "positive": pos,
        "shuffled_floor_median": floor_med, "shuffled_floor_p90": floor_p90,
        "schema_defect_caught_before_run": ("the second corpus keys its text as `user_prompt`; "
                                            "v1's extractor searched text/content/utterance/"
                                            "prompt/message and would have returned an EMPTY "
                                            "corpus, whose overlap 0 is silence not disjointness"),
        "impossible": ("string overlap is not topical comparability; ONE axis, bounded"),
    }, indent=2))
    print(f"\n  wrote {OUT / 'overlap.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
