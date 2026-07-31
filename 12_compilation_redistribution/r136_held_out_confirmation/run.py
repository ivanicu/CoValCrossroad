"""r136 -- every settled headline, re-run on prompts it was never found on.

THE GAP THIS CLOSES
-------------------
The campaign's own standard detector reports `confirmatory` ABSENT in all 128 rounds. Every finding
in this project was discovered and tested on the same 968 prompts. That is not a small omission: a
result found by looking at data and then confirmed on that same data has had exactly one chance to
be wrong, and it already took it.

So: a deterministic split of the prompts into a DISCOVERY half and a CONFIRMATION half, and every
settled headline recomputed on both. The split is by a hash of the prompt id, fixed here, computed
before any number below and independent of every outcome -- so it cannot be tuned, and re-running
this file reproduces the same partition forever.

WHAT IS AND IS NOT BEING CLAIMED
--------------------------------
This is a HELD-OUT check, not an independent replication. Both halves come from one release, one
annotator panel, one judge. A finding that survives here has been shown not to be an artifact of
WHICH PROMPTS were looked at; it has not been shown to transfer to another release, another panel,
or another judge, and nothing here licenses that. The honest name for what this buys is
prompt-level generalisation, and that is the only thing it is reported as.

PRE-REGISTERED PER FINDING (fixed before any half was scored)
-------------------------------------------------------------
CONFIRMED    the confirmation half reproduces the SIGN and its 95% CI contains the discovery half's
             point estimate.
ATTENUATED   same sign, but the discovery point sits outside the confirmation CI -- the effect is
             real and the discovery half overstated its size.
FAILED       the sign flips, or the confirmation CI contains zero when the discovery CI did not.

A finding that FAILS here is not "unlucky". It is a finding that was about which prompts were read.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

from covalx import load_join  # noqa: E402
from covalx.judge import parse_ranking  # noqa: E402
from covalx.stamp import stamp  # noqa: E402

FULL_NPZ = _ROOT / "01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_full.npz"
CORE_NPZ = _ROOT / "01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_core.npz"
COMPARISONS = _ROOT / "data/comparisons.jsonl"
RUBRICS = _ROOT / "data/conversation_rubrics.jsonl"

N_BOOT = 3000
SEEDS = (8101, 4409, 20260730, 31337, 271828)
SPLIT_SALT = "r136-held-out-confirmation"   # default; overridable so the SPLIT ITSELF gets swept


SALT = SPLIT_SALT      # rebound from --salt in main(); a module global so half() stays pure


def half(pid: str) -> int:
    """0 = discovery, 1 = confirmation. A pure function of the id and a salt written before any
    number was computed, so the partition cannot be tuned and always reproduces."""
    h = hashlib.sha256((SALT + "|" + str(pid)).encode()).hexdigest()
    return int(h[:8], 16) % 2


def load_sat(path):
    z = np.load(path, allow_pickle=True)
    d = defaultdict(dict)
    for m, s in zip(z["meta"], z["sat"]):
        pid, ci, lab = str(m).split("|")
        d[pid][(int(ci), lab)] = float(s)
    return d


def norm(s):
    return re.sub(r"\s+", " ", (s or "").strip().lower()).rstrip(" .;:!")


def block_pairs(a, block):
    b = (a.get("ranking_blocks") or {}).get(block) or []
    if not b or not b[0].get("ranking"):
        return []
    t = parse_ranking(b[0]["ranking"])
    return [(x.strip(), y.strip())
            for i in range(len(t)) for j in range(i + 1, len(t)) for x in t[i] for y in t[j]]


def vetoes(a):
    out = set()
    for blk in (a.get("ranking_blocks") or {}).get("unacceptable") or []:
        for s in (blk.get("rating") or []):
            m = re.match(r"\s*([A-D])\b", str(s))
            if m:
                out.add(m.group(1))
    return out


def conc(scores, prs):
    g = t = 0
    for x, y in prs:
        if x in scores and y in scores and scores[x] != scores[y]:
            t += 1
            g += scores[x] > scores[y]
    return g, t


def boot_mean(vals, seed, n=N_BOOT):
    v = np.asarray(vals, float)
    if v.size == 0:
        return None
    rng = np.random.default_rng(seed)
    b = v[rng.integers(0, len(v), size=(n, len(v)))].mean(1)
    return float(v.mean()), float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--salt", default=SPLIT_SALT,
                    help="the partition is a researcher degree of freedom; sweep it")
    ap.add_argument("--out", default=str(_RES / "r136_held_out_confirmation.json"))
    args = ap.parse_args()
    global SALT
    SALT = args.salt
    _RES.mkdir(parents=True, exist_ok=True)
    for p in (FULL_NPZ, CORE_NPZ, COMPARISONS, RUBRICS):
        if not p.exists():
            print(f"REFUSING: missing {p}. Exits 2, never 0.", file=sys.stderr)
            return 2
    SAT_F, SAT_C = load_sat(FULL_NPZ), load_sat(CORE_NPZ)

    ratings, raw = {}, {}
    core_text = {}
    for line in open(RUBRICS):
        r = json.loads(line)
        cid = r["conversation"]["id"]
        core_text[cid] = {norm(it.get("criterion")) for it in (r.get("coval_core") or [])
                          if (it.get("criterion") or "").strip()}
        for i, it in enumerate(r.get("coval_full") or []):
            s = [x["score"] for x in (it.get("scores") or [])]
            if s:
                ratings[(cid, i)] = float(np.mean(s))
                raw[(cid, i)] = (np.asarray(s, float), norm(it.get("criterion")))

    # -------- one pass, collecting every finding's per-unit contributions, tagged by half --------
    F = {k: ([], []) for k in ("polarity", "sign_core", "sign_full_eq", "sign_full_sg",
                               "veto_core", "veto_peer", "individ")}
    contested = ([], [])
    n_prompt = [0, 0]
    for pid, comp, rub in load_join(str(COMPARISONS), str(RUBRICS)):
        if pid not in SAT_F or pid not in SAT_C:
            continue
        H = half(pid)
        n_prompt[H] += 1
        cid = rub["conversation"]["id"]
        labs = sorted({lab for (_ci, lab) in SAT_C[pid]})
        if len(labs) < 2:
            continue

        # --- finding 1: polarity components, within-prompt centred -----------------------------
        P, N_, K = defaultdict(list), defaultdict(list), defaultdict(list)
        for (ci, lab), v in SAT_F[pid].items():
            if ratings.get((cid, ci), 0.0) >= 0:
                P[lab].append(v)
            else:
                N_[lab].append(1.0 - v)
        for (ci, lab), v in SAT_C[pid].items():
            K[lab].append(v)
        ls = sorted(set(P) & set(N_) & set(K))
        if len(ls) >= 4:
            p = np.array([np.mean(P[l]) for l in ls])
            n = np.array([np.mean(N_[l]) for l in ls])
            k = np.array([np.mean(K[l]) for l in ls])
            F["polarity"][H].append((p - p.mean(), n - n.mean(), k - k.mean()))

        # --- finding 2: the three arms' concordance --------------------------------------------
        def arm(sat, sign):
            acc = {l: [] for l in labs}
            for (ci, lab), v in sat.items():
                if lab in acc:
                    neg = sign and ratings.get((cid, ci), 0.0) < 0
                    acc[lab].append(1.0 - v if neg else v)
            return {l: float(np.mean(v)) for l, v in acc.items() if v}
        A = {"core": arm(SAT_C[pid], False), "full_eq": arm(SAT_F[pid], False),
             "full_sg": arm(SAT_F[pid], True)}
        asmts = (comp.get("metadata") or {}).get("assessments") or []
        pooled = [pr for a in asmts for pr in block_pairs(a, "world")]
        for key, nm in (("core", "sign_core"), ("full_eq", "sign_full_eq"),
                        ("full_sg", "sign_full_sg")):
            g, t = conc(A[key], pooled)
            if t:
                F[nm][H].append(g / t)

        # --- finding 4: the veto, arm vs human peer --------------------------------------------
        tops = {k: max(v, key=v.get) for k, v in A.items() if v}
        for a in asmts:
            v = vetoes(a) & set(labs)
            if not v or len(v) >= len(labs):
                continue
            peer = []
            for b in asmts:
                if b is a or b.get("annotator_id") == a.get("annotator_id"):
                    continue
                tb = block_pairs(b, "world")
                if tb:
                    t2 = parse_ranking(((b.get("ranking_blocks") or {}).get("world")
                                        or [{}])[0].get("ranking", ""))
                    if t2 and len(t2[0]) == 1:
                        peer.append(int(t2[0][0].strip() in v))
            if peer and "core" in tops:
                F["veto_core"][H].append(int(tops["core"] in v))
                F["veto_peer"][H].append(float(np.mean(peer)))

        # --- finding 5: own vs stranger weights ------------------------------------------------
        rated = defaultdict(dict)
        for i, it in enumerate(rub.get("coval_full") or []):
            for x in (it.get("scores") or []):
                rated[x["annotator_id"]][i] = float(x["score"])
        M = {ci: np.array([SAT_F[pid].get((ci, l), np.nan) for l in labs])
             for ci in {c for (c, _l) in SAT_F[pid]}}
        for a in asmts:
            aid, mine = a.get("annotator_id"), rated.get(a.get("annotator_id"))
            pw = block_pairs(a, "world")
            if not mine or not pw:
                continue
            for o, d in rated.items():
                if o == aid:
                    continue
                keys = sorted(set(mine) & set(d))
                if len(keys) < 3:
                    continue

                def sc(w):
                    num, den = np.zeros(len(labs)), 0.0
                    for ci in keys:
                        vv = M.get(ci)
                        if vv is None:
                            continue
                        num += w[ci] * np.nan_to_num(vv, nan=0.5)
                        den += abs(w[ci])
                    return None if den == 0 else {l: float(x) for l, x in zip(labs, num / den)}
                s1, s2 = sc(mine), sc(d)
                if s1 and s2:
                    g1, t1 = conc(s1, pw)
                    g2, t2 = conc(s2, pw)
                    if t1 and t2:
                        F["individ"][H].append(g1 / t1 - g2 / t2)
                    break        # one stranger per person-prompt keeps the halves comparable

        # --- finding 3: contested criteria and verbatim retention ------------------------------
        for i, it in enumerate(rub.get("coval_full") or []):
            k = (cid, i)
            if k not in raw:
                continue
            arr, txt = raw[k]
            if len(arr) < 4:
                continue
            frac = min(int((arr > 0).sum()), int((arr < 0).sum())) / len(arr)
            contested[H].append((int(frac >= 0.20), int(txt in core_text.get(cid, set())),
                                 abs(float(arr.mean()))))

    print(f"salt={args.salt!r}  prompts: discovery {n_prompt[0]}, confirmation {n_prompt[1]} "
          f"(deterministic sha256 split on the prompt id)")

    findings = {}

    # 1 --------------------------------------------------------------------------------------
    for H in (0, 1):
        rows = F["polarity"][H]
        if not rows:
            continue
        Pv = np.concatenate([r[0] for r in rows])
        Nv = np.concatenate([r[1] for r in rows])
        Kv = np.concatenate([r[2] for r in rows])
        X = np.column_stack([Pv, Nv, np.ones(len(Pv))])
        b = np.linalg.lstsq(X, Kv, rcond=None)[0]
        rng = np.random.default_rng(SEEDS[0] + H)
        bs = []
        for _ in range(600):
            j = rng.integers(0, len(Pv), len(Pv))
            bb = np.linalg.lstsq(X[j], Kv[j], rcond=None)[0]
            if bb[0] != 0:
                bs.append(bb[1] / bb[0])
        findings.setdefault("polarity_ratio_beta_neg_over_beta_pos", {})[H] = (
            float(b[1] / b[0]), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)))

    # 2 --------------------------------------------------------------------------------------
    for nm, key in (("acc_core", "sign_core"), ("acc_full_equal", "sign_full_eq"),
                    ("acc_full_signed", "sign_full_sg")):
        for H in (0, 1):
            r = boot_mean(F[key][H], SEEDS[1] + H)
            if r:
                findings.setdefault(nm, {})[H] = r

    # 3 --------------------------------------------------------------------------------------
    for H in (0, 1):
        rows = contested[H]
        if len(rows) < 50:
            continue
        c = np.array([r[0] for r in rows], float)
        y = np.array([r[1] for r in rows], float)
        m = np.array([r[2] for r in rows], float)
        X = np.column_stack([np.ones(len(c)), c, (m - m.mean()) / (m.std() or 1)])

        def fit(Xa, ya):
            bb = np.zeros(Xa.shape[1])
            for _ in range(120):
                pp = 1 / (1 + np.exp(-np.clip(Xa @ bb, -30, 30)))
                W = pp * (1 - pp)
                Hm = Xa.T @ (Xa * W[:, None]) + 1e-6 * np.eye(Xa.shape[1])
                bb += np.linalg.solve(Hm, Xa.T @ (ya - pp) - 1e-6 * bb)
            return bb
        b0 = fit(X, y)
        rng = np.random.default_rng(SEEDS[2] + H)
        bs = []
        for _ in range(500):
            j = rng.integers(0, len(y), len(y))
            if 5 < y[j].sum() < len(j):
                bs.append(fit(X[j], y[j])[1])
        findings.setdefault("contested_log_odds_of_verbatim_retention", {})[H] = (
            float(b0[1]), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)))

    # 4 --------------------------------------------------------------------------------------
    for H in (0, 1):
        if F["veto_core"][H]:
            d = np.array(F["veto_core"][H], float) - np.array(F["veto_peer"][H], float)
            r = boot_mean(d, SEEDS[3] + H)
            if r:
                findings.setdefault("veto_core_minus_human_peer", {})[H] = r

    # 5 --------------------------------------------------------------------------------------
    for H in (0, 1):
        r = boot_mean(F["individ"][H], SEEDS[4] + H)
        if r:
            findings.setdefault("own_minus_stranger_weights", {})[H] = r

    print(f"\n  {'finding':<46}{'discovery':>22}{'confirmation':>24}   verdict")
    out = {}
    for nm, hv in findings.items():
        if 0 not in hv or 1 not in hv:
            out[nm] = {"verdict": "NOT-ESTIMABLE-ON-BOTH-HALVES"}
            print(f"  {nm:<46}{'--':>22}{'--':>24}   NOT-ESTIMABLE")
            continue
        (d, dl, dh), (c, cl, ch) = hv[0], hv[1]
        same_sign = (d > 0) == (c > 0)
        contains = cl <= d <= ch
        zero_in_conf = cl <= 0 <= ch
        zero_in_disc = dl <= 0 <= dh
        v = ("FAILED" if (not same_sign) or (zero_in_conf and not zero_in_disc) else
             "CONFIRMED" if contains else "ATTENUATED")
        out[nm] = {"discovery": [d, dl, dh], "confirmation": [c, cl, ch], "verdict": v}
        print(f"  {nm:<46}{d:>+9.4f} [{dl:+.3f},{dh:+.3f}]{c:>+9.4f} [{cl:+.3f},{ch:+.3f}]   {v}")

    vs = [v["verdict"] for v in out.values()]
    n_ok = sum(v == "CONFIRMED" for v in vs)
    n_att = sum(v == "ATTENUATED" for v in vs)
    n_bad = sum(v == "FAILED" for v in vs)
    conclusion = (
        f"The campaign's own standard detector reports `confirmatory` absent in all 128 rounds: "
        f"every finding was discovered and tested on the same {sum(n_prompt)} prompts. This round "
        f"splits them by a sha256 of the prompt id under a salt fixed in source before any number "
        f"was computed -- {n_prompt[0]} discovery, {n_prompt[1]} confirmation -- and recomputes "
        f"every settled headline on both. Of {len(out)} headlines, {n_ok} CONFIRMED (same sign, "
        f"confirmation CI contains the discovery point), {n_att} ATTENUATED (same sign, discovery "
        f"overstated the size), {n_bad} FAILED. "
        + "; ".join(f"{k}: {v['verdict']}" for k, v in out.items())
        + ". WHAT THIS DOES NOT BUY: both halves come from one release, one annotator panel and one "
          "judge, so a surviving finding has been shown not to be an artifact of WHICH PROMPTS were "
          "read, and nothing more. It has not been shown to transfer to another release, panel, or "
          "judge, and the word replication is not available for it.")
    print(f"\n{conclusion}\n")

    Path(args.out).write_text(json.dumps(
        {"salt": args.salt, "n_discovery": n_prompt[0], "n_confirmation": n_prompt[1],
         "findings": out, "n_confirmed": n_ok, "n_attenuated": n_att, "n_failed": n_bad,
         "conclusion": conclusion, **stamp(__file__)}, indent=1, sort_keys=True))
    print(f"-> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
