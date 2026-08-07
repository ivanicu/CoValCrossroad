# R840 · a FAILING gate and a BLIND gate share an exit code

**Arc A25 — can the instrument be run at all.** Opened by entry 1353, which found
`next_gradient_labels_its_hypotheses.py` sitting in the census FAIL column while its own output said
*"a control misbehaved; the counts above are silence."* It was not failing. **It was dark**, and had
been for ~646 commits, because its positive control anchored two fixed commits inside a sliding
60-commit window.

**This round asks whether that was one accident or a population.**

---

## PRE-REGISTRATION — written before the run

### ESTIMAND
Among the assurance gates that exit non-zero, the count that are **DARK** (their own declared
controls did not validate, so the gate's output is *silence about the repository*) versus
**FAILING** (every declared control passed and the gate reports a real defect).

**This is a count over gates, not over defects.** The claim's unit is *a gate's epistemic status*;
the instrument's unit is *lines printed on stdout*. Named separately and required to match before
the control was designed, per §4's grep row.

### IDENTIFICATION
Yes, and cheaply — every gate in this suite prints its control lines. **The quantity is not
recoverable from exit status**, which is the whole point: exit 1 is emitted by both classes.

### SCOPE
- **population** — every `assurance/*.py` the push sweep runs (excludes `_*` helpers, the two
  tree-moving scripts, `run_all.py`, `HEADLINES.py`), restricted to those that exited non-zero: **14**
- **instrument** — a stdout classifier, pre-registered below
- **baseline** — the census's current reading, which treats all 14 as one class
- **regime** — this repo at this commit; a gate's status is a property of the pair, not of the gate

### WORLDS
| | prediction if run |
|---|---|
| **A · 1353 was an accident** | ~1 dark gate (the one already found). The FAIL column means what the census says. |
| **B · darkness is a population** | several dark gates. **The census's FAIL count is not a defect count**, and every ratchet built on it inherits the error. |
| **C · the classifier cannot separate them** | the positive control fails and the round returns UNVERIFIED. |

### CLASSIFICATION RULE — fixed before any gate was read
```
DARK      exit == 124 (timed out: no verdict was produced)
       or exit == 2   (this suite's declared code for unrunnable / empty population)
       or stdout matches a CONTROL line marked FAIL/UNRUNNABLE/BLIND
FAILING   exit == 1 AND every CONTROL line found is PASS AND >=1 control line exists
UNCLASSIFIED  anything else — reported separately, NEVER folded into either
```
**Three-valued.** UNCLASSIFIED is not an acquittal and is not darkness.

### POSITIVE CONTROL — the same gate at two commits
`next_gradient_labels_its_hypotheses.py` is known to be **DARK at `HEAD~1`** (control `0/2 caught`)
and **FAILING at `HEAD`** (control `2/2 caught`, 15 findings). The two versions differ **only in the
defect**. The classifier must return `DARK` for the first and `FAILING` for the second.

⚠ **And it must fail at g = 0:** a gate that exits 0 must classify as `GREEN`, not as either arm. A
classifier that labels everything DARK would pass a one-sided control.

### PRE-REGISTERED KILL — a conditional, not a threshold
```
if positive_control_both_arms_correct and g0_arm_correct:
    report the counts
else:
    verdict = UNVERIFIED        # never "the census is fine", never "the census is broken"
```
**A classifier that cannot separate the one case I already know is not entitled to an opinion about
the thirteen I don't.**

### WHAT THIS ROUND STRUCTURALLY CANNOT DO
| criterion | why not, and what it would require |
|---|---|
| independently replicated | one repo, one suite — a second suite built by someone else |
| construct validated | *"dark"* has no external gold standard; the control anchors it to **one** adjudicated case, which is a calibration, not a validation |
| cross-dataset / cross-domain | this suite only |
| causally identified | naming *why* a gate went dark needs a per-gate intervention; this round classifies, it does not explain |

⚠ **Marked N/A, not "planned".**

---

## RESULT — world **B**. Darkness is a population, not an accident.

**Positive control passed on all three arms** (`fd99c0f0`→DARK, `098784e9`→FAILING, known-green→GREEN),
so the pre-registered kill is satisfied and the counts below are admissible.

| class | n | meaning |
|---|---:|---|
| **DARK** | **5** | the gate's output is **silence about the repo** — 1 timeout, 4 exit-2 |
| **FAILING** | **3** | controls printed and all passed; the defect is real |
| **UNCLASSIFIED** | **6** | my classifier found **no control line** — a claim about the instrument |
| GREEN | 0 | |

⭐ **Of 14 gates in the census's FAIL column, only 3 are established as genuinely failing.**
**The FAIL column is not a defect count**, and every ratchet reading it as one inherits the error.

### ⚠ THE 6 UNCLASSIFIED SPLIT IN TWO — and folding them into a finding would have been the error

`UNCLASSIFIED` means *my* classifier saw no control **line**. That is a statement about the
instrument until the **source** is read. Read (`results/unclassified_split.json`), with the
source-grep's own positive control reported — a gate known to carry synthetic plants scores **23**:

| gate | control vocabulary in source | reading |
|---|---:|---|
| `attack_every_check.py` | **48** / 279 lines | has controls; **my output-format matcher is blind to it** |
| `attack_no_withdrawn_framings.py` | 6 / 95 | same |
| `attack_outcome_variable_declared.py` | 2 / 59 | same |
| `retired_framing_in_emittable_source.py` | 1 / 140 | same |
| `outcome_variable_declared.py` | **0** / 137 | **no control detected** |
| `seed_filter_is_disclosed.py` | **0** / 161 | **no control detected** |

⚠ **`NO CONTROL DETECTED`, never `NO CONTROLS`** — a word list cannot establish an absence.

### ⛔ THE DEFECT THIS ROUND BUILT INTO ITSELF

The first version of the positive control read **`HEAD~1`** — *a sliding reference to a fixed
object*, which is **exactly the defect entries 1353 and 1354 measured**, committed for the third
time **inside the round investigating the first two, within the same hour**. It was correct at
launch and wrong twenty minutes later: the next commit made `HEAD~1` the *repaired* file, so the
known-DARK arm would have silently stopped being dark and the control would have failed **for its
own reasons**. Both arms are now pinned by hash.

⭐ **The rule this round earned three times over: a control's anchor must be an IDENTITY, never a
POSITION.** `HEAD~1`, `-n 60`, *"the last release"*, *"recent commits"* are all positions.

**Reproducibility:** re-run at `c37a45b8` (a different commit from the first run's `098784e9`)
returned **identical counts and identical per-gate classes**. That holds *because* the anchors are
pinned — the pre-pin version would have failed its own control on the second run.
