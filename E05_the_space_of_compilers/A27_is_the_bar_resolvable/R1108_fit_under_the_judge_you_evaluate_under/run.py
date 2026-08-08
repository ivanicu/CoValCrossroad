#!/usr/bin/env python3
"""R1108 — is the definition JUDGE-dependent or FITTING-PROTOCOL-dependent? Refit and recount.

R1105 measured the admitted set at **9 under the 2B judge and 0 under the 8B**, on the same 43 arms —
and computed the 8B side **entirely from `_08b` arms**, i.e. criteria selected under the 2B judge and
merely RE-SCORED by the 8B one. R1107 then found that under `_08bR` — the rule RE-RUN under 8B —
`greedy`'s deficit against `indep` **reverses sign at 4 of 4 doses**.

⛔ SO R1105's `0` MAY BE AN ARTIFACT OF EVALUATING ARMS FITTED FOR THE OTHER JUDGE, and the two
readings carry different repairs:
  · judge-dependent            -> the definition does not survive a change of instrument. Abandon it.
  · fitting-protocol-dependent -> it survives if every candidate is fitted under the judge it is
                                  evaluated under. The repair is a PROTOCOL CLAUSE, not abandonment.
No round has computed the second, and the files to do it cost 0 judge calls.

⭐ AND THE SPECIFICATION IS COHERENT FOR ARMS THAT FIT NOTHING, which is why this is one world and
not a mixture. `select_core.py`'s own help states the two specifications COINCIDE EXACTLY for the
satisfaction-blind rules (`random_k`, `topw_k`, `topabs_k`, `full`); `coval_core`, `gen`, `promptecho`
and the two comparators are fixed criterion texts, so re-running is re-scoring for them too. **That
identity is asserted as a PLACEBO below, byte-for-byte, rather than assumed.**

ESTIMAND        the ②′ admitted set under the 8B judge when every REBUILDABLE candidate is re-run
                under the 8B satisfaction (`_08bR`), on R1105's 43-arm population — and the same set
                after clause ③'s leakage exclusion, because arms that come back by REFITTING TO THE
                TARGET are exactly the ones ③ removes.
IDENTIFICATION  identified for the 32 arms `select_core.py` can regenerate. The 11 it cannot
                (`coval_core`, `gen`, `promptecho`, the shams, the comparators) fit nothing, so
                re-running IS re-scoring and their `_08b`/`sat08_` file is the correct cell — stated,
                and checked for the rules where the identity is provable.
UNIT OF THE     an arm and its ②′ membership under a named (judge, fitting-protocol) pair.
  INSTRUMENT
UNIT OF THE     the same. ⚠ NOT R1105's unit, which was (arm, judge) with the protocol held at
  CLAIM         `re-scored`. The protocol is the axis this round adds, and the two are named
                separately so R1105's `0` is not quoted as this round's baseline without it.
SCOPE           population: R1105's 43 arms. instrument: R1055's operator, analytic inner bound
                (validated against its 4000-draw bootstrap). baseline: R1105's two sets, 9 and 0.
                regime: 968 prompts, target A2, comparators from the judge under test.
WORLDS          A JUDGE-DEPENDENT            the refit set is still below R978's band of 4. Then
                                 R1105's conclusion stands unchanged and the instrument, not the
                                 protocol, is what the definition cannot survive.
                B PROTOCOL-DEPENDENT         the refit set is >= 4. Then R1105's `0` is an artifact
                                 of evaluating arms fitted for the other judge, and the repair is a
                                 clause requiring the candidate to be fitted under the evaluating
                                 judge.
                Prediction matrix on (|refit admitted|, |refit admitted after clause ③|):
                  A -> (< 4, < 4)     B -> (>= 4, and the ③ column decides whether it is LEGITIMATE)
KILL            pre-registered. World A is KILLED if the refit admitted set has >= 4 members. ⚠ AND
                THE SECOND COLUMN IS PRE-REGISTERED TOO, because a recovery made entirely of leaky
                arms is not a recovery of the definition: if every returning arm is in R1094's
                leakage list, world B is TECHNICALLY true and PRACTICALLY empty, and the verdict must
                say so rather than report the larger number. Gated:
                                    if positive_2B_matches_R1105 and placebo_identity_holds
                                       and rebuild_exact: evaluate(|refit|)
                                    else:                 UNVERIFIED
POSITIVE CTRL   the 2B world must reproduce R1105's committed 9-arm set BY NAME on this population.
REBUILD CTRL    rebuilding `greedy_k4_fit1_08b` and `indep_k4_fit1_08b` must reproduce the COMMITTED
                npz byte-for-byte (`meta` and `sat` both `array_equal`), as R1107 established.
PLACEBO         ⭐ THE PROVABLE IDENTITY. For every satisfaction-blind rule the `_08b` and `_08bR`
                files must be BYTE-IDENTICAL — `select_core.py` says so and this checks it. If they
                differ, the two specifications are not what the release documents and every cell in
                R1105, R1106 and R1107 built on that distinction needs re-reading.
NEGATIVE CTRL   the refit world must DIFFER from the re-scored world on at least the fitted rules —
                otherwise `refitting` did nothing and the round is comparing a set with itself.
NOISE FLOOR     R1103's sampling interval on the admitted set, [17, 26] at the full 99-arm
                population, is reported beside this gauge and never subtracted from it.
MULTIPLICITY    43 arms x 3 worlds (2B, 8B re-scored, 8B re-run), every membership reported.
SPECIFICATION   world x clause {②′ alone, ②′ ∧ ③ leakage}. Both columns published whole.
SEEDS           the analytic bound is deterministic; the bootstrap validation uses one fixed seed.
ARTIFACT        results/refit_admitted.json with the source hash.
REPRODUCIBILITY deterministic.
IMPOSSIBLE      | criterion | what it would require |
                | a refit cell for `coval_core`, `gen`, `promptecho`, the shams | a generator; they
                  are fixed criterion texts and re-running is re-scoring for them |
                | whether either judge is CORRECT | an external gold standard |
                | cross-release | a second release |
"""
from __future__ import annotations

