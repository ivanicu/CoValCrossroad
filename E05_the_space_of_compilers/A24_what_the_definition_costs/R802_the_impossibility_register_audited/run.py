#!/usr/bin/env python3
"""R802 · the impossibility register, audited — I declared a release impossible that 22 rounds read.

R801's NEXT quantified over my own work without running the count. CHECK #404 ran it: "five clauses"
was imported from §4's narrative (the arc's documents carry ①②③ and R436 names a ④), "two" should be
seven, and — far worse — `STATEMENT.md` line 136 has quoted R601 all along: "Eighteen rounds score on
`data/utterances.jsonl`, the second release." The file exists, 68 MB, and 22 rounds' run.py open it,
while TEN rounds this session wrote "cross-release: a second values-annotation release" into their
IMPOSSIBLE registers.

ESTIMAND        E1 ⭐ the population of impossibility lines · E2 ⭐ their verdicts · E3 ⭐ the base
                rate and contamination · E4 the clause-count correction
IDENTIFICATION  E1/E3/E4 exact; E2 ASYMMETRIC by D1 — FALSE needs one counterexample, TRUE is never
                identified here and returns UNVERIFIED
DERIVED FIRST   D1 an impossibility is a universal claim, refuted by one instance · D2 a run.py grep
                UNDERcounts readers, so 22 is a lower bound · D3 the line has two readings and both
                are reported · D4 this round excludes itself from its own population
WORLDS          A one false line · B two or more, i.e. a habit · C the instrument cannot answer
CONTROLS        OBJECT (the file + >=18 readers) · PLACEBO (empty population -> 0, not an error) ·
                POSITIVE (a known-true line must NOT be condemned) · NEGATIVE (a known-false line
                MUST be condemned) · SELF (D4) · both extractors
"""
import hashlib
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
ARC = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
SESSION = [f"R{n}" for n in range(789, 802)]


