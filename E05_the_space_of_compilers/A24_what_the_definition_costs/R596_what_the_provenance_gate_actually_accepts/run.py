#!/usr/bin/env python3
"""
R596 -- what does the provenance gate actually accept?

CHECK #196 FOUND THE ARITHMETIC TRAP IN R595's CLOSING LINE. It proposed running the gate
against a `world` that is a sentence containing "unverified" and seeing whether it passes.
The gate's predicate, read from source, is `w and w != "UNVERIFIED"` -- EXACT string
inequality. That a variant spelling passes is FORCED BY THE CODE. Reporting it as a finding
would be `1+1=2, therefore 2<3`: a derivation dressed as an experiment.

So the derivation is labelled as one below and the round measures what could have come out
otherwise: WHETHER ANY CITED ROUND ACTUALLY EXPLOITS THE HOLE, and whether the gate's other
reachable holes are live or latent. A hole nobody has walked through is a cheap fix; a hole
the deliverable is standing in is a rescoping.

⚠ AND THIS IS A LOCK-ATTACK, so P7 applies: >=5 vectors ACTUALLY PERFORMED, each in a
SANDBOX COPY of the repo, never against the live deliverable. The evidence is the gate's own
exit code on a planted tree, not my reading of its source.

ESTIMAND        (i) n_exploit = cited rounds whose `world` means unverified but is not the
                exact string -- the ACTIVE exploitation count.
                (ii) for each of 8 planted spellings, the gate's exit code on a sandbox tree.
IDENTIFICATION  (i) is a complete enumeration -- no sampling. ⚠ "means unverified" is not
                decidable from the string, so it is bounded from ABOVE by a case-insensitive
                substring test and reported as a bound.
                (ii) is exact: an exit code is not an estimate.
SCOPE           population : the 83 rounds STATEMENT.md cites under the gate's OWN citation
                             regex `R(\\d{3})[,)]`, which is not the same regex R592 used
                             (`R(\\d{3})`, 91 rounds) -- two instruments, two populations,
                             and the gate's own is the one that governs it
                instrument : subprocess exit code of the real gate file, unmodified, run in a
                             sandbox tree. Instrument unit = EXIT CODE; claim unit = WHETHER
                             THE GATE STOPS THIS ROUND. Equal by construction.
                baseline   : the unplanted sandbox must exit 0 (else the sandbox is broken)
                regime     : as committed at this sha
WORLDS          A LATENT: no cited round exploits any hole -> the gate has never been walked
                  through, the fix is mechanical, and no claim moves.
                B ACTIVE: >=1 cited round passes while meaning unverified -> the deliverable
                  rests on a round the gate exists to exclude, and that claim needs rescoping.
                C THE GATE IS INERT: it cannot stop ANY planted spelling including the exact
                  one -> it has never been a gate at all and every round it "cleared" is
                  UNVERIFIED rather than cleared.
KILL            pre-registered: if the EXACT spelling does not make the gate fail in the
                sandbox, the sandbox is invalid and every other cell is UNVERIFIED -- no
                acceptance claim may be read from a harness that cannot produce a rejection.
POSITIVE CTRL   plant `world = "UNVERIFIED"` verbatim on a cited round. The gate MUST exit
                non-zero. This is the floor: it proves the harness can produce a rejection.
                Fails at g=0: the unplanted sandbox must exit 0.
NEGATIVE CTRL   plant `world = "B"` (a normal verdict). The gate must still exit 0 -- proving
                the rejection above came from the SPELLING and not from the act of planting.
PLACEBO         plant a key that is not `world` at all (`wrld`). Must exit 0.
SEEDS           n/a -- the harness is deterministic; instead every cell is run TWICE and the
                two exit codes are required to agree, which is the reproducibility check.
MULTIPLICITY    8 spellings x 2 runs + 3 controls. All reported, including the ones that pass.
ARTIFACT        results/gate_acceptance.json
IMPOSSIBLE      construct validity for "means unverified": not decidable from a string without
                the round's author. n_exploit is an UPPER BOUND via case-insensitive substring,
                and is reported as one.
"""
from __future__ import annotations
import json, pathlib, re, shutil, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[3]
E05 = ROOT / "E05_the_space_of_compilers"
GATE = ROOT / "assurance" / "statement_provenance.py"
OUT = pathlib.Path(__file__).resolve().parent / "results"

SPELLINGS = [
    ("exact", "UNVERIFIED"),
    ("lowercase", "unverified"),
    ("trailing space", "UNVERIFIED "),
    ("leading space", " UNVERIFIED"),
    ("trailing newline", "UNVERIFIED\n"),
    ("sentence", "UNVERIFIED -- a control did not fire"),
    ("prefixed", "world: UNVERIFIED"),
    ("em-dash form", "UNVERIFIED — the instrument was unfit"),
]


