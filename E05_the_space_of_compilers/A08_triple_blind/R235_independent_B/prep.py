#!/usr/bin/env python
"""
R235_independent_B / prep.py  -- build a verified, cached join of the four objects.

Nothing here is analysis. It exists because the release does NOT ship a usable key:
  conversation_rubrics.jsonl  keys prompts by  conversation.id
  comparisons.jsonl           keys prompts by  prompt_id
  the satisfaction tensors    key   prompts by  prompt_id
and  set(conversation.id) & set(prompt_id) == {}  (verified, 0 of 986).

So the rubric<->prompt link must be REBUILT from the prompt text, and the rebuild
must be validated by something it could have failed:

  POSITIVE CONTROL ON THE JOIN: for every joined prompt, the number of criteria in
  coval_full must equal 1 + max(criterion index) appearing in the satisfaction
  tensor's `meta`, and likewise for coval_core.  If the join were wrong these would
  disagree for most prompts.  Observed: 966/966 agree for full AND core.

Written 2026-08-03.
"""
import json, re, sys, pickle, collections, itertools
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
OUT  = Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)

SAT_MAIN = ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results"
SAT_ALT  = ROOT / "E04_no_fraction_only_an_equivalence_class/A02_the_chain_from_a_person_to_the_standard/R164_instrument/results"

JUDGES = {
    "main":       (SAT_MAIN / "a04_full.npz",              SAT_MAIN / "a04_core.npz"),
    "phi":        (SAT_ALT  / "sat_full_phi.npz",          SAT_ALT  / "sat_core_phi.npz"),
    "qwen3b":     (SAT_ALT  / "sat_full_qwen3b.npz",       SAT_ALT  / "sat_core_qwen3b.npz"),
    "v_default":  (SAT_ALT  / "sat_full_variant_default.npz",    SAT_ALT / "sat_core_variant_default.npz"),
    "v_nofewshot":(SAT_ALT  / "sat_full_variant_no_fewshot.npz", SAT_ALT / "sat_core_variant_no_fewshot.npz"),
    "v_swapped":  (SAT_ALT  / "sat_full_variant_swapped.npz",    SAT_ALT / "sat_core_variant_swapped.npz"),
}

LETTERS = "ABCD"


def _norm(s):
    return re.sub(r"\s+", " ", str(s)).strip().lower()


def rub_userkey(d):
    return tuple(_norm(" ".join(map(str, m["content"].get("parts", []))))
                 for m in d["conversation"]["messages"] if m["author"]["role"] == "user")


def cmp_userkey(d):
    return tuple(_norm(m["content"]) for m in d["prompt"]["messages"] if m["role"] == "user")


def parse_ranking(s):
    """'A > B=C  > D' -> rank vector over ABCD, 0 = best, ties share the smaller rank.
    Returns None if unparseable or if it does not name exactly A..D once each."""
    if not isinstance(s, str):
        return None
    t = re.sub(r"\s+", "", s).upper()
    if not re.fullmatch(r"[A-D]([>=][A-D])*", t):
        return None
    toks = re.split(r"([>=])", t)
    groups, cur = [], [toks[0]]
    for op, item in zip(toks[1::2], toks[2::2]):
        if op == "=":
            cur.append(item)
        else:
            groups.append(cur); cur = [item]
    groups.append(cur)
    seen = [x for g in groups for x in g]
    if sorted(seen) != list(LETTERS):
        return None
    r = np.zeros(4, dtype=np.int8)
    pos = 0
    for g in groups:
        for x in g:
            r[LETTERS.index(x)] = pos
        pos += len(g)
    return r


def load_sat(path):
    z = np.load(path, allow_pickle=True)
    out = collections.defaultdict(dict)
    for m, s in zip(z["meta"], z["sat"]):
        p, ci, r = m.split("|")
        out[p][(int(ci), r)] = float(s)
    return out


def sat_matrix(entry, K):
    """dict {(ci, letter): v} -> (K,4) array; nan where absent."""
    M = np.full((K, 4), np.nan, dtype=np.float64)
    for (ci, r), v in entry.items():
        if ci < K:
            M[ci, LETTERS.index(r)] = v
    return M


