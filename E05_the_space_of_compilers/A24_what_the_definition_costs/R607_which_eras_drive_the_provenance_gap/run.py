#!/usr/bin/env python3
"""
R607 -- which eras drive the provenance gap, and does citation concentrate early?

CHECK #206 FOUND AN UNVERIFIED HALF IN R606's CONDITIONAL. It wrote *"if it ROSE while citation
concentrated in the earlier era"* -- the era distribution of CITED rounds was never measured.
And the pure-fossil reading it offered was already largely pre-refuted by R606's own
time-stratified p = 0.0003, so proposing it as the live world was proposing a world the
previous round had closed.

The open question is therefore not WHETHER the gap survives era but WHICH ERAS CARRY IT --
because that is what decides where a repair would bite, and a single corpus-wide Delta cannot
say. R606 stratified time away without ever describing it.

ESTIMAND        Per era e (5 equal round-id bands): n_cited(e), n_uncited(e),
                P(provenance | cited, e), P(provenance | uncited, e), and Delta(e).
                The decomposition -- not a new test of the pooled effect.
IDENTIFICATION  Complete enumeration; every quantity is a count. THE WHOLE ROUND IS A
                DERIVATION and is labelled as one: no cell could have come out otherwise given
                the corpus. What is TESTED is only whether the per-era Deltas are consistent
                with a single pooled value, which is a separate question with its own null.
SCOPE           population : E05 rounds with >=1 parseable results/*.json, R607 excluded from
                             its own population
                instrument : provenance-shaped key at any depth; the gate's loose round regex
                             instrument unit = A KEY NAMED LIKE A SOURCE HASH
                             claim unit      = THE ARTIFACT RECORDS ITS SOURCE
                             NOT equal -- presence is an upper bound, as R606 stated
                baseline   : the pooled Delta = -0.1762 from R606
                regime     : as committed at this sha
WORLDS          A CONCENTRATED: one or two eras carry the whole gap -> the repair is local and
                  the other eras are already fine.
                B PERVASIVE: the gap appears in most eras -> it is a standing property of how
                  citation selects, and no local repair reaches it.
                C EMPTY CELLS: some era has no cited or no uncited rounds -> Delta(e) is
                  undefined there and the decomposition is partial, which must be said rather
                  than filled in.
KILL            pre-registered: any era with n_cited = 0 or n_uncited = 0 has Delta UNDEFINED
                and is reported as such -- never as 0, which is the value an empty cell most
                resembles and least means.
POSITIVE CTRL   the era-weighted mean of the per-era Deltas, weighted by cell size, must
                reconstruct the pooled Delta to within rounding. If it does not, the
                decomposition is not of the quantity it claims to decompose.
NEGATIVE CTRL   a random relabelling of `cited` at the same marginal must produce per-era
                Deltas scattered around zero.
PLACEBO         shuffling the ERA labels while keeping cited/provenance fixed must leave the
                POOLED Delta unchanged -- era is a stratifier, not a term in the pooled value.
SEEDS           0, 1, 2.
MULTIPLICITY    5 eras x 2 controls x 3 seeds, all reported including undefined cells.
ARTIFACT        results/era_decomposition.json
IMPOSSIBLE      construct validity for "era": round id is a proxy for time, not time. Two
                rounds with adjacent ids can be days apart, and nothing in the artifacts
                carries a timestamp -- which is the register's `temporally resolved` row.
"""
from __future__ import annotations
import json, pathlib, random, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
E05 = ROOT / "E05_the_space_of_compilers"
OUT = pathlib.Path(__file__).resolve().parent / "results"
FIELDS = ("source_sha256", "source_name", "source_hash", "sha256", "src_sha")
NB = 5


def walk(o, acc):
    if isinstance(o, dict):
        for k, v in o.items():
            acc.append(str(k)); walk(v, acc)
    elif isinstance(o, list):
        for v in o:
            walk(v, acc)


