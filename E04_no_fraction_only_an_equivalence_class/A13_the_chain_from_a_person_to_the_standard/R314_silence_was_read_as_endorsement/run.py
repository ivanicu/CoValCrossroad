"""R314 — R150 wrote the reason it was wrong in the docstring of the function that was wrong.

`assurance/consistency.py` has been exiting 1 with this FAIL on every run:

    full-rejection rate: r150 distribution vs r151 direct count
      0.0105 vs 0.03895   |diff| 0.02845   tol 0.003
      "the same quantity computed in two rounds from the same field; they should agree to
       rounding and a larger gap means one of them filtered silently"

The explanation is wrong and so is the check. Neither round filtered silently: 0.0105 x 18562 =
194.9 and r151 reports 195 full rejections. **Same numerator, two denominators.** The check
compares two rates as though they shared a population — `realstat · name the estimand before the
bound`, where the same 0 errors was 2.34% or 24.71% by sampling unit.

⛔ AND THE DEFECT IS NOT A TIE. R150's own `parse_unacceptable` docstring reads:

    "an empty set because the person said nothing is unacceptable is a JUDGEMENT; a missing
     block is a MISSING ANSWER, and collapsing them would turn silence into an endorsement"

and the line under it is `if blk is None: return set(), False`. In this release **not-asked is an
empty LIST, never a missing key**, so that branch never fires. R150 stated the distinction
precisely and then implemented a test that cannot detect it. R151 found this ("13,672 never-posed
questions were being counted as answered-zero") and corrected its own population — but nobody
carried the correction back, so R150's artifact still holds the pre-correction numbers and the
consistency check now demands that a claim agree with its own retraction, naming the CORRECTED
round as the suspect. A future reader following that message would repair the correction back
into the bug.

Measured directly from `data/annotators.jsonl`:
    18,678 assessments · 13,672 with `unacceptable == []` (never posed) · 5,006 asked ·
    0 with the key absent — so `blk is None` fires exactly zero times.
    All 195 full rejections lie inside the asked set, necessarily.
R150's own header says 18,562, which is 116 short of the file: a third, separate discrepancy.

ESTIMAND      R150's four published quantities recomputed over the ASKED population:
              (a) the veto-count distribution, (b) `served_delta` = the service rate under a
              veto-respecting chooser minus under plurality, (c) `change_rate`, (d) `coverage`.
              The estimand is the CHANGE each undergoes, with R150's number as the comparison.
IDENTIFICATION exact for (a) and (d). For (b) and (c) the correction also shrinks the testable
              set, because R150's gate `len(vv) >= 3` counted never-asked rows toward the
              three, so the corrected estimate is over FEWER prompts and its own CI must be
              recomputed rather than inherited. Where the corrected testable set is too small
              the answer is a bound, not a point.
SCOPE         population CoVal annotators.jsonl assessments · instrument none, human veto
              blocks and rankings only · baseline plurality chooser · regime prompts with >=6
              rankings and >=3 ASKED veto responses.
WORLDS        W-DILUTION  the 13,672 never-asked rows act as consent, diluting the veto signal.
                          Prediction: |served_delta| and change_rate GROW under correction.
              W-INERT     they are spread so per-prompt winners barely move. Prediction: both
                          essentially unchanged, and R150's headline survives its own defect.
              W-REVERSAL  correction flips the sign of served_delta -> R150's headline was an
                          artifact of the defect, not merely diluted by it.
              W-UNIDENT   the corrected testable set is too small to estimate at all -> the
                          claim is withdrawn rather than corrected, and that is the finding.
KILL          conditional on the positive control below:
                corrected CI excludes 0 and |delta| > R150's |delta|      -> W-DILUTION
                corrected CI excludes 0 and sign flips                    -> W-REVERSAL
                corrected CI includes 0 while R150's excluded it          -> W-UNIDENT
                corrected |delta| within 20% of R150's, CI excluding 0    -> W-INERT
POSITIVE CTRL THE DECISIVE ONE, and it has an exact published target. Run this round's own
              pipeline with the DEFECT RE-INJECTED (`blk is None`) and require it to reproduce
              R150's committed artifact: coverage 1.0, testable 1091, change_rate 0.0614,
              served_delta -0.01557. If it does, the reimplementation is faithful and every
              difference below is the POPULATION, not my code. If it does not, this round is
              measuring its own bug and returns UNVERIFIED. Fails at g=0 in the sense that
              running it CORRECTED must NOT reproduce those numbers.
NEGATIVE CTRL permute the RESPONSE LABELS within a prompt, one permutation shared by everyone
              in it: veto counts keep their shape, panel size and per-person veto counts are
              preserved, and only the correspondence to the rankings is destroyed.
              ⚠ THIS IS THE THIRD VERSION AND THE FIRST TWO ARE IN THE RECORD BECAUSE THEY
              FAILED IN OPPOSITE DIRECTIONS. ① permuting WHICH PERSON held each veto set is a
              NO-OP -- the statistic reads per-response veto COUNTS, invariant to relabelling
              people -- and it returned the observed value at sd exactly 0.00000 while printing
              "INSIDE the permutation floor", a FALSE RETRACTION of a live result. ② the
              criterion `|observed| > |permuted| + 1.96 sd` presupposes a null near ZERO; this
              null sits at -0.276, because a label-permuted chooser picks LOW-ranked responses
              by construction. A one-sided operator aimed at the wrong tail reported FAIL on a
              result the same numbers decisively separate. The live version is a two-sided test
              against the measured envelope.
PLACEBO       plurality chooser against itself: served_delta must be exactly 0.
NOISE FLOOR   the permutation spread of served_delta, measured over seeds, not assumed.
MULTIPLICITY  4 quantities x 2 populations = 8 cells, all reported.
SEEDS         200 for the negative control (the label said 20 for one run while the loop ran
              200 -- a stale string, corrected; a number in a print is an assertion too).
ARTIFACT      results/silence.json with source hash.
IMPOSSIBLE    knowing WHY the question was not posed — the release carries no field for it. If
              it was withheld non-randomly (e.g. only for prompts already flagged) the asked
              population is itself selected, and this round corrects the arithmetic without
              being able to correct that. Named, not planned.
"""
import hashlib, json, math, pathlib, sys
from collections import Counter, defaultdict
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
RANK_MAP = {"A": 0, "B": 1, "C": 2, "D": 3}
R150 = (SELF.parent.parent / "R150_does_the_veto_do_anything" / "results" / "veto.json")
TARGET = dict(coverage=1.0, testable_prompts=1091, change_rate=0.0614, served_delta=-0.01557)


