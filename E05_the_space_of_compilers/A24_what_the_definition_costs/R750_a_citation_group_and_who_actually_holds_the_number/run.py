#!/usr/bin/env python3
"""R750 · when a sentence cites several rounds, how many of them actually hold the number?

ESTIMAND        for each sentence citing >=2 distinct rounds and stating a number, the SUPPORT
                DEPTH: how many of the cited rounds' own artifacts contain that number.
IDENTIFICATION  identified given a matcher, and the matcher IS the instrument, so three are swept.
                ⚠ R590's documented repair is REUSED: its prefix matcher reported 13 orphans of
                which 9 were its own bug, and rounded matching cut them to 4. R590 has no run.py,
                so the relation is re-implemented with the repair carried forward and the prefix
                rule kept ONLY as the loose end of the curve, to show what it costs.
SCOPE           population = the multi-cited numeric sentences on STATEMENT.md · instrument = three
                matchers · baseline = the SHAM, single-citation numeric sentences (R590's own
                population) · regime = page and committed artifacts at this tree_sha.
WORLDS          A shared support (median >= 2) · B diluted support (median <= 1), in which case
                R749's row-8 failure is an instance of a general property.
KILL            conditional; gated on POSITIVE recovering a known-supported synthetic group, g=0
                returning 0 for a number in no artifact, NEGATIVE changing the distribution, and
                PLACEBO exactly 0.
POSITIVE CTRL   a value two rounds' artifacts PROVABLY contain, found by direct search rather than
                by the matcher, in a fabricated sentence citing exactly those two. Band computed:
                floor = a never-matching matcher (0), ceiling = the group size (2).
g=0             a number in NO artifact -> support 0 AND reported. A skipped zero would raise the
                median by removing the worst cases.
NEGATIVE CTRL   rotate the sentence -> citation-group map; the distribution must change. Excludes
                "support is a property of the NUMBER rather than of the cited rounds".
SHAM            ingredient ABSENT: single-citation numeric sentences. Without this base rate a low
                support depth could simply mean artifacts do not store printed values at all.
PLACEBO         the same sentence scored twice -> exactly 0 difference, 0 of N.
NOISE FLOOR     no rng. The variance is the MATCHER: prefix / rounded / tolerance.
MULTIPLICITY    3 matchers x 2 populations x {median, share>=2, share==0} = 18 reported, plus the
                README-vs-artifact confound split.
UNIT            instrument unit = (sentence, number, round); claim unit = sentence. Support is per
                NUMBER, the per-sentence value is the MAXIMUM, and multi-number sentences are
                counted rather than averaged away.
ARTIFACT        results/r750.json with tree_sha; a later round attacks this by adding a matcher, or
                by resolving support from a round's README where the artifact is silent.
REPRODUCIBILITY two hash seeds byte-identical, both writes confirmed.
IMPOSSIBLE      whether a citation SHOULD support its number (needs an editorial standard) · values
                computed but never persisted (needs re-running rounds, which would overwrite
                committed artifacts -- deferred with the reason) · generalising beyond this page ·
                independently replicated.

⛔ DERIVATIONS, LABELLED, NOT EVIDENCE:
   support <= group size ALWAYS. "Support is less than the citation count" is not a finding; only
   the DISTRIBUTION is. And the SHAM's population is DISJOINT from the main one by construction,
   so no sentence is its own comparator.
"""
from __future__ import annotations
import json, os, pathlib, re, statistics, subprocess

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
A24 = HERE.parent
STM = ROOT / "E05_the_space_of_compilers" / "STATEMENT.md"

NUM = re.compile(r"\*\*([-+]?\d[\d,]*\.?\d*)\*\*|(?<![\w.])(\d+\.\d{3,})(?![\w.])")


def _plain(o):
    for cast in (bool, int, float):
        if isinstance(o, cast) or type(o).__name__ == cast.__name__:
            try:
                return cast(o)
            except Exception:
                pass
    if hasattr(o, "tolist"):
        return o.tolist()
    return str(o)


def numbers_in(s):
    out = []
    for m in NUM.finditer(s):
        v = (m.group(1) or m.group(2)).replace(",", "")
        try:
            float(v)
        except ValueError:
            continue
        out.append(v)
    return sorted(set(out))


def blob_of(rid, which="artifact"):
    for d in sorted(A24.glob(f"R{rid:03d}_*")):
        if which == "artifact":
            return "".join(f.read_text() for f in sorted((d / "results").glob("*.json"))) \
                if (d / "results").exists() else ""
        p = d / "README.md"
        return p.read_text() if p.exists() else ""
    return None


