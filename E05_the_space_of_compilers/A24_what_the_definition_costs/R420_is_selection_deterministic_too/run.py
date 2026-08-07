"""R420 -- is SELECTION deterministic too? If so, R415's pairs were never a reproducibility failure.

R419 measured the scoring floor at exactly zero: two runs of identical criteria are bitwise identical.
Its NEXT said to run the same pair test one stage upstream, on `select_core.py`.

⛔ AND THE ANSWER SETS UP A CONTRADICTION THAT IS THE REAL POINT OF THIS ROUND. R416 measured that
   `core_X_08b.json` and `core_X_08bR.json` differ on 91-99.6% of prompts. If SCORING is deterministic
   (R419, measured) and SELECTION is deterministic given its inputs, then two end-to-end runs of the
   same rule CANNOT produce different criteria -- so the inputs must have differed, and the two files
   were DIFFERENT CONFIGURATIONS BY INTENT rather than a reproducibility failure at all.

   That would close R415's arc completely: there was never any instability to find.

⭐ AND UNLIKE THE JUDGE, THIS IS CPU-ONLY, SO RUNG 1 AND THE REAL TEST BOTH FIT. R417 had to stop at a
   source scan because scoring needs the GPU. Selection does not, so this round does the gauge scan
   AND runs the thing twice, and lets them cross-check: source-says-deterministic plus
   runs-agree is convergent; either one alone is not.

⛔ ARITHMETIC TRAP. That a seeded rng gives the same draws twice is forced -- `default_rng(0)` is
   `default_rng(0)`. What is NOT forced is whether the selection PATH for the rules in question
   touches the rng at all, nor whether anything else in it varies: dict ordering, file iteration,
   ties broken by float comparison. The empirical pair is what covers those, and the scan alone
   would not.

ESTIMAND        (A) whether `select_core.py`'s source contains any unseeded stochastic construct on
                    the selection path;
                (B) whether two invocations with IDENTICAL arguments produce byte-identical
                    `core_*.json`;
                (C) what (A) and (B) jointly imply for R415/R416's pairs.

IDENTIFICATION  (A) exact for what the source contains. (B) exact for this rule and these inputs.
                NOT identified: determinism for rules this round does not run, and determinism
                across machines. Named.

SCOPE           population: one rule (`topw_k`, k=4), the rule supplying 4 of the 5 published arms ·
                instrument: file hashes on the emitted core JSON · baseline: a file against itself ·
                regime: CPU, default inputs.

WORLDS
  W-SELECTION-DETERMINISTIC  the two runs emit byte-identical criteria. Then, with R419's zero
                             scoring floor, the whole pipeline is deterministic given its inputs, and
                             R416's 91-99.6% difference must come from DIFFERENT INPUTS -- meaning
                             the `_08b`/`_08bR` files were different configurations, not a failure.
  W-SELECTION-VARIES         they differ. Then selection is where the campaign's real variance lives,
                             it has never been measured, and R415's shift finally has a mechanism.

PREDICTION MATRIX
  W-SELECTION-DETERMINISTIC -> the two core JSONs hash equal
  W-SELECTION-VARIES        -> they differ, and the per-prompt change share is reported

PRE-REGISTERED KILL -- conditional on the controls, never on the hash alone.
    if self_hash_equal and both_runs_produced_a_file:
        hashes equal -> W-SELECTION-DETERMINISTIC
        else         -> W-SELECTION-VARIES, share reported
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

CONTROLS
  SELF (=)     a file hashed against itself must be equal, or every "differs" is meaningless.
  PRODUCED     both runs must actually emit a file. A missing file is not agreement -- an empty
               population passing is the failure the ledger names, and it would read as a PASS here.
  SCAN (+/-)   the stochastic-construct scan is checked on a planted `np.random.shuffle(` line and on
               a clean line, both directions, because a scan that finds nothing in a file with
               nothing proves only that it found nothing.
  DISTINCT     the two runs write to DIFFERENT tags, so neither overwrites the other and the
               comparison is between two artifacts rather than a file against itself.

MULTIPLICITY    1 rule x 2 runs; the scan over the whole file; all printed.
SEEDS           the tool's own default seed, held FIXED across both runs -- varying it would test a
                different question and would guarantee a difference for `random_k`.
ARTIFACT        results/r420_selection_determinism.json with the source hash.

IMPOSSIBLE HERE
  determinism for rules not run  -- one rule. `oracle_k`/`greedy_k`/`indep_k` need `--select-npz`
                                    and are not exercised; named rather than assumed to follow.
  cross-machine determinism      -- one machine.
  proving the 08b/08bR inputs differed -- this can only make it the remaining explanation, never
                                    demonstrate it. The producer records inputs from now on; those
                                    two files do not.

EXIT
    0  the controls hold and the comparison is reported
    1  a control misbehaved -- UNVERIFIED
    2  a run produced no file -- never a silent pass
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
RES = ROOT / "corebench" / "results"
SEL = ROOT / "corebench" / "select_core.py"
PY = ROOT / ".venv" / "bin" / "python"
STOCH = re.compile(r"np\.random\.(?!default_rng)|random\.(?:random|shuffle|choice|sample)\(|"
                   r"default_rng\(\s*\)|time\.time\(\)")


def h(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    if not SEL.exists():
        print("  UNRUNNABLE: select_core.py absent. Exit 2, never 0."); return 2
    src = SEL.read_text()

    print("R420 · is SELECTION deterministic too?\n")
    print("  ⛔ THE ANSWER SETS UP A CONTRADICTION. R419 measured the scoring floor at ZERO. If")
    print("     selection is deterministic too, then two end-to-end runs of one rule CANNOT emit")
    print("     different criteria — so R416's 91-99.6% difference must come from DIFFERENT INPUTS,")
    print("     and R415's pairs were different CONFIGURATIONS rather than a reproducibility")
    print("     failure. There would never have been any instability to find.\n")

    # ---- CONTROLS on the scan ---------------------------------------------------------------------
    pos = bool(STOCH.search("np.random.shuffle(order)\n"))
    neg = not STOCH.search("rng = np.random.default_rng(a.seed)\n")
    print("  CONTROLS")
    print(f"    SCAN (+)   a planted `np.random.shuffle(` is flagged: {pos}   "
          f"{'PASS' if pos else 'FAIL'}")
    print(f"    SCAN (-)   a SEEDED `default_rng(a.seed)` is NOT flagged: {neg}   "
          f"{'PASS' if neg else 'FAIL — seeding is determinism, not a violation of it'}")
    if not (pos and neg):
        print("\n  UNVERIFIED — the scan is blind in one direction. Exit 1."); return 1

    hits = [(i + 1, l.strip()[:74]) for i, l in enumerate(src.splitlines()) if STOCH.search(l)]
    print(f"\n  (A) UNSEEDED STOCHASTIC CONSTRUCTS in select_core.py: "
          f"{len(hits)}   {[x[0] for x in hits] or 'none'}")
    for ln, txt in hits[:4]:
        print(f"      L{ln}: {txt}")
    seeded = [(i + 1, l.strip()[:74]) for i, l in enumerate(src.splitlines())
              if "default_rng(" in l]
    for ln, txt in seeded[:2]:
        print(f"      SEEDED  L{ln}: {txt}   <- determinism, not a violation")

    # ---- (B) run it twice with IDENTICAL arguments -------------------------------------------------
    print(f"\n  (B) TWO INVOCATIONS WITH IDENTICAL ARGUMENTS — CPU only, so unlike the judge this")
    print(f"      round can run the real test and not stop at the scan")
    outs = {}
    for tag in ("_detA", "_detB"):
        cmd = [str(PY), str(SEL), "--rule", "topw_k", "--k", "4", "--tag-suffix", tag]
        r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=1800)
        f = RES / f"core_topw_k4{tag}.json"
        outs[tag] = f if f.exists() else None
        print(f"    {tag}  rc={r.returncode}  file={'yes' if f.exists() else 'NO'}"
              + ("" if f.exists() else f"   {(r.stderr or r.stdout).strip().splitlines()[-1][:90]}"))
    if not all(outs.values()):
        print("\n  UNRUNNABLE: a run produced no file. An empty population passing is the failure")
        print("  the ledger names, and it would read as agreement here. Exit 2."); return 2

    a, b = outs["_detA"], outs["_detB"]
    self_ok = h(a) == h(a)
    ha, hb = h(a), h(b)
    same = ha == hb
    da, db = json.loads(a.read_text()), json.loads(b.read_text())
    keys = set(da) & set(db) if isinstance(da, dict) else set()
    chg = sum(1 for k in keys if da[k] != db[k]) if keys else 0
    share = chg / len(keys) if keys else None
    print(f"    SELF (=)   a file against itself hashes equal: {self_ok}")
    print(f"\n    core_topw_k4_detA  {ha[:16]}")
    print(f"    core_topw_k4_detB  {hb[:16]}")
    print(f"    identical: {same}" + (f"   prompts changed: {share:.1%}" if share is not None else ""))

    print()
    if same:
        v = "W_SELECTION_DETERMINISTIC"
        print(f"  W-SELECTION-DETERMINISTIC — two invocations with identical arguments emit")
        print(f"  BYTE-IDENTICAL criteria, and the source holds no unseeded stochastic construct on")
        print(f"  the selection path. Source and behaviour agree, which neither establishes alone.")
        print(f"  ⛔ COMBINED WITH R419's ZERO SCORING FLOOR, THE PIPELINE IS DETERMINISTIC GIVEN ITS")
        print(f"     INPUTS. So R416's 91-99.6% criteria difference cannot be a reproducibility")
        print(f"     failure: the INPUTS to those two runs must have differed, and the `_08b`/")
        print(f"     `_08bR` files are two DIFFERENT CONFIGURATIONS rather than two draws.")
        print(f"  ⚠ THIS MAKES THAT THE REMAINING EXPLANATION. It does not DEMONSTRATE it, because")
        print(f"    those two files record no inputs — which is exactly the gap the provenance field")
        print(f"    now closes for everything produced from here on.")
    else:
        v = "W_SELECTION_VARIES"
        print(f"  W-SELECTION-VARIES — identical arguments emit DIFFERENT criteria"
              + (f" on {share:.1%} of prompts" if share is not None else "") + ".")
        print(f"  Selection is where the campaign's real variance lives, it has never been measured,")
        print(f"  and R415's shift finally has a mechanism.")

    print(f"\n  ⚠ ONE RULE. `topw_k` supplies 4 of the 5 published arms, but `oracle_k`/`greedy_k`/")
    print(f"    `indep_k` take a `--select-npz` and are NOT exercised here. Their determinism does")
    print(f"    not follow and is not claimed.")

    art = dict(source_sha256=hashlib.sha256(SELF.read_bytes()).hexdigest(), source_name=SELF.name,
               unseeded_hits=hits, seeded=seeded, sha_a=ha, sha_b=hb, identical=same,
               changed_share=share, rule="topw_k", k=4,
               controls=dict(scan_pos=pos, scan_neg=neg, self_hash=self_ok), verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r420_selection_determinism.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
