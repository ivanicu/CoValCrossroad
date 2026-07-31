"""The last unexamined object: the four response texts themselves.

r152 established that prompts whose menu failed are prompts where everybody else is also unhappy --
shared inadequacy, not dispersed demand -- and that the topic predicts nothing. So whatever makes a
candidate set fail is a property of the candidate set, and the responses are the one object in this
release the audit has never opened.

TWO MECHANISMS, and they call for opposite fixes:

  NO REAL CHOICE   the four responses are near-duplicates of each other. Then the menu offers the
                   appearance of a choice and none of the substance, and someone who wants something
                   else rejects all four because there is effectively only one. The fix is diversity
                   in generation.
  FOUR BAD OPTIONS the responses are genuinely different and all unsatisfactory -- all hedging, all
                   refusing, all thin. The fix is quality, not diversity, and a more varied sample
                   from the same distribution would not help.

Distinguishable: the first predicts inter-response SIMILARITY drives the rejection rate; the second
predicts refusal and hedging markers drive it while similarity does not.

MEASUREMENT IS DETERMINISTIC ARITHMETIC -- TF-IDF cosine over content words, computed here rather
than embedded by a model. That keeps this round in the instrument-free half of the campaign, where
the two claims that have survived every attack already live.

A CONFOUND WRITTEN BEFORE THE RUN. Longer responses share more vocabulary by chance, so similarity
and length are coupled; length is carried as its own feature and the similarity result is only
readable beside it. Multiplicity over the whole feature family, BH at q=0.05, held-out splits.
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import re
import sys
from collections import Counter, defaultdict

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
RANK_MAP = {"A": 0, "B": 1, "C": 2, "D": 3}

WORD = re.compile(r"\b[a-z][a-z'-]{2,}\b")
STOP = frozenset("""the a an and or but if then than that this these those of to in on for with as
by at from is are was were be been being it its their our your my not no do does did have has had
will would should could can may might must about into over under more most less you they we he she
i can't don't isn't""".split())
REFUSAL = re.compile(r"\b(i (can't|cannot|won't|am not able|'m not able)|i'm sorry|i am sorry|"
                     r"unable to (help|assist|provide)|can't help with|not able to provide)\b", re.I)
HEDGE = re.compile(r"\b(it depends|may vary|some (people|experts)|others (may|might)|"
                   r"there is no (single|one)|consult a|professional|generally|typically|often)\b",
                   re.I)


def toks(s: str) -> list[str]:
    return [w for w in WORD.findall(s.lower()) if w not in STOP]


def parse_ranking(txt: str):
    v = np.full(4, np.nan)
    groups = [g.strip() for g in txt.replace(" ", "").split(">") if g.strip()]
    if not groups:
        return None
    for gi, g in enumerate(groups):
        for letter in g.split("="):
            if letter in RANK_MAP:
                v[RANK_MAP[letter]] = -gi
    return v if not np.isnan(v).all() else None


def parse_unacc(blocks):
    blk = blocks.get("unacceptable")
    if blk is None:
        return set(), False
    out = set()
    for b in blk or []:
        for r in b.get("rating", []) or []:
            for letter, idx in RANK_MAP.items():
                if r.strip().startswith(letter):
                    out.add(idx)
    return out, True


def msg_text(m) -> str:
    c = m.get("content")
    if isinstance(c, str):
        return c
    if isinstance(c, dict):
        return " ".join(x for x in (c.get("parts") or []) if isinstance(x, str))
    return ""


def load_responses() -> dict[str, list[str]]:
    """prompt_id -> the four assistant response texts, ordered A..D."""
    out = {}
    with (ROOT / "data" / "comparisons.jsonl").open() as fh:
        for line in fh:
            r = json.loads(line)
            slots: dict[int, str] = {}
            for resp in r.get("responses", []):
                idx = RANK_MAP.get((resp.get("response_index") or "").strip())
                if idx is None:
                    continue
                txt = []
                for m in resp.get("messages", []):
                    role = m.get("role") or (m.get("author") or {}).get("role")
                    if role in ("assistant", None):
                        txt.append(msg_text(m))
                slots[idx] = " ".join(t for t in txt if t)
            if len(slots) == 4:
                out[r["prompt_id"]] = [slots[i] for i in range(4)]
    return out


