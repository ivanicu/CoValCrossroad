#!/usr/bin/env python3
"""
R680 -- twenty-two citations, how many computations? n_eff for the deliverable's central number.

CHECK #281 ON R679's NEXT LINE -- THE PROPOSED TEST IS BLIND, KILLED BY A GAUGE TEST FOR FREE.
  R679 asked to separate "recomputed" from "restated" by whether the set appears as a VALUE in a
  round's results/. A value in results/ is produced IDENTICALLY by recomputation and by a hard-coded
  literal: the MEASUREMENT is invariant under the distinction the PROPERTY depends on. Attack ladder
  step 1, three lines, zero compute. ⭐ And R676's census had already recorded `R529.ext_rank` and
  `R534.ext_rank`, so the proposed test's answer was committed before the round was proposed.

ESTIMAND        A: of the rounds whose committed results contain the ③-extension set
                   {coval_core, topw_k3, topw_k4, topw_k6, topw_k8}, how many DERIVE it -- zero
                   member literals in EXECUTABLE source -- rather than restate it?
                B: the share deriving.
IDENTIFICATION  ⚠ UPPER BOUND, not a certificate. "No code literals" does not prove independent
                computation: a round could READ the set from another round's artifact and pass.
                That is copying through a file and is NOT separated here.
SCOPE           population : every round whose results/*.json contains the set as a list value
                instrument : Python tokenizer strip of comments + docstrings, then literal count
                             instrument unit = A ROUND'S EXECUTABLE SOURCE
                             claim unit      = AN INDEPENDENT COMPUTATION
                             ⚠ NOT EQUAL -- hence the upper bound, carried into the verdict.
                baseline   : R678's producer, R294
                regime     : this repository at HEAD
WORLDS          A MANY COMPUTATIONS: several rounds derive the set; the citations carry independent
                  weight and n_eff is large.
                B ONE COMPUTATION, MANY QUOTES: one round derives and the rest restate; the
                  deliverable's central number rests on a single un-replicated computation, and 22
                  citations are 1 computation quoted 22 times.
KILL            pre-registered: ZERO derivers -> the classifier is broken, verdict UNVERIFIED.
CONFOUND        docstrings quote arm names in every round header, so a raw literal count measures
                PROSE. Stripped via tokenizer; the NEGATIVE control checks the strip works.
POSITIVE CTRL   a synthetic source with all five as list literals -> RESTATES.
g=0             a synthetic source with none -> not RESTATES; the detector returns both values.
NEGATIVE CTRL   all five inside a docstring only -> DERIVES after stripping.
PLACEBO         classification run twice is identical.
ARTIFACT        results/n_eff.json
IMPOSSIBLE      proving independent computation would need each round re-executed against its own
                inputs; 93 rounds in this arc are corpus-dependent and would not reproduce.
"""
from __future__ import annotations
import io, json, pathlib, re, subprocess, sys, tokenize

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
ARC = HERE.parent
FIVE = frozenset({"coval_core", "topw_k3", "topw_k4", "topw_k6", "topw_k8"})


def executable_source(src: str) -> str:
    """⭐ Strip comments AND docstrings. Every round header quotes arm names; without this the
       count measures PROSE, which is the confound named before the run."""
    out, prev_end, prev_tok = [], (1, 0), tokenize.INDENT
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    except Exception:
        return src
    for t in toks:
        if t.type == tokenize.COMMENT:
            continue
        if t.type == tokenize.STRING and prev_tok in (tokenize.INDENT, tokenize.NEWLINE,
                                                      tokenize.NL, tokenize.DEDENT,
                                                      tokenize.ENCODING):
            prev_tok = t.type
            continue                     # a bare string statement = a docstring
        out.append(t.string)
        if t.type not in (tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT):
            prev_tok = t.type
        elif t.type in (tokenize.NEWLINE, tokenize.NL):
            prev_tok = t.type
    return " ".join(out)


def literals(src: str) -> int:
    ex = executable_source(src)
    return sum(1 for m in FIVE if re.search(rf'["\']{re.escape(m)}["\']', ex))


def holds_set(j: pathlib.Path) -> bool:
    try: o = json.loads(j.read_text())
    except Exception: return False
    found = [False]
    def walk(x):
        if found[0]: return
        if isinstance(x, dict):
            for v in x.values(): walk(v)
        elif isinstance(x, list):
            if all(isinstance(y, str) for y in x) and frozenset(x) == FIVE:
                found[0] = True; return
            for v in x: walk(v)
    walk(o)
    return found[0]