# ---- the three matchers. `prefix` is R590's BROKEN rule, kept to show what it costs.
def m_prefix(val, blob):
    return bool(re.search(rf"(?<![\d.]){re.escape(val)}", blob))


def m_rounded(val, blob):
    """R590's repair: the document rounds, the artifact stores full floats."""
    if m_prefix(val, blob):
        return True
    if "." not in val:
        return bool(re.search(rf"(?<![\d.]){re.escape(val)}\.0*(?![1-9])", blob))
    dp = len(val.split(".")[1])
    try:
        target = float(val)
    except ValueError:
        return False
    for m in re.finditer(r"[-+]?\d+\.\d+", blob):
        try:
            if round(float(m.group()), dp) == target:
                return True
        except ValueError:
            continue
    return False


def m_tolerance(val, blob):
    if m_rounded(val, blob):
        return True
    try:
        target = float(val)
    except ValueError:
        return False
    tol = max(abs(target) * 1e-4, 1e-9)
    for m in re.finditer(r"[-+]?\d+\.?\d*", blob):
        try:
            if abs(float(m.group()) - target) <= tol:
                return True
        except ValueError:
            continue
    return False


MATCHERS = [("prefix (R590's broken rule)", m_prefix), ("rounded (its repair)", m_rounded),
            ("tolerance", m_tolerance)]