def load_rates() -> dict[str, float]:
    per: dict[str, list[int]] = defaultdict(list)
    with (ROOT / "data" / "annotators.jsonl").open() as fh:
        for line in fh:
            rec = json.loads(line)
            for a in rec.get("assessments", []):
                u, has = parse_unacc(a.get("ranking_blocks") or {})
                if has:
                    per[a["conversation_id"]].append(int(len(u) == 4))
    return {k: float(np.mean(v)) for k, v in per.items() if len(v) >= 5}


def idf_from(corpus: list[list[str]]) -> dict[str, float]:
    df: Counter[str] = Counter()
    for d in corpus:
        df.update(set(d))
    n = len(corpus)
    return {w: math.log(1 + n / (1 + c)) for w, c in df.items()}


def cosine(a: list[str], b: list[str], idf: dict) -> float:
    ca, cb = Counter(a), Counter(b)
    va = {w: c * idf.get(w, 1.0) for w, c in ca.items()}
    vb = {w: c * idf.get(w, 1.0) for w, c in cb.items()}
    na = math.sqrt(sum(x * x for x in va.values()))
    nb = math.sqrt(sum(x * x for x in vb.values()))
    if na == 0 or nb == 0:
        return float("nan")
    dot = sum(v * vb.get(w, 0.0) for w, v in va.items())
    return dot / (na * nb)


