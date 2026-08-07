"""R427/selftest -- a POSITIVE CONTROL on the ANALYSIS, run before the GPU finishes.

⛔ WHY. `run.py` has never executed. It was written, then patched three times -- a swept tiebreak, a
   FIRST baseline, a VACUOUS arm -- and every patch was made without running the file. Five judged
   arms are queued at ~10 minutes each. A crash discovered after 50 minutes of GPU is the cheap
   failure; a SILENTLY WRONG BRANCH is the expensive one, and this campaign's ledger records the
   verdict-string failure four times in one session.

⭐ THE LEDGER'S OWN RULE, APPLIED TO THE ANALYSIS RATHER THAN TO THE DATA. A zero from an instrument
   never shown to return non-zero is silence. `run.py` IS an instrument: it maps satisfaction to a
   world. So build worlds where the answer is KNOWN and require it to name each one.

⛔ ARITHMETIC TRAP. That a synthetic arm which always ranks the chosen response first achieves
   accuracy 1.0 is FORCED. It is a derivation and it is worthless as a finding -- which is exactly
   what makes it a usable positive control. What is NOT forced is whether `run.py`'s BRANCH names the
   right world when handed it, and that is the only thing tested here.

THE FIXTURES, each a world whose verdict is known in advance:
  ORACLE     satisfaction always ranks the human-chosen response first  -> must NOT be W-DOES-NOT
  NOISE      satisfaction is seeded noise, independent of the choice     -> must be W-DOES-NOT
  SATURATED  every response scores identically                          -> must be W-TIEBREAK
             (the world the gauge test bought; if this does not fire, that control is decorative)

CONTROLS ON THE CONTROL
  DISTINCT   the three fixtures must not produce the same verdict, or the analysis is a constant
             function and every real result it reports is meaningless.
  SCHEMA     the fixtures are written by the SAME np.savez_compressed call shape the producer uses,
             so a schema drift in the producer breaks this test too rather than passing silently.

EXIT
    0  every fixture is named correctly and the verdicts are distinct
    1  a fixture is misclassified, or the analysis is constant -- the ANALYSIS is unfit
    2  the analysis or corpus is missing -- never a silent pass
"""
from __future__ import annotations
import importlib.util
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent


def build(kind, data, crit_k=4, seed=0):
    """-> (meta, sat, targets) in the producer's exact schema."""
    rng = np.random.default_rng(seed)
    meta, sat, tgt = [], [], []
    for cid, iid, _pr, cands in data:
        chosen = [c[0] for c in cands if c[3]]
        tgt.append({"conv": cid, "inter": iid,
                    "resp": [{"id": r, "score": s, "chosen": ch, "len": len(t), "turn": tn}
                             for r, t, s, ch, tn in cands]})
        for rid, text, _s, ch, _tn in cands:
            if kind == "oracle":
                base = 1.0 if (chosen and rid == chosen[0]) else 0.0
            elif kind == "noise":
                base = float(rng.random())
            else:                                    # saturated
                base = 1.0
            for j in range(crit_k):
                meta.append(f"{cid}|{iid}|{rid}|{j}")
                sat.append(base)
    return np.array(meta), np.asarray(sat, np.float32), tgt