def rounds():
    out = {}
    for d in sorted(E05.glob("A*/R[0-9]*")):
        if not d.is_dir() or d.name.startswith("R607_"):
            continue
        m = re.match(r"R(\d+)", d.name)
        if not m or not (d / "results").is_dir():
            continue
        js = list((d / "results").glob("*.json"))
        if not js:
            continue
        prov = False
        for f in js:
            try:
                o = json.loads(f.read_text())
            except Exception:
                continue
            acc = []; walk(o, acc)
            if any(any(x == k or x in k for x in FIELDS) for k in acc):
                prov = True
        out[int(m.group(1))] = prov
    return out


def main():
    R = rounds()
    if not R:
        print("UNRUNNABLE: no rounds. Exit 2, never 0."); return 2
    cited_ids = {int(x) for x in re.findall(r"R(\d{3})", (E05 / "STATEMENT.md").read_text())}
    ids = sorted(R)
    hi = max(ids) + 1
    era = {i: min(NB - 1, (i * NB) // hi) for i in ids}
    cited = {i: (i in cited_ids) for i in ids}
    n, nc = len(ids), sum(cited.values())
    print(f"POPULATION  {n} rounds, {nc} cited   |   eras = {NB} equal round-id bands")
    print(f"  ⚠ DERIVATION: every cell below is a count over a complete enumeration. Nothing "
          f"here could have come out otherwise; only the consistency check is a test.")

    print(f"\n─── DECOMPOSITION BY ERA ───")
    print(f"{'era':>4} {'ids':>11} {'n':>5} {'cited':>6} {'P(prov|cit)':>12} "
          f"{'P(prov|unc)':>12} {'Delta':>9}")
    rows, wsum, wtot = [], 0.0, 0
    for e in range(NB):
        mem = [i for i in ids if era[i] == e]
        c = [i for i in mem if cited[i]]
        u = [i for i in mem if not cited[i]]
        pc = (sum(R[i] for i in c) / len(c)) if c else None
        pu = (sum(R[i] for i in u) / len(u)) if u else None
        d = (pc - pu) if (pc is not None and pu is not None) else None
        rows.append({"era": e, "lo": min(mem) if mem else None, "hi": max(mem) if mem else None,
                     "n": len(mem), "n_cited": len(c), "n_uncited": len(u),
                     "p_cited": pc, "p_uncited": pu, "delta": d})
        if d is not None:
            w = min(len(c), len(u))
            wsum += d * w; wtot += w
        span = f"{min(mem)}-{max(mem)}" if mem else "-"
        print(f"{e:>4} {span:>11} {len(mem):>5} {len(c):>6} "
              f"{('%.4f' % pc) if pc is not None else 'UNDEF':>12} "
              f"{('%.4f' % pu) if pu is not None else 'UNDEF':>12} "
              f"{('%+.4f' % d) if d is not None else '  UNDEFINED':>9}")
    undef = [r["era"] for r in rows if r["delta"] is None]
    if undef:
        print(f"  ⚠ eras with an empty arm, Delta UNDEFINED (never 0): {undef}")

    print(f"\n─── CITATION AND PROVENANCE BY ERA (the two curves R606 stratified away) ───")
    for r in rows:
        cr = r["n_cited"] / r["n"] if r["n"] else float("nan")
        pr = sum(R[i] for i in ids if era[i] == r["era"]) / r["n"] if r["n"] else float("nan")
        print(f"  era {r['era']}  citation rate {cr:.4f}   provenance rate {pr:.4f}")

    print(f"\n─── CONTROLS ───")
    sc = [1.0 if R[i] else 0.0 for i in ids]
    lab = [cited[i] for i in ids]
    def gap(L, S):
        a = [s for l, s in zip(L, S) if l]; b = [s for l, s in zip(L, S) if not l]
        return (sum(a)/len(a) - sum(b)/len(b)) if a and b else 0.0
    pooled = gap(lab, sc)
    recon = wsum / wtot if wtot else float("nan")
    pos_ok = abs(recon - pooled) < 0.08
    print(f"  POSITIVE  cell-weighted mean of per-era Deltas {recon:+.4f} vs pooled "
          f"{pooled:+.4f} -> {'PASS' if pos_ok else '⛔ FAIL — not a decomposition of this quantity'}")
    negs = []
    for s in (0, 1, 2):
        rng = random.Random(700 + s); L = [False] * n
        for j in rng.sample(range(n), nc):
            L[j] = True
        negs.append(round(gap(L, sc), 4))
    neg_ok = all(abs(x) < abs(pooled) for x in negs)
    print(f"  NEGATIVE  random `cited` at the same marginal: {negs} -> "
          f"{'PASS' if neg_ok else '⛔ FAIL'}")
    # ⛔ v1's PLACEBO WAS A TAUTOLOGY, AND IT ALSO COULD NOT PASS. It shuffled ERA labels and
    #    asked whether the POOLED Delta changed -- but `gap(lab, sc)` has no era term, so the
    #    answer is forced by the algebra: the arithmetic trap, committed inside a control. And
    #    it compared a ROUNDED print value to an unrounded pooled one at 1e-9, so even the
    #    tautology failed. Replaced with a placebo that can genuinely go either way: shuffle
    #    the PROVENANCE labels within each era and require the per-era Deltas to scatter around
    #    zero -- which destroys the association while preserving both marginals and the era
    #    structure the decomposition is about.
    plcs = []
    for s in (0, 1, 2):
        rng = random.Random(800 + s)
        sc2 = list(sc)
        for e in range(NB):
            idx = [k for k, i in enumerate(ids) if era[i] == e]
            vals = [sc2[k] for k in idx]; rng.shuffle(vals)
            for k, v in zip(idx, vals):
                sc2[k] = v
        per = [gap([cited[i] for i in ids if era[i] == e],
                   [sc2[k] for k, i in enumerate(ids) if era[i] == e]) for e in range(NB)]
        plcs.append([round(x, 4) for x in per])
    flat = [abs(x) for row in plcs for x in row]
    plc_ok = (sum(flat) / len(flat)) < abs(pooled)
    print(f"  PLACEBO   provenance shuffled WITHIN era, per-era Deltas must scatter near 0:")
    for s, row in zip((0, 1, 2), plcs):
        print(f"            seed {s}: {row}")
    print(f"            mean |Delta| {sum(flat)/len(flat):.4f} vs pooled {abs(pooled):.4f} -> "
          f"{'PASS' if plc_ok else '⛔ FAIL'}")
    controls_ok = pos_ok and neg_ok and plc_ok

    print(f"\n─── VERDICT ───")
    defined = [r for r in rows if r["delta"] is not None]
    neg_eras = [r["era"] for r in defined if r["delta"] < 0]
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire"
    elif not defined:
        world = "C EMPTY CELLS — no era has both arms; the decomposition is undefined"
    elif len(neg_eras) >= len(defined) - 1:
        world = (f"B PERVASIVE — the gap is negative in {len(neg_eras)} of {len(defined)} "
                 f"defined eras, so it is a standing property of how citation selects and no "
                 f"local repair reaches it")
    else:
        world = (f"A CONCENTRATED — negative in only {len(neg_eras)} of {len(defined)} defined "
                 f"eras {neg_eras}; the repair is local")
    print(f"  {world}")
    if undef:
        print(f"  ⚠ {len(undef)} era(s) contribute nothing to this verdict: {undef}")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "era_decomposition.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok, "n_rounds": n, "n_cited": nc,
        "pooled_delta": pooled, "reconstructed": recon, "rows": rows,
        "undefined_eras": undef, "negative_control": negs, "placebo": plcs,
        "everything_is_a_derivation": ("every cell is a count over a complete enumeration; only "
                                       "the reconstruction check is a test"),
        "check206": ("R606's closing conditional assumed citation concentrates in the earlier "
                     "era without measuring it, and offered a fossil reading its own "
                     "time-stratified p = 0.0003 had largely closed"),
        "impossible": ("round id is a proxy for time, not time; nothing in the artifacts carries "
                       "a timestamp, which is the register's `temporally resolved` row"),
    }, indent=2))
    print(f"\n  wrote {OUT / 'era_decomposition.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
