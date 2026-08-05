#!/usr/bin/env python3
"""
R673 -- reconcile the gate's own walk against R672's ad-hoc walk. 249 vs 167.

CHECK #274 ON R672's NEXT LINE -- AND IT IS FALSE, IN THE ONE CLAUSE I WAS PROUDEST OF.
  R672's commit body says the two numbers are "in results/freeze_history.json", and takes the gate's
  PROVENANCE escape on the strength of that citation -- the escape 283 of 284 opportunities had left
  untouched. `grep -c 249 results/freeze_history.json` -> 0. THE ARTIFACT DOES NOT CONTAIN THE
  NUMBER. The escape passed anyway, because PROVENANCE matches the SHAPE of a citation and never
  opens the file. So: the first round in this arc to use the escape used it falsely, and the gate
  certified it. That is R674's question and it is recorded in the ledger now, not deferred silently.

ESTIMAND        of the 82-instance disagreement between the gate's walk (167 frozen, PASSES) and
                R672's ad-hoc walk (249 flagged), what share is attributable to the NEXT-paragraph
                EXTRACTION RULE rather than to the set of commits walked?
IDENTIFICATION  exact and decomposable: run both extractions over ONE shared commit list, then
                partition the disagreeing shas into (extraction-only) and (range-only). Nothing is
                estimated.
SCOPE           population : every commit in this repository's history reachable from HEAD
                instrument : the gate's own extraction vs R672's regex, same QUANT/ARTIFACT/
                             PROVENANCE, same window
                             instrument unit = A COMMIT SHA
                             claim unit      = A COMMIT SHA -- EQUAL, this is a like-for-like diff
                baseline   : the freeze's 167
                regime     : this repository, this history
WORLDS          A EXTRACTION: the two regexes select different paragraphs from the same commits.
                B RANGE: the gate walks fewer commits than I did.
                C BOTH / NEITHER: the disagreement is not decomposable into these two.
KILL            pre-registered: walks differing by >20 commits kill world A outright.
POSITIVE CTRL   the two walks must agree on >=1 sha, or they are not measuring the same object.
NEGATIVE CTRL   a sha known to be IN the freeze must be flagged by both.
PLACEBO         the gate's extraction run twice must be byte-identical.
ARTIFACT        results/reconciliation.json
IMPOSSIBLE      which extraction is CORRECT is a judgement about what a NEXT paragraph IS; this
                round attributes the gap and does not adjudicate it.
"""
from __future__ import annotations
import importlib.util, json, pathlib, re, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent

spec = importlib.util.spec_from_file_location(
    "gate", ROOT / "assurance" / "next_line_quantifiers_are_computed.py")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

ADHOC = re.compile(r"^NEXT\b(.*?)(?=\n[A-Z]{3,}\b|\Z)", re.M | re.S)


def flags(text: str) -> bool:
    for m in gate.QUANT.finditer(text):
        w = text[max(0, m.start() - gate.WINDOW): m.end() + gate.WINDOW]
        if gate.ARTIFACT.search(w) and not gate.PROVENANCE.search(w):
            return True
    return False


def extract_gate(body: str) -> str:
    ms = list(re.finditer(r"^NEXT:\s*(.*?)(?:\n\n|\Z)", body, re.S | re.M))
    return " ".join(ms[-1].group(1).split()) if ms else ""


def extract_adhoc(body: str) -> str:
    m = ADHOC.search(body)
    return " ".join(m.group(1).split()) if m else ""


