"""R318 — the site MDE is quoted as [0.1250, 0.1250]. Is that a property of the site, or of a draw?

R317 ended on a decision about the deliverable rather than the instruments: six rounds read
`_archive/r257_first_pass/instruments_retyped_prompt.npz`, which is gitignored and which **no
committed code writes** — six readers, zero writers, checked by grep over every `.py` in the repo.
Five of the six are cited by `FORMULATION.md`, and they carry the campaign's most load-bearing
single number: *"the site's own MDE — what this release could ever have shown"*, `[0.1250, 0.1250]`.

⛔ AND THE OBVIOUS FIX WAS WRONG. R257's committed `results/instruments.npz` is the same size and
holds the same keys, so it looks like the archived file under another name. It is not: the two have
**byte-identical `meta`** — same 45,204 rows, same 250 conversations, same index — and **different
`sat`**. They are TWO INDEPENDENT JUDGINGS OF ONE GRID, which is what an instrument-noise design
needs and is exactly why a first pass was kept. Substituting one for the other does not restore a
missing input; it asks a different question, and asking it is this round.

ESTIMAND      the draw-dependence of `mde_bracket` — the spread of the site MDE across two
              independent judgings of the identical grid — and whether R274's VERDICT survives
              the swap even where its numbers do not.
IDENTIFICATION n = 2 DRAWS. That supports a RANGE and nothing else: no sd, no interval, no
              "±". Reporting a spread of two as a distribution is the failure this campaign
              already has an entry for, and the bound is stated instead.
SCOPE         population the 250 prompts of R274's calibration · instrument Qwen3.5 judgings A
              (archived first pass) and B (R257's committed rerun) · baseline none · regime the
              class-agreement statistic at R274's calibrated threshold.
WORLDS        W-DRAW-STABLE  both draws give the same bracket -> the number is a property of the
                             site and the archived file is merely a convenience.
              W-DRAW-BOUND   the brackets differ -> `[0.1250, 0.1250]` is one draw's answer
                             reported without naming the draw, and the honest form is the range
                             over draws.
              W-VERDICT-MOVES the swap changes which effects clear the MDE -> the arc's
                             conclusion is draw-dependent too, which is far worse than a number
                             moving and would require re-opening every claim downstream.
KILL          conditional on the placebo below:
                brackets identical                              -> W-DRAW-STABLE
                brackets differ, admitted set identical         -> W-DRAW-BOUND
                admitted set differs                            -> W-VERDICT-MOVES
POSITIVE CTRL the two inputs must be two draws of ONE design, or the comparison is between
              different objects and means nothing. Required: `meta` arrays byte-identical and
              `sat` arrays NOT identical. Both are asserted, and the round refuses if either
              fails — identical `sat` would mean I substituted a file for itself, and differing
              `meta` would mean the grids differ and no MDE comparison is licensed.
PLACEBO       re-run R274's committed code on its OWN archived input and require the result to
              equal the COMMITTED ARTIFACT ON DISK, key for key. This is the one that makes the
              rest readable: it establishes that the published artifact came from the published
              code, rather than comparing two fresh runs to each other and calling that
              determinism. 16 of 16 keys, exact.
NEGATIVE CTRL none is available and that is stated rather than improvised: destroying the
              structure under test here means judging the grid a third time, which needs the
              GPU and the pueue queue, and is named in IMPOSSIBLE rather than skipped quietly.
NOISE FLOOR   the two draws ARE the floor, and n=2 is why this round reports a range.
MULTIPLICITY  7 quantities compared across 2 draws; every one printed, movers and non-movers.
SEEDS         R274 is deterministic given its input — established by the placebo, not assumed.
ARTIFACT      results/draw_dependence.json, plus both draws' full artifacts beside it.
IMPOSSIBLE    a third draw, which would turn the range into an estimate and needs a GPU judging
              run through pueue; and knowing WHICH draw the release's own numbers were built
              from, since the archived pass is undated in the repo.
"""
import hashlib, json, pathlib, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
RES = SELF.parent / "results"
A_NPZ = ROOT / "_archive/r257_first_pass/instruments_retyped_prompt.npz"
B_NPZ = (ROOT / "E05_the_space_of_compilers/A23_is_the_admissibility_gate_the_right_gate"
         / "R257_label_order_gauge_propagation" / "results" / "instruments.npz")
