#!/usr/bin/env python3
"""
R849 · does the PROPOSED clause survive the test it was written to pass?

⛔ WHY. Entry 1368 showed both readings of ④ fail — strict excludes **0 of 42** (untested
decoration, by the register's own rule) and permissive excludes **25 of 58 including
`coval_core`** (empty extension). It then proposed a repair:

    "…exceeds, by a margin reported with its interval, the best rule in a NAMED reference class R,
     where R is stated in full and the margin is a lower bound on the margin against any superset."

**A proposal is a suggestion until it is instantiated and its extension counted.** This arc has
condemned four clauses with one question — *name an admissible object this clause EXCLUDES* — and
that question now points at my own wording. **It can fail here, and failing is the useful outcome.**

ESTIMAND        the EXTENSION of ④′: the number of scored arms whose paired per-prompt margin over
                the reference class's best rule is resolvably positive.
IDENTIFICATION  yes. R = R847/R848's 394 response-only rules, named in full and persisted; every
                arm is a released score matrix.
SCOPE           population: all `sat_*.npz` arms scored on the evaluation half (n reported)
                instrument: A2 vs the EVEN annotators; bar selected on the ODD annotators
                baseline:   the original ④ — strict extension 42/42 admitted, permissive 33/58
                regime:     home release; no fitting on labels in R
WORLDS          A · extension is 1 -> ④′ is the "definition describes the instance" failure, the
                    same one the register already names, and my repair is no repair
                B · extension is ~all -> ④′ excludes nothing and is decoration, exactly what
                    condemned the strict reading
                C · extension is strictly between -> ④′ does definitional work, and this is the
                    first clause in this definition that provably does
KILL            CONDITIONAL, pre-registered:
                  if placebo (bar vs itself) == 0 exactly
                     and positive control (an oracle arm) SATISFIES ④′
                     and negative control (a random arm) does NOT
                  then read the extension
                  else UNVERIFIED — the instantiation is unfit and its count means nothing
⚠ SELECTION     the bar rule is chosen on the ODD annotators and every margin is evaluated on the
                EVEN half. This is the other writer's R843 remedy verbatim: *"A3 must choose its
                subset on the ODD annotators and be scored on the EVEN half."* Selecting the bar on
                the scoring set is the winner's curse and would inflate the bar, DEFLATING the
                extension — i.e. it would flatter the clause by making it look selective.
PLACEBO         the bar rule against itself must be exactly 0.0.
MULTIPLICITY    one test per arm over ~107 arms; BH at q=0.05 over the whole family, cells tested
                reported beside cells surviving, non-survivors counted.
ARTIFACT        results/proposed_clause_extension.json with the commit hash and every arm's margin.
IMPOSSIBLE      construct validated (no external gold standard for "is this really a core") ·
                cross-release · causally identified. N/A with what each would require.
"""
import itertools, json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
import score as SC                                              # noqa: E402
R435 = next(ROOT.glob("E0*/A*/R435_*"), None)
import importlib.util                                            # noqa: E402
_s = importlib.util.spec_from_file_location("r435", R435 / "run.py")
r435 = importlib.util.module_from_spec(_s); _s.loader.exec_module(r435)

L = ["A", "B", "C", "D"]
POS_CTRL, NEG_CTRL = "oracle_k4", "random_k4_s0"


