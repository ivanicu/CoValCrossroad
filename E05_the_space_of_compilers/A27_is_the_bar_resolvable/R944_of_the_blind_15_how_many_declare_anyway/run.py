#!/usr/bin/env python3
"""
R944 · the gate cannot see 15 rounds that reference a proxy route. Do those 15 declare anyway?
        The blind spot's SIZE was R943; its COST is whether anything fell through it.

⛔ WHY NOT THE ROUND MY NEXT PROPOSED. R943 closed with *"read the 15 and separate `loads a model`
from `scores its reported outcome with one`."* **That round is not runnable as stated.** The separation
is a semantic judgement about each round's intent, the only available reader is me, and door ③ says a
judgement sampled from the weights that wrote the corpus is void — this session cannot dispatch an
independent one. **A next-gradient line is the least-controlled sentence in a report and this one
proposed an uncontrolled instrument.** So the estimand is replaced by one with a checkable answer.

⭐ **THE QUESTION THAT SURVIVES.** The gate exists to guarantee that a round scoring against a model
proxy SAYS SO in its own results. R943 measured that the gate cannot see 15 such candidates. But a
blind spot only costs something if something fell through it. **So: of those 15, how many already
carry a declaration?** That is exact, it is answerable off disk, and it separates two worlds with
different consequences for `DEFINITION.md`.

⚠ **AND THE PROXY IS SOUND IN ONE DIRECTION ONLY — THIS IS A P6 LEDGER, NOT A COUNT.**
  PROPERTY  : the round tells its reader the outcome was model-scored
  PROXY     : some string in its results matches the gate's own `DECLARES` regex, 10 phrases
  IMPLICATION: matches ⇒ declared. **NOT declared ⇏ silent** — a round may say it in words the
              regex has never heard, which is the same defect as `USES_GOLD` one layer over.
  SAFE SIDE : a match is CONFIRMED-DECLARED. A non-match is **UNVERIFIED**, never `undeclared`.
Folding UNVERIFIED into `undeclared` would manufacture a defect count in the direction that makes the
gate look worse — and this arc has now twice caught itself reaching for the number that flatters the
round rather than the object.

ESTIMAND        of R943's 15 route-referencing rounds WITH published results, how many carry a
                declaration matching the gate's own `DECLARES` regex somewhere in those results.
IDENTIFICATION  exact for the proxy; the property is only bounded, so verdicts are three-valued.
SCOPE           population: R943's committed `route_only_with_results` list, read from its artifact —
                            not re-derived, so this round cannot quietly change the population
                instrument: the gate's `DECLARES` regex, transcribed from :54-57, applied to every
                            string in every non-provisional results JSON, walked recursively
                baseline:   the gate's live behaviour — it flags 3 rounds, all mentions (R943)
                regime:     HEAD, one release, one repo
WORLDS          A · few declare -> the blind spot has a live cost: rounds publish numbers off model
                    machinery with nothing telling a reader a model produced them, and
                    `DEFINITION.md`'s instrument bookkeeping is incomplete by that many
                B · most declare -> the guarantee is UNENFORCED BUT SATISFIED. The gate never checked
                    these rounds and they declared anyway, so what protects the deliverable here is
                    practice, not the gate — which is a different repair: the gate is redundant where
                    it works and absent where it does not
KILL            CONDITIONAL — the declaration reader is validated on PLANTED documents, because every
                corpus case's status is exactly what is being measured:
                  ⭐ ① POSITIVE, PLANTED: a doc containing `model-scored outcome` must read DECLARES.
                     ⚠ AND FAIL AT g=0: the identical doc with that phrase deleted must NOT.
                  ⭐ ② NEGATIVE / DISCRIMINATION, PLANTED: a doc whose only relevant word is `gold`
                     in passing must NOT read DECLARES. The gate's own comment at :52-53 says a
                     declaration must name the proxy NATURE of the outcome, not merely mention the
                     word — so a reader that fires on `gold` is measuring vocabulary, not disclosure,
                     and would report World B by construction.
                  ⭐ ③ NESTING: the planted declaration must be found when buried inside a list inside
                     a dict. R942 established the gate walks nested structures; a reader that only
                     checks top-level strings would under-count declarations and again manufacture
                     World A.
                  ⭐ ④ POPULATION FROM DISK: the 15 names are READ from R943's artifact, and the
                     count must match. A round that re-derives its own population can move it.
                  ⭐ ⑤ THREE-VALUED: every round reported as CONFIRMED-DECLARED or UNVERIFIED, with
                     the matched phrase and file quoted for the former. No round is called undeclared.
MULTIPLICITY    15 rounds × every non-provisional results file × every string; all reported, including
                rounds with zero admissible files, which are their own category and not silent.
ARTIFACT        results/who_declares.json
IMPOSSIBLE      independently replicated · cross-release · construct validated · criterion validated —
                one repo, one release. ⚠ AND: `does this round score its outcome with the model` stays
                OPEN. This measures disclosure, not usage, and a round can truthfully declare while
                never touching a proxy, or use one and disclose in unrecognised words. Both directions
                remain, and neither is closed by anything on disk.
"""
import json, pathlib, re, subprocess

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"

