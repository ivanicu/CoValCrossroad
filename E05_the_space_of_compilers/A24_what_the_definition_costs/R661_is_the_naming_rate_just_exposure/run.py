#!/usr/bin/env python3
"""
R661 -- is the 18.3% naming rate just EXPOSURE? And the rival I named had its arrow backwards.

CHECK #262 ON R660's CLOSING LINE. ONE SENTENCE CONTRADICTS ITSELF AND ONE RIVAL IS INVERTED.
  ⛔ "18.3% is the first number in this thread WITH A FLOOR UNDER IT -- but IT HAS NO FLOOR yet
     either." Both cannot hold. The commit body for the same round says "with any CONTENT", which
     is coherent; the README carries the broken version, and the README is what a later round
     reads. A correction must reach the artifact that a successor will open.
  ⛔ "the obvious rival is that entries name RECENT rounds -- the arc's own rounds are named
     constantly while the 200s are not." THE ARROW IS BACKWARDS. A ledger entry can only name a
     round that ALREADY EXISTED, so an OLD round has had MORE chances to be named. Exposure
     predicts the opposite of what I asserted.
  ⛔ And the assertion is false on its face: measured, the mention distribution PEAKS at R450-499
     (27 mentions) while the most recent full block R550-599 has 3 -- the second lowest. A middle
     peak is what neither rival predicts, and I stated the rival as fact in a NEXT line.

ESTIMAND        rho = Spearman correlation between a round's id and its EXPOSURE-CORRECTED naming
                rate, where exposure(r) = the number of wall-entries written after round r existed.
                Plus the shape: is the exposure-corrected profile MONOTONE in round age?
IDENTIFICATION  Exact for the correlation given the exposure model. NOT identified for "this round
                was named BECAUSE of its content" -- naming is an authored act and no statistic
                recovers intent. So the round settles whether recency/exposure SUFFICE, never what
                the residual variation is.
SCOPE           population : the 290 rounds declaring an IMPOSSIBLE register, MINUS this round
                instrument : R659's tight pattern at R659's horizon (entry <= 688), reproduced
                             instrument unit = A (ROUND, ENTRY) MENTION
                             claim unit      = A ROUND'S NAMING RATE
                             NOT EQUAL -- one entry names several rounds, which is why exposure is
                             counted in ENTRIES and the rate is per ROUND
                baseline   : a permutation null over the round->entry assignment, 5 seeds
                regime     : at the tree sha persisted in the artifact
WORLDS          A EXPOSURE EXPLAINS IT: |rho| is large and the profile monotone -> the naming rate
                  is an artifact of when a round was written and says nothing about registers.
                B IT DOES NOT: |rho| small or the profile non-monotone -> the variation is about
                  the rounds, and 18.3% survives as a fact about registers.
                C NO RESOLUTION: |rho| sits inside the permutation spread -> the design cannot
                  separate them and the number stays uninterpreted.
KILL            pre-registered in PREREGISTRATION.txt before the code: point |rho| 0.20, interval
                [0.00, 0.60], directional "the profile is NOT monotone". If |rho| > 0.60 AND the
                profile is monotone, the directional prediction is RETRACTED.
POSITIVE CTRL   a SYNTHETIC world where naming IS pure exposure -- assign mentions in proportion to
                exposure -- must produce a monotone profile and a large |rho|. If it does not, the
                instrument cannot detect the world it is meant to rule out, and no null is
                admissible. This is the arm R660 was missing.
NEGATIVE CTRL   a synthetic world where mentions are assigned uniformly at random must produce
                |rho| inside the permutation spread.
PLACEBO         shuffling the ROUND IDS while keeping the mention counts must destroy any real
                gradient -- that IS the permutation null, and it is reported as a spread, not a p.
NOISE FLOOR     the permutation spread over 5 seeds, measured, not assumed.
MULTIPLICITY    1 correlation x 1 population + 3 synthetic worlds + 5 permutation seeds + the
                binned profile printed whole.
ARTIFACT        results/exposure.json, with the tree sha and the pre-registration verbatim.
IMPOSSIBLE      why a particular round was named is an authored act; no statistic recovers intent.
                The round settles SUFFICIENCY of recency/exposure, never the content of the rest.
"""
from __future__ import annotations
import ast, json, pathlib, random, re, subprocess, sys
from collections import Counter

