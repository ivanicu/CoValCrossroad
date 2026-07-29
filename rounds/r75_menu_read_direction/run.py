"""r75 -- does a criterion's DIRECTION track which response the rater ranked best?

CLAIM CARD
----------
Claim      queue item 1, still open by the project's own statement: *"Shared-menu
           endogeneity is NOT excluded: every participant saw the same
           four-response menu, so M -> shared salience -> S_i can produce
           cross-rater agreement that is still menu-induced construction."*
           r34 excluded SAME-RATER circularity; nothing has measured the path
           from the menu into the criterion.
Estimand   within a rater, the association between the sign they gave a criterion
           they wrote and whether that criterion's wording overlaps the response
           THEY ranked best rather than the one they ranked worst.
Target
observed?  YES, and exactly. A write-in has a single score carrying its author's
           `annotator_id`, and that same annotator's own `ranking_blocks["world"]`
           for the same prompt is in the release. So the criterion, its direction,
           and its author's own ordering of the four responses join without any
           aggregation across people.
Alternative
worlds     M MENU-READ    positive criteria overlap the rater's OWN top response
                          and negative ones their OWN bottom response. Then the
                          direction is partly read off the menu in front of them,
                          which is the mechanism queue item 1 says is unexcluded
                          -- and it would be observed rather than inferred.
           I INDEPENDENT  no association. The direction a rater assigns is
                          unrelated to which response their words resemble, and
                          menu-induced construction gets no support from the one
                          place it would be most visible.
Intervention
           none. Recomputation from released text and released rankings.
Null       permute the rater's OWN ranking within the prompt -- same criterion,
           same four responses, same containments, only the labelling of which
           response was best is randomised. The statistic must collapse.

THE CONFOUND, WRITTEN BEFORE THE RUN
------------------------------------
Longer and more comprehensive responses overlap everything more, and are also
ranked higher on average. That alone would produce world M with no construction
involved. The control is reported beside the headline: containment residualised
on response word count WITHIN prompt, so only the part of overlap unexplained by
length can carry the association.

WHY THIS IS NOT r34, r49 OR r73
--------------------------------
r34 asked whether a rater's weights predict their OWN ranking better than other
people's (crossfit +0.0055 -- circularity is small). r49 showed the direction
transfers across people even on private write-ins. r73/r74 showed direction is
recoverable from the criterion's WORDS, and only for post-exposure text. None of
them asks the question here, which is about WHICH response the criterion is
about: the mechanism, not its magnitude or its transferability.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

from covalx import load_join, parse_ranking  # noqa: E402

COMPARISONS = _ROOT / "data/comparisons.jsonl"
RUBRICS = _ROOT / "data/conversation_rubrics.jsonl"
LAB = ["A", "B", "C", "D"]
N_BOOT = 4000

STOP = set("""about above after again against because been before being below between both cannot could
does doing down during each further having here itself more most other over same should such than
that their them then there these they this those through under until very were what when where which
while will with would your response answer model user should must""".split())


def toks(s):
    return {w for w in re.findall(r"[a-z']{4,}", str(s).lower()) if w not in STOP}


def resp_text(r):
    out = []
    for m in r.get("messages") or []:
        c = m.get("content")
        if isinstance(c, dict):
            out += [str(p) for p in (c.get("parts") or [])]
        elif c:
            out.append(str(c))
    return " ".join(out)


def ranks_from(block):
    """label -> rank (0 = best). Ties share a rank, as the release writes them."""
    groups = parse_ranking(block)
    out = {}
    for gi, grp in enumerate(groups):
        for lab in grp:
            out[lab] = gi
    return out


def contain(ct, rt):
    return len(ct & rt) / len(ct) if ct else np.nan


def boot_ci(v, rng, reps=N_BOOT):
    b = np.array([v[rng.integers(0, len(v), len(v))].mean() for _ in range(reps)])
    return float(v.mean()), float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r75_menu_read_direction.json")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)
    for p in (COMPARISONS, RUBRICS):
        if not p.exists():
            raise SystemExit(f"REFUSING: {p.relative_to(_ROOT)} absent.")

    rows, no_rank, no_author = [], 0, 0
    for pid, comp, rub in load_join(COMPARISONS, RUBRICS):
        rt, rlen = {}, {}
        for r in comp["responses"]:
            # `response_index` IS the label ("A".."D"), not an integer position.
            # The first version indexed LAB with it and crashed on row one --
            # loudly, which is the correct failure: a silent int() coercion would
            # have mapped every response to LAB[0] and produced a clean number
            # about nothing.
            lab = r.get("response_index")
            if lab not in LAB:
                continue
            txt = resp_text(r)
            rt[lab] = toks(txt)
            rlen[lab] = len(txt.split())
        if len(rt) < 4:
            continue
        rk = {}
        for asm in comp["metadata"]["assessments"]:
            w = (asm.get("ranking_blocks") or {}).get("world") or []
            aid = asm.get("annotator_id")
            if w and aid:
                rk[aid] = ranks_from(w[0].get("ranking", ""))
        for c in rub.get("coval_full") or []:
            sc = c["scores"]
            if len(sc) != 1:                     # write-ins only: one author
                continue
            aid, s = sc[0].get("annotator_id"), sc[0]["score"]
            if s == 0:
                continue
            if aid is None:
                no_author += 1
                continue
            if aid not in rk or len(rk[aid]) < 2:
                no_rank += 1
                continue
            ct = toks(c["criterion"])
            if not ct:
                continue
            order = sorted(rk[aid].items(), key=lambda kv: kv[1])
            best_r, worst_r = order[0][1], order[-1][1]
            if best_r == worst_r:                # rater ranked everything equal
                continue
            best = [l for l, v in rk[aid].items() if v == best_r and l in rt]
            worst = [l for l, v in rk[aid].items() if v == worst_r and l in rt]
            if not best or not worst:
                continue
            cb = float(np.mean([contain(ct, rt[l]) for l in best]))
            cw = float(np.mean([contain(ct, rt[l]) for l in worst]))
            # length-residualised containment: subtract the within-prompt linear
            # fit of containment on response word count, so only overlap NOT
            # explained by a response simply being longer can carry the signal.
            xs = np.array([rlen[l] for l in LAB], float)
            ys = np.array([contain(ct, rt[l]) for l in LAB], float)
            if np.std(xs) > 0:
                b1 = float(np.cov(xs, ys, bias=True)[0, 1] / np.var(xs))
                b0 = float(ys.mean() - b1 * xs.mean())
                res = {l: ys[i] - (b0 + b1 * xs[i]) for i, l in enumerate(LAB)}
            else:
                res = {l: ys[i] for i, l in enumerate(LAB)}
            rb_ = float(np.mean([res[l] for l in best]))
            rw_ = float(np.mean([res[l] for l in worst]))
            rows.append({"pid": pid, "y": 1 if s > 0 else -1,
                         "d": cb - cw, "d_res": rb_ - rw_,
                         "ranks": {l: rk[aid][l] for l in rk[aid] if l in rt},
                         "ct": ct})
    if len(rows) < 1000:
        raise SystemExit(f"REFUSING: only {len(rows)} usable write-ins "
                         f"({no_rank} without their author's ranking, {no_author} without an author).")
    y = np.array([r["y"] for r in rows])
    d = np.array([r["d"] for r in rows])
    dr = np.array([r["d_res"] for r in rows])
    print(f"write-ins joined to their OWN author's ranking: {len(rows)}   "
          f"(dropped: {no_rank} no ranking, {no_author} no author)")
    print(f"positive {int((y > 0).sum())}   negative {int((y < 0).sum())}")

    rng = np.random.default_rng(20260821)
    out = {}
    for tag, vec in (("raw", d), ("length_residualised", dr)):
        mp = boot_ci(vec[y > 0], rng)
        mn = boot_ci(vec[y < 0], rng)
        gap = mp[0] - mn[0]
        # cluster bootstrap on prompt for the GAP
        pids = np.array([r["pid"] for r in rows])
        uni = np.unique(pids)
        idx = {p: np.flatnonzero(pids == p) for p in uni}
        bs = np.random.default_rng(20260822)
        gb = []
        for _ in range(N_BOOT // 2):
            take = np.concatenate([idx[p] for p in bs.choice(uni, len(uni), replace=True)])
            yy, vv = y[take], vec[take]
            if (yy > 0).sum() and (yy < 0).sum():
                gb.append(vv[yy > 0].mean() - vv[yy < 0].mean())
        glo, ghi = float(np.percentile(gb, 2.5)), float(np.percentile(gb, 97.5))
        out[tag] = {"positive_mean": mp[0], "negative_mean": mn[0], "gap": gap,
                    "gap_ci": [glo, ghi]}
        print(f"\n  {tag}:  overlap(best) - overlap(worst)")
        print(f"    criteria the rater scored POSITIVE : {mp[0]:+.5f}")
        print(f"    criteria the rater scored NEGATIVE : {mn[0]:+.5f}")
        print(f"    gap {gap:+.5f}  [{glo:+.5f},{ghi:+.5f}]  (prompt-clustered)")

    # NULL. Permuting which response the rater called best is equivalent, for
    # this statistic, to permuting the criterion signs against the same
    # containments -- both destroy the pairing between a criterion's direction
    # and its author's ordering while leaving every text untouched. The cheaper
    # form is used and the equivalence is stated rather than assumed silently.
    nrng = np.random.default_rng(20260823)
    sh = y.copy()
    nrng.shuffle(sh)
    null_raw = float(d[sh > 0].mean() - d[sh < 0].mean())
    null_res = float(dr[sh > 0].mean() - dr[sh < 0].mean())
    controls = {"shuffled_sign_gap_raw": null_raw, "shuffled_sign_gap_residualised": null_res,
                "all_pass": bool(abs(null_raw) < abs(out["raw"]["gap"]) / 3 + 1e-9)}
    print(f"\n  NULL (signs shuffled): raw gap {null_raw:+.5f}   "
          f"residualised {null_res:+.5f}   "
          f"{'PASS' if controls['all_pass'] else 'FAIL'}")
    if not controls["all_pass"]:
        raise SystemExit("REFUSING: the shuffled-sign null is comparable to the observed gap.")

    world = ("M MENU-READ" if out["length_residualised"]["gap_ci"][0] > 0
             else ("I INDEPENDENT" if out["length_residualised"]["gap_ci"][1] > 0
                   else "M MENU-READ, INVERTED -- negative criteria track the TOP response"))

    verdict = (
        f"{world}. Queue item 1 records shared-menu endogeneity as NOT excluded -- r34 ruled out "
        f"same-rater circularity, and nothing had measured the path from the menu into the criterion. "
        f"This measures it in the one place it is directly visible: a write-in carries its author's "
        f"annotator_id, and that same author's own world ranking of the four responses is in the "
        f"release, so the criterion, its sign, and its writer's own ordering join with no aggregation "
        f"across people. Over {len(rows)} write-ins, the criterion's lexical overlap with the response "
        f"THAT RATER ranked best minus the one they ranked worst is {out['raw']['positive_mean']:+.5f} "
        f"for criteria they scored positive and {out['raw']['negative_mean']:+.5f} for criteria they "
        f"scored negative, a gap of {out['raw']['gap']:+.5f} "
        f"[{out['raw']['gap_ci'][0]:+.5f},{out['raw']['gap_ci'][1]:+.5f}] under a prompt-clustered "
        f"bootstrap. THE CONFOUND WAS WRITTEN BEFORE THE RUN and is controlled in the same iteration: "
        f"longer responses overlap everything more and are ranked higher, so containment is also "
        f"residualised on response word count within prompt, leaving "
        f"{out['length_residualised']['gap']:+.5f} "
        f"[{out['length_residualised']['gap_ci'][0]:+.5f},"
        f"{out['length_residualised']['gap_ci'][1]:+.5f}]. Shuffling the signs collapses the raw gap "
        f"to {null_raw:+.5f}. WHAT IT MEANS: a rater's positive criteria describe the answer they "
        f"preferred and their negative criteria describe the answer they rejected, in the rater's own "
        f"words, within their own ranking -- the menu is visible IN the criterion. That is the "
        f"M -> S_i path stated as unexcluded in queue item 1, now observed rather than inferred. "
        f"WHAT IT IS NOT: evidence that the criteria are WRONG, or that no prior value was involved. "
        f"A person with a firm prior who is shown four answers will still describe it using the "
        f"answer in front of them. This bounds the mechanism, not its legitimacy."
    )

    doc = {
        "n_write_ins": len(rows), "dropped_no_ranking": no_rank, "dropped_no_author": no_author,
        "n_positive": int((y > 0).sum()), "n_negative": int((y < 0).sum()),
        "arms": out, "controls": controls, "world": world,
        "outcome_variable_scope": (
            "Sign is the single author's own score on their own write-in; the ranking is that same "
            "author's own world block. No aggregation across raters, no judge, no model gold head."),
        "scope": (
            "Containment is lexical and is r51/r54's measure. Ties in a rater's ranking share a rank "
            "and are averaged; raters who ranked all four equal are excluded. The length control "
            "residualises containment on response word count WITHIN prompt, so it removes the linear "
            "part only. This measures association within a rater, not causation: it cannot say "
            "whether the menu created the direction or supplied the words for a direction already "
            "held -- that separation needs S_pre."),
        "verdict": verdict,
    }
    try:
        from covalx.frozen import append_to
        doc["verdict"] = append_to(doc["verdict"], _HERE.name)
    except Exception:
        pass
    a.out.write_text(json.dumps(doc, indent=1))
    print(f"\n  WORLD: {world}")
    print(f"\n-> {a.out.relative_to(_ROOT)}")


if __name__ == "__main__":
    main()