import hashlib, json, pathlib, re, subprocess, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"
A27 = ROOT / "E05_the_space_of_compilers" / "A27_is_the_bar_resolvable"
PY = str(ROOT / ".venv" / "bin" / "python")
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls  # noqa: E402

OUT = HERE / "results" / "refit_admitted.json"
WORK = pathlib.Path("/tmp/claude-1000/-home-ivan/7d277876-c2fd-4a27-9b05-652b391121ff/scratchpad/r1108_arms")
COMP, Z, NBOOT, BAND = ["generic", "genericpool16"], 1.959963984540054, 4000, 4
BLIND_RULES = ("random_k", "topw_k", "topabs_k", "full")   # spec `_08b` == `_08bR` by construction

TAG = re.compile(r"^(?P<rule>full|topw_k|topabs_k|topvar_k|topwvar_k|random_k|oracle_k|indep_k|"
                 r"greedy_k)(?P<k>\d+)?(?:_s(?P<seed>\d+))?(?:_fit(?P<fit>\d+))?$")


def parse(tag):
    m = TAG.match(tag)
    if not m:
        return None
    d = m.groupdict()
    return {"rule": d["rule"], "k": int(d["k"]) if d["k"] else 4,
            "seed": int(d["seed"]) if d["seed"] else 0,
            "fit": int(d["fit"]) if d["fit"] else -1}


def build(spec, rule, k, seed, fit, suffix):
    cmd = [PY, str(ROOT / "corebench" / "select_core.py"), "--rule", rule,
           "--outdir", str(WORK), "--seed", str(seed)]
    if rule != "full":
        cmd += ["--k", str(k)]
    if fit >= 0:
        cmd += ["--fit-parity", str(fit)]
    if spec == "08b":
        cmd += ["--full-npz", str(RES / "sat08_full.npz"),
                "--select-npz", str(RES / "sat_full.npz"), "--tag-suffix", suffix]
    elif spec == "08bR":
        cmd += ["--full-npz", str(RES / "sat08_full.npz"), "--tag-suffix", suffix]
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT), timeout=3600)
    return p.returncode == 0