HERE = pathlib.Path(__file__).resolve().parent
A24 = HERE.parent
ROOT = A24.parents[1]
LEDGER = ROOT / "RETRACTIONS.md"
HORIZON = 688
PREREG = {"point_abs_rho": 0.20, "interval": [0.00, 0.60],
          "directional": "the exposure-corrected profile is NOT monotone in round age",
          "kill": "|rho| > 0.60 AND monotone retracts the directional prediction"}

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
    """Rank correlation, ties averaged. Written out rather than imported: numpy is not needed and
    a hand rank is checkable by eye."""
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


def monotone(profile):
    """Is the binned profile monotone (either direction), ignoring empty bins?"""
    v = [y for _, y in profile if y is not None]
    if len(v) < 3:
        return True
    up = all(b >= a for a, b in zip(v, v[1:]))
    dn = all(b <= a for a, b in zip(v, v[1:]))
    return up or dn


def main() -> int:
    if not LEDGER.exists():
        print("UNRUNNABLE: RETRACTIONS.md absent. Exit 2, never 0.")
        return 2
    es = [e for e in entries(LEDGER.read_text()) if e["id"] <= HORIZON]
    T = [e for e in es if tight(e)]
    named = [e for e in T if re.search(r"\bR\d{3}\b", e["title"] + e["body"])]

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

    # mentions, and EXPOSURE: entries whose own round-id ordering places them after round r.
    # A ledger entry's position is proxied by the highest round it names, which is the earliest
    # moment it could have been written. Stated as a proxy, with its direction, per the ledger.
    ment = Counter()
    entry_time = {}
    for e in named:
        ids = sorted({int(x) for x in re.findall(r"\bR(\d{3})\b", e["title"] + e["body"])})
        entry_time[e["id"]] = max(ids) if ids else 0
        for i in ids:
            if i in rounds:
                ment[i] += 1
    times = sorted(entry_time.values())
    expo = {r: sum(1 for t in times if t >= r) for r in declaring}

    print("─── PRE-REGISTRATION (written before any code for this round) ───")
    print(f"  point |rho| {PREREG['point_abs_rho']}   interval {PREREG['interval']}")
    print(f"  directional: {PREREG['directional']}")
    print(f"  kill       : {PREREG['kill']}")

    print("\n─── CONTROLS ───")
    print(f"  POSITIVE-0 R659's tight/named reproduce at horizon {HORIZON}: {len(T)}/{len(named)} "
          f"-> {'PASS' if (len(T), len(named)) == (39, 36) else '⛔ FAIL'}")
    xs = [float(r) for r in declaring]
    rate = [ment.get(r, 0) / max(expo[r], 1) for r in declaring]
    rho = spearman(xs, rate)

    # the permutation spread is computed FIRST, because two controls below are read against it
    perm_pre = []
    for seed in range(5):
        rg0 = random.Random(100 + seed)
        keys0 = list(declaring)
        rg0.shuffle(keys0)
        sh0 = {k: ment.get(o, 0) for k, o in zip(declaring, keys0)}
        perm_pre.append(abs(spearman(xs, [sh0[r] / max(expo[r], 1) for r in declaring])))
    lo_pre, phi_pre = min(perm_pre), max(perm_pre)
    total_m = sum(ment.values())
    rng = random.Random(0)
    w = [expo[r] for r in declaring]
    tot_w = sum(w) or 1
    synth_expo = Counter()
    for _ in range(total_m):
        x, acc = rng.random() * tot_w, 0.0
        for r, wi in zip(declaring, w):
            acc += wi
            if acc >= x:
                synth_expo[r] += 1
                break
    rho_expo = spearman(xs, [synth_expo.get(r, 0) / max(expo[r], 1) for r in declaring])
    # ⛔⛔ v1 CALLED THE PURE-EXPOSURE WORLD ITS POSITIVE CONTROL AND IT FAILED -- CORRECTLY, AND
    #     THE FAILURE INVERTS THE DESIGN. The statistic DIVIDES BY EXPOSURE, so a world where
    #     mentions are generated proportional to exposure is FLAT BY CONSTRUCTION and must land in
    #     the null. Demanding a large |rho| there is a CHECK THAT CANNOT PASS -- §4's row, the
    #     mirror of the one R660 committed. The two controls were swapped:
    #       SHAM      pure exposure -> must land INSIDE the permutation spread (it does)
    #       POSITIVE  a gradient exposure CANNOT explain -> mentions ~ exposure x (1 + k*rank),
    #                 which survives the division and must produce a large |rho|
    print(f"  SHAM       a world where naming IS pure exposure -> |rho| = {abs(rho_expo):.3f} -> "
          f"{'PASS — the correction removes it, as it must' if abs(rho_expo) <= phi_pre else '⛔ FAIL — the correction does not remove its own target'}")
    synth_grad = Counter()
    nR = len(declaring)
    wg = [expo[r] * (1.0 + 4.0 * (i / max(nR - 1, 1))) for i, r in enumerate(declaring)]
    tot_g = sum(wg) or 1
    for _ in range(total_m):
        x, acc = rng.random() * tot_g, 0.0
        for r, wi in zip(declaring, wg):
            acc += wi
            if acc >= x:
                synth_grad[r] += 1
                break
    rho_grad = spearman(xs, [synth_grad.get(r, 0) / max(expo[r], 1) for r in declaring])
    print(f"  POSITIVE-1 a world with a gradient EXPOSURE CANNOT EXPLAIN (mentions ~ exposure x "
          f"(1+4*rank)) -> |rho| = {abs(rho_grad):.3f} -> "
          f"{'PASS — the statistic can see a residual gradient' if abs(rho_grad) > phi_pre else '⛔ FAIL — no power, no null is admissible'}")
    unif = Counter()
    for _ in range(total_m):
        unif[rng.choice(declaring)] += 1
    rho_unif = spearman(xs, [unif.get(r, 0) / max(expo[r], 1) for r in declaring])
    print(f"  NEGATIVE   a SYNTHETIC world of uniform-at-random mentions -> |rho| = "
          f"{abs(rho_unif):.3f}")
    perm = []
    for seed in range(5):
        rg = random.Random(100 + seed)
        keys = list(declaring)
        rg.shuffle(keys)
        shuffled = {k: ment.get(o, 0) for k, o in zip(declaring, keys)}
        perm.append(abs(spearman(xs, [shuffled[r] / max(expo[r], 1) for r in declaring])))
    plo, phi = min(perm), max(perm)
    print(f"  PLACEBO    permutation null (5 seeds, round-ids shuffled) -> |rho| in "
          f"[{plo:.3f}, {phi:.3f}] — a SPREAD, not a p-value")
    controls_ok = ((len(T), len(named)) == (39, 36) and abs(rho_grad) > phi_pre
                   and abs(rho_expo) <= phi_pre)

    # ---- THE MEASUREMENT ------------------------------------------------------------
    print(f"\n─── NAMING RATE vs ROUND AGE, EXPOSURE-CORRECTED ───")
    print(f"  declaring rounds        : {len(declaring)}")
    print(f"  mentions (round,entry)  : {total_m}")
    print(f"  ⭐ observed |rho|         : {abs(rho):.3f}   (id vs mentions/exposure)")
    print(f"  permutation spread      : [{plo:.3f}, {phi:.3f}]")
    print(f"  sham (pure exposure)    : {abs(rho_expo):.3f}   uniform: {abs(rho_unif):.3f}   "
          f"planted residual gradient: {abs(rho_grad):.3f}")
    informative = abs(rho) > phi
    print(f"  => observed is {'ABOVE' if informative else 'INSIDE'} the permutation spread — "
          f"{'a real gradient' if informative else 'NO gradient distinguishable from chance'}")

    BIN = 50
    prof = []
    for b in range(min(declaring) // BIN * BIN, max(declaring) + 1, BIN):
        rs = [r for r in declaring if b <= r < b + BIN]
        if not rs:
            prof.append((b, None))
            continue
        m_, e_ = sum(ment.get(r, 0) for r in rs), sum(expo[r] for r in rs)
        prof.append((b, m_ / e_ if e_ else None))
    print(f"\n  the binned profile, whole (G3 — every bin including the empty ones):")
    for b, v in prof:
        rs = [r for r in declaring if b <= r < b + BIN]
        bar = "█" * int((v or 0) * 200)
        print(f"    R{b:>3}-{b+BIN-1:<3}  n={len(rs):>3}  mentions="
              f"{sum(ment.get(r,0) for r in rs):>3}  exposure={sum(expo[r] for r in rs):>4}  "
              f"rate={'—' if v is None else f'{v:.4f}'}  {bar}")
    mono = monotone(prof)
    print(f"\n  profile monotone in round age? {mono}")

    # ⭐⭐⭐ THE PER-ROUND STATISTIC HAS NO POWER, AND ITS OWN POSITIVE CONTROL IS WHAT SHOWS IT:
    #     a planted 5x gradient returns |rho| = {rho_grad:.3f}, inside the null. The cause is the
    #     UNIT, not the gradient -- 86 mentions over 290 rounds leaves most rounds at zero, so the
    #     rank vector is ~70% ties and Spearman is near-degenerate. The repair is to change the
    #     unit to the BIN, and to re-run every control at that unit rather than assume it inherits.
    def binned_rho(counts):
        xb, yb = [], []
        for b in range(min(declaring) // BIN * BIN, max(declaring) + 1, BIN):
            rs = [r for r in declaring if b <= r < b + BIN]
            e_ = sum(expo[r] for r in rs)
            if not rs or not e_:
                continue
            xb.append(float(b))
            yb.append(sum(counts.get(r, 0) for r in rs) / e_)
        return spearman(xb, yb), len(xb)

    rho_b, nb = binned_rho(ment)
    rho_b_grad, _ = binned_rho(synth_grad)
    rho_b_expo, _ = binned_rho(synth_expo)
    perm_b = []
    for seed in range(5):
        rg2 = random.Random(200 + seed)
        keys2 = list(declaring)
        rg2.shuffle(keys2)
        perm_b.append(abs(binned_rho({k: ment.get(o, 0)
                                      for k, o in zip(declaring, keys2)})[0]))
    plo_b, phi_b = min(perm_b), max(perm_b)
    print(f"\n─── THE SAME QUESTION AT THE BIN UNIT (n={nb} bins), with its controls RE-RUN ───")
    print(f"  POSITIVE  planted residual gradient -> |rho_bin| = {abs(rho_b_grad):.3f} vs null "
          f"[{plo_b:.3f}, {phi_b:.3f}] -> "
          f"{'PASS — the bin unit HAS power' if abs(rho_b_grad) > phi_b else '⛔ FAIL — no power at this unit either'}")
    print(f"  SHAM      pure exposure            -> |rho_bin| = {abs(rho_b_expo):.3f} -> "
          f"{'PASS — removed by the correction' if abs(rho_b_expo) <= phi_b else '⛔ FAIL'}")
    print(f"  OBSERVED                            -> |rho_bin| = {abs(rho_b):.3f} -> "
          f"{'ABOVE the null' if abs(rho_b) > phi_b else 'INSIDE the null'}")
    bin_ok = abs(rho_b_grad) > phi_b and abs(rho_b_expo) <= phi_b

    lo, hi = PREREG["interval"]
    inside = lo <= abs(rho) <= hi
    directional = not mono
    print(f"\n─── THE PRE-REGISTERED ESTIMATE, EVALUATED ───")
    print(f"  point {PREREG['point_abs_rho']} · interval [{lo}, {hi}]   measured |rho| {abs(rho):.3f}")
    print(f"  => magnitude {'INSIDE' if inside else 'OUTSIDE'}; error vs point "
          f"{abs(rho) - PREREG['point_abs_rho']:+.3f}")
    print(f"  => directional ('NOT monotone'): {'HOLDS' if directional else '⛔ RETRACTED'}")

    sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                         cwd=str(ROOT)).stdout.strip()
    print(f"\n─── VERDICT ───")
    if not controls_ok and not bin_ok:
        world = (f"UNVERIFIED AT EVERY UNIT TRIED — the per-round statistic returns "
                 f"|rho| = {abs(rho_grad):.3f} on a PLANTED 5x gradient, inside its own null "
                 f"[{lo_pre:.3f}, {phi_pre:.3f}], so it has no power; and the bin unit "
                 f"{'also fails' if not bin_ok else 'was not reached'}. The observed "
                 f"{abs(rho):.3f} is NOT admissible as a gradient. ⭐ 86 mentions over "
                 f"{len(declaring)} rounds leaves most at zero — the design is under-powered by "
                 f"the SPARSITY, and its own positive control is what established that rather "
                 f"than a plausible-looking number being reported.")
    elif not controls_ok and bin_ok and abs(rho_b) <= phi_b:
        # ⛔ v1 LABELLED THIS "B NOT EXPOSURE" WHILE ITS OWN NUMBER SAT INSIDE THE NULL. Third
        #    instance of the verdict-string mode in three rounds. A null WITH demonstrated power
        #    is a real result and must be stated as one -- but it is "no gradient detectable",
        #    not "the gradient is not exposure".
        world = (f"C A NULL WITH POWER — at the BIN unit a planted 5x residual gradient is "
                 f"detected ({abs(rho_b_grad):.3f} vs null [{plo_b:.3f}, {phi_b:.3f}]) and the "
                 f"pure-exposure sham is removed ({abs(rho_b_expo):.3f}), so the design can see "
                 f"the world it was built to rule out. The OBSERVED {abs(rho_b):.3f} lands INSIDE "
                 f"the null: NO age gradient is detectable. ⭐ So recency does not explain the "
                 f"18.3%, and neither does anything else this design can see. ⚠ MDE, stated: with "
                 f"only {nb} bins the null is wide, and the planted gradient clears it by "
                 f"{abs(rho_b_grad)-phi_b:.3f} — this design detects a gradient of roughly 5x "
                 f"across the range and nothing weaker. The per-round number {abs(rho):.3f} is "
                 f"WITHDRAWN: computed at a unit whose planted-gradient control returned "
                 f"{abs(rho_grad):.3f}, inside its own null.")
    elif not controls_ok and bin_ok:
        world = (f"B NOT EXPOSURE, AT THE BIN UNIT ONLY — the per-round statistic has no power "
                 f"(planted gradient {abs(rho_grad):.3f}, inside its null), but the BIN unit does: "
                 f"a planted residual gradient reaches {abs(rho_b_grad):.3f} against a null of "
                 f"[{plo_b:.3f}, {phi_b:.3f}], the pure-exposure sham is removed at "
                 f"{abs(rho_b_expo):.3f}, and the OBSERVED bin-level |rho| is {abs(rho_b):.3f} — "
                 f"{'ABOVE' if abs(rho_b) > phi_b else 'INSIDE'} the null. The profile is "
                 f"{'NOT ' if not mono else ''}monotone. ⚠ The per-round number {abs(rho):.3f} is "
                 f"withdrawn: it was computed at a unit with no demonstrated power.")
    elif not informative:
        world = (f"C NO RESOLUTION — observed |rho| = {abs(rho):.3f} sits INSIDE the permutation "
                 f"spread [{plo:.3f}, {phi:.3f}], so this design cannot separate an age gradient "
                 f"from chance and 18.3% stays uninterpreted. ⚠ Note the pure-exposure world "
                 f"reaches {abs(rho_grad):.3f} on a PLANTED residual gradient, so the "
                 f"statistic has power and the answer is genuinely 'no signal', not 'no power'.")
    elif abs(rho) > 0.60 and mono:
        world = (f"A EXPOSURE EXPLAINS IT — |rho| = {abs(rho):.3f} and the profile is monotone, so "
                 f"the naming rate is an artifact of when a round was written. The pre-registered "
                 f"directional prediction is RETRACTED.")
    else:
        world = (f"B NOT EXPOSURE — |rho| = {abs(rho):.3f} against a permutation spread of "
                 f"[{plo:.3f}, {phi:.3f}], and the profile is {'NOT ' if not mono else ''}monotone "
                 f"in round age. Recency does not explain the naming rate, and the rival R660's "
                 f"NEXT asserted had its arrow backwards: an OLD round has had MORE chances to be "
                 f"named, not fewer.")
    print(f"  {world}")
    print(f"\n  MULTIPLICITY: 1 correlation + 2 synthetic worlds + 5 permutation seeds + "
          f"{len(prof)} bins printed whole.")
    print(f"  ⚠ EXPOSURE IS A PROXY: an entry's write-time is taken as the highest round it names, "
          f"the earliest moment it could exist. Direction stated; it biases toward MORE exposure "
          f"for old rounds, which is the direction that would MANUFACTURE world A.")
    print(f"  ⭐ tree sha: {sha[:12]}")

    out = HERE / "results"
    out.mkdir(parents=True, exist_ok=True)
    (out / "exposure.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok, "tree_sha": sha, "prereg": PREREG,
        "declaring": len(declaring), "mentions": total_m,
        "rho": rho, "abs_rho": abs(rho), "monotone": mono, "informative": informative,
        "permutation_spread": [plo, phi], "rho_pure_exposure_world": abs(rho_expo),
        "rho_uniform_world": abs(rho_unif), "rho_planted_gradient": abs(rho_grad),
        "profile": [{"bin": b, "rate": v} for b, v in prof],
        "bin_unit": {"n_bins": nb, "rho": rho_b, "planted_gradient": abs(rho_b_grad),
                     "sham_pure_exposure": abs(rho_b_expo), "null": [plo_b, phi_b],
                     "has_power": bin_ok},
        "magnitude_inside": inside, "directional_holds": directional,
        "check262": ("R660's README said 18.3% is 'the first number with a FLOOR under it -- but "
                     "it has NO FLOOR yet either', which contradicts itself; the commit body says "
                     "'with any CONTENT' and is coherent. And its recency rival is INVERTED: an "
                     "entry can only name a round that already existed, so an OLD round has had "
                     "MORE chances. Measured, mentions peak at R450-499 (27) while R550-599 has "
                     "3 -- a middle peak neither rival predicts."),
        "impossible": ("why a particular round was named is an authored act; no statistic "
                       "recovers intent. This settles SUFFICIENCY of recency/exposure only."),
    }, indent=2))
    print(f"\n  wrote {out / 'exposure.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
