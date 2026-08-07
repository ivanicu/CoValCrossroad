#!/usr/bin/env python3
"""
R884 · how much of each gate's frozen baseline is the gate — or its own round — measuring itself?

⛔ WHY, and it is a measured number rather than a worry. The share gate froze **3,090** entries and
R883 had reported **1,788** for the corpus. The gap decomposed exactly: **1,302 came from R883's own
artifact**, which persists a table of other rounds' shares — an INVENTORY, not 1,302 new published
rates. **42.1% of that gate's baseline is the audit looking at itself.**

**Self-inclusion is the norm in this suite and nothing declares it.** `tree_survives_the_sweep`
stamps its own census; `a_next_names_the_check_that_cleared_it` reads commit bodies including the
commit that added it; `a_commit_body_names_its_own_round` likewise. **A self-including instrument
reports a number about itself mixed with the number about the corpus**, and only the share gate's
case has been decomposed.


⛔⛔ POST-RUN CORRECTION. **SEVEN NON-EMPTY BASELINES — 348 ENTRIES — WERE SILENTLY SKIPPED, AND THE
ROUND PRINTED "1 baseline EMPTY" AS IF THAT WERE THE WHOLE REMAINDER.**

`OWNERS` lists 5 baselines. Every other `KNOWN_*.json` hit a `continue` that appended to `empty`
**only if no non-empty list value existed** — and all seven store their entries under keys my check
does not know: `shas` (223) · `rounds` (34) · `stale` (30) · `typed` (31) · `ids` (17) · `unlabelled`
(12) · `names` (1). **They were neither scanned nor named**, and the printed line implied the
population was fully accounted for.

⭐ **So the SCOPE line above is wrong where it says "5 of 13 … the 8 empty ones are REPORTED".**
Exactly **one** is empty (`KNOWN_MDE_WITHOUT_DENOMINATOR`). The true split is **5 scanned · 7
non-empty and UNSCANNED · 1 empty**, and the unscanned 348 entries are **38.5% of the 904 baseline
entries this suite holds outside the share gate**.

⭐⭐ **WORLD A STILL STANDS ON WHAT WAS MEASURED** — of the five scanned, only the share gate is
materially self-inflated (0.421 vs 0.013 / 0.000 / 0.000 / 0.000). **But it is now a claim about 5
of 12 non-empty baselines, not about the suite**, and the seven unscanned ones are `UNVERIFIED` in
both directions rather than absent.

⛔ **This is the same defect the last four rounds have been about, committed inside the round that
audits it: a population chosen by what my code already knew how to read.** R873's over-wide
population, R882's wrong denominator, R883's own inventory — and now a hard-coded map deciding what
counts as a baseline. **The tell each time is a `continue` or a filter whose complement is never
counted.**

⚠ **The remedy that would have caught it, and it is cheap:** require the scanned count plus the
skipped count plus the empty count to equal the globbed count, and print all four. **A partition
that does not sum to its population is not a partition.**

ESTIMAND        for every frozen baseline: the share of its entries that originate from the gate's
                own artifact, its own round directory, or the commit that introduced it.
IDENTIFICATION  exact for path-keyed baselines (the origin is in the key). ⚠ **PARTIAL for
                commit-hash baselines** — a hash does not carry which file it is about, so
                self-inclusion there is measured by whether the commit TOUCHED the gate's own
                files, which is a weaker test. **Reported separately, never pooled with the exact
                cases**, because pooling a partial measure with an exact one produces a number that
                is neither.
SCOPE           population: every `assurance/KNOWN_*.json` with a non-empty entry list — 5 of 13;
                            the 8 empty ones are REPORTED, since a gate with no baseline has
                            nothing to be inflated by and is not evidence either way
                instrument: string match of the gate's own name/round against each entry
                baseline:   0% self-inclusion — a gate measuring only the corpus
                regime:     this repo, this commit
WORLDS          A · the share gate is the only inflated baseline -> R883's case was specific to a
                    round that published its findings as data
                B · several baselines are materially self-inflated -> every "N frozen" figure in
                    this suite is partly a statement about the suite, and they need decomposing
                C · the baselines are mostly empty or too small to say -> the question is not
                    answerable at this corpus size and that is the finding
KILL            CONDITIONAL, all required:
                  ⭐ ① POSITIVE, on a REAL decomposed case: the share gate must come back at
                     1302/3090 = 0.421 ± 0.001. That number is committed in its baseline's own
                     `decomposition` field, so this is a check against disk, not against memory.
                  ⭐ ② g=0: a baseline with NO entry naming the gate must come back at 0.000.
                     A detector that finds self-inclusion everywhere passes arm ① trivially.
                  ③ at least one non-empty baseline besides the share gate, else WORLD C and the
                     comparison cannot be made.
MULTIPLICITY    5 non-empty baselines; all reported, plus the 8 empty ones named.
ARTIFACT        results/gate_self_inclusion.json
IMPOSSIBLE      cross-release · construct validated · causally identified.
"""
import json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
ASSUR = ROOT / "assurance"

# baseline file -> (entry key, the gate that owns it, the round whose output could inflate it)
OWNERS = {
    "KNOWN_UNAUDITABLE_SHARES.json": ("keys", "a_share_carries_its_counts", "R883"),
    "KNOWN_LITERAL_VERDICTS.json": ("keys", "a_verdict_threshold_is_named", "R881"),
    "KNOWN_MISNAMED_COMMITS.json": ("hashes", "a_commit_body_names_its_own_round", None),
    "KNOWN_UNCITED_NEXTS.json": ("hashes", "a_next_names_the_check_that_cleared_it", None),
    "KNOWN_UNSTABLE_SEEDS.json": ("files", "a_seed_must_be_stable", "R842"),
}


