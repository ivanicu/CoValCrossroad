#!/usr/bin/env python3
"""A NEXT is a claim that something is UNDONE — and it must cite the check that established it.

⛔ WHY. R858 measured it: of **26** NEXT lines written in one session, **7 (27%)** pointed at
something **already done or structurally impossible** — a fitted-combiner class R824/R825 had
built, a wording R824 had computed, a noise component the definition's own table refuted, an
intersection the population forbade, a conjunction clause ③ cannot reach, a domination test sitting
in R347's committed verdict string, and a second corpus R603 had already ruled a different KIND.

**Every one WAS caught — by the prior-art check at the START of the following round.** The check
works. ⛔ **It runs one round too late**: the NEXT is written, committed, and becomes the next
round's framing before anything tests it. **Four of the seven cost a round's opening.**

⚠ **WHAT THIS GATE CAN AND CANNOT DO — stated up front, not discovered later.**
It reads commit bodies, so it can only ever act AFTER the fact. **It is a RATCHET, not a
preventive.** What it buys is that the omission becomes visible and countable instead of being
rediscovered one round later, every time.

PROXY LEDGER
  PROPERTY    the NEXT's claim that something is undone was checked against prior art before it
              was written
  PROXY       the NEXT block cites a check (`check #N`, `check N`) or says it was checked against
              prior art
  IMPLICATION **no citation => not cleared** is SOUND: you cannot cite a check you did not run.
              **citation => cleared is NOT**: the number could name the wrong check, or one that
              returned nothing. This rules on ABSENCE only.
  SAFE SIDE   flags missing citations. A cited NEXT is UNVERIFIED, never certified — and this file
              says so rather than letting a passing exit imply otherwise.

⚠ A NOTE ON THE BASELINE. 25 of the 26 audited NEXTs predate the convention and are frozen. **Frozen
means RECORDED, not forgiven** — each is still a claim written without the check that would have
tested it, and R858 names the seven that turned out to be empty.
"""
import json, pathlib, re, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
FROZEN = pathlib.Path(__file__).resolve().parent / "KNOWN_UNCITED_NEXTS.json"
N_COMMITS = 400                      # ⚠ a WINDOW; see the expiry note below
# ⚠ CAPTURES FROM `NEXT` ONWARD, INCLUDING THE BRACKET — caught by this file's own g=0 arm.
# The first version captured only what follows the colon, and the citation lives in the bracket
# BEFORE it (`NEXT [checked against prior art, check #514]: ...`), so a correctly-cited NEXT was
# flagged. The POSITIVE arm could not see this: it only asks whether an uncited NEXT is caught.
# A control that only proves the detector fires is half a control.
# ⚠ AND A COLON IS REQUIRED ON THE FIRST LINE — caught on the REAL corpus, not in a fixture.
# The previous version matched prose that merely BEGINS a line with the word, e.g. R858's own
# body: "NEXT lines. A grep is a measuring instrument". The g=0 arm below had tested the word
# MID-SENTENCE, which is not the failure mode the corpus actually contains — §4's
# `a control validated on imagined cases`, validated against my imagination. The arm now uses
# the real offending string.
NEXT_RX = re.compile(r"^(NEXT\b[^\n]*?:.*?)(?:\n\n|\Z)", re.M | re.S)
CITE_RX = re.compile(r"check\s*#?\s*\d+|checked against prior art|prior[- ]art check", re.I)


def blocks(n=N_COMMITS):
    out = subprocess.run(["git", "-C", str(ROOT), "log", f"-{n}", "--format=%H%x01%b%x02"],
                         capture_output=True, text=True).stdout
    recs = []
    for r in out.split("\x02"):
        if not r.strip():
            continue
        p = (r.split("\x01") + [""])[:2]
        m = NEXT_RX.search(p[1] or "")
        if m:
            recs.append((p[0].strip()[:8], " ".join(m.group(1).split())))
    return recs


def uncited(recs):
    return [(h, t) for h, t in recs if not CITE_RX.search(t)]


