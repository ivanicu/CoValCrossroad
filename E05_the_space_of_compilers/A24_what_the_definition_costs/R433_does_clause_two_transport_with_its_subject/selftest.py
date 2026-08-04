"""R433/selftest -- a POSITIVE CONTROL ON THE ANALYSIS, run before the GPU finishes.

⛔ WHY. `run.py` has never executed and ~40 minutes of judging are queued behind it. R427 wrote the
   same file for the same reason and it earned its keep: a crash discovered after the arms land is
   the CHEAP failure; a SILENTLY WRONG BRANCH is the expensive one, and this campaign's ledger
   records the verdict-string failure four times in one session and twice more since.

⭐ THE LEDGER'S OWN RULE, TURNED ON THE ANALYSIS RATHER THAN THE DATA. A zero from an instrument
   never shown to return non-zero is silence. `run.py` IS an instrument: it maps two scored arms to
   a world. So build worlds where the answer is KNOWN and require it to name each one.

⛔ ARITHMETIC TRAP, NAMED. That a synthetic arm which always ranks the chosen response first scores
   1.0 is FORCED. It is a derivation and worthless as a finding -- which is exactly what makes it a
   usable fixture. What is NOT forced is whether run.py's BRANCH names the right world when handed
   it, and that is the only thing tested here.

THE FIXTURES, each a world whose verdict is known in advance:
  TRANSPORTS  the generated arm always picks the chosen response, the length rule rarely does
              -> must be W-TRANSPORTS
  LOSES       the generated arm picks at random, the length rule always picks the chosen one
              -> must be W-LOSES
  FILLER      the sham scores RESOLVEDLY ABOVE the real arm -> must be W-FILLER.
              ⛔ THIS FIXTURE WAS REBUILT. It first made sham IDENTICAL to gen and demanded
              W-FILLER, which encodes the PRE-AMENDMENT semantics: under AMENDMENT 1 an equal sham
              means the conversation-match buys nothing MEASURABLE, which is a bound and is reported
              as the `sham_verdict` diagnostic, while W-FILLER is reserved for the genuinely
              surprising event -- criteria from the WRONG conversation beating the right ones by
              more than the design's own resolution. A fixture that demands the old behaviour after
              the design was corrected tests my memory, not the code.

CONTROLS ON THE CONTROL
  DISTINCT  the three fixtures must not produce the same verdict, or the analysis is a constant
            function and every real result it reports is meaningless.
  SCHEMA    the fixtures are written by the SAME np.savez_compressed call shape the producer uses,
            INCLUDING the provenance fields run.py refuses on -- so a schema drift in the producer
            breaks this test too rather than passing silently.

EXIT  0 every fixture named correctly and the verdicts distinct
      1 a fixture is misclassified, or the analysis is constant -- the ANALYSIS is unfit
      2 the analysis or its inputs are missing -- never a silent pass
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
K = 4


def build(kind, n_conv=60, n_inter=3, n_resp=3, seed=0):
    """-> {armname: (meta, sat, targets, provenance)} in the producer's exact schema."""
    rng = np.random.default_rng(seed)
    tgt, layout = [], []
    for ci in range(n_conv):
        for ii in range(n_inter):
            ids = [f"r{ci}_{ii}_{k}" for k in range(n_resp)]
            chosen = ids[rng.integers(n_resp)]
            # the LENGTH rule picks the longest; make it the chosen one only when we want it to win
            lens = {r: 10 + i for i, r in enumerate(ids)}
            if kind == "loses":
                lens = {r: (100 if r == chosen else 10) for r in ids}
            else:
                loser = [r for r in ids if r != chosen][0]
                lens = {r: (100 if r == loser else 10) for r in ids}
            layout.append((f"c{ci}", f"i{ci}_{ii}", ids, chosen))
            tgt.append({"conv": f"c{ci}", "inter": f"i{ci}_{ii}",
                        "resp": [{"id": r, "score": 50.0, "chosen": r == chosen,
                                  "len": lens[r], "turn": ii} for r in ids]})

    def arm(rule, tag):
        meta, sat = [], []
        for cid, iid, ids, chosen in layout:
            for r in ids:
                v = rule(r, chosen, ids)
                for j in range(K):
                    meta.append(f"{cid}|{iid}|{r}|{j}"); sat.append(v)
        prov = {"core_mode": "conversation_keyed", "n_criterion_sets": 2200,
                "n_criteria": [K], "n_calls": len(meta),
                "criteria_sha256": hashlib.sha256(tag.encode()).hexdigest()}
        return (np.array(meta), np.asarray(sat, np.float32), tgt, prov)

    oracle = lambda r, ch, ids: 1.0 if r == ch else 0.0
    rand = lambda r, ch, ids: float(rng.random())
    out = {}
    if kind == "transports":
        out["gen"] = arm(oracle, "gen"); out["sham"] = arm(rand, "sham")
    elif kind == "loses":
        out["gen"] = arm(rand, "gen"); out["sham"] = arm(rand, "sham2")
    else:                                        # filler: the SHAM resolvedly BEATS the real arm
        out["gen"] = arm(rand, "gen"); out["sham"] = arm(oracle, "sham3")
    out["generic"] = arm(rand, "generic")
    return out


