#!/usr/bin/env python3
"""
R674 -- does the PROVENANCE rule ever open the file it accepts? And do cited numbers exist?

CHECK #275 ON R673's NEXT LINE -- IT MISCOUNTED, AND THE MISCOUNT IS THE ROUND.
  R673's NEXT says "run it over the two known takers of the escape". Measured over all 1,233
  commits under the gate's own rule: there is ONE taker, 8da27ea. R672 is not a taker and R673 is
  not a taker -- in both, the quantifier had no ARTIFACT word inside the gate's window, so the line
  was never flagged and PROVENANCE never ran on it. R672's commit body announced it was
  "deliberately taking the escape"; the gate never offered it one. ⭐ SO R673's LEDGER 743 CITED AN
  EVENT THAT DID NOT HAPPEN, and this round retracts the instance while testing the mechanism
  properly.

ARITHMETIC TRAP, DECLARED. "PROVENANCE is a regex, therefore it cannot open a file" is a DERIVATION
  from the source, not a measurement -- it could not have come out otherwise. It is labelled as one
  and carries no evidential weight. What IS measurable, and is this round's estimand, is whether the
  numbers people write beside citations actually occur in the cited artifacts.

ESTIMAND        over every NEXT paragraph citing an artifact path with a number nearby, the share of
                those numbers that OCCUR in the cited file.
IDENTIFICATION  exact for "the string occurs"; NOT identified for "the number means what the
                sentence says it means" -- so the result bounds provenance quality from ABOVE.
SCOPE           population : NEXT paragraphs in 1,233 commit bodies + all README `## NEXT` sections
                instrument : path regex + number regex + literal file read at HEAD
                             instrument unit = A (path, number) PAIR
                             claim unit      = A (path, number) PAIR -- EQUAL
                baseline   : none exists; the random baseline is built below
                regime     : files read at HEAD, not at citing time (biases the rate DOWN)
WORLDS          A CEREMONIAL: citations are decorative; most cited numbers are not in the file.
                B LOAD-BEARING: most are, and provenance here is real.
KILL            pre-registered: fewer than 5 qualifying pairs -> UNRUNNABLE, exit 2.
POSITIVE CTRL   synthetic pair whose number IS in the file must verify; and must FAIL at g=0 when
                the number is replaced by one the file lacks.
NEGATIVE CTRL   synthetic pair citing a real file lacking the number must fail.
PLACEBO         nonexistent path -> UNRESOLVABLE, never verified, never folded into failures.
RANDOM BASELINE each number re-tested against a RANDOMLY chosen other artifact -- if a number
                verifies as often against a random file, the citation carries no information.
ARTIFACT        results/provenance_semantics.json
IMPOSSIBLE      whether the cited number MEANS what the sentence claims needs a reader, not a grep.
"""
from __future__ import annotations
import importlib.util, json, pathlib, random, re, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
spec = importlib.util.spec_from_file_location(
    "gate", ROOT / "assurance" / "next_line_quantifiers_are_computed.py")
gate = importlib.util.module_from_spec(spec); spec.loader.exec_module(gate)

PATH = re.compile(r"\b((?:[\w./-]+/)?[\w.-]+\.(?:json|py|md|csv|txt))\b")
NUM = re.compile(r"(?<![\w.])(\d[\d,]{0,9}(?:\.\d+)?)(?![\w.])")
SEED = 20260805


def cited_pairs(text, src):
    out = []
    for pm in PATH.finditer(text):
        w = text[max(0, pm.start() - 240): pm.end() + 240]
        for nm in NUM.finditer(w):
            n = nm.group(1).replace(",", "")
            if len(n) >= 2 and n not in pm.group(1):
                out.append({"src": src, "path": pm.group(1), "num": n})
    return out


def resolve(p):
    c = ROOT / p
    if c.is_file(): return c
    hits = [f for f in ROOT.rglob(pathlib.Path(p).name) if "/_archive/" not in str(f)]
    return hits[0] if len(hits) == 1 else None


def occurs(f, n):
    try: t = f.read_text(errors="ignore")
    except Exception: return False
    return bool(re.search(rf"(?<![\w.]){re.escape(n)}(?![\w.])", t) or
                re.search(rf"(?<![\w.]){re.escape(f'{int(n):,}')}(?![\w.])", t) if n.isdigit()
                else re.search(rf"(?<![\w.]){re.escape(n)}(?![\w.])", t))


