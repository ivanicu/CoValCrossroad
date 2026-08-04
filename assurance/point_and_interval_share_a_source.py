"""A point estimate and its interval must be computed from the SAME array.

R141_verification publishes, in one dict literal:

    "delta_mean": float(np.mean(ds)),                                  # ds: all 5 seeds
    "ci":         [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]   # bs: seed 0

`ds` and `bs` are different arrays. The mean averages five matched samples; the interval brackets
one of them. Both numbers are individually correct and only their PAIRING is wrong, which is why
every artifact-level gate in this suite is blind to it: the values are internally plausible, the
keys are adjacent, and nothing in the JSON records which array each came from. It surfaced only
where the displacement happened to exceed the CI half-width -- 6 of 14 nodes -- while all 14 were
displaced by 4.5 to 9.5 seed-sd.

So this check reads the SOURCE, not the artifact. For every dict literal in every round's `run.py`
it pairs a mean-like key with an interval-like key and compares the variable names each value is
built from. Disjoint name sets is the signature.

⚠ THIS IS A SEARCH, AND §4 SAYS A SEARCH IS A MEASURING INSTRUMENT WITH NO POSITIVE CONTROL BY
DEFAULT. Three things are therefore built in rather than promised:

  1. POSITIVE CONTROL ON A REAL CASE. R141_verification is a KNOWN positive, diagnosed from its own
     source and annotated in its README. If this check stops flagging R141 it has drifted, and a
     clean run from it afterwards would be silence.
  2. NEGATIVE CONTROL, SYNTHETIC. A dict whose mean and CI are built from the SAME name must not be
     flagged, and one built from different names must be -- both planted, both asserted.
  3. THE VERDICT IS `CANDIDATE`, NOT `DEFECT`. A pair can legitimately draw on different names --
     `ci` from a bootstrap array and the mean from the observed statistic is correct practice when
     the bootstrap is centred on that same statistic. This check cannot tell those apart, and it
     says so on every run. It reports where to look. It does not convict.

EXIT
    0  the positive control fires, the negatives behave, candidates are reported
    1  the instrument has drifted -- it no longer flags R141, or a planted case misbehaves
    2  no round sources found: an empty population, never a silent pass
"""
from __future__ import annotations
import ast
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
KNOWN_POSITIVE = "R141_verification"
MEANISH = re.compile(r"(^|_)(mean|delta|estimate|effect|point|centre|center)($|_)", re.I)
CIISH = re.compile(r"(^|_)(ci|interval|bounds?|bracket)($|_)", re.I)


def names_in(node: ast.AST) -> set[str]:
    """DATA names only. ⚠ v1 returned every ast.Name, so `np` and `float` appeared on both sides of
    every pair and the sets were almost never disjoint -- the synthetic control reported
    `different-array flagged=0 (want 1)`, and R141's PASS was therefore fired by some OTHER pair in
    that file rather than by the `ds`/`bs` defect the check was built on. A positive control that
    passes for the wrong reason is §4's `a control that shares the instrument's blind spot`, and it
    licenses nothing. Names in CALL POSITION are functions and modules, not data, so they are
    removed structurally rather than by a hand-written stoplist."""
    called = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Call):
            f = n.func
            while isinstance(f, ast.Attribute):
                f = f.value
            if isinstance(f, ast.Name):
                called.add(f.id)
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)} - called


def scan_source(src: str) -> list[tuple[str, str, set[str], set[str]]]:
    """Every dict literal pairing a mean-like key with a CI-like key, whose value name-sets are
    DISJOINT. Returns (mean_key, ci_key, mean_names, ci_names)."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        means, cis = [], []
        for k, v in zip(node.keys, node.values):
            if not isinstance(k, ast.Constant) or not isinstance(k.value, str):
                continue
            if CIISH.search(k.value):
                cis.append((k.value, names_in(v)))
            elif MEANISH.search(k.value):
                means.append((k.value, names_in(v)))
        for mk, mn in means:
            for ck, cn in cis:
                if mn and cn and not (mn & cn):
                    out.append((mk, ck, mn, cn))
    return out


def positive_control() -> tuple[bool, str]:
    """Planted, both directions. Same name -> must NOT flag. Different names -> MUST flag."""
    same = 'x = {"delta_mean": float(np.mean(ds)), "ci": [np.percentile(ds, 2.5)]}'
    diff = 'x = {"delta_mean": float(np.mean(ds)), "ci": [np.percentile(bs, 2.5)]}'
    a, b = scan_source(same), scan_source(diff)
    ok = (not a) and len(b) == 1
    return ok, f"same-array flagged={len(a)} (want 0), different-array flagged={len(b)} (want 1)"


def main() -> int:
    srcs = sorted(ROOT.glob("E0*/**/run.py"))
    if not srcs:
        print("  UNRUNNABLE: no round sources found. Exit 2, never 0.")
        return 2

    pc_ok, pc_detail = positive_control()
    print(f"  synthetic control: {pc_detail} -> {'PASS' if pc_ok else 'FAIL'}")

    hits = {}
    for p in srcs:
        found = scan_source(p.read_text(encoding="utf-8", errors="replace"))
        if found:
            hits[p.relative_to(ROOT).as_posix()] = found

    # ⚠ THE CONTROL'S UNIT MUST EQUAL THE CLAIM'S UNIT. v1 asserted only that R141's FILE appeared
    # in the hit list -- and it did, via `rater_style_null_mean`/`krippendorff_alpha_interval`,
    # a DIFFERENT pair. The diagnosed defect is the ('delta_mean', 'ci') pair, so the control now
    # requires THAT pair, with `ds` on the mean side and `bs` on the interval side. Asserting the
    # file while claiming the pair is §4's blind-spot control wearing a green light, and it is the
    # second time in this one file that the same shape got through.
    r141 = [v for k, v in hits.items() if KNOWN_POSITIVE in k]
    known_pair = [(mk, ck, mn, cn) for h in r141 for mk, ck, mn, cn in h
                  if mk == "delta_mean" and ck == "ci"]
    known_ok = any("ds" in mn and "bs" in cn for _, _, mn, cn in known_pair)
    print(f"  real control: the DIAGNOSED pair ('delta_mean' <- ds, 'ci' <- bs) in "
          f"{KNOWN_POSITIVE} is flagged -> "
          f"{'PASS' if known_ok else 'FAIL — the instrument does not find the defect it was built on'}")
    if known_pair:
        for mk, ck, mn, cn in known_pair[:1]:
            print(f"      {mk!r} <- {sorted(mn)}   |   {ck!r} <- {sorted(cn)}")

    print(f"\n  {len(srcs)} round sources scanned, {len(hits)} carry a mean/interval pair built "
          f"from DISJOINT variable names\n")
    for path in sorted(hits):
        for mk, ck, mn, cn in hits[path][:2]:
            mark = "  <-- KNOWN, diagnosed at R340" if KNOWN_POSITIVE in path else ""
            print(f"    {path}")
            print(f"        {mk!r} <- {sorted(mn)}   |   {ck!r} <- {sorted(cn)}{mark}")

    print("\n  ⚠ THESE ARE CANDIDATES, NOT DEFECTS. A mean taken from the observed statistic beside")
    print("    a CI from a bootstrap array is CORRECT practice when the bootstrap is centred on that")
    print("    same statistic, and this check cannot tell that apart from R141's case, where the")
    print("    mean averaged five matched samples and the interval bracketed one. It reports where")
    print("    to look; the artifact's own displacement from the interval's CENTRE is what decides.")

    if not pc_ok or not known_ok:
        print("\n  DRIFTED: a control misbehaved, so a clean list here would be silence.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