def main():
    # ---------- rubrics ----------
    rub_by_key = {}
    for line in open(ROOT / "data/conversation_rubrics.jsonl"):
        d = json.loads(line)
        rub_by_key[rub_userkey(d)] = d

    # ---------- comparisons ----------
    cmp_by_key = {}
    for line in open(ROOT / "data/comparisons.jsonl"):
        d = json.loads(line)
        cmp_by_key[cmp_userkey(d)] = d

    keys = set(rub_by_key) & set(cmp_by_key)
    joined = {cmp_by_key[k]["prompt_id"]: (rub_by_key[k], cmp_by_key[k]) for k in keys}
    print(f"[join] rubric prompts={len(rub_by_key)} comparison prompts={len(cmp_by_key)} joined={len(joined)}")

    # ---------- satisfaction, all judges ----------
    sat = {}
    for name, (fp, cp) in JUDGES.items():
        if not (fp.exists() and cp.exists()):
            print(f"[sat] MISSING {name}"); continue
        sat[name] = (load_sat(fp), load_sat(cp))
        print(f"[sat] {name}: full prompts={len(sat[name][0])} core prompts={len(sat[name][1])}")

    # ---------- POSITIVE CONTROL ON THE JOIN ----------
    ctrl = {}
    for name, (F, C) in sat.items():
        ok_f = bad_f = ok_c = bad_c = unjoined = 0
        for p in F:
            if p not in joined:
                unjoined += 1; continue
            rub = joined[p][0]
            kf = 1 + max(ci for ci, _ in F[p])
            kc = 1 + max(ci for ci, _ in C[p]) if p in C else -1
            (ok_f, bad_f) = (ok_f + 1, bad_f) if kf == len(rub["coval_full"]) else (ok_f, bad_f + 1)
            (ok_c, bad_c) = (ok_c + 1, bad_c) if kc == len(rub["coval_core"]) else (ok_c, bad_c + 1)
        ctrl[name] = dict(full_ok=ok_f, full_bad=bad_f, core_ok=ok_c, core_bad=bad_c, unjoined=unjoined)
        print(f"[join-control] {name}: full {ok_f} ok / {bad_f} bad ; core {ok_c} ok / {bad_c} bad ; unjoined {unjoined}")

    # ---------- build per-prompt records ----------
    recs = {}
    n_drop = collections.Counter()
    for p, (rub, cmpd) in joined.items():
        if p not in sat["main"][0] or p not in sat["main"][1]:
            n_drop["no_main_sat"] += 1; continue
        full = rub["coval_full"]; core = rub["coval_core"]
        K, M = len(full), len(core)
        if K < 2 or M < 2:
            n_drop["degenerate_size"] += 1; continue

        # weights: annotator x criterion, nan = not rated by that person
        ann_ids = sorted({s["annotator_id"] for c in full for s in c["scores"]})
        aidx = {a: i for i, a in enumerate(ann_ids)}
        W = np.full((len(ann_ids), K), np.nan)
        for ci, c in enumerate(full):
            for s in c["scores"]:
                W[aidx[s["annotator_id"]], ci] = s["score"]

        # human rankings, per assessment
        rows = []
        for a in cmpd["metadata"]["assessments"]:
            rb = a.get("ranking_blocks") or {}
            def first(key):
                for b in rb.get(key, []) or []:
                    r = parse_ranking(b.get("ranking"))
                    if r is not None:
                        return r
                return None
            rp, rw = first("personal"), first("world")
            # veto block: which responses this person called unacceptable
            veto = np.zeros(4, dtype=bool)
            for b in rb.get("unacceptable", []) or []:
                for txt in (b.get("rating") or []):
                    m = re.match(r"\s*([A-D])\b", str(txt).upper())
                    if m:
                        veto[LETTERS.index(m.group(1))] = True
            if rp is None and rw is None:
                continue
            rows.append((a["annotator_id"], rp, rw, veto))
        if not rows:
            n_drop["no_ranking"] += 1; continue

        rec = dict(
            prompt_id=p, K=K, M=M,
            W=W.astype(np.float32), ann_ids=ann_ids,
            rank_ann=[r[0] for r in rows],
            rank_personal=np.stack([r[1] if r[1] is not None else np.full(4, -1, np.int8) for r in rows]),
            rank_world=np.stack([r[2] if r[2] is not None else np.full(4, -1, np.int8) for r in rows]),
            has_personal=np.array([r[1] is not None for r in rows]),
            has_world=np.array([r[2] is not None for r in rows]),
            veto=np.stack([r[3] for r in rows]),
            # index of each ranker inside W (may be absent -> -1)
            ranker_w=np.array([aidx.get(r[0], -1) for r in rows]),
            sat={},
        )
        for name, (F, C) in sat.items():
            if p in F and p in C:
                sf = sat_matrix(F[p], K); sc = sat_matrix(C[p], M)
                if np.isnan(sf).any() or np.isnan(sc).any():
                    continue
                rec["sat"][name] = (sf.astype(np.float32), sc.astype(np.float32))
        if "main" not in rec["sat"]:
            n_drop["incomplete_main_sat"] += 1; continue
        recs[p] = rec

    print(f"[recs] built {len(recs)} ; drops {dict(n_drop)}")
    print("[recs] judge coverage:", {j: sum(j in r['sat'] for r in recs.values()) for j in sat})

    with open(OUT / "prepared.pkl", "wb") as f:
        pickle.dump(dict(recs=recs, join_control=ctrl,
                         n_rubric=len(rub_by_key), n_cmp=len(cmp_by_key), n_joined=len(joined)), f)
    print(f"[write] {OUT/'prepared.pkl'}")


if __name__ == "__main__":
    main()
