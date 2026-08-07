# R498 · The auditor of auditors cannot run inside the suite — and the cycle it contains is not traversed

**Decision this makes safe:** whether `assurance/` needs restructuring to break a suspected
recursion between its two directory-globbing auditors. **It does not.** The recursion is real in the
discovery graph and is never traversed. The gate is unrunnable in the suite for a duller reason.

## What was measured

| | |
|---|---|
| suite timeout (read from `run_all.py`, not assumed) | **90 s** |
| `run_all` discovers | 43 gates — **including `audit_the_auditors`** |
| `audit_the_auditors` discovers | 51 gates — **including `run_all`** |
| `run_all` ever seen as a live child of the auditor | **never**, 2 reps × ~375 samples |
| `audit_the_auditors` wall-clock | **≥150 s** (killed at cap), spread **0.0 s**, both reps |
| a plain gate, same harness | **0.4 s** — the harness is not globally slow |

**Verdict: `CONFIRMED` that the auditor cannot complete inside the suite. `CONFIRMED` that the cycle
exists in the discovery graph. `UNVERIFIED` whether the cycle would be traversed at completion.**

## The kill fired, and it killed my own claim

Pre-registered: *"if zero nested `run_all` processes are ever observed, world C is dead and I
withdraw the cycle claim regardless of what the glob contains."* Zero were observed. **Three commands
earlier I had asserted "each auditor runs the other, bounded only by timeouts." That is withdrawn.**

## Why the verdict stops at UNVERIFIED rather than "inert"

A tempting next step reconstructs the auditor's sort order, finds `run_all` at index 42, notes the
probe reached index 45, and concludes the cycle was *reached and declined*. **That inference is not
admissible here.** The index mapping is a **re-implementation** of the auditor's ordering rule, and
the round's positive controls validate **set membership only** — nothing established that my order is
its order. And the arithmetic refuses to close: `run_all` runs 43 gates under a 120 s per-script
timeout, so 45 positions inside 150 s is impossible if it genuinely ran.

⭐ **So the honest state is three-valued, and the middle value is the finding.** *A search is an
instrument*; an order reconstruction is a second instrument, and it inherited a positive control
designed for the first.

## The recursive shape worth keeping

**The reason the cycle question cannot be sharpened is the finding itself.** `audit_the_auditors`
would have to run to completion to show whether it traverses the cycle, and the measured fact is that
it never runs to completion. **The gate whose entire job is catching gates that pass on empty
populations is the one gate the suite cannot run.**

## Controls

- **probe (i), discovery** — excise-nothing reproduces the base count; excising a present script drops
  it by exactly 1; excising an absent name changes nothing. **All PASS.**
- **probe (ii), process tree** — must see children known to exist: **saw 25 distinct gates**. Placebo
  (a nonexistent script name) returned 0. Sham (the same probe on a non-auditor gate) returned 0
  `run_all`. **All PASS.**
- **negative** — a plain gate alone runs in 0.4 s, so the overrun is not the harness or the machine.

## Killed before it ran

The first draft discriminated by **excision**, driven by a `COVAL_EXCISE` environment variable that
**nothing reads** — both arms would have been the identical run. Caught in review, replaced by direct
observation of the process tree. **A discriminator that cannot discriminate is the failure this
standard exists to catch, and it was one edit from being the whole design.**

## Found while building this, and worse than the finding

`audit_the_auditors.py:56` snapshots `assurance/` and afterwards `unlink()`s **every file not in the
snapshot**, treating "not in my snapshot" as "written by the gate under test". It actually means
"created since my snapshot, **by anyone**." While this round ran, it **deleted `residue_debt.py`
thirty seconds after that file was committed and pushed.** Recovered with `git checkout`. The gate's
own docstring says restoration "is verified" — true for files it knows about, silently destructive
for files it does not.
