#!/usr/bin/env python3
"""R986 — the definition names a scalar size, and the released core does not have one.

⛔ WHY. R985 derived k from the object and found the two readings of clause ① — min per-prompt k > 1
and modal k > 1 — disagree on `gen`. Its NEXT said the question is about the STATEMENT's wording.
Read from the object, `DEFINITION.md:61`:

    > Its size, **under that same judge J**, is **greater than one**.
    > *(Reported, not required: sizes 3 to 8 are not distinguishable by this release.)*

**"Its size" is a scalar.** And **36 of 99 arms have no scalar size** — including `coval_core`, the
released core the whole definition was written from, whose per-prompt size runs **2 to 4**.

ESTIMAND        for each arm, the DECOMPOSITION of per-prompt size variation into
                  ① POOL CAPPING   — the prompt offers fewer criteria than the rule requests, so
                                     the realised size is min(k, pool). A property of the PROMPT.
                  ② ARM SELECTION  — the arm takes fewer than the pool allows. A property of the ARM.
                and the share of arms for which "its size" denotes a well-defined number at all.
IDENTIFICATION  exact. Both quantities are counts read from satisfaction matrices; the pool is
                `full`, the arm that uses every criterion available.
                ⚠ This is largely a DERIVATION once the matrices are read — the decomposition could
                not have come out otherwise. What could have come out otherwise, and is the
                measurement, is WHICH arms have a residual after pool capping is removed.
SCOPE           population : the 99 arms, 968 prompts
                instrument : distinct criterion indices per prompt; pool = `full`'s per-prompt count
                baseline   : min(nominal k, pool) — the size an arm would have if pool capping were
                             the whole story
                regime     : release one; nominal k taken as the modal per-prompt count
WORLDS          A POOL CAPPING EXPLAINS IT ALL   every arm's per-prompt size equals min(k, pool), so
                              the variation is a fact about prompts and "its size" can be read as
                              the rule's nominal k without loss.
                B THE ARMS ALSO VARY   at least one arm — and it matters whether it is `coval_core` —
                              selects fewer than the pool allows, so its size is genuinely a
                              distribution and no scalar reading is faithful.
                prediction matrix: A -> residual 0 for every arm. B -> a named set with residuals.
KILL            pre-registered, CONDITIONAL on the controls: residual 0 everywhere ⇒ world B dead
                and clause ① can be read as nominal k. Any residual ⇒ world A dead, and the arms
                must be NAMED with their residual counts.
POSITIVE CTRL   arms sharing a nominal k must share an IDENTICAL per-prompt profile if pool capping
                is the mechanism. Measured across the k12 and k8 families — if they differ, the
                pool explanation is wrong before any residual is computed.
NEGATIVE CTRL   `full` uses every available criterion, so its per-prompt size must EQUAL the pool
                exactly. A residual there would mean the pool proxy is not the pool.
PLACEBO         an arm whose nominal k is below every pool size — `topw_k1`, k=1 against a minimum
                pool of 4 — must show ZERO variation. If even that one varies, the reading is wrong.
NOISE FLOOR     none: these are counts, not estimates. Said rather than fabricated.
MULTIPLICITY    every arm classified; residual counts persisted for all with a non-zero one.
SEEDS           N/A — deterministic. Two runs required byte-identical.
ARTIFACT        results/size_decomposition.json with this file's source hash.
IMPOSSIBLE      construct validity — N/A: this establishes that "its size" is ambiguous, never which
                reading the clause SHOULD take. That is an authorial decision, not a measurement,
                and this round deliberately does not make it.
                cross-release — N/A: one release.
"""
from __future__ import annotations
import collections
import hashlib
import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat                                              # noqa: E402

A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"


def per_prompt(nm):
    f = RES / f"sat_{nm}.npz"
    if not f.exists():
        return None
    try:
        S = load_sat(f)
    except Exception:
        return None
    return {p: len({i for i, _ in S[p]}) for p in S}


