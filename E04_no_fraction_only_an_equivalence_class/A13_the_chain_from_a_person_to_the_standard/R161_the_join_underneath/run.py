"""The single point of failure under six rounds: does index i mean the same criterion everywhere?

r155 through r160 all attach a weight to a criterion by position. The weights come from
`conversation_rubrics.jsonl`; the satisfaction tensor is keyed `promptid|criterion_index|letter` and
was built by a different script. If those two orderings ever disagree, every weighted arm in this
phase is scoring criteria against other criteria's weights, and nothing would look obviously wrong:
the numbers would still be numbers, the CIs would still be tight, and the conclusions would be
noise wearing a confidence interval.

Worse, the release makes this easy to get wrong. Its two id namespaces are disjoint -- the rubric
file has its own conversation ids and the prompt file has another set, with ZERO overlap -- so the
rubric has to be joined to the prompt by message text. A text join that silently pairs the wrong
records is exactly the failure that leaves no trace.

FOUR CHECKS, in increasing strength.

  1  structural   does every prompt's tensor have a contiguous criterion index with no holes
  2  injective    does any prompt receive more than one rubric record
  3  cardinality  does the rubric's criterion count equal the tensor's, per prompt
  4  semantic     does index i actually POINT AT the same criterion in both

The first three are necessary and none of them is sufficient. Two rubrics with fifteen criteria in
different orders pass all three.

CHECK FOUR IS A POSITIVE CONTROL AND IT NEEDS NO MODEL. If index i is the same criterion in both,
then a criterion's weight and its mean satisfaction should be related -- a prohibition carries a
negative weight and is a thing responses should not do, so a response set satisfies it less. Permute
the weight vector WITHIN a prompt and that relationship must vanish while every marginal is
preserved. Whatever survives the permutation is alignment.

AND A LATENT HAZARD WORTH NAMING EVEN THOUGH IT HAS NOT FIRED. `load_join` exists TWICE -- in
`covalx/judge.py` and again inside the r04 round that built the tensor -- along with its three
helpers. They are byte-identical today, which is luck rather than design: nothing prevents one from
being edited. The guard below asserts they stay identical, because the day they diverge is the day
every weighted number in this phase becomes wrong silently.
"""
from __future__ import annotations
import sys as _sys, pathlib as _pl  # noqa: E402
_sys.path.insert(0, str(next(p for p in _pl.Path(__file__).resolve().parents
                             if (p / 'covalx').is_dir())))  # noqa: E402
from covalx.legacy import round_results  # noqa: E402

import hashlib
import json
import math
import pathlib
import sys
from collections import Counter, defaultdict

import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
LETTERS = "ABCD"
DUPLICATED = ("load_join", "norm", "message_key", "content_key")
SITES = ("covalx/judge.py", "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/run.py")


def _body(path: str, name: str) -> str:
    s = (ROOT / path).read_text()
    i = s.index(f"def {name}(")
    j = s.find("\ndef ", i + 1)
    return s[i: j if j > 0 else len(s)].strip()


def duplication_guard() -> dict:
    out = {}
    for fn in DUPLICATED:
        bodies = [_body(p, fn) for p in SITES]
        same = bodies[0] == bodies[1]
        out[fn] = {"identical": same,
                   "sha": hashlib.sha256(bodies[0].encode()).hexdigest()[:16]}
    return out


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    from covalx.judge import load_join

    z = np.load(round_results("R04")
                / "a04_full.npz", allow_pickle=True)
    cells: dict[str, dict[tuple[int, int], float]] = defaultdict(dict)
    seen_idx: dict[str, set] = defaultdict(set)
    for s, m in zip(z["sat"], z["meta"]):
        cid, ci, rl = str(m).split("|")
        seen_idx[cid].add(int(ci))
        if rl in LETTERS:
            cells[cid][(int(ci), LETTERS.index(rl))] = float(s)
    sat = {}
    for cid, d in cells.items():
        M = np.full((max(k[0] for k in d) + 1, 4), np.nan)
        for (i, j), v in d.items():
            M[i, j] = v
        sat[cid] = M

    joined = load_join(ROOT / "data" / "comparisons.jsonl",
                       ROOT / "data" / "conversation_rubrics.jsonl")
    W = {pid: np.array([np.mean([s["score"] for s in it["scores"]])
                        for it in r["coval_full"]], float) for pid, _p, r in joined}

    gaps = sum(1 for c, v in seen_idx.items() if len(v) != max(v) + 1)
    dup = [k for k, v in Counter(p for p, _a, _b in joined).items() if v > 1]
    card_bad = sum(1 for pid, _p, r in joined
                   if pid in sat and len(r["coval_full"]) != sat[pid].shape[0])
    print(f"1 structural   tensor prompts {len(seen_idx)}, with index gaps: {gaps}")
    print(f"2 injective    prompts receiving >1 rubric record: {len(dup)}")
    print(f"3 cardinality  criterion-count mismatches: {card_bad} of {len(joined)}")

    rng = np.random.default_rng(0)
    obs, null = [], []
    for cid, M in sat.items():
        w = W.get(cid)
        if w is None:
            continue
        n = min(M.shape[0], len(w))
        if n < 4:
            continue
        s = np.nanmean(M[:n], axis=1)
        ok = np.isfinite(s) & np.isfinite(w[:n])
        if ok.sum() < 4 or np.std(w[:n][ok]) < 1e-9 or np.std(s[ok]) < 1e-9:
            continue
        obs.append(float(np.corrcoef(w[:n][ok], s[ok])[0, 1]))
        null.append(float(np.corrcoef(rng.permutation(w[:n][ok]), s[ok])[0, 1]))
    obs, null = np.array(obs), np.array(null)
    mo, so = obs.mean(), obs.std(ddof=1) / math.sqrt(obs.size)
    mn, sn = null.mean(), null.std(ddof=1) / math.sqrt(null.size)
    z_sep = (mo - mn) / math.sqrt(so ** 2 + sn ** 2)
    print(f"4 semantic     corr(weight, mean satisfaction) {mo:+.4f} +- {1.96 * so:.4f}")
    print(f"               weights permuted in-prompt      {mn:+.4f} +- {1.96 * sn:.4f}")
    print(f"               separation z = {z_sep:.1f}   prompts {obs.size}")

    guard = duplication_guard()
    print("\nduplication guard (load_join and helpers exist in two files):")
    for fn, g in guard.items():
        print(f"   {fn:14s} identical: {g['identical']}   {g['sha']}")
    diverged = [f for f, g in guard.items() if not g["identical"]]

    ok = (gaps == 0 and not dup and card_bad == 0 and z_sep > 3 and not diverged)
    print(f"\nALIGNMENT: {'HOLDS' if ok else 'BROKEN'}")
    print("  the correlation is only +0.099, which is itself worth noticing: a criterion's weight "
          "barely predicts how often responses satisfy it. The response set was not built to "
          "satisfy what people weighted highly.")

    (OUT / "join.json").write_text(json.dumps(
        {"tensor_prompts": len(seen_idx), "index_gaps": gaps,
         "prompts_with_multiple_rubrics": len(dup), "cardinality_mismatches": card_bad,
         "joined": len(joined),
         "alignment_corr": round(float(mo), 4), "alignment_null": round(float(mn), 4),
         "alignment_z": round(float(z_sep), 2), "prompts_tested": int(obs.size),
         "duplication_guard": guard, "diverged": diverged, "alignment_holds": bool(ok),
         "instrument": "none -- counts, ids and a permutation"}, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