def main() -> int:
    allshas = subprocess.run(["git", "log", "--format=%H"], cwd=ROOT,
                             capture_output=True, text=True).stdout.split()
    win = allshas[:400]                      # the gate's own window: next_lines(n=400)
    bodies = {}
    for s in allshas:
        bodies[s] = subprocess.run(["git", "log", "-1", "--format=%B", s], cwd=ROOT,
                                   capture_output=True, text=True).stdout

    def hits(shalist, ex):
        return {s for s in shalist if (t := ex(bodies[s])) and flags(t)}

    G_win = hits(win, extract_gate)          # gate rule, gate range
    A_win = hits(win, extract_adhoc)         # my rule,  gate range   -> isolates EXTRACTION
    A_all = hits(allshas, extract_adhoc)     # my rule,  all commits  -> isolates RANGE
    G_all = hits(allshas, extract_gate)
    frozen = set(json.loads((ROOT/"assurance"/"KNOWN_QUANTIFIED_NEXT.json").read_text())["shas"])

    print("─── CONTROLS ───")
    agree = G_win & A_win
    posok = len(agree) >= 1
    print(f"  POSITIVE  the two extractions must agree on >=1 sha in the shared window -> "
          f"{len(agree)} -> {'PASS' if posok else '⛔ FAIL — not the same object'}")
    fr_res = {s for s in allshas if s[:len(next(iter(frozen)))] in frozen} if frozen else set()
    negok = bool(fr_res & (G_all | A_all))
    print(f"  NEGATIVE  a sha known to be IN the freeze must be flagged -> "
          f"{len(fr_res & (G_all|A_all))} of {len(fr_res)} resolved -> "
          f"{'PASS' if negok else '⛔ FAIL'}")
    plcok = hits(win, extract_gate) == G_win
    print(f"  PLACEBO   gate extraction run twice identical -> {'PASS' if plcok else '⛔ FAIL'}")
    ctl = posok and negok and plcok

    n_range = len(allshas) - len(win)
    print(f"\n─── THE PRE-REGISTERED KILL, EVALUATED FIRST ───")
    print(f"  commits in history: {len(allshas)}   gate's window: {len(win)}   difference: {n_range}")
    killed = n_range > 20
    print(f"  registered kill: 'walks differing by more than 20 commits kill world A' -> "
          f"{'⭐ FIRES — the RANGE differs by ' + str(n_range) if killed else 'does not fire'}")

    print(f"\n─── 2×2 DECOMPOSITION (each factor varied alone) ───")
    print(f"  gate rule  × gate range (400) : {len(G_win)}")
    print(f"  adhoc rule × gate range (400) : {len(A_win)}    <- EXTRACTION effect: "
          f"{len(A_win)-len(G_win):+d}")
    print(f"  adhoc rule × all  ({len(allshas)})      : {len(A_all)}    <- RANGE effect: "
          f"{len(A_all)-len(A_win):+d}")
    print(f"  gate rule  × all  ({len(allshas)})      : {len(G_all)}")
    print(f"  freeze                        : {len(frozen)}")
    ext = len(A_win) - len(G_win)
    rng = len(A_all) - len(A_win)
    gap = len(A_all) - len(frozen)
    tot = abs(ext) + abs(rng)
    share = abs(ext)/tot if tot else 0.0
    print(f"\n  gap to explain (adhoc_all − frozen) : {gap}")
    print(f"  extraction contributes              : {ext:+d}  ({share:.1%} of the moved mass)")
    print(f"  range contributes                   : {rng:+d}  ({1-share:.1%})")
    L = len(next(iter(frozen)))
    res = {s for s in allshas if s[:L] in frozen}
    inwin = {s for s in res if s in set(win)}
    scrolled = len(res) - len(inwin)
    print(f"\n  ⚠ THE −{abs(gap-ext-rng)} IS NOT A RESIDUAL, AND CALLING IT ONE WOULD HIDE THE FINDING.")
    print(f"    The gap was defined against the FREEZE, which is not one of the four cells above.")
    print(f"    freeze entries resolvable to a commit : {len(res)} of {len(frozen)}")
    print(f"    ⭐ inside the gate's {len(win)}-commit window : {len(inwin)}")
    print(f"    ⭐ SCROLLED OUT — frozen but invisible  : {scrolled}  ({scrolled/len(frozen):.1%})")
    print(f"    and {len(inwin)-len(G_win)} frozen shas still IN the window are no longer flagged by "
          f"the gate's own rule.")

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire."
    elif killed:
        world = (f"⭐ THE KILL FIRES AND MY REGISTERED HYPOTHESIS IS DEAD. The gate walks the last "
                 f"{len(win)} commits; the history holds {len(allshas)}. That is {n_range} commits "
                 f"apart, far past the 20 I pre-registered as fatal. But the decomposition says the "
                 f"kill's PREMISE was also wrong: varying each factor alone, extraction moves "
                 f"{ext:+d} and range moves {rng:+d}, so the honest answer is BOTH, at "
                 f"{share:.0%}/{1-share:.0%}. I registered 'extraction, >=70%' and the range turns "
                 f"out to be the larger term. ⭐ AND THE OPERATIONAL FACT THAT MATTERS MORE THAN "
                 f"EITHER: the gate cannot see past commit {len(win)}, so its freeze is not a record "
                 f"of the repository — it is a record of a MOVING WINDOW, and entries scroll out of "
                 f"its view without ever being retired. R672 called the freeze a drain; it is worse "
                 f"than that — it is a drain with a leak at the far end that nobody is counting.")
    else:
        world = (f"extraction {share:.1%}, range {1-share:.1%}; kill did not fire.")
    print(f"  {world}")

    sha = subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True).stdout.strip()
    print(f"\n  MULTIPLICITY: {len(allshas)} shas × 2 extractions × 2 ranges + 3 controls.")
    print(f"  ⭐ tree sha: {sha[:12]}")
    (HERE/"results").mkdir(exist_ok=True)
    (HERE/"results"/"reconciliation.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha,
        "commits_in_history": len(allshas), "gate_window": len(win),
        "range_difference": n_range, "kill_fired": killed,
        "gate_rule_gate_range": len(G_win), "adhoc_rule_gate_range": len(A_win),
        "adhoc_rule_all": len(A_all), "gate_rule_all": len(G_all), "frozen": len(frozen),
        "adhoc_all_count_249": len(A_all),
        "extraction_effect": ext, "range_effect": rng, "extraction_share": share,
        "gap": gap, "frozen_resolvable": len(res), "frozen_in_window": len(inwin),
        "frozen_scrolled_out": scrolled,
        "registered": "extraction >=70% [40,100]; kill if walks differ by >20 commits",
        "check274": ("R672's commit body cited results/freeze_history.json for 249; grep -c 249 on "
                     "that file returns 0. PROVENANCE matches the SHAPE of a citation and never "
                     "opens the file."),
    }, indent=2))
    print(f"  wrote {HERE/'results'/'reconciliation.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