PUBLISHED = (ROOT / "E05_the_space_of_compilers/A23_is_the_admissibility_gate_the_right_gate"
             / "R274_the_site_MDE_at_fine_resolution" / "results" / "calibrated_mde.json")
DRAW_A = RES / "draw_A_replay_of_published.json"     # R274 code, archived input
DRAW_B = RES / "draw_B_committed_npz.json"           # R274 code, R257's committed input


def main():
    for p in (PUBLISHED, DRAW_A, DRAW_B):
        if not p.exists():
            print(f"  UNRUNNABLE: {p.name} absent."); return 2
    pub = json.loads(PUBLISHED.read_text())
    A = json.loads(DRAW_A.read_text())
    B = json.loads(DRAW_B.read_text())

    # ---- POSITIVE CONTROL · are these two draws of ONE design? --------------------------------
    print("  POSITIVE CONTROL — the two inputs must be two judgings of the SAME grid")
    if not (A_NPZ.exists() and B_NPZ.exists()):
        print("  UNRUNNABLE: an input npz is absent."); return 2
    za, zb = np.load(A_NPZ, allow_pickle=True), np.load(B_NPZ, allow_pickle=True)
    meta_same = za["meta"].shape == zb["meta"].shape and bool((za["meta"] == zb["meta"]).all())
    sat_diff = not np.array_equal(za["sat"], zb["sat"])
    print(f"    rows {len(za['meta'])} vs {len(zb['meta'])}")
    print(f"    meta byte-identical (same grid)     : {meta_same}   <- required True")
    print(f"    sat differs (two distinct judgings) : {sat_diff}   <- required True")
    print(f"    sha256 A {hashlib.sha256(A_NPZ.read_bytes()).hexdigest()[:16]} · "
          f"B {hashlib.sha256(B_NPZ.read_bytes()).hexdigest()[:16]}")
    pos_ok = meta_same and sat_diff
    if not pos_ok:
        print("  REFUSING: these are not two draws of one design; no MDE comparison is licensed.")
        return 2

    # ---- PLACEBO · does the committed artifact come from the committed code? -------------------
    keys = sorted(set(pub) | set(A))
    replay_diff = [k for k in keys if pub.get(k) != A.get(k)]
    plc_ok = not replay_diff
    print(f"\n  PLACEBO — replay R274 on its OWN input, compare to the artifact ON DISK")
    print(f"    {len(keys) - len(replay_diff)} of {len(keys)} keys identical   "
          f"{'PASS' if plc_ok else 'FAIL: ' + str(replay_diff)}")
    print("    (compared against disk, not against a second fresh run -- two fresh runs agreeing")
    print("     certifies determinism and says nothing about what was committed)")

    # ---- the swap ------------------------------------------------------------------------------
    print(f"\n  THE SWAP — identical grid, second judging\n")
    print(f"    {'quantity':<18}{'draw A (published)':>22}{'draw B':>20}{'moved':>8}")
    moved, watch = [], ("mde_bracket", "tau", "alpha_holdout", "cal_mean", "cal_sd",
                        "shamA", "shamB")
    for k in watch:
        a, b = A.get(k), B.get(k)
        d = a != b
        if d:
            moved.append(k)
        print(f"    {k:<18}{str(a):>22}{str(b):>20}{'YES' if d else '-':>8}")

    br_a, br_b = A.get("mde_bracket"), B.get("mde_bracket")
    lo = sorted({br_a[0], br_b[0]}); hi = sorted({br_a[1], br_b[1]})
    # the ADMITTED SET is what a verdict rests on; extracted from each verdict string rather than
    # re-derived, because re-deriving it would be a second implementation of R274 inside R318.
    # ⚠ THIS EXTRACTOR WAS WRONG AND IT MANUFACTURED THE WORST VERDICT ON THE MENU. The first
    # version took the FIRST bracketed span in the verdict string -- which is the MDE bracket,
    # `[0.1250, 0.1250]`, not the admitted set -- so it "differed" for exactly the reason the
    # round was measuring, and printed W-VERDICT-MOVES: *every claim downstream must be
    # re-opened*. That is `a search is an instrument and has no positive control`, and the cost
    # of shipping it would have been a fabricated crisis. The admitted set is the span that names
    # ROUNDS, so it is the one containing a letter, and the extractor now has a control: it must
    # return a span mentioning a round id, or the round refuses rather than comparing None to
    # None and calling that agreement.
    import re as _re
    def admitted(v):
        spans = _re.findall(r"\[[^\[\]]*\]", v.get("verdict", ""))
        named = [x for x in spans if _re.search(r"[Rr]\d{2,}", x)]
        return named[0] if named else None
    ad_a, ad_b = admitted(A), admitted(B)
    if ad_a is None or ad_b is None:
        print(f"\n  REFUSING: the admitted-set extractor found no round-naming span "
              f"(A={ad_a!r}, B={ad_b!r}). Two Nones comparing equal is not agreement.")
        return 2
    same_admitted = ad_a == ad_b
    print(f"\n    admitted set, draw A: {ad_a}")
    print(f"    admitted set, draw B: {ad_b}")
    print(f"    identical: {same_admitted}")

    # ---- KILL ------------------------------------------------------------------------------------
    ctrl = pos_ok and plc_ok
    print("\n  " + "=" * 78)
    print(f"  CONTROLS  positive={pos_ok}  placebo={plc_ok}  -> "
          f"{'evaluate' if ctrl else 'UNVERIFIED'}")
    if not ctrl:
        world = "UNVERIFIED"
        print("  -> UNVERIFIED. A control misbehaved; the comparison is not readable.")
    elif not same_admitted:
        world = "W-VERDICT-MOVES"
        print("  -> W-VERDICT-MOVES. The swap changes which effects clear the MDE. Every claim")
        print("     downstream of this arc has to be re-opened, because the arc's CONCLUSION and")
        print("     not merely its number depends on which judging was used.")
    elif br_a == br_b:
        world = "W-DRAW-STABLE"
        print(f"  -> W-DRAW-STABLE. Both judgings give {br_a}. The number is a property of the")
        print("     site, and the archived file is a convenience rather than evidence.")
    else:
        world = "W-DRAW-BOUND"
        print(f"  -> W-DRAW-BOUND. The bracket moves {br_a} -> {br_b} across two judgings of the")
        print(f"     IDENTICAL grid, while the admitted set does not move at all.")
        print(f"     ⚠ So `the site MDE is [0.1250, 0.1250]` is ONE DRAW'S ANSWER reported without")
        print(f"       naming the draw -- the scope failure this campaign has retracted for more")
        print(f"       than any other. Over the two draws available the lower bound is in")
        print(f"       {{{', '.join(f'{x:.4f}' for x in lo)}}} and the upper in "
              f"{{{', '.join(f'{x:.4f}' for x in hi)}}}.")
        print(f"     ⚠ AND THE CONCLUSION IS STRONGER THAN IT WAS. R274's verdict, its admitted")
        print(f"       set and its retraction of R268 all survive an INDEPENDENT JUDGING -- which")
        print(f"       is a severity test nobody designed and it passed. The number is what")
        print(f"       weakened; the finding is what held.")
        print(f"     n = 2 DRAWS: this is a RANGE, not an interval. No sd is computable and none")
        print(f"       is reported.")
    print("  " + "=" * 78)
    print(f"\n  MULTIPLICITY  {len(watch)} quantities x 2 draws; {len(moved)} moved: {moved}")

    o = RES / "draw_dependence.json"
    o.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(SELF.read_bytes()).hexdigest()[:16], world=world,
        n_draws=2, meta_identical=bool(meta_same), sat_differs=bool(sat_diff),
        placebo_keys_identical=len(keys) - len(replay_diff), placebo_keys=len(keys),
        placebo_ok=bool(plc_ok), replay_diff=replay_diff,
        bracket_A=br_a, bracket_B=br_b, lower_over_draws=lo, upper_over_draws=hi,
        moved=moved, admitted_A=ad_a, admitted_B=ad_b, admitted_identical=bool(same_admitted),
        sha_A=hashlib.sha256(A_NPZ.read_bytes()).hexdigest()[:16],
        sha_B=hashlib.sha256(B_NPZ.read_bytes()).hexdigest()[:16]), indent=1))
    print(f"\n  artifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