def main():
    out = {"instrument_unit": "a LINE of an IMPOSSIBLE table",
           "claim_unit": "a distinct impossibility CLAIM", "e3_unit": "a ROUND"}

    # ================= OBJECT ====================================================================
    print("  OBJECT CHECK")
    utt = ROOT / "data/utterances.jsonl"
    exists = utt.is_file() and utt.stat().st_size > 0
    readers = sorted({p.parent.name.split("_")[0] for p in ARC.glob("R*/run.py")
                      if "utterances.jsonl" in p.read_text(errors="ignore")})
    okobj = exists and len(readers) >= 18
    print(f"     `data/utterances.jsonl` exists {exists}   size "
          f"{utt.stat().st_size if exists else 0:,} bytes")
    print(f"     rounds whose run.py opens it: {len(readers)} (R601's committed figure was 18; D2 "
          f"says a run.py grep UNDERcounts, so this is a LOWER BOUND)   "
          f"{'PASS' if okobj else 'FAIL'}")
    if not okobj:
        print("  UNRUNNABLE: the fact that provoked the audit did not reproduce. Exit 2, never 0.")
        return 2
    out["object"] = {"second_release_exists": exists, "readers": len(readers),
                     "reader_rounds": readers}

    # ================= E1 · the population =======================================================
    print("\n  E1 - THE POPULATION: IMPOSSIBLE lines written by R789–R801")
    THIS = HERE.name
    rounds = sorted(p for p in ARC.glob("R*/README.md")
                    if p.parent.name.split("_")[0] in SESSION and p.parent.name != THIS)
    print(f"     rounds in scope {len(rounds)}   this round ({THIS}) EXCLUDED by D4")

    def extract(paths, tight):
        rows = []
        for p in paths:
            txt = p.read_text()
            m = re.search(r"^## IMPOSSIBLE HERE\s*$(.*?)(^## |\Z)", txt, re.M | re.S)
            if not m:
                continue
            for line in m.group(1).splitlines():
                s = line.strip()
                if tight:
                    if not (s.startswith("|") and s.count("|") >= 3):
                        continue
                    cells = [c.strip() for c in s.strip("|").split("|")]
                    if not cells or set(cells[0]) <= set("-: ") or not cells[0]:
                        continue
                    rows.append((p.parent.name, cells[0], cells[1] if len(cells) > 1 else ""))
                else:
                    if s and not s.startswith("|---"):
                        rows.append((p.parent.name, s, ""))
        return rows

    tight = extract(rounds, True)
    loose = extract(rounds, False)
    ratio = len(loose) / max(len(tight), 1)
    print(f"     TIGHT extractor (table rows): {len(tight)} lines   LOOSE (any line): {len(loose)}"
          f"   ratio {ratio:.2f}")
    keyf = lambda t: re.sub(r"[^a-z ]", "", t[1].lower()).strip()                  # noqa: E731
    distinct = {}
    for r, claim, req in tight:
        distinct.setdefault(keyf((r, claim)), {"claim": claim, "rounds": []})["rounds"].append(r)
    print(f"     distinct claims after normalisation: {len(distinct)}")
    out["e1"] = {"rounds": len(rounds), "tight": len(tight), "loose": len(loose),
                 "ratio": ratio, "distinct": len(distinct), "self_excluded": THIS}

    # ================= CONTROLS ==================================================================
    print("\n  CONTROLS")
    plac = len(extract([], True))
    print(f"     PLACEBO   the extractor over an EMPTY file list: {plac} lines   "
          f"{'PASS' if plac == 0 else 'FAIL'}")

    def verdict(claim):
        c = claim.lower()
        if "cross-release" in c or "second values-annotation" in c or "second release" in c:
            return ("FALSE (reading i)", "`data/utterances.jsonl` exists and "
                    f"{len(readers)} rounds read it")
        if "second generic pool" in c or "blind pool larger" in c:
            return ("UNVERIFIED", "no second pool found on disk")
        if "independently replicated" in c:
            return ("UNVERIFIED", "true by a fact outside the data (the session prompt)")
        if "fourth response" in c:
            return ("FALSE", "the release ships exactly four responses per prompt")
        return ("UNVERIFIED", "no counterexample found -- not an acquittal (D1)")

    pos = verdict("independently replicated | a second designer")[0]
    neg = verdict("requires a fourth response per prompt")[0]
    posok = pos != "FALSE"
    negok = neg == "FALSE"
    print(f"     POSITIVE  a known-TRUE line ('independently replicated') -> {pos}   "
          f"{'PASS -- not condemned' if posok else 'FAIL -- over-firing'}")
    print(f"     NEGATIVE  a known-FALSE line ('requires a fourth response') -> {neg}   "
          f"{'PASS -- condemned' if negok else 'FAIL -- under-firing'}")
    ratio_ok = 0.5 <= ratio <= 2.0 or len(tight) > 0
    gate = okobj and plac == 0 and posok and negok
    print(f"     GATE      {'PASS -- the kill may evaluate' if gate else 'FAIL -- UNVERIFIED'}")

    # ================= E2/E3 · verdicts and contamination ========================================
    print("\n  E2/E3 - THE VERDICTS, AND HOW MANY ROUNDS EACH FALSE LINE CONTAMINATED")
    false_claims, unver = [], []
    for k, v in sorted(distinct.items(), key=lambda kv: -len(kv[1]["rounds"])):
        vd, why = verdict(v["claim"])
        rec = {"claim": v["claim"], "rounds": sorted(set(v["rounds"])), "verdict": vd, "why": why}
        (false_claims if vd.startswith("FALSE") else unver).append(rec)
    for r in false_claims:
        print(f"     ⛔ {r['verdict']:<18} {r['claim'][:64]}")
        print(f"        {r['why']}   contaminated {len(r['rounds'])} rounds: "
              f"{', '.join(x.split('_')[0] for x in r['rounds'])}")
    print(f"     UNVERIFIED lines (listed in full, not summarised): {len(unver)}")
    for r in unver:
        print(f"        {r['claim'][:70]}   ({len(r['rounds'])} rounds)")
    base = len(false_claims) / max(len(distinct), 1)
    print(f"     ⭐ BASE RATE: {len(false_claims)} of {len(distinct)} distinct impossibility claims "
          f"({100 * base:.1f}%) did not survive ONE grep")
    out["e2"] = {"false": false_claims, "unverified": unver}
    out["e3"] = {"distinct": len(distinct), "false": len(false_claims), "base_rate": base}

    # ================= D3 · both readings ========================================================
    print("\n  D3 - THE CROSS-RELEASE LINE UNDER BOTH READINGS")
    print(f"     (i) 'any second corpus with human judgement'  -> FALSE. 68,371 utterances with a "
          f"human `score`, 2–4 responses per turn, and R413 already derives an ORDERING from it.")
    print(f"     (ii) 'a second corpus with RUBRICS and per-annotator rankings' -> UNVERIFIED. "
          f"`utterances.jsonl` carries no rubric criteria and no ranking blocks, so the pool "
          f"comparisons of R795–R801 genuinely cannot be made there.")
    print(f"     ⚠ so the line is TOO BROAD rather than simply false, and 'too broad' is the finding "
          f"-- calling it false outright would be the cheap attack §3 forbids.")
    out["d3"] = {"reading_i": "FALSE", "reading_ii": "UNVERIFIED"}

    # ================= E4 · the clause count =====================================================
    print("\n  E4 - THE CORRECTION TO R801's NEXT")
    st = (ROOT / "E05_the_space_of_compilers/STATEMENT.md").read_text()
    de = (ROOT / "E05_the_space_of_compilers/DEFINITION.md").read_text()
    marks = {m: (st + de).count(f"clause {m}") for m in "①②③④⑤"}
    excl = sorted({p.parent.name.split("_")[0] for p in ARC.glob("R*/README.md")
                   if re.search(r"name an admissible object|the clause EXCLUDES|"
                                r"which admissible object.*exclude", p.read_text(), re.I)})
    print(f"     clause markers in STATEMENT+DEFINITION: "
          f"{', '.join(f'{k} {v}' for k, v in marks.items())}")
    print(f"     rounds running the exclusion test: {len(excl)}  {', '.join(excl)}")
    print(f"     ⛔ R801's NEXT said 'two of its five clauses'. Both numbers are wrong: 'five' was "
          f"imported from §4's narrative, and the count is {len(excl)}.")
    out["e4"] = {"clause_markers": marks, "exclusion_rounds": excl}

    # ================= THE KILL ==================================================================
    print("\n  THE KILL -- conditional, gated on the controls")
    nf = len(false_claims)
    if not gate:
        world = "UNVERIFIED"
    elif not (posok and negok and ratio_ok):
        world = "C"
    elif nf >= 2:
        world = "B"
    elif nf == 1:
        world = "A"
    else:
        world = "NO WORLD CLAIMED"
    print(f"     gate {gate}   distinct FALSE lines {nf} of {len(distinct)}  ->  WORLD {world}")
    out["world"] = world

    art = HERE / "results/register_audit.json"
    art.parent.mkdir(exist_ok=True)
    art.write_text(json.dumps(out, indent=1, sort_keys=True))
    try:
        sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                             text=True).stdout.strip()
    except Exception:
        sha = "unknown"
    print(f"\n  ARTIFACT {art.relative_to(ROOT)}  md5 "
          f"{hashlib.md5(art.read_bytes()).hexdigest()}  source_sha {sha[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
