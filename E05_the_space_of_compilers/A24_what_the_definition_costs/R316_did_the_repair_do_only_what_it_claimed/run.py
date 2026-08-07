"""R316 — did the repair do ONLY what it claimed?

R315 measured 25 of 278 probed rounds unable to resolve their inputs. The repair (commit 97d09f7)
introduced `covalx.legacy.round_dir`, rewrote 21 call sites in 18 rounds to cite siblings by ROUND
ID instead of by epoch-and-arc path, and added `.venv` to the isolation harness's untracked-input
links.

⛔ THE GATE IS NOT "THE PATH EXISTS NOW". That is the check that cannot fail: I edited the path, so
of course it resolves. The question a later round needs answered is whether the edit moved the
rounds it was aimed at AND LEFT EVERYTHING ELSE ALONE — because a path fix that silently changes
another round's classification is a different change than the one I think I made.

⚠ AND THAT GATE IS UNREADABLE WITHOUT A NOISE FLOOR, which is why sweep B exists. 40 of the 300
classifications are TIMEOUT at a 60 s wall clock, and a timeout is not deterministic: under
different machine load a round crosses the boundary either way. Comparing two sweeps and reading
every difference as an effect of the repair would attribute load to code. So the floor was
MEASURED, not assumed, by running the sweep twice with NOTHING changed.

ESTIMAND      the set of rounds whose runnability classification changed between the pre-repair
              sweep (A) and the post-repair sweep (C), partitioned into: the rounds the repair
              targeted, the rounds it did not, and movement attributable to the measured churn.
IDENTIFICATION exact, and this is the unusual part — the churn floor (A vs B, unchanged) showed
              BROKEN-INPUT is DETERMINISTIC: 0 of 25 churned and the broken sets were identical.
              Only TIMEOUT<->REACHED-WRITE moved, 2 of 300. So a BROKEN-INPUT transition is
              attributable and a TIMEOUT transition is not, and the gate is written on that
              asymmetry rather than on a blanket tolerance.
SCOPE         population every `E*/A*/R*/run.py` at the two commits · instrument the R315 probe
              (`sys.addaudithook` on `open`) in a detached git worktree · 60 s wall clock ·
              no GPU, no network.
WORLDS        W-CLEAN     exactly the targeted rounds leave BROKEN-INPUT; everything else is
                          either unchanged or moves within the measured churn class.
              W-OVERREACH some round NOT targeted changes class in a way churn cannot explain ->
                          the edit did more than it claimed and the diff must be re-read.
              W-SHORT     a targeted round does NOT leave BROKEN-INPUT -> the repair is
                          incomplete and the round names its input some other way too.
              W-BOTH      both, reported separately rather than netted.
KILL          pre-registered, conditional on the floor holding:
                targeted-and-moved == targeted AND no untargeted round moves outside the
                  MEASURED churn classes                                              -> W-CLEAN
                any untargeted round moves outside them                               -> W-OVERREACH
                any targeted round stays BROKEN-INPUT                                 -> W-SHORT
              ⚠ THE FIRST VERSION GATED ONLY ON BROKEN-INPUT TRANSITIONS AND WAS WRONG. It
              printed W-CLEAN while R07 and R201 -- two files the repair had EDITED -- went
              REACHED-WRITE -> OTHER-ERROR, a transition absent from the floor and therefore not
              churn. Both were genuine regressions introduced by the repair. The criterion now
              names the churn classes the floor actually produced and treats every other
              untargeted transition as overreach.
              The three cohorts are DERIVED from sweep A by a declared rule, not typed from
              memory — my first draft hard-coded them and got the third set wrong, and a negative
              control keyed to an invented membership list validates nothing. They are disjoint
              and fixed before the comparison, which is why ONE post-repair sweep suffices to
              attribute two bundled changes: a round that raised before any in-repo read can only
              have moved because of the `.venv` link, and a round naming a stale epoch path only
              because of the resolver.
POSITIVE CTRL r144 must leave BROKEN-INPUT. It is the round that motivated the whole line and its
              input path was verified dead and then verified live. If it has not moved, the
              comparison is not measuring the repair and everything else is void.
              Fails at g=0: sweep B is the g=0 arm — the same comparison with NO repair applied
              must show ZERO targeted rounds moving. It showed 0 of 25.
NEGATIVE CTRL the `_archive/` rounds were deliberately NOT repaired: their input is gitignored
              DATA that no setup step recreates, so they genuinely cannot run from a clean clone.
              They must STILL be BROKEN-INPUT. A repair that "fixed" them would have fixed the
              measurement rather than the repository.
NOISE FLOOR   measured: 2 of 300 classifications moved between two unchanged sweeps, both
              TIMEOUT<->REACHED-WRITE, 0 involving BROKEN-INPUT.
MULTIPLICITY  300 rounds compared, every transition class reported with its count.
SEEDS         n/a — the comparison is deterministic given the three artifacts; the floor is the
              replicate.
ARTIFACT      results/repair_gate.json with source hash and the full transition table.
IMPOSSIBLE    proving the repaired rounds now produce CORRECT results. REACHED-WRITE means inputs
              resolved. R144 is the one case taken further, by re-running it and diffing its
              output against its committed artifact — and that diff is a separate finding, not
              part of this gate.
"""
import hashlib, json, pathlib, sys
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
SCRATCH = pathlib.Path("/tmp/claude-1000/-home-ivan/"
                       "7d277876-c2fd-4a27-9b05-652b391121ff/scratchpad")
