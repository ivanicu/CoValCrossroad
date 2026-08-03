"""r69 -- r54's predictor reliability, for a quantity r54 itself calls an exact text statistic.

CLAIM CARD
----------
Claim      r54's detection floor is 0.300, computed by applying r67's predictor
           reliability of 0.657 to r54's half-width.
Estimand   the split-half reliability of r54's per-prompt overlap-collapse
           quantity, and the floor that follows.
Target
observed?  YES, and cheaply: r54's predictor is deterministic given the text.
           Its own scope line says so -- "The overlap quantities are exact text
           statistics" -- so the only instability is WHICH criteria enter the
           per-prompt average, which is exactly what a criteria split-half
           measures.
Alternative
worlds     T TRANSFERS      reliability near r67's 0.657, the transfer was
                            harmless, and r54's floor stays at 0.300.
           D DETERMINISTIC  reliability well above it, because r54's quantity
                            contains no judge output at all -- r67 measured
                            spread loss and criterion-space geometry, both JUDGE
                            OUTPUTS, and r54's is a word count. The floor drops
                            and r54's refutation is stronger than the ledger says.
Intervention
           none. Recomputation from released text.
Null       (i) a half against ITSELF must give 1.0;
           (ii) a half against a prompt-shuffled other half must give ~0.
           Both run before any reliability is read.

WHY THIS EXISTS
---------------
Entry 110: r67's 0.657 was measured on spread loss and criterion-space geometry,
and applying it to r40's embedding distance was wrong because that predictor has
no criteria to split. Entry 117 then measured r40 properly at 0.9132, far above
0.657.

**r54 is the same transfer, unchecked.** Its overlap statistic does average over a
prompt's criteria, so unlike r40 it CAN be split -- but it contains no judge
output, so there is no reason its reliability should match a judge-scored
quantity's. Third instance of one move: carrying a number across a boundary
without asking whether the boundary is crossable.

METHOD, following r54 exactly
-----------------------------
Same tokeniser, same stoplist, same `containment`, same join (`covalx.load_join`
over comparisons + rubrics), same donor permutation seed 20260727 over the same
250-item list -- so the donor pairing is the one r54's collapse was computed
against. Only the criteria entering each average change.

A NOTE ON r54's OWN DEFAULT
---------------------------
`E03_the_instrument_was_the_object/A01_can_a_local_judge_be_an_instrument/R54_overlap_transfer/run.py` defaults `--gen` to `a12_response_set.json`,
which has no `prompt_ids` key and would raise KeyError; r54 was run with an
explicit `--gen a12_fresh_generations.json`. This round uses the file r54 was
actually run on, and states the discrepancy rather than silently picking one.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = next(p for p in _HERE.parents if (p / "covalx").is_dir())
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

from covalx import load_join  # noqa: E402

GEN = _ROOT / "E01_the_rubric_was_the_object/A03_is_the_attribution_real_and_against_what_floor/R12_response_set/results/a12_fresh_generations.json"
COMPARISONS = _ROOT / "data/comparisons.jsonl"
RUBRICS = _ROOT / "data/conversation_rubrics.jsonl"
HALF_WIDTH = 0.1336          # r54's published corr CI half-width
REL_OUTCOME = {"optimistic": 0.422, "pessimistic": 0.302}
R67_REL = 0.657              # what the ledger transferred onto this row
N_SPLITS = 200               # r57's own convention; one draw is not a measurement

STOP = set("""about above after again against because been before being below between both cannot could
does doing down during each further having here itself more most other over same should such than
that their them then there these they this those through under until very were what when where which
while will with would your response answer model user should must""".split())


def toks(s):
    return {w for w in re.findall(r"[a-z']{4,}", str(s).lower()) if w not in STOP}


def containment(crits, texts):
    rt = [toks(t) for t in texts]
    out = []
    for c in crits:
        ct = toks(c)
        if ct:
            out.append(float(np.mean([len(ct & r) / len(ct) for r in rt])))
    return float(np.mean(out)) if out else np.nan


def spearman_brown(r, k=2.0):
    return k * r / (1 + (k - 1) * r) if r > -1 else float("nan")


def collapse_for(sel, items, donor, gen):
    """r54's collapse, computed on the criteria subset `sel[k]` for prompt k.

    sel is indexed by position, not by object identity: an earlier version keyed
    the halves by `id(list)`, which is a lookup that silently falls back to the
    FULL criteria set when it misses -- a check that cannot fail (entry 96).
    """
    out = []
    for k, it in enumerate(items):
        o, f = gen["original"][it["i"]], gen["fresh"][it["i"]]
        c_own, c_don = sel[k], sel[int(donor[k])]
        if not c_own or not c_don:
            out.append(np.nan)
            continue
        adv_o = containment(c_own, o) - containment(c_don, o)
        adv_f = containment(c_own, f) - containment(c_don, f)
        out.append(adv_o - adv_f)
    return np.array(out, float)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r69_r54_predictor_reliability.json")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)
    for p in (GEN, COMPARISONS, RUBRICS):
        if not p.exists():
            raise SystemExit(f"REFUSING: {p.relative_to(_ROOT)} absent.")

    gen = json.loads(GEN.read_text())
    gp = {p_: i for i, p_ in enumerate(gen["prompt_ids"])}
    items = []
    for pid, _comp, rub in load_join(COMPARISONS, RUBRICS):
        if pid not in gp:
            continue
        cr = [c["criterion"] for c in (rub.get("coval_core") or [])]
        if cr:
            items.append({"pid": pid, "crits": cr, "i": gp[pid]})
    n = len(items)
    if n < 30:
        raise SystemExit(f"REFUSING: only {n} joined prompts.")
    rng = np.random.default_rng(20260727)      # r54's donor seed, r54's n
    donor = np.array([(i + 1 + rng.integers(0, n - 1)) % n for i in range(n)])

    # Halves, per prompt, keyed by POSITION. The same split is used in the own
    # arm and the donor arm: otherwise the two arms would differ by the split as
    # well as by the criteria, and the correlation would measure the wrong thing.
    #
    # AVERAGED OVER N_SPLITS DRAWS (corrected). The first version of this round
    # drew ONE split and reported 0.3794. r57 averages 200; r70 found that a
    # single draw moved the OUTCOME's reliability from 0.3048 to 0.3911, about
    # 1.5 SD, so a one-draw split-half is one realisation and not a measurement
    # -- the same error as taking four points off one realisation and calling it
    # replication. Both the mean and the across-split spread are reported.
    split = np.random.default_rng(20260729)
    k_lt_4 = sum(1 for it in items if len(it["crits"]) < 4)
    splittable = np.array([len(it["crits"]) >= 4 for it in items])

    def corr_on(x, y, mask):
        m = np.isfinite(x) & np.isfinite(y) & mask
        return float(np.corrcoef(x[m], y[m])[0, 1])

    def draw():
        selA, selB = [], []
        for it in items:
            cs = it["crits"]
            o = split.permutation(len(cs))
            h = len(cs) // 2
            selA.append([cs[i] for i in o[:h]])
            selB.append([cs[i] for i in o[h:2 * h]])
        return (selA, selB, collapse_for(selA, items, donor, gen),
                collapse_for(selB, items, donor, gen))

    all_draws = [draw() for _ in range(N_SPLITS)]
    draws = [(x, y) for _, _, x, y in all_draws]
    selA, selB, cA, cB = all_draws[0]
    ok = np.isfinite(cA) & np.isfinite(cB)

    # ---- controls, before any reliability is read ------------------------
    self_r = float(np.corrcoef(cA[ok], cA[ok])[0, 1])
    sh = cB[ok].copy()
    np.random.default_rng(11).shuffle(sh)
    shuf_r = float(np.corrcoef(cA[ok], sh)[0, 1])
    # POSITIVE CONTROL, and it is the load-bearing one. A low split-half is only
    # evidence about the CRITERIA if the estimator can return a high one at all;
    # otherwise it is silence mistaken for a measurement. So: split the RESPONSES
    # instead, keeping every criterion. Prompt-level response vocabulary is shared
    # between the halves by construction, so a working estimator MUST score high
    # here. Without this, the first reading below -- "the collapse is unstable" --
    # was equally consistent with a broken split, and I had in fact drawn it from
    # a second LOW number before running this.
    pc = np.random.default_rng(20260730)
    pa, pb = [], []
    for it in items:
        o = gen["original"][it["i"]]
        pm = pc.permutation(len(o))
        h = len(o) // 2
        pa.append(containment(it["crits"], [o[j] for j in pm[:h]]))
        pb.append(containment(it["crits"], [o[j] for j in pm[h:2 * h]]))
    pa, pb = np.array(pa, float), np.array(pb, float)
    pok = np.isfinite(pa) & np.isfinite(pb)
    pos_r = float(np.corrcoef(pa[pok], pb[pok])[0, 1])
    pos_sh = pb[pok].copy()
    np.random.default_rng(7).shuffle(pos_sh)
    pos_shuf = float(np.corrcoef(pa[pok], pos_sh)[0, 1])
    print(f"positive control (split RESPONSES, all criteria): {pos_r:+.4f} "
          f"-> Spearman-Brown {spearman_brown(pos_r):.4f}   shuffled {pos_shuf:+.4f}")

    controls = {"self": self_r, "prompt_shuffled": shuf_r,
                "positive_control_response_split": pos_r,
                "positive_control_spearman_brown": spearman_brown(pos_r),
                "positive_control_shuffled": pos_shuf,
                "all_pass": bool(abs(self_r - 1) < 1e-9 and abs(shuf_r) < 0.20
                                 and pos_r > 0.5 and abs(pos_shuf) < 0.20)}
    print(f"joined prompts: {n}   usable pairs: {int(ok.sum())}   K<4: {k_lt_4}")
    print(f"controls: self={self_r:.4f} shuffled={shuf_r:+.4f}  "
          f"{'PASS' if controls['all_pass'] else 'FAIL'}")
    if not controls["all_pass"]:
        raise SystemExit("REFUSING: the split-half estimator fails its own controls.")

    m4 = ok & splittable
    per_split = np.array([corr_on(x, y, splittable) for x, y in draws])
    raw = float(per_split.mean())
    rel = spearman_brown(raw)
    single = corr_on(cA, cB, splittable)
    print(f"across {N_SPLITS} splits: raw mean {raw:+.4f}  sd {per_split.std():.4f}  "
          f"range [{per_split.min():+.4f},{per_split.max():+.4f}]  "
          f"(the single split first published: {single:+.4f})")

    # Is the instability specific to the COLLAPSE (a difference of differences),
    # or does it already sit in the raw containment LEVEL? A difference of four
    # noisy terms would be unstable even if each term were prompt-stable, so this
    # separates "the contrast amplifies noise" from "the criterion axis is noisy".
    lvl_per = []
    for sA, sB, _, _ in all_draws:
        lvlA = np.array([containment(sA[k], gen["original"][it["i"]])
                         for k, it in enumerate(items)], float)
        lvlB = np.array([containment(sB[k], gen["original"][it["i"]])
                         for k, it in enumerate(items)], float)
        lvl_per.append(corr_on(lvlA, lvlB, splittable))
    lvl_raw = float(np.mean(lvl_per))
    lvl_rel = spearman_brown(lvl_raw)
    print(f"raw containment LEVEL, same criteria split: {lvl_raw:+.4f} "
          f"-> Spearman-Brown {lvl_rel:.4f}")
    raw_all = float(np.array([corr_on(x, y, ok) for x, y in draws]).mean())
    rel_all = spearman_brown(raw_all)
    print(f"\nK>=4 only (n={int(m4.sum())}): split-half {raw:+.4f}  Spearman-Brown {rel:.4f}")
    print(f"all joined (n={int(ok.sum())}): split-half {raw_all:+.4f}  "
          f"Spearman-Brown {rel_all:.4f}")
    print(f"r67's transferred reliability: {R67_REL}")

    floors = {tag: {"transferred_0657": HALF_WIDTH / np.sqrt(R67_REL * ro),
                    "measured": HALF_WIDTH / np.sqrt(max(rel, 1e-6) * ro)}
              for tag, ro in REL_OUTCOME.items()}
    print("\nr54's detection floor:")
    for tag, ro in REL_OUTCOME.items():
        f = floors[tag]
        print(f"  rel_outcome={ro:.3f}  transferred {f['transferred_0657']:.3f}"
              f"   measured {f['measured']:.3f}")
    # TWO-SIDED, and it has to be. The first version read
    #   world = "D DETERMINISTIC" if rel > R67_REL + 0.10 else "T TRANSFERS"
    # which labels 0.3794 as "the transfer was harmless" -- a threshold that can
    # only fire upward, so the downward world had no label to land in and would
    # have been reported as agreement. I wrote both worlds ABOVE r67 because I
    # was sure determinism implied high reliability. The third world is the one
    # that happened, and naming it only after seeing it is why it is named here
    # rather than quietly folded into T.
    if rel > R67_REL + 0.10:
        world = "D DETERMINISTIC"
    elif rel < R67_REL - 0.10:
        world = "U UNDER-CREDITED"
    else:
        world = "T TRANSFERS"

    verdict = (
        f"{world}. r54's per-prompt overlap collapse is deterministic given the text -- the round "
        f"calls it an exact text statistic -- and I expected that to mean a HIGH split-half "
        f"reliability, above r67's 0.657. It is {rel:.4f}, materially BELOW it. Splitting each "
        f"prompt's core criteria 2-2 and recomputing r54's own containment on each half, over the "
        f"{int(m4.sum())} prompts with four core criteria: split-half {raw:+.4f}, Spearman-Brown "
        f"{rel:.4f}; over all {int(ok.sum())} joined prompts including the {k_lt_4} with three "
        f"criteria, {rel_all:.4f}. Controls first: a half against itself {self_r:.4f}, against a "
        f"prompt-shuffled half {shuf_r:+.4f}, and -- the load-bearing one -- splitting the RESPONSES "
        f"instead of the criteria returns {spearman_brown(pos_r):.4f}, so the estimator CAN report a "
        f"high reliability and its low value here is a fact about the criteria, not about the "
        f"machinery. I had drawn that conclusion from a second low number before running this "
        f"control, which would have been silence read as a measurement. WHAT I HAD CONFUSED: "
        f"determinism is a property of the INSTRUMENT; reliability here is a property of the "
        f"CRITERIA SAMPLE. A function with zero measurement error still has low split-half "
        f"reliability when a prompt's own criteria disagree about the quantity. And the instability "
        f"is not an artifact of the contrast: the raw containment LEVEL, split the same way, is "
        f"{lvl_rel:.4f} -- already low before any difference is taken, so two criteria from one "
        f"rubric simply do not share much lexical overlap with the same responses. "
        f"CONSEQUENCE FOR THE LEDGER: r54's floor RISES from the "
        f"{floors['pessimistic']['transferred_0657']:.3f} published to "
        f"{floors['pessimistic']['measured']:.3f} at the pessimistic outcome reliability "
        f"({floors['optimistic']['measured']:.3f} at the optimistic), so the row already called the "
        f"ledger's weakest test is weaker still. THE SINGLE RELIABILITY COLUMN IS WRONG IN BOTH "
        f"DIRECTIONS: entry 117 measured r40's predictor at 0.9132, far ABOVE the transferred "
        f"0.657, and this measures r54's at {rel:.4f}, far BELOW it. A ledger-wide reliability is "
        f"not a conservative simplification -- it moved two rows in opposite directions, and only "
        f"measuring each predictor separately can say which way."
    )

    doc = {
        "n_joined": n, "n_usable": int(ok.sum()), "n_splittable_K_ge_4": int(m4.sum()),
        "prompts_K_lt_4": k_lt_4,
        "split_half_r": raw, "spearman_brown": rel,
        "level_split_half_r": lvl_raw, "level_spearman_brown": lvl_rel,
        "split_half_r_all": raw_all, "spearman_brown_all": rel_all,
        "transferred_reliability": R67_REL,
        "half_width_from_r54": HALF_WIDTH,
        "floors": floors, "world": world, "controls": controls,
        "outcome_variable_scope": (
            "This round measures the reliability of r54's PREDICTOR only. The attribution r54 "
            "correlates that predictor against is scored by the r08 model gold head, not by humans "
            "(entry 50, r47), so the floor computed here still has a proxy-world outcome on the "
            "other side. A more reliable predictor does not make the outcome human."),
        "scope": (
            "Split-half over a prompt's core criteria, 2-2, Spearman-Brown corrected to full "
            "length. Both the K>=4 figure and the all-prompts figure are reported; the K<4 prompts "
            "split 1-1 and are counted. The donor permutation uses r54's seed over r54's full "
            "250-item list, so the pairing is unchanged. Deterministic given the text: no judge is "
            "invoked anywhere in this round, which is the entire point. "
            "r54's own --gen default (a12_response_set.json) lacks prompt_ids and would raise "
            "KeyError; this round uses a12_fresh_generations.json, the file r54 was run on."),
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
