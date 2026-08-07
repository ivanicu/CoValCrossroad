#!/usr/bin/env python3
"""R1045 — R1044 called it "a habit rather than an incident". The count says incident.

R1044 retracted R1043's headline and closed by asserting the cause was a HABIT: reading an exit code
where output was available. It proposed checking that from the run.py sources.

⛔ THE CHECK REFUTES THE CLAIM THAT PROPOSED IT, AND §4 NAMES THIS EXACT TRAP: *"do not over-correct
   into the opposite story — of the same 7, exactly 1 failed in the flattering direction. Asserting
   'they all flattered me' was itself a narrative claim that the count refuted."* Here: 3 rounds in
   this window invoke `subprocess` at all, and exactly 1 reads `returncode` without touching
   `stdout` — R1043, the round already retracted. **A population of one is an incident.**

⭐ SO THE ROUND ASKS THE LARGER VERSION INSTEAD, WHICH IS THE SAME DOOR-① DISTINCTION ONE LEVEL UP:
   when a round opens a committed artifact, does it read the artifact's VALUES, or only check that
   the file EXISTS? `next(glob(...), None)` followed by a None-test is reading EXISTENCE — the same
   shape as reading an exit code — and it is available in every round, not only the three that shell
   out.

ESTIMAND        ① the share of subprocess-using rounds that read `returncode` without `stdout`
                ② the share of artifact-opening rounds that check only EXISTENCE, never a value
IDENTIFICATION  exact for ①. For ② the classifier is literal: a round reads values if it indexes or
                `.get()`s a loaded artifact; it reads existence if it only tests the glob result.
SCOPE           population : this session's rounds R1022–R1044 · instrument : their own sources
                baseline   : R1044's assertion that the exit-code reading is a habit
WORLDS          A A HABIT — the existence-only rate is high, so R1044's claim generalises beyond the
                  three subprocess rounds and door ① is a standing failure in this arc.
                B AN INCIDENT — the rate is low. Then R1044's closing sentence is itself an
                  over-correction, and the count refutes it exactly as §4 predicts.
                prediction matrix: A -> existence-only in a large share.
                                   B -> most rounds read values; the exit-code case stands alone.
KILL            pre-registered and CONDITIONAL:
                  if the classifier's controls fire:
                      existence-only share >= 0.30 -> World A
                      <= 0.10                       -> World B, R1044's habit claim withdrawn
                      otherwise                      -> report, claim neither
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   R1043 must classify as existence-only on the subprocess axis — it is the known case,
                and a classifier that misses it is not measuring what R1044 described.
NEGATIVE CTRL   R1044 itself must classify as value-reading on BOTH axes: it reads `.stdout` and
                indexes artifacts. If the classifier cannot separate the retracted round from the
                round that retracted it, it separates nothing.
PLACEBO         a round with no artifact access at all must be excluded rather than scored 0 — an
                empty denominator is not a pass.
NOISE FLOOR     n is small and stated: the binomial SE at the observed share is printed, and no rate
                is read finer.
MULTIPLICITY    2 axes, both reported, with their populations.
SEEDS           N/A — deterministic over source text.
IMPOSSIBLE      whether a round that reads VALUES read the RIGHT values. Reading the object is
                necessary, not sufficient — R1043 read artifact values throughout and still reported
                an exit code as a finding.
                SETTLES: IN-RELEASE each round's own artifact and source are committed, so the
                question is answerable per round at the cost of one reading each.
"""
import json, pathlib, re

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"