A_PATH = (SELF.parent.parent / "R315_how_many_rounds_can_still_run"
          / "results" / "runnability.json")
B_PATH = SCRATCH / "sweep_B.json"
# C was the FIRST post-repair sweep and it returned W-OVERREACH: two rounds the repair had edited
# regressed REACHED-WRITE -> OTHER-ERROR. D is the sweep after those regressions were fixed. C is
# kept at scratchpad/gate_AC.json rather than overwritten, because a gate that only ever shows the
# run where it passed is not a gate.
C_PATH = SCRATCH / ("sweep_E.json" if (SCRATCH / "sweep_E.json").exists() else "sweep_C.json")

# ⚠ THE COHORTS ARE DERIVED FROM SWEEP A, NOT TYPED. My first draft hard-coded all three sets
# from memory and got the third wrong -- it listed R255, which was never broken. A hand-written
# membership list IS an answer key, and a negative control keyed to an invented set validates
# nothing. What is DECLARED here is only the RULE that sorts an observed breakage into a cohort;
# the membership is read off the pre-repair artifact, which is an observation and predates the
# repair, so nothing about the outcome can leak into it.
def cohort(missing: str | None) -> str:
    if missing is None:
        return "venv"          # raised before any in-repo read: the worktree had no .venv
    if "_archive" in missing:
        return "archive"       # gitignored DATA -- deliberately NOT repaired
    return "resolver"          # a sibling named by a stale epoch/arc path


def load(p):
    if not p.exists():
        return None
    d = json.loads(p.read_text())
    return {t["path"]: t for t in d["table"]}, d


