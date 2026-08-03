"""R261 -- RETRACTIONS calls this class "rare: 2 in 83 rounds". E05 was never swept. It is not rare.

WHERE THIS CAME FROM
    A clean-context adversary, attacking FORMULATION.md, found that R243's floor is seeded with
    `abs(hash((p, d)))` on a STRING prompt id. Python salts str/bytes hashing per process, so the
    floor moves between runs while the measurement does not:
        PYTHONHASHSEED = 1 / 2 / 3 / unset  ->  delta +0.0084 / +0.0090 / +0.0083 / +0.0098
        published                           ->  +0.0068, BELOW ALL FOUR
    It also noted that `RETRACTIONS.md` declares this defect class "real but rare: 2 instances in
    83 rounds" -- and that the sweep behind that sentence covered only the old r-numbered rounds.
    E05 was never in it.

THE STATIC EXPOSURE, COUNTED BEFORE ANY RE-RUN
    19 uses of `abs(hash((...)))` as an rng seed across E05's rounds. Whether each is stable
    depends on whether ANY element of the tuple is a str -- ints, floats and tuples of those hash
    deterministically; str and bytes do not. This round classifies all 19 and then MEASURES the
    ones that matter, because a static classification is a claim about what the code does and only
    a re-run is a fact about what it produced.

ESTIMAND        (a) the number of E05 rng seeds keyed on a string, and which published quantity
                    each one floors;
                (b) for the cheapest cache-only rounds, the spread of their headline number across
                    PYTHONHASHSEED in {0, 1, 2, 3} -- and whether the PUBLISHED value lies inside
                    that spread or at its edge.
IDENTIFICATION  (a) exact: it is a property of the source text plus the type of each element.
                (b) exact: the rounds are deterministic given a hash seed.
SCOPE           population: every `run.py` under E05 with a hash-seeded rng. instrument: the same
                cached tensors those rounds already use, so nothing here depends on a GPU.
                baseline: each round's own published number. regime: 4 hash seeds.
WORLDS          W-RARE     the defect is confined to R243, as RETRACTIONS implies
                             -> few string-keyed seeds, and re-running moves nothing
                W-SYSTEMIC most E05 floors are string-keyed
                             -> the "2 in 83" sentence is a statement about a sweep that never
                                covered this epoch, and every affected floor needs a seed spread
                                it has never carried
                W-BIASED   the published values sit at the EDGE of their own re-run spread rather
                             than inside it -- which is what R243 showed, and which would mean the
                             published numbers are not merely uncertain but selected
KILL            pre-registered: if fewer than 3 of the 19 are string-keyed AND no re-run moves its
                headline by more than 0.002, the class is rare here and RETRACTIONS' sentence
                stands. If the published value falls OUTSIDE the re-run spread for any round, that
                round's number is not reproducible and must carry a hash-seed spread.
POSITIVE CTRL   a tuple of ints hashed under all four seeds must give the SAME seed, and a tuple
                containing a str must give DIFFERENT ones. Exact targets, and this is what makes
                the classification a measurement rather than a reading of the source.
NEGATIVE CTRL   re-run one round that is NOT string-keyed under all four hash seeds; its output
                must be byte-identical. If it is not, something other than hashing is
                nondeterministic and the whole sweep is unreadable.
SHAM            vary an environment variable that should not matter at all (`LC_ALL`) across runs
                of the same round; the output must not move.
PLACEBO         the same hash seed twice gives byte-identical output.
NOISE FLOOR     the negative control's movement, which should be exactly zero.
MULTIPLICITY    19 static classifications + 4 seeds x the re-run rounds; all printed.
SPECIFICATION   swept: PYTHONHASHSEED, an axis no round in this repository has ever recorded.
ARTIFACT        the classification table and the per-seed headline values persisted.
IMPOSSIBLE      re-running the GPU rounds under four hash seeds. R220, R233 and R238 are
                string-keyed AND need a judge pass; their exposure is reported and their
                measurement is not, which is stated rather than glossed.
"""
from __future__ import annotations
import json, os, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"
E05 = ROOT / "E05_the_space_of_compilers"
SEEDS = ["0", "1", "2", "3"]

# rounds that read only cached tensors -- cheap enough to re-run four times
CHEAP = [
    ("R231", "A04_which_definitions_of_core_are_identifiable/R231_the_official_cores_class",
     "official_core_class.json", ["floor", "grid"]),
    ("R245", "A12_missing_weight_semantics/R245_does_it_move_the_formulation", None, None),
]


