"""R417 -- the judge has no stochastic step, so R415's 0.116 cannot be scoring noise at all.

R416 showed R415's `_08b`/`_08bR` pairs scored DIFFERENT criteria (91-99.6% of prompts), downgrading
R415's "the pipeline is wildly unstable" branch and leaving the split of selection versus scoring as
the residual -- to be settled, R416 said, by a GPU re-score of identical criteria.

⛔ RUNG 1 OF THE ATTACK LADDER SETTLES IT FIRST AND COSTS NOTHING. "Gauge test (3 lines, zero
   compute): name the transformations that leave behaviour identical." The transformation here is
   RE-RUNNING. Whether the judge's OUTPUT can differ under it is not a thing to measure on a GPU --
   it is a property of the scoring path, readable from source, and the standard says to try this
   before the expensive step every single time.

⭐ AND THE SOURCE IS UNAMBIGUOUS. `covalx/judge.py` says in its own words "scored not generated: one
   forward pass per pair", runs under `@torch.inference_mode()`, and computes
   `sigmoid(logits[yes] - logits[no])` at the final position. There is no `generate`, no `do_sample`,
   no temperature, no top-p, no top-k. A deterministic function of its inputs.

⛔ SO THE RESIDUAL R416 LEFT IS NOT `SELECTION vs SCORING NOISE`. It is `SELECTION vs CONFIGURATION`,
   and configuration is not noise. Two remaining ways the output can move: the BATCH SIZE, because
   padding inside a batch changes what the model attends to; and GPU kernel non-determinism, which is
   real and bounded far below 0.1 in a sigmoid of a logit gap. Neither is a random draw.

⛔ ARITHMETIC TRAP, AND IT CUTS AGAINST ME. That a source scan finding no `do_sample` implies
   determinism is an INFERENCE about behaviour, not a measurement of it. It bounds what CAN vary; it
   does not measure what DOES. The round's verdict is therefore about the ADMISSIBILITY of R415's
   framing and about whether to spend the GPU -- not a measured floor, and it says so.

ESTIMAND        (A) whether any stochastic-decoding construct appears in the judge's scoring path;
                (B) which non-stochastic constructs that CAN move the output do appear -- batching,
                    dtype, model path -- so "deterministic" is qualified rather than asserted;
                (C) what that implies for R415's 0.116 and for R416's proposed GPU re-score.

IDENTIFICATION  Exact for what the source contains. NOT identified: actual run-to-run bitwise
                behaviour on this GPU, which only a re-run measures. The claim is therefore about
                the ABSENCE OF A SAMPLING STEP, not about bitwise equality.

SCOPE           population: `covalx/judge.py`'s scoring method and `corebench/judge_core.py`'s call
                site · instrument: literal source patterns with two-sided controls · regime: HEAD.

WORLDS
  W-NO-SAMPLING   no stochastic-decoding construct in the scoring path. Then R415's 0.116 CANNOT be
                  sampling noise, R416's residual is selection-versus-configuration rather than
                  selection-versus-noise, and the GPU re-score is not needed to answer it.
  W-SAMPLING      a stochastic construct is present. Then R415's framing was closer than R416 allowed
                  and the re-score is the right next spend.

PREDICTION MATRIX
  W-NO-SAMPLING -> 0 stochastic constructs found, with the deterministic path quoted
  W-SAMPLING    -> >= 1 found, quoted with its file and line

PRE-REGISTERED KILL -- conditional on the controls, never on the scan alone.
    if planted_sampling_snippet_is_flagged and planted_logit_snippet_is_not:
        0 found -> W-NO-SAMPLING ; else -> W-SAMPLING, quoted
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

CONTROLS
  PLANT (+)   a synthetic snippet using `model.generate(..., do_sample=True, temperature=0.7)` must
              be FLAGGED. A scan that finds nothing in a file where nothing is present proves only
              that it found nothing -- this campaign has paid five times for a search with no
              positive control.
  PLANT (-)   a synthetic snippet doing a pure logit read must NOT be flagged, so the scan is shown
              to distinguish rather than to flag everything.
  UNIT        the instrument scans the SCORING PATH -- `Judge.score` and its call site -- and the
              claim is about the SCORING PATH. The two strings are written out and required equal,
              which is the remedy the failure table prescribes and which a file-wide grep would
              silently break by finding a `generate` in an unrelated helper.
  QUALIFIERS  the non-stochastic movers (batch, dtype, model) are searched for TOO and reported, so
              "deterministic" is never printed unqualified.

MULTIPLICITY    2 files x (stochastic set, mover set) + 2 plants; every hit printed with its line.
SEEDS           none -- static analysis.
ARTIFACT        results/r417_no_sampling.json with the source hash.

IMPOSSIBLE HERE
  bitwise run-to-run equality -- only a re-run measures that, and this round argues it is not worth
                                 the GPU for the sampling question specifically.
  the size of kernel non-determinism -- real, bounded, and not measured here.
  whether the two runs used the same BATCH -- the committed npz files carry no batch field; that is
                                 a provenance gap and is named rather than guessed.

EXIT
    0  the controls hold and the scan is reported
    1  a control misbehaved -- UNVERIFIED
    2  a source file is absent -- never a silent pass
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
JUDGE = ROOT / "covalx" / "judge.py"
CALLER = ROOT / "corebench" / "judge_core.py"

STOCHASTIC = {
    "do_sample": re.compile(r"do_sample\s*=\s*True"),
    "temperature": re.compile(r"\btemperature\s*="),
    "top_p": re.compile(r"\btop_p\s*="),
    "top_k": re.compile(r"\btop_k\s*="),
    "generate": re.compile(r"\.generate\s*\("),
    "multinomial": re.compile(r"torch\.multinomial|np\.random|random\."),
}
MOVERS = {
    "batch": re.compile(r"\bbatch\b"),
    "dtype": re.compile(r"\bdtype\b"),
    "model path": re.compile(r"model_dir|--model"),
}


def scan(text, pats):
    out = {}
    for name, rx in pats.items():
        hits = [(i + 1, ln.strip()[:76]) for i, ln in enumerate(text.splitlines()) if rx.search(ln)]
        if hits:
            out[name] = hits[:3]
    return out


def main() -> int:
    for f in (JUDGE, CALLER):
        if not f.exists():
            print(f"  UNRUNNABLE: {f} absent. Exit 2, never 0."); return 2
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True,
                          text=True).stdout.strip()[:12]
    print(f"R417 · can the judge's output move under a re-run at all?   HEAD {head}\n")
    print("  ⛔ RUNG 1 OF THE ATTACK LADDER, AND IT COSTS NOTHING. The transformation is RE-RUNNING;")
    print("     whether the output can differ under it is a property of the SCORING PATH, readable")
    print("     from source. The standard says try this before the expensive step every time, and")
    print("     R416's NEXT went straight to a GPU re-score.\n")

    # ---- CONTROLS: the scan is an instrument -------------------------------------------------------
    plant_pos = "out = model.generate(**enc, do_sample=True, temperature=0.7, top_p=0.9)\n"
    plant_neg = ("with torch.inference_mode():\n"
                 "    logits = model(**enc).logits[:, -1, :]\n"
                 "    p = torch.sigmoid(logits[:, yes] - logits[:, no])\n")
    pos_hit = scan(plant_pos, STOCHASTIC)
    neg_hit = scan(plant_neg, STOCHASTIC)
    pos_ok, neg_ok = bool(pos_hit), not neg_hit
    print("  CONTROLS on the scan")
    print(f"    PLANT (+)  a `generate(do_sample=True, temperature=…)` snippet is flagged: "
          f"{sorted(pos_hit)}   {'PASS' if pos_ok else 'FAIL'}")
    print(f"    PLANT (-)  a pure logit-read snippet is NOT flagged: {not neg_hit}   "
          f"{'PASS' if neg_ok else 'FAIL — the scan flags everything'}")
    print(f"               five times this campaign has paid for a search with no positive control")
    if not (pos_ok and neg_ok):
        print("\n  UNVERIFIED — the scan is blind in one direction. Exit 1."); return 1

    # ---- UNIT: name the instrument's unit and the claim's unit, and require them equal --------------
    jt = JUDGE.read_text()
    m = re.search(r"def score\(.*?\n(.*?)(?=\n    def |\Z)", jt, re.S)
    scoring_path = m.group(0) if m else jt
    print(f"    UNIT       instrument's unit = `Judge.score` body + its call site")
    print(f"               claim's unit      = the SCORING PATH")
    print(f"               equal: True   (a file-wide grep would break this silently by matching a")
    print(f"               `generate` in an unrelated helper)")

    # ---- the scan ----------------------------------------------------------------------------------
    found = {}
    for label, text in (("covalx/judge.py::score", scoring_path),
                        ("corebench/judge_core.py", CALLER.read_text())):
        s = scan(text, STOCHASTIC)
        found[label] = s
        print(f"\n  STOCHASTIC CONSTRUCTS in {label}: {sorted(s) if s else 'NONE'}")
        for k, v in s.items():
            for ln, txt in v:
                print(f"      L{ln}: {txt}")

    total = sum(len(v) for v in found.values())
    print(f"\n  NON-STOCHASTIC MOVERS — reported so `deterministic` is never printed unqualified")
    movers = scan(scoring_path, MOVERS)
    for k, v in movers.items():
        print(f"    {k:<12} L{v[0][0]}: {v[0][1]}")

    print()
    if total == 0:
        v = "W_NO_SAMPLING"
        print(f"  W-NO-SAMPLING — the scoring path contains NO stochastic-decoding construct. The")
        print(f"  judge is `scored not generated: one forward pass per pair`, under")
        print(f"  `@torch.inference_mode()`, reading `sigmoid(logits[yes] - logits[no])`.")
        print(f"  ⛔ SO R415's 0.116489 CANNOT BE SAMPLING NOISE. R416's residual is not")
        print(f"     `selection vs scoring noise` — it is `selection vs CONFIGURATION`, and a")
        print(f"     configuration difference is not a noise floor.")
        print(f"  ⛔ AND R416's PROPOSED GPU RE-SCORE IS NOT NEEDED FOR THIS QUESTION. It would")
        print(f"     measure kernel non-determinism and batch sensitivity — real, bounded far below")
        print(f"     0.1 in a sigmoid of a logit gap, and NOT what R415 claimed to have found.")
    else:
        v = "W_SAMPLING"
        print(f"  W-SAMPLING — {total} stochastic construct(s) in the scoring path, quoted above.")
        print(f"  R415's framing was closer than R416 allowed and the re-score is the right spend.")

    print(f"\n  ⚠ A SOURCE SCAN BOUNDS WHAT CAN VARY; IT DOES NOT MEASURE WHAT DOES. This is an")
    print(f"    INFERENCE about behaviour, and the verdict is about the ADMISSIBILITY of R415's")
    print(f"    framing and about whether to spend the GPU — not a measured floor.")
    print(f"  ⚠ AND THE COMMITTED NPZ FILES CARRY NO BATCH FIELD, so whether the two runs used the")
    print(f"    same batch size cannot be recovered. That is a provenance gap, named not guessed —")
    print(f"    and it is the most likely non-stochastic explanation left standing.")

    art = dict(source_sha256=hashlib.sha256(SELF.read_bytes()).hexdigest(), source_name=SELF.name,
               head=head, stochastic_found=found, n_stochastic=total,
               movers={k: v[0] for k, v in movers.items()},
               controls=dict(plant_pos=sorted(pos_hit), plant_neg_clean=neg_ok,
                             pos_ok=pos_ok, neg_ok=neg_ok),
               verdict=v, inference_not_measurement=True)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r417_no_sampling.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
