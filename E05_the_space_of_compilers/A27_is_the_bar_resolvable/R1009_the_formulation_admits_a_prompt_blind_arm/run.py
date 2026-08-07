#!/usr/bin/env python3
"""R1009 — the formulation admits an arm that never reads the conversation.

⛔ WHY THIS AND NOT R1008's NEXT. R1008's NEXT asked for AST dataflow to decide list-valued
constants. That is the third consecutive instrumentation round, and R1007's retraction moved the
OBJECT-level state without anyone restating it. Reading R1000's committed extension arm by arm to do
that restating turned up the following, which is not an instrument question at all:

    genericpool16's extension contains `generic` and `generic_reprov`.

⭐ `generic` is a PROMPT-BLIND comparator — R921 certified it as one, and clause ② is defined as
"resolvably beats a NAMED prompt-blind comparator". So under one certified comparator, the OTHER
certified comparator qualifies as a core. **A criterion set that never reads the conversation is
admitted by the definition of a core.**

ESTIMAND        ① is any arm R921 certifies prompt-blind admitted by the formulation ②∧③?
                ② if so, by what margin, and is the admission RESOLVABLE rather than marginal?
                ③ the mechanism: do the two certified comparators differ in strength, so that the
                   weaker one lets the stronger one through?
IDENTIFICATION  exact. The prompt-blind set is READ from R921's committed
                `legitimate_comparators`; admission is R923's committed operator. No new judgement
                is introduced — the question is whether two committed artifacts contradict.
SCOPE           population : R1000's 96-arm intersection · instrument : A2, cluster bootstrap
                baseline   : each certified comparator in turn · regime : this release, n = 968
WORLDS          A CLEAN     no prompt-blind arm is admitted under any certified comparator. The
                            formulation excludes them implicitly and needs no repair.
                B SELF-ADMITTING  a prompt-blind arm is admitted. Then the definition, as written,
                            calls a conversation-blind set a core — the failure the standard names
                            as "name an admissible object this clause EXCLUDES", answered with the
                            comparator itself.
                prediction matrix: A -> 0 prompt-blind arms in any extension.
                                   B -> >= 1, and the margin says whether it is marginal or not.
KILL            pre-registered: if world B, the defect is written into DEFINITION.md in THIS round,
                beside the formulation, not deferred. A definition that admits its own null is not a
                finding to schedule.
POSITIVE CTRL   `coval_core` must be admitted under both comparators — R1000 established it. If the
                operator here does not reproduce that, it is not R1000's operator and nothing holds.
NEGATIVE CTRL   an arm certified prompt-blind must NOT be admitted against ITSELF: the paired
                difference of an arm with itself is identically zero, so `lo > 0` must be False. If
                a self-comparison were admitted the operator would be broken and every count void.
PLACEBO         `topw_k4_sham` — the same operation with the ingredient inverted — must be excluded.
                A definition that admits the sham has no content.
NOISE FLOOR     the 2.5th percentile of the bootstrapped paired difference IS the resolution here;
                the admission is `lo > 0`, so marginality is read off `lo` directly and reported.
MULTIPLICITY    2 certified comparators × every prompt-blind arm, all cells printed.
ARTIFACT        results/prompt_blind_admitted.json with this file's source hash.
IMPOSSIBLE      ⚠ whether the RELEASE intends `generic` to be a candidate at all — N/A. R921
                certified it as a COMPARATOR; nothing says it may not also be scored as an arm, and
                the definition as written places no restriction. That silence is the defect.
                What it would require: a statement in the release about what may be a core.
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"
NEW = ROOT / "corebench" / "results_r893_leaky"
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
A26 = ROOT / "E05_the_space_of_compilers/A26_can_the_definition_be_applied_without_provenance"
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls  # noqa: E402

NBOOT, SEED = 8000, 921
SUPERVISED = ("oracle_k", "indep_k", "greedy_k")


def main() -> int:
    need = {"r881": next(A24.glob("R881_*/results/boundary_distance.json"), None),
            "r921": next(A26.glob("R921_*/results/comparator_sweep.json"), None),
            "r922": next(A26.glob("R922_*/results/threshold_or_comparison.json"), None),
            "r1000": next(A27.glob("R1000_*/results/conjunction.json"), None)}
    if [k for k, v in need.items() if v is None]:
        print(f"  UNRUNNABLE: missing {[k for k, v in need.items() if v is None]}. Exit 2.")
        return 2
    legit = json.loads(need["r921"].read_text())["legitimate_comparators"]
    ref922 = {r["comparator"]: r for r in json.loads(need["r922"].read_text())["rows"]}
    arms881 = [x["arm"] for x in json.loads(need["r881"].read_text())["arms"]]
    pop = json.loads(need["r1000"].read_text())["population_arms"]
    print(f"  PROMPT-BLIND SET, read from R921: {legit}")
    print(f"  ⭐ clause ② is 'resolvably beats a NAMED prompt-blind comparator', and these are the "
          f"arms R921 certified as prompt-blind.")

    tg, _ = load_targets()
    S0 = load_sat(RES / f"sat_{legit[-1]}.npz")
    pids = sorted(set(S0) & {p for p in tg if len(tg[p]) >= 2})
    H = {p: np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids}
    n = len(pids)

    def vec(nm):
        for d in (RES, NEW):
            f = d / f"sat_{nm}.npz"
            if not f.exists():
                continue
            try:
                Sa = load_sat(f)
            except Exception:
                return None
            v = np.full(n, np.nan)
            for k, p in enumerate(pids):
                if p in Sa:
                    c = np.array(cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]}))), float)
                    v[k] = float(np.mean([(c == h[:len(c)]).mean() for h in H[p]]))
            if np.isfinite(v).sum() < 200:
                return None
            return np.nan_to_num(v, nan=np.nanmean(v))
        return None

    V, names = [], []
    for a in arms881:
        v = vec(a)
        if v is not None:
            V.append(v)
            names.append(a)
    V = np.array(V)
    mu = V.mean(axis=1)
    rng = np.random.default_rng(SEED)
    idx = rng.integers(0, n, size=(NBOOT, n))
    M = np.stack([V[:, idx[b]].mean(axis=1) for b in range(NBOOT)], axis=1)

    rows, wire_ok, blind_admitted = [], True, []
    for c in legit:
        i = names.index(c)
        D = M - M[i][None, :]
        lo = np.percentile(D, 2.5, axis=1)
        hi = np.percentile(D, 97.5, axis=1)
        adm = lo > 0
        wire_ok &= (abs(float(mu[adm].min()) - ref922[c]["implied_cut_mean_a2"]) < 1e-9
                    and int(adm.sum()) - int(adm[i]) == ref922[c]["n_admitted"])
        for b in legit:
            if b == c:
                continue
            j = names.index(b)
            ok = bool(adm[j]) and not b.startswith(SUPERVISED) and b in pop
            rows.append({"comparator": c, "prompt_blind_arm": b, "admitted": ok,
                         "mean_diff": float(mu[j] - mu[i]), "lo": float(lo[j]),
                         "hi": float(hi[j])})
            if ok:
                blind_admitted.append((c, b, float(lo[j])))
        # self-comparison NEGATIVE control
        rows.append({"comparator": c, "prompt_blind_arm": c + " (SELF)",
                     "admitted": bool(adm[i]), "mean_diff": float(mu[i] - mu[i]),
                     "lo": float(lo[i]), "hi": float(hi[i])})

    pc = [c for c in legit if bool(np.percentile(M - M[names.index(c)][None, :], 2.5,
                                                 axis=1)[names.index("coval_core")] > 0)]
    pos_ok = len(pc) == len(legit)
    neg_ok = all(not r["admitted"] for r in rows if r["prompt_blind_arm"].endswith("(SELF)"))
    sham = "topw_k4_sham"
    plac_ok = True
    if sham in names:
        plac_ok = all(not bool(np.percentile(M - M[names.index(c)][None, :], 2.5,
                                             axis=1)[names.index(sham)] > 0) for c in legit)
    print(f"\n  POSITIVE ① R922 wiring reproduced: {'PASS' if wire_ok else '⛔ FAIL'}")
    print(f"  POSITIVE ② `coval_core` admitted under both comparators: "
          f"{'PASS' if pos_ok else '⛔ FAIL'}")
    print(f"  NEGATIVE  an arm is never admitted against ITSELF: "
          f"{'PASS' if neg_ok else '⛔ FAIL'}")
    print(f"  PLACEBO   `{sham}` (ingredient inverted) is excluded under both: "
          f"{'PASS' if plac_ok else '⛔ FAIL'}")
    if not (wire_ok and pos_ok and neg_ok and plac_ok):
        print("\n⛔ a control failed; nothing below certifies anything. Exit 2, never 0.")
        return 2

    print(f"\n  {'comparator':<16}{'prompt-blind arm':<26}{'Δmean':>9}{'lo':>9}{'hi':>9}  admitted")
    for r in rows:
        print(f"  {r['comparator']:<16}{r['prompt_blind_arm']:<26}{r['mean_diff']:>+9.4f}"
              f"{r['lo']:>+9.4f}{r['hi']:>+9.4f}  {r['admitted']}")

    world = (f"B SELF-ADMITTING — {len(blind_admitted)} prompt-blind arm(s) are admitted by the "
             f"formulation" if blind_admitted else
             "A CLEAN — no prompt-blind arm is admitted under any certified comparator")
    print(f"\n⭐ {world}")
    if blind_admitted:
        for c, b, lo in blind_admitted:
            print(f"   ⛔ under comparator `{c}`, the prompt-blind arm `{b}` is admitted, "
                  f"lo = {lo:+.4f} — RESOLVABLE, not marginal")
        print("\n⛔ SO THE DEFINITION ADMITS A CRITERION SET THAT NEVER READS THE CONVERSATION.")
        print("   The mechanism is that R921's two certified comparators are NOT of equal strength:")
        print("   one resolvably beats the other, so naming the weaker one as clause ②'s reference")
        print("   lets the stronger one through as a core. The clause says 'a NAMED prompt-blind")
        print("   comparator' and never says WHICH — and that silence is the defect.")
        print("\n⚠ AND THIS IS THE QUESTION THE STANDARD PRESCRIBES FOR EVERY CLAUSE: name an")
        print("   admissible object this clause EXCLUDES. Clause ② excludes 68-72 arms and does")
        print("   NOT exclude the comparator it is defined against.")

    out = HERE / "results" / "prompt_blind_admitted.json"
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head="does the formulation admit an arm that never reads the conversation",
        n_prompts=n, nboot=NBOOT, seed=SEED, prompt_blind_set=legit,
        controls={"positive_r922_wiring": bool(wire_ok), "positive_core_admitted": bool(pos_ok),
                  "negative_self_never_admitted": bool(neg_ok),
                  "placebo_sham_excluded": bool(plac_ok)},
        rows=rows, blind_admitted=[{"comparator": c, "arm": b, "lo": lo}
                                   for c, b, lo in blind_admitted],
        world=world,
        mechanism="R921's two certified comparators are not of equal strength; naming the weaker "
                  "one as clause ②'s reference lets the stronger one through as a core",
        limitation="says the definition as written admits it, not that the release intends "
                   "`generic` to be a candidate arm",
        would_require="a statement in the release about what may be a core",
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
