"""EXPLORATORY PROBE, not a round. Does the SIGN of the rubric's criteria explain why sixteen
generic sentences beat the conversation's own rubric at matched k and matched access?

Sum-of-satisfaction has no sign: a criterion the humans weighted -10 adds exactly like a +10 one.
The generic 16 are all positively oriented. If that is the mechanism, restricting S1 to its
POSITIVELY weighted criteria should close Delta_source at A0 and A1."""
import itertools, json, sys, pathlib
import numpy as np
ROOT = pathlib.Path(".").resolve()
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, cls, L
from covalx.judge import load_join
PR = list(itertools.combinations(range(4), 2)); RES = ROOT / "corebench/results"

tg, _ = load_targets()
rub = {}
for pid, _p, r in load_join(ROOT/"data/comparisons.jsonl", ROOT/"data/conversation_rubrics.jsonl"):
    it = r.get("coval_full") or []
    rub[pid] = ([x["criterion"] for x in it],
                [float(np.mean([s["score"] for s in (x.get("scores") or [])])) if x.get("scores") else 0.0 for x in it])
FULL, POOL = load_sat(RES/"sat_full.npz"), load_sat(RES/"sat_genericpool16.npz")
pids = sorted(set(FULL)&set(POOL)&set(rub)&{p for p in tg if len(tg[p])>=2})
H0 = {p: np.array([cls(np.array(t[0],float)) for i,t in enumerate(tg[p]) if i%2==0]) for p in pids}
pids = [p for p in pids if len(H0[p])>=1 and len(rub[p][0])>=8]
def mat(sat,p,n): return np.array([[sat[p].get((i,x),0.0) for x in L] for i in range(n)],float)
S1={p:mat(FULL,p,len(rub[p][0])) for p in pids}; S2={p:mat(POOL,p,16) for p in pids}
W={p:np.array(rub[p][1],float) for p in pids}
def ag(C,p,idx):
    y=C[list(idx)].sum(0); c=np.sign(y[[u for u,_ in PR]]-y[[w for _,w in PR]])
    return float((H0[p]==c).mean())

neg = np.array([float((W[p]<0).mean()) for p in pids])
print(f"  {len(pids)} prompts · share of rubric criteria with NEGATIVE mean human weight: "
      f"{neg.mean():.3f} (median {np.median(neg):.3f}, prompts with >=1 negative: {(neg>0).mean():.3f})")

K=4
def randcell(C_of, cand_of, seeds=(0,1,2,3,4)):
    vs=[]
    for s in seeds:
        v=[]
        for p in pids:
            c=cand_of(p)
            if len(c)<K: continue
            r=np.random.default_rng(abs(hash(p))%1000+s*7919 if False else int.from_bytes(p.encode()[:4],'big')+s)
            v.append(ag(C_of(p),p,r.choice(c,K,replace=False)))
        vs.append(np.mean(v))
    return float(np.mean(vs)), len(v)

allc  = lambda p: np.arange(S1[p].shape[0])
posc  = lambda p: np.where(W[p]>0)[0]
negc  = lambda p: np.where(W[p]<0)[0]
a_all,n1 = randcell(lambda p:S1[p], allc)
a_pos,n2 = randcell(lambda p:S1[p], posc)
a_s2 ,n3 = randcell(lambda p:S2[p], lambda p: np.arange(16))
print(f"\n  A0 (random k=4), matched rule, matched k:")
print(f"     S1 ALL rubric criteria      {a_all:.6f}   (n={n1})")
print(f"     S1 POSITIVE-weight only     {a_pos:.6f}   (n={n2})   Δ vs ALL {a_pos-a_all:+.6f}")
print(f"     S2 generic 16               {a_s2:.6f}   (n={n3})   Δ_source now {a_pos-a_s2:+.6f}")
# the sharpest form: flip the sign of negative-weight criteria instead of dropping them
def signed(p):
    C=S1[p].copy(); C[W[p]<0]*=-1.0; return C
a_flip,_ = randcell(signed, allc)
print(f"     S1 with NEGATIVE criteria SIGN-FLIPPED  {a_flip:.6f}   Δ vs ALL {a_flip-a_all:+.6f}"
      f"   Δ_source now {a_flip-a_s2:+.6f}")
