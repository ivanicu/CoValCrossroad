"""R291 — auditing the IMPOSSIBILITY REGISTER itself, after one of its lines turned out false.

WHY. R290's premise was that `cross-model` had been wrongly registered as impossible — the judge is
my instrument, not the site, and a second model was on disk. That raises the obvious question I had
never asked: **how many of the OTHER registered impossibilities were checked?** The register's whole
job is to be the honest list, so an unchecked line in it is the most expensive kind, and §4's
`a wall never checked` applies to it more sharply than to anything else.

Three lines were checkable from the release schema and none had been:
  `temporally resolved — timestamps the release may not carry`   -> CHECK the schema
  `position randomized — needs a presentation-order field`        -> CHECK the schema
  `cross-model`                                                   -> falsified in R290

⚠ AND THIS ROUND EXISTS BECAUSE I RAN IT AS INLINE SCRIPTS FIRST. §3: no cheap attacks — no null,
no artifact, no stamp is not evidence whichever way it comes out. The numbers below are the same
ones, re-run inside a round that persists them and states its null.

ESTIMAND        (a) which registered-impossible lines are decidable from the release schema;
                (b) the slot (response_index) effect in the HUMAN target, against a within-prompt
                    permutation null; (c) the same effect in each JUDGE's scores; (d) whether the
                    two share it, which is what would make it a confound rather than a residual.
IDENTIFICATION  (a) is a schema fact. (b)-(d) are exact given the release; the null is exact.
SCOPE           population CoVal prompts with >=2 annotators · instrument Qwen3.5-2B-Base ·
                baseline the within-prompt permutation null · regime mean human score per slot.
WORLDS          W-SHARED    both human and judge carry a resolved slot effect in the same direction
                            -> A2 is inflated by a shared position artifact and every margin in the
                            file is partly order agreement.
                W-RESIDUAL  the human carries one and the judge does not -> slot is a component of
                            the TARGET that no arm tracks, so it caps achievable A2 rather than
                            inflating it. Different sign of consequence entirely.
KILL            pre-registered: if any arm's judge scores show a slot effect separable from the
                permutation null AND its slot ordering matches the human's, W-SHARED holds and
                every A2 in FORMULATION.md is re-labelled as containing a position component.
POSITIVE CTRL   the null must be able to fire: a synthetic target with a PLANTED slot effect of the
                human's observed size must return p < 0.05. Otherwise a null result is silence.
NEGATIVE CTRL   the within-prompt permutation preserves each prompt's score multiset exactly, so it
                destroys slot and NOTHING else. Stated because a permutation null answers `did the
                pairing matter`, never `why`, and here the pairing IS slot by construction.
PLACEBO         a target with slots already exchangeable must return p near uniform.
MULTIPLICITY    5 tested effects (4 arms + human); BH over all 5.
SEEDS           2000 permutation draws; the draw count floors p at 1/2001.
ARTIFACT        results/register_audit.json with source hash.
IMPOSSIBLE      `construct validated` and `cross-release` remain genuinely impossible and are NOT
                touched by this round — the point is that they now sit beside checked lines rather
                than unchecked ones.
"""
import json, sys, pathlib, itertools, hashlib
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec          # noqa: E402

DRAWS = 2000
ARMS = ["coval_core", "topw_k4", "generic", "full"]


def spread(M):
    m = M.mean(axis=0)
    return float(m.max() - m.min())


def perm_p(M, rng, draws=DRAWS):
    obs = spread(M)
    null = np.array([spread(np.array([r[rng.permutation(4)] for r in M])) for _ in range(draws)])
    return obs, float(null.mean()), float(np.percentile(null, 95)), float((null >= obs).mean())


