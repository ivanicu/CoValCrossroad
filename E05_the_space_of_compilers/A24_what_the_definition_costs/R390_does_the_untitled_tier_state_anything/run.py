"""R390 -- the 68 untitled rounds: do they state a finding in their OUTPUT, or nowhere at all?

R389 split the backfill debt in two: 158 of 226 rounds open their docstring with
`rNN -- <one sentence naming what the round is for>`, and 68 do not. For the titled tier the
backfilled sentence is READ. For the untitled tier it would have to be CONSTRUCTED, and a
constructed sentence is where an invented finding comes from.

⛔ SO THE QUESTION IS WHETHER THE UNTITLED TIER IS SILENT, OR MERELY SILENT IN ITS DOCSTRING. R389
   measured a static property of the source. A round can carry no title and still END ITS RUN with a
   verdict it wrote itself -- all three paid units did. If the untitled rounds do too, the title is
   COSMETIC and the tier is cheap. If they do not, then writing a finding for them means inventing
   one, and the honest act is to record that they have none.

⛔ AND THE SAFETY CONSTRAINT IS NOT INCIDENTAL, IT IS WHY THIS ROUND IS BUILT THE WAY IT IS. R389's
   first copy was destroyed by running `_isolated.py` as a script: its selftest plants a saboteur
   that deletes an epoch directory, and it ran against the LIVE TREE -- 1,408 tracked files, plus
   every uncommitted file, which git could not restore. This round therefore manages its own
   worktree with explicit checkout and restore and never imports that module. Subjects run ONLY
   inside the worktree, and the live tree is never the cwd of a subject.

⛔ ARITHMETIC TRAP, answered before the run. Could this come out otherwise? YES. A round with no
   title is free to print a verdict or to print a table and stop. Nothing about lacking a docstring
   title forces either, and the two outcomes recommend opposite actions -- pay the tier, or mark it
   unpayable. What IS partly forced and is controlled: "verdict-shaped line" is a search instrument,
   so it is calibrated on the three rounds already paid, whose answer is known from having read
   their output.

ESTIMAND        over a prefix of the untitled tier: does the round's stdout contain a self-stated
                verdict line -- a line the round wrote to say what it concluded?
                Reported as counts, with every subject's outcome printed.

IDENTIFICATION  Exact for subjects that run. A subject that fails or times out is UNVERIFIED and is
                counted separately, never folded into "silent".
                NOT identified: whether a verdict line is TRUE, or whether a round without one truly
                had no finding. Absence of a stated verdict bounds what can be READ; it does not
                prove there was nothing to say.

SCOPE           population: the untitled rounds R389 identified · instrument: a verdict-shape
                pattern with its own two-sided control · regime: HEAD, in an isolated worktree.

WORLDS
  W-TITLE-COSMETIC   most untitled rounds still state a verdict in their output. The docstring title
                     is cosmetic, the tier is READABLE, and the debt is one project after all.
  W-GENUINELY-SILENT most do not. Writing a finding for them means constructing one, and the honest
                     act is to mark them as having no stated finding rather than manufacture one.
  W-MIXED            both occur -- then the tier splits again and the counts are the estimate.

PREDICTION MATRIX
  W-TITLE-COSMETIC   -> >= 70% of running subjects print a verdict line
  W-GENUINELY-SILENT -> <= 30% do
  W-MIXED            -> between

PRE-REGISTERED KILL -- conditional on the controls, never on the share alone.
    if verdict_pattern_positive_control_ok and verdict_pattern_negative_control_ok:
        s = share of RUNNING subjects whose output carries a verdict line
        if s >= 0.70   -> W-TITLE-COSMETIC
        elif s <= 0.30 -> W-GENUINELY-SILENT
        else           -> W-MIXED
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

CONTROLS
  VERDICT (+)   R21, R24 and R28 -- the three units already paid, whose outputs I have READ and
                which all end in a verdict line -- must be detected. Their answer comes from R389,
                not from this pattern.
  VERDICT (-)   a script that prints only a table of numbers must NOT be detected. Both directions,
                because a pattern matching any line would pass the positive control and mean
                nothing.
  ISOLATION     subjects run only inside a git worktree, checked out and restored explicitly by this
                round. `_isolated.py` is NEVER imported or executed -- running it as a script is
                what destroyed R389's first copy.
  UNVERIFIED    a subject that fails or times out is counted apart from a silent one. A dead round
                is not a quiet round, and merging them would manufacture the silent verdict.

MULTIPLICITY    one share over one prefix; every subject and outcome printed, survivors and not.
SEEDS           none -- execution is the measurement.
ARTIFACT        results/r390_untitled_tier.json with the source hash.

IMPOSSIBLE HERE
  whether a verdict line is TRUE      -- detection is structural; truth is a judgement.
  whether a silent round HAD a finding -- absence bounds what can be READ, nothing more.
  all 68                              -- a prefix is run inside a bounded budget, and the count run
                                         is printed beside the count remaining.
  a second release                    -- one release.

EXIT
    0  controls hold and the tier is classified
    1  a control misbehaved -- UNVERIFIED
    2  too few subjects available or the worktree is unusable -- never a silent pass
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import re
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
PY = ROOT / ".venv" / "bin" / "python"
WT = pathlib.Path("/tmp/claude-1000/-home-ivan/7d277876-c2fd-4a27-9b05-652b391121ff/scratchpad/r390_wt")
R389 = HERE.parent / "R389_the_reading_burden" / "results" / "r389_reading_burden.json"
N_SUBJECTS = 8
TIMEOUT_S = 120
# a line the ROUND wrote to say what it concluded. Anchored on the two forms the corpus uses.
VERDICT = re.compile(r"^\s*(VERDICT\b|->\s*\S|⛔|⭐)", re.M)
PAID = ("R21_donor_distance", "R24_regime_receipt", "R28_multiplicative")
sys.path.insert(0, str(ROOT / "covalx"))
try:
    from stamp import stamp
except Exception:
    def stamp(f):
        return {"source_sha256": hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest(),
                "source_name": pathlib.Path(f).name}


def main() -> int:
    if not R389.exists():
        print("  UNRUNNABLE: R389's artifact absent. Exit 2, never 0."); return 2
    d = json.loads(R389.read_text())
    untitled = sorted(k for k, v in d["rows"].items() if not v["titled"])
    if len(untitled) < 10:
        print(f"  UNRUNNABLE: only {len(untitled)} untitled rounds. Exit 2, never 0."); return 2

    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True,
                          text=True).stdout.strip()
    print(f"R390 · do the untitled rounds state anything?   HEAD {head[:12]}\n")
    print(f"  ⛔ SAFETY FIRST, AND IT IS WHY THIS ROUND IS BUILT THIS WAY. R389's first copy was")
    print(f"     destroyed by running `_isolated.py` as a script — its selftest plants a saboteur")
    print(f"     that deletes an epoch directory, and it ran against the LIVE TREE. This round")
    print(f"     manages its own worktree and NEVER imports or executes that module.\n")

    if not WT.exists():
        r = subprocess.run(["git", "worktree", "add", "--detach", str(WT), head],
                           cwd=str(ROOT), capture_output=True, text=True)
        if r.returncode != 0:
            print(f"  UNRUNNABLE: cannot create worktree ({r.stderr.strip()[:120]}). Exit 2.")
            return 2
    subprocess.run(["git", "checkout", "-f", "-q", head], cwd=str(WT), capture_output=True)
    subprocess.run(["git", "clean", "-fdq"], cwd=str(WT), capture_output=True)

    # ⛔ THE POSITIVE CONTROL CAUGHT A MISSING INPUT, AND IT IS THE SAME ONE `_isolated` DOCUMENTS.
    #   A fresh worktree holds only TRACKED files, so `data/` contains `fetch.py` and none of the
    #   69 MB release, and `.venv` is absent entirely. R21 and R28 load models and died; R24 does
    #   not and ran. Avoiding `_isolated` for safety cost me its input linking, so the linking is
    #   replicated here — PER ENTRY, because a directory git has materialised for a tracked file
    #   must be FILLED IN rather than skipped, which is the exact repair `_isolated` records having
    #   made after every isolated run in its history executed against an empty `data/`.
    def link_inputs():
        for name in ("data", ".venv"):
            src, dst = ROOT / name, WT / name
            if not src.exists():
                continue
            if not dst.exists():
                dst.symlink_to(src, target_is_directory=src.is_dir()); continue
            if src.is_dir() and dst.is_dir():
                for child in src.iterdir():
                    t = dst / child.name
                    if not t.exists() and not t.is_symlink():
                        t.symlink_to(child, target_is_directory=child.is_dir())

    link_inputs()
    print(f"  worktree {WT}  (subjects never run in the live tree; data/ and .venv linked per entry)")

    def run_subject(rel: pathlib.Path):
        t0 = time.monotonic()
        try:
            p = subprocess.run([str(PY), "run.py"], cwd=str(rel), capture_output=True,
                               text=True, timeout=TIMEOUT_S)
        except subprocess.TimeoutExpired:
            return "TIMEOUT", "", time.monotonic() - t0
        out = p.stdout + p.stderr
        if p.returncode != 0:
            return "FAILED", out, time.monotonic() - t0
        return "RAN", out, time.monotonic() - t0

    # ---- CONTROLS ------------------------------------------------------------------------------
    pos = {}
    for name in PAID:
        dd = next((q for q in WT.glob(f"E0*/A*/{name}") if q.is_dir()), None)
        if dd is None:
            pos[name] = None; continue
        cls, out, _ = run_subject(dd)
        pos[name] = bool(VERDICT.search(out)) if cls == "RAN" else None
        subprocess.run(["git", "checkout", "-f", "-q", head], cwd=str(WT), capture_output=True)
        link_inputs()
        subprocess.run(["git", "checkout", "-f", "-q", head], cwd=str(WT), capture_output=True)
    pos_ok = all(v is True for v in pos.values())
    neg_text = "col_a  col_b\n  1.23   4.56\n  7.89   0.12\n"
    neg_ok = not VERDICT.search(neg_text)
    print(f"\n  CONTROLS on the verdict-shape pattern")
    print(f"    VERDICT (+)  the three units already paid are detected: {pos}  "
          f"{'PASS' if pos_ok else 'FAIL'}")
    print(f"    VERDICT (-)  a bare table of numbers is NOT detected: {not bool(VERDICT.search(neg_text))}"
          f"  {'PASS' if neg_ok else 'FAIL'}")
    if not (pos_ok and neg_ok):
        print("\n  UNVERIFIED — the pattern is blind in one direction. Exit 1."); return 1

    # ---- the subjects ---------------------------------------------------------------------------
    subjects = untitled[:N_SUBJECTS]
    print(f"\n  RUNNING {len(subjects)} of {len(untitled)} untitled rounds "
          f"(timeout {TIMEOUT_S}s each)")
    print(f"    {'round':<38}{'outcome':>9}{'secs':>7}   states a verdict?")
    rows = {}
    for name in subjects:
        dd = next((q for q in WT.glob(f"E0*/A*/{name}") if q.is_dir()), None)
        if dd is None:
            rows[name] = dict(outcome="ABSENT", verdict=None, secs=0.0)
            print(f"    {name:<38}{'ABSENT':>9}"); continue
        cls, out, secs = run_subject(dd)
        v = bool(VERDICT.search(out)) if cls == "RAN" else None
        rows[name] = dict(outcome=cls, verdict=v, secs=round(secs, 1), lines=len(out.splitlines()))
        print(f"    {name:<38}{cls:>9}{secs:>7.1f}   "
              f"{'YES' if v else ('no' if v is False else '—')}")
        subprocess.run(["git", "checkout", "-f", "-q", head], cwd=str(WT), capture_output=True)
        link_inputs()

    ran = [k for k, v in rows.items() if v["outcome"] == "RAN"]
    withv = [k for k in ran if rows[k]["verdict"]]
    unver = [k for k, v in rows.items() if v["outcome"] != "RAN"]
    share = len(withv) / len(ran) if ran else 0.0
    print(f"\n    RAN {len(ran)} · UNVERIFIED {len(unver)} · of those that ran, "
          f"{len(withv)} state a verdict ({share:.0%})")
    print(f"    remaining untried in this tier: {len(untitled) - len(subjects)}")

    # ---- VERDICT -------------------------------------------------------------------------------
    print()
    if not ran:
        print("  UNVERIFIED — no subject ran, so nothing about the tier is measured. Exit 1.")
        return 1
    if share >= 0.70:
        print(f"  W-TITLE-COSMETIC — {len(withv)} of {len(ran)} untitled rounds that ran STATE a")
        print(f"  verdict in their output. The docstring title is cosmetic: the tier is READABLE,")
        print(f"  the sentence can be read rather than constructed, and the debt is ONE project")
        print(f"  after all — R389's split was a property of the docstrings, not of the findings.")
        v = "W_TITLE_COSMETIC"
    elif share <= 0.30:
        print(f"  W-GENUINELY-SILENT — only {len(withv)} of {len(ran)} state a verdict. Writing a")
        print(f"  finding for these means CONSTRUCTING one, and the honest act is to mark them as")
        print(f"  having no stated finding rather than to manufacture one.")
        v = "W_GENUINELY_SILENT"
    else:
        print(f"  W-MIXED — {len(withv)} of {len(ran)} ({share:.0%}) state a verdict. The tier")
        print(f"  splits again, and those counts are the estimate rather than the share.")
        v = "W_MIXED"

    print(f"\n  ⚠ DETECTION IS STRUCTURAL, NOT TRUTH. A verdict line may be wrong; this measures")
    print(f"    that the round wrote one, never that it is right.")
    print(f"  ⚠ AND ABSENCE BOUNDS WHAT CAN BE READ, NOT WHAT WAS FOUND. A round with no stated")
    print(f"    verdict may still have had a finding its author never wrote down — which is the")
    print(f"    whole reason this debt exists.")
    print(f"  ⚠ {len(subjects)} of {len(untitled)} run. The remainder is named, not assumed.")

    art = dict(stamp(str(SELF)), head=head[:12], n_untitled=len(untitled),
               n_subjects=len(subjects), rows=rows, ran=ran, with_verdict=withv,
               unverified=unver, share=share,
               controls=dict(verdict_pos=pos, verdict_pos_ok=pos_ok, verdict_neg_ok=neg_ok),
               verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r390_untitled_tier.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
