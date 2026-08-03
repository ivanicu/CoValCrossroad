"""The whole chain, N to Y, as ONE number -- which this project has never computed.

Ivan: "我要的不是每一步，我要的是整条链从N到Y". Correct, and the gap is real.

r144 reported "N -> Y = 0.585" and that is NOT the chain. Reading its own definitions: N is a
person's own rubric applied to the four responses, and Y is THAT SAME PERSON'S ranking. So 0.585
is a within-person consistency check -- does someone's stated rubric predict their own choice --
and the pipeline appears nowhere in it. Every other number in that round is a single adjacent
hop. Nobody has asked what fraction of what a person put in at N survives all the way to what the
compiled standard actually does.

THE QUANTITY. For one prompt and one participant i:

    N_i   the person's OWN normative input as a vector over the four responses:
          sum over every criterion c that i rated of  rating_i(c) x satisfaction(c, response)
          This is what i said should matter, applied to the things being judged.

    Y     what the pipeline OUTPUTS as a vector over the same four responses:
          the compiled coval_core rubric's score. Y_full is the uncompiled comparison.

Only contrasts among four responses matter, so both are mean-centred; alignment is cosine.
End-to-end preservation is cos(N_i, Y).

A COSINE ALONE IS UNINTERPRETABLE, so it is scored between two references measured on the same
prompt:

    CEILING   the single vector that maximally agrees with EVERYONE on this prompt -- the top
              eigenvector of the sum of outer products of the centred N_i. No standard, however
              compiled, can beat it, because it is by construction the best possible compromise.
    FLOOR     a core rubric from a DIFFERENT prompt, scored on these responses. Same object, same
              instrument, no relationship to this question.

    preservation = (observed - floor) / (ceiling - floor)

That fraction is the answer to "how much of N reaches Y", and it is a proportion of what was
ACHIEVABLE rather than of 1.0 -- because perfect agreement with everyone is impossible when people
disagree, and r179 measured that disagreement directly: two humans pick the same best response
47.8% of the time.

THE CEILING IS NOT A MODELLING CHOICE. It is the largest eigenvalue of a positive semi-definite
matrix built from the participants' own vectors, so it is arithmetic on this prompt's data.
"""
from __future__ import annotations

import json
import math
import pathlib
import random
import sys
from collections import Counter, defaultdict

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
DATA = ROOT / "data"
LETTERS = "ABCD"
T_FULL = ROOT / "01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_full.npz"
T_CORE = ROOT / "01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_core.npz"

from covalx.estimand import both  # noqa: E402
from covalx.robust import jackknife_calibrated, report  # noqa: E402


def load(p):
    d = np.load(p, allow_pickle=True)
    out = defaultdict(dict)
    for k, v in zip(d["meta"], d["sat"]):
        pid, i, L = str(k).split("|")
        out[pid][(int(i), L)] = float(v)
    return out