def main() -> int:
    print("─── CONTROLS ───")
    pos = literals('X = ["coval_core", "topw_k3", "topw_k4", "topw_k6", "topw_k8"]')
    print(f"  POSITIVE  all five as list literals -> {pos}/5 -> "
          f"{'PASS (RESTATES)' if pos == 5 else '⛔ FAIL'}")
    g0 = literals('X = compute_from(data)\nY = [a for a in arms if ok(a)]')
    print(f"  g=0       a source with none -> {g0}/5 -> "
          f"{'PASS — the detector returns both values' if g0 == 0 else '⛔ FAIL'}")
    docsrc = ('"""header quoting coval_core topw_k3 topw_k4 topw_k6 topw_k8 as prose."""\n'
              'def f():\n    """also "coval_core" and "topw_k3" and "topw_k4" here."""\n    return 1\n')
    neg = literals(docsrc)
    print(f"  NEGATIVE  all five in a DOCSTRING only -> {neg}/5 -> "
          f"{'PASS — the confound is stripped' if neg == 0 else f'⛔ FAIL — prose counted as code ({neg})'}")
    plc = literals(docsrc) == neg and literals(
        'X = ["coval_core", "topw_k3", "topw_k4", "topw_k6", "topw_k8"]') == pos
    print(f"  PLACEBO   run twice identical -> {'PASS' if plc else '⛔ FAIL'}")
    ctl = pos == 5 and g0 == 0 and neg == 0 and plc

    rounds = []
    for d in sorted(ARC.glob("R*")):
        res = d / "results"
        if not res.is_dir() or not (d / "run.py").is_file(): continue
        if not any(holds_set(j) for j in res.glob("*.json")): continue
        n = literals((d / "run.py").read_text(errors="ignore"))
        rounds.append({"round": d.name.split("_")[0], "literals": n, "derives": n == 0})

    if not rounds:
        print("\nUNRUNNABLE: 0 rounds hold the set. Exit 2, never 0 — and never a verdict."); return 2

    der = [r for r in rounds if r["derives"]]
    print(f"\n─── THE COUNT (G3 — every round holding the set, none sampled) ───")
    for r in sorted(rounds, key=lambda r: (r["literals"], r["round"])):
        print(f"  {r['round']:<7} literals in executable source: {r['literals']}/5   "
              f"{'⭐ DERIVES' if r['derives'] else 'restates'}")
    share = len(der) / len(rounds)
    print(f"\n  rounds whose results hold the set : {len(rounds)}")
    print(f"  ⭐ DERIVE it (0 code literals)     : {len(der)}  -> {[r['round'] for r in der]}")
    print(f"  restate it                        : {len(rounds) - len(der)}")
    print(f"  registered A 3 [1,8] -> {len(der)}: "
          f"{'INSIDE' if 1 <= len(der) <= 8 else '⛔ OUTSIDE'}, error {len(der)-3:+d}")
    print(f"  registered B 30% [10,60] -> {share:.1%}: "
          f"{'INSIDE' if 0.10 <= share <= 0.60 else '⛔ OUTSIDE'}, error {share-0.30:+.1%}")
    dirn = any(r["round"] == "R294" for r in der)
    print(f"  DIRECTIONAL R294 (the producer) is among the derivers -> "
          f"{'HOLDS' if dirn else '⛔ FAILS'}")
    killed = len(der) == 0

    # ⭐ TIGHTEN THE UPPER BOUND INSIDE THE ROUND, since it is one grep. "No code literals" admits
    #   copying THROUGH A FILE. A deriver that reads another round's results/ is not independent of
    #   it. This does not prove independence either -- it removes one way of faking it.
    READS = re.compile(r"results/[\w.]+\.json|R\d{3}[\w]*/results", re.I)
    indep, reads = [], []
    for r in der:
        d = next(iter(ARC.glob(f"{r['round']}_*")), None)
        src = executable_source((d / "run.py").read_text(errors="ignore")) if d else ""
        (reads if READS.search(src) else indep).append(r["round"])
    print(f"\n  ⭐ OF THE {len(der)} DERIVERS — do they read another round's artifact?")
    print(f"     read a prior results/ file : {len(reads)}  {reads}")
    print(f"     read none                  : {len(indep)}  {indep}")
    print(f"     ⚠ so independent computations are AT MOST {len(indep)}, not {len(der)} — and still")
    print(f"       at most, because reading the release's own data is not copying but sharing a source.")

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire; no derivation count is admissible."
    elif killed:
        world = ("UNVERIFIED — zero derivers. The set must be computed somewhere, so the classifier "
                 "is broken rather than the corpus empty. Never 'nobody computed it'.")
    else:
        world = (f"⭐⭐⭐ {len(der)} of {len(rounds)} rounds holding the ③ extension DERIVE it; "
                 f"{len(rounds)-len(der)} carry it as code literals. R679 measured 22 rounds cited by "
                 f"the deliverable's extension rows. ⭐ SO THE CITATION COUNT AND THE COMPUTATION "
                 f"COUNT ARE DIFFERENT NUMBERS, and it is the second that bounds how much independent "
                 f"support the deliverable's central set has. ⚠ AND THIS IS AN UPPER BOUND ON "
                 f"INDEPENDENCE, NOT A COUNT OF IT: a round with no code literals may still READ the "
                 f"set from another round's artifact, which is copying through a file and is not "
                 f"separated here. The honest reading is 'at most {len(der)} independent "
                 f"computations', never 'exactly {len(der)}'. ⭐ TIGHTENED INSIDE THIS ROUND: {len(reads)} "
                 f"of the {len(der)} derivers read a prior round's results/ file, so the bound on "
                 f"independent computations is AT MOST {len(indep)}.")
    print(f"  {world}")

    sha = subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True).stdout.strip()
    print(f"\n  MULTIPLICITY: {len(rounds)} rounds × 1 set, 4 controls.")
    print(f"  ⭐ tree sha: {sha[:12]}")
    (HERE/"results").mkdir(exist_ok=True)
    (HERE/"results"/"n_eff.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha,
        "n_rounds_holding_set": len(rounds), "n_derive": len(der), "derive_share": share,
        "derivers": [r["round"] for r in der], "rounds": rounds,
        "derivers_reading_prior_artifact": reads, "derivers_reading_none": indep,
        "independent_upper_bound": len(indep),
        "kill_fired": killed, "directional_holds": dirn,
        "registered": "A 3 [1,8]; B 30% [10,60]; R294 among derivers; kill if 0 derive",
        "check281": ("R679's proposed test -- set present as a VALUE in results/ -- is invariant "
                     "under the recompute/restate distinction, so it is blind. Killed by a gauge "
                     "test at zero compute."),
        "upper_bound": ("no code literals does not prove independent computation; a round may read "
                        "the set from another round's artifact. At most N, never exactly N."),
    }, indent=2))
    print(f"  wrote {HERE/'results'/'n_eff.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
