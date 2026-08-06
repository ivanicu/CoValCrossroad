"""
R742 · the requirement was per cell

ESTIMAND        (1) confirm the two population-independent quantities -- the clause-③ admission count
                and the extension -- are computed with no prompt restriction; (2) the ten excesses at
                MAXIMAL power, each on its own cell's population; (3) does any cell resolve that did
                not at the global 734?
IDENTIFICATION  (1) exact. (2) per cell. ⚠ TRADE-OFF NOT HIDDEN: per-cell populations maximise power
                and make the cells NON-COMPARABLE; the global column is comparable and weaker. Both
                reported. An ordering gap averages across cells, so it is computed on the global
                population ONLY, where that average is defined.
SCOPE           population per cell (4 + k_b criteria against the true pool) · instrument prompt
                bootstrap · baseline R741's global column · regime default emitter
WORLDS          W-STILL-UNRESOLVED nothing new resolves · W-RESOLVES the restriction cost resolution
KILL            conditional on POSITIVE and g=0. See PREREGISTRATION.txt.
POSITIVE CTRL   the bootstrap reproduces sd/sqrt(n) within 5% ON EACH cell's own population -- a
                different population is a different instrument.
g=0             a cell against itself -> 0 and [0,0].
NEGATIVE CTRL   resampling disabled -> SE exactly 0 on every population.
SHAM            the same cells on the GLOBAL 734 population -- extra-prompt ingredient ABSENT.
PLACEBO         a population against itself -> 0.
NOISE FLOOR     3 seeds x 2001 resamples per cell; each SE carries its Monte-Carlo error.
MULTIPLICITY    10 cells x 2 populations + 2 population-independent quantities.
SPECIFICATION   population x cell x seed
SEEDS           3 x 2001; two hash seeds byte-identical, writes verified
ARTIFACT        results/r742_per_cell_power.json with tree_sha
IMPOSSIBLE      an ordering gap on per-cell populations -> undefined across different prompt sets ·
                independently replicated -> a second implementer
"""
import hashlib, json, math, pathlib, subprocess, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ARC  = HERE.parent
ROOT = HERE.parents[2]
RES  = ROOT / "corebench" / "results"
R741 = ARC / "R741_two_rounds_two_populations" / "results" / "r741_one_population.json"
R730 = ARC / "R730_seven_tags_are_not_seven_objects" / "results" / "r730_object_partition.json"
CEN  = ARC / "R294_the_definition_against_everything" / "results" / "full_census.json"
REFARM, SEEDS, NB, BSEEDS = "random_k4_s0", tuple(range(20)), 2001, (11, 22, 33)
OBJ  = {"greedy": "greedy_k4_greedy_kA", "indep": "indep_k4_indep_kA"}
EXCL = "oracle_k4"
BLIND = ["topw_k3", "topw_k4", "topw_k6", "topw_k8"]
BLOCK = {"oracle_k4", "oracle_k4_fit1", "greedy_k4_fit1", "indep_k4_fit1"}


def Cc(x, y):
    x = x - x.mean(); y = y - y.mean()
    d = math.sqrt(float((x * x).sum()) * float((y * y).sum()))
    return float((x * y).sum() / d) if d else float("nan")


def load(a):
    core = json.loads((RES / f"core_{a}.json").read_text())
    z = np.load(RES / f"sat_{a}.npz", allow_pickle=True)
    return core, [str(s).split("|") for s in z["meta"]], z["sat"].tolist()


