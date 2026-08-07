#!/usr/bin/env python3
"""
R952 · R951 found the ledger declares no classes of its own. But an EXTERNAL taxonomy exists — §4 of
        the standard, 20 named failure modes. What share of the 1,149 retractions instances one?

⛔ WHY NOT THE ROUND I SAID I WOULD BUILD. R951 closed proposing a write-time gate requiring each new
retraction to declare its class. **That binds only future entries, and the question is about the 1,149
that exist.** A convention for tomorrow is not an answer about today, and closing a World C by
legislating rather than measuring is how a question gets retired without being settled.

⭐ **AND THE TAXONOMY DOES NOT HAVE TO BE MINE.** R951's whole design turned on refusing to invent
classes — reading 1,149 entries and grouping them by what they look like to me is a control validated
against my imagination. **§4 of the standard already names 20 failure modes, each introduced as `a
real, dated event, not a hypothetical`.** They were extracted here from the skill file itself, never
from memory. So the classes are external to the ledger and external to this round's author.

⭐⭐⭐ **AND THE ANSWER IS INFORMATIVE IN BOTH DIRECTIONS, WHICH IS WHAT MAKES IT A FORK.** §4 was
written FROM this programme. If coverage is high, Ivan's question has a measured answer — yes, the
same handful of errors, and here they are ranked. **If coverage is low, the standard's own taxonomy
under-represents its source**, which is a finding about the standard rather than about the ledger, and
a more uncomfortable one.

⚠ **A KEYWORD MATCHER IS THE INSTRUMENT §4 ITSELF RECORDS THREE FAILURES OF.** So: the keywords are
the mode NAMES' own tokens, never phrases I add; a match needs >=2 distinctive shared tokens, swept
over 1–3 as a specification curve; and the floor is measured with DECOY modes built by sampling the
ledger's own vocabulary at matched token counts. If decoys match as often, the instrument is measuring
vocabulary density and no coverage number is admissible.

ESTIMAND        the share of RETRACTIONS.md's numbered entries whose title shares >=t distinctive
                tokens with at least one §4 mode name, for t in {1,2,3}, against a decoy-mode floor.
IDENTIFICATION  identified as a rate against a measured floor. NOT identified as `this retraction IS
                that failure`: shared tokens are not shared mechanism. Bounds, direction named.
SCOPE           population: every `^## <n> · ` entry title in RETRACTIONS.md at HEAD (R951: 1,149)
                instrument: token overlap between the entry title and a §4 mode name, both stemmed
                baseline:   decoy modes drawn from the ledger's own vocabulary, matched on token
                            count and mode count, 3 seeds
                regime:     HEAD, one repo, one standard version
WORLDS          A · coverage well above the decoy floor and concentrated in a few modes -> the
                    retractions instance a small named set, and §0.2's question is answered from an
                    external taxonomy rather than from my reading
                B · coverage at the decoy floor -> the match is vocabulary density; the ledger's
                    errors cannot be assigned to §4 modes lexically and the question stays open
                C · coverage above the floor but LOW -> §4, written from this programme, names only
                    a minority of what its own source recorded. A finding about the standard.
KILL            CONDITIONAL:
                  ⭐ ① POSITIVE, HAND-READ: entry 437's title — `My verdict string ignored a failing
                     control` — must match §4's `the verdict string is not a computation`. Read off
                     the ledger before the matcher was written.
                  ⭐ ② g=0: a synthetic title made only of stopwords must match NO mode. A matcher
                     that fires on function words measures nothing.
                  ⭐ ③ DECOY FLOOR, 3 seeds: 20 decoy `modes` sampled from the ledger's own
                     vocabulary, matched on token count. **Real coverage inside the decoy spread is
                     World B and no share is admissible.**
                  ⭐ ④ SPECIFICATION: the threshold t is swept over 1–3, not chosen. A single cell
                     reported as the coverage is the failure this standard names at experiment scale.
                  ⭐ ⑤ ALL 20 MODES REPORTED including the zeros, and the unmatched share named with
                     examples, because reporting only the modes that fired is the multiplicity
                     failure with manners.
MULTIPLICITY    1,149 titles × 20 modes × 3 thresholds × (1 real + 3 decoy seeds); all printed.
ARTIFACT        results/mode_coverage.json
IMPOSSIBLE      independently replicated · cross-release · construct validated · criterion validated.
                ⚠ AND: **shared tokens are not shared mechanism.** An entry titled `my verdict string
                ignored a control` genuinely instances that mode; an entry that merely uses the word
                `control` does not. This bounds coverage from ABOVE and says so.
"""
import json
import pathlib
import random
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
LEDGER = ROOT / "RETRACTIONS.md"
SKILL = pathlib.Path("/home/ivan/.claude/skills/realstat/SKILL.md")
ENTRY = re.compile(r"^## (\d+) · (.+)$")
MODE_ROW = re.compile(r"^\| \*\*([^*]+)\*\*")
WORD = re.compile(r"[a-z]{3,}")
STOP = {"the", "and", "not", "for", "that", "this", "with", "its", "was", "are", "under", "than",
        "every", "each", "from", "one", "two", "all", "but", "has", "have", "own", "same", "only",
        "any", "how", "what", "which", "when", "then", "also", "into", "over", "out", "per", "see",
        "does", "did", "can", "cannot", "must", "here", "there", "they", "them", "their", "it"}