def main() -> int:
    prod = ROOT / "corebench" / "judge_transport.py"
    analysis = HERE / "run.py"
    corpus = ROOT / "data" / "utterances.jsonl"
    if not (prod.exists() and analysis.exists() and corpus.exists()):
        print("  UNRUNNABLE: producer, analysis or corpus absent. Exit 2, never 0."); return 2
    spec = importlib.util.spec_from_file_location("jt", prod)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    data = m.load_second(corpus, 120, 0)             # small: this tests LOGIC, not power

    print("R427 · selftest — a positive control on the ANALYSIS, before the GPU finishes\n")
    print("  ⛔ run.py has never executed. Written, then patched three times — swept tiebreak, FIRST")
    print("     baseline, VACUOUS arm — every patch made without running the file, with five judged")
    print("     arms queued at ~10 minutes each.\n")

    want = {"oracle": ("not", "W-DOES-NOT"), "noise": ("is", "W-DOES-NOT"),
            "saturated": ("is", "W-TIEBREAK")}
    got, ok_all = {}, True
    for kind in ("oracle", "noise", "saturated"):
        tmp = pathlib.Path(tempfile.mkdtemp(prefix=f"r427st_{kind}_"))
        try:
            (tmp / "results").mkdir()
            meta, sat, tgt = build(kind, data)
            np.savez_compressed(tmp / "sat_transport_generic.npz", meta=meta, sat=sat,
                                targets=np.array(json.dumps(tgt)),
                                provenance=np.array(json.dumps({"corpus": f"SYNTHETIC:{kind}"})))
            # ⛔ THE FIRST VERSION OF THIS HARNESS FAILED FOR ITS OWN REASONS -- the ledger's
            #    dominant control failure, 4 of 7 in one day. It copied run.py into a shallow tmp
            #    dir where `parents[3]` does not exist, so all three fixtures died with IndexError
            #    and the analysis was never exercised at all. ROOT must be rewritten too.
            src = analysis.read_text().replace(
                'ROOT = pathlib.Path(__file__).resolve().parents[3]',
                f'ROOT = pathlib.Path({str(ROOT)!r})').replace(
                'RES = ROOT / "corebench" / "results"', f'RES = pathlib.Path({str(tmp)!r})').replace(
                'HERE = SELF.parent', f'HERE = pathlib.Path({str(tmp)!r})')
            probe = tmp / "probe.py"
            probe.write_text(src)
            r = subprocess.run([str(ROOT / ".venv" / "bin" / "python"), str(probe)],
                               capture_output=True, text=True, timeout=900)
            out = r.stdout + r.stderr
            verdict = next((w for w in ("W-TIEBREAK", "W-DOES-NOT", "W-LENGTH", "W-ANY-CRITERIA",
                                        "W-VACUOUS", "W-TRANSPORTS", "UNVERIFIED")
                            if w in out), f"NONE (rc={r.returncode})")
            got[kind] = verdict
            rel, exp = want[kind]
            # ⛔ AND THE `must NOT be` RELATION WAS A CHECK THAT COULD NOT FAIL: a CRASH satisfies
            #    "not W-DOES-NOT". The verdict must first be a REAL verdict, then the relation is
            #    evaluated. Without this, a broken analysis passes the oracle fixture.
            real = verdict in ("W-TIEBREAK", "W-DOES-NOT", "W-LENGTH", "W-ANY-CRITERIA",
                               "W-VACUOUS", "W-TRANSPORTS", "UNVERIFIED")
            ok = real and ((verdict != exp) if rel == "not" else (verdict == exp))
            ok_all &= ok
            print(f"    {kind:<10} verdict {verdict:<16} must {'NOT be' if rel=='not' else 'be'} "
                  f"{exp:<12} {'ok' if ok else ('⛔ NOT A VERDICT' if not real else '⛔ MISCLASSIFIED')}")
            if not ok:
                tail = [l for l in out.strip().splitlines() if l.strip()][-4:]
                for l in tail:
                    print(f"        {l[:100]}")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    distinct = len(set(got.values())) > 1
    print(f"\n  CONTROL · DISTINCT  the three fixtures produce {len(set(got.values()))} different "
          f"verdicts: {distinct}   {'PASS' if distinct else 'FAIL — the analysis is a CONSTANT'}")
    print(f"    a constant analysis names the same world whatever it is handed, and every real")
    print(f"    result it reports would be meaningless.")

    print()
    if ok_all and distinct:
        print("  PASS — the analysis names each known world correctly and is not constant. The 50")
        print("  minutes of GPU now queued will be read by an instrument that has been shown able to")
        print("  return more than one answer.")
        return 0
    print("  FAIL — the ANALYSIS is unfit. This is the cheap failure and it was found before the")
    print("  arms landed, which is the entire point of running it now.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
