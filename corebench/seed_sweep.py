import sys, pathlib, itertools, collections
import numpy as np
ROOT = pathlib.Path("/home/ivan/research.trustworthy-ai.coval-deep-analysis.build.lg.private.editable")
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT/"corebench"))
from score import load_sat, load_targets
from compare import per_prompt_hits, paired
tg, _ = load_targets()
KS, SEEDS, HO = [2,3,4,6,8,12], [0,1,2], [0,1,2]
print("\n  RANDOM-SEED SWEEP: is the flat selection margin an artifact of one draw?\n")
print(f"  {'k':>4}{'topw':>9}{'random mean':>13}{'random spread':>15}{'Δ mean':>10}{'Δ min':>9}{'Δ max':>9}  all>0")
rows = {}
for k in KS:
    A = load_sat(ROOT/"corebench"/"results"/f"sat_topw_k{k}.npz")
    ha = [per_prompt_hits(A, tg, s) for s in HO]
    ta = float(np.mean([np.mean(list(h.values())) for h in ha]))
    ds, rs = [], []
    for sd in SEEDS:
        p = ROOT/"corebench"/"results"/f"sat_random_k{k}_s{sd}.npz"
        if not p.exists(): continue
        B = load_sat(p); hb = [per_prompt_hits(B, tg, s) for s in HO]
        rs.append(float(np.mean([np.mean(list(h.values())) for h in hb])))
        d = np.concatenate([np.array([ha[i][q]-hb[i][q] for q in sorted(set(ha[i])&set(hb[i]))])
                            for i in range(len(HO))])
        ds.append(float(d.mean()))
    rows[k] = (ta, rs, ds)
    print(f"  {k:>4}{ta:>9.4f}{np.mean(rs):>13.4f}{max(rs)-min(rs):>15.4f}"
          f"{np.mean(ds):>10.4f}{min(ds):>9.4f}{max(ds):>9.4f}   {all(x>0 for x in ds)}")
allds = [d for _t, _r, ds in rows.values() for d in ds]
print(f"\n  cells: {len(KS)} sizes x {len(SEEDS)} random seeds = {len(allds)}")
print(f"  Δ over ALL cells: mean {np.mean(allds):+.4f}  min {min(allds):+.4f}  max {max(allds):+.4f}")
print(f"  cells with Δ > 0: {sum(1 for d in allds if d>0)}/{len(allds)}")
sp = [max(r)-min(r) for _t, r, _d in rows.values()]
print(f"  random-draw spread within a k: max {max(sp):.4f}  vs the selection margin ~{np.mean(allds):.4f}")