def parse_ranking(txt):
    v = np.full(4, np.nan)
    groups = [g.strip() for g in txt.replace(" ", "").split(">") if g.strip()]
    if not groups:
        return None
    for gi, g in enumerate(groups):
        for letter in g.split("="):
            if letter in RANK_MAP:
                v[RANK_MAP[letter]] = -gi
    return v if not np.isnan(v).all() else None


def unacceptable(blocks, buggy):
    """buggy=True reproduces R150 exactly: `blk is None`, which never fires in this release."""
    blk = blocks.get("unacceptable")
    if buggy:
        if blk is None:
            return set(), False
    else:
        if not (blk or blocks.get("personal")):
            return set(), False
    out = set()
    for b in blk or []:
        for r in b.get("rating", []) or []:
            s = r.strip()
            for letter, idx in RANK_MAP.items():
                if s.startswith(letter):
                    out.add(idx)
    return out, True


def load(buggy):
    rank, veto = defaultdict(dict), defaultdict(dict)
    n_ass = n_asked = 0
    with (ROOT / "data" / "annotators.jsonl").open() as fh:
        for line in fh:
            rec = json.loads(line)
            aid = rec["annotator_id"]
            for a in rec.get("assessments", []):
                blocks = a.get("ranking_blocks") or {}
                cid = a["conversation_id"]
                n_ass += 1
                for key in ("world", "personal"):
                    got = False
                    for b in blocks.get(key, []) or []:
                        v = parse_ranking(b.get("ranking") or "")
                        if v is not None:
                            rank[cid][aid] = v; got = True; break
                    if got:
                        break
                u, has = unacceptable(blocks, buggy)
                if has:
                    n_asked += 1
                    veto[cid][aid] = u
    return rank, veto, n_ass, n_asked