def main() -> int:
    if not STM.exists():
        print("UNRUNNABLE: STATEMENT.md absent. Exit 2, never 0."); return 2
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n", STM.read_text()) if s.strip()]
    multi, single = [], []
    for s in sents:
        rr = sorted({int(x) for x in re.findall(r"R(\d{3})", s)})
        ns = numbers_in(s)
        if not ns:
            continue
        (multi if len(rr) >= 2 else single if len(rr) == 1 else []).append((s, rr, ns))
    print("R750 · when a sentence cites several rounds, how many of them hold the number?\n")
    print(f"population: {len(sents)} sentences · multi-cited numeric {len(multi)} · "
          f"single-cited numeric {len(single)} (the SHAM base rate)")
    print(f"  ⛔ the two populations are DISJOINT by construction -- no sentence is its own "
          f"comparator.")
    if not multi or not single:
        print("UNRUNNABLE: a population is empty. Exit 2, never 0."); return 2

    BLOB = {}

    def blob(rid, which="artifact"):
        if (rid, which) not in BLOB:
            BLOB[(rid, which)] = blob_of(rid, which) or ""
        return BLOB[(rid, which)]

    def support(rr, ns, match, which="artifact", rotate=0):
        """per NUMBER; the sentence's value is the MAXIMUM over its numbers."""
        best, per = 0, {}
        R = rr[rotate:] + rr[:rotate] if rotate else rr
        for n in ns:
            k = sum(1 for rid in R if match(n, blob(rid, which)))
            per[n] = k
            best = max(best, k)
        return best, per

    # ---- POSITIVE : a value two artifacts PROVABLY contain, found without the matcher
    pos_pair, pos_val = None, None
    cand = sorted({int(x) for s, rr, _ in multi for x in rr})[:40]
    for a in cand:
        for b in cand:
            if a >= b:
                continue
            ba, bb = blob(a), blob(b)
            for m in re.finditer(r"[-+]?\d+\.\d{4}", ba):
                v = m.group()
                if v in bb:
                    pos_pair, pos_val = (a, b), v
                    break
            if pos_pair:
                break
        if pos_pair:
            break
    if pos_pair:
        got, _ = support(list(pos_pair), [pos_val], m_rounded)
        floor, _ = support(list(pos_pair), [pos_val], lambda v, b: False)
        POSITIVE = (got == 2 and floor == 0)
        print(f"\nPOSITIVE  value {pos_val} found by DIRECT SEARCH in both R{pos_pair[0]} and "
              f"R{pos_pair[1]}. Band computed: never-matching floor {floor}, group size 2, "
              f"measured {got}   {'PASS' if POSITIVE else 'FAIL'}")
    else:
        POSITIVE = False
        print("\nPOSITIVE  FAIL -- no value provably shared by two cited artifacts; the control "
              "cannot be built and the round is UNVERIFIED, not clean")

    # ---- g=0 : a number in no artifact
    g0v = "987654.321"
    g0, _ = support([int(x) for x in cand[:3]], [g0v], m_rounded)
    G0 = (g0 == 0)
    print(f"g=0       a number in no artifact -> support {g0}, REPORTED not skipped  "
          f"{'PASS' if G0 else 'FAIL -- a skipped zero would raise the median'}")

    # ---- the grid : 3 matchers x 2 populations
    grid, per_sentence = {}, {}
    for mn, mf in MATCHERS:
        for pn, P in (("multi-cited", multi), ("single-cited (SHAM)", single)):
            vals = []
            for s, rr, ns in P:
                k, per = support(rr, ns, mf)
                vals.append(k)
                if pn == "multi-cited" and mn.startswith("rounded"):
                    per_sentence[s[:150]] = {"cites": rr, "numbers": ns, "support": k,
                                             "per_number": per}
            grid[f"{mn}|{pn}"] = {
                "n": len(vals), "median": statistics.median(vals) if vals else None,
                "share_ge2": sum(1 for v in vals if v >= 2) / len(vals) if vals else None,
                "share_0": sum(1 for v in vals if v == 0) / len(vals) if vals else None}
    print(f"\n  {'matcher':<28}{'population':<22}{'n':>4}{'median':>8}{'share>=2':>10}"
          f"{'share=0':>9}")
    for mn, _ in MATCHERS:
        for pn in ("multi-cited", "single-cited (SHAM)"):
            g = grid[f"{mn}|{pn}"]
            print(f"  {mn:<28}{pn:<22}{g['n']:>4}{g['median']:>8.1f}"
                  f"{g['share_ge2']:>10.4f}{g['share_0']:>9.4f}")
    print("  ⛔ support <= group size ALWAYS -- only the DISTRIBUTION is a measurement.")
    print("  ⛔ the SHAM's share>=2 is STRUCTURALLY 0 -- a single-citation sentence cannot have "
          "support 2. Its informative column is share=0, not share>=2.")

    P1 = grid["rounded (its repair)|multi-cited"]["median"]
    P2 = grid["rounded (its repair)|multi-cited"]["share_ge2"]
    P3 = 1.0 - grid["rounded (its repair)|single-cited (SHAM)"]["share_0"]
    P4 = int(round(grid["rounded (its repair)|multi-cited"]["share_0"] * len(multi)))
    orphan_prefix = int(round(grid["prefix (R590's broken rule)|multi-cited"]["share_0"] * len(multi)))
    P5 = orphan_prefix - P4
    print(f"\nP1        median support depth, ROUNDED: {P1}  (registered 1, band [0,3])")
    print(f"P2        share of groups with support >=2: {P2:.4f}  (registered 0.35)")
    print(f"P3        SHAM base rate, single-citation support >=1: {P3:.4f}  "
          f"(registered 0.79 ⚠ PRIOR-ART INFORMED from R590's 15/19 = 0.789, declared)")
    print(f"P4        groups with support EXACTLY 0: {P4} of {len(multi)}  (registered 2)")
    print(f"P5        orphans the BROKEN prefix rule manufactures over the repaired one: "
          f"{orphan_prefix} - {P4} = {P5}  (registered >=1)")

    # ---- DIRECTIONAL : does support grow with group size?
    bysize = {}
    for s, rr, ns in multi:
        k, _ = support(rr, ns, m_rounded)
        bysize.setdefault(len(rr), []).append(k)
    print(f"\nDIRECTIONAL support by citation-group size:")
    for sz in sorted(bysize):
        print(f"            size {sz}: n={len(bysize[sz]):<3} mean support "
              f"{statistics.mean(bysize[sz]):.2f}")
    # ⛔ A MEAN OVER n=1 IS NOT A TREND. Sizes with fewer than 3 sentences are printed and
    #    EXCLUDED from the directional, because comparing a one-observation cell against a
    #    twelve-observation one is reading a single sentence as a slope.
    sizes = sorted(bysize)
    usable = [z for z in sizes if len(bysize[z]) >= 3]
    thin = [z for z in sizes if len(bysize[z]) < 3]
    if len(usable) >= 2:
        D = not (statistics.mean(bysize[usable[-1]]) > statistics.mean(bysize[usable[0]]) + 1.0)
        print(f"            usable sizes (n>=3): {usable}; support does NOT grow: {D}")
    else:
        D = None
        print(f"            UNDERPOWERED: usable sizes (n>=3) = {usable}, so the directional is "
              f"UNCOMPUTED rather than answered.")
    print(f"            ⚠ sizes {thin} carry ONE SENTENCE EACH and are excluded from the test, "
          f"not from the table.")

    # ---- CONFOUND : the number may live in the README, not the artifact
    readme_sup = []
    for s, rr, ns in multi:
        k, _ = support(rr, ns, m_rounded, which="readme")
        readme_sup.append(k)
    print(f"\nCONFOUND  the same check against each round's README: median "
          f"{statistics.median(readme_sup):.1f}, share>=2 "
          f"{sum(1 for v in readme_sup if v>=2)/len(readme_sup):.4f} -- reported BESIDE the "
          f"artifact figure, never merged")

    # ---- NEGATIVE : reassign each sentence a DIFFERENT sentence's citation group
    #
    # ⛔ REPAIRED AFTER ITS FIRST RUN, AND THE REPAIR IS A CONTROL THAT COULD NOT FAIL.
    #    v1 rotated the group WITHIN a sentence -- `rr[1:] + rr[:1]` -- and reported 0/17 changed.
    #    Of course: support SUMS over every member, so rotation permutes a set being summed and the
    #    count is invariant BY CONSTRUCTION. The control was mathematically incapable of returning
    #    anything but "no change", so it could never exclude the world it named. That is §4's
    #    control-that-cannot-PASS in its mirror form, and it is mine.
    #    (R749's rotation WAS valid because its resolver reads exactly ONE citation, so order is
    #    load-bearing there and is not here -- the same operation is a control in one round and a
    #    no-op in the next, which is why a control must be re-derived per design.)
    #    The structure to destroy is the SENTENCE-to-GROUP pairing, so each sentence is given the
    #    NEXT sentence's group, deterministically.
    base = [support(rr, ns, m_rounded)[0] for s, rr, ns in multi]
    shifted = [support(multi[(i + 1) % len(multi)][1], ns, m_rounded)[0]
               for i, (s, rr, ns) in enumerate(multi)]
    NEGATIVE = (shifted != base)
    print(f"NEGATIVE  each sentence given ANOTHER sentence's citation group: "
          f"{sum(1 for a,b in zip(shifted,base) if a!=b)}/{len(base)} supports change  "
          f"{'PASS' if NEGATIVE else 'FAIL -- support is a property of the NUMBER, not the rounds'}")

    # ---- PLACEBO
    again = [support(rr, ns, m_rounded)[0] for s, rr, ns in multi]
    PLACEBO = (again == base)
    print(f"PLACEBO   scored twice: {sum(1 for a,b in zip(again,base) if a!=b)} differing, "
          f"0 of {len(base)}  {'PASS' if PLACEBO else 'FAIL'}")

    multi_number = sum(1 for _, _, ns in multi if len(ns) > 1)
    print(f"UNIT      sentences stating >1 number: {multi_number} of {len(multi)} -- support is per "
          f"NUMBER and the sentence value is the MAXIMUM, printed rather than averaged away")

    # ---- VERDICT : computed, referencing every declared control
    controls = {"POSITIVE": POSITIVE, "g0": G0, "NEGATIVE": NEGATIVE, "PLACEBO": PLACEBO}
    if not all(controls.values()):
        world, why = "UNVERIFIED", "a control did not fire"
    elif P1 >= 2:
        world, why = "A", ("citation groups are genuine joint grounding; row 8 is one bad row "
                           "rather than an instance")
    else:
        world, why = "B", ("the group does not ground the number -- the page must name WHICH "
                           "citation computed each figure")
    print(f"\ncontrols  {sum(controls.values())} PASS, "
          f"{len(controls)-sum(controls.values())} FAIL  {controls}")
    print(f"WORLD {world} -- {why}")

    sha = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT,
                         capture_output=True, text=True).stdout.strip()
    out = {"round": "R750", "world": world, "why": why, "tree_sha": sha,
           "hashseed": os.environ.get("PYTHONHASHSEED"),
           "n_multi": len(multi), "n_single": len(single), "grid": grid,
           "P1_median_support": P1, "P2_share_ge2": P2, "P3_sham_base_rate": P3,
           "P4_support_zero": P4, "P5_prefix_manufactured_orphans": P5,
           "by_group_size": {str(k): {"n": len(v), "mean": statistics.mean(v)}
                             for k, v in sorted(bysize.items())},
           "directional_no_growth_with_size": D, "directional_underpowered": D is None,
           "thin_group_sizes_excluded": thin,
           "sham_share_ge2_is_structurally_zero": True,
           "readme_median": statistics.median(readme_sup),
           "multi_number_sentences": multi_number,
           "positive_detail": {"pair": list(pos_pair) if pos_pair else None, "value": pos_val},
           "per_sentence": per_sentence, "controls": controls,
           "support_le_group_size_is_a_derivation": True}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "r750.json").write_text(json.dumps(out, indent=2, sort_keys=True,
                                                          default=_plain))
    print(f"\nwrote results/r750.json  tree {sha[:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