THRESHOLDS = (1, 2, 3)
SEEDS = (11, 23, 37)


def stem(w):
    for suf in ("ing", "ed", "es", "s"):
        if len(w) > 4 and w.endswith(suf):
            return w[: -len(suf)]
    return w


def toks(s):
    return {stem(w) for w in WORD.findall(s.lower()) if w not in STOP}


def main() -> int:
    if not SKILL.exists():
        print(f"  UNRUNNABLE: the standard is not at {SKILL}; the taxonomy must be read from the "
              f"object, never from memory. Exit 2, never 0.")
        return 2
    sk = SKILL.read_text(errors="replace")
    s4 = sk[sk.find("## §4"): sk.find("## §5")]
    modes = [m.group(1).strip() for m in
             (MODE_ROW.match(l) for l in s4.splitlines()) if m]
    print(f"  §4 taxonomy READ FROM THE OBJECT: {len(modes)} named modes")
    if len(modes) < 10:
        print("  UNRUNNABLE: mode extraction found too few rows. Exit 2, never 0.")
        return 2
    mode_toks = {m: toks(m) for m in modes}

    lines = LEDGER.read_text(errors="replace").splitlines()
    titles = {}
    for l in lines:
        m = ENTRY.match(l)
        if m:
            titles[int(m.group(1))] = m.group(2)
    print(f"  {len(titles):,} entry titles (R951 parsed the same population)")

    def best(title, table, t):
        """⛔ RETURNS THE ARGMAX SET, NOT A WINNER. The first version took max() over a dict, which
        breaks ties by declaration order -- and entry 437 ties at 2 tokens between `the control
        fails for its own reasons` and `the verdict string is not a computation`, so the control
        would have failed on an ordering artifact rather than a miss. Ties are a real property of a
        20-mode lexical taxonomy and are counted below rather than hidden by a tie-break."""
        tt = toks(title)
        hits = [(k, len(tt & v)) for k, v in table.items() if len(tt & v) >= t]
        if not hits:
            return []
        top = max(n for _, n in hits)
        return [k for k, n in hits if n == top]

    t437 = titles.get(437, "")
    m437 = best(t437, mode_toks, 2)
    c1 = "the verdict string is not a computation" in m437
    print(f"\n  ① POSITIVE, HAND-READ — entry 437 `{t437[:56]}…`")
    print(f"     -> argmax set {m437}: {c1}  "
          f"{'PASS — the hand-read mode is among the argmax' if c1 else 'FAIL — the matcher misses a mapping read off the object'}")

    c2 = not best("the of and that with from into over per", mode_toks, 1)
    print(f"  ② g=0 — a stopword-only title matches nothing: {c2}  "
          f"{'PASS' if c2 else 'FAIL — the matcher fires on function words'}")

    if not (c1 and c2):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "c1": c1, "c2": c2},
                  open(OUT / "mode_coverage.json", "w"), indent=2)
        return 2

    # decoy modes: the ledger's own vocabulary, matched on mode count and per-mode token count
    vocab = [w for t in titles.values() for w in toks(t)]
    curve, decoy_curve = {}, {}
    for t in THRESHOLDS:
        assigned = {n: best(ti, mode_toks, t) for n, ti in titles.items()}
        cov = sum(1 for v in assigned.values() if v) / len(titles)
        ties = sum(1 for v in assigned.values() if len(v) > 1)
        curve[t] = {"coverage": cov, "assigned": assigned, "ambiguous": ties}
        floors = []
        for seed in SEEDS:
            rng = random.Random(seed)
            decoys = {f"decoy{i}": set(rng.sample(vocab, len(mode_toks[m])))
                      for i, m in enumerate(modes)}
            floors.append(sum(1 for ti in titles.values() if best(ti, decoys, t))
                          / len(titles))
        decoy_curve[t] = floors
        print(f"\n  ④ t={t} — coverage {cov:.3f}   decoy floor "
              f"{[f'{f:.3f}' for f in floors]}  (max {max(floors):.3f})   "
              f"AMBIGUOUS (tied across >1 mode) {ties:,} = {ties/len(titles):.3f}")

    t = 2
    cov = curve[t]["coverage"]
    fl_lo, fl_hi = min(decoy_curve[t]), max(decoy_curve[t])
    c3 = cov > fl_hi
    print(f"\n  ③ DECOY FLOOR at t={t} — real {cov:.3f} vs [{fl_lo:.3f}, {fl_hi:.3f}]: {c3}  "
          f"{'PASS — not vocabulary density' if c3 else 'FAIL — decoys match as often'}")

    # ⚠ TWO UNITS, KEPT APART: a TITLE is matched once; an ATTRIBUTION is per tied mode, so the
    #   attributions can exceed the titles. Summing them would double a count, which is the
    #   namespace conflation R951's control ③ forbids, one object down.
    counts = {}
    for v in curve[t]["assigned"].values():
        for m in v:
            counts[m] = counts.get(m, 0) + 1
    n_attr = sum(counts.values())
    n_matched = sum(1 for v in curve[t]["assigned"].values() if v)
    print(f"\n  UNITS — {n_matched:,} TITLES matched, {n_attr:,} mode ATTRIBUTIONS "
          f"({curve[t]['ambiguous']:,} titles tie across modes); never summed")
    print(f"\n  ⑤ ALL {len(modes)} MODES AT t={t}, INCLUDING ZEROS:")
    for m in sorted(modes, key=lambda x: -counts.get(x, 0)):
        n = counts.get(m, 0)
        print(f"     {n:>5}  {m}")
    unmatched = [n for n, v in curve[t]["assigned"].items() if not v]
    print(f"\n     UNMATCHED: {len(unmatched):,} of {len(titles):,} "
          f"({len(unmatched)/len(titles):.1%}); examples:")
    for n in unmatched[:6]:
        print(f"        {n}  {titles[n][:88]}")

    top3 = sum(sorted(counts.values(), reverse=True)[:3]) / len(titles)  # ATTRIBUTIONS / titles
    world = "B" if not c3 else ("A" if cov >= 0.5 else "C")
    print(f"\n  ⭐⭐⭐ WORLD {world}: " + (
        f"{cov:.3f} of the {len(titles):,} retractions match a §4 mode at t={t}, against a decoy "
        f"floor of [{fl_lo:.3f}, {fl_hi:.3f}], and the top three modes carry {top3:.3f} of all "
        f"entries. **The retractions do instance a small named set, and the taxonomy is external "
        f"to both the ledger and this round's author.**"
        if world == "A" else
        f"coverage {cov:.3f} sits inside the decoy floor [{fl_lo:.3f}, {fl_hi:.3f}]. **The match is "
        f"vocabulary density**, entries cannot be assigned to §4 modes lexically, and R951's World C "
        f"stands: the question needs a read."
        if world == "B" else
        f"coverage is {cov:.3f} — above the decoy floor [{fl_lo:.3f}, {fl_hi:.3f}], so the signal is "
        f"real, but a MINORITY. §4 was written from this programme and describes itself as `a real, "
        f"dated event, not a hypothetical`, yet its 20 modes name only {cov:.0%} of what its own "
        f"source recorded. **That is a finding about the standard, not about the ledger**, and the "
        f"top three modes still carry {top3:.3f} of all entries."))
    print(f"     ⚠ BOUND FROM ABOVE: shared tokens are not shared mechanism. An entry using the word "
          f"`control` is not thereby an instance of a control failure.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "n_titles": len(titles), "n_modes": len(modes),
               "modes": modes,
               "coverage_by_threshold": {str(k): v["coverage"] for k, v in curve.items()},
               "decoy_floor_by_threshold": {str(k): v for k, v in decoy_curve.items()},
               "counts_at_t2": counts, "top3_share": top3,
               "ambiguous_at_t2": curve[2]["ambiguous"],
               "units": {"titles_matched": n_matched, "mode_attributions": n_attr,
                         "note": "a tied title contributes one attribution per tied mode; the two "
                                 "counts are never summed"},
               "n_unmatched_at_t2": len(unmatched),
               "unmatched_examples": {str(n): titles[n] for n in unmatched[:20]},
               "taxonomy_source": str(SKILL),
               "bound": "shared tokens are not shared mechanism; coverage is bounded from ABOVE",
               "unit_note": "counts are LEDGER ENTRIES",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "mode_coverage.json", "w"), indent=2)
    print(f"\n  artifact: results/mode_coverage.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