def main() -> int:
    rng = random.Random(SEED)
    pairs = []
    shas = subprocess.run(["git", "log", "--format=%H"], cwd=ROOT,
                          capture_output=True, text=True).stdout.split()
    for s in shas:
        b = subprocess.run(["git", "log", "-1", "--format=%B", s], cwd=ROOT,
                           capture_output=True, text=True).stdout
        ms = list(re.finditer(r"^NEXT:\s*(.*?)(?:\n\n|\Z)", b, re.S | re.M))
        if ms: pairs += cited_pairs(" ".join(ms[-1].group(1).split()), "commit")
    for name, sec in gate.readme_next_sections(ROOT):
        pairs += cited_pairs(sec, "readme")

    if len(pairs) < 5:
        print(f"UNRUNNABLE: {len(pairs)} qualifying pairs, pre-registered floor is 5. Exit 2.")
        return 2

    print("─── CONTROLS ───")
    tgt = ROOT / "assurance" / "KNOWN_QUANTIFIED_NEXT.json"
    real_n = str(json.loads(tgt.read_text())["count"])
    pos = occurs(tgt, real_n)
    pos_g0 = occurs(tgt, "987654321")
    print(f"  POSITIVE  a number that IS in the file must verify -> {real_n} in "
          f"KNOWN_QUANTIFIED_NEXT.json: {pos} -> {'PASS' if pos else '⛔ FAIL'}")
    print(f"  g=0 CHECK the same control must FAIL on a number the file lacks -> 987654321: "
          f"{pos_g0} -> {'PASS — the control can fail' if not pos_g0 else '⛔ FAIL — cannot fail'}")
    neg = occurs(ROOT / "RETRACTIONS.md", "987654321")
    print(f"  NEGATIVE  a real file lacking the number must fail -> {neg} -> "
          f"{'PASS' if not neg else '⛔ FAIL'}")
    plc = resolve("no_such_directory/absolutely_not_here.json")
    print(f"  PLACEBO   a nonexistent path must be UNRESOLVABLE -> {plc} -> "
          f"{'PASS' if plc is None else '⛔ FAIL'}")
    ctl = pos and not pos_g0 and not neg and plc is None

    ok = unres = bad = 0
    per = {"commit": [0, 0], "readme": [0, 0]}
    rndok = rndtot = 0
    arts = [f for f in ROOT.rglob("*.json") if "/_archive/" not in str(f)]
    for p in pairs:
        f = resolve(p["path"])
        if f is None: unres += 1; p["v"] = "UNRESOLVABLE"; continue
        v = occurs(f, p["num"]); p["v"] = "OK" if v else "ABSENT"
        ok += v; bad += (not v)
        per[p["src"]][0] += v; per[p["src"]][1] += 1
        if arts:
            rndok += occurs(rng.choice(arts), p["num"]); rndtot += 1

    dec = ok + bad
    rate = ok / dec if dec else 0.0
    rnd = rndok / rndtot if rndtot else 0.0
    print(f"\n─── THE MEASUREMENT ───")
    print(f"  (path, number) pairs found       : {len(pairs)}")
    print(f"  ⚠ UNRESOLVABLE (path not found)  : {unres}  — reported separately, NOT folded into "
          f"failures, which would inflate the failure rate")
    print(f"  decidable pairs                  : {dec}")
    print(f"  ⭐ number occurs in the cited file: {ok}  ({rate:.1%})")
    print(f"  number ABSENT                    : {bad}")
    print(f"\n  RANDOM BASELINE — the same numbers against a RANDOMLY chosen artifact: {rnd:.1%}")
    print(f"  ⭐ lift over random: {rate - rnd:+.1%}  -> "
          f"{'the citation carries information' if rate - rnd > 0.10 else '⛔ the citation adds little over pointing anywhere'}")
    for k, (a, b_) in per.items():
        print(f"  {k:<8}: {a}/{b_} = {a/max(b_,1):.1%}")
    rr = per["readme"][0]/max(per["readme"][1],1); rc = per["commit"][0]/max(per["commit"][1],1)
    dirn = rr < rc
    # ⭐ PRICE THE PRECISION BEFORE READING A DIRECTIONAL FAILURE. A bootstrap over the pairs, so a
    #    15-vs-65 split is not mistaken for a measured reversal.
    boot = []
    rboot = random.Random(SEED + 1)
    rp = [1 if x["v"] == "OK" else 0 for x in pairs if x["src"] == "readme" and x["v"] != "UNRESOLVABLE"]
    cp = [1 if x["v"] == "OK" else 0 for x in pairs if x["src"] == "commit" and x["v"] != "UNRESOLVABLE"]
    for _ in range(2000):
        a = sum(rboot.choice(rp) for _ in rp)/len(rp) if rp else 0
        b = sum(rboot.choice(cp) for _ in cp)/len(cp) if cp else 0
        boot.append(a - b)
    boot.sort()
    lo, hi = boot[int(.025*len(boot))], boot[int(.975*len(boot))]
    mde = (hi - lo) / 2
    print(f"  DIRECTIONAL registered: README < commit -> {'HOLDS' if dirn else '⛔ FAILS'}")
    print(f"    ⚠ BUT PRICE IT: README−commit = {rr-rc:+.1%}, 95% bootstrap CI "
          f"[{lo:+.1%}, {hi:+.1%}] over n_readme={len(rp)}, n_commit={len(cp)}.")
    print(f"    the interval {'STRADDLES ZERO — the reversal is NOT resolved, and reporting it as a' if lo <= 0 <= hi else 'excludes zero — the reversal IS resolved'}")
    print(f"    {'measured reversal would be reading noise. The registered direction is UNVERIFIED, not refuted.' if lo <= 0 <= hi else 'finding.'}")
    dir_verdict = "UNVERIFIED" if lo <= 0 <= hi else ("HOLDS" if dirn else "REFUTED")

    print(f"\n─── VERDICT ───")
    if not ctl: world = "UNVERIFIED — a control did not fire."
    elif rate - rnd <= 0.10:
        world = (f"A CEREMONIAL — cited numbers verify at {rate:.1%} against {rnd:.1%} for a RANDOM "
                 f"artifact, a lift of {rate-rnd:+.1%}. The citation barely beats pointing anywhere.")
    else:
        world = (f"B LOAD-BEARING — {rate:.1%} of cited numbers occur in the cited file against "
                 f"{rnd:.1%} random, lift {rate-rnd:+.1%}. ⚠ UPPER BOUND: occurrence is not "
                 f"meaning; the string being present does not make the sentence true.")
    print(f"  {world}")
    print(f"  registered 40% [15,70] -> observed {rate:.1%}: "
          f"{'INSIDE' if 0.15 <= rate <= 0.70 else '⛔ OUTSIDE'}, error {rate-0.40:+.1%}")

    sha = subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True).stdout.strip()
    print(f"\n  MULTIPLICITY: {len(pairs)} pairs × 2 sources + 4 controls + 1 random baseline.")
    print(f"  ⭐ tree sha: {sha[:12]}   seed: {SEED}")
    (HERE/"results").mkdir(exist_ok=True)
    (HERE/"results"/"provenance_semantics.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha, "seed": SEED,
        "pairs": len(pairs), "unresolvable": unres, "decidable": dec, "verified": ok,
        "absent": bad, "rate": rate, "random_baseline": rnd, "lift": rate - rnd,
        "per_source": per, "directional_holds": dirn, "directional_verdict": dir_verdict,
        "readme_minus_commit": rr-rc, "dir_ci": [lo, hi], "dir_mde": mde,
        "registered": "40% [15,70]; README < commit; kill if <5 pairs",
        "check275": ("R673's NEXT said 'the two known takers of the escape'. Measured over 1,233 "
                     "commits under the gate's own rule there is ONE: 8da27ea. Neither R672 nor "
                     "R673 took it -- their quantifiers had no ARTIFACT word in the gate's window, "
                     "so they were never flagged and PROVENANCE never ran. R673's ledger 743 cited "
                     "an event that did not occur."),
        "derivation_not_evidence": ("'a regex cannot open a file' is read off the source and could "
                                    "not have come out otherwise -- a DERIVATION, carrying no "
                                    "evidential weight."),
        "scope_limit": "files read at HEAD, not at citing time; biases the rate DOWN",
    }, indent=2))
    print(f"  wrote {HERE/'results'/'provenance_semantics.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
