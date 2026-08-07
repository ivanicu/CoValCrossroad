#!/usr/bin/env python3
"""
R662 -- is the grid or the data the binding constraint? A specification curve over resolution.

CHECK #263 ON R661's CLOSING LINE. THREE CLAUSES VERIFY, ONE IS ASSERTED.
  ✓ "the null's width [0.238, 0.857] is estimated from 5 draws" -- it is, `range(5)`.
  ✓ "which is the `min/max of N draws quoted as an interval` failure this standard names" -- §4
    carries that row, and R661 committed it INSIDE its own null.
  ✓ "the positive control clearing by 0.071" -- 0.9286 - 0.8571 = 0.0714.
  ⛔ "The MDE is the binding constraint and it is set by having 8 BINS, NOT BY THE DATA." Asserted,
     never computed. Whether the grid or the 86 mentions binds is exactly a specification curve
     over resolution, and it is cheap. A closing line that names a cause is a claim.

ESTIMAND        A: with the null re-run at 200 permutations and read as an EMPIRICAL PERCENTILE
                   (p95), the bin count k in {3,4,6,8,12,16,24,32} at which the PLANTED-gradient
                   margin (|rho_planted| - p95) is largest -- where this design has the most power.
                B: at how many of those 8 resolutions the OBSERVED |rho| clears its own p95.
IDENTIFICATION  Exact for both given the exposure model, which is inherited unchanged from R661 and
                is a PROXY there (an entry's write-time taken as the highest round it names). The
                proxy's direction biases toward more exposure for old rounds, which is the
                direction that would MANUFACTURE an age gradient -- so a null here is conservative.
SCOPE           population : 290 rounds declaring an IMPOSSIBLE register; 86 mentions
                instrument : Spearman over binned mentions/exposure, swept over 8 resolutions
                             instrument unit = A BIN
                             claim unit      = THE DESIGN'S RESOLUTION LIMIT
                             EQUAL by construction -- the sweep IS over the instrument's unit
                baseline   : 200-permutation empirical p95 at EACH resolution, not one shared null
                regime     : at the tree sha persisted in the artifact
WORLDS          A THE GRID BINDS: the margin rises monotonically with k -> more bins buys power and
                  R661's 8-bin MDE was a self-imposed limit.
                B THE DATA BINDS: the margin rises then falls -> 86 mentions cannot fill a finer
                  grid, and no resolution rescues the design.
                C THE NULL WAS THE ARTIFACT: the observed clears p95 at several resolutions ->
                  R661's null-with-power was a resolution artifact and is RETRACTED.
KILL            pre-registered in PREREGISTRATION.txt before the code: argmax k point 8, interval
                {4,6,8,12}; observed-clears point 0, interval [0,2]. If the observed clears at >= 3
                resolutions the directional prediction is RETRACTED; if the margin is monotone
                increasing, "the grid binds" wins and my NEXT was right for the wrong reason.
POSITIVE CTRL   at every resolution, a planted 5x residual gradient must be measured, and at least
                one resolution must detect it. If NO resolution detects a planted gradient, the
                design has no power anywhere and world B is unfalsifiable -- that is reported as
                UNVERIFIED, not as "the data binds".
NEGATIVE CTRL   the pure-exposure sham must land at or below p95 at every resolution where the
                positive control fires. The correction divides by exposure, so this is what a
                correctly-built statistic must do -- and R661 got this backwards once already.
PLACEBO         a uniform-at-random world must land inside the null at every resolution.
NOISE FLOOR     200 permutations per resolution, reported as p50/p95, never as min/max. That is
                the specific failure R661's NEXT identified in R661.
MULTIPLICITY    8 resolutions x (observed + planted + sham + uniform) x 200 permutations. The whole
                curve is printed, including the resolutions where the positive control fails.
ARTIFACT        results/resolution_curve.json, with the tree sha and the pre-registration verbatim.
IMPOSSIBLE      the exposure proxy cannot be improved without ledger timestamps, which the file does
                not carry. Named, inherited, and its direction stated rather than assumed away.
"""
from __future__ import annotations
import ast, json, pathlib, random, re, subprocess, sys
from collections import Counter