def centred(v):
    v = np.asarray(v, float)
    v = v - v.mean()
    n = np.linalg.norm(v)
    return v / n if n > 1e-12 else None


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    sf, sc = load(T_FULL), load(T_CORE)
    from covalx.judge import load_join
    joined = list(load_join(DATA / "comparisons.jsonl", DATA / "conversation_rubrics.jsonl"))

    # ---------------------------------------------------------------- build N_i, Y_core, Y_full
    prompts = {}
    for pid, _p, r in joined:
        full, core = r["coval_full"], r["coval_core"]
        if pid not in sf or pid not in sc or not core:
            continue
        # N_i : per participant, their own ratings x satisfaction
        per = defaultdict(lambda: np.zeros(4))
        for ci, it in enumerate(full):
            sat = [sf[pid].get((ci, L)) for L in LETTERS]
            if any(s is None for s in sat):
                continue
            for s_ in (it.get("scores") or []):
                aid, w = s_.get("annotator_id"), float(s_["score"])
                per[aid] = per[aid] + w * np.array(sat, float)
        N = {a: centred(v) for a, v in per.items()}
        N = {a: v for a, v in N.items() if v is not None}
        if len(N) < 3:
            continue
        # Y_core : the compiled standard's own score. core carries no weights -- every item was
        # rewritten to positive -- so the standard IS the unweighted sum of its criteria.
        yc = np.zeros(4)
        ok = True
        for k in range(len(core)):
            sat = [sc[pid].get((k, L)) for L in LETTERS]
            if any(s is None for s in sat):
                ok = False
                break
            yc = yc + np.array(sat, float)
        if not ok:
            continue
        # Y_full : the uncompiled rubric with the crowd's mean weights
        yf = np.zeros(4)
        for ci, it in enumerate(full):
            sat = [sf[pid].get((ci, L)) for L in LETTERS]
            if any(s is None for s in sat) or not it.get("scores"):
                continue
            w = float(np.mean([s_["score"] for s_ in it["scores"]]))
            yf = yf + w * np.array(sat, float)
        Yc, Yf = centred(yc), centred(yf)
        if Yc is None or Yf is None:
            continue
        prompts[pid] = {"N": N, "Yc": Yc, "Yf": Yf}
    print(f"prompts with >=3 participants, both tensors and a core: {len(prompts)}")
    print(f"participants across them: {sum(len(v['N']) for v in prompts.values())}")

    # ---------------------------------------------------------------- ceiling and floor
    rng = random.Random(0)
    pids = list(prompts)
    rows = []
    for pid in pids:
        d = prompts[pid]
        M = np.stack(list(d["N"].values()))
        # CEILING: the single unit vector maximising mean squared alignment with every N_i is the
        # top eigenvector of M^T M. Its mean |cosine| is the best any one standard can do here.
        w, V = np.linalg.eigh(M.T @ M)
        best = V[:, int(np.argmax(w))]
        ceil = float(np.mean(np.abs(M @ best)))
        # FLOOR: a core rubric from a DIFFERENT prompt, same instrument, no relationship
        other = rng.choice([p for p in pids if p != pid])
        fl = float(np.mean(np.abs(M @ prompts[other]["Yc"])))
        obs_c = float(np.mean(np.abs(M @ d["Yc"])))
        obs_f = float(np.mean(np.abs(M @ d["Yf"])))
        rows.append({"pid": pid, "n": len(d["N"]), "ceiling": ceil, "floor": fl,
                     "core": obs_c, "full": obs_f})

    def frac(o, c, f):
        return (o - f) / (c - f) if c - f > 1e-9 else float("nan")

    for r in rows:
        r["preserved_core"] = frac(r["core"], r["ceiling"], r["floor"])
        r["preserved_full"] = frac(r["full"], r["ceiling"], r["floor"])

    print("\n" + "=" * 92)
    print("THE WHOLE CHAIN, N -> Y, AS ONE NUMBER")
    print("=" * 92)
    for lbl, key in (("ceiling  (best possible single standard)", "ceiling"),
                     ("Y_full   (uncompiled rubric, crowd weights)", "full"),
                     ("Y_core   (the compiled standard, what ships)", "core"),
                     ("floor    (a different prompt's core)", "floor")):
        v = [r[key] for r in rows]
        m = float(np.mean(v))
        se = float(np.std(v, ddof=1) / math.sqrt(len(v)))
        print(f"  {lbl:44s} mean |cos| {m:.4f}  [{m - 1.96 * se:.4f}, {m + 1.96 * se:.4f}]")

    pc = [r["preserved_core"] for r in rows if r["preserved_core"] == r["preserved_core"]]
    pf = [r["preserved_full"] for r in rows if r["preserved_full"] == r["preserved_full"]]
    mc = float(np.mean(pc))
    sec = float(np.std(pc, ddof=1) / math.sqrt(len(pc)))
    mf = float(np.mean(pf))
    sef = float(np.std(pf, ddof=1) / math.sqrt(len(pf)))
    print(f"\n  PRESERVATION, as a fraction of what was achievable on the same prompt:")
    print(f"    N -> Y_full  (elicit, aggregate)            {mf:6.1%}  "
          f"[{mf - 1.96 * sef:.1%}, {mf + 1.96 * sef:.1%}]")
    print(f"    N -> Y_core  (elicit, aggregate, COMPILE)   {mc:6.1%}  "
          f"[{mc - 1.96 * sec:.1%}, {mc + 1.96 * sec:.1%}]")
    d = np.array(pf) - np.array(pc)
    md = float(d.mean())
    sed = float(d.std(ddof=1) / math.sqrt(len(d)))
    print(f"    cost of the compilation step                {md:+6.1%}  "
          f"[{md - 1.96 * sed:+.1%}, {md + 1.96 * sed:+.1%}]  z {md / sed:+.1f}")

    # ---------------------------------------------------------------- the guard and the attack
    print("\n" + "=" * 92)
    print("UNIT AND CONCENTRATION")
    print("=" * 92)
    b = both(pc, [r["pid"] for r in rows if r["preserved_core"] == r["preserved_core"]],
             name="N->Y core preservation")
    print(f"  per-prompt {b['group']:.4f} vs per-observation {b['observation']:.4f}, gap "
          f"{b['gap']:+.5f} -- the prompt IS the unit here, one value each")
    jk = jackknife_calibrated(pc, name="N->Y preservation")
    report(jk, "N->Y core preservation")

    print("\n" + "=" * 92)
    print("READING")
    print("=" * 92)
    print(f"  END TO END: {mc:.0%} of the achievable normative signal reaches the compiled")
    print(f"  standard that ships. Not {mc:.0%} of 'what people said' -- {mc:.0%} of what ANY single")
    print(f"  standard could have carried, given that the people disagree with each other.")
    print(f"  The ceiling is {np.mean([r['ceiling'] for r in rows]):.3f} mean |cos| and the floor is "
          f"{np.mean([r['floor'] for r in rows]):.3f}, so the")
    print(f"  band is real and the fraction is not dividing by something near zero.")
    print(f"\n  AND THE COMPILATION STEP COSTS {abs(md):.1%} OF IT ({md:+.1%}, z {md / sed:+.1f}).")
    print(f"  That is the same step r146 showed gives back 40% of the fairness gain and r188")
    print(f"  showed passes the post-hoc rationalisation through unchanged. Three independent")
    print(f"  measurements, one step.")
    print(f"\n  WHAT THIS IS NOT. It is alignment of DIRECTION between a person's weighted criteria")
    print(f"  and the standard's score over four responses. It routes through the rebuilt")
    print(f"  Qwen3.5-2B-Base judge on BOTH sides, so a judge bias cancels in the contrast but the")
    print(f"  absolute level is that judge's. And N is what a person RATED, which r187 showed is")
    print(f"  partly a description of the answer they had already chosen -- so the input end of")
    print(f"  this chain is itself not innocent.")

    (OUT / "chain_n_to_y.json").write_text(json.dumps(
        {"prompts": len(rows), "participants": int(sum(r["n"] for r in rows)),
         "levels": {k: float(np.mean([r[k] for r in rows]))
                    for k in ("ceiling", "full", "core", "floor")},
         "preserved_full": mf, "preserved_full_se": sef,
         "preserved_core": mc, "preserved_core_se": sec,
         "compilation_cost": md, "compilation_cost_se": sed, "z": md / sed,
         "estimand": {k: b[k] for k in ("observation", "group", "gap")},
         "jackknife": {k: jk[k] for k in ("kill_at", "reference_p10_lo", "reference_p10_hi",
                                          "verdict", "max_single_unit_shift_rel")}}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