def corr_test(rows, feat, outcome="rate"):
    x = np.array([r[feat] for r in rows], float)
    y = np.array([r[outcome] for r in rows], float)
    m = ~(np.isnan(x) | np.isnan(y))
    x, y = x[m], y[m]
    if len(x) < 30 or x.std() == 0:
        return None
    r = float(np.corrcoef(x, y)[0, 1])
    z = 0.5 * math.log((1 + r) / (1 - r)) if abs(r) < 1 else 0.0
    se = 1 / math.sqrt(len(x) - 3)
    p = 2 * (1 - 0.5 * (1 + math.erf(abs(z / se) / math.sqrt(2))))
    return {"feature": feat, "r": r, "n": len(x), "p": p,
            "ci95": [math.tanh(z - 1.96 * se), math.tanh(z + 1.96 * se)]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--salts", type=int, nargs="+", default=[1, 2, 3, 4, 5])
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    resp = load_responses()
    rates = load_rates()
    common = sorted(set(resp) & set(rates))
    print(f"prompts with four parsed responses {len(resp)}   with a rejection rate {len(rates)}   "
          f"joined {len(common)}")
    if not common:
        print("REFUSING: nothing joined; a table of nothing is not a result.")
        return 2

    corpus = [toks(t) for pid in common for t in resp[pid]]
    idf = idf_from(corpus)
    print(f"vocabulary {len(idf)}   mean response chars "
          f"{np.mean([len(t) for pid in common for t in resp[pid]]):.0f}")

    rows = []
    for pid in common:
        texts = resp[pid]
        tk = [toks(t) for t in texts]
        sims = [cosine(tk[i], tk[j], idf) for i in range(4) for j in range(i + 1, 4)]
        sims = [s for s in sims if not math.isnan(s)]
        lens = [len(t) for t in texts]
        rows.append({
            "pid": pid, "rate": rates[pid],
            "similarity_mean": float(np.mean(sims)) if sims else float("nan"),
            "similarity_max": float(np.max(sims)) if sims else float("nan"),
            "similarity_min": float(np.min(sims)) if sims else float("nan"),
            "length_mean": float(np.mean(lens)),
            "length_spread": float(np.std(lens) / (np.mean(lens) + 1e-9)),
            "refusal_any": float(any(REFUSAL.search(t) for t in texts)),
            "refusal_share": float(np.mean([bool(REFUSAL.search(t)) for t in texts])),
            "hedge_share": float(np.mean([bool(HEDGE.search(t)) for t in texts])),
            "hedge_density": float(np.mean([len(HEDGE.findall(t)) for t in texts])),
        })

    feats = ["similarity_mean", "similarity_max", "similarity_min", "length_mean",
             "length_spread", "refusal_any", "refusal_share", "hedge_share", "hedge_density"]
    res, dropped = [], []
    for f in feats:
        c = corr_test(rows, f)
        (res.append(c) if c else dropped.append(f))
    if dropped:
        print(f"DROPPED as constant or under-covered (named, not silently omitted): {dropped}")
    ps = [c["p"] for c in res]
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    kmax = -1
    for rank_, i in enumerate(order, 1):
        if ps[i] <= 0.05 * rank_ / len(ps):
            kmax = rank_
    for rank_, i in enumerate(order, 1):
        res[i]["bh"] = rank_ <= kmax

    print(f"\ncorrelation with the per-prompt full-rejection RATE ({len(res)} features, BH q=0.05)")
    for c in sorted(res, key=lambda c: c["p"]):
        print(f"  {c['feature']:18s} r={c['r']:+.4f} [{c['ci95'][0]:+.3f},{c['ci95'][1]:+.3f}] "
              f"n={c['n']:4d} p={c['p']:.5f} {'BH' if c['bh'] else ''}")

    survivors = [c["feature"] for c in res if c["bh"]]
    held = {}
    print("\nheld out (disjoint halves):")
    for f in survivors:
        signs = []
        for salt in args.salts:
            a = [r for r in rows if (hash((r["pid"], salt)) & 0xFFFF) % 2 == 0]
            b = [r for r in rows if (hash((r["pid"], salt)) & 0xFFFF) % 2 == 1]
            ca, cb = corr_test(a, f), corr_test(b, f)
            if ca and cb:
                signs.append((ca["r"] > 0) == (cb["r"] > 0))
        held[f] = f"{sum(signs)}/{len(signs)}"
        print(f"  {f:18s} halves agree on sign in {held[f]}")

    sim = next((c for c in res if c["feature"] == "similarity_mean"), None)
    ref = next((c for c in res if c["feature"] == "refusal_share"), None)
    hed = next((c for c in res if c["feature"] == "hedge_share"), None)
    quality = max([c for c in (ref, hed) if c], key=lambda c: abs(c["r"]), default=None)
    # THE VERDICT MUST BE ABLE TO SAY NEITHER. The first version picked whichever of similarity
    # and the quality markers had the larger |r| and named it the mechanism -- with both at 0.03
    # it duly announced "FOUR BAD OPTIONS", which is a label attached to a comparison between two
    # nulls. A decision rule with no NEITHER branch always finds a winner and is not a test.
    se_z = 1 / math.sqrt(len(rows) - 3)
    mde_r = math.tanh(2.8 * se_z)
    verdict = "UNDECIDED"
    if sim and quality:
        print(f"\nsimilarity r={sim['r']:+.4f}   best quality marker "
              f"{quality['feature']} r={quality['r']:+.4f}")
        print(f"MDE at 80% power for n={len(rows)}: |r| = {mde_r:.4f}")
        if not survivors:
            verdict = (f"NEITHER -- no response-text feature survives BH; the largest is "
                       f"|r|={max(abs(c['r']) for c in res):.4f} against an MDE of {mde_r:.4f}, "
                       f"so nothing explains more than about "
                       f"{100 * max(c['r'] ** 2 for c in res):.1f}% of the variance")
        elif abs(sim["r"]) > abs(quality["r"]):
            verdict = "NO REAL CHOICE -- inter-response similarity drives it"
        else:
            verdict = f"FOUR BAD OPTIONS -- {quality['feature']} drives it, not similarity"
        print(f"VERDICT: {verdict}")

    (OUT / "menu_itself.json").write_text(json.dumps({
        "n_prompts": len(common), "vocabulary": len(idf),
        "features": sorted(res, key=lambda c: c["p"]), "dropped": dropped,
        "held_out": held, "verdict": verdict,
        "mde_r_at_80pct": round(mde_r, 4), "n_bh_survivors": len(survivors),
        "largest_abs_r": round(max(abs(c["r"]) for c in res), 4),
        "instrument": "none -- TF-IDF cosine computed here; no model executed",
    }, indent=1, default=float))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