def main() -> int:
    f05 = next(A27.glob("R1105_*/results/second_judge.json"), None)
    f94 = next(A27.glob("R1094_*/results/two_readings.json"), None)
    f03 = next(A27.glob("R1103_*/results/set_stability.json"), None)
    if f05 is None or f94 is None or f03 is None:
        print("  UNRUNNABLE: a prior artifact is absent. Exit 2, never 0."); return 2
    s05 = json.loads(f05.read_text())
    common = s05["population"]["common"]
    a2_ref = set(s05["sets"]["admitted_2B"])
    leak = set(json.loads(f94.read_text())["readings"]["leakage_excludes"])
    samp = json.loads(f03.read_text())["set_size"]
    WORK.mkdir(parents=True, exist_ok=True)

    tg, _ = load_targets()
    base = load_sat(RES / "sat_generic.npz")
    pids = sorted(set(base) & {p for p in tg if len(tg[p]) >= 2})
    H = {p: [np.array(cls(np.array(t[0], float)), float) for t in tg[p]] for p in pids}
    n = len(pids)

    def perprompt(path):
        Sa = load_sat(path)
        v = np.full(n, np.nan)
        for i, p in enumerate(pids):
            if p in Sa:
                c = np.array(cls(yvec(Sa[p], sorted({j for j, _ in Sa[p]}))), float)
                v[i] = float(np.mean([(c == h).mean() for h in H[p]]))
        return v

    # ---- build the refit world for every rebuildable arm
    rebuildable, notrebuildable, blind_pairs = {}, [], {}
    for a in common:
        spec = parse(a)
        if spec is None:
            notrebuildable.append(a); continue
        okR = build("08bR", spec["rule"], spec["k"], spec["seed"], spec["fit"], "_R8")
        okB = build("08b", spec["rule"], spec["k"], spec["seed"], spec["fit"], "_B8")
        if okR and okB:
            rebuildable[a] = spec
            if spec["rule"] in BLIND_RULES:
                blind_pairs[a] = spec
        else:
            notrebuildable.append(a)
    print(f"  rebuildable {len(rebuildable)} · not rebuildable {len(notrebuildable)} "
          f"{notrebuildable}")

    def emitted(a, suffix):
        spec = rebuildable[a]
        tag = spec["rule"] + ("" if spec["rule"] == "full" else str(spec["k"]))
        if spec["rule"] == "random_k":
            tag += f"_s{spec['seed']}"
        if spec["fit"] >= 0:
            tag += f"_fit{spec['fit']}"
        return WORK / f"sat_{tag}{suffix}.npz"

    # ---- PLACEBO: the provable identity, checked byte-for-byte
    ident_fail = []
    for a in blind_pairs:
        fb, fr = emitted(a, "_B8"), emitted(a, "_R8")
        if not (fb.exists() and fr.exists()):
            ident_fail.append((a, "missing")); continue
        b, r = np.load(fb, allow_pickle=True), np.load(fr, allow_pickle=True)
        if not (np.array_equal(b["meta"], r["meta"]) and np.array_equal(b["sat"], r["sat"])):
            ident_fail.append((a, "differs"))
    placebo_identity = not ident_fail
    print(f"  PLACEBO `_08b` == `_08bR` for the {len(blind_pairs)} satisfaction-blind arms: "
          f"{placebo_identity} {ident_fail if ident_fail else ''}")

    # ---- REBUILD control against two committed cells
    rb = {}
    for a in ("greedy_k4_fit1", "indep_k4_fit1"):
        f = emitted(a, "_B8") if a in rebuildable else None
        c = RES / f"sat_{a}_08b.npz"
        rb[a] = bool(f and f.exists() and c.exists()
                     and np.array_equal(np.load(c, allow_pickle=True)["meta"],
                                        np.load(f, allow_pickle=True)["meta"])
                     and np.array_equal(np.load(c, allow_pickle=True)["sat"],
                                        np.load(f, allow_pickle=True)["sat"]))
    rebuild_exact = all(rb.values())
    print(f"  REBUILD reproduces committed `_08b` cells: {rb}")

    # ---- the three worlds
    def world(kind):
        V, C = {}, {}
        for a in common:
            if kind == "2B":
                p = RES / f"sat_{a}.npz"
            elif a in rebuildable:
                p = emitted(a, "_B8" if kind == "8B_rescored" else "_R8")
            else:
                p = RES / f"sat_{a}_08b.npz"
                if not p.exists():
                    p = RES / f"sat08_{a}.npz"
            if not p.exists():
                continue
            v = perprompt(p)
            cov = np.isfinite(v)
            if cov.sum() < 100:
                continue
            V[a], C[a] = np.nan_to_num(v, nan=0.0), cov
        return V, C

    def lo_ana(d):
        m = len(d)
        return float(d.mean() - Z * d.std(ddof=1) / np.sqrt(m)) if m > 1 else 0.0

    def lo_boot(d, seed=11):
        rng = np.random.default_rng(seed); m = len(d)
        return float(np.percentile(d[rng.integers(0, m, size=(NBOOT, m))].mean(axis=1), 2.5))

    def admit(V, C, inner="analytic"):
        out = set()
        for a in V:
            if a in COMP:
                continue
            beats = 0
            for c in COMP:
                if c not in V:
                    continue
                m = C[a] & C[c]
                d = (V[a] - V[c])[m]
                if len(d) < 30:
                    continue
                if (lo_boot(d) if inner == "boot" else lo_ana(d)) > 0:
                    beats += 1
            if beats >= len(COMP):
                out.add(a)
        return out

    sets = {}
    for kind in ("2B", "8B_rescored", "8B_refit"):
        V, C = world(kind)
        sets[kind] = admit(V, C)
        print(f"  {kind:<14} admitted {len(sets[kind]):>2}  {sorted(sets[kind])}")
        if kind == "2B":
            positive = sets[kind] == a2_ref
            instrument_ok = admit(V, C, "boot") == sets[kind]

    refit, rescored = sets["8B_refit"], sets["8B_rescored"]
    negative_differs = refit != rescored
    refit_after3 = sorted(refit - leak)
    rescored_after3 = sorted(rescored - leak)

    gate_open = positive and placebo_identity and rebuild_exact and instrument_ok
    world_A_killed = (len(refit) >= BAND) if gate_open else None
    legitimate = len(refit_after3) >= BAND if gate_open else None

    payload = {
        "round": "R1108",
        "question": "is the definition judge-dependent or fitting-protocol-dependent?",
        "population": {"common": len(common), "rebuildable": sorted(rebuildable),
                       "not_rebuildable": notrebuildable,
                       "why_not_rebuildable": ("fixed criterion texts — `select_core.py` does not "
                                               "produce them and re-running IS re-scoring for an arm "
                                               "that fits nothing")},
        "sets": {k: sorted(v) for k, v in sets.items()},
        "sizes": {k: len(v) for k, v in sets.items()},
        "R1105_committed": {"2B": len(a2_ref), "8B_rescored": s05["sets"]["n_8B"]},
        "clause3_leakage": {
            "refit_after_leakage_exclusion": refit_after3,
            "n_refit_after_leakage": len(refit_after3),
            "rescored_after_leakage_exclusion": rescored_after3,
            "why": ("arms that return by REFITTING TO THE TARGET are exactly the ones clause ③ "
                    "removes, so a recovery made only of leaky arms is technically world B and "
                    "practically empty"),
        },
        "controls": {
            "POSITIVE the 2B world reproduces R1105's committed 9-arm set by name": bool(positive),
            "PLACEBO `_08b` == `_08bR` byte-for-byte on every satisfaction-blind arm":
                bool(placebo_identity),
            "REBUILD two committed `_08b` cells are reproduced byte-for-byte": bool(rebuild_exact),
            "INSTRUMENT the analytic inner bound equals the 4000-draw bootstrap on the 2B world":
                bool(instrument_ok),
            "NEGATIVE the refit world differs from the re-scored world": bool(negative_differs),
        },
        "kill": {"gate_open": gate_open, "world_A_killed": world_A_killed,
                 "threshold": BAND, "observed_refit": len(refit),
                 "observed_refit_after_clause3": len(refit_after3),
                 "recovery_is_legitimate": legitimate},
        "yardsticks": {"R978_band": BAND,
                       "R1103_sampling_interval_on_size": [samp["p2.5"], samp["p97.5"]],
                       "note": "sampling and instrument are separate axes and are never subtracted"},
        "source_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
    }
    if not gate_open:
        payload["verdict"] = ("⚠ UNVERIFIED — a control is red. "
                              f"Controls: {json.dumps(payload['controls'])}")
    else:
        payload["verdict"] = (
            f"{'⛔ WORLD A IS KILLED' if world_A_killed else '⭐ WORLD A SURVIVES'}: refitting every "
            f"rebuildable candidate under the judge it is evaluated under gives an admitted set of "
            f"{len(refit)} against R1105's {s05['sets']['n_8B']} re-scored and {len(a2_ref)} under "
            f"the 2B judge, threshold {BAND}. "
            + (f"⛔ BUT AFTER CLAUSE ③'s LEAKAGE EXCLUSION IT IS {len(refit_after3)} "
               f"({refit_after3}), so the recovery is "
               + ("LEGITIMATE — arms that do not consume the target come back."
                  if legitimate else
                  "MADE OF ARMS THE DEFINITION ALREADY EXCLUDES: refitting recovers admission by "
                  "fitting harder to the target, which is the one thing ③ forbids.")
               if world_A_killed else
               "So the definition is JUDGE-dependent, not merely protocol-dependent, and R1105's "
               "conclusion stands unchanged."))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=1, sort_keys=True))
    print()
    for k, v in payload["controls"].items():
        print(f"  [{'PASS' if v else 'FAIL'}] {k}")
    print()
    print(f"  after clause ③ — refit {len(refit_after3)} {refit_after3} · "
          f"rescored {len(rescored_after3)} {rescored_after3}")
    print()
    print(" ", payload["verdict"])
    return 0 if gate_open else 2


if __name__ == "__main__":
    sys.exit(main())