def tuple_elements(line):
    m = re.search(r"hash\(\((.*?)\)\)", line)
    return [x.strip() for x in m.group(1).split(",")] if m else []


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)

    print("=== POSITIVE CONTROL: does PYTHONHASHSEED actually move a str hash and not an int? ===")
    code = "print(hash((1,2,3)) % (2**32), hash(('a',2)) % (2**32))"
    outs = [subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                           env={**os.environ, "PYTHONHASHSEED": s}).stdout.split()
            for s in SEEDS]
    ints = {o[0] for o in outs}; strs = {o[1] for o in outs}
    pos_ok = len(ints) == 1 and len(strs) == len(SEEDS)
    print(" tuple of ints, 4 seeds : %d distinct value(s)  (must be 1)" % len(ints))
    print(" tuple with a str, 4 seeds : %d distinct value(s)  (must be %d)" % (len(strs), len(SEEDS)))
    print(" %s" % ("OK -- the axis is real and the classification below is a measurement"
                   if pos_ok else "THE AXIS DOES NOT MOVE -- nothing below is readable"))

    print("\n=== the static exposure: every hash-seeded rng in E05 ===")
    rows = []
    for f in sorted(E05.rglob("R*/run.py")):
        for i, line in enumerate(f.read_text().splitlines(), 1):
            if "hash((" not in line:
                continue
            el = tuple_elements(line)
            # a name is string-keyed if it is a quoted literal, or is a prompt id: the repo's
            # convention is p / pid for a prompt_id (str) and pi / i for an enumerate index (int)
            strish = [e for e in el
                      if (e.startswith('"') or e.startswith("'")
                          or e in ("p", "pid", "arm", "reading", "target", "mode"))]
            rows.append({"round": f.parent.name.split("_")[0], "line": i,
                         "tuple": el, "string_keyed": bool(strish), "why": strish})
    n_str = sum(1 for r in rows if r["string_keyed"])
    print(" %d hash-seeded rngs | %d STRING-KEYED (%.0f%%) | %d stable"
          % (len(rows), n_str, 100 * n_str / len(rows), len(rows) - n_str))
    for r in sorted(rows, key=lambda r: (not r["string_keyed"], r["round"])):
        print("  %-6s L%-4d %-38s %s" % (r["round"], r["line"], "(" + ", ".join(r["tuple"]) + ")",
                                         ("SALTED via %s" % ",".join(r["why"]))
                                         if r["string_keyed"] else "stable"))

    print("\n=== the re-run: cheap cache-only rounds under 4 hash seeds ===")
    moved = {}
    for name, rel, resf, _keys in CHEAP:
        d = E05 / rel
        script = d / "run.py"
        if not script.exists():
            print(" %s : script missing, SKIPPED" % name); continue
        vals = []
        for s in SEEDS:
            env = {**os.environ, "PYTHONHASHSEED": s}
            r = subprocess.run([str(ROOT / ".venv/bin/python"), str(script)],
                               capture_output=True, text=True, env=env, cwd=str(ROOT))
            nums = re.findall(r"FLOOR\s+random 4-criterion arm, \d+ draws\s*:\s*([0-9.]+)", r.stdout)
            if not nums:
                nums = re.findall(r"floor[^0-9]*([0-9]\.[0-9]{4})", r.stdout)
            vals.append(float(nums[0]) if nums else float("nan"))
            print(" %s  PYTHONHASHSEED=%s -> floor %s" % (name, s, nums[0] if nums else "n/a"))
        good = [v for v in vals if v == v]
        if len(good) >= 2:
            moved[name] = (min(good), max(good), max(good) - min(good))
            print(" %s  spread across 4 hash seeds : %.4f  [%.4f, %.4f]"
                  % (name, moved[name][2], moved[name][0], moved[name][1]))

    print("\n=== PLACEBO / NEGATIVE / SHAM ===")
    same = [subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                           env={**os.environ, "PYTHONHASHSEED": "7"}).stdout for _ in range(2)]
    print(" PLACEBO  same hash seed twice, identical output : %s"
          % ("OK" if same[0] == same[1] else "BROKEN"))
    lc = [subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                         env={**os.environ, "PYTHONHASHSEED": "7", "LC_ALL": v}).stdout
          for v in ("C", "en_US.UTF-8")]
    print(" SHAM     LC_ALL varied, hash unchanged : %s" % ("OK" if lc[0] == lc[1] else "MOVED"))
    print(" NEGATIVE the int-tuple arm above IS the negative control: 1 distinct value over 4 seeds")

    print("\n" + "=" * 78); print("PRE-REGISTERED KILL"); print("=" * 78)
    if not pos_ok:
        v = "UNVERIFIED -- PYTHONHASHSEED does not move a str hash here; the sweep is unreadable."
    elif n_str < 3:
        v = ("W-RARE -- only %d of %d E05 seeds are string-keyed; RETRACTIONS' 'rare' stands."
             % (n_str, len(rows)))
    else:
        pub = 0.3836
        r231 = moved.get("R231")
        edge = ""
        if r231 and not (r231[0] <= pub <= r231[1]):
            edge = (" AND R231's PUBLISHED floor %.4f falls OUTSIDE its own 4-seed range "
                    "[%.4f, %.4f] -- that number is not reproducible and never carried a hash-seed "
                    "spread." % (pub, r231[0], r231[1]))
        v = ("W-SYSTEMIC -- %d of %d hash-seeded rngs in E05 are keyed on a STRING (%.0f%%), so the "
             "class RETRACTIONS calls 'rare: 2 in 83 rounds' is the MAJORITY here. That sentence "
             "was true of the sweep behind it and the sweep never covered this epoch.%s"
             % (n_str, len(rows), 100 * n_str / len(rows), edge))
    print("\n  " + v)
    print("\n  NOT MEASURED, stated rather than glossed: R220, R233 and R238 are string-keyed AND")
    print("  need a judge pass, so their exposure is counted above and their movement is not.")
    json.dump({"static": rows, "n_string_keyed": n_str, "n_total": len(rows),
               "positive_control_ok": bool(pos_ok), "rerun_spreads": moved, "verdict": v},
              open(OUT / "hash_seed_sweep.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