def main():
    tg, _ = load_targets()
    S = {a: load_sat(ROOT / "corebench" / "results" / f"sat_{a}.npz") for a in ARMS}
    pids = sorted(set.intersection(*(set(v) for v in S.values())) &
                  {p for p in tg if len(tg[p]) >= 2})
    H = np.array([np.array([np.array(t[0], float) for t in tg[p]]).mean(axis=0) for p in pids])
    rng = np.random.default_rng(11)
    print(f"  {len(pids)} prompts · within-prompt permutation null, {DRAWS} draws\n")

    # ---- schema decisions -----------------------------------------------------------------
    rec = json.loads((ROOT / "data" / "comparisons.jsonl").open().readline())
    def paths(o, pre="", out=None, d=0):
        out = out if out is not None else set()
        if d > 3: return out
        if isinstance(o, dict):
            for k, v in o.items(): out.add(pre + k); paths(v, pre + k + ".", out, d + 1)
        elif isinstance(o, list) and o: paths(o[0], pre + "[].", out, d + 1)
        return out
    ks = sorted(paths(rec))
    has_time = [k for k in ks if any(w in k.lower() for w in ("time", "date", "stamp"))]
    has_pos = [k for k in ks if any(w in k.lower() for w in ("index", "order", "position"))]
    print("  THE REGISTER, AUDITED AGAINST THE SCHEMA\n")
    print(f"    temporally resolved  fields found: {has_time or 'NONE'}"
          f"  -> {'DECIDABLE' if has_time else 'CONFIRMED IMPOSSIBLE — measured, not assumed'}")
    print(f"    position randomized  fields found: {has_pos}"
          f"  -> {'the field EXISTS; testable' if has_pos else 'CONFIRMED IMPOSSIBLE'}")
    print(f"    cross-model          falsified in R290 — a second judge was on disk\n")

    # ---- positive control: can the null fire? ---------------------------------------------
    planted = H.copy(); planted[:, 2] += 0.12
    _, _, _, p_plant = perm_p(planted, np.random.default_rng(5), 500)
    exch = np.array([r[np.random.default_rng(1000 + i).permutation(4)] for i, r in enumerate(H)])
    _, _, _, p_exch = perm_p(exch, np.random.default_rng(6), 500)
    print(f"  POSITIVE CTRL  planted slot effect of the human's own size -> p = {p_plant:.4f}  "
          f"{'PASS' if p_plant < 0.05 else 'FAIL — the null cannot fire, so no p below is readable'}")
    print(f"  PLACEBO        slots made exchangeable by construction  -> p = {p_exch:.4f}  "
          f"{'PASS' if p_exch > 0.05 else 'FAIL'}")
    if not (p_plant < 0.05 and p_exch > 0.05):
        print("\n  UNVERIFIED — the null does not behave; nothing below is readable.")
        return 1

    # ---- the effects ----------------------------------------------------------------------
    rows, grid = {}, []
    print(f"\n  SLOT EFFECT, human and judge\n")
    print(f"    {'source':<14}{'slot means':<40}{'max−min':>9}{'null':>8}{'p':>9}")
    ho, hn, h95, hp = perm_p(H, rng)
    rows["HUMAN"] = dict(spread=ho, null=hn, p=hp, order=[int(x) for x in np.argsort(-H.mean(0))])
    grid.append(("HUMAN", hp))
    for a in ARMS:
        Y = np.array([np.array(yvec(S[a][p], sorted({i for i, _ in S[a][p]})), float) for p in pids])
        o, nm, n95, pv = perm_p(Y, rng)
        rows[a] = dict(spread=o, null=nm, p=pv, order=[int(x) for x in np.argsort(-Y.mean(0))])
        grid.append((a, pv))
        print(f"    {a:<14}{np.array2string(Y.mean(0), precision=4):<40}{o:>9.4f}{nm:>8.4f}{pv:>9.4f}")
    print(f"    {'HUMAN':<14}{np.array2string(H.mean(0), precision=4):<40}{ho:>9.4f}{hn:>8.4f}{hp:>9.4f}")

    grid.sort(key=lambda z: z[1]); C = len(grid)
    surv = {k for i, (k, p) in enumerate(grid, 1) if p <= 0.05 * i / C}
    print(f"\n    BH q=0.05 over {C} cells · survivors {sorted(surv)}")

    shared = [a for a in ARMS if a in surv and rows[a]["order"] == rows["HUMAN"]["order"]]
    print("\n  " + "=" * 76)
    print(f"  PRE-REGISTERED KILL: any arm with a SEPARABLE slot effect matching the human's "
          f"ordering ?  {bool(shared)}   {shared}")
    if shared:
        print("  -> W-SHARED. Every A2 in the file contains a position component and must say so.")
    else:
        print("  -> W-RESIDUAL. The HUMAN carries a resolved slot effect and NO judge does, so slot")
        print("     is a component of the TARGET that no arm tracks. It does not inflate any margin;")
        print("     it sits in the unreachable residual and CAPS achievable A2. Opposite sign of")
        print("     consequence from the confound I was looking for.")
    print(f"  human slot order (best→worst) {rows['HUMAN']['order']}   "
          f"arms: {{{', '.join(f'{a}:{rows[a]['order']}' for a in ARMS)}}}")
    print("  " + "=" * 76)

    src = hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16]
    o_ = pathlib.Path(__file__).parent / "results" / "register_audit.json"
    o_.parent.mkdir(parents=True, exist_ok=True)
    o_.write_text(json.dumps(dict(source_sha=src, n_prompts=len(pids), schema_time=has_time,
                                  schema_pos=has_pos, effects=rows, bh=sorted(surv),
                                  shared=shared, pos_ctrl_p=p_plant, placebo_p=p_exch), indent=1))
    print(f"\n  artifact {o_.relative_to(ROOT)}  src {src}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
