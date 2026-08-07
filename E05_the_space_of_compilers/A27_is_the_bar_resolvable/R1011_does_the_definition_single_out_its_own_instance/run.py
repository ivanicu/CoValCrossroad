#!/usr/bin/env python3
"""R1011 — inside the definition's own extension, does the released core have any special status?

⛔ WHY NOT R1010's NEXT. It proposed computing, per artifact, "the ratio of readers between the
STRONGEST field and the most-used one". ⭐ **`strongest` is not identified** — deciding which field of
an artifact is strongest is a judgement per artifact, so the quantity cannot be computed without me
supplying the answer it is meant to test. Identification before power: the question as written is not
estimable, and it is withdrawn rather than approximated. (The identified version — the share of
committed fields never read by later code — is a different question and is not this round.)

⭐ AND THREE OF THE LAST FOUR ROUNDS WERE ABOUT THE LOOP. The object-level state after R1009's repair
is: the definition is ②′∧③, its extension is 9 arms and 4 DISTINCT objects (R1005's census) —
`coval_core`, `topw_k3`, `topw_k4` (with two deterministic twins), `topw_k6`, `topw_k8`. So the
definition admits the released core plus a slice of one trivial family. **The question the whole quest
has been circling is whether it SINGLES OUT the instance or merely contains it.**

ESTIMAND        within the extension, the paired A2 difference between `coval_core` and every other
                admitted arm, with its bootstrap interval — and whether any of them is resolvable.
IDENTIFICATION  direct. Both arms are scored on the same 968 prompts against the same annotators; the
                paired difference is the same estimand clause ② already uses, pointed inward.
SCOPE           population : the extension under ②′ (R1009's repair: beats EVERY certified
                             prompt-blind comparator) — 9 arms, deduplicated to 4 distinct
                instrument : A2, per-prompt graded agreement, cluster bootstrap over prompts
                baseline   : each admitted arm in turn · regime : this release, n = 968
WORLDS          A SINGLED OUT       `coval_core` resolvably beats every other admitted arm. The
                                    definition contains the instance AND ranks it first.
                B INDISTINGUISHABLE no admitted arm is resolvably ordered against it. The definition
                                    admits a set in which the instance has no special status — it
                                    contains the core without singling it out.
                C OUTRANKED         some admitted arm resolvably BEATS it. Then the definition admits
                                    something better than the object it was written from, which is
                                    the strongest possible answer to "does it describe the instance".
                prediction matrix: A -> all lo > 0. B -> all intervals straddle 0. C -> some hi < 0.
KILL            pre-registered: if world B or C, the statement must say so beside the formulation in
                THIS round — a definition that cannot rank its own instance is not a finding to defer,
                and it is the reading of "the definition describes the instance" from the other side.
POSITIVE CTRL   `coval_core` against a KNOWN-WORSE arm outside the extension (`random_k4_s0`) must be
                resolvable and positive. If the instrument cannot order the core above a random
                selector, it cannot order anything and every interval below is silence.
NEGATIVE CTRL   `coval_core` against its own deterministic twin `coval_core_2bA` — identical outputs
                (R1005: agreement exactly 1.000) — must give a difference of EXACTLY zero with a
                degenerate interval. A non-zero there means the pairing is broken.
SHAM            `coval_core_sham` — the same construction with the ingredient inverted — must be
                resolvably WORSE. A definition whose instance cannot beat its own sham has no content.
PLACEBO         `coval_core` against itself: identically zero.
NOISE FLOOR     the width of the twin comparison's interval IS the floor — it is the same design with
                a known-zero effect, so it measures what this design returns when there is nothing.
MULTIPLICITY    every admitted arm × 1 reference, all pairs reported, BH over the whole family.
ARTIFACT        results/instance_rank.json with this file's source hash.
IMPOSSIBLE      ⚠ construct validity — N/A throughout: A2 is agreement with the release's own
                annotators. "Better" here means "agrees more", never "is a better core".
                ⚠ cross-release — N/A. One release, one core.
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"
NEW = ROOT / "corebench" / "results_r893_leaky"
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls  # noqa: E402

NBOOT, SEED = 8000, 1011
CORE = "coval_core"
SHAM, WORSE = "coval_core_sham", "random_k4_s0"
# ⛔⛔ THE FIRST NEGATIVE CONTROL FAILED AND THE DIAGNOSIS BECAME A FINDING. It used
# `coval_core_2bA`, which R1005's census reports as agreeing with `coval_core` at EXACTLY 1.000, so
# their A2 difference had to be zero. It came back -0.0033 [-0.0122, +0.0051].
# ⭐ CAUSE, measured: `coval_core_2bA` and `2bB` are scored on **200 of 968 prompts (21%)**, and the
# committed A2 loader fills the missing 768 with the arm's OWN MEAN
# (`np.nan_to_num(v, nan=np.nanmean(v))`, guarded only by `< 200`). R1005's census skipped missing
# prompts, so its 1.000 is a statement about the 200 SHARED prompts; this round's A2 vectors are
# over all 968 with 79% imputed. Two different populations, and the control was right to refuse.
# ⭐⭐ CONSEQUENCE FOR THE EXTENSION: 2 of its 9 arms are those twins. But deduplication removes
# them, and the 4 DISTINCT objects — coval_core, topw_k3, topw_k4, topw_k6, topw_k8 — are all at
# 968/968. So R1004's count of 9 was inflated by duplication AND by imputation; the distinct figure
# is clean. This round therefore runs on FULL-COVERAGE arms only, and says so.
# ⭐ REPLACED negative control: `topw_k4_detA` vs `topw_k4_detB`, a deterministic pair at full
# coverage, so a known-zero effect is tested without imputation anywhere.
TWIN_A, TWIN_B = "topw_k4_detA", "topw_k4_detB"
MIN_COVER = 968


def main() -> int:
    r1000 = next(A27.glob("R1000_*/results/conjunction.json"), None)
    if r1000 is None:
        print("  UNRUNNABLE: R1000's artifact is missing. Exit 2, never 0.")
        return 2
    c = json.loads(r1000.read_text())
    # ⭐ ②′ = R1009's repair: beats EVERY certified prompt-blind comparator = the intersection.
    ext = sorted(set(c["cells"]["generic"]["conjunction"]) &
                 set(c["cells"]["genericpool16"]["conjunction"]))
    print(f"  extension under ②′ (R1009's repair, the intersection): {len(ext)} arms")
    print(f"    {ext}")

    tg, _ = load_targets()
    S0 = load_sat(RES / "sat_genericpool16.npz")
    pids = sorted(set(S0) & {p for p in tg if len(tg[p]) >= 2})
    H = {p: np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids}
    n = len(pids)

    def vec(nm):
        for d in (RES, NEW):
            f = d / f"sat_{nm}.npz"
            if not f.exists():
                continue
            try:
                Sa = load_sat(f)
            except Exception:
                return None
            v = np.full(n, np.nan)
            for k, p in enumerate(pids):
                if p in Sa:
                    cc = np.array(cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]}))), float)
                    v[k] = float(np.mean([(cc == h[:len(cc)]).mean() for h in H[p]]))
            if np.isfinite(v).sum() < 200:
                return None
            return np.nan_to_num(v, nan=np.nanmean(v))
        return None

    # ---------- COVERAGE, measured before anything is compared ----------
    def cover(nm):
        for d in (RES, NEW):
            f = d / f"sat_{nm}.npz"
            if f.exists():
                try:
                    Sa = load_sat(f)
                except Exception:
                    return 0
                return sum(1 for p in pids if p in Sa)
        return 0

    cov = {a: cover(a) for a in sorted(set(ext) | {CORE, TWIN_A, TWIN_B, SHAM, WORSE})}
    print(f"\n  COVERAGE — prompts each arm is actually scored on:")
    for a in sorted(cov, key=lambda x: cov[x]):
        flag = "" if cov[a] >= MIN_COVER else "   ⛔ PARTIAL — its A2 would be imputed"
        print(f"    {a:<24}{cov[a]:>5} / {n}{flag}")
    dropped = [a for a in ext if cov.get(a, 0) < MIN_COVER]
    ext = [a for a in ext if cov.get(a, 0) >= MIN_COVER]
    print(f"  ⭐ dropped from the extension for partial coverage: {dropped}")
    print(f"     remaining, all at {MIN_COVER}/{n}: {ext}")
    want = sorted(set(ext) | {CORE, TWIN_A, TWIN_B, SHAM, WORSE})
    V, names = {}, []
    for a in want:
        v = vec(a)
        if v is not None:
            V[a] = v
            names.append(a)
    if CORE not in V:
        print("  UNRUNNABLE: the instance is not scoreable. Exit 2, never 0.")
        return 2
    rng = np.random.default_rng(SEED)
    idx = rng.integers(0, n, size=(NBOOT, n))

    def paired(a, b):
        d = V[a] - V[b]
        bs = d[idx].mean(axis=1)
        return float(d.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))

    # ---------- controls ----------
    p_m, p_lo, p_hi = paired(CORE, WORSE) if WORSE in V else (np.nan,) * 3
    pos_ok = WORSE in V and p_lo > 0
    have_twins = TWIN_A in V and TWIN_B in V
    t_m, t_lo, t_hi = paired(TWIN_A, TWIN_B) if have_twins else (np.nan,) * 3
    neg_ok = have_twins and abs(t_m) < 1e-12 and abs(t_lo) < 1e-12 and abs(t_hi) < 1e-12
    s_m, s_lo, s_hi = paired(CORE, SHAM) if SHAM in V else (np.nan,) * 3
    sham_ok = SHAM in V and s_lo > 0
    z_m, z_lo, z_hi = paired(CORE, CORE)
    plac_ok = z_m == 0.0 and z_lo == 0.0 and z_hi == 0.0
    print(f"\n  POSITIVE  core vs `{WORSE}`   {p_m:+.4f} [{p_lo:+.4f}, {p_hi:+.4f}] must be "
          f"resolvably positive: {'PASS' if pos_ok else '⛔ FAIL'}")
    print(f"  NEGATIVE  `{TWIN_A}` vs `{TWIN_B}` (deterministic pair, BOTH at full coverage) "
          f"{t_m:+.4f} [{t_lo:+.4f}, {t_hi:+.4f}] must be EXACTLY zero: "
          f"{'PASS' if neg_ok else '⛔ FAIL'}")
    print(f"  SHAM      core vs `{SHAM}`  {s_m:+.4f} [{s_lo:+.4f}, {s_hi:+.4f}] must be "
          f"resolvably positive: {'PASS' if sham_ok else '⛔ FAIL'}")
    print(f"  PLACEBO   core vs itself     {z_m:+.4f} [{z_lo:+.4f}, {z_hi:+.4f}] must be zero: "
          f"{'PASS' if plac_ok else '⛔ FAIL'}")
    if not (pos_ok and neg_ok and sham_ok and plac_ok):
        print("\n⛔ a control failed; nothing below certifies anything. Exit 2, never 0.")
        return 2
    floor = t_hi - t_lo
    print(f"  NOISE FLOOR — the twin comparison's interval width, a known-zero effect in this same "
          f"design: {floor:.6f}")

    rivals = [a for a in ext if a in V and a != CORE and not a.startswith("coval_core")]
    print(f"\n  {'admitted arm':<20}{'Δ (core − arm)':>16}{'lo':>10}{'hi':>10}  resolvable")
    rows = []
    for a in rivals:
        m, lo, hi = paired(CORE, a)
        res = "core BETTER" if lo > 0 else ("core WORSE" if hi < 0 else "no")
        rows.append({"arm": a, "delta": m, "lo": lo, "hi": hi, "resolvable": res})
        print(f"  {a:<20}{m:>+16.4f}{lo:>+10.4f}{hi:>+10.4f}  {res}")

    better = [r for r in rows if r["resolvable"] == "core BETTER"]
    worse = [r for r in rows if r["resolvable"] == "core WORSE"]
    world = ("C OUTRANKED — an admitted arm resolvably BEATS the instance" if worse else
             "A SINGLED OUT — the instance resolvably beats every other admitted arm"
             if len(better) == len(rows) and rows else
             f"B INDISTINGUISHABLE — {len(rows) - len(better)} of {len(rows)} admitted arms are not "
             f"resolvably ordered against the instance")
    print(f"\n⭐ {world}")
    if not (rows and len(better) == len(rows)):
        print("⛔ PRE-REGISTERED KILL FIRES: the definition CONTAINS the released core without")
        print("   SINGLING IT OUT. It admits a set in which the instance has no special status —")
        print("   which is 'the definition describes the instance' read from the other side: the")
        print("   clauses were written from one object and cannot rank that object above the")
        print("   trivial family they also admit.")
    print(f"\n⚠ 'BETTER' HERE MEANS 'AGREES MORE WITH THIS RELEASE'S ANNOTATORS'. It does not mean a")
    print("   better core. A2 is the release's own target and there is no external criterion.")

    out = HERE / "results" / "instance_rank.json"
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head="does the definition single out its own instance, or merely contain it",
        n_prompts=n, nboot=NBOOT, seed=SEED, extension=ext, rivals=[r["arm"] for r in rows],
        coverage=cov, dropped_for_partial_coverage=dropped,
        coverage_finding="coval_core_2bA and _2bB are scored on 200 of 968 prompts (21%); the "
                         "committed A2 loader imputes the missing 768 with the arm's own mean, so "
                         "their admission in R1000's extension rests on 79% imputed values. "
                         "Deduplication removes them and the 4 distinct objects are all at 968.",
        controls={"positive_vs_random": {"d": p_m, "lo": p_lo, "hi": p_hi, "ok": bool(pos_ok)},
                  "negative_vs_twin": {"d": t_m, "lo": t_lo, "hi": t_hi, "ok": bool(neg_ok)},
                  "sham": {"d": s_m, "lo": s_lo, "hi": s_hi, "ok": bool(sham_ok)},
                  "placebo_self": {"d": z_m, "ok": bool(plac_ok)}},
        noise_floor_twin_interval_width=floor, rows=rows, world=world,
        n_resolvably_better=len(better), n_rivals=len(rows),
        limitation="'better' means agrees more with this release's annotators; A2 is the release's "
                   "own target and there is no external criterion",
        withdrawn_next="R1010's NEXT asked for the reader-ratio of each artifact's STRONGEST field; "
                       "`strongest` is not identified without a per-artifact judgement, so the "
                       "quantity is not estimable and the question is withdrawn rather than "
                       "approximated",
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