def main():
    have = [(n, load(p)) for n, p in (("A", A_PATH), ("B", B_PATH), ("C", C_PATH))]
    missing = [n for n, v in have if v is None]
    if missing:
        print(f"  UNRUNNABLE: sweep artifact(s) {missing} absent. This round compares three "
              f"sweeps and cannot be evaluated on fewer."); return 2
    (A, Ad), (B, Bd), (C, Cd) = (v for _, v in have)

    def rid(p):
        return pathlib.Path(p).name.split("_")[0]

    groups = {"resolver": set(), "venv": set(), "archive": set()}
    for k, t in A.items():
        if t["cls"] == "BROKEN-INPUT":
            groups[cohort(t["missing"])].add(rid(k))
    TARGET_RESOLVER, TARGET_VENV = groups["resolver"], groups["venv"]
    EXPECT_STILL_BROKEN = groups["archive"]
    print(f"  COHORTS, derived from sweep A (pre-repair observation, not a typed list)")
    for nm, s_ in (("resolver (targeted)", TARGET_RESOLVER), ("venv link (targeted)", TARGET_VENV),
                   ("archive (deliberately NOT repaired)", EXPECT_STILL_BROKEN)):
        print(f"    {nm:<38}{len(s_):>3}  {sorted(s_)}")
    if not (TARGET_RESOLVER and TARGET_VENV and EXPECT_STILL_BROKEN):
        print("  REFUSING: a cohort is empty; the gate would be vacuous."); return 2
    print()

    # ---- the measured floor (A vs B, nothing changed) ------------------------------------------
    com_ab = set(A) & set(B)
    churn = [(k, A[k]["cls"], B[k]["cls"]) for k in com_ab if A[k]["cls"] != B[k]["cls"]]
    churn_broken = [c for c in churn if "BROKEN-INPUT" in (c[1], c[2])]
    print(f"  NOISE FLOOR — two sweeps, NOTHING changed between them")
    print(f"    {len(churn)} of {len(com_ab)} classifications moved ({len(churn)/len(com_ab):.1%})")
    for (x, y), n in Counter((x, y) for _, x, y in churn).most_common():
        print(f"      {n:>3}  {x} -> {y}")
    print(f"    BROKEN-INPUT churn: {len(churn_broken)}  -> a BROKEN transition is "
          f"{'ATTRIBUTABLE' if not churn_broken else 'NOT attributable'}")
    floor_ok = not churn_broken
    a_bro = {rid(k) for k in A if A[k]["cls"] == "BROKEN-INPUT"}
    b_bro = {rid(k) for k in B if B[k]["cls"] == "BROKEN-INPUT"}
    print(f"    g=0 arm: with NO repair, targeted rounds that moved = "
          f"{len((TARGET_RESOLVER | TARGET_VENV) & (a_bro - b_bro))} of "
          f"{len(TARGET_RESOLVER | TARGET_VENV)}")

    # ---- the repair (A vs C) --------------------------------------------------------------------
    com_ac = set(A) & set(C)
    moved = [(k, A[k]["cls"], C[k]["cls"]) for k in com_ac if A[k]["cls"] != C[k]["cls"]]
    c_bro = {rid(k) for k in C if C[k]["cls"] == "BROKEN-INPUT"}
    print(f"\n  THE REPAIR — sweep A (pre) vs sweep C (post)")
    print(f"    BROKEN-INPUT  {len(a_bro)} -> {len(c_bro)}")
    print(f"    {len(moved)} of {len(com_ac)} classifications moved in total")
    for (x, y), n in Counter((x, y) for _, x, y in moved).most_common():
        print(f"      {n:>3}  {x} -> {y}")

    targeted = TARGET_RESOLVER | TARGET_VENV
    left_broken = a_bro - c_bro
    entered_broken = c_bro - a_bro
    tgt_moved = targeted & left_broken
    tgt_stuck = targeted & c_bro
    untgt_left = left_broken - targeted
    print(f"\n  {'set':<44}{'n':>5}  members")
    rows = [("targeted by the resolver, left BROKEN", TARGET_RESOLVER & left_broken),
            ("targeted by the .venv link, left BROKEN", TARGET_VENV & left_broken),
            ("targeted but STILL BROKEN (W-SHORT)", tgt_stuck),
            ("UNtargeted, left BROKEN (unexplained)", untgt_left),
            ("UNtargeted, ENTERED BROKEN (W-OVERREACH)", entered_broken - targeted),
            ("deliberately not repaired, still BROKEN", EXPECT_STILL_BROKEN & c_bro)]
    for nm, s in rows:
        print(f"    {nm:<44}{len(s):>5}  {sorted(s) if len(s) <= 14 else str(sorted(s))[:60]}")

    # ⚠ UNTARGETED REGRESSION IN ANY CLASS, not only BROKEN-INPUT. The first version of this
    # gate branched solely on BROKEN transitions and printed W-CLEAN while TWO untargeted rounds
    # went REACHED-WRITE -> OTHER-ERROR: R07 and R201, both files the repair had EDITED, both
    # stable across the A/B floor, so neither was churn. `realstat §4 · the verdict string is not
    # a computation` -- the branch did not reference every transition the round had already
    # printed three lines above. The regressions were real: the import-anchor heuristic put the
    # import AFTER its own use in one file, and before covalx was importable in the other. The
    # gate built to catch exactly this said CLEAN.
    CHURN_CLASSES = {("TIMEOUT", "REACHED-WRITE"), ("REACHED-WRITE", "TIMEOUT")}
    regressed = [(k, x, y) for k, x, y in moved
                 if rid(k) not in targeted and (x, y) not in CHURN_CLASSES]
    # DIRECTION IS COMPUTED, NOT TYPED. An untargeted move is overreach either way -- the
    # pre-registered criterion does not get relaxed because I like the direction -- but calling
    # an improvement "the edit did more than it claimed" without saying WHICH WAY is the same
    # error as a hard-coded `over`/`under` in a verdict string. FAIL = the file did not resolve
    # its inputs; OK = it did. TIMEOUT is neither and is reported as UNCLEAR.
    FAIL, OK = {"BROKEN-INPUT", "OTHER-ERROR"}, {"REACHED-WRITE", "COMPLETED"}
    def direction(x, y):
        if x in FAIL and y in OK:
            return "IMPROVED"
        if x in OK and y in FAIL:
            return "REGRESSED"
        return "UNCLEAR"
    print(f"\n  UNTARGETED MOVEMENT OUTSIDE THE MEASURED CHURN CLASSES: {len(regressed)}")
    for k, x, y in regressed:
        print(f"    {pathlib.Path(k).name:<46}{x} -> {y}   {direction(x, y)}")
    dirs = Counter(direction(x, y) for _, x, y in regressed)
    if regressed:
        print(f"    direction: {dict(dirs)}  -- still overreach, and still reported as such")
    if not regressed:
        print(f"    (churn classes seen in the floor: "
              f"{sorted({f'{x}->{y}' for _, x, y in churn})})")

    pos_ok = "R144" in left_broken
    neg_ok = bool(EXPECT_STILL_BROKEN & c_bro)
    print(f"\n  POSITIVE  r144 left BROKEN-INPUT: {pos_ok}")
    print(f"  NEGATIVE  deliberately-unrepaired rounds still BROKEN: {neg_ok}")

    # ---- KILL ------------------------------------------------------------------------------------
    ctrl = floor_ok and pos_ok and neg_ok
    over = bool((entered_broken - targeted) or untgt_left or regressed)
    short = bool(tgt_stuck)
    print("\n  " + "=" * 78)
    print(f"  CONTROLS  floor={floor_ok}  positive={pos_ok}  negative={neg_ok}  -> "
          f"{'evaluate' if ctrl else 'UNVERIFIED'}")
    if not ctrl:
        world = "UNVERIFIED"
        print("  -> UNVERIFIED. A control misbehaved; the comparison is not readable.")
    elif over and short:
        world = "W-BOTH"
        print(f"  -> W-BOTH. {len(tgt_stuck)} targeted rounds did not move AND "
              f"{len(entered_broken - targeted) + len(untgt_left)} untargeted rounds changed.")
        print("     Reported separately rather than netted: they are different defects.")
    elif over:
        world = "W-OVERREACH"
        # DEDUPED. The first version summed three overlapping sets and printed "2 rounds" while
        # listing one: R165 was in both `entered_broken - targeted` and `regressed`. A count and
        # a list that disagree in the same sentence is the verdict string not being a computation.
        n_over = len({rid(k) for k, _, _ in regressed} | untgt_left | (entered_broken - targeted))
        print(f"  -> W-OVERREACH. {n_over} rounds the repair did not target changed class in a")
        print("     way the measured churn cannot explain. The edit did more than it claimed:")
        for k, x, y in regressed:
            print(f"       {pathlib.Path(k).name:<44}{x} -> {y}   {direction(x, y)}")
        if dirs and not dirs.get("REGRESSED"):
            print("     ⚠ NONE of them regressed -- every untargeted move IMPROVED or is")
            print("       UNCLEAR. The verdict stands because the criterion was pre-registered")
            print("       over untargeted movement, not over damage, and relaxing it here")
            print("       because the direction is flattering is how a gate stops working.")
    elif short:
        world = "W-SHORT"
        print(f"  -> W-SHORT. {sorted(tgt_stuck)} stayed BROKEN. The repair is incomplete —")
        print("     those rounds name their input some other way as well.")
    else:
        world = "W-CLEAN"
        print(f"  -> W-CLEAN. Exactly the {len(tgt_moved)} targeted rounds left BROKEN-INPUT, no")
        print(f"     untargeted round entered or left it, and the remaining {len(moved) - len(tgt_moved)}")
        print(f"     movements are all in the measured churn classes "
              f"{sorted({f'{x}->{y}' for _, x, y in churn})}, floor {len(churn)}/{len(com_ab)}.")
        print(f"     BROKEN-INPUT {len(a_bro)} -> {len(c_bro)}; what remains is the "
              f"{len(EXPECT_STILL_BROKEN & c_bro)} rounds whose input is")
        print("     gitignored DATA that no setup step recreates — a real reproducibility hole,")
        print("     left standing deliberately rather than fixed out of the measurement.")
    print("  " + "=" * 78)

    o = SELF.parent / "results" / "repair_gate.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(SELF.read_bytes()).hexdigest()[:16], world=world,
        floor=dict(moved=len(churn), of=len(com_ab), broken_churn=len(churn_broken),
                   classes={f"{x}->{y}": n for (x, y), n in
                            Counter((x, y) for _, x, y in churn).items()}),
        broken_before=sorted(a_bro), broken_after=sorted(c_bro),
        targeted_resolver=sorted(TARGET_RESOLVER), targeted_venv=sorted(TARGET_VENV),
        targeted_moved=sorted(tgt_moved), targeted_stuck=sorted(tgt_stuck),
        untargeted_left=sorted(untgt_left),
        untargeted_entered=sorted(entered_broken - targeted),
        untargeted_regressed=[[k, x, y, direction(x, y)] for k, x, y in regressed],
        untargeted_direction=dict(dirs),
        churn_classes=sorted({f"{x}->{y}" for _, x, y in churn}),
        still_broken_by_design=sorted(EXPECT_STILL_BROKEN & c_bro),
        transitions={f"{x}->{y}": n for (x, y), n in
                     Counter((x, y) for _, x, y in moved).items()},
        counts_before=Ad["counts"], counts_after=Cd["counts"],
        positive_ok=bool(pos_ok), negative_ok=bool(neg_ok), floor_ok=bool(floor_ok)), indent=1))
    print(f"\n  artifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