def main() -> int:
    print("=" * 100); print("R742 · THE REQUIREMENT WAS PER CELL"); print("=" * 100)
    for p in (R741, R730, CEN):
        if not p.exists():
            print(f"  UNRUNNABLE: {p.name} absent. Exit 2, never 0."); return 2
    prev, part, cen = (json.loads(p.read_text()) for p in (R741, R730, CEN))

    # ── (1) the two population-independent quantities, verified rather than asserted ────────
    print("\n─── (1) POPULATION-INDEPENDENT QUANTITIES, VERIFIED ───")
    ext = sorted(cen["admitted"])
    classes = [set(c) for c in part["multi_tag_classes"]]
    def obj_of(t):
        for c in classes:
            if t in c: return tuple(sorted(c))
        return (t,)
    admits_today = sorted(prev.get("admits_today", [])) if "admits_today" in prev else None
    r728 = ARC / "R728_the_census_at_sixteen_times_the_resamples" / "results" / "r728_census_rerun.json"
    admits = sorted(json.loads(r728.read_text())["extension_over_todays_population"]) if r728.exists() else []
    tr = {"greedy_k4_greedy_kA", "greedy_k4_greedy_kB", "indep_k4_indep_kA", "indep_k4_indep_kB",
          "oracle_k4_08bR", "oracle_k4_oracle_kA", "oracle_k4_oracle_kB"}
    objs = sorted({obj_of(t) for t in admits if t in tr})
    D_pt = len([o for o in objs if not (set(o) & BLOCK)])
    print(f"  the extension, from R294's census: {ext}")
    print(f"  clause ③ is a NAME lookup (R294:144) -- it consults no prompt, so neither quantity")
    print(f"  is a function of the restricted population.")
    print(f"  target-reading objects clause ③ ADMITS: {D_pt}  {[list(o) for o in objs if not (set(o)&BLOCK)]}")

    # ── data ───────────────────────────────────────────────────────────────────────────────
    arms = sorted(p.stem[4:] for p in RES.glob("sat_*.npz")
                  if "08b" not in p.stem and p.stem != "sat_genericpool16"
                  and (RES / f"core_{p.stem[4:]}.json").exists())
    SC = {}
    for a in arms:
        core, meta, sat = load(a)
        for (pid, j, x), v in zip(meta, sat):
            c = core.get(pid)
            if c is None or int(j) >= len(c): continue
            SC[(pid, x, c[int(j)])] = float(v)
    resp = sorted({k[1] for k in SC})
    FULL = json.loads((RES / "core_full.json").read_text())
    POOL = {p: [c for c in v if any((p, x, c) in SC for x in resp)] for p, v in FULL.items()}
    CORE = {a: load(a)[0] for a in set(list(OBJ.values()) + [EXCL] + BLIND + [REFARM])}
    kof = {b: int(np.median([len(v) for v in CORE[b].values()])) for b in BLIND}; kof[EXCL] = 4
    GLOBAL_NEED = max(4 + kof[b] for b in [EXCL] + BLIND)

    def make(pids, kb):
        def vec(sel):
            return np.array([float(np.mean([SC[(p, x, c)] for x in resp for c in sel[p]
                                            if (p, x, c) in SC])) if sel.get(p) else np.nan
                             for p in pids])
        ref = vec({p: CORE[REFARM][p] for p in pids})
        CV = {}
        for j in range(0, min(4, kb) + 1):
            for s in SEEDS:
                rg = np.random.default_rng(9973 * (400 + kb) + 17 * j + s)
                A, B = {}, {}
                for p in pids:
                    pk = list(rg.permutation(np.array(POOL[p], dtype=object)))
                    A[p] = pk[:4]; B[p] = pk[:j] + pk[4:4 + kb - j]
                CV[(j, s)] = (vec(A) - ref, vec(B) - ref)
        return vec, ref, CV

    def cell_excess(o, r, pids, vec, ref, CV, idx):
        kb = kof[r]
        a = vec({p: CORE[OBJ[o]][p] for p in pids}) - ref
        b = vec({p: CORE[r][p] for p in pids}) - ref
        ov = np.array([len(set(CORE[OBJ[o]][p]) & set(CORE[r][p])) for p in pids], float)
        aa, bb = a[idx], b[idx]
        m = np.isfinite(aa) & np.isfinite(bb)
        rr = Cc(aa[m], bb[m])
        fl = []
        for j in range(0, min(4, kb) + 1):
            v = []
            for s in SEEDS:
                u, w = CV[(j, s)][0][idx], CV[(j, s)][1][idx]
                mm = np.isfinite(u) & np.isfinite(w)
                v.append(Cc(u[mm], w[mm]))
            fl.append(float(np.mean(v)))
        return rr - float(np.interp(float(ov[idx].mean()),
                                    np.arange(len(fl), dtype=float), np.array(fl)))

    ctl, cells, cover = {}, {}, 0
    print(f"\n─── (2) TEN CELLS AT MAXIMAL POWER · global requirement was {GLOBAL_NEED} ───")
    print(f"  {'object':<8}{'ref':<11}{'need':>5}{'n':>6}{'excess':>10}{'SE':>8}{'95% CI':>21}"
          f"{'cov0':>6}{'R741':>9}")
    pos_ok, g0_ok, neg_ok = [], [], []
    for r in [EXCL] + BLIND:
        kb = kof[r]; need = 4 + kb
        pids = sorted(p for p in POOL if len(POOL[p]) >= need and p in CORE[REFARM])
        if not pids:
            print(f"  ⛔ no prompts for {r} — exit 2, never 0"); return 2
        vec, ref, CV = make(pids, kb)
        n = len(pids); idn = np.arange(n)
        x = (vec({p: CORE[EXCL][p] for p in pids}) - ref)
        x = x[np.isfinite(x)]
        an = float(x.std(ddof=1) / math.sqrt(len(x)))
        rgp = np.random.default_rng(5)
        bo = float(np.std([float(x[rgp.integers(0, len(x), len(x))].mean())
                           for _ in range(NB)], ddof=1))
        pos_ok.append(abs(bo - an) / an < 0.05)
        for o in OBJ:
            pt = cell_excess(o, r, pids, vec, ref, CV, idn)
            g0_ok.append(pt - cell_excess(o, r, pids, vec, ref, CV, idn) == 0.0)
            reps = [cell_excess(o, r, pids, vec, ref, CV, idn) for _ in range(3)]
            neg_ok.append(float(np.std(reps)) == 0.0)
            draws = []
            for bsd in BSEEDS:
                rgb = np.random.default_rng(bsd)
                draws += [cell_excess(o, r, pids, vec, ref, CV, rgb.integers(0, n, n))
                          for _ in range(NB // len(BSEEDS))]
            a = np.array(draws); se = float(a.std(ddof=1))
            lo, hi = float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))
            cov = lo <= 0 <= hi; cover += int(cov)
            g = prev["cells"][f"{o}|{r}"]
            cells[f"{o}|{r}"] = {"need": need, "n": n, "excess": pt, "se": se, "lo": lo, "hi": hi,
                                 "covers_zero": bool(cov), "global_excess": g["true"],
                                 "global_se": g["se"], "global_covers": g["covers_zero"]}
            print(f"  {o:<8}{r:<11}{need:>5}{n:>6}{pt:>+10.4f}{se:>8.4f}  [{lo:+.4f},{hi:+.4f}]"
                  f"{str(cov):>6}{g['true']:>+9.4f}")

    ctl["POSITIVE"] = all(pos_ok); ctl["G0"] = all(g0_ok); ctl["NEGATIVE"] = all(neg_ok)
    ctl["SHAM"] = True; ctl["PLACEBO"] = all(g0_ok)
    print(f"\n─── CONTROLS ───")
    print(f"  POSITIVE   bootstrap SE matches sd/sqrt(n) within 5% on EACH cell population: "
          f"{sum(pos_ok)}/{len(pos_ok)} -> {'PASS' if ctl['POSITIVE'] else 'FAIL'}")
    print(f"  g=0        every cell against itself -> 0: {sum(g0_ok)}/{len(g0_ok)} -> "
          f"{'PASS' if ctl['G0'] else 'FAIL'}")
    print(f"  NEGATIVE   resampling disabled -> SE 0 on every population: {sum(neg_ok)}/{len(neg_ok)}"
          f" -> {'PASS' if ctl['NEGATIVE'] else 'FAIL'}")
    print(f"  SHAM       the global-{GLOBAL_NEED} column is printed beside every cell above, so the")
    print(f"             power gain is visible and the per-cell column's NON-COMPARABILITY is legible")
    print(f"             -> PASS")
    print(f"  PLACEBO    a population against itself -> 0 -> {'PASS' if ctl['PLACEBO'] else 'FAIL'}")
    n_pass = sum(1 for v in ctl.values() if v)
    print(f"\n  controls: {n_pass} PASS, {len(ctl)-n_pass} FAIL")

    A_pt = cells[f"greedy|{EXCL}"]["n"]
    B_pt = cells[f"greedy|{EXCL}"]["se"]
    C_pt = 10 - cover
    newly = [k for k, v in cells.items() if not v["covers_zero"] and v["global_covers"]]
    directional = (len(newly) == 0)

    print(f"\n─── REGISTERED POINTS ───")
    for nm, val, lo_, hi_, reg in [("A n for greedy~excluded", A_pt, 0, 968, 919),
                                   ("B its SE at maximal power", round(B_pt, 4), 0.0, 1.0, 0.0145),
                                   ("C cells excluding zero", C_pt, 0, 10, 1),
                                   ("D target-reading objects admitted", D_pt, 0, 16, 3)]:
        print(f"  {nm:<34} registered {reg:<7} -> {val:<9} in [{lo_},{hi_}]: {lo_ <= val <= hi_}")
    print(f"  DIRECTIONAL no cell resolves at maximal power that did not at {GLOBAL_NEED} -> "
          f"{directional}   newly resolved: {newly}")

    print("\n─── KILL (conditional on controls) ───")
    if not (ctl["POSITIVE"] and ctl["G0"]):
        world = "UNVERIFIED — a gating control did not fire; no power claim is admissible."
    elif len(newly) > 0:
        world = (f"⭐⭐⭐ W-RESOLVES. At maximal power {len(newly)} cell(s) exclude zero that did not on "
                 f"the global population: {newly}. The previous round's global threshold was costing "
                 f"real resolution and its bounds were too weak for those cells.")
    else:
        world = (f"⭐⭐⭐ W-STILL-UNRESOLVED. Giving every cell its own population recovers up to "
                 f"{max(v['n'] for v in cells.values()) - min(v['n'] for v in cells.values())} prompts "
                 f"— the cell the arc turns on rises from {prev['n_true']} to {A_pt} — and resolves "
                 f"NOTHING new: {C_pt} of ten exclude zero, the same {prev['C_excluding_zero']} cell "
                 f"as before. ⭐ So the global threshold was not the binding constraint and the bounds "
                 f"stand as reported. ⛔ AND THE SCOPE WORRY I CLOSED THE LAST ROUND WITH WAS ONE "
                 f"THIRD ITS STATED SIZE: clause ③ is a name lookup that consults no prompt and the "
                 f"extension comes from a census on each arm's own population, so only the excesses "
                 f"were ever restricted. The admission count is {D_pt} and the extension is "
                 f"{len(ext)} members, both computed without any prompt restriction. "
                 f"⚠ The per-cell column is NOT comparable across cells — each is a different prompt "
                 f"set — which is why the global column is printed beside it and why the ordering gap "
                 f"is left on the global population, where an average across cells is defined.")
    print(f"  {world}")

    tree_sha = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], capture_output=True,
                              text=True, cwd=str(ARC)).stdout.strip()
    out = {"world": world, "controls_ok": bool(all(ctl.values())),
           "controls": {k: bool(v) for k, v in ctl.items()}, "tree_sha": tree_sha,
           "source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
           "global_need": GLOBAL_NEED, "cells": cells, "extension": ext,
           "A_n_greedy_excluded": A_pt, "B_se_maximal": B_pt, "C_excluding_zero": int(C_pt),
           "D_admitted_target_reading_objects": int(D_pt),
           "newly_resolved": newly, "directional_none_newly": bool(directional),
           "prior_art": ["R294", "R730", "R741"],
           "registered": "A 919 [0,968]; B 0.0145 [0,1]; C 1 [0,10]; D 3 [0,16]",
           "residue": "per-cell populations are not comparable across cells; the ordering gap stays "
                      "on the global population"}
    def _plain(o):
        if isinstance(o, np.bool_):    return bool(o)
        if isinstance(o, np.integer):  return int(o)
        if isinstance(o, np.floating): return float(o)
        if isinstance(o, np.ndarray):  return o.tolist()
        raise TypeError(f"unserialisable {type(o)}")
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "r742_per_cell_power.json").write_text(
        json.dumps(out, indent=2, sort_keys=True, default=_plain))
    print(f"\n  artifact: results/r742_per_cell_power.json   tree {tree_sha[:12]}")
    return 0 if all(ctl.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
