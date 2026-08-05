#!/usr/bin/env python3
"""
R597 -- is the repaired allowance's unsound direction REACHABLE in this document?

CHECK #197 FOUND TWO ERRORS IN R596's CLOSING LINE, IN OPPOSITE DIRECTIONS.
  ⛔ It called "paragraphs citing >1 round AND containing UNVERIFIED" *the exact size* of the
     unsound population. It is a SUPERSET: the rule only fires when a cited round IS
     unverified, so paragraphs where none is do not exercise it at all.
  ⛔ And it is simultaneously a SUBSET, which is the worse half. Unsoundness does NOT require
     multiple citations. A paragraph citing ONE round can contain the word for an unrelated
     reason -- quoting it, naming a different round's verdict, discussing the concept -- and
     the round is then allowed by an ACCIDENTAL marker. I narrowed by a PROXY (citation count)
     for a PROPERTY (marker intent), which is the same error class as the last seventeen, now
     committed inside the correction to one of them.

So the population is layered rather than counted once, and the layer that matters is the one
where the rule actually fires.

⚠ AND A MEASURED ZERO IS INADMISSIBLE UNTIL THE INSTRUMENT HAS RETURNED NON-ZERO (P5 ★). The
layer count came back 0 on first inspection, which is exactly when an instrument must be
pointed somewhere the answer is known to be positive before its zero may be read.

ESTIMAND        (i) |L3| = paragraphs of STATEMENT.md that cite >=1 round, contain the token
                UNVERIFIED, and cite at least one round the repaired gate classes UNVERIFIED
                -- the layer where the allowance actually fires.
                (ii) for each such paragraph, whether the marker is BOUND (the paragraph
                declares that round) or ACCIDENTAL (present for another reason).
                (iii) exit code of the real gate on a synthetic document that plants the
                unsound case -- reachability in principle, separate from incidence here.
IDENTIFICATION  (i) and (iii) are exact. ⚠ (ii) is NOT decidable mechanically -- "present for
                another reason" is about intent. It is bounded: a paragraph citing exactly one
                round and naming it UNVERIFIED is BOUND by construction; anything else is
                reported as UNDECIDABLE, never as accidental.
SCOPE           population : the 50 paragraphs of STATEMENT.md carrying >=1 citation
                instrument : the gate's own citation regex and the gate's own first-token
                             UNVERIFIED test, imported by re-implementation of the two rules
                             it actually applies -- and cross-checked against the gate's exit
                             code, which is the arbiter
                baseline   : positive-control corpora where the layer is known non-empty
                regime     : as committed at this sha
WORLDS          A UNREACHABLE HERE: |L3| = 0 and the synthetic plant IS allowed -> the hole is
                  real in principle and absent from this document. Fix is optional, and the
                  honest statement is a scope, not a repair.
                B LIVE: |L3| >= 1 with an accidental marker -> a round is being allowed by a
                  word that was not about it, and that citation needs rescoping now.
                C THE RULE IS SOUND ANYWAY: the synthetic plant is STOPPED -> my reading of
                  the rule was wrong and there is no unsound direction to size.
KILL            pre-registered: if the positive-control corpora ALSO return |L3| = 0, the
                counter has never returned non-zero and every zero it reports is silence.
                Verdict UNVERIFIED regardless of what the synthetic plant does.
POSITIVE CTRL   run the same counter over DEFINITION.md and FORMULATION.md and over the round
                READMEs -- corpora where citations and the token co-occur far more densely.
                It must return non-zero somewhere. Fails at g=0: an empty document must
                return 0.
NEGATIVE CTRL   a synthetic document citing rounds with NO occurrence of the token must
                return 0 at every layer.
PLACEBO         count the same layers for a token that appears nowhere ("ZZQ") -- must be 0.
SEEDS           n/a, deterministic; the synthetic plant is run TWICE and must agree.
MULTIPLICITY    4 layers x 4 corpora + 3 synthetic gate runs. All reported.
ARTIFACT        results/reachability.json
IMPOSSIBLE      construct validity for "the marker was about THIS round": intent is not in the
                string. Bounded above by the BOUND/UNDECIDABLE split, never asserted.
"""
from __future__ import annotations
import json, pathlib, re, shutil, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[3]
E05 = ROOT / "E05_the_space_of_compilers"
OUT = pathlib.Path(__file__).resolve().parent / "results"
CITE = r"\(R(\d{3})[,)]|R(\d{3})[,)]"


