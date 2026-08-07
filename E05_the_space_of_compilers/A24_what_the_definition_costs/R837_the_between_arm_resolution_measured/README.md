# R837 · the between-arm resolution, measured instead of bounded

**The decision this made safe:** whether R835's null was an artifact of its resolution. **It was, in
part** — one of the three flagged pairs separates at the true MDE, and the true MDEs are roughly
**half** R835's.

Design in `PREREGISTRATION.txt`, committed with `run.py` before it ran.

## My own NEXT asked for the wrong quantity

R836 closed: *"measure ρ."* ⛔ **ρ was only ever a route to `MDE_AC`.** R436's arm path needs the
human rankings and the committed `sat_*.npz` — **no response texts, no features, no judge** — so the
per-prompt difference vector is computable directly and its sd taken. **One step, not two.** §4's
*does the data have more to give?*, asked **before** the re-run this time.

## Result

| upper | lower | n | gap | sd | **TRUE MDE** | R835's MDE | verdict |
|---|---|---|---|---|---|---|---|
| `gen` | `random_k12_s0` | 968 | **+0.0347** | 0.1874 | **0.0118** | 0.0232 | **SEPARABLE** |
| `generic` | `gen` | 968 | +0.0137 | 0.1650 | **0.0104** | 0.0232 | inside 2×MDE |
| `promptecho` | `topvar_k4_08b` | 398 | +0.0302 | 0.2248 | **0.0221** | 0.0384 | inside 2×MDE |

**Controls**: `oracle_k4` vs `generic` → gap **+0.0759**, MDE **0.0106**, **SEPARABLE** ✓ · arm
against itself (scored twice through the same path) → **sd exactly 0** ✓ · three seeds
byte-identical ✓.

**W-RESOLVED.** ⭐ **`gen` separates from the random cluster at 2.9× MDE** — so the label-free class
is **not** noise, and clause ② holds inside it.

## R836's derivation validated, and its table's criterion corrected

The measured MDE ratios imply **ρ = 0.835 – 0.899**, close to the **0.8377** R836 borrowed and in the
direction it predicted. And every outcome matches the arithmetic **at R835's own 2× criterion**:

| pair | implied ρ | ρ needed at 2× | outcome |
|---|---|---|---|
| `gen` / `random_k12_s0` | 0.870 | > 0.719 | **SEPARABLE** ✓ |
| `generic` / `gen` | 0.899 | > 0.956 | not ✓ |
| `promptecho` / `topvar_k4_08b` | 0.835 | > 0.923 | not ✓ |

⚠ **R836's published ρ\* used the 1× criterion while R835's verdict used 2×**, so its table
**over-predicted** how many pairs flip. The derivation was right; the threshold it was evaluated at
did not match its parent round.

## ⛔ The bug the kill caught

v1 passed `SC.load_targets()` — a **2-tuple** `(targets, demographics)` — as `targets`, so
`p not in targets` tested membership in a 2-element tuple: **n = 0 for every pair**. I briefly blamed
R466's disjoint id spaces. **They are fine: |targets ∩ sat| = 968.** The kill returned **UNVERIFIED**
rather than publishing n=0, which is what it is for.

## NEXT

The per-prompt difference vectors are persisted in this artifact, so the remaining 42 adjacent pairs
of R835's ordering can be resolved by the same recomputation without re-deriving anything — and
R835's table can be replaced with measured MDEs rather than bounded ones.