def cited_by_gate_regex(text):
    """The gate's OWN citation regex, not a reimplementation of it."""
    return sorted({int(x) for x in
                   re.findall(r"\(R(\d{3})[,)]", text) + re.findall(r"R(\d{3})[,)]", text)})


def run_gate(tree: pathlib.Path):
    r = subprocess.run([sys.executable, str(tree / "assurance" / "statement_provenance.py")],
                       cwd=str(tree), capture_output=True, text=True, timeout=300)
    return r.returncode, (r.stdout or "")[-400:]


def sandbox(target_round: int, key: str, value):
    """A COPY of the repo with one cited round's artifact overwritten. Never the live tree."""
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="r596_"))
    tree = tmp / "repo"
    tree.mkdir()
    shutil.copytree(ROOT / "assurance", tree / "assurance")
    dst = tree / "E05_the_space_of_compilers"
    dst.mkdir()
    for f in ("STATEMENT.md", "DEFINITION.md"):
        shutil.copy2(E05 / f, dst / f)
    a24 = dst / "A24_what_the_definition_costs"
    a24.mkdir()
    for d in sorted((E05 / "A24_what_the_definition_costs").glob("R[0-9]*")):
        if not d.is_dir() or not (d / "results").is_dir():
            continue
        rid = int(re.match(r"R(\d+)", d.name).group(1))
        (a24 / d.name / "results").mkdir(parents=True)
        for f in sorted((d / "results").glob("*.json")):
            shutil.copy2(f, a24 / d.name / "results" / f.name)
        if rid == target_round and key is not None:
            for f in sorted((a24 / d.name / "results").glob("*.json")):
                f.unlink()
            (a24 / d.name / "results" / "planted.json").write_text(
                json.dumps({key: value, "planted_by": "R596"}))
    return tmp, tree


