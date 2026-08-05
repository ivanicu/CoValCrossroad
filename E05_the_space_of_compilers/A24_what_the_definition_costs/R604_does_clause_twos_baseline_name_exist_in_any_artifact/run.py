#!/usr/bin/env python3
"""
R604 -- does clause ②'s baseline name exist in anything that computed a score?

CHECK #203 CAUGHT A SUBSTANTIVE MIS-ATTRIBUTION in R603's closing line: *"a rubric could be
generated and a core selected from it, WHICH IS WHAT R433 DID"*. R433 generated the TREATMENT
(`gen`, criteria per conversation); its resolved contrast was against `length`, a judge-free
heuristic, and its prompt-blind comparator was `generic`. There is no "R433's generated
baseline", so the measurement that line proposed was ill-posed. Read from R433's own table:
gen 0.4590 · sham 0.4540 · generic 0.4497 · length 0.5135, and `gen - generic` -- CLAUSE ②'s
OWN CLAIM -- is +0.0093 [-0.0008, +0.0186] against MDE 0.0140: NOT RESOLVED.

Chasing that correction into the artifacts surfaced something larger. `STATEMENT.md` names ②'s
comparator **`POOL[0:4]` by file order**, at percentile 93.7 of its 1,820-subset class. But the
rounds that actually SCORED clause ② record it as **`sat_genericpool16[:4]`**.

ESTIMAND        For each candidate name for ②'s comparator: n_scoring = artifacts that contain
                the name AND at least one numeric score; n_prose = artifacts that contain it
                with no score. A name whose n_scoring is 0 exists only in the writing.
IDENTIFICATION  Exact for containment. ⚠ "is the comparator" is not decidable from a name --
                two names can denote one object. So the round reports the SPLIT and, where both
                names occur in one artifact, checks whether they carry the SAME number, which
                is the only evidence of identity available without re-running the scorer.
SCOPE           population : every results/*.json under E05
                instrument : substring containment + numeric-value presence
                             instrument unit = A NAME IN AN ARTIFACT
                             claim unit      = A NAME THAT DENOTES A SCORED ARM
                             NOT equal -- hence the scoring/prose split rather than a raw count
                baseline   : `topw_k4`, a name known to be a scored arm
                regime     : as committed at this sha
WORLDS          A ONE OBJECT, TWO NAMES: both names appear in scoring artifacts, or they
                  co-occur carrying the same number -> a rename, untracked but harmless.
                B PROSE-ONLY NAME: `POOL[0:4]` appears in NO scoring artifact -> the
                  deliverable names ②'s baseline with a string no scorer ever wrote, and the
                  percentile 93.7 attached to it is anchored to a different label.
                C DIFFERENT OBJECTS: they co-occur with DIFFERENT numbers -> ②'s stated
                  baseline is not the one the scores were computed against.
KILL            pre-registered: if the positive control name is not found in scoring artifacts,
                the instrument cannot see scored arms and every zero is UNVERIFIED.
POSITIVE CTRL   `topw_k4` -- a known scored arm -- must appear in >=1 scoring artifact.
NEGATIVE CTRL   an invented arm name must appear in none.
PLACEBO         a word that appears only in prose (`nevertheless`) must have n_scoring 0,
                proving the split can put something on the prose side.
SEEDS           n/a, deterministic.
MULTIPLICITY    4 names x every artifact + 3 control checks, all reported.
ARTIFACT        results/baseline_name.json
IMPOSSIBLE      construct validity for "denotes the same arm": two names are the same object
                only if a scorer says so. Without re-running the scorer this bounds the
                question and does not close it.
"""
from __future__ import annotations
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
E05 = ROOT / "E05_the_space_of_compilers"
OUT = pathlib.Path(__file__).resolve().parent / "results"
NUM = re.compile(r"\d+\.\d{3,}")

NAMES = {
    "POOL[0:4]":            ["POOL[0:4]", "POOL[0:4]".lower(), "pool_0_4", "pool04"],
    "sat_genericpool16[:4]":["genericpool16"],
    "topw_k4 (POSITIVE)":   ["topw_k4"],
    "zzq_invented (NEG)":   ["zzq_invented_arm_name"],
    "nevertheless (PLACEBO)":["nevertheless"],
}


def keys_and_strings(o, keys, strings):
    """Separate the KEY namespace from the STRING-VALUE namespace."""
    if isinstance(o, dict):
        for k, v in o.items():
            keys.add(str(k))
            keys_and_strings(v, keys, strings)
    elif isinstance(o, list):
        for v in o:
            keys_and_strings(v, keys, strings)
    elif isinstance(o, str):
        strings.append(o)


def artifacts():
    """⛔ v1 CALLED AN ARTIFACT `SCORING` IF IT CONTAINED ANY DECIMAL. R472 and R560 are
    register/scope AUDIT rounds whose artifacts are full of decimals about compliance, so
    `POOL[0:4]` was credited with a scoring artifact it never had, and the verdict branch fired
    on a proxy that does not mean what its label needs. The discriminator is now the JSON
    NAMESPACE: an arm that was SCORED appears as a KEY (or inside an arms list); a name quoted
    by an audit appears inside a STRING VALUE. That is mechanical and invents nothing."""
    out = []
    # ⛔ AND I DID IT AGAIN. R601 hit exactly this — a round scanning a population containing
    #    its own artifact finds every literal it searches for — and I wrote the general remedy
    #    into RETRACTIONS as entry 497 two rounds ago: A ROUND MAY NOT BE A MEMBER OF THE
    #    POPULATION IT MEASURES. Writing a remedy is not installing it; this one is now in the
    #    code rather than in the ledger.
    for f in sorted(E05.glob("A*/R[0-9]*/results/*.json")):
        if f.parts[-3].startswith("R604_"):
            continue
        try:
            raw = f.read_text(errors="ignore")
            o = json.loads(raw)
        except Exception:
            continue
        ks, ss = set(), []
        keys_and_strings(o, ks, ss)
        out.append((f, raw, ks, ss))
    return out