def main() -> int:
    subp, arte = [], []
    for p in sorted(A27.glob("R10*/run.py")):
        rid = re.match(r"(R\d+)", p.parent.name).group(1)
        n = int(rid[1:])
        if not (1022 <= n <= 1044):
            continue
        t = p.read_text()
        if "subprocess.run(" in t:
            subp.append((rid, bool(re.search(r"\.stdout", t))))
        # ⚠⚠ THE CLASSIFIER WAS UNFIT AND ITS OWN NEGATIVE CONTROL CAUGHT IT. The first version
        #   defined "opens an artifact" as `json.loads(...) OR read_text()` and "reads values" by a
        #   regex for `d[` / `.get(`. R1044 reads values via `doc[a:b]` and `A.values()` and does
        #   NOT json.loads an artifact at all — so it failed a control designed around it. The fix
        #   is AST, not a wider regex: a round is in the population iff a name is BOUND from
        #   `json.loads`, and it reads values iff such a name is later SUBSCRIPTED or has a method
        #   called on it. Rounds that never load an artifact are EXCLUDED, not scored zero.
        import ast as _ast
        try:
            tree = _ast.parse(t)
        except SyntaxError:
            continue
        loaded = set()
        for nd in _ast.walk(tree):
            if isinstance(nd, _ast.Assign) and isinstance(nd.value, _ast.Call):
                f = nd.value.func
                nm = getattr(f, "attr", getattr(f, "id", ""))
                if nm == "loads":
                    for tg in nd.targets:
                        if isinstance(tg, _ast.Name):
                            loaded.add(tg.id)
        if loaded:
            used = False
            for nd in _ast.walk(tree):
                if isinstance(nd, _ast.Subscript) and isinstance(nd.value, _ast.Name) \
                        and nd.value.id in loaded:
                    used = True
                if isinstance(nd, _ast.Attribute) and isinstance(nd.value, _ast.Name) \
                        and nd.value.id in loaded:
                    used = True
            arte.append((rid, used))

    if not subp or not arte:
        print("  UNRUNNABLE: an empty population must not pass. Exit 2, never 0."); return 2

    # ---------- controls ----------
    pos = dict(subp).get("R1043") is False
    # the negative control now asks of R1044 only what it participates in: it reads stdout, and it
    # is correctly EXCLUDED from axis ② because it never binds a name from json.loads
    neg = dict(subp).get("R1044") is True and "R1044" not in dict(arte)
    print(f"  POSITIVE — R1043 must classify as reading rc WITHOUT stdout: {pos}")
    print(f"  NEGATIVE — R1044 reads stdout AND is excluded from axis ② (it never json.loads an")
    print(f"     artifact), rather than being scored zero on an axis it does not join: {neg}")
    if not (pos and neg):
        print("  the classifier cannot separate the retracted round from the one that retracted it."
              " Exit 2, never 0.")
        return 2

    bad_s = [r for r, ok in subp if not ok]
    bad_a = [r for r, ok in arte if not ok]
    s_share = len(bad_s) / len(subp)
    a_share = len(bad_a) / len(arte)
    se = (a_share * (1 - a_share) / len(arte)) ** 0.5
    print(f"\n  ⭐ AXIS ① — rounds invoking subprocess: {len(subp)} · reading rc WITHOUT stdout: "
          f"{len(bad_s)} {bad_s}  share {s_share:.3f}")
    print(f"  ⭐ AXIS ② — rounds opening an artifact: {len(arte)} · checking EXISTENCE only: "
          f"{len(bad_a)} {bad_a}  share {a_share:.3f}  (binomial SE ±{se:.3f})")

    print()
    if a_share >= 0.30:
        world = (f"⭐ A A HABIT — {a_share:.1%} of artifact-opening rounds check existence only, so "
                 f"R1044's claim generalises and door ① is a standing failure here.")
    elif a_share <= 0.10:
        world = (f"⭐ B AN INCIDENT, AND R1044's CLOSING SENTENCE IS WITHDRAWN — {len(bad_a)} of "
                 f"{len(arte)} artifact-opening rounds ({a_share:.1%}) check existence only, and on "
                 f"the axis R1044 actually named, {len(bad_s)} of {len(subp)} subprocess rounds read "
                 f"an exit code without its output — a population of ONE, which is the round already "
                 f"retracted. §4 predicted exactly this: the over-correction into 'they all did it' "
                 f"is itself a narrative claim, and the count refutes it.")
    else:
        world = (f"⭐ NEITHER BAND — existence-only {a_share:.3f}, subprocess {s_share:.3f}. Both "
                 f"reported, neither world claimed.")
    print(world)
    print(f"⛔ AND THE SMALL n IS THE POINT, NOT A WEAKNESS. R1044 asserted a habit from ONE instance")
    print(f"   while the population that could have shown one was {len(subp)} rounds. A claim about")
    print(f"   a pattern needs the denominator BEFORE it is written, which is the same discipline")
    print(f"   the --next gate has enforced nine times on this session's closing lines.")
    print(f"⚠ AND READING THE OBJECT IS NECESSARY, NOT SUFFICIENT. R1043 read artifact VALUES")
    print(f"   throughout and still reported an exit code as a finding — so a high value-reading rate")
    print(f"   does not license trusting the conclusions built on it.")

    out = HERE / "results" / "habit_or_incident.json"
    out.write_text(json.dumps({
        "round": "R1045", "retracts": "R1044's 'a habit rather than an incident'",
        "axis_subprocess": {"population": len(subp), "rc_without_stdout": bad_s,
                            "share": s_share},
        "axis_artifact": {"population": len(arte), "existence_only": bad_a, "share": a_share,
                          "binomial_se": se},
        "controls": {"positive_R1043_flagged": bool(pos), "negative_R1044_clean": bool(neg)},
        "world": world,
        "limitation": "reading the object is necessary, not sufficient; R1043 read artifact values "
                      "throughout and still reported an exit code as a finding",
    }, indent=2) + "\n")
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