def main() -> int:
    pool = per_prompt("full")
    if pool is None:
        print("  UNRUNNABLE: `full` (the pool proxy) is missing. Exit 2, never 0.")
        return 2
    arms = [x["arm"] for x in json.loads(
        next(A24.glob("R881_*/results/boundary_distance.json")).read_text())["arms"]]
    prof = {a: per_prompt(a) for a in arms}
    prof = {a: v for a, v in prof.items() if v}
    print(f"POPULATION  {len(prof)} arms × {len(pool)} prompts")
    print(f"  pool size runs {min(pool.values())}..{max(pool.values())}")

    # ⛔ THE POPULATION HAD TO BE CLASSIFIED FIRST, AND v1 DID NOT DO IT. Grouping by MODAL k put
    #    `full` and `full_sham` in a bogus "k=13 family" and the control failed 25 of 26 — on a pair
    #    that SHOULD differ, since a sham draws a different prompt's criteria. The three genuine
    #    families are identical 26 of 26.
    #    ⭐ The classifier is a property, not a name list: an arm draws from the PROMPT's pool iff
    #    its size never exceeds the pool. `genericpool16` carries 16 criteria where the pool is 4,
    #    so it draws from a fixed external pool and `min(k, pool)` is simply the wrong baseline for
    #    it. `full` equals the pool everywhere and has no nominal k at all.
    #    (Fifth time this session an object-level check caught a population I had assumed.)
    prompt_pool_arms = {a for a, v in prof.items() if all(v[q] <= pool[q] for q in v)}
    exhaustive = {a for a in prompt_pool_arms if all(prof[a][q] == pool[q] for q in prof[a])}
    external = set(prof) - prompt_pool_arms
    decomposable = prompt_pool_arms - exhaustive
    print(f"  CLASSIFIED  prompt-pool {len(prompt_pool_arms)} · of those pool-exhaustive "
          f"{len(exhaustive)} {sorted(exhaustive)} · external-pool {len(external)} "
          f"{sorted(external)}")
    print(f"  the decomposition applies to the {len(decomposable)} arms with a declared k drawing "
          f"from the prompt's pool")

    fams = collections.defaultdict(list)
    for a in decomposable:
        fams[collections.Counter(prof[a].values()).most_common(1)[0][0]].append(a)
    checked, ident = 0, 0
    for k, mem in sorted(fams.items()):
        if len(mem) < 2 or k <= 4:
            continue
        base = prof[mem[0]]
        same = [m for m in mem[1:] if prof[m] == base]
        checked += len(mem) - 1
        ident += len(same)
    pos_ok = checked > 0 and ident == checked
    print(f"\nPOSITIVE CONTROL  arms sharing a nominal k share an identical per-prompt profile: "
          f"{ident} of {checked} -> {'PASS' if pos_ok else '⛔ FAIL'}")

    neg_ok = prof.get("full") == pool
    p1 = prof.get("topw_k1")
    plac_ok = p1 is not None and len(set(p1.values())) == 1 and set(p1.values()) == {1}
    print(f"NEGATIVE CONTROL  `full` equals the pool exactly: {neg_ok}")
    print(f"PLACEBO           topw_k1 (nominal 1, min pool {min(pool.values())}) shows zero "
          f"variation: {plac_ok}")
    ctrl_ok = pos_ok and neg_ok and plac_ok

    # ── THE DECOMPOSITION
    rows = []
    for a in sorted(decomposable):
        v = prof[a]
        nominal = collections.Counter(v.values()).most_common(1)[0][0]
        capped = {p: min(nominal, pool[p]) for p in v}
        resid = [p for p in v if v[p] != capped[p]]
        rows.append({"arm": a, "nominal": nominal, "min": min(v.values()), "max": max(v.values()),
                     "variable": len(set(v.values())) > 1,
                     "explained_by_pool": len(v) - len(resid), "residual": len(resid),
                     "residual_share": len(resid) / len(v)})
    var = [r for r in rows if r["variable"]]
    with_resid = [r for r in rows if r["residual"] > 0]
    print(f"\nDECOMPOSITION  {len(var)} of {len(rows)} arms have a VARIABLE per-prompt size")
    print(f"  of those, pool capping explains it ENTIRELY for "
          f"{len(var) - len([r for r in var if r['residual']])} arms")
    print(f"  arms with a RESIDUAL (they select fewer than the pool allows): {len(with_resid)}")
    print(f"\n  {'arm':<24}{'nominal':>8}{'min':>5}{'max':>5}{'residual':>10}{'share':>9}")
    for r in sorted(with_resid, key=lambda r: -r["residual"])[:12]:
        print(f"  {r['arm']:<24}{r['nominal']:>8}{r['min']:>5}{r['max']:>5}"
              f"{r['residual']:>10}{r['residual_share']:>9.1%}")

    core = next((r for r in rows if r["arm"] == "coval_core"), None)
    if core is None:
        print("  ⛔ coval_core is not in the decomposable set — the round cannot answer its own "
              "question. Exit 2, never 0.")
        return 2
    print(f"\n  ⭐ coval_core — the released core: nominal {core['nominal']}, per-prompt size "
          f"{core['min']}..{core['max']}, residual {core['residual']} prompts "
          f"({core['residual_share']:.1%})")

    if not ctrl_ok:
        world = "UNVERIFIED — a control failed; the decomposition certifies nothing"
    elif not with_resid:
        world = ("A POOL CAPPING EXPLAINS IT ALL — every arm's size is min(k, pool), so the "
                 "variation is a fact about prompts and clause ① can read `size` as nominal k")
    else:
        world = (f"B THE ARMS ALSO VARY — {len(with_resid)} arm(s) select fewer than the pool "
                 f"allows, including coval_core on {core['residual']} prompts. `Its size` denotes "
                 f"a distribution, not a number, for the released core itself.")
    print(f"\n⭐ {world}")

    out = HERE / "results" / "size_decomposition.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head=subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                            text=True).stdout.strip()[:8],
        clause_text="Its size, under that same judge J, is greater than one.",
        n_arms=len(rows), n_prompts=len(pool),
        classified={"prompt_pool": len(prompt_pool_arms), "pool_exhaustive": sorted(exhaustive),
                    "external_pool": sorted(external), "decomposable": len(decomposable)},
        pool_min=min(pool.values()), pool_max=max(pool.values()),
        n_variable=len(var), n_with_residual=len(with_resid),
        controls={"positive_same_k_same_profile": [ident, checked, pos_ok],
                  "negative_full_equals_pool": neg_ok, "placebo_topw_k1_fixed": plac_ok,
                  "all_ok": ctrl_ok},
        coval_core=core, rows=rows, world=world,
        note="this establishes that `its size` is ambiguous between nominal k, realised per-prompt "
             "size, and arm selection. WHICH reading the clause should take is an authorial "
             "decision and is deliberately not made here.",
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