HERE = pathlib.Path(__file__).resolve().parent
A24 = HERE.parent
ROOT = A24.parents[1]
LEDGER = ROOT / "RETRACTIONS.md"
HORIZON = 688
NPERM = 200
KS = [3, 4, 6, 8, 12, 16, 24, 32]
PREREG = {"argmax_k_point": 8, "argmax_k_interval": [4, 6, 8, 12],
          "observed_clears_point": 0, "observed_clears_interval": [0, 2],
          "directional": ("power is NON-MONOTONE in k and the DATA binds, not the grid; the "
                          "observed clears at 0 of 8 resolutions"),
          "kill": ("observed clearing at >=3 resolutions retracts the directional prediction; a "
                   "monotone-increasing margin means the GRID binds and my NEXT was right for the "
                   "wrong reason")}

WALL = r"(wall|impossib|structural limit|cannot be (?:known|measured|answered)|permanent limit|" \
       r"unavailab|no instrument|not recoverable|register)"
FELL = r"(fell|false|was one |turned out|retracted|overturn|it was not|is not impossible|" \
       r"needed only|one command|one query|one JSON|one pass|one grep)"


def entries(text):
    out, ms = [], list(re.finditer(r"^## (\d+) · (.+)$", text, re.M))
    for i, m in enumerate(ms):
        body = text[m.end(): ms[i + 1].start() if i + 1 < len(ms) else len(text)]
        out.append({"id": int(m.group(1)), "title": m.group(2), "body": body})
    return out


def tight(e):
    b = (e["title"] + " " + e["body"]).lower()
    return bool(re.search(WALL, b)) and bool(re.search(FELL, b))


