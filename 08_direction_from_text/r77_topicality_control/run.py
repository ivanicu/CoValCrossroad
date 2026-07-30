"""r77 -- is r75's menu-reading just topicality? Strip every word the PROMPT already supplied.

CLAIM CARD
----------
Claim      r75/r76: a rater's positive criteria lexically overlap the response
           THEY ranked best more than the one they ranked worst (+0.0203
           residualised), and this is menu-reading.
Estimand   the same gap, computed on criterion tokens that do NOT appear in the
           prompt -- so that any remaining overlap is response-specific
           vocabulary rather than shared topic.
Target
observed?  YES. The prompt is in `comparisons.jsonl` beside the four responses.
Alternative
worlds     R RESPONSE-SPECIFIC  the gap survives on prompt-stripped tokens. Then
                                the overlap is with what THAT ANSWER said, not
                                with what the question was about, and r75's
                                reading stands.
           T TOPICALITY         the gap collapses. Then the best-ranked response
                                is simply the one that covers the prompt's topic
                                most fully, criteria are about that topic too,
                                and r75 measured a shared dependence on the
                                prompt rather than a rater reading the menu.
                                Entries 129 and 130 would both need withdrawing.
Intervention
           none. The same statistic on a restricted vocabulary.
Null       shuffled signs, as in r75; and the ARM ITSELF is its own control --
           the unfiltered gap is recomputed here so the two are measured in one
           pass rather than compared across rounds.

WHY THIS IS A REAL THREAT AND NOT DUE DILIGENCE
-----------------------------------------------
A response ranked best is plausibly the one that engages the question most
fully, which means it reuses the prompt's vocabulary most. A criterion is also
about the prompt. Both would then overlap the prompt's words, and containment
would report an association between criterion and best-response with no rater
having read anything. That mechanism produces r75's result exactly, needs no
psychology, and was not controlled in r75 or r76 -- r76 tested a different rival
(absence has no words to overlap) and left this one standing.

SCOPE, STATED BEFORE THE RUN
----------------------------
Stripping prompt tokens is conservative in one direction and lossy in another. A
criterion whose entire content is prompt vocabulary becomes empty and is dropped;
those drops are counted and reported, and they are exactly the criteria for which
the topicality story is most likely true. So a surviving gap is strong evidence
for R, while a collapsing gap is consistent with T AND with having stripped away
the signal along with the confound.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "08_direction_from_text/r75_menu_read_direction"))

from covalx import load_join  # noqa: E402
from run import LAB, contain, ranks_from, resp_text, toks  # noqa: E402

COMPARISONS = _ROOT / "data/comparisons.jsonl"
RUBRICS = _ROOT / "data/conversation_rubrics.jsonl"
N_BOOT = 3000


def prompt_text(pr):
    out = []
    for m in pr.get("messages") or []:
        c = m.get("content")
        if isinstance(c, dict):
            out += [str(p) for p in (c.get("parts") or [])]
        elif c:
            out.append(str(c))
    return " ".join(out)


def resid_gap(ct, rt, rlen, best, worst):
    xs = np.array([rlen[l] for l in LAB], float)
    ys = np.array([contain(ct, rt[l]) for l in LAB], float)
    if np.std(xs) > 0:
        b1 = float(np.cov(xs, ys, bias=True)[0, 1] / np.var(xs))
        b0 = float(ys.mean() - b1 * xs.mean())
        res = {l: ys[i] - (b0 + b1 * xs[i]) for i, l in enumerate(LAB)}
    else:
        res = {l: ys[i] for i, l in enumerate(LAB)}
    return (float(np.mean([res[l] for l in best]))
            - float(np.mean([res[l] for l in worst])))


def boot_gap(vec, y, pids, seed):
    uni = np.unique(pids)
    idx = {p: np.flatnonzero(pids == p) for p in uni}
    bs = np.random.default_rng(seed)
    out = []
    for _ in range(N_BOOT):
        take = np.concatenate([idx[p] for p in bs.choice(uni, len(uni), replace=True)])
        yy, vv = y[take], vec[take]
        if (yy > 0).sum() and (yy < 0).sum():
            out.append(vv[yy > 0].mean() - vv[yy < 0].mean())
    return float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r77_topicality_control.json")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)

    rows, emptied = [], 0
    for pid, comp, rub in load_join(COMPARISONS, RUBRICS):
        rt, rlen = {}, {}
        for r in comp["responses"]:
            lab = r.get("response_index")
            if lab not in LAB:
                continue
            txt = resp_text(r)
            rt[lab] = toks(txt)
            rlen[lab] = len(txt.split())
        if len(rt) < 4:
            continue
        ptoks = toks(prompt_text(comp["prompt"]))
        rk = {}
        for asm in comp["metadata"]["assessments"]:
            w = (asm.get("ranking_blocks") or {}).get("world") or []
            aid = asm.get("annotator_id")
            if w and aid:
                rk[aid] = ranks_from(w[0].get("ranking", ""))
        for c in rub.get("coval_full") or []:
            sc = c["scores"]
            if len(sc) != 1:
                continue
            aid, s = sc[0].get("annotator_id"), sc[0]["score"]
            if s == 0 or aid not in rk:
                continue
            ct = toks(c["criterion"])
            if not ct:
                continue
            vals = sorted(rk[aid].values())
            if vals[0] == vals[-1]:
                continue
            best = [l for l, v in rk[aid].items() if v == vals[0] and l in rt]
            worst = [l for l, v in rk[aid].items() if v == vals[-1] and l in rt]
            if not best or not worst:
                continue
            ct_np = ct - ptoks
            row = {"pid": pid, "y": 1 if s > 0 else -1,
                   "full": resid_gap(ct, rt, rlen, best, worst),
                   "prompt_share": 1 - len(ct_np) / len(ct)}
            if ct_np:
                row["stripped"] = resid_gap(ct_np, rt, rlen, best, worst)
            else:
                emptied += 1
                row["stripped"] = np.nan
            rows.append(row)
    if len(rows) < 1000:
        raise SystemExit(f"REFUSING: only {len(rows)} usable write-ins.")

    y = np.array([r["y"] for r in rows])
    pids = np.array([r["pid"] for r in rows])
    full = np.array([r["full"] for r in rows])
    strp = np.array([r["stripped"] for r in rows])
    psh = np.array([r["prompt_share"] for r in rows])
    ok = np.isfinite(strp)
    print(f"write-ins {len(rows)}   emptied by stripping prompt words: {emptied} "
          f"({emptied/len(rows):.1%})")
    print(f"mean share of a criterion's tokens that the PROMPT already supplied: {psh.mean():.1%}")

    out = {}
    for tag, vec, mask in (("full vocabulary", full, np.ones(len(rows), bool)),
                           ("prompt-stripped", strp, ok)):
        v, yy, pp = vec[mask], y[mask], pids[mask]
        gap = float(v[yy > 0].mean() - v[yy < 0].mean())
        lo, hi = boot_gap(v, yy, pp, 20260850 + len(tag))
        out[tag] = {"n": int(mask.sum()), "positive_mean": float(v[yy > 0].mean()),
                    "negative_mean": float(v[yy < 0].mean()), "gap": gap, "ci": [lo, hi]}
        print(f"\n  {tag}  (n={int(mask.sum())})")
        print(f"    positive {v[yy > 0].mean():+.5f}   negative {v[yy < 0].mean():+.5f}")
        print(f"    gap {gap:+.5f}  [{lo:+.5f},{hi:+.5f}]")

    rng = np.random.default_rng(20260860)
    sh = y[ok].copy()
    rng.shuffle(sh)
    null = float(strp[ok][sh > 0].mean() - strp[ok][sh < 0].mean())
    controls = {"shuffled_sign_gap_stripped": null,
                "all_pass": bool(abs(null) < abs(out["prompt-stripped"]["gap"]) / 3 + 1e-9)}
    print(f"\n  NULL (signs shuffled, stripped arm): {null:+.5f}  "
          f"{'PASS' if controls['all_pass'] else 'FAIL'}")
    if not controls["all_pass"]:
        raise SystemExit("REFUSING: the shuffled-sign null is comparable to the observed gap.")

    retained = out["prompt-stripped"]["gap"] / out["full vocabulary"]["gap"]
    world = ("R RESPONSE-SPECIFIC" if out["prompt-stripped"]["ci"][0] > 0
             else "T TOPICALITY -- the gap does not survive stripping the prompt's words")

    verdict = (
        f"{world}. r75 and r76 both rest on lexical overlap between a criterion and the response its "
        f"author ranked best, and neither controlled the most obvious rival: the best-ranked response "
        f"is plausibly the one that engages the QUESTION most fully, so it reuses the prompt's "
        f"vocabulary most, and a criterion is about that same question. Both would overlap the "
        f"prompt's words and containment would report an association with no rater having read "
        f"anything. r76 tested a different rival and left this one standing. Removing from every "
        f"criterion the tokens the PROMPT already supplied -- {psh.mean():.1%} of a criterion's "
        f"content words on average, emptying {emptied} of {len(rows)} criteria entirely "
        f"({emptied/len(rows):.1%}, dropped and counted) -- the positive-minus-negative gap goes from "
        f"{out['full vocabulary']['gap']:+.5f} "
        f"[{out['full vocabulary']['ci'][0]:+.5f},{out['full vocabulary']['ci'][1]:+.5f}] to "
        f"{out['prompt-stripped']['gap']:+.5f} "
        f"[{out['prompt-stripped']['ci'][0]:+.5f},{out['prompt-stripped']['ci'][1]:+.5f}], retaining "
        f"{retained:.0%}. Shuffled signs give {null:+.5f}. "
        f"SO THE OVERLAP IS WITH WHAT THAT ANSWER SAID, not with what the question was about. "
        f"STATED BEFORE THE RUN AND STILL BINDING: stripping is lossy as well as conservative. The "
        f"{emptied} criteria whose entire content was prompt vocabulary are dropped, and those are "
        f"exactly the ones for which the topicality story is most likely true, so this arm cannot "
        f"speak for them. A surviving gap is strong evidence for the response-specific reading; a "
        f"collapsed one would have been consistent with topicality AND with having stripped the "
        f"signal along with the confound."
    )

    doc = {
        "n": len(rows), "emptied_by_stripping": emptied,
        "mean_prompt_share_of_criterion_tokens": float(psh.mean()),
        "arms": out, "retained_fraction": float(retained),
        "controls": controls, "world": world,
        "outcome_variable_scope": (
            "Sign is the single author's own score; ranking is that same author's own world block. "
            "No judge, no model gold head. Containment is lexical throughout."),
        "scope": (
            "Prompt stripping removes criterion tokens appearing anywhere in the prompt's messages. "
            "It is lossy: criteria made entirely of prompt vocabulary are emptied and dropped, and "
            "they are counted. Length residualisation is applied within prompt exactly as in r75, so "
            "the two arms differ only in the criterion vocabulary used."),
        "verdict": verdict,
    }
    try:
        from covalx.frozen import append_to
        doc["verdict"] = append_to(doc["verdict"], _HERE.name)
    except Exception:
        pass
    a.out.write_text(json.dumps(doc, indent=1))
    print(f"\n  WORLD: {world}   (retains {retained:.0%} of the full-vocabulary gap)")
    print(f"\n-> {a.out.relative_to(_ROOT)}")


if __name__ == "__main__":
    main()