def main():
    text = (E05 / "STATEMENT.md").read_text()
    cites = cited_by_gate_regex(text)
    if not cites:
        print("UNRUNNABLE: the gate's own regex finds no citations. Exit 2, never 0.")
        return 2
    print(f"POPULATION  rounds cited under the GATE'S OWN regex `R(\\d{{3}})[,)]` : {len(cites)}")
    loose = sorted({int(x) for x in re.findall(r"R(\d{3})", text)})
    print(f"  ⚠ a LOOSER regex `R(\\d{{3}})` (the one R592 used) finds {len(loose)}. "
          f"Two instruments, two populations; the gate is governed by its own.")

    # ---- DERIVATION, labelled. Read from source, not measured. ----------------------
    src = GATE.read_text()
    pred = re.search(r"flag = .*", src)
    print(f"\n─── DERIVATION (forced by the code -- NOT evidence) ───")
    print(f"  predicate: {pred.group(0).strip() if pred else '(not found)'}")
    print(f"  `!=` is EXACT string inequality, so every spelling other than the literal")
    print(f"  'UNVERIFIED' passes BY CONSTRUCTION. This could not have come out otherwise.")

    # ---- MEASUREMENT (i): is the hole ACTIVE? ---------------------------------------
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

    worlds = {r: world_of(r) for r in cites}
    exact = [r for r, w in worlds.items() if w == "UNVERIFIED"]
    missing = [r for r, w in worlds.items() if w is None]
    # ⚠ RE-CLASSIFIED after the repair. "Accepted by accident" and "allowed because the
    # citing paragraph declares it" are DIFFERENT STATES that the first version printed as
    # one. R501 moved from the first to the second without its artifact changing, which is
    # exactly why the two must be counted separately.
    paras = re.split(r"\n\s*\n", text)
    flavoured = [r for r, w in worlds.items()
                 if w and w != "UNVERIFIED" and "unverified" in w.lower()]
    declared = [r for r in flavoured
                if any(f"R{r}" in p_ and "UNVERIFIED" in p_ for p_ in paras)]
    exploit = [r for r in flavoured if r not in declared]
    print(f"\n─── MEASUREMENT: is the hole ACTIVE among cited rounds? ───")
    print(f"  exact 'UNVERIFIED' (correctly stopped)          : {len(exact)} {exact}")
    print(f"  no `world` at all  (correctly stopped)          : {len(missing)} {missing}")
    print(f"  unverified-flavoured, NOT the exact string      : {len(flavoured)} {flavoured}")
    print(f"    of those, DECLARED in the citing paragraph    : {len(declared)} {declared}")
    print(f"  ⛔ UNDECLARED and therefore silently accepted    : {len(exploit)} {exploit}")
    for r in flavoured:
        print(f"      R{r}: {worlds[r][:110]!r}")

    # ---- THE ATTACK: 8 spellings x 2 runs, in sandboxes, controls first -------------
    victim = sorted(cites)[len(cites) // 2]
    print(f"\n─── CONTROLS (sandbox on cited round R{victim}) ───")
    cells = {}
    tmp, tree = sandbox(victim, None, None)
    rc0, _ = run_gate(tree)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"  g=0 UNPLANTED sandbox exits {rc0} -> "
          f"{'PASS' if rc0 == 0 else '⛔ the sandbox itself is broken; nothing below is admissible'}")

    tmp, tree = sandbox(victim, "world", "UNVERIFIED")
    rc_pos, _ = run_gate(tree)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"  POSITIVE  planted exact 'UNVERIFIED' exits {rc_pos} -> "
          f"{'PASS -- the harness CAN produce a rejection' if rc_pos != 0 else '⛔ FAIL'}")

    tmp, tree = sandbox(victim, "world", "B")
    rc_neg, _ = run_gate(tree)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"  NEGATIVE  planted a normal verdict 'B' exits {rc_neg} -> "
          f"{'PASS -- the rejection came from the SPELLING, not from planting' if rc_neg == 0 else '⛔ FAIL'}")

    tmp, tree = sandbox(victim, "wrld", "UNVERIFIED")
    rc_plc, _ = run_gate(tree)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"  PLACEBO   planted under key 'wrld' exits {rc_plc} -> "
          f"{'PASS' if rc_plc != 0 else 'exits 0'}   "
          f"(no `world` key at all is ALSO a rejection path, so non-zero is expected here)")

    harness_ok = (rc0 == 0) and (rc_pos != 0) and (rc_neg == 0)
    if not harness_ok:
        print("\n⛔ THE HARNESS DID NOT PASS ITS OWN CONTROLS -- every acceptance cell below "
              "is UNVERIFIED, not an acceptance. Exit 2.")
        return 2

    print(f"\n─── ATTACK: 8 spellings, each run TWICE (P7: vectors actually performed) ───")
    print(f"{'spelling':>18} {'run1':>6} {'run2':>6}  {'agree':>6}  outcome")
    for name, val in SPELLINGS:
        rcs = []
        for _ in range(2):
            tmp, tree = sandbox(victim, "world", val)
            rc, _tail = run_gate(tree)
            shutil.rmtree(tmp, ignore_errors=True)
            rcs.append(rc)
        agree = rcs[0] == rcs[1]
        stopped = rcs[0] != 0
        cells[name] = {"value": val, "exit_codes": rcs, "reproducible": agree,
                       "stopped": stopped}
        print(f"{name:>18} {rcs[0]:>6} {rcs[1]:>6}  {str(agree):>6}  "
              f"{'STOPPED' if stopped else '⛔ ACCEPTED -- the gate lets this through'}")

    accepted = [n for n, c in cells.items() if not c["stopped"]]
    print(f"\n  MULTIPLICITY: {len(SPELLINGS)} spellings x 2 runs + 3 controls = "
          f"{len(SPELLINGS)*2+3} gate invocations. "
          f"{len(SPELLINGS)-len(accepted)} stopped, {len(accepted)} accepted.")

    # ---- VERDICT: a function of the controls and the cells, nothing written between --
    print(f"\n─── VERDICT ───")
    if exploit:
        world = (f"B ACTIVE -- {len(exploit)} cited round(s) carry an unverified-flavoured "
                 f"`world` that the gate accepts UNDECLARED: {exploit}")
    elif declared and accepted:
        world = (f"B WAS ACTIVE, NOW DECLARED -- R{declared} was passing silently; the "
                 f"repaired gate recognises it as UNVERIFIED and allows it only because the "
                 f"citing paragraph says so. {len(accepted)} spelling(s) still accepted "
                 f"({accepted}): a string rule cannot be made sound over an untyped field")
    elif accepted:
        world = (f"A LATENT -- the gate accepts {len(accepted)} of {len(SPELLINGS)} spellings "
                 f"({accepted}) but NO cited round currently uses one. The hole is real, "
                 f"demonstrated by exit code, and unexploited; the fix is mechanical and no "
                 f"claim moves.")
    else:
        world = "the gate stops every spelling tested -- no hole demonstrated"
    print(f"  {world}")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "gate_acceptance.json").write_text(json.dumps({
        "world": world,
        "n_cited_gate_regex": len(cites), "n_cited_loose_regex": len(loose),
        "victim_round": victim,
        "exact_unverified_cited": exact, "no_world_cited": missing,
        "exploiting_cited": exploit, "flavoured_cited": flavoured,
        "declared_cited": declared,
        "control_unplanted_exit": rc0, "control_positive_exit": rc_pos,
        "control_negative_exit": rc_neg, "control_placebo_exit": rc_plc,
        "harness_ok": harness_ok, "spellings": cells, "accepted": accepted,
        "derivation": ("the predicate is exact string inequality; variant spellings pass BY "
                       "CONSTRUCTION. That half is a DERIVATION, not evidence -- only the "
                       "exploitation count and the exit codes could have come out otherwise"),
        "upper_bound_note": ("'means unverified' is not decidable from a string; the "
                             "exploitation count is an UPPER BOUND via case-insensitive "
                             "substring"),
    }, indent=2))
    print(f"\n  wrote {OUT / 'gate_acceptance.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
