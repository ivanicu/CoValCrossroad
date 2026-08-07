"""R384 — the document the campaign designates as holding its findings names 22% of its rounds.

Four rounds have now converged on the same wall from different directions. R380 found the donor
gate's GATE 2 vacuous because the README stopped being a per-round table. R382 confirmed the same
vacancy with a second instrument. R383 tested three replacement sites and found the one that clears
every quantitative bar is an index of QUESTIONS. R383's NEXT named the assumption underneath all
four: **that a per-round finding is written down somewhere.** This tests that assumption over the
whole corpus rather than over fourteen rounds.

⭐ AND THE SITES ARE NOT MY CHOICE -- THE CAMPAIGN'S OWN DOCUMENTS NAME THEM. Every arc README says,
   in its own words:
       "Table of contents only. Each round's README states its design; the finding lives in
        ../../README.md"
   So the design belongs in the round's own README and the FINDING belongs in the root README. That
   removes the failure R383 walked into: there, I chose three candidate sites and my criterion for
   ranking them turned out to be on the wrong quantity. Here the corpus specifies the sites and the
   only question is whether they are populated.

⛔ ARITHMETIC TRAP, answered before the run. Could this come out otherwise? YES. The root README
   could name every round -- it is a document I have been appending to all session, one paragraph per
   round, and nothing prevents it from covering all of them. What it actually covers is the
   measurement. Note the direction of the bias if any: the rounds I have written this session ARE in
   it, so the recent tail is covered by construction and the number is if anything FLATTERING.

ESTIMAND        over every round directory in the campaign:
                  (a) does its OWN README exist?            (the campaign's designated DESIGN site)
                  (b) is it named in the root README?       (the campaign's designated FINDING site)
                  (c) how many have NEITHER?
                and the same three counts restricted to rounds that PRODUCED an artifact, since a
                round with results is one that has something to report.

IDENTIFICATION  Exact -- file existence and substring presence are enumerations, not samples.
                NOT identified: whether a round SHOULD have a finding written down. A round that
                produced nothing may legitimately have nothing to state, which is why the artifact
                restriction is measured separately rather than assumed either way.

SCOPE           population: every `E0*/A*/R*` directory · instrument: file existence + substring ·
                baseline: the campaign's own stated structure · regime: HEAD.

WORLDS
  W-FINDINGS-UNWRITTEN  most rounds have no root-README paragraph. The campaign's findings are not
                        written where the campaign says they live, every gate that rules on that
                        document is ruling on a fraction, and the nine remaining red gates are one
                        problem rather than nine.
  W-FINDINGS-WRITTEN    most do. Then the four rounds of vacancy findings are local to the donor
                        registry and the assumption underneath them was sound.
  W-DESIGN-ONLY         round READMEs are near-complete while root mentions are not -- the design is
                        recorded and the finding is not, which is a different repair from either.

PREDICTION MATRIX
  W-FINDINGS-UNWRITTEN -> root-README coverage < 50%
  W-FINDINGS-WRITTEN   -> root-README coverage >= 50%
  W-DESIGN-ONLY        -> own-README coverage >= 80% while root coverage < 50%

PRE-REGISTERED KILL -- conditional on the controls, never on a count alone.
    if positive_control_ok and negative_control_ok:
        r = share of rounds named in the root README
        d = share with their own README
        if r >= 0.50               -> W-FINDINGS-WRITTEN
        elif d >= 0.80 and r < 0.50 -> W-DESIGN-ONLY
        else                        -> W-FINDINGS-UNWRITTEN
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.
⚠ The 50% is not a discovery threshold, it is the point at which a document describes more of its
  subject than it omits. Stated so it cannot be mistaken for an effect size.

CONTROLS
  POSITIVE   rounds this session wrote paragraphs for (R380-R383) MUST count as named in the root
             README. Their answer is known independently -- I wrote them -- so a census that missed
             them would be broken in the direction that matters.
  NEGATIVE   `R106_share_level_under_redraw` and `R109_donor_arm_is_text_blind` MUST count as
             lacking their own README. R380 established that by listing their directories, before
             this question existed. Both directions, because a census that reported everything
             present would pass the positive control and mean nothing.
  SELF       this round's own directory is excluded. R382's negative control failed for exactly
             this, and R383 repeated the guard; it is now standard rather than a discovery.
  EMPTY      fewer than 100 round directories -> exit 2. A coverage fraction over a lost population
             is the failure this whole line of rounds is about.

MULTIPLICITY    a census, not a test family. Every count printed, and the artifact-restricted
                subgroup printed beside the whole so neither can hide the other.
SEEDS           none -- deterministic.
ARTIFACT        results/r384_finding_sites.json with the source hash.

IMPOSSIBLE HERE
  whether a round SHOULD state a finding  -- a judgement; the artifact restriction is the closest
                                             objective proxy and is reported separately.
  whether existing text IS a finding      -- R383 showed a site can exist and hold a question. This
                                             counts SITES, and the question-mark rate is reported
                                             beside them rather than folded in.
  a second release                        -- one release.

EXIT
    0  controls hold and the corpus is classified
    1  a control misbehaved -- UNVERIFIED
    2  the population is too small to be the corpus -- never a silent pass
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
sys.path.insert(0, str(ROOT / "covalx"))
try:
    from stamp import stamp                                  # noqa: E402
except Exception:                                            # pragma: no cover
    def stamp(f):
        return {"source_sha256": hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest(),
                "source_name": pathlib.Path(f).name}

POS = ["R380_the_gate_convicted_a_registry_it_never_read",
       "R381_do_the_red_gates_share_a_dead_path",
       "R382_does_the_pattern_match_anything",
       "R383_test_the_proxy_before_adopting_it"]
NEG = ["R106_share_level_under_redraw", "R109_donor_arm_is_text_blind"]


def main() -> int:
    rounds = sorted(p for p in ROOT.glob("E0*/A*/R*")
                    if p.is_dir() and p != HERE and not p.name.startswith("_"))
    if len(rounds) < 100:
        print(f"  UNRUNNABLE: only {len(rounds)} round directories. A coverage fraction over a lost")
        print(f"  population is the failure this line of rounds is about. Exit 2, never 0.")
        return 2
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True,
                          text=True).stdout.strip()[:12]
    root_txt = (ROOT / "README.md").read_text()
    print(f"R384 · where the findings are not   HEAD {head}\n")
    print(f"  ⭐ THE SITES ARE THE CAMPAIGN'S OWN, quoted from any arc README:")
    print(f"     \"Each round's README states its design; the finding lives in ../../README.md\"")
    print(f"     So this round chooses nothing — R383's failure was choosing sites and then")
    print(f"     ranking them on the wrong quantity.\n")

    rows = {}
    for d in rounds:
        res = d / "results"
        rows[d.name] = dict(
            own_readme=(d / "README.md").exists(),
            in_root=(d.name in root_txt),
            has_artifact=bool(res.is_dir() and any(res.iterdir())),
        )

    # ---- CONTROLS ------------------------------------------------------------------------------
    pos_ok = all(rows.get(r, {}).get("in_root") for r in POS if r in rows)
    pos_n = sum(1 for r in POS if r in rows)
    neg_ok = all(rows.get(r, {}).get("own_readme") is False for r in NEG if r in rows)
    neg_n = sum(1 for r in NEG if r in rows)
    print(f"  CONTROLS, both against answers established BEFORE this question")
    print(f"    POSITIVE  {pos_n} rounds I wrote paragraphs for this session are all named in the")
    print(f"              root README: {pos_ok}  {'PASS' if pos_ok and pos_n else 'FAIL'}")
    print(f"    NEGATIVE  {neg_n} rounds R380 listed as having no README of their own still lack")
    print(f"              one: {neg_ok}  {'PASS' if neg_ok and neg_n else 'FAIL'}")
    if not (pos_ok and pos_n and neg_ok and neg_n):
        print("\n  UNVERIFIED — the census is blind in one direction. Exit 1."); return 1

    n = len(rows)
    own = sum(1 for r in rows.values() if r["own_readme"])
    inroot = sum(1 for r in rows.values() if r["in_root"])
    neither = sum(1 for r in rows.values() if not r["own_readme"] and not r["in_root"])
    art = [k for k, r in rows.items() if r["has_artifact"]]
    a_own = sum(1 for k in art if rows[k]["own_readme"])
    a_root = sum(1 for k in art if rows[k]["in_root"])
    a_neither = sum(1 for k in art if not rows[k]["own_readme"] and not rows[k]["in_root"])

    print(f"\n  THE CENSUS — {n} round directories")
    print(f"    {'':<34}{'all rounds':>18}{'produced an artifact':>24}")
    print(f"    {'has its OWN README (design)':<34}{own:>8} {own/n:>8.0%}"
          f"{a_own:>14} {a_own/len(art):>8.0%}")
    print(f"    {'named in root README (finding)':<34}{inroot:>8} {inroot/n:>8.0%}"
          f"{a_root:>14} {a_root/len(art):>8.0%}")
    print(f"    {'NEITHER':<34}{neither:>8} {neither/n:>8.0%}"
          f"{a_neither:>14} {a_neither/len(art):>8.0%}")
    print(f"    rounds that produced an artifact: {len(art)} of {n}")

    r_share, d_share = inroot / n, own / n

    # ---- VERDICT -------------------------------------------------------------------------------
    print()
    if r_share >= 0.50:
        print(f"  W-FINDINGS-WRITTEN — {r_share:.0%} of rounds are named in the document the")
        print(f"  campaign says holds its findings. The four vacancy findings are local to the")
        print(f"  donor registry and the assumption underneath them was sound.")
        v = "W_FINDINGS_WRITTEN"
    elif d_share >= 0.80:
        print(f"  W-DESIGN-ONLY — {d_share:.0%} of rounds record their DESIGN in their own README")
        print(f"  while only {r_share:.0%} are named in the root README. The design is recorded and")
        print(f"  the finding is not, which is a different repair from either alternative.")
        v = "W_DESIGN_ONLY"
    else:
        print(f"  W-FINDINGS-UNWRITTEN — the root README names {inroot} of {n} rounds "
              f"({r_share:.0%}), and")
        print(f"  {own} ({d_share:.0%}) have a README of their own. **{neither} rounds "
              f"({neither/n:.0%}) have NEITHER.**")
        print(f"  ⛔ So the document the campaign designates as holding its findings describes a")
        print(f"     minority of them. Every gate that rules on that document is ruling on a")
        print(f"     FRACTION, and reporting a verdict over a fraction as though it covered the")
        print(f"     corpus is the shape of failure four consecutive rounds have now found.")
        print(f"  ⭐ Which makes the nine remaining red gates ONE problem rather than nine: not a")
        print(f"     dead path, not a stale pattern, not a coupling — a corpus whose findings were")
        print(f"     never written where its own documents say they live.")
        v = "W_FINDINGS_UNWRITTEN"

    # ⭐ THE CONSEQUENCE FOR A GATE THAT IS GREEN, computed rather than asserted. The passing gate
    #   `every_round_reaches_the_readme` accepts the root README **OR the round's own ARC README**,
    #   and R383 measured that an arc row is an index entry -- often a QUESTION. So a round can
    #   satisfy `reaches the readme` while having no finding site at all.
    #   ⚠ AND THE GATE SAYS SO ITSELF, which is the part that matters: its docstring reads
    #     "read the pass honestly: this check passes today because generate_round_index.py wrote
    #      those arc tables in the same session. That is a CONSTRUCTION, not a discovery, and it is
    #      weak evidence of the property."
    #   The confession was written. What was never done is measure how much it admits. That is the
    #   `a confession is never audited` failure, and four rounds this session walked past it.
    arcs = {}
    arc_only = 0
    for d in rounds:
        a = d.parent / "README.md"
        if a not in arcs:
            arcs[a] = a.read_text(errors="ignore") if a.exists() else ""
        if (d.name in arcs[a]) and not rows[d.name]["in_root"]:
            arc_only += 1
    print(f"\n  ⭐ WHAT A GREEN GATE ADMITS, and it confessed this itself")
    print(f"    `every_round_reaches_the_readme` accepts the root README OR the round's ARC README.")
    print(f"    rounds passing it ONLY via an arc index row: {arc_only} of {n} ({arc_only/n:.0%})")
    print(f"    Its own docstring says: \"this check passes today because generate_round_index.py")
    print(f"    wrote those arc tables in the same session. That is a CONSTRUCTION, not a")
    print(f"    discovery, and it is weak evidence of the property.\"")
    print(f"    ⛔ The confession was WRITTEN. What was never done is MEASURE HOW MUCH IT ADMITS —")
    print(f"       and four rounds this session walked past it while auditing the RED gates.")

    print(f"\n  ⚠ THE NUMBER IS FLATTERING, and the direction is stated rather than left to be")
    print(f"    discovered: the rounds written THIS SESSION are in the root README by construction,")
    print(f"    because I appended a paragraph for each. The coverage of everything older is lower")
    print(f"    than the headline.")
    print(f"  ⚠ AND THIS COUNTS SITES, NEVER CONTENT. R383 showed a site can exist and hold a")
    print(f"    QUESTION. A round named in the root README has a paragraph; whether that paragraph")
    print(f"    states a finding is a different measurement and is not claimed here.")

    out = dict(stamp(str(SELF)), head=head, n_rounds=n, own_readme=own, in_root=inroot,
               neither=neither, n_artifact=len(art), artifact_own=a_own, artifact_root=a_root,
               artifact_neither=a_neither, root_share=r_share, own_share=d_share,
               arc_only=arc_only, controls=dict(positive=pos_ok, positive_n=pos_n, negative=neg_ok, negative_n=neg_n),
               verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r384_finding_sites.json"
    outp.write_text(json.dumps(out, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