def cites_in(p):
    return sorted({int(a or b) for a, b in re.findall(CITE, p)})


def world_of(rid):
    for d in (E05 / "A24_what_the_definition_costs").glob(f"R{rid}_*"):
        for f in sorted((d / "results").glob("*.json")):
            try:
                j = json.loads(f.read_text())
            except Exception:
                continue
            if isinstance(j, dict) and isinstance(j.get("world"), str):
                return j["world"]
    return None


def is_unverified(w):
    """The gate's own rule, re-implemented; the gate's EXIT CODE is the arbiter below."""
    if not w:
        return True
    return re.split(r"[\s,;:.—–-]+", w.strip(), maxsplit=1)[0].strip("`*_'\"").upper() \
        == "UNVERIFIED"


def layers(text, token="UNVERIFIED"):
    paras = re.split(r"\n\s*\n", text)
    L0 = [(i, cites_in(p), p) for i, p in enumerate(paras) if cites_in(p)]
    L1 = [x for x in L0 if token in x[2]]
    L2 = [x for x in L1 if len(x[1]) >= 2]                        # R596's (wrong) filter
    L3 = [x for x in L1 if any(is_unverified(world_of(r)) for r in x[1])]
    return L0, L1, L2, L3


def main():
    text = (E05 / "STATEMENT.md").read_text()
    L0, L1, L2, L3 = layers(text)
    print(f"STATEMENT.md — the layered population (R596's line counted ONE layer and called "
          f"it exact)")
    print(f"  L0  paragraphs with >=1 citation                      : {len(L0)}")
    print(f"  L1  + contains the token UNVERIFIED                   : {len(L1)}")
    print(f"  L2  + cites >=2 rounds   <- R596's filter, a SUBSET   : {len(L2)}")
    print(f"  L3  + >=1 cited round IS unverified  <- WHERE IT FIRES: {len(L3)}")

    # ---- CONTROLS FIRST. A zero is inadmissible from an instrument never shown non-zero.
    print(f"\n─── CONTROLS ───")
    ctl = {}
    for name, path in (("DEFINITION.md", E05 / "DEFINITION.md"),
                       ("FORMULATION.md", E05 / "FORMULATION.md")):
        if not path.is_file():
            ctl[name] = None
            print(f"  POSITIVE  {name:<16} ABSENT — cannot serve as a control")
            continue
        a, b, c, d = layers(path.read_text())
        ctl[name] = [len(a), len(b), len(c), len(d)]
        print(f"  POSITIVE  {name:<16} L0={len(a):<4} L1={len(b):<4} L2={len(c):<4} "
              f"L3={len(d):<4}")
    readme_txt = "\n\n".join(
        (d / "README.md").read_text()
        for d in sorted((E05 / "A24_what_the_definition_costs").glob("R[0-9]*"))
        if (d / "README.md").is_file())
    ra, rb, rc, rd = layers(readme_txt)
    ctl["round READMEs"] = [len(ra), len(rb), len(rc), len(rd)]
    print(f"  POSITIVE  {'round READMEs':<16} L0={len(ra):<4} L1={len(rb):<4} "
          f"L2={len(rc):<4} L3={len(rd):<4}")
    nonzero = any(v and v[3] > 0 for v in ctl.values() if v)
    print(f"  -> counter has returned NON-ZERO at L3 somewhere: "
          f"{'PASS' if nonzero else '⛔ FAIL — every zero it reports is silence'}")

    e0, e1, e2, e3 = layers("")
    g0_ok = (len(e0), len(e1), len(e2), len(e3)) == (0, 0, 0, 0)
    print(f"  g=0       empty document returns {(len(e0), len(e1), len(e2), len(e3))} -> "
          f"{'PASS' if g0_ok else '⛔ FAIL'}")
    neg = "a claim rests on this *(R501)* and nothing else.\n\nanother *(R475)* here.\n"
    n0, n1, n2, n3 = layers(neg)
    neg_ok = len(n1) == 0
    print(f"  NEGATIVE  synthetic doc citing rounds with NO token: L0={len(n0)} L1={len(n1)} "
          f"-> {'PASS' if neg_ok else '⛔ FAIL'}")
    p0, p1, p2, p3 = layers(text, token="ZZQ")
    plc_ok = len(p1) == 0
    print(f"  PLACEBO   token 'ZZQ' over STATEMENT.md: L1={len(p1)} -> "
          f"{'PASS' if plc_ok else '⛔ FAIL'}")

    controls_ok = nonzero and g0_ok and neg_ok and plc_ok

    # ---- (ii) BOUND vs UNDECIDABLE for the L3 members ------------------------------
    print(f"\n─── L3 MEMBERS: is the marker BOUND to the unverified round? ───")
    members = []
    for i, cs, p in L3:
        unv = [r for r in cs if is_unverified(world_of(r))]
        bound = (len(cs) == 1)
        members.append({"para": i, "cites": cs, "unverified": unv,
                        "status": "BOUND (single citation)" if bound else "UNDECIDABLE"})
        print(f"  para {i}: cites {cs}, unverified {unv} -> "
              f"{'BOUND — one citation, the marker can only be about it' if bound else 'UNDECIDABLE — intent is not in the string'}")
    if not members:
        print("  (none)")

    # ---- (iii) REACHABILITY: plant the unsound case and read the gate's exit code ----
    print(f"\n─── REACHABILITY: is the unsound direction reachable AT ALL? (gate exit code) ───")

    def sandbox_with_doc(doc_text, victim, world_val):
        tmp = pathlib.Path(tempfile.mkdtemp(prefix="r597_"))
        tree = tmp / "repo"
        tree.mkdir()
        shutil.copytree(ROOT / "assurance", tree / "assurance")
        dst = tree / "E05_the_space_of_compilers"
        dst.mkdir()
        (dst / "STATEMENT.md").write_text(doc_text)
        shutil.copy2(E05 / "DEFINITION.md", dst / "DEFINITION.md")
        a24 = dst / "A24_what_the_definition_costs"
        a24.mkdir()
        for d in sorted((E05 / "A24_what_the_definition_costs").glob("R[0-9]*")):
            if not d.is_dir() or not (d / "results").is_dir():
                continue
            rid = int(re.match(r"R(\d+)", d.name).group(1))
            (a24 / d.name / "results").mkdir(parents=True)
            for f in sorted((d / "results").glob("*.json")):
                shutil.copy2(f, a24 / d.name / "results" / f.name)
            if rid == victim:
                for f in sorted((a24 / d.name / "results").glob("*.json")):
                    f.unlink()
                (a24 / d.name / "results" / "planted.json").write_text(
                    json.dumps({"world": world_val, "planted_by": "R597"}))
        r = subprocess.run([sys.executable,
                            str(tree / "assurance" / "statement_provenance.py")],
                           cwd=str(tree), capture_output=True, text=True, timeout=300)
        shutil.rmtree(tmp, ignore_errors=True)
        return r.returncode

    # every decimal on the real statement must still be anchored, so reuse the real text and
    # APPEND one synthetic paragraph -- a minimal document would fail the anchoring clause for
    # unrelated reasons and the exit code would not be about the allowance at all.
    victim = 507
    exploit_doc = text + (
        f"\n\nThe question of whether the floor is UNVERIFIED is discussed for R466, and a "
        f"separate result rests on this *(R{victim})*.\n")
    control_doc = text + (
        f"\n\nA separate result rests on this *(R{victim})* with no marker in the paragraph.\n")
    rc_exploit = [sandbox_with_doc(exploit_doc, victim, "UNVERIFIED") for _ in range(2)]
    rc_control = sandbox_with_doc(control_doc, victim, "UNVERIFIED")
    rc_clean = sandbox_with_doc(control_doc, victim, "B")
    print(f"  PLANT  R{victim} unverified, paragraph mentions UNVERIFIED for ANOTHER round: "
          f"exit {rc_exploit}  {'(runs agree)' if rc_exploit[0] == rc_exploit[1] else '⛔ RUNS DISAGREE'}")
    print(f"  PLANT  R{victim} unverified, paragraph has NO marker (must be STOPPED): "
          f"exit {rc_control}")
    print(f"  PLANT  R{victim} normal verdict 'B'          (must be ALLOWED): exit {rc_clean}")
    harness_ok = (rc_control != 0) and (rc_clean == 0) and rc_exploit[0] == rc_exploit[1]
    reachable = harness_ok and rc_exploit[0] == 0

    # ---- VERDICT: a function of the controls, nothing written between ----------------
    print(f"\n─── VERDICT ───")
    if not controls_ok or not harness_ok:
        world = ("UNVERIFIED — a control did not fire; neither the count nor the "
                 "reachability may be read")
    elif len(L3) == 0 and reachable:
        world = (f"A UNREACHABLE HERE — the unsound direction IS real (an unverified round "
                 f"planted into a paragraph whose UNVERIFIED refers to a DIFFERENT round is "
                 f"allowed, exit {rc_exploit[0]}), and STATEMENT.md contains {len(L3)} "
                 f"instances of it. A scope, not a repair.")
    elif len(L3) > 0:
        # ⛔ v1 FIRED "B LIVE" ON len(L3) > 0. World B was PRE-REGISTERED as "a round is being
        #    allowed by a word that was not about it" -- which requires an ACCIDENTAL marker,
        #    not merely that the allowance fires. With every L3 member BOUND, B is false and
        #    the branch was asserting something the round had not established. Same row as
        #    R593's non-partition elif: a label fired on a condition its own definition does
        #    not name. The states are now separated.
        und = [m for m in members if m["status"] != "BOUND (single citation)"]
        if und:
            world = (f"B LIVE — {len(L3)} paragraph(s) exercise the allowance and {len(und)} "
                     f"carry an UNDECIDABLE marker: para(s) "
                     f"{[m['para'] for m in und]} may be riding a word that was not about the "
                     f"round they allow")
        else:
            world = (f"D FIRES ONCE, CORRECTLY BOUND — the allowance is exercised in "
                     f"{len(L3)} paragraph(s), all single-citation, so the marker can only be "
                     f"about the round it allows. The unsound direction is REACHABLE "
                     f"(planted exploit exit {rc_exploit[0]}) but UNEXERCISED here.")
    else:
        world = ("C THE RULE IS SOUND ANYWAY — the planted exploit was STOPPED, so the "
                 "unsound direction I described does not exist")
    print(f"  {world}")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "reachability.json").write_text(json.dumps({
        "world": world,
        "layers_statement": {"L0": len(L0), "L1": len(L1), "L2_r596_filter": len(L2),
                             "L3_where_it_fires": len(L3)},
        "control_corpora": ctl, "controls_ok": controls_ok,
        "l3_members": members,
        "exit_exploit": rc_exploit, "exit_control_no_marker": rc_control,
        "exit_normal_verdict": rc_clean,
        "harness_ok": harness_ok, "reachable": reachable,
        "r596_line_was": ("a SUPERSET (the rule only fires when a cited round IS unverified) "
                          "and simultaneously a SUBSET (unsoundness does not require >=2 "
                          "citations -- one citation with an accidental marker suffices)"),
        "upper_bound_note": ("'the marker was about THIS round' is intent, not string; a "
                             "single-citation paragraph is BOUND by construction and every "
                             "other case is UNDECIDABLE, never asserted to be accidental"),
    }, indent=2))
    print(f"\n  wrote {OUT / 'reachability.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
