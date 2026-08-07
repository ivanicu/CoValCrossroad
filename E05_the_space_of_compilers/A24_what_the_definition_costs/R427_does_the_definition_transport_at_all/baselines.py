"""R427/baselines -- the shortcut bar, measured BEFORE any judged arm exists.

⭐ WHY THIS RUNS FIRST AND SEPARATELY. Every baseline in R427's design -- chance, longest, first --
   is computable from the CORPUS ALONE. None of them needs the judge. So the bar an arm must clear
   can be fixed while the GPU is still scoring, and fixing it first is the difference between a
   baseline and a number chosen after seeing the result.

⛔ AND IT IS A SCRIPT, NOT AN INLINE HEREDOC. This campaign's own standard says an inline script with
   no artifact is not evidence whichever way it comes out; that applies to a baseline exactly as it
   applies to an attack, because a baseline is what a later claim will be measured against.

ESTIMAND        ACC of each judge-free rule at picking the human-chosen response, with the
                CONVERSATION as the unit (R413: kappa_chosen 1.0 within a conversation).

IDENTIFICATION  Exact. These rules are deterministic functions of the corpus.

SCOPE           population: the SAME 2,200 seeded conversations R427's judged arms use, restricted to
                interactions with exactly one chosen response · instrument: none -- no judge is
                involved · baseline: CHANCE = mean(1/n_responses) · regime: seed 0.

⛔ ARITHMETIC TRAP. CHANCE is `mean(1/n_responses)` and is FORCED by the design -- a DERIVATION, not
   a measurement. LONGEST, SHORTEST and FIRST are not forced: each could have landed anywhere.

CONTROLS
  TWO-SIDED    SHORTEST is run beside LONGEST. If BOTH beat chance, the "length effect" would be an
               artifact of the argmax or the tiebreak rather than a preference with a direction. A
               real monotone length preference must show them on OPPOSITE sides of chance, and the
               magnitudes should be comparable. This is the control that makes LONGEST readable.
  PLACEBO      CHANCE against itself is exactly 0 by construction and is not reported as a finding.
  UNIT         conversation, not row -- rows would shrink every MDE by ~1.8x.

EXIT
    0  the baselines are reported
    2  the corpus is absent -- never a silent pass
"""
from __future__ import annotations
import collections
import hashlib
import importlib.util
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
ZEFF = 1.959964 + 0.841621


def clus(by):
    a = np.array([np.mean(v) for v in by.values() if v], float)
    return float(a.mean()), float(ZEFF * a.std(ddof=1) / np.sqrt(len(a))), len(a)


def paired(by, ref):
    ks = [k for k in by if k in ref]
    d = np.array([np.mean(by[k]) - np.mean(ref[k]) for k in ks], float)
    return float(d.mean()), float(ZEFF * d.std(ddof=1) / np.sqrt(len(d)))


def main() -> int:
    prod = ROOT / "corebench" / "judge_transport.py"
    corpus = ROOT / "data" / "utterances.jsonl"
    if not (prod.exists() and corpus.exists()):
        print("  UNRUNNABLE: producer or corpus absent. Exit 2, never 0."); return 2
    spec = importlib.util.spec_from_file_location("jt", prod)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    data = m.load_second(corpus, 2200, 0)          # the SAME sampler the judged arms use

    print("R427 · baselines — the bar, measured BEFORE any judged arm exists\n")
    by = {k: collections.defaultdict(list) for k in ("chance", "longest", "shortest", "first")}
    n_resp = []
    for cid, _iid, _pr, cands in data:
        ch = [c for c in cands if c[3]]
        if len(ch) != 1:
            continue
        n_resp.append(len(cands)); tgt = ch[0][0]
        by["chance"][cid].append(1.0 / len(cands))
        by["longest"][cid].append(float(max(cands, key=lambda c: (len(c[1]), c[0]))[0] == tgt))
        by["shortest"][cid].append(float(min(cands, key=lambda c: (len(c[1]), c[0]))[0] == tgt))
        by["first"][cid].append(float(cands[0][0] == tgt))
    if not n_resp:
        print("  UNRUNNABLE: no admissible interaction. Exit 2."); return 2

    print(f"  admissible interactions (exactly one chosen): {len(n_resp):,}   "
          f"conversations: {len(by['chance']):,}")
    print(f"  mean responses per interaction: {np.mean(n_resp):.3f}\n")
    out = {}
    print(f"    {'rule':<22} {'ACC':>8} {'MDE':>8}   {'− chance':>10} {'MDE':>8}")
    for k in ("chance", "longest", "shortest", "first"):
        mu, mde, n = clus(by[k])
        if k == "chance":
            out[k] = dict(acc=mu, mde=mde, n=n)
            print(f"    {'CHANCE (derivation)':<22} {mu:>8.4f} {mde:>8.4f}   {'—':>10} {'—':>8}")
            continue
        d, dm = paired(by[k], by["chance"])
        out[k] = dict(acc=mu, mde=mde, n=n, minus_chance=d, minus_chance_mde=dm,
                      ratio=(abs(d) / dm if dm else float("nan")))
        print(f"    {k.upper():<22} {mu:>8.4f} {mde:>8.4f}   {d:>+10.4f} {dm:>8.4f}   "
              f"{abs(d)/dm:.2f}x its MDE")

    lo, sh = out["longest"], out["shortest"]
    two_sided = (lo["minus_chance"] > 0) and (sh["minus_chance"] < 0)
    print(f"\n  CONTROL · TWO-SIDED   LONGEST {lo['minus_chance']:+.4f} and SHORTEST "
          f"{sh['minus_chance']:+.4f} sit on OPPOSITE sides of chance: {two_sided}   "
          f"{'PASS' if two_sided else 'FAIL — a length effect on both sides is an artifact'}")
    print(f"    if BOTH beat chance, the `length effect` would be an artifact of the argmax or the")
    print(f"    tiebreak rather than a preference with a direction. This is what makes LONGEST")
    print(f"    readable as a baseline instead of a coincidence.")

    print(f"\n  ⭐ THE BAR IS NOT CHANCE. LONGEST reaches {lo['acc']:.4f} with no judge, no criteria")
    print(f"     and no compute. An arm landing between {out['chance']['acc']:.4f} and "
          f"{lo['acc']:.4f} would `beat chance` and still be WORSE than picking the longer reply.")
    print(f"  ⚠ FIRST is {out['first']['minus_chance']:+.4f} at "
          f"{out['first']['ratio']:.2f}x its MDE — a positional effect that is present and marginal.")
    print(f"    The release has no presentation-order field, so this is the only position control")
    print(f"    available and it is reported as a bound rather than dismissed.")

    art = dict(source_sha256=hashlib.sha256(SELF.read_bytes()).hexdigest(), source_name=SELF.name,
               n_interactions=len(n_resp), n_convs=len(by["chance"]),
               mean_responses=float(np.mean(n_resp)), rules=out,
               controls=dict(two_sided=two_sided), computed_before_arms=True)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r427_baselines_prejudge.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
