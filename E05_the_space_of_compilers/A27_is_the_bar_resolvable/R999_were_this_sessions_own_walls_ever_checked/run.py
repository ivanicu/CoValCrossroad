#!/usr/bin/env python3
"""R999 — were this session's own declared walls ever checked?

⛔ WHY. R998 overturned R997's wall one round after it was built, and noted that the mechanism worth
examining is not the 14 edges but **why the wall stood for exactly one round: R997's own NEXT sent
someone to check it.** That is a claim about the loop, and §4 warns the closing sentence is exactly
where I am worst — so it is measured from artifacts rather than recalled.

ESTIMAND        of the rounds from R974 on whose artifact declares a wall or limit, the share a
                LATER round revisited.
IDENTIFICATION  identified up to the instrument. ⚠ "Revisited" is operationalised as a later commit
                naming the round **in a sentence containing a revisit verb** — anchored, because
                R998 measured that a bare `\\bR\\d+\\b` scan fires on 70% of a corpus and calibrates
                against nothing. The anchor is the lesson, applied to the round that learned it.
SCOPE           population : rounds R974+ under A27 whose results carry a limit field
                             (`not_measured`, `would_require`, `reopens_*`, `limitation`, …)
                instrument : the round id inside a sentence matching a revisit verb, over commit
                             bodies of LATER commits only
                baseline   : the same ids under an unanchored scan, reported for contrast
                regime     : this session's commits
WORLDS          A THE LOOP CHECKS ITSELF   most declared walls were revisited, so the NEXT line is
                              doing the work R998 credited it with.
                B THE LOOP DOES NOT   most stood unchecked, and R997's one-round life was luck
                              rather than mechanism.
                prediction matrix: A -> majority revisited. B -> a minority, named.
KILL            pre-registered: if fewer than half the eligible walls were revisited, world A is
                dead and R998's credit to the NEXT line is withdrawn.
POSITIVE CTRL   R997's wall MUST read revisited — R998 exists and corrects it by name. If the
                instrument misses that, it is measuring nothing.
NEGATIVE CTRL   ⛔ v1's NEGATIVE WAS CONTRADICTORY BY CONSTRUCTION and its own run caught it: it
                made R997 serve BOTH as the positive (must read revisited, since R998 corrects it)
                and as the "last round, no successor" negative (must not). The same round cannot be
                both. And the intended control is **structurally unavailable** here — every
                wall-declaring round has at least one later commit, so there is no zero-opportunity
                case to test on. Named as unavailable rather than fudged.
                ⭐ REPLACED with one that IS available: a round id that appears in NO commit must
                read unrevisited. That tests whether the classifier invents revisits, which is the
                failure mode that matters.
PLACEBO         the unanchored scan is run alongside and must return materially more, or the anchor
                is doing nothing and the whole design collapses to R998's rejected instrument.
NOISE FLOOR     none: counts of a literal pattern over a finite commit set.
MULTIPLICITY    every eligible round reported, revisited or not.
ARTIFACT        results/walls_checked.json with this file's source hash.
IMPOSSIBLE      whether a revisit was CORRECT — N/A: this counts whether a wall was returned to, not
                whether the return was right. R998 happens to have overturned one; that is not
                evidence the others were handled well.
                ⚠ AND ELIGIBILITY IS UNEQUAL BY CONSTRUCTION: a wall declared at R997 had one round
                to be checked in, one declared at R979 had nineteen. The share is reported WITH the
                per-round opportunity, never as a flat rate.
"""
from __future__ import annotations
import glob, hashlib, json, pathlib, re, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"
WALL_KEYS = ("not_measured", "would_require", "reopens_at", "reopens_if", "reopens_at_entry",
             "redundancy_not_closable", "limitation", "not_decided", "upper_bound_note",
             "not_done", "not_shown", "still_authorial", "impossible")
REVISIT = re.compile(r"\b(check|checked|test|tested|correct|corrected|reopen|refus|overturn|"
                     r"measur|narrow|tighten|resolv)\w*\b", re.I)
SENT = re.compile(r"(?<=[.!?—])\s+|\n")