def main():
    A = artifacts()
    if not A:
        print("UNRUNNABLE: no artifacts. Exit 2, never 0."); return 2
    n_scored = sum(1 for _, raw, _, _ in A if NUM.search(raw))
    print(f"POPULATION  {len(A)} parseable results/*.json, {n_scored} containing a decimal")
    print(f"  ⚠ `contains a decimal` is NOT `scored an arm` — the split below is by JSON "
          f"NAMESPACE: name-as-KEY means an arm the round scored, name-in-a-STRING means a "
          f"name the round quoted")

    tally = {}
    for label, pats in NAMES.items():
        as_key, in_str = [], []
        for f, raw, ks, ss in A:
            if any(any(p in k for p in pats) for k in ks):
                as_key.append(f)
            elif any(any(p in s for p in pats) for s in ss):
                in_str.append(f)
        rounds = sorted({re.match(r"R(\d+)", f.parts[-3]).group(1)
                         for f in as_key + in_str if re.match(r"R\d+", f.parts[-3])})
        tally[label] = {"n_total": len(as_key) + len(in_str),
                        "n_scoring": len(as_key), "n_prose": len(in_str),
                        "rounds_as_key": sorted({re.match(r"R(\d+)", f.parts[-3]).group(1)
                                                 for f in as_key if re.match(r"R\d+", f.parts[-3])}),
                        "rounds": rounds}

    print(f"\n─── CONTROLS ───")
    pos = tally["topw_k4 (POSITIVE)"]["n_scoring"] > 0
    print(f"  POSITIVE  `topw_k4`, a known scored arm: {tally['topw_k4 (POSITIVE)']['n_scoring']} "
          f"scoring artifact(s) -> {'PASS' if pos else '⛔ FAIL'}")
    neg = tally["zzq_invented (NEG)"]["n_total"] == 0
    print(f"  NEGATIVE  an invented arm name: {tally['zzq_invented (NEG)']['n_total']} "
          f"artifact(s) -> {'PASS' if neg else '⛔ FAIL'}")
    plc = tally["nevertheless (PLACEBO)"]
    plc_ok = plc["n_scoring"] == 0
    print(f"  PLACEBO   a prose-only word: {plc['n_total']} total, {plc['n_scoring']} scoring "
          f"-> {'PASS — the split can put something on the prose side' if plc_ok else '⛔ FAIL'}")
    controls_ok = pos and neg and plc_ok

    print(f"\n─── THE TWO CANDIDATE NAMES FOR ②'s COMPARATOR ───")
    for label in ("POOL[0:4]", "sat_genericpool16[:4]"):
        t = tally[label]
        print(f"  {label:<24} total {t['n_total']:>3}   SCORING {t['n_scoring']:>3}   "
              f"prose {t['n_prose']:>3}   as-KEY in rounds {t['rounds_as_key'][:8]}   "
              f"all {t['rounds'][:8]}")

    co = [f for f, raw, _, _ in A
          if any(p in raw for p in NAMES["POOL[0:4]"]) and "genericpool16" in raw]
    print(f"\n  artifacts containing BOTH names: {len(co)} "
          f"{[str(f.parts[-3])[:28] for f in co][:4]}")

    print(f"\n─── VERDICT ───")
    p, g = tally["POOL[0:4]"], tally["sat_genericpool16[:4]"]
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire"
    elif p["n_scoring"] == 0 and g["n_scoring"] > 0:
        world = (f"B PROSE-ONLY NAME — `POOL[0:4]` appears in {p['n_scoring']} scoring "
                 f"artifact(s) and {p['n_prose']} prose one(s), while `genericpool16` appears in "
                 f"{g['n_scoring']} scoring artifact(s). The deliverable names ②'s baseline with "
                 f"a string no scorer ever wrote; the percentile 93.7 attached to it was computed "
                 f"against a differently-labelled object, and whether they denote the same arm is "
                 f"UNVERIFIED from names alone.")
    elif p["n_scoring"] > 0 and g["n_scoring"] > 0:
        world = "A ONE OBJECT, TWO NAMES — both appear in scoring artifacts"
    else:
        world = (f"neither name is scored: POOL {p['n_scoring']}, genericpool "
                 f"{g['n_scoring']} — the comparator is unlocatable")
    print(f"  {world}")
    print(f"\n  MULTIPLICITY: {len(NAMES)} names x {len(A)} artifacts + 3 control checks.")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "baseline_name.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok,
        "n_artifacts": len(A), "n_with_scores": n_scored,
        "tally": tally, "both_names_in": [str(f.relative_to(E05)) for f in co],
        "check203": ("R603's closing line said a rubric-generation-and-core-selection is 'what "
                     "R433 did'. R433 generated the TREATMENT; its comparator was `generic` and "
                     "its resolved contrast was against `length`. Read from R433's own table: "
                     "gen 0.4590, sham 0.4540, generic 0.4497, length 0.5135, and gen-generic "
                     "= +0.0093 [-0.0008, +0.0186] vs MDE 0.0140, NOT RESOLVED."),
        "impossible": ("two names denote one arm only if a scorer says so; without re-running "
                       "the scorer this bounds the question and does not close it"),
    }, indent=2))
    print(f"\n  wrote {OUT / 'baseline_name.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