def measure(rank, veto, shuffle_seed=None, placebo=False):
    same = diff = testable = 0
    sp_l, sv_l = [], []
    dist = Counter()
    rng = np.random.default_rng(shuffle_seed) if shuffle_seed is not None else None
    for cid, per in rank.items():
        vv = dict(veto.get(cid, {}))
        if rng is not None and vv:
            # NEGATIVE CONTROL, SECOND VERSION. The first permuted WHICH ANNOTATOR held which
            # veto set — and that is a NO-OP by construction, because the statistic reads
            # `vcount[r] = how many people vetoed r`, which is invariant to relabelling the
            # people. It returned the observed value with sd exactly 0.00000 across 5 seeds and
            # printed "INSIDE the permutation floor", i.e. a FALSE RETRACTION of a live result.
            # Kept in the record because the sd of exactly zero is the diagnostic tell.
            # What the statistic actually uses is the ALIGNMENT between the responses people
            # veto and the responses they rank highly. So permute the RESPONSE LABELS within
            # the prompt, one permutation shared by everyone in it: veto counts keep their
            # shape, panel size and per-person veto counts are preserved, and only the
            # correspondence to the rankings is destroyed.
            pi = rng.permutation(4)
            vv = {a: {int(pi[i]) for i in u} for a, u in vv.items()}
        for u in vv.values():
            dist[len(u)] += 1
        if len(per) < 6 or len(vv) < 3:
            continue
        tops = {a: set(np.nonzero(x >= np.nanmax(x) - 1e-9)[0].tolist()) for a, x in per.items()}
        counts_top = [sum(1 for t in tops.values() if r in t) for r in range(4)]
        plur = int(np.argmax(counts_top))
        vcount = [sum(1 for u in vv.values() if r in u) for r in range(4)]
        best = min(vcount)
        cand = [r for r in range(4) if vcount[r] == best]
        vch = plur if placebo else max(cand, key=lambda r: counts_top[r])
        testable += 1
        same, diff = (same + 1, diff) if vch == plur else (same, diff + 1)
        sp_l.append(np.mean([1 if plur in t else 0 for t in tops.values()]))
        sv_l.append(np.mean([1 if vch in t else 0 for t in tops.values()]))
    if not testable:
        return dict(testable=0)
    sp, sv = float(np.mean(sp_l)), float(np.mean(sv_l))
    d = np.array(sv_l) - np.array(sp_l)
    se = float(d.std(ddof=1) / math.sqrt(len(d))) if len(d) > 1 else float("nan")
    tot = sum(dist.values())
    return dict(testable=testable, change_rate=diff / testable, served_plurality=sp,
                served_veto=sv, served_delta=sv - sp,
                ci=[sv - sp - 1.96 * se, sv - sp + 1.96 * se], se=se,
                dist={k: dist[k] / tot for k in range(5)}, n_veto_rows=tot)