# transcribed from assurance/outcome_variable_declared.py:54-57 -- the gate's own definition
DECLARES = re.compile(
    r"model[- ]scored|model gold|gold proxy|proxy world|proxy-world|"
    r"against a model|model proxy|no human rankings|judge-relative|"
    r"not human|model-scored outcome", re.I)
PROVISIONAL = re.compile(r"smoke|dry[_-]?run|draft|scratch|trial|pilot|prelim|wip", re.I)

PLANT_POS = {"scope": {"notes": ["the outcome is a model-scored quantity, not a human ranking"]}}
PLANT_G0 = {"scope": {"notes": ["the outcome is a quantity computed from the release"]}}
PLANT_NEG = {"scope": {"notes": ["we loaded the gold file and compared the gold values"]}}


def strings(doc, path=""):
    if isinstance(doc, dict):
        for k, v in doc.items():
            yield from strings(v, f"{path}.{k}" if path else k)
    elif isinstance(doc, list):
        for i, v in enumerate(doc):
            yield from strings(v, f"{path}[{i}]")
    elif isinstance(doc, str):
        yield path, doc


def declares(doc):
    for jp, s in strings(doc):
        m = DECLARES.search(s)
        if m:
            return jp, m.group(0)
    return None, None


def main() -> int:
    art = next(A27.glob("R943_*/results/blind_side.json"), None)
    if art is None:
        print("  UNRUNNABLE: R943 artifact missing; this round reads its population. Exit 2.")
        return 2
    d = json.loads(art.read_text())
    pop = d["route_only_with_results"]
    c4 = len(pop) == 15
    print(f"  ④ POPULATION FROM DISK — {len(pop)} rounds read from R943's artifact, expected 15: "
          f"{c4}  {'PASS' if c4 else 'FAIL — the population moved'}")

    p_jp, p_hit = declares(PLANT_POS)
    g0_jp, _ = declares(PLANT_G0)
    c1 = p_hit is not None and g0_jp is None
    print(f"\n  ① POSITIVE, PLANTED — planted declaration found at `{p_jp}` as `{p_hit}`; the same "
          f"doc with the phrase deleted finds {g0_jp}: {c1}  "
          f"{'PASS — recovers a declaration AND does not fire at g=0' if c1 else 'FAIL'}")

    n_jp, n_hit = declares(PLANT_NEG)
    c2 = n_hit is None
    print(f"  ② NEGATIVE / DISCRIMINATION, PLANTED — a doc mentioning `gold` in passing must NOT "
          f"read as a declaration; found {n_hit}: {c2}  "
          f"{'PASS — disclosure, not vocabulary' if c2 else 'FAIL — the reader measures vocabulary'}")

    c3 = p_jp is not None and "[" in p_jp
    print(f"  ③ NESTING — the planted declaration sits inside a list inside a dict and was found at "
          f"`{p_jp}`: {c3}  {'PASS' if c3 else 'FAIL — the reader only sees top-level strings'}")

    if not (c1 and c2 and c3 and c4):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "c1": c1, "c2": c2, "c3": c3, "c4": c4},
                  open(OUT / "who_declares.json", "w"), indent=2)
        return 2

    rows = []
    for rnd in pop:
        dirs = list(ROOT.glob(f"E0*/A*/{rnd}"))
        files = [f for dd in dirs for f in dd.glob("results/**/*.json")
                 if not PROVISIONAL.search(f.name) and "_smoke_archive" not in f.parts]
        hit_jp = hit_s = hit_f = None
        unreadable = []
        for f in files:
            try:
                doc = json.loads(f.read_text())
            except Exception as e:
                unreadable.append(f"{f.name}: {type(e).__name__}")
                continue
            jp, s = declares(doc)
            if s:
                hit_jp, hit_s, hit_f = jp, s, f.name
                break
        rows.append({"round": rnd, "n_files": len(files), "unreadable": unreadable,
                     "verdict": "CONFIRMED-DECLARED" if hit_s else
                                ("UNVERIFIED (no admissible results file)" if not files
                                 else "UNVERIFIED"),
                     "file": hit_f, "json_path": hit_jp, "phrase": hit_s})

    print(f"\n  ⑤ THREE-VALUED, EVERY ROUND, WITH THE EVIDENCE:")
    print(f"     {'round':<38}{'files':>6}  verdict")
    for r in rows:
        print(f"     {r['round']:<38}{r['n_files']:>6}  {r['verdict']}")
        if r["phrase"]:
            print(f"        <- {r['file']} :: {r['json_path']} :: \"{r['phrase']}\"")
        if r["unreadable"]:
            print(f"        ⚠ unreadable: {r['unreadable']}")

    conf = [r for r in rows if r["verdict"] == "CONFIRMED-DECLARED"]
    unver = [r for r in rows if r["verdict"] != "CONFIRMED-DECLARED"]
    nofile = [r for r in rows if not r["n_files"]]
    share = len(conf) / len(rows)
    world = "B" if share >= 0.5 else "A"

    print(f"\n  ⭐⭐⭐ WORLD {world}: {len(conf)} of {len(rows)} rounds the gate cannot see are "
          f"CONFIRMED-DECLARED ({share:.0%}); {len(unver)} are UNVERIFIED, of which {len(nofile)} "
          f"have no admissible results file at all.")
    if world == "B":
        print(f"     The guarantee is UNENFORCED BUT SATISFIED on the majority: the gate never "
              f"examined these rounds and they declared anyway. What protects the deliverable here "
              f"is practice, not the gate — so the repair is not `tighten the gate's threshold`, it "
              f"is `the gate is redundant where it works and absent where it does not`.")
    else:
        print(f"     The blind spot has a live cost: most of these publish numbers off model "
              f"machinery with no recognised declaration attached.")
    print(f"     ⛔ AND NOT ONE ROUND IS CALLED UNDECLARED. `DECLARES` is 10 phrases; a round may "
          f"disclose in words it has never heard — the same defect as `USES_GOLD`, one layer over. "
          f"UNVERIFIED means the proxy is unfit here, which is not an acquittal and not a conviction.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world,
               "population_source": "R943 results/blind_side.json :: route_only_with_results",
               "n_population": len(rows),
               "confirmed_declared": [r["round"] for r in conf],
               "unverified": [r["round"] for r in unver],
               "unverified_with_no_results_file": [r["round"] for r in nofile],
               "share_confirmed": share,
               "rows": rows,
               "proxy_ledger": {
                   "property": "the round tells its reader the outcome was model-scored",
                   "proxy": "a results string matches the gate's DECLARES regex",
                   "implication": "matches => declared; non-match does NOT imply silent",
                   "safe_side": "a non-match is UNVERIFIED, never `undeclared`"},
               "still_open": "whether any of these rounds SCORES its outcome with a model; this "
                             "measures disclosure, not usage, and nothing on disk closes it",
               "unit_note": "counts are ROUNDS",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "who_declares.json", "w"), indent=2)
    print(f"\n  artifact: results/who_declares.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