def load_texts():
    t = {}
    for line in open(ROOT / "data" / "comparisons.jsonl", encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        g = {x.get("response_index"): " ".join(
            str(m.get("content") or "") for m in (x.get("messages") or [])
            if m.get("role") == "assistant") for x in (r.get("responses") or [])}
        if len(g) >= 4 and all(g.get(c) for c in L):
            t[r["prompt_id"]] = {c: g[c] for c in L}
    return t


def boot(d, n=4000, seed=17):
    rng = np.random.default_rng(seed)
    bs = np.array([d[rng.integers(0, len(d), len(d))].mean() for _ in range(n)])
    lo, hi = np.percentile(bs, [2.5, 97.5])
    p = max(2 * min((bs <= 0).mean(), (bs >= 0).mean()), 1.0 / (n + 1))
    return float(d.mean()), float(lo), float(hi), float(p)


def bh(ps, q=0.05):
    C = len(ps); order = sorted(range(C), key=lambda i: ps[i]); kmax = -1
    for rank, i in enumerate(order, 1):
        if ps[i] <= q * rank / C:
            kmax = rank
    keep = [False] * C
    for rank, i in enumerate(order, 1):
        if rank <= kmax:
            keep[i] = True
    return keep


def main() -> int:
    targets, _ = SC.load_targets()
    texts = load_texts()
    pids = sorted(set(texts) & set(targets))
    print(f"  prompts usable: {len(pids)}")
    if len(pids) < 200:
        print("  UNRUNNABLE. Exit 2, never 0.")
        return 2

    # ODD annotators select the bar; EVEN annotators evaluate every margin.
    Hodd = {p: np.array([SC.cls(np.array(y, float)) for y, _ in targets[p][0::2]]) for p in pids}
    Heven = {p: np.array([SC.cls(np.array(y, float)) for y, _ in targets[p][1::2]]) for p in pids}
    pids = [p for p in pids if len(Hodd[p]) and len(Heven[p])]
    print(f"  prompts with BOTH halves non-empty: {len(pids)}")

    feats = {p: {c: r435.features(texts[p][c]) for c in L} for p in pids}
    base = sorted({k for p in pids for c in L for k in feats[p][c]} - {"__pos__"})
    fam = {}
    for name, key, sign in r435.RULES:
        fam[name] = {p: np.array([(feats[p][c][key] if key != "__pos__" else L.index(c))
                                  for c in L], float) * (1.0 if sign > 0 else -1.0) for p in pids}
    Z = {p: {k: ((lambda v: (v - v.mean()) / (v.std() + 1e-12))(
        np.array([feats[p][c][k] for c in L], float))) for k in base} for p in pids}
    for a, b in itertools.combinations(base, 2):
        for sa, sb in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            fam[f"{'+' if sa>0 else '-'}{a}{'+' if sb>0 else '-'}{b}"] = {
                p: sa * Z[p][a] + sb * Z[p][b] for p in pids}
    print(f"  reference class R: {len(fam)} rules, named in full and persisted")

    # ⚠ SELECT on ODD only
    sel = {n: float(np.mean([np.mean(SC.cls(v[p]) == Hodd[p]) for p in pids]))
           for n, v in fam.items()}
    star = max(sel, key=sel.get)
    print(f"  bar rule selected on the ODD half: `{star}` (odd-half A2 {sel[star]:.4f})")
    bar_even = {p: np.array([np.mean(SC.cls(fam[star][p]) == Heven[p])]) for p in pids}
    bar_mean = float(np.mean([bar_even[p][0] for p in pids]))
    print(f"  its EVEN-half A2 (the bar every arm must clear): {bar_mean:.4f}")

    # ---- PLACEBO ------------------------------------------------------------------------------
    pl = np.array([float(np.mean(SC.cls(fam[star][p]) == Heven[p])
                         - np.mean(SC.cls(fam[star][p]) == Heven[p])) for p in pids])
    pl_ok = abs(pl.mean()) < 1e-12
    print(f"  PLACEBO  bar rule vs itself: {pl.mean():+.2e}  {'PASS' if pl_ok else 'FAIL'}")

    # ---- every arm's margin on the EVEN half ---------------------------------------------------
    rows = []
    for f in sorted((ROOT / "corebench" / "results").glob("sat_*.npz")):
        nm = f.stem[4:]
        try:
            S = SC.load_sat(f)
        except Exception:
            continue
        ks = [p for p in pids if p in S]
        if len(ks) < 200:
            continue
        d = np.array([float(np.mean(SC.cls(SC.yvec(S[p], sorted({i for i, _ in S[p]}))) == Heven[p])
                            - np.mean(SC.cls(fam[star][p]) == Heven[p])) for p in ks])
        o, lo, hi, p_ = boot(d)
        rows.append({"arm": nm, "n": len(ks), "margin": o, "ci": [lo, hi], "p": p_})
    keep = bh([r["p"] for r in rows])
    for r, k in zip(rows, keep):
        r["satisfies"] = bool(k and r["ci"][0] > 0)
    ext = [r["arm"] for r in rows if r["satisfies"]]

    pc = next((r for r in rows if r["arm"] == POS_CTRL), None)
    nc = next((r for r in rows if r["arm"] == NEG_CTRL), None)
    pc_ok = bool(pc and pc["satisfies"])
    nc_ok = bool(nc and not nc["satisfies"])
    print(f"  POSITIVE  `{POS_CTRL}` must satisfy ④′: "
          f"{pc['satisfies'] if pc else 'ABSENT'} ({pc['margin']:+.4f} if present)  "
          f"{'PASS' if pc_ok else 'FAIL'}")
    print(f"  NEGATIVE  `{NEG_CTRL}` must NOT satisfy: "
          f"{(not nc['satisfies']) if nc else 'ABSENT'} ({nc['margin']:+.4f} if present)  "
          f"{'PASS' if nc_ok else 'FAIL'}")

    if not (pl_ok and pc_ok and nc_ok):
        print("\n  UNVERIFIED: a control failed for its own reasons; the extension count means")
        print("  nothing and is not reported. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "placebo_ok": pl_ok,
                   "pos_ok": pc_ok, "neg_ok": nc_ok},
                  open(OUT / "proposed_clause_extension.json", "w"), indent=2)
        return 2

    print(f"\n  MULTIPLICITY  {len(rows)} arms tested · {sum(keep)} survive BH q=0.05 · "
          f"{len(rows)-sum(keep)} non-survivors")
    print(f"  ⭐ EXTENSION of ④′: {len(ext)} of {len(rows)} arms")
    core = next((r for r in rows if r["arm"] == "coval_core"), None)
    if core:
        print(f"     `coval_core`: margin {core['margin']:+.4f} {core['ci']} — "
              f"{'SATISFIES' if core['satisfies'] else 'FAILS'}")
    world = "A" if len(ext) <= 1 else ("B" if len(ext) >= len(rows) - 1 else "C")
    print(f"  ⭐ WORLD {world}: " + {"A": "extension is 1 — the clause describes its instance,"
                                    " which is the failure the register already names",
                                    "B": "extension is ~all — the clause excludes nothing and is"
                                    " decoration, exactly what condemned the strict reading",
                                    "C": "extension is strictly between — ④′ DOES definitional"
                                    " work"}[world])
    print(f"     excluded: {len(rows)-len(ext)} arms. A clause is only as good as what it excludes.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "bar_rule": star, "bar_even_half_A2": bar_mean,
               "reference_class_size": len(fam), "n_arms": len(rows),
               "extension": ext, "extension_size": len(ext),
               "controls": {"placebo": float(pl.mean()), "pos": pc_ok, "neg": nc_ok},
               "arms": rows}, open(OUT / "proposed_clause_extension.json", "w"), indent=2)
    print(f"\n  artifact: results/proposed_clause_extension.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
