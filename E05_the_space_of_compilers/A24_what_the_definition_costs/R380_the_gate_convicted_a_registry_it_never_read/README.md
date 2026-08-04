# R380 — the gate convicted seventeen rounds using a glob that matched zero files

**The decision this makes safe:** *is the donor registry stale?* **No.** The gate never read the
source it accused. **Repaired — and still not green, because that is the honest state.**

## Result — `W_PATH_BLIND_GATE2_VACUOUS`. Four controls PASS. Two runs byte-identical. **No GPU spent.**

The gate's output was:

```
rounds constructing a donor mapping: 0   registry entries: 17
FINDING: 17 registry entr(ies) name a round that no longer constructs a donor mapping
         -- the registry has drifted from the source
```

| | |
|---|---:|
| files matched by the gate's glob `rounds/E*/A*/R*/run.py` | **0** |
| files actually at `E0*/A*/R*/run.py` | **363** |
| registry rounds located once the detector is pointed at the tree | **17 of 17** |

> **A `0` from a detector never shown to return non-zero is silence — and here it produced an
> ACCUSATION.** The obvious action on that output is to delete seventeen registry entries. That
> would have destroyed the record to satisfy a typo.

## ⛔ The gate's own docstring predicted this

> *"the registry is not trusted — it is VERIFIED against the source tree on every run"* … *"a check
> that is right about what it iterates over and blind to what is missing"*

It then iterated `ROOT/rounds/E*/A*/R*/run.py`. **The confession was written and the code did the
opposite.**

## ⭐ Repairing the path immediately surfaced what the gate exists for

**`R106_share_level_under_redraw`** and **`R109_donor_arm_is_text_blind`** construct donor mappings
and were in no registry. Both are now registered as needing a draw scope — R106's estimand *is* the
sampling distribution of a share's level over independent donor draws; R109's is whether the donor
arm responds to donor content at all.

**The gate's stated purpose — *"a new donor round that nobody classified FAILS rather than passing
silently"* — was fully defeated by the path bug, and repairing it found two on the first run.**

## ⛔ Repairing only GATE 1 would have disarmed the gate by making it green

GATE 2 rules on **README table rows**. The root README stopped being a per-round table:

| | |
|---|---:|
| locatable table rows for registry rounds | **0** |
| registry rounds mentioned in README.md at all | **1 of 20** |

**Its PROPERTY still stands; its PROXY is gone.** Choosing a new proxy is a design decision, not a
silent substitution — so the repaired gate now **says it examined nothing and exits 2**.

> **Fixing a gate is not the same as making it green.** A green gate whose second half rules on
> nothing is `realstat §4 · empty population passes`, introduced *by* a repair.

## ⛔ And my own guard masked a real finding — caught by the disarm proof

v1 of the guard returned **2 whenever GATE 2 was vacuous** — including when GATE 1 had just caught
an unregistered donor round. The plant fired, the FINDING printed, **and the exit code said "empty
population."** An exit code reporting the weaker of two facts hides the stronger.

Fixed: a GATE 1 failure takes precedence; **2 is reserved for *nothing examined AND nothing found*.**

| live gate | exit |
|---|---|
| unregistered donor round planted | **1** — the finding wins |
| plant removed (g=0) | **2** — the honest vacancy |

## Controls

| | returned |
|---|---|
| **DETECTOR (+)** | `R21_donor_distance` — located **by hand** at `E01_…/R21_donor_distance/run.py:111`, independently of this gate — is found |
| **DETECTOR (−)** | **343 of 363** rounds carry no donor idiom and are not flagged. Both directions: a detector flagging all 363 would pass the positive control and mean nothing |
| **DISARM PROOF** ⭐ | run on the **live repaired gate**, not only in this round: fires with the plant, silent at g=0 |
| reproducibility | two runs **byte-identical** (`52a0453d3ef3`) |

## Register

| criterion | status |
|---|---|
| **a third donor idiom** | **N/A, unchanged** — invisible to both regexes, exactly as the gate's own docstring states. This repaired **where** it looks, never **what** it recognises |
| **GATE 2's property** | **still stands** — a donor-difference number should state its draw where the finding is stated. What is gone is the proxy, and the vacancy is reported rather than filled |
| **R106 / R109's `needs_scope`** | set **True** — the conservative direction, since True *demands* a scope. Each carries its reason |
| **a second release** | **N/A** — one release |

## The sentence I can no longer write

> *"17 registry entries name a round that no longer constructs a donor mapping — the registry has
> drifted from the source."*

**All seventeen construct one. The glob matched zero files in the entire repository, and the gate
convicted a registry it never read.**

Artifact: `results/r380_donor_gate.json`, source-stamped.
