# R1085 — isolation is necessary for **safety** and buys **0** for **comparability**. Both measured.

**The decision this round makes safe:** whether R1084's excluded 41 need a cloned repository per run
to be measurable. **They need it to keep the real repository intact — and not, it turns out, to make
their floor readable.** The premise was half right and the sham says which half.

## The result, with its scope

**Population** the 41 writing scripts R1084 identified. **1** is excluded (`_one_home_per_claim_
UNVALIDATED.py` — a `SyntaxError`, `_`-prefixed, wired nowhere). **40** measured, each run in its own
fresh `git clone`. **Instrument** clone-per-run (~466 MB, ~0.4 s), CPython subprocess, 60 s timeout
enforced on the **process group**. **Baseline** the two-fresh-clone determinism floor. **Regime** this
checkout, tree verified clean before and after.

| | |
|---|---:|
| isolated floor clean | **35 of 40** |
| floor **dirty** even isolated | **1** — `attack_a_retraction_declares_its_class.py` |
| timed out (UNVERIFIED, not folded in) | **4** |
| **move between working directories** | **2** — `kill_is_wired_into_the_branch.py`, `manifest.py` |

⚠ **THE SHAM DEFLATES THE ROUND'S OWN PREMISE.** The same comparison with the ingredient removed —
both arms in **one** clone, which is R1084's design — leaves the floor dirty for **1 of 40**, the
same script. **Isolation buys 0 scripts of measurable floor.** For 39 of 40, running twice in place
would have given the same answer.

⭐ **What isolation does buy is measured by a different control, and it is not optional.** The POSITIVE
control shows a relative write dirties the clone and **leaves the real repository untouched**; R1084
measured what happens without that — `ASSURANCE.md` truncated to 22 of 111 lines, `DEFECTS.json`
−395, `MANIFEST.json` +943. **Isolation is a safety property, not a statistical one**, and this round
had to build it to learn that the statistic never needed it.

## Controls — 6, all green

| control | result |
|---|---|
| POSITIVE a relative write dirties the **clone** | PASS |
| POSITIVE …and leaves the **real repository** untouched | PASS |
| g=0 a plant that writes nothing dirties neither | PASS |
| NEGATIVE an **absolute** write **escapes** the clone (against a scratch sentinel) | PASS |
| NEGATIVE …and still did not touch the real repository | PASS |
| PLACEBO the isolated floor is clean for most of the population | PASS |

⛔ **The g=0 could not pass as first written.** The plant *file* is itself written into the clone, so
the clone was dirty by construction and the criterion was satisfied before anything ran — §4's
*control that cannot PASS*, built inside the round about isolation. It measures the **delta across
execution** now, not the count.

**Specification curve** — 4 cells. `2 / 3 / 2 / 2` moving: dropping path normalisation adds one, and
that cell is reported rather than dropped.

## ⛔ The first full run ABORTED on world C — and the cause was me

It stopped with *"the real repository changed while running
`backfilled_findings_are_rederivable.py`"* and refused to report numbers. Two candidate causes, both
checked against the object:

| candidate | evidence | verdict |
|---|---|---|
| a round script escaped the clone by absolute path | **0 of 1012** `E0*/A*/R*/run.py` carry a literal naming this repository (0 unparsable) | **refuted** |
| I edited the working tree during a run that watches it | my 5 `attack_*.py` repairs landed **18:00:40**; the abort was written **18:02:20** | **confirmed** |

**The control fired for its own reasons — the fourth time in this arc — and it was still right to
fire.** A safety control that only trips on causes you predicted is not a safety control; refusing to
report under an unattributed state change is the correct behaviour. What it lacks is the diff: it
says *that* the repository moved and not *what* moved, which is why the cause had to be reconstructed
from timestamps instead of read off.

⚠ **And that run's timeout could not bind.** `subprocess.run(timeout=…)` kills the direct child and
then keeps reading pipes a **grandchild** holds open —
`backfilled_findings_are_rederivable.py` launches `.venv/bin/python run.py` on round directories.
`run_in` now uses `start_new_session=True` + `os.killpg`, so the whole tree dies. The re-run reached
index 20 in 11 minutes where the old one reached index 15 in 13.

## Production shipped with this round

**5 scripts repaired** — `attack_a_published_number_is_named`, `attack_a_retraction_declares_its_class`,
`attack_no_withdrawn_framings`, `attack_outcome_variable_declared`, `attack_scope_reaches_the_reader`
carried `ROOT = Path("/home/ivan/research…")`, an absolute literal that reaches out of any clone and
breaks the moment the repository moves. All now derive `ROOT` from `__file__`. **Zero absolute
literals remain and every verdict is unchanged** (`1, 0, 1, 1, 0` before and after) — a repair that
moved a verdict would have been a different change. It is why 40 of 41 are isolable here where 35
would have been.

## ⛔ The arc-level measurement this round owes, computed from git

| | |
|---|---:|
| rounds since R1080 | **6** |
| lines added to `DEFINITION.md` | **144** |
| commits changing the clause text `resolvably beats` | **0** |

Six rounds shipped four instruments and **did not move the definition once**. Every round audits the
guard the previous one shipped. That is a basin, and naming it is worth more than the next guard.

## Impossibility register

| criterion | status | what it would require |
|---|---|---|
| the 4 timed-out scripts | **N/A** | a timeout longer than 60 s; they re-run round experiments and are minutes each |
| `_one_home_per_claim_UNVALIDATED.py` | **N/A** | it does not parse; repairing it is a rewrite, not a measurement |
| attributing a world-C abort to a script | **N/A here** | the control must record the diff, not just the state hash — named as the next fix |
| cross-repository | **N/A** | a second assurance directory |

`run.py` · `results/isolation_reaches_the_writers.json`
