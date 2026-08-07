#!/usr/bin/env python3
"""A commit that ADDS a round directory must name that round in its body.

⛔ WHY, and it is a measured event, not a hypothetical. Commit `496b0b28` added the whole of
`R866_the_comparator_is_a_swept_axis_not_a_choice` — run.py, results, the DEFINITION.md annotation —
and its body is **a different round's diary entry**, about a sham residual for clause ②, mentioning
R703. Nothing in the commit is about R866.

**The mechanism, and it is worth stating because nothing in the output distinguished it.** The round
was committed in two attempts. The first aborted at the annotation guard, which sits ABOVE the
heredoc that writes the message file — so `cat > m9.txt` never ran. The retry then did
`git commit -F m9.txt` against a **stale `m9.txt` left in the scratchpad by an earlier round**
(mtime 17:16:42, hours before). The two edit commands I ran on that file "succeeded" — they edited
the stale content. `git commit` reported 4 files changed and the push succeeded. **Every signal said
the round had landed with its reasoning attached, and the reasoning belonged to another round.**

⚠ THIS IS THE THIRD TIME IN FOUR ROUNDS THAT A SIDE CHANNEL FAILED SILENTLY while its primary
succeeded: an annotation aborting on a from-memory anchor (twice) and now a message file carrying
another round's content. **The class is: a file-based hand-off whose staleness is indistinguishable
from success.** The annotation guard already fixed one direction; this fixes the other.

PROXY LEDGER
  PROPERTY    the commit's WHY is about the round the commit contains
  PROXY       the body mentions the `R<number>` of every round directory the commit ADDS
  IMPLICATION **no mention => the body is not about that round** is SOUND: a diary entry that never
              names its round cannot be that round's diary entry.
              **mention => the body is about it** is NOT sound: a stale body could coincidentally
              mention the number. This rules on ABSENCE only.
  SAFE SIDE   flags missing mentions. A mentioning body is UNVERIFIED, never certified.

⚠ It cannot catch a stale body for a commit that adds NO round directory (an annotation-only or
fix-only commit). Named here rather than discovered later.
"""
import json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
FROZEN = pathlib.Path(__file__).resolve().parent / "KNOWN_MISNAMED_COMMITS.json"
CORR = pathlib.Path(__file__).resolve().parent / "COMMIT_BODY_CORRECTIONS.json"
N_COMMITS = 400
RDIR = re.compile(r"/(R(\d+))_[a-z0-9_]+/")


def added_rounds(h):
    out = subprocess.run(["git", "-C", str(ROOT), "show", "--diff-filter=A", "--name-only",
                          "--format=", h], capture_output=True, text=True).stdout
    return sorted({m.group(1) for p in out.splitlines() for m in [RDIR.search("/" + p)] if m})


def offenders(n=N_COMMITS):
    log = subprocess.run(["git", "-C", str(ROOT), "log", f"-{n}", "--format=%H%x01%s%x01%b%x02"],
                         capture_output=True, text=True).stdout
    bad, seen = [], 0
    for rec in log.split("\x02"):
        if not rec.strip():
            continue
        parts = (rec.split("\x01") + ["", ""])[:3]
        h, subj, body = parts[0].strip(), parts[1], parts[2]
        rs = added_rounds(h)
        if not rs:
            continue
        seen += 1
        text = subj + "\n" + body
        missing = [r for r in rs if not re.search(rf"\b{r}\b", text)]
        if missing:
            bad.append((h[:8], missing, " ".join(subj.split())[:70]))
    return bad, seen


def controls() -> bool:
    """Both arms. A detector that flags everything passes the positive arm alone."""
    good = ("R866 measured the comparator sweep", ["R866"])
    bad = ("the sham residual clause two was kept for", ["R866"])
    pos = [r for r in bad[1] if not re.search(rf"\b{r}\b", bad[0])] == ["R866"]
    g0 = [r for r in good[1] if not re.search(rf"\b{r}\b", good[0])] == []
    print(f"  POSITIVE CONTROL  a body NOT naming its round is flagged: {pos}  "
          f"{'PASS' if pos else 'FAIL'}")
    print(f"  g=0               a body naming its round is not flagged: {g0}  "
          f"{'PASS' if g0 else 'FAIL'}")
    print("    The positive arm uses the REAL offending subject line from 496b0b28, not an")
    print("    invented one — a control validated against cases I made up is validated against")
    print("    my imagination.")
    return pos and g0


def main() -> int:
    if not controls():
        print("\n  UNVERIFIED: the detector failed its own controls. Exit 2, never 0.")
        return 2
    bad, seen = offenders()
    if not seen:
        print("\n  OBSERVED NOTHING: no commit in the window ADDS a round directory. A check with")
        print("  no population has not passed — it has not run. Exit 2, never 0.")
        return 2
    frozen = set(json.loads(FROZEN.read_text())["hashes"]) if FROZEN.exists() else set()
    # ⚠ A CORRECTION is not a pardon. It asserts that the round's real diary entry exists in a
    # LATER commit, and the gate verifies that claim rather than taking it. History here is pushed
    # and rebase is not used, so annotating is the only honest repair (L81).
    corr = json.loads(CORR.read_text())["corrections"] if CORR.exists() else {}
    log_all = subprocess.run(["git", "-C", str(ROOT), "log", f"-{N_COMMITS}", "--format=%s%x01%b"],
                             capture_output=True, text=True).stdout
    repaired = set()
    for h, rec in corr.items():
        if re.search(rf"\b{rec['round']}\b", log_all):
            repaired.add(h)
        else:
            print(f"  ⛔ CORRECTION UNHONOURED for {h}: it claims {rec['round']}'s real body exists,")
            print(f"     and no commit in the window carries it. A correction that cannot be")
            print(f"     verified is a second wrong claim on top of the first.")
    if repaired:
        print(f"  ⓘ {len(repaired)} commit(s) repaired by a VERIFIED correction record: "
              f"{sorted(repaired)}")
    new = [b for b in bad if b[0] not in frozen and b[0] not in repaired]
    print(f"\n  {seen} commit(s) add a round · {len(bad)} do not name it · {len(frozen)} frozen · "
          f"{len(new)} NEW")
    if new:
        print(f"\n  FAIL: {len(new)} commit(s) carry a body that never names the round they add:")
        for h, miss, subj in new[:8]:
            print(f"    {h}  missing {miss}  |  {subj}")
        print("  A commit body IS the diary entry. One that never names its own round is either")
        print("  stale or about something else — and 496b0b28 was both.")
        return 1
    print("\n  PASS: every round-adding commit names its round. ⚠ This rules on ABSENCE only —")
    print("  a body could name the number and still be stale, and commits that add NO round")
    print("  directory are outside this gate's population entirely.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
