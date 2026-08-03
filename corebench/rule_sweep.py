import sys, pathlib, itertools, collections
import numpy as np
ROOT = pathlib.Path("/home/ivan/research.trustworthy-ai.coval-deep-analysis.build.lg.private.editable")
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT/"corebench"))
from score import load_sat, load_targets, yvec, cls
PAIRS = list(itertools.combinations(range(4), 2))
def a2(c,h): return float(np.mean([c[q]==h[q] for q in range(6)]))
tg,_ = load_targets()
RULES = ["topw_k4","topabs_k4","topwvar_k4","topvar_k4"]
RAND  = [f"random_k4_s{s}" for s in (0,1,2)]
def cells(name):
    S = load_sat(ROOT/"corebench"/"results"/f"sat_{name}.npz"); out={}
    for p in S:
        if p not in tg or len(tg[p])<2: continue
        out[p] = cls(yvec(S[p], sorted({i for i,_ in S[p]})))
    return out
C = {n: cells(n) for n in RULES+RAND}
print("\n  IS IT 'SELECTION', OR IS IT ONE RULE?   k=4, A2, 3 held-out draws x 3 random seeds\n")
print(f"  {'rule':<14}{'A2':>9}{'Δ vs random (mean)':>21}{'min':>9}{'max':>9}  all>0")
rows={}
for r in RULES:
    per, absv = [], []
    for s in (0,1,2):
        rng = np.random.default_rng(900+s); h={}
        for p in C[r]:
            v = tg[p]; h[p] = cls(np.array(v[int(rng.integers(len(v)))][0], float))
        absv.append(np.mean([a2(C[r][p], h[p]) for p in C[r]]))
        for rd in RAND:
            ks = sorted(set(C[r]) & set(C[rd]))
            per.append(np.mean([a2(C[r][p],h[p]) - a2(C[rd][p],h[p]) for p in ks]))
    rows[r]=(np.mean(absv), per)
    print(f"  {r:<14}{np.mean(absv):>9.4f}{np.mean(per):>21.4f}{min(per):>9.4f}{max(per):>9.4f}"
          f"   {all(x>0 for x in per)}")
print(f"\n  rules beating random in ALL 9 cells : "
      f"{[r for r in RULES if all(x>0 for x in rows[r][1])]}")
print(f"  rules failing at least one cell     : "
      f"{[r for r in RULES if not all(x>0 for x in rows[r][1])]}")
print(f"\n  -> 'selection beats random' is true of {sum(1 for r in RULES if all(x>0 for x in rows[r][1]))}"
      f" of {len(RULES)} rules tested.\n")