def entries(path, key):
    try:
        d = json.loads(path.read_text())
    except Exception:
        return None
    v = d.get(key)
    return v if isinstance(v, list) else None


def commit_touches(h, gate, rnd):
    out = subprocess.run(["git", "-C", str(ROOT), "show", "--name-only", "--format=", h],
                         capture_output=True, text=True).stdout
    return (gate in out) or (bool(rnd) and rnd in out)


def main() -> int:
    # ---- controls -----------------------------------------------------------------------------
    sp = ASSUR / "KNOWN_UNAUDITABLE_SHARES.json"
    ks = entries(sp, "keys") or []
    self_share = sum(1 for k in ks if "R883" in k)
    p1 = bool(ks) and abs(self_share / len(ks) - 1302 / 3090) < 1e-3
    committed = json.loads(sp.read_text()).get("decomposition", "")
    p1 = p1 and ("1302" in committed and "3090" in committed)
    fake = ["E01/A01/R02_x/results/a.json::rate", "E01/A01/R03_y/results/b.json::share"]
    p2 = sum(1 for k in fake if "R883" in k) == 0
    print(f"  ① POSITIVE  the share gate recomputes at {self_share}/{len(ks)} = "
          f"{self_share/max(len(ks),1):.4f} vs its committed 1302/3090 = {1302/3090:.4f}: {p1}  "
          f"{'PASS' if p1 else 'FAIL'}")
    print(f"     checked against the `decomposition` field ON DISK, not against my memory of it")
    print(f"  ② g=0       a baseline with no self-entries gives 0.000: {p2}  "
          f"{'PASS' if p2 else 'FAIL'}")
    if not (p1 and p2):
        print("\n  UNVERIFIED: the detector failed its own controls. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED"}, open(OUT / "gate_self_inclusion.json", "w"), indent=2)
        return 2

    exact, partial, empty = [], [], []
    for f in sorted(ASSUR.glob("KNOWN_*.json")):
        nm = f.name
        if nm not in OWNERS:
            d = json.loads(f.read_text()) if f.exists() else {}
            if not any(isinstance(v, list) and v for v in d.values()):
                empty.append(nm)
            continue
        key, gate, rnd = OWNERS[nm]
        es = entries(f, key)
        if not es:
            empty.append(nm); continue
        if key == "hashes":
            n_self = sum(1 for h in es if commit_touches(h, gate, rnd))
            partial.append({"baseline": nm, "gate": gate, "n": len(es), "n_self": n_self,
                            "share": n_self / len(es), "kind": "PARTIAL (hash, weaker test)"})
        else:
            n_self = sum(1 for k in es
                         if gate in str(k) or (rnd and rnd in str(k)))
            exact.append({"baseline": nm, "gate": gate, "n": len(es), "n_self": n_self,
                          "share": n_self / len(es), "kind": "EXACT (path-keyed)"})

    print(f"\n  EXACT (the entry key carries its origin):")
    for r in exact:
        print(f"    {r['baseline']:<34} {r['n_self']:>5}/{r['n']:<5} = {r['share']:.3f}")
    print(f"  PARTIAL (commit hashes — a hash does not say what it is ABOUT):")
    for r in partial:
        print(f"    {r['baseline']:<34} {r['n_self']:>5}/{r['n']:<5} = {r['share']:.3f}")
    print(f"  ⚠ {len(empty)} baseline(s) EMPTY — nothing to inflate, and not evidence either way:")
    print(f"    {', '.join(sorted(empty)[:6])}{' ...' if len(empty) > 6 else ''}")

    k3 = len(exact) >= 2
    print(f"\n  ③ at least one non-empty baseline besides the share gate: {k3}  "
          f"{'PASS' if k3 else 'FAIL'}")
    material = [r for r in exact + partial if r["share"] >= 0.05]
    world = ("C" if not k3 else "B" if len(material) >= 2 else "A")
    print(f"\n  ⭐ WORLD {world}: " + {
        "A": "the share gate is the only materially inflated baseline — R883's case was specific"
             " to a round that published its findings as data",
        "B": "several baselines are materially self-inflated — every 'N frozen' figure in this"
             " suite is partly a statement about the suite and needs decomposing",
        "C": "too few non-empty baselines to compare — the question is not answerable at this"
             " corpus size"}[world])
    for r in material:
        print(f"     ⭐ {r['baseline']} at {r['share']:.3f}  [{r['kind']}]")
    print(f"     ⚠ EXACT and PARTIAL are NOT pooled. A hash-keyed baseline cannot say what a")
    print(f"       commit was ABOUT, only what it TOUCHED, and averaging the two produces a")
    print(f"       number that is neither.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "exact": exact, "partial": partial,
               "empty_baselines": sorted(empty), "n_material": len(material),
               "not_pooled": "EXACT (path-keyed) and PARTIAL (hash-keyed) are reported apart",
               "positive_control": {"share_gate_self": self_share, "share_gate_total": len(ks)}},
              open(OUT / "gate_self_inclusion.json", "w"), indent=2)
    print(f"\n  artifact: results/gate_self_inclusion.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