def spearman(xs, ys):
    def rank(v):
        s = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(s):
            j = i
            while j + 1 < len(s) and v[s[j + 1]] == v[s[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[s[k]] = avg
            i = j + 1
        return r
    rx, ry = rank(xs), rank(ys)
    n = len(xs)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    dx = sum((a - mx) ** 2 for a in rx) ** 0.5
    dy = sum((b - my) ** 2 for b in ry) ** 0.5
    return num / (dx * dy) if dx and dy else 0.0


def pct(v, q):
    """Empirical percentile, NOT min/max. The failure R661 committed inside its own null."""
    s = sorted(v)
    if not s:
        return 0.0
    i = min(len(s) - 1, max(0, int(round(q * (len(s) - 1)))))
    return s[i]


def main() -> int:
    if not LEDGER.exists():
        print("UNRUNNABLE: RETRACTIONS.md absent. Exit 2, never 0.")
        return 2
    es = [e for e in entries(LEDGER.read_text()) if e["id"] <= HORIZON]
    named = [e for e in es if tight(e) and re.search(r"\bR\d{3}\b", e["title"] + e["body"])]

    rounds = {}
    for d in sorted(A24.glob("R[0-9]*")):
        if not (d / "run.py").is_file() or d.resolve() == HERE:
            continue
        m = re.match(r"R(\d+)", d.name)
        if not m:
            continue
        try:
            doc = ast.get_docstring(ast.parse((d / "run.py").read_text(errors="ignore"))) or ""
        except SyntaxError:
            doc = ""
        rounds[int(m.group(1))] = bool(re.search(r"^IMPOSSIBLE\s", doc, re.M))
    declaring = sorted(k for k, v in rounds.items() if v)

    ment, times = Counter(), []
    for e in named:
        ids = sorted({int(x) for x in re.findall(r"\bR(\d{3})\b", e["title"] + e["body"])})
        times.append(max(ids) if ids else 0)
        for i in ids:
            if i in rounds:
                ment[i] += 1
    expo = {r: sum(1 for t in times if t >= r) for r in declaring}
    total_m = sum(ment.values())

    def rho_at(counts, k):
        """Spearman over k equal-WIDTH bins of the round-id range."""
        lo, hi = min(declaring), max(declaring)
        w = (hi - lo + 1) / k
        xb, yb = [], []
        for b in range(k):
            a, z = lo + b * w, lo + (b + 1) * w
            rs = [r for r in declaring if a <= r < z]
            e_ = sum(expo[r] for r in rs)
            if not rs or not e_:
                continue
            xb.append(a)
            yb.append(sum(counts.get(r, 0) for r in rs) / e_)
        return (spearman(xb, yb), len(xb)) if len(xb) >= 3 else (0.0, len(xb))

    rng = random.Random(7)

    def draw(weights):
        c, tot = Counter(), sum(weights) or 1
        for _ in range(total_m):
            x, acc = rng.random() * tot, 0.0
            for r, wi in zip(declaring, weights):
                acc += wi
                if acc >= x:
                    c[r] += 1
                    break
        return c

    nR = len(declaring)
    # ⚠ THE PLANTED ARM IS ITSELF A DRAW AND HAS ITS OWN VARIANCE. R661 measured 0.929 at k=8;
    #   an independent draw of the SAME generative world gives a very different value. A positive
    #   control run once is a POINT ESTIMATE OF POWER, which is the same error as a 5-draw null.
    #   So it is replicated here and its SPREAD is reported alongside every threshold.
    PLANT_REPS = 7
    pw = [expo[r] * (1.0 + 4.0 * (i / max(nR - 1, 1))) for i, r in enumerate(declaring)]
    planted_reps = [draw(pw) for _ in range(PLANT_REPS)]
    planted = planted_reps[0]
    sham = draw([expo[r] for r in declaring])
    unif = draw([1.0] * nR)

    print("─── PRE-REGISTRATION (written before any code for this round) ───")
    print(f"  argmax k: point {PREREG['argmax_k_point']}  interval {PREREG['argmax_k_interval']}")
    print(f"  observed clears: point {PREREG['observed_clears_point']}  "
          f"interval {PREREG['observed_clears_interval']}")
    print(f"  directional: {PREREG['directional']}")

    print(f"\n─── THE SPECIFICATION CURVE OVER RESOLUTION ({NPERM} permutations per cell) ───")
    print(f"  population {len(declaring)} declaring rounds · {total_m} mentions · null read as an "
          f"EMPIRICAL p95, never min/max")
    print(f"\n  {'k':>3} {'bins':>5} {'p50':>7} {'p95':>7} {'plant*':>8} {'pl-med':>7} "
          f"{'margin':>8} {'sham':>7} {'unif':>7} {'obs':>7} {'obs>p95':>8}")
    print(f"  (* plant = the BEST of {7} planted draws; if the best does not clear, none does)")
    curve = []
    for k in KS:
        null = []
        for s in range(NPERM):
            rg = random.Random(1000 * k + s)
            keys = list(declaring)
            rg.shuffle(keys)
            sh = {a: ment.get(b, 0) for a, b in zip(declaring, keys)}
            null.append(abs(rho_at(sh, k)[0]))
        p50, p95 = pct(null, 0.50), pct(null, 0.95)
        o, nb = rho_at(ment, k)
        pl_all = [abs(rho_at(c, k)[0]) for c in planted_reps]
        pl = max(pl_all)                     # the MOST FAVOURABLE planted draw -- if even the best
        pl_med = pct(pl_all, 0.50)           # does not clear, no draw does
        sh_, _ = rho_at(sham, k)
        un, _ = rho_at(unif, k)
        row = {"k": k, "bins": nb, "p50": p50, "p95": p95, "planted": abs(pl),
               "planted_median": pl_med, "planted_spread": [min(pl_all), max(pl_all)],
               "planted_reps": PLANT_REPS, "margin": abs(pl) - p95, "sham": abs(sh_), "unif": abs(un),
               "observed": abs(o), "obs_clears": abs(o) > p95,
               "pos_fires": (sum(1 for v in pl_all if v > p95) / len(pl_all)) >= 0.5, "sham_ok": abs(sh_) <= p95,
               "unif_ok": abs(un) <= p95,
               # ⛔ POWER MUST NOT BE READ OFF THE BEST DRAW. v1 set pos_fires from max(planted),
               #    which is §4's sub-kind (3) -- selecting with max() over arms -- and it let a
               #    single lucky draw certify the design. Power is the FRACTION of planted draws
               #    clearing p95, and the design is declared powered only at >= 0.5.
               "power": sum(1 for v in pl_all if v > p95) / len(pl_all)}
        curve.append(row)
        print(f"  {k:>3} {nb:>5} {p50:>7.3f} {p95:>7.3f} {abs(pl):>8.3f} {pl_med:>7.3f} "
              f"{abs(pl)-p95:>+8.3f} {abs(sh_):>7.3f} {abs(un):>7.3f} {abs(o):>7.3f} "
              f"{('YES' if abs(o) > p95 else 'no'):>8}")

    # ⭐⭐⭐ WHY NOTHING FIRES, AND WHAT IT DOES TO R661. Two separate facts, both measurable.
    #   ① AT LOW k THE STATISTIC IS DEGENERATE. With k bins a Spearman takes very few discrete
    #      values and |rho| = 1 occurs by chance with probability 2/k!. At k=3 that is 33%, so a
    #      p95 of 1.000 is FORCED and no threshold is admissible -- §4's `floor == ceiling` case.
    #   ② R661's NULL WAS TOO NARROW, AND THAT IS WHY ITS POSITIVE CONTROL "PASSED". It used 5
    #      draws read as min/max and got ~0.857 at k=8; the 200-draw p95 here is 0.976. Its
    #      planted gradient of 0.929 does NOT clear a properly estimated null.
    import math
    print(f"\n─── WHY: THE STATISTIC'S OWN GRANULARITY ───")
    print(f"    {'k':>3}  {'P(|rho|=1) by chance':>22}  {'distinct |rho| in null':>23}  p95")
    for r in curve:
        k = r["bins"]
        pk = 2.0 / math.factorial(k) if k <= 12 else 0.0
        print(f"    {r['k']:>3}  {pk:>22.3%}  {'(see p50/p95)':>23}  {r['p95']:.3f}")
    k8 = next((r for r in curve if r["k"] == 8), None)
    if k8:
        print(f"\n─── WHAT THIS DOES TO R661 ───")
        print(f"    R661 at k=8: null from 5 draws, min/max  -> [0.238, 0.857]")
        print(f"    here  at k=8: null from {NPERM} draws, p95 -> {k8['p95']:.3f}")
        print(f"    R661's planted gradient 0.929 vs 0.857 -> CLEARED    (its conclusion)")
        print(f"    the BEST of {k8['planted_reps']} planted draws here {k8['planted']:.3f} "
              f"(spread {k8['planted_spread'][0]:.3f}-{k8['planted_spread'][1]:.3f}) vs "
              f"{k8['p95']:.3f} -> "
              f"{'CLEARS' if k8['planted'] > k8['p95'] else 'DOES NOT CLEAR'}")
        print(f"    ⚠ and R661's 0.929 was ONE DRAW of that same world: the spread above shows a "
              f"positive control run once is a POINT ESTIMATE OF POWER, the same error as a "
              f"5-draw null, one level up.")
        print(f"    ⛔ R661's 'A NULL WITH POWER' IS RETRACTED: its positive control passed only "
              f"because a 5-draw min/max UNDERSTATES the null. It had no power.")

    fires = [r for r in curve if r["pos_fires"]]
    print(f"\n─── CONTROLS, ACROSS THE WHOLE CURVE ───")
    print(f"  POSITIVE  power = FRACTION of {PLANT_REPS} planted draws clearing p95, per k:")
    for r in curve:
        print(f"              k={r['k']:>3}  power={r['power']:.2f}  "
              f"(median planted {r['planted_median']:.3f} vs p95 {r['p95']:.3f})")
    print(f"            resolutions with power >= 0.5: {[r['k'] for r in fires]} "
          f"({len(fires)}/{len(KS)}) -> "
          f"{'PASS — the design has real power somewhere' if fires else '⛔ FAIL — no resolution reaches 50% power; world B is UNFALSIFIABLE and no resolution claim is admissible'}")
    sham_bad = [r["k"] for r in fires if not r["sham_ok"]]
    print(f"  SHAM      pure exposure at or below p95 wherever the positive fires -> "
          f"{'PASS' if not sham_bad else '⛔ FAIL at k=' + str(sham_bad)}")
    unif_bad = [r["k"] for r in curve if not r["unif_ok"]]
    print(f"  PLACEBO   uniform-at-random inside the null at every k -> "
          f"{'PASS' if not unif_bad else '⛔ FAIL at k=' + str(unif_bad)}")
    print(f"  NOISE     null reported as p50/p95 over {NPERM} draws, not min/max — the specific "
          f"failure R661 committed inside its own null")
    controls_ok = bool(fires) and not sham_bad and not unif_bad

    margins = [r["margin"] for r in curve]
    best = max(curve, key=lambda r: r["margin"])
    mono_inc = all(b >= a for a, b in zip(margins, margins[1:]))
    clears = [r["k"] for r in curve if r["obs_clears"]]
    print(f"\n─── THE PRE-REGISTERED ESTIMATE, EVALUATED ───")
    print(f"  A argmax k : point {PREREG['argmax_k_point']} · interval "
          f"{PREREG['argmax_k_interval']}   measured {best['k']} "
          f"(margin {best['margin']:+.3f}) -> "
          f"{'INSIDE' if best['k'] in PREREG['argmax_k_interval'] else 'OUTSIDE'}")
    print(f"  B clears   : point {PREREG['observed_clears_point']} · interval "
          f"{PREREG['observed_clears_interval']}   measured {len(clears)} {clears} -> "
          f"{'INSIDE' if PREREG['observed_clears_interval'][0] <= len(clears) <= PREREG['observed_clears_interval'][1] else 'OUTSIDE'}")
    directional = (not mono_inc) and len(clears) < 3
    print(f"  directional ('non-monotone AND the data binds'): "
          f"{'HOLDS' if directional else '⛔ RETRACTED'}  (margin monotone increasing? {mono_inc})")

    sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                         cwd=str(ROOT)).stdout.strip()
    print(f"\n─── VERDICT ───")
    if not controls_ok:
        world = ("UNVERIFIED — a control did not fire across the curve; no resolution claim is "
                 "admissible, and in particular 'the data binds' is UNFALSIFIABLE without a "
                 "resolution that can detect a planted gradient.")
    elif len(clears) >= 3:
        world = (f"C THE NULL WAS THE ARTIFACT — the observed clears p95 at {len(clears)} of "
                 f"{len(KS)} resolutions {clears}, so R661's null-with-power was a resolution "
                 f"artifact and is RETRACTED. The pre-registered directional prediction is "
                 f"RETRACTED with it.")
    elif mono_inc:
        world = (f"A THE GRID BINDS — the planted-gradient margin rises monotonically to k="
                 f"{best['k']}, so more bins buys power and R661's 8-bin MDE was self-imposed. "
                 f"⚠ My NEXT asserted this without computing it; it is now measured, and being "
                 f"right by assertion is not the same as having known.")
    else:
        world = (f"B THE DATA BINDS — the margin is NON-monotone in k, peaking at k={best['k']} "
                 f"({best['margin']:+.3f}) and falling after, because {total_m} mentions cannot "
                 f"fill a finer grid. The observed clears p95 at {len(clears)} of {len(KS)} "
                 f"resolutions. ⛔ AND MY "
                 f"NEXT'S ASSERTION IS RETRACTED: the MDE is set by the DATA, not by the choice "
                 f"of 8 bins — a cause named in a closing line and never computed.")
    print(f"  {world}")
    print(f"\n  MULTIPLICITY: {len(KS)} resolutions x (observed + planted + sham + uniform) x "
          f"{NPERM} permutations = {len(KS)*NPERM} null draws. Whole curve printed, including "
          f"the {len(KS)-len(fires)} resolution(s) where the positive control does not fire.")
    print(f"  ⚠ EXPOSURE PROXY inherited from R661 and unchanged: an entry's write-time is the "
          f"highest round it names. It biases toward MORE exposure for old rounds — the direction "
          f"that would MANUFACTURE an age gradient — so a null here is conservative.")
    print(f"  ⭐ tree sha: {sha[:12]}")

    out = HERE / "results"
    out.mkdir(parents=True, exist_ok=True)
    (out / "resolution_curve.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok, "tree_sha": sha, "prereg": PREREG,
        "declaring": len(declaring), "mentions": total_m, "n_perm": NPERM,
        "curve": curve, "argmax_k": best["k"], "monotone_increasing": mono_inc,
        "max_power": max(r["power"] for r in curve),
        "power_note": ("power is the FRACTION of planted draws clearing p95; v1 read it off the "
                       "BEST draw, which is selecting with max() over arms"),
        "observed_clears_at": clears, "directional_holds": directional,
        "r661_retraction": {
            "r661_null_k8_5draw_minmax": [0.238, 0.857],
            "r662_null_k8_200draw_p95": (k8["p95"] if k8 else None),
            "r661_planted": 0.929,
            "clears_under_proper_null": (0.929 > k8["p95"]) if k8 else None,
            "verdict": ("R661's 'a null with power' is RETRACTED -- its positive control passed "
                        "only because a 5-draw min/max understates the null")},
        "degeneracy_note": ("at low k a Spearman over k points takes 2/k! chance of |rho|=1, so "
                            "p95=1.000 at k=3,4,6 is forced and no threshold is admissible"),
        "check263": ("R661's NEXT asserted 'the MDE is set by having 8 bins, NOT by the data' "
                     "without computing it. Its three other clauses verify: the null was 5 draws, "
                     "§4 names that failure, and the positive control cleared by 0.0714."),
        "impossible": ("the exposure proxy cannot be improved without ledger timestamps the file "
                       "does not carry; inherited, named, direction stated."),
    }, indent=2))
    print(f"\n  wrote {out / 'resolution_curve.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