def main() -> int:
    walls = {}
    for f in sorted(glob.glob(str(A27 / "R9[7-9]*/results/*.json"))):
        m = re.search(r"/R(\d+)_", f)
        if not m or int(m.group(1)) < 974:
            continue
        try:
            j = json.loads(pathlib.Path(f).read_text())
        except Exception:
            continue
        k = [x for x in WALL_KEYS if x in j and j[x]]
        if k:
            walls[int(m.group(1))] = k
    if len(walls) < 5:
        print(f"  UNRUNNABLE: only {len(walls)} wall-declaring rounds found. Exit 2, never 0.")
        return 2
    print(f"POPULATION  {len(walls)} rounds R974+ declaring a wall: {sorted(walls)}")

    log = subprocess.run(["git", "log", "--format=@@@%H%x01%s%x01%b"], cwd=ROOT,
                         capture_output=True, text=True).stdout
    commits = []
    for blk in log.split("@@@")[1:]:
        parts = blk.split("\x01")
        if len(parts) >= 3:
            commits.append((parts[0][:8], parts[1] + "\n" + parts[2]))
    # newest-first from git log; a "later" commit is one appearing EARLIER in this list
    order = {h: i for i, (h, _b) in enumerate(commits)}

    def introduced(n):
        d = next(iter(glob.glob(str(A27 / f"R{n}_*"))), None)
        if not d:
            return None
        out = subprocess.run(["git", "log", "--reverse", "--diff-filter=A", "--format=%H", "--", d],
                             cwd=ROOT, capture_output=True, text=True).stdout.split()
        return out[0][:8] if out else None

    rows = []
    for n in sorted(walls):
        intro = introduced(n)
        if intro is None or intro not in order:
            rows.append({"round": n, "keys": walls[n], "later_commits": 0,
                         "revisited": False, "unanchored": False, "note": "no introducing commit"})
            continue
        later = [b for h, b in commits if order[h] < order[intro]]
        pat = re.compile(rf"\bR{n}\b")
        anch = any(pat.search(s) and REVISIT.search(s) for b in later for s in SENT.split(b))
        loose = any(pat.search(b) for b in later)
        rows.append({"round": n, "keys": walls[n], "later_commits": len(later),
                     "revisited": anch, "unanchored": loose})

    print(f"\n  {'round':>6}{'later commits':>15}{'revisited':>11}{'unanchored':>12}   keys")
    for r in rows:
        print(f"  {r['round']:>6}{r['later_commits']:>15}{str(r['revisited']):>11}"
              f"{str(r['unanchored']):>12}   {','.join(r['keys'])[:44]}")

    eligible = [r for r in rows if r["later_commits"] > 0]
    rev = [r for r in eligible if r["revisited"]]
    loose_n = sum(1 for r in eligible if r["unanchored"])

    pos = next((r for r in rows if r["round"] == 997), None)
    pos_ok = bool(pos and pos["revisited"])
    # a round id present in no commit at all must read unrevisited
    ghost = re.compile(r"\bR99999\b")
    neg_ok = not any(ghost.search(s2) and REVISIT.search(s2)
                     for _h, b in commits for s2 in SENT.split(b))
    zero_opp = [r for r in rows if r["later_commits"] == 0]
    plac_ok = loose_n > len(rev)
    print(f"\n  POSITIVE  R997's wall reads revisited (R998 corrects it by name): {pos_ok}")
    print(f"  NEGATIVE  a round id in no commit reads unrevisited: {neg_ok}")
    print(f"  ⚠ UNAVAILABLE  the 'zero-opportunity' control needs a wall with no later commit; "
          f"there are {len(zero_opp)} such rounds, so it cannot be run here and is NOT claimed")
    print(f"  PLACEBO   unanchored {loose_n} > anchored {len(rev)}: {plac_ok} — the anchor works")
    ctrl_ok = pos_ok and neg_ok and plac_ok
    if not ctrl_ok:
        print("\n  ⛔ a control failed; the share certifies nothing. Exit 2, never 0.")
        return 2

    share = len(rev) / len(eligible) if eligible else 0
    world = (f"A THE LOOP CHECKS ITSELF — {len(rev)} of {len(eligible)} eligible walls were "
             f"revisited ({share:.0%})" if share >= 0.5 else
             f"B THE LOOP DOES NOT — only {len(rev)} of {len(eligible)} ({share:.0%}) were "
             f"revisited; R998's credit to the NEXT line is withdrawn")
    print(f"\n⭐ {world}")
    print(f"\n⚠ ELIGIBILITY IS UNEQUAL BY CONSTRUCTION: R997 had "
          f"{next(r['later_commits'] for r in rows if r['round']==997)} later commits to be checked "
          f"in; R979 had {next(r['later_commits'] for r in rows if r['round']==979)}. The share is "
          f"reported WITH that column, never as a flat rate.")
    print("⚠ AND THIS COUNTS WHETHER A WALL WAS RETURNED TO, NEVER WHETHER THE RETURN WAS RIGHT.")

    out = HERE / "results" / "walls_checked.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head=subprocess.run(["git","rev-parse","HEAD"], cwd=ROOT, capture_output=True,
                            text=True).stdout.strip()[:8],
        n_walls=len(walls), n_eligible=len(eligible), n_revisited=len(rev), share=share,
        n_unanchored=loose_n, rows=rows,
        controls={"positive_r997_revisited": pos_ok, "negative_ghost_id_unrevisited": neg_ok,
                  "placebo_anchor_matters": plac_ok, "all_ok": ctrl_ok,
                  "unavailable_zero_opportunity_control": len(zero_opp) == 0},
        world=world,
        caveats=["eligibility is unequal: later rounds had fewer chances to be checked",
                 "counts whether a wall was returned to, never whether the return was right"],
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