def main():
    if not R150.exists():
        print(f"  UNRUNNABLE: {R150.relative_to(ROOT)} absent."); return 2
    pub = json.loads(R150.read_text())

    # ---- POSITIVE CONTROL · re-inject the defect, require R150's published numbers ------------
    rk_b, vt_b, n_ass, n_ask_b = load(buggy=True)
    bug = measure(rk_b, vt_b)
    print(f"  POSITIVE CONTROL — this round's pipeline with R150's defect RE-INJECTED,")
    print(f"  scored against R150's COMMITTED artifact, not against my expectation.\n")
    print(f"    {'quantity':<20}{'R150 published':>16}{'reproduced':>13}{'':>4}")
    hits = []
    for k, want in (("coverage", TARGET["coverage"]), ("testable_prompts", TARGET["testable_prompts"]),
                    ("change_rate", TARGET["change_rate"]), ("served_delta", TARGET["served_delta"])):
        got = {"coverage": n_ask_b / n_ass, "testable_prompts": bug["testable"],
               "change_rate": bug["change_rate"], "served_delta": bug["served_delta"]}[k]
        tol = 2 if k == "testable_prompts" else 0.0006
        ok = abs(got - want) <= tol
        hits.append(ok)
        print(f"    {k:<20}{want:>16.5f}{got:>13.5f}{'  ok' if ok else '  MISMATCH':>6}")
    pos_ok = all(hits)
    print(f"    -> reimplementation is {'FAITHFUL' if pos_ok else 'NOT faithful'}; every "
          f"difference below is {'the POPULATION' if pos_ok else 'UNREADABLE'}")

    # ---- the corrected population -------------------------------------------------------------
    rk, vt, _, n_ask = load(buggy=False)
    cor = measure(rk, vt)
    g0_ok = abs(cor["served_delta"] - TARGET["served_delta"]) > 0.0006
    print(f"\n  POPULATION   {n_ass} assessments · asked {n_ask} ({n_ask/n_ass:.1%}) · "
          f"never posed {n_ass - n_ask}")
    print(f"               R150's header says 18562 assessments — {n_ass - 18562} short of the file.")
    print(f"    g=0 check: corrected run does NOT reproduce the buggy served_delta: {g0_ok}")

    print(f"\n  {'quantity':<24}{'R150 (all rows)':>18}{'corrected (asked)':>20}{'change':>12}")
    rows = [("veto-count P(0)", bug["dist"][0], cor["dist"][0]),
            ("veto-count P(4)", bug["dist"][4], cor["dist"][4]),
            ("coverage", n_ask_b / n_ass, n_ask / n_ass),
            ("testable prompts", bug["testable"], cor["testable"]),
            ("change rate", bug["change_rate"], cor["change_rate"]),
            ("served_delta", bug["served_delta"], cor["served_delta"])]
    for nm, a, b in rows:
        ch = f"{b - a:+.4f}" if abs(a) < 100 else f"{b - a:+.0f}"
        print(f"    {nm:<22}{a:>18.4f}{b:>20.4f}{ch:>12}")
    pub_ci = pub["served_delta_ci95"]
    ci_pub = "[{:+.5f}, {:+.5f}]".format(pub_ci[0], pub_ci[1])
    ci_cor = "[{:+.5f}, {:+.5f}]".format(cor["ci"][0], cor["ci"][1])
    print(f"    {'served_delta CI95':<22}{ci_pub:>18}{ci_cor:>20}")

    # ---- PLACEBO ------------------------------------------------------------------------------
    plc = measure(rk, vt, placebo=True)["served_delta"]
    print(f"\n  PLACEBO   plurality chooser against itself: {plc:+.2e}  "
          f"{'PASS' if abs(plc) < 1e-12 else 'FAIL'}")

    # ---- NEGATIVE CONTROL ---------------------------------------------------------------------
    perm = [measure(rk, vt, shuffle_seed=s)["served_delta"] for s in range(200)]
    pm, ps = float(np.mean(perm)), float(np.std(perm))
    plo, phi = float(np.percentile(perm, 2.5)), float(np.percentile(perm, 97.5))
    # THE CRITERION WAS WRONG TOO, and in a way worth recording. I first wrote
    #     neg_ok = abs(observed) > abs(permuted) + 1.96*sd
    # which presupposes the null sits near ZERO. It does not: with the response labels
    # permuted the veto-respecting chooser picks responses people rank LOW, so the null
    # predicts a LARGE negative served_delta (-0.280), not a small one. The observed -0.053 is
    # outside that envelope on the OTHER side. A one-sided operator aimed at the wrong tail
    # reported FAIL on a result the same numbers decisively separate.
    # `realstat §4 · the control fails for its own reasons`, form ②.
    neg_ok = not (plo <= cor["served_delta"] <= phi)
    print(f"  NEGATIVE  permute the RESPONSE LABELS within prompt, 200 seeds: {pm:+.5f} ± {ps:.5f}")
    print(f"            (the first version permuted WHICH PERSON held each veto set and was a")
    print(f"             NO-OP: sd exactly 0.00000, printing a false retraction. See run.py.)")
    print(f"            envelope [{plo:+.5f}, {phi:+.5f}] — this null is NOT near zero: with the")
    print(f"            labels permuted the chooser picks LOW-ranked responses by construction.")
    print(f"            corrected {cor['served_delta']:+.5f} -> "
          f"{'OUTSIDE the envelope' if neg_ok else 'INSIDE the envelope'}"
          f"{', and on the LESS-HARM side: vetoes land on responses people already rank low' if neg_ok and cor['served_delta'] > phi else ''}")

    # ---- KILL ---------------------------------------------------------------------------------
    # neg_ok now GATES. The pre-registration made the kill conditional on the positive control
    # only; tightening it after the first negative control turned out to be a no-op is a
    # post-hoc change and is recorded as one. It can only make the verdict harder to obtain.
    ctrl = pos_ok and g0_ok and abs(plc) < 1e-12 and neg_ok
    excl = not (cor["ci"][0] <= 0 <= cor["ci"][1])
    grew = abs(cor["served_delta"]) > abs(TARGET["served_delta"])
    flip = np.sign(cor["served_delta"]) != np.sign(TARGET["served_delta"])
    print("\n  " + "=" * 78)
    print(f"  CONTROLS  positive={pos_ok}  g0={g0_ok}  placebo={abs(plc) < 1e-12}  "
          f"negative={neg_ok} (GATING, tightened post-hoc)  "
          f"-> {'evaluate' if ctrl else 'UNVERIFIED'}")
    if not ctrl:
        world = "UNVERIFIED"
        print("  -> UNVERIFIED. A control misbehaved; the correction is not readable.")
    elif not excl:
        world = "W-UNIDENT"
        print(f"  -> W-UNIDENT. Corrected served_delta {cor['served_delta']:+.5f} "
              f"[{cor['ci'][0]:+.5f}, {cor['ci'][1]:+.5f}] INCLUDES zero on {cor['testable']}")
        print(f"     testable prompts, where R150 had {bug['testable']} and a CI that excluded it.")
        print("     The claim is WITHDRAWN, not corrected: once silence stops counting as")
        print("     endorsement the release cannot say whether respecting vetoes costs service.")
    elif flip:
        world = "W-REVERSAL"
        print(f"  -> W-REVERSAL. The sign flips: {TARGET['served_delta']:+.5f} -> "
              f"{cor['served_delta']:+.5f}. R150's headline was produced BY the defect.")
    elif grew:
        world = "W-DILUTION"
        print(f"  -> W-DILUTION. |served_delta| grows {abs(TARGET['served_delta']):.5f} -> "
              f"{abs(cor['served_delta']):.5f}. The 13,672 never-posed rows were acting as")
        print("     consent and diluting the veto signal; R150 UNDERSTATED the cost.")
    else:
        world = "W-INERT"
        print(f"  -> W-INERT. {cor['served_delta']:+.5f} vs {TARGET['served_delta']:+.5f}: the")
        print("     never-posed rows are spread so per-prompt winners barely move. R150's")
        print("     headline survives its own defect — which is luck, not method.")
    print("  " + "=" * 78)
    print(f"\n  ⚠ SEPARATELY, AND IT HOLDS WHATEVER THE VERDICT: the DISTRIBUTION numbers are")
    print(f"    wrong by construction. P(veto nothing) {bug['dist'][0]:.4f} -> {cor['dist'][0]:.4f}")
    print(f"    and P(reject all four) {bug['dist'][4]:.4f} -> {cor['dist'][4]:.4f}. Any sentence")
    print(f"    of the form 'N% of people vetoed nothing' is a statement about how often the")
    print(f"    QUESTION WAS ASKED, not about what people judged.")
    print(f"\n  MULTIPLICITY  8 cells (4 quantities x 2 populations), all printed above.")

    o = SELF.parent / "results" / "silence.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(SELF.read_bytes()).hexdigest()[:16], world=world,
        n_assessments=n_ass, n_asked=n_ask, n_never_posed=n_ass - n_ask,
        r150_header_assessments=18562, header_shortfall=n_ass - 18562,
        buggy=bug, corrected=cor, placebo=plc, permutation_mean=pm, permutation_sd=ps,
        permutation_n_seeds=200, permutation_envelope=[plo, phi],
        first_negative_control="permuted WHICH PERSON held each veto set; a NO-OP because the "
                               "statistic reads per-response veto COUNTS, invariant to "
                               "relabelling people. sd exactly 0. Replaced, both reported.",
        positive_ok=bool(pos_ok), g0_ok=bool(g0_ok), negative_ok=bool(neg_ok),
        ci_excludes_zero=bool(excl)), indent=1))
    print(f"\n  artifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