def synthetic_controls() -> bool:
    """Both arms required. A detector that flags everything passes the positive arm alone."""
    good = "NEXT [checked against prior art BEFORE writing, check #514]: do the thing.\n\n"
    bad = "NEXT [HYPOTHESIS, untested]: do the thing nobody has done.\n\n"
    none = ("prose from R858's own body, taken verbatim:\n"
            "NEXT lines. A grep is a measuring instrument, and this one was live.\n\n")
    pos = len(uncited([("a", " ".join(NEXT_RX.search(bad).group(1).split()))])) == 1
    g0a = len(uncited([("b", " ".join(NEXT_RX.search(good).group(1).split()))])) == 0
    g0b = NEXT_RX.search(none) is None
    print(f"  POSITIVE CONTROL  an UNCITED NEXT is flagged: {pos}  {'PASS' if pos else 'FAIL'}")
    print(f"  g=0               a CITED NEXT is not flagged: {g0a}  {'PASS' if g0a else 'FAIL'}")
    print(f"  g=0               prose merely CONTAINING the word is not a NEXT: {g0b}  "
          f"{'PASS' if g0b else 'FAIL'}")
    print("    The third arm exists because the first version of R858's own extractor matched")
    print("    `NEXT` anywhere and returned 87 of 89 commits — a grep is a measuring instrument,")
    print("    and that one was committed live before it was caught.")
    return pos and g0a and g0b


def main() -> int:
    if not synthetic_controls():
        print("\n  UNVERIFIED: the detector failed its own controls. Exit 2, never 0.")
        return 2

    recs = blocks()
    if not recs:
        print("\n  OBSERVED NOTHING: no commit in the window carries a NEXT block. A check with no")
        print("  population has not passed — it has not run. Exit 2, never 0.")
        return 2

    bad = uncited(recs)
    frozen = set(json.loads(FROZEN.read_text())["hashes"]) if FROZEN.exists() else set()
    new = [(h, t) for h, t in bad if h not in frozen]
    print(f"\n  {len(recs)} NEXT block(s) in the last {N_COMMITS} commits · "
          f"{len(bad)} uncited · {len(frozen)} frozen · {len(new)} NEW")

    # ⚠ EXPIRY, learned the hard way: entries 1353/1354 found a control and a baseline anchored to
    # FIXED commits inside a SLIDING window, dark for ~646 commits. Here the frozen set is hashes
    # and the population is a window, so the SAME expiry applies: as commits accumulate, frozen
    # entries scroll out and the count silently becomes a PREVALENCE rather than an INCREMENT.
    # Named and reported, not left to be rediscovered.
    inwin = {h for h, _ in recs}
    scrolled = sorted(frozen - inwin)
    if frozen and not (frozen & inwin):
        print(f"  ⚠ BASELINE OUT OF POPULATION: all {len(frozen)} frozen hashes have scrolled out")
        print(f"    of the {N_COMMITS}-commit window. The count above is a PREVALENCE, not an")
        print( "    INCREMENT since baseline. (Entries 1353/1354 — same shape, twice.)")
    elif scrolled:
        print(f"  ⓘ {len(scrolled)} frozen hash(es) have scrolled out and are out of population,")
        print( "    not fixed — counting them as fixed would shrink this by time rather than work.")

    if new:
        print(f"\n  FAIL: {len(new)} NEXT line(s) cite no check:")
        for h, t in new[:8]:
            print(f"    {h}  {t[:78]}")
        print("  A NEXT is a CLAIM THAT SOMETHING IS UNDONE. R858 measured 27% of them wrong about")
        print("  exactly that. Cite the check number that established it, as every other claim here")
        print("  cites its evidence.")
        return 1

    print(f"\n  PASS: no NEW uncited NEXT. ⚠ A cited NEXT is UNVERIFIED, never certified — the")
    print("  number could name the wrong check or one that returned nothing. This rules on ABSENCE.")
    print("  ⚠ And this gate is a RATCHET, not a preventive: it reads commit bodies, so it can only")
    print("  ever act after the NEXT has already been written and acted on.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