def main() -> int:
    analysis = HERE / "run.py"
    pre = HERE / "PREREGISTRATION.md"
    if not (analysis.exists() and pre.exists()):
        print("  UNRUNNABLE: analysis or preregistration absent. Exit 2, never 0."); return 2

    print("R433 · selftest — a positive control on the ANALYSIS, before the GPU finishes\n")
    print("  ⛔ run.py has never executed and ~40 minutes of judging are queued behind it.\n")

    want = {"transports": "W-TRANSPORTS", "loses": "W-LOSES", "filler": "W-FILLER"}
    got, ok_all = {}, True
    for kind in ("transports", "loses", "filler"):
        tmp = pathlib.Path(tempfile.mkdtemp(prefix=f"r433st_{kind}_"))
        try:
            (tmp / "corebench" / "results").mkdir(parents=True)
            (tmp / "results").mkdir(parents=True, exist_ok=True)
            arms = build(kind)
            for name, stem in (("gen", "sat_transport_gen"), ("sham", "sat_transport_gen_sham"),
                               ("generic", "sat_transport_generic")):
                meta, sat, tgt, prov = arms[name]
                np.savez_compressed(tmp / "corebench" / "results" / f"{stem}.npz",
                                    meta=meta, sat=sat, targets=np.array(json.dumps(tgt)),
                                    provenance=np.array(json.dumps(prov, sort_keys=True)))
            # ⛔ ROOT AND SAT MUST BOTH BE REWRITTEN. R427's first harness copied the analysis into a
            #    shallow tmp dir where `parents[3]` does not exist, so every fixture died with
            #    IndexError and the analysis was never exercised at all -- a control that reports
            #    success having executed nothing, inside the file written to prevent exactly that.
            src = analysis.read_text().replace(
                'ROOT = pathlib.Path(__file__).resolve().parents[3]',
                f'ROOT = pathlib.Path({str(ROOT)!r})').replace(
                'SAT = ROOT / "corebench" / "results"',
                f'SAT = pathlib.Path({str(tmp / "corebench" / "results")!r})').replace(
                'HERE = pathlib.Path(__file__).resolve().parent',
                f'HERE = pathlib.Path({str(tmp)!r})')
            shutil.copy(pre, tmp / "PREREGISTRATION.md")
            probe = tmp / "probe.py"
            probe.write_text(src)
            r = subprocess.run([str(ROOT / ".venv" / "bin" / "python"), str(probe)],
                               capture_output=True, text=True, timeout=900)
            out = r.stdout + r.stderr
            verdict = next((w for w in ("W-FILLER", "W-TRANSPORTS", "W-LOSES", "W-UNRESOLVED",
                                        "UNVERIFIED") if f"WORLD: {w}" in out),
                           f"NONE (rc={r.returncode})")
            got[kind] = verdict
            good = verdict == want[kind]
            ok_all &= good
            print(f"    {kind:<11} verdict {verdict:<14} must be {want[kind]:<14} "
                  f"{'ok' if good else '⛔ MISCLASSIFIED'}")
            if not good:
                for l in [x for x in out.strip().splitlines() if x.strip()][-6:]:
                    print(f"        {l[:110]}")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    distinct = len(set(got.values())) > 1
    print(f"\n  CONTROL · DISTINCT  the three fixtures produce {len(set(got.values()))} different "
          f"verdicts   {'PASS' if distinct else 'FAIL — the analysis is a CONSTANT'}")
    print("    a constant analysis names the same world whatever it is handed, and every real")
    print("    result it reports would be meaningless.")

    print()
    if ok_all and distinct:
        print("  PASS — the analysis names each known world correctly and is not constant. The")
        print("  judging now queued will be read by an instrument shown able to return more than")
        print("  one answer, INCLUDING W-FILLER — which under AMENDMENT 1 is a RESOLVED INVERSION,")
        print("  no longer a veto. (This sentence said 'the world that voids the other three' until")
        print("  the amendment landed; a stale verdict string in the file that exists to catch stale")
        print("  verdict strings is the joke this campaign keeps writing.)")
        return 0
    print("  FAIL — the ANALYSIS is unfit. This is the cheap failure and it was found before the")
    print("  arms landed, which is the entire point of running it now.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
