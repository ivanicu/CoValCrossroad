"""R395 -- can a SOURCE-LEVEL gauge test decide stability, or must the expensive rounds be re-run?

R394 established that 13 fast rounds reproduce their numbers exactly at an unchanged source hash, and
named its own blind spot: the two rounds R393 censored at 90s carry 80% of the gate's cost and are
exactly the population that result cannot speak for. R394's NEXT specified the cheap step first -- a
gauge test on the censored rounds' SOURCE for constructs that vary at fixed source, before paying to
run them twice.

⛔ BUT A SOURCE GREP IS AN INSTRUMENT, AND THIS CAMPAIGN HAS BEEN BURNED BY EXACTLY THIS FIVE TIMES.
   A pattern that flags `random` or `time` will flag almost every scientific script ever written,
   return "both censored rounds are at risk", and read as an answer. So the question this round can
   honestly ask is not "are the censored rounds risky" but the prior one:

       DOES A SOURCE-LEVEL DETECTOR HAVE ANY DISCRIMINATING POWER AT ALL?

⭐ AND THE CALIBRATION SET ALREADY EXISTS, WHICH IS THE ONLY REASON THIS IS AFFORDABLE. R394 measured
   13 rounds as STABLE. Those are LABELLED NEGATIVES produced by a DIFFERENT ROUND for a DIFFERENT
   PURPOSE, so the detector can be scored against them rather than against my imagination -- the
   failure this file's own table calls "a control validated on imagined cases". R394's rng plant is
   the labelled positive. Neither label was produced here.

⛔ ARITHMETIC TRAP, answered before the run. Could this come out otherwise? YES. The detector could
   fire on 0 of 13 known-stable rounds (discriminating), on 13 of 13 (useless), or anywhere between.
   Nothing about the corpus forces the rate, and I do not know it -- R394 measured OUTPUT stability
   and never looked at what the sources contain.

ESTIMAND        (a) the detector's firing rate on the 13 rounds R394 LABELLED STABLE -- its
                    false-positive rate against ground truth it did not generate;
                (b) the constructs found in the 2 CENSORED rounds, NAMED per round, never as a rate.
                With 2 subjects no rate is admissible and none is computed.

IDENTIFICATION  (a) exact -- the labels are committed and the patterns are deterministic.
                (b) NOT identified: whether a construct REACHES printed output is undecidable by
                grep. So a hit is "capable of varying", never "does vary", and that gap is the whole
                reason (a) exists.

SCOPE           population: 13 labelled-stable + 2 censored rounds · instrument: literal source
                patterns · baseline: R394's labels · regime: HEAD.

WORLDS
  W-GAUGE-DECISIVE  the detector is quiet on most labelled-stable rounds. Then a hit on a censored
                    round carries information and the cheap step can stand in for the expensive one.
  W-GAUGE-BLIND     the detector fires on most labelled-stable rounds too. Then it has no
                    discriminating power, the gauge test CANNOT replace the re-run, and R394's NEXT
                    was wrong to propose it as a substitute. That is a finding about the METHOD and
                    it prices the next step honestly instead of buying a cheap wrong answer.

PREDICTION MATRIX
  W-GAUGE-DECISIVE -> fires on <= 4 of 13 labelled-stable
  W-GAUGE-BLIND    -> fires on >= 9 of 13 labelled-stable
  between 5 and 8  -> named explicitly as partial, never rounded to whichever world I prefer

PRE-REGISTERED KILL -- conditional on the controls, never on the rate alone.
    if plant_detected and clean_file_silent:
        fp = rounds among the 13 labelled-stable with >= 1 hit
        if fp <= 4 -> W-GAUGE-DECISIVE ; elif fp >= 9 -> W-GAUGE-BLIND ; else -> PARTIAL, named
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

CONTROLS
  PLANT (+)   R394's own rng plant source must be flagged. A detector that misses an unseeded
              random draw cannot be trusted when it stays quiet.
  PLANT (-)   a file containing only a print of a literal must NOT be flagged, so silence is shown
              to be attainable and the detector is not a constant.
  LABELS      the negatives come from R394's committed artifact, not from this round's judgement.
  EMPTY       fewer than 10 labelled-stable subjects, or 0 censored, -> exit 2, never 0.

MULTIPLICITY    15 rounds x 7 pattern families, every hit printed with the pattern named.
SEEDS           none -- static analysis.
ARTIFACT        results/r395_gauge_power.json with the source hash.

IMPOSSIBLE HERE
  whether a construct reaches output  -- undecidable by grep; it is why (a) is the real estimand.
  a rate over the censored rounds     -- n=2. Named constructs only.
  proving a round IS deterministic    -- neither grep nor two runs can do that.
  a second release                    -- one release.

EXIT
    0  controls hold and the detector's power is measured
    1  a control misbehaved -- UNVERIFIED
    2  the population is unusable -- never a silent pass
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
R393 = HERE.parent / "R393_what_the_gate_will_cost" / "results" / "r393_gate_cost.json"
R394 = HERE.parent / "R394_is_the_source_hash_a_valid_key" / "results" / "r394_source_hash_key.json"
PLANT = HERE.parent / "R394_is_the_source_hash_a_valid_key" / "results" / "_plants" / "rng.py"

# seven families of construct that CAN vary at fixed source. Deliberately the patterns a careful
# author would actually write down -- the point is to measure their power, not to defend them.
PATTERNS = {
    "wall_clock":   re.compile(r"\btime\.(time|perf_counter|monotonic)\b|datetime\.now|time\.sleep"),
    "unseeded_rng": re.compile(r"\brandom\.(random|randint|choice|shuffle|sample)\b|np\.random\.(?!seed|default_rng)"),
    "builtin_hash": re.compile(r"(?<![\w.])hash\("),
    "set_order":    re.compile(r"for\s+\w+\s+in\s+set\(|\bfor\s+\w+\s+in\s+\w*_?set\b"),
    "fs_order":     re.compile(r"os\.listdir|\.iterdir\(\)|(?<!sorted\()\.glob\("),
    "gpu":          re.compile(r"\btorch\b|\bcuda\b|device\s*="),
    "concurrency":  re.compile(r"multiprocessing|ThreadPool|concurrent\.futures"),
}


def scan(text: str):
    return sorted(k for k, rx in PATTERNS.items() if rx.search(text))


def main() -> int:
    if not (R393.exists() and R394.exists()):
        print("  UNRUNNABLE: R393/R394 artifacts absent. Exit 2, never 0."); return 2
    a394 = json.loads(R394.read_text())
    a393 = json.loads(R393.read_text())
    stable = sorted(k for k, v in a394["rows"].items() if v["status"] == "STABLE")
    censored = sorted(k for k, v in a393["rows"].items() if v["status"] == "CENSORED")
    if len(stable) < 10 or not censored:
        print(f"  UNRUNNABLE: {len(stable)} labelled-stable, {len(censored)} censored. Exit 2.")
        return 2

    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True,
                          text=True).stdout.strip()[:12]
    print(f"R395 · can a source gauge test replace the re-run?   HEAD {head}\n")
    print(f"  ⛔ THE QUESTION IS NOT `ARE THE CENSORED ROUNDS RISKY`. A pattern matching `random` or")
    print(f"     `time` flags nearly every scientific script, returns `both are at risk`, and reads")
    print(f"     as an answer. The prior question is whether the detector discriminates AT ALL.")
    print(f"  ⭐ AND THE ANSWER KEY WAS NOT MADE HERE: R394 labelled 13 rounds STABLE for a different")
    print(f"     purpose, so the false-positive rate is scored against committed ground truth.\n")

    # ---- CONTROLS -------------------------------------------------------------------------------
    if not PLANT.exists():
        print("  UNRUNNABLE: R394's rng plant absent — no positive control. Exit 2."); return 2
    plant_hits = scan(PLANT.read_text())
    clean_hits = scan("print('value 0.5000 and 12345')\n")
    pos_ok, neg_ok = ("unseeded_rng" in plant_hits), (not clean_hits)
    print(f"  CONTROLS on the source detector")
    print(f"    PLANT (+)  R394's unseeded-rng plant flags {plant_hits}   "
          f"{'PASS' if pos_ok else 'FAIL — silence below would mean nothing'}")
    print(f"    PLANT (-)  a literal-only file flags {clean_hits}   "
          f"{'PASS' if neg_ok else 'FAIL — the detector is a constant'}")
    if not (pos_ok and neg_ok):
        print("\n  UNVERIFIED — the detector is blind in one direction. Exit 1."); return 1

    def find_src(name):
        d = next((q for q in ROOT.glob(f"E0*/A*/{name}") if q.is_dir()), None)
        return (d / "run.py") if d and (d / "run.py").exists() else None

    # ---- (a) FALSE POSITIVES on ground truth this round did not make ----------------------------
    print(f"\n  (a) THE DETECTOR ON {len(stable)} ROUNDS R394 MEASURED AS STABLE — every hit here is a")
    print(f"      FALSE POSITIVE, because the output was proven identical across two runs")
    rows, fp = {}, []
    for name in stable:
        p = find_src(name)
        if p is None:
            rows[name] = dict(label="STABLE", status="ABSENT"); continue
        h = scan(p.read_text())
        rows[name] = dict(label="STABLE", status="SCANNED", hits=h)
        if h:
            fp.append(name)
        print(f"    {name:<44} {'FLAGGED' if h else 'quiet  '}  {h if h else ''}")
    scanned = [k for k, v in rows.items() if v["status"] == "SCANNED"]
    rate = len(fp) / len(scanned) if scanned else 0.0
    print(f"\n      FALSE POSITIVES {len(fp)} of {len(scanned)}  ({rate:.0%})")

    # ---- (b) the censored rounds, NAMED, never rated --------------------------------------------
    print(f"\n  (b) THE {len(censored)} CENSORED ROUNDS — constructs NAMED, no rate computed, because")
    print(f"      n=2 supports no rate and quoting one would be the arithmetic trap in a lab coat")
    for name in censored:
        p = find_src(name)
        if p is None:
            rows[name] = dict(label="CENSORED", status="ABSENT")
            print(f"    {name:<44} ABSENT"); continue
        h = scan(p.read_text())
        rows[name] = dict(label="CENSORED", status="SCANNED", hits=h)
        print(f"    {name:<44} {h if h else 'quiet'}")

    # ---- VERDICT --------------------------------------------------------------------------------
    print()
    if len(fp) <= 4:
        v = "W_GAUGE_DECISIVE"
        print(f"  W-GAUGE-DECISIVE — the detector is quiet on {len(scanned)-len(fp)} of {len(scanned)}")
        print(f"  rounds whose output is PROVEN identical, so a hit on a censored round carries")
        print(f"  information and the cheap step can stand in for the expensive one.")
    elif len(fp) >= 9:
        v = "W_GAUGE_BLIND"
        print(f"  W-GAUGE-BLIND — the detector fires on {len(fp)} of {len(scanned)} rounds whose")
        print(f"  output is PROVEN identical. It has no discriminating power, so a hit on a censored")
        print(f"  round means nothing, and A SOURCE GAUGE TEST CANNOT REPLACE THE RE-RUN.")
        print(f"  R394's NEXT proposed exactly that substitution, and this refuses it. The finding is")
        print(f"  about the METHOD: the cheap route is closed, and the expensive one is now PRICED")
        print(f"  rather than merely postponed.")
    else:
        v = "W_GAUGE_PARTIAL"
        print(f"  PARTIAL — {len(fp)} of {len(scanned)} false positives, between the pre-registered")
        print(f"  thresholds. Named as partial rather than rounded toward whichever world I prefer.")

    print(f"\n  ⚠ A HIT IS `CAPABLE OF VARYING`, NEVER `DOES VARY`. Whether a construct reaches printed")
    print(f"    output is undecidable by grep — which is precisely why the false-positive rate above")
    print(f"    is the estimand and the censored rounds' hit list is not.")

    art = dict(source_sha256=hashlib.sha256(SELF.read_bytes()).hexdigest(), source_name=SELF.name,
               head=head, rows=rows, n_labelled_stable=len(scanned), n_false_positive=len(fp),
               false_positive_rate=round(rate, 3), censored=censored,
               controls=dict(plant_hits=plant_hits, pos_ok=pos_ok, clean_hits=clean_hits,
                             neg_ok=neg_ok),
               verdict=v)
    outp = HERE / "results" / "r395_gauge_power.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
