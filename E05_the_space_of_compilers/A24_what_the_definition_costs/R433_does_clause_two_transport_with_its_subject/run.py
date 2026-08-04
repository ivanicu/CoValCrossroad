"""R433 -- clause ②'s SUBJECT, measured on a second release for the first time.

The design, the worlds, the bar and the kill are in PREREGISTRATION.md, committed at fa8eea5 while
the GPU was still generating and BEFORE any arm was scored. This file executes it. Nothing here may
loosen a threshold that file states; if the two disagree, that file wins and this one is the bug.

⛔ THE ONE DESIGN DECISION NOT IN THE PREREGISTRATION, MADE EXPLICIT HERE. The generated arm can
   cover FEWER interactions than the blind arms, because a conversation whose generation failed to
   parse is dropped by the producer. Comparing an arm scored on 7,000 interactions against a
   baseline computed on 7,342 is comparing two populations and calling it a treatment effect. So
   every number below is computed on the INTERSECTION of all loaded arms, and the size of that
   intersection is printed before any accuracy. That is not a threshold change; it is the estimand's
   population, and the preregistration named the population as "the same 2,200-conversation sample".

ESTIMAND    ACC_gen = P(the response the generated core ranks first is the one a human chose),
            on the intersection population, aggregated BY CONVERSATION (R413) and reported under
            both weightings because R430/R431 showed the two differ and bounded that at <=0.0050
            on an excess -- a bound that does not automatically transfer to an accuracy.
BAR         0.5096, the judge-free longest-reply rule. RECOMPUTED here on the intersection rather
            than quoted from R427, because R427's 0.5096 is on ITS population and quoting it across
            a different one is the scope error this campaign has retracted more than any other.
KILL        as written in PREREGISTRATION.md, evaluated only if the three gate conditions hold.

EXIT 0 W-TRANSPORTS · 1 W-LOSES or W-UNRESOLVED · 2 UNVERIFIED / gate fails / UNRUNNABLE
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / "results"
SAT = ROOT / "corebench" / "results"
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"
ZEFF = 1.959964 + 0.841621


def _r429():
    spec = importlib.util.spec_from_file_location(
        "r429", A24 / "R429_is_the_tightest_pair_a_resolved_claim" / "run.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def load_arm(stem):
    p = SAT / f"{stem}.npz"
    if not p.exists():
        return None, None, None
    d = np.load(p, allow_pickle=True)
    meta, sat = d["meta"], d["sat"].astype(np.float64)
    acc = {}
    for key, s in zip(meta, sat):
        conv, inter, resp, _j = str(key).split("|")
        acc.setdefault((conv, inter), {}).setdefault(resp, []).append(s)
    scored = {k: {r: float(np.mean(v)) for r, v in dd.items()} for k, dd in acc.items()}
    prov = json.loads(str(d["provenance"])) if "provenance" in d else {}
    return scored, json.loads(str(d["targets"])), prov


def picks(scored, targets):
    out = {}
    for t in targets:
        key = (t["conv"], t["inter"])
        sc = scored.get(key)
        if not sc:
            continue
        ids = [r["id"] for r in t["resp"] if r["id"] in sc]
        if len(ids) < 2:
            continue
        out[key] = max(sorted(ids), key=lambda r: sc[r])
    return out


def by_conv(hits, weighting, keys=None):
    ks = keys if keys is not None else list(hits)
    if weighting == "CONV":
        v = [float(np.mean(hits[k])) for k in ks if hits[k]]
        return float(np.mean(v)) if v else float("nan")
    flat = [x for k in ks for x in hits[k]]
    return float(np.mean(flat)) if flat else float("nan")


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    pre = HERE / "PREREGISTRATION.md"
    if not pre.exists():
        print("  UNRUNNABLE: the preregistration is absent. A kill that is not on disk before the")
        print("  run is not a kill. Exit 2, never 0."); return 2

    arms = {}
    for name, stem in (("gen", "sat_transport_gen"), ("sham", "sat_transport_gen_sham"),
                       ("generic", "sat_transport_generic")):
        s, t, pv = load_arm(stem)
        if s is None:
            print(f"  UNRUNNABLE: {stem}.npz absent — the judge has not run. Exit 2, never 0.")
            return 2
        arms[name] = (s, t, pv)

    print("R433 · clause ②'s SUBJECT on a second release — executing PREREGISTRATION.md\n")
    pv = arms["gen"][2]
    print(f"  provenance (gen): mode {pv.get('core_mode')} · sets {pv.get('n_criterion_sets')} · "
          f"k {pv.get('n_criteria')} · calls {pv.get('n_calls'):,} · "
          f"sha {str(pv.get('criteria_sha256'))[:12]}")
    if pv.get("core_mode") != "conversation_keyed":
        print("  ⛔ REFUSING: the generated arm is not conversation-keyed. Whatever it measures, it")
        print("  is not clause ②'s subject. Exit 2."); return 2
    if pv.get("criteria_sha256") == arms["sham"][2].get("criteria_sha256"):
        print("  ⛔ REFUSING: the real and sham arms carry the SAME criteria hash — the sham is not")
        print("  a sham. Exit 2."); return 2

    # ⛔ THE STALE-ARTIFACT CHECK, and the pipeline creates the exact window it guards. The core is
    #    regenerated by one job and re-judged by a later one, so between them an OLD .npz sits on
    #    disk beside a NEW core file. Nothing in the filesystem marks the mismatch: the npz is
    #    valid, recent, correctly named, and scored on a population that no longer exists. This
    #    campaign's ledger calls it `determinism read as currency` -- a check that certifies a run
    #    happened without certifying it came from the committed inputs.
    #    The npz's own provenance carries the hash of the criteria it CONSUMED; recomputing that
    #    hash from the core file now on disk and requiring equality closes the window.
    for nm, core_file in (("gen", "core_gen_second.json"), ("sham", "core_gen_second_sham.json")):
        cp = SAT / core_file
        if not cp.exists():
            print(f"  ⛔ REFUSING: {core_file} absent, so the {nm} arm's provenance cannot be"
                  f" checked against its input. Exit 2."); return 2
        core_now = json.loads(cp.read_text())
        want = hashlib.sha256(json.dumps(
            {k: sorted(v) for k, v in sorted(core_now.items())},
            sort_keys=True).encode()).hexdigest()
        have = arms[nm][2].get("criteria_sha256")
        if want != have:
            print(f"  ⛔ REFUSING: the {nm} arm was scored on a DIFFERENT core than the one on disk.")
            print(f"     npz provenance {str(have)[:16]}  vs  {core_file} now {want[:16]}")
            print(f"     A stale artifact beside a fresh input is indistinguishable from a good run")
            print(f"     by every property except this hash. Exit 2."); return 2
    print(f"  provenance cross-check: both arms hash-match the core files on disk")

    # ---- population: the INTERSECTION, printed before any accuracy -----------------------------
    P = {n: picks(arms[n][0], arms[n][1]) for n in arms}
    targ = {(t["conv"], t["inter"]): t for t in arms["generic"][1]}
    chosen, lens = {}, {}
    for k, t in targ.items():
        ch = [r["id"] for r in t["resp"] if r.get("chosen")]
        if ch:
            chosen[k] = ch[0]
            lens[k] = max(t["resp"], key=lambda r: r.get("len", 0))["id"]
    keys = sorted(set.intersection(*[set(P[n]) for n in P]) & set(chosen))
    convs = sorted({k[0] for k in keys})
    print(f"\n  POPULATION (intersection of all arms, before any accuracy)")
    for n in P:
        print(f"    {n:<8} {len(P[n]):>6} interactions")
    print(f"    INTERSECTION {len(keys)} interactions over {len(convs)} conversations")

    # ---- GATE: the three preregistered conditions, before the kill -----------------------------
    core_gen = json.loads((SAT / "core_gen_second.json").read_text()) \
        if (SAT / "core_gen_second.json").exists() else {}
    # ⛔ WAS `/ 2200`, A HARD-CODED SAMPLE SIZE, and the selftest caught it: a fixture with 60
    #    conversations scored parse_rate 60/2200 = 0.027 and every world collapsed to UNVERIFIED.
    #    The same defect fires on any real run at a different `--convs`, and it fires in the
    #    UNFLATTERING direction -- which is why it would have been diagnosed as a bad generator
    #    rather than as a bad denominator. A rate must divide by the population it was drawn from,
    #    and that population is what the judge actually sampled.
    n_sampled = len({k[0] for k in P["generic"]})
    parse_rate = pv.get("n_criterion_sets", 0) / max(n_sampled, 1)
    coverage = len({k[0] for k in keys}) / max(len({k[0] for k in P["generic"]}), 1)

    def hits(name):
        h = {}
        for k in keys:
            h.setdefault(k[0], []).append(1.0 if P[name][k] == chosen[k] else 0.0)
        return h
    H = {n: hits(n) for n in P}
    H["length"] = {}
    for k in keys:
        H["length"].setdefault(k[0], []).append(1.0 if lens[k] == chosen[k] else 0.0)

    acc = {n: {w: by_conv(H[n], w) for w in ("CONV", "INTER")} for n in H}

    # ⛔ AMENDMENT 1 (PREREGISTRATION.md), made before any arm was scored. The gate USED to require
    #    `sham < real`, which PRESUPPOSES A NON-NULL EFFECT -- the ledger's `control fails for its
    #    own reasons`, form ②. selftest.py's LOSES fixture, where the arm genuinely carries nothing,
    #    returned W-FILLER instead of W-LOSES because with gen ~ sham the comparison is a coin flip.
    #    A true null would have been reported as a broken generator half the time.
    #    Two fixes: the sham comparison now carries its own RESOLUTION, and W-FILLER is demoted from
    #    a VETO to a reported diagnostic -- whether the conversation-match is inert does not decide
    #    whether the arm beats the length rule.
    dsh = [float(np.mean(H["sham"][c])) - float(np.mean(H["gen"][c])) for c in convs]
    bsh = []
    for sd in (81, 82, 83):
        r = np.random.default_rng(sd)
        for _ in range(400):
            bsh.append(float(np.mean(np.array(dsh)[r.choice(len(convs), len(convs), replace=True)])))
    mde_sham = float(ZEFF * np.std(bsh))
    sham_above = (acc["sham"]["INTER"] - acc["gen"]["INTER"]) > mde_sham
    gate = (parse_rate >= 0.80) and (coverage >= 0.80)
    print(f"\n  GATE (admissibility only — does the arm exist? See AMENDMENT 1.)")
    print(f"    parse rate  {parse_rate:.4f}  >= 0.80   {'ok' if parse_rate >= 0.80 else '⛔'}")
    print(f"    coverage    {coverage:.4f}  >= 0.80   {'ok' if coverage >= 0.80 else '⛔'}")
    print(f"  DIAGNOSTIC (informs the reading, not the admissibility)")
    print(f"    sham {acc['sham']['INTER']:.4f} vs real {acc['gen']['INTER']:.4f}, gap "
          f"{acc['gen']['INTER']-acc['sham']['INTER']:+.4f} vs its own MDE {mde_sham:.4f} -> "
          f"{'⛔ sham RESOLVEDLY ABOVE real — W-FILLER' if sham_above else 'sham not above real'}")
    # the three-level diagnostic AMENDMENT 1 promised. A single `world` string cannot carry two
    # findings, and squeezing them into one is how a verdict starts asserting what nobody checked.
    gapv = acc["gen"]["INTER"] - acc["sham"]["INTER"]
    sham_verdict = ("W-INVERTED" if sham_above else
                    "W-SPECIFIC" if gapv > mde_sham else "W-NO-MEASURABLE-MATCH")
    print(f"    sham_verdict {sham_verdict}  —  W-SPECIFIC: the conversation-match buys a resolved")
    print(f"    amount · W-NO-MEASURABLE-MATCH: it buys less than {mde_sham:.4f}, a BOUND not a zero")
    print(f"    · W-INVERTED: the wrong conversation's criteria win, which would be a finding about")
    print(f"    the generator and not about clause ②")

    # ---- controls ------------------------------------------------------------------------------
    ok = True
    pl = abs(by_conv(H["gen"], "INTER") - by_conv(H["gen"], "INTER"))
    ok &= (pl == 0.0)
    print(f"\n  PLACEBO   the arm against itself -> {pl:.1e}, must be 0   "
          f"{'PASS' if pl == 0.0 else '⛔ FAIL'}")

    def planted(g, seed):
        rng = np.random.default_rng(seed)
        h = {}
        for k in keys:
            base = 1.0 if P["gen"][k] == chosen[k] else 0.0
            h.setdefault(k[0], []).append(1.0 if (g > 0 and rng.random() < g) else base)
        return h
    sweep = [(g, by_conv(planted(g, 7), "INTER")) for g in (0.0, 0.10, 0.25, 0.50)]
    noop = abs(sweep[0][1] - acc["gen"]["INTER"]) < 1e-12
    rising = all(sweep[i][1] >= sweep[i - 1][1] - 1e-9 for i in range(1, len(sweep)))
    ok &= (noop and rising)
    print(f"  g=0       a no-op plant -> {sweep[0][1]:.4f} vs unplanted {acc['gen']['INTER']:.4f}   "
          f"{'PASS' if noop else '⛔ FAIL'}")
    print(f"  POSITIVE  dose sweep: " + " · ".join(f"g={g:.2f} {v:.4f}" for g, v in sweep) +
          f"   {'PASS' if rising else '⛔ FAIL'}")

    # ---- the paired comparison against the BAR, recomputed on THIS population ------------------
    print(f"\n  {'arm':<10}{'CONV':>9}{'INTER':>9}   (the bar is recomputed here, not quoted)")
    for n in ("gen", "sham", "generic", "length"):
        print(f"  {n:<10}{acc[n]['CONV']:>9.4f}{acc[n]['INTER']:>9.4f}")

    cells = {}
    for w in ("CONV", "INTER"):
        d = []
        for c in convs:
            g = H["gen"][c]; l = H["length"][c]
            d.append(float(np.mean(g)) - float(np.mean(l)) if w == "CONV" else (sum(g), sum(l), len(g)))
        if w == "CONV":
            arr = np.array(d)
            point = float(arr.mean())
        else:
            G = sum(x[0] for x in d); L = sum(x[1] for x in d); C = sum(x[2] for x in d)
            point = (G - L) / C
        bs = []
        for sd in (71, 72, 73):
            rng = np.random.default_rng(sd)
            for _ in range(400):
                take = rng.choice(len(convs), len(convs), replace=True)
                if w == "CONV":
                    bs.append(float(np.mean(np.array(d)[take])))
                else:
                    sel = [d[i] for i in take]
                    bs.append((sum(x[0] for x in sel) - sum(x[1] for x in sel))
                              / max(sum(x[2] for x in sel), 1))
        bs = np.array(bs)
        lo, hi = np.percentile(bs, [2.5, 97.5])
        mde = float(ZEFF * bs.std())
        cells[w] = {"delta_vs_length": point, "lo": float(lo), "hi": float(hi), "mde": mde,
                    "resolved": bool(abs(point) > mde),
                    "gen": acc["gen"][w], "length": acc["length"][w],
                    "generic": acc["generic"][w], "sham": acc["sham"][w],
                    "neutral_gap": acc["gen"][w] - acc["generic"][w],
                    "sham_gap": acc["gen"][w] - acc["sham"][w]}
        c = cells[w]
        print(f"\n  {w}: gen - length = {point:+.4f} [{lo:+.4f},{hi:+.4f}] vs own MDE {mde:.4f}"
              f"  -> {'RESOLVED' if c['resolved'] else 'inside the floor'}")
        print(f"       NEUTRAL gap (gen - generic) {c['neutral_gap']:+.4f}  — isolates BENEFIT")
        print(f"       SHAM    gap (gen - sham)    {c['sham_gap']:+.4f}  — bounds benefit + HARM, "
              f"and must never be quoted as the value of the ingredient")

    # ---- the conditional kill ------------------------------------------------------------------
    if not gate or not ok:
        world = "UNVERIFIED"
    elif sham_above:
        world = "W-FILLER"
    else:
        pt = cells["INTER"]["delta_vs_length"]; md = cells["INTER"]["mde"]
        world = ("W-TRANSPORTS" if pt > md else "W-LOSES" if pt < -md else "W-UNRESOLVED")
    print(f"\n  WORLD: {world}")
    if world == "W-TRANSPORTS":
        print("    clause ② holds on a second release WITH ITS SUBJECT PRESENT: a core generated")
        print("    from the conversation alone beats the judge-free length rule by more than the")
        print("    design's own resolution. The transport row becomes a measured result.")
    elif world == "W-LOSES":
        print("    ⛔ clause ② does NOT transport even with its subject present. A prompt-specific")
        print("    core generated from the conversation alone loses to a length heuristic, so the")
        print("    clause is DESCRIPTIVE of what CoVal did rather than a licence, and the")
        print("    definition owes a scope line naming the release it holds on.")
    elif world == "W-UNRESOLVED":
        print("    the design cannot separate them. Report the BOUND and the MDE, never a point —")
        print("    correcting a magnitude does not license a point estimate.")
    elif world == "W-FILLER":
        print("    ⛔ the wrong-conversation sham matches the real arm. 'Prompt-specific' criteria")
        print("    are generic text that happens to be generated per conversation. This is a")
        print("    finding about the GENERATOR and it voids the other three worlds.")
    else:
        print("    a control or a gate condition failed; the kill is NOT evaluated.")

    (RES / "r433_clause2_subject.json").write_text(json.dumps(
        {"source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
         "world": world, "gate": {"parse_rate": parse_rate, "coverage": coverage,
                                  "sham_above_resolved": bool(sham_above), "mde_sham": mde_sham,
                                  "passed": bool(gate)},
         "controls_ok": bool(ok), "acc": acc, "cells": cells,
         "sham_verdict": sham_verdict, "sham_gap": gapv,
         "n_interactions": len(keys), "n_conversations": len(convs),
         "dose_sweep": [{"g": g, "acc": v} for g, v in sweep],
         "provenance_gen": pv, "provenance_sham": arms["sham"][2]}, indent=1))
    print(f"\n  artifact -> {(RES / 'r433_clause2_subject.json').relative_to(ROOT)}")
    return 0 if world == "W-TRANSPORTS" else (2 if world in ("UNVERIFIED", "W-FILLER") else 1)


if __name__ == "__main__":
    sys.exit(main())
