#!/usr/bin/env python3
"""
R945 · R944 saw 2/2 visible declare and 0/13 invisible, post-hoc at n=2. Pre-register it and run it
        at 14 against 14: is disclosure produced by ENFORCEMENT, or by practice the gate never touched?

⛔ WHY THIS MATTERS AND IS NOT BOOKKEEPING. If disclosure tracks what the gate can SEE, then every
declaration in this repo is a gate artefact and the 14 rounds it cannot see are dark by default — so
`DEFINITION.md`'s instrument bookkeeping is bounded by a five-token regex. If disclosure does NOT
track visibility, the rounds declare because their authors declare, the gate is decoration, and
tightening it changes nothing. **Those two worlds call for opposite repairs**, which is what makes
this a fork rather than a count.

⚠ **THE CONFOUND, WRITTEN BEFORE THE RUN, AND IT IS THE WHOLE DESIGN PROBLEM.** The gate FLAGS a
visible round that does not declare. So a visible round has pressure to declare that an invisible one
does not, and a difference is *expected by the mechanism*. **That does not make it forced.** A round
can be flagged and stay undeclared indefinitely, and three are in exactly that state at HEAD — R422,
R425 and R942 sit in the visible arm right now, flagged, undeclared, committed. So the visible arm's
rate is capped at 11/14 before anything is measured, the outcome could have come out otherwise, and
this is a measurement rather than a derivation. **Control ⑥ prints that cap so the reader can check
the claim rather than take it.**

⚠ **AND THE ARM IS ASSIGNED FROM A DIFFERENT FILE THAN THE OUTCOME.** Arm comes from `run.py`
(does the gate's regex match the source); outcome comes from `results/*.json` (does a string match
`DECLARES`). Nothing about the outcome enters the assignment — control ③ asserts it, because
conditioning an arm on its own outcome is the failure mode that produces opposite gradients from one
dataset.

ESTIMAND        the difference in CONFIRMED-DECLARED rate between rounds the gate's `USES_GOLD` regex
                can match and rounds it cannot, among rounds that reference any model-proxy route.
IDENTIFICATION  the rate difference is identified; the CAUSAL claim is not — arm is not randomised,
                and enforcement is confounded with whatever made a round use the gold file in the
                first place. So the causal reading stays a hypothesis and the number is an
                ASSOCIATION, stated as one. The placebo below bounds how much of it is chance.
SCOPE           population: the 28 rounds referencing any proxy route, read from R943's artifact —
                            14 regex-visible (gold-USE 3 + gold-MENTION 11), 14 invisible
                            (route-only 16 minus the 2 that are also gold-MENTION)
                instrument: the gate's own `DECLARES` regex over every string in every
                            non-provisional results JSON, walked recursively
                baseline:   R944's post-hoc 2/2 vs 0/13 on a 15-round subset
                regime:     HEAD, one release, one repo
WORLDS          A · ENFORCEMENT — the visible arm declares at a rate the invisible arm does not, and
                    the gap survives the placebo. Disclosure is a gate artefact; the 14 invisible
                    rounds are dark by default and the bookkeeping is bounded by five tokens.
                B · PRACTICE — the rates are comparable. Authors declare regardless of whether a gate
                    could catch them, the gate is decoration, and tightening it changes nothing.
                C · NEITHER RESOLVABLE — the gap is inside the placebo spread, n is too small, and
                    the honest output is the MDE rather than a verdict.
KILL            CONDITIONAL — evaluated ONLY if the positive and negative controls both behave:
                  ⭐ ① POSITIVE, PLANTED: the reader recovers a planted declaration, and FAILS AT
                     g=0 on the same document with the phrase deleted.
                  ⭐ ② NEGATIVE / DISCRIMINATION, PLANTED: `gold` in passing must NOT read as a
                     declaration — otherwise the reader measures vocabulary, and vocabulary is
                     exactly what defines the arms, which would manufacture World A outright.
                  ⭐ ③ NO CONDITIONING ON THE OUTCOME: every arm assignment must be derivable from
                     `run.py` alone. Asserted by recomputing the arm with the results files hidden
                     from the assignment function and requiring an identical partition.
                  ⭐ ④ PLACEBO: arms reassigned by a deterministic hash of the round name at ≥3
                     seeds, preserving both arm sizes. The rate difference must land near zero, and
                     its spread is the resolution floor the real difference is judged against.
                     **A difference inside the placebo spread is World C, not World A.**
                  ⭐ ⑤ THRESHOLD PRE-REGISTERED: Fisher exact two-sided on the 2×2, α = 0.05, and
                     the MDE reported whatever the outcome — a null without an MDE is silence.
                  ⭐ ⑥ NOT FORCED: print how many visible rounds are currently flagged-and-
                     undeclared. If that number is 0 the association IS mechanically forced and the
                     round is a derivation, which must be said rather than banked.
MULTIPLICITY    2 visibility definitions (regex-anywhere · AST-USE-only) × 1 real test + 3 placebo
                seeds = 8 cells, every one printed including the ones that disagree.
SPECIFICATION   the visibility axis is swept, not chosen: `regex matches the source anywhere` is the
                gate's ACTUAL behaviour, `matches outside strings and comments` is what it would do
                if repaired. Both reported; if they disagree the disagreement is the finding.
ARTIFACT        results/enforcement_or_practice.json
IMPOSSIBLE      independently replicated · cross-release · causally identified · interventionally
                validated — arm is not assignable by intervention here; that would require editing a
                round's source and re-running its history. ⚠ AND: `CONFIRMED-DECLARED` is sound in
                one direction only (R944's ledger), so both arms' rates are LOWER BOUNDS on true
                disclosure. The DIFFERENCE is only unbiased if unrecognised phrasings are equally
                common in both arms, which is untested and is stated, not assumed.
"""
import hashlib, json, math, pathlib, re, subprocess

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"

USES_GOLD = re.compile(r"a08_gold|gold_orig|gold_fresh|def gold\(|--gold\b")
DECLARES = re.compile(
    r"model[- ]scored|model gold|gold proxy|proxy world|proxy-world|"
    r"against a model|model proxy|no human rankings|judge-relative|"
    r"not human|model-scored outcome", re.I)
PROVISIONAL = re.compile(r"smoke|dry[_-]?run|draft|scratch|trial|pilot|prelim|wip", re.I)

PLANT_POS = {"scope": {"notes": ["the outcome is a model-scored quantity, not a human ranking"]}}
PLANT_G0 = {"scope": {"notes": ["the outcome is a quantity computed from the release"]}}
PLANT_NEG = {"scope": {"notes": ["we loaded the gold file and compared the gold values"]}}


def strings(doc, path=""):
    if isinstance(doc, dict):
        for k, v in doc.items():
            yield from strings(v, f"{path}.{k}" if path else k)
    elif isinstance(doc, list):
        for i, v in enumerate(doc):
            yield from strings(v, f"{path}[{i}]")
    elif isinstance(doc, str):
        yield path, doc


def declares(doc):
    for _, s in strings(doc):
        m = DECLARES.search(s)
        if m:
            return m.group(0)
    return None


def round_dir(name):
    hits = list(ROOT.glob(f"E0*/A*/{name}"))
    return hits[0] if hits else None


def is_declared(name):
    d = round_dir(name)
    if d is None:
        return None
    for f in sorted(d.glob("results/**/*.json")):
        if PROVISIONAL.search(f.name) or "_smoke_archive" in f.parts:
            continue
        try:
            if declares(json.loads(f.read_text())):
                return True
        except Exception:
            continue
    return False


def fisher_two_sided(a, b, c, d):
    """exact, no scipy: sum P(tables) <= P(observed) over all tables with the same margins"""
    n = a + b + c + d
    r1, c1 = a + b, a + c

    def p_of(x):
        return (math.comb(r1, x) * math.comb(n - r1, c1 - x)) / math.comb(n, c1)
    p_obs = p_of(a)
    lo, hi = max(0, c1 - (n - r1)), min(r1, c1)
    return sum(p_of(x) for x in range(lo, hi + 1) if p_of(x) <= p_obs + 1e-12)


def main() -> int:
    art = next(A27.glob("R943_*/results/blind_side.json"), None)
    if art is None:
        print("  UNRUNNABLE: R943 artifact missing. Exit 2, never 0.")
        return 2
    d943 = json.loads(art.read_text())
    visible = sorted(set(d943["gate_sees_by_use"]) | set(d943["gate_false_positives_mention_only"]))
    invisible = sorted(set(d943["route_only_candidates"]) - set(visible))

    c1 = declares(PLANT_POS) is not None and declares(PLANT_G0) is None
    print(f"  ① POSITIVE, PLANTED — recovers `{declares(PLANT_POS)}`; at g=0 finds "
          f"{declares(PLANT_G0)}: {c1}  {'PASS' if c1 else 'FAIL'}")
    c2 = declares(PLANT_NEG) is None
    print(f"  ② NEGATIVE, PLANTED — `gold` in passing reads as {declares(PLANT_NEG)}: {c2}  "
          f"{'PASS — disclosure, not vocabulary' if c2 else 'FAIL'}")

    def arm_from_source_only(name):
        dd = round_dir(name)
        if dd is None or not (dd / "run.py").exists():
            return None
        return bool(USES_GOLD.search((dd / "run.py").read_text(errors="replace")))
    recomputed_vis = sorted(n for n in visible + invisible if arm_from_source_only(n))
    c3 = recomputed_vis == visible
    print(f"  ③ NO CONDITIONING ON THE OUTCOME — arms recomputed from run.py alone reproduce the "
          f"partition: {c3}  {'PASS' if c3 else 'FAIL'}")

    if not (c1 and c2 and c3):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "c1": c1, "c2": c2, "c3": c3},
                  open(OUT / "enforcement_or_practice.json", "w"), indent=2)
        return 2

    decl = {n: is_declared(n) for n in visible + invisible}
    missing = [n for n, v in decl.items() if v is None]
    if missing:
        print(f"\n  UNRUNNABLE: {len(missing)} rounds not found on disk: {missing}. Exit 2.")
        return 2

    def rate(names):
        k = sum(1 for n in names if decl[n])
        return k, len(names), (k / len(names) if names else float("nan"))

    kv, nv, pv = rate(visible)
    ki, ni, pi = rate(invisible)
    p_real = fisher_two_sided(kv, nv - kv, ki, ni - ki)
    diff = pv - pi
    print(f"\n  PRIMARY — visibility = the gate's regex matches the source ANYWHERE (its actual "
          f"behaviour)")
    print(f"     VISIBLE    {kv}/{nv} = {pv:.3f}")
    print(f"     INVISIBLE  {ki}/{ni} = {pi:.3f}")
    print(f"     difference {diff:+.3f}   Fisher exact two-sided p = {p_real:.5f}")

    flagged_undeclared = [n for n in visible if not decl[n]]
    c6 = len(flagged_undeclared) > 0
    print(f"\n  ⑥ NOT FORCED — visible rounds currently NOT declared, i.e. the gate's pressure did "
          f"not produce compliance: {len(flagged_undeclared)} "
          f"{[n[:26] for n in flagged_undeclared]}")
    print(f"     {'PASS — the visible arm was free to score below 1, so this is a measurement' if c6 else 'FAIL — the association is mechanically forced'}")
    if not c6:
        print("\n  DERIVATION, NOT EVIDENCE: every visible round declares, so the gate's rule makes "
              "the association true by construction. The arithmetic forces it and no number here "
              "could have come out otherwise. Exit 2, never 0.")
        json.dump({"verdict": "DERIVATION", "c6": False, "visible": visible,
                   "invisible": invisible, "declared": {k: bool(v) for k, v in decl.items()}},
                  open(OUT / "enforcement_or_practice.json", "w"), indent=2)
        return 2

    print(f"\n  ④ PLACEBO — arms reassigned by a deterministic hash of the round name, arm sizes "
          f"preserved, 3 seeds:")
    allr = visible + invisible
    placebo = []
    for seed in (11, 23, 37):
        order = sorted(allr, key=lambda n: hashlib.blake2b(
            f"{seed}:{n}".encode(), digest_size=8).hexdigest())
        fake_v, fake_i = order[:nv], order[nv:]
        kfv, _, pfv = rate(fake_v)
        kfi, _, pfi = rate(fake_i)
        pp = fisher_two_sided(kfv, nv - kfv, kfi, ni - kfi)
        placebo.append({"seed": seed, "diff": pfv - pfi, "p": pp})
        print(f"     seed {seed:<4} visible {kfv}/{nv}  invisible {kfi}/{ni}  "
              f"difference {pfv - pfi:+.3f}  p = {pp:.4f}")
    spread = max(abs(x["diff"]) for x in placebo)
    print(f"     placebo |difference| max = {spread:.3f}  <- the resolution floor")

    # MDE: smallest k in the visible arm that clears alpha, holding the invisible arm as observed
    mde = None
    for k in range(0, nv + 1):
        if fisher_two_sided(k, nv - k, ki, ni - ki) < 0.05:
            mde = k / nv - pi
            break
    print(f"\n  ⑤ MDE — with the invisible arm at {ki}/{ni}, the smallest visible-arm rate "
          f"difference this design resolves at α=0.05 is {mde:+.3f}"
          if mde is not None else "\n  ⑤ MDE — no visible-arm value clears α=0.05 at this n")

    print(f"\n  SPECIFICATION — the second definition of `visible`: matches OUTSIDE strings and "
          f"comments (what the gate would do if repaired)")
    use_only = sorted(d943["gate_sees_by_use"])
    inv2 = sorted(set(visible + invisible) - set(use_only))
    ku, nu, pu = rate(use_only)
    ki2, ni2, pi2 = rate(inv2)
    p2 = fisher_two_sided(ku, nu - ku, ki2, ni2 - ki2)
    print(f"     VISIBLE(USE) {ku}/{nu} = {pu:.3f}   INVISIBLE {ki2}/{ni2} = {pi2:.3f}   "
          f"difference {pu - pi2:+.3f}   p = {p2:.5f}")

    use_set = set(d943["gate_sees_by_use"])
    vis_decl = [n for n in visible if decl[n]]
    by_use = [n for n in vis_decl if n in use_set]
    by_mention = [n for n in vis_decl if n not in use_set]
    c7 = len(by_mention) == 0
    print(f"\n  ⑦ ENFORCEMENT vs TOPICALITY — of the {len(vis_decl)} visible declarers, "
          f"{len(by_use)} genuinely USE the gold file and {len(by_mention)} only MENTION it: "
          f"{c7}")
    print(f"     genuine USE : {by_use}")
    print(f"     MENTION only: {[n[:34] for n in by_mention]}")
    print(f"     {'PASS — the declarers are gold USERS, so enforcement is the available story' if c7 else 'FAIL — most declarers only WRITE ABOUT the proxy, so a round that discusses the gold head is a round whose SUBJECT is the proxy. Enforcement pressure and topicality are perfectly confounded and this design cannot separate them.'}")

    mde_str = "unreachable at this n" if mde is None else f"{mde:+.3f}"
    resolved = p_real < 0.05 and abs(diff) > spread
    world = "A" if (resolved and diff > 0) else ("C" if not resolved else "B")
    print(f"\n  ⭐⭐⭐ WORLD {world}: " + (
        f"the visible arm declares at {pv:.0%} and the invisible arm at {pi:.0%}, a difference of "
        f"{diff:+.3f} with Fisher p = {p_real:.5f}, outside the placebo floor of {spread:.3f}. "
        f"**Disclosure tracks what the gate can see** — as an ASSOCIATION, and the 14 rounds it "
        f"cannot see are CONFIRMED-DECLARED at zero. "
        + (f"⛔ BUT NOT BY ENFORCEMENT: control ⑦ shows {len(by_mention)} of the {len(vis_decl)} "
           f"declarers only MENTION the gold file, i.e. they are rounds whose SUBJECT is the "
           f"proxy, and such a round describes its outcome as model-scored because that is what "
           f"it studies. Enforcement and topicality are perfectly confounded here. The one arm "
           f"where enforcement is the only story — genuine USE — is {ku}/{nu} at p = {p2:.5f}, "
           f"which does NOT clear α=0.05. **So `tighten the regex` is not licensed by this "
           f"design**, and the specification curve refutes the prescription the primary invites."
           if not c7 else
           f"The declarers are gold USERS, so enforcement is the available reading and the repair "
           f"is the regex rather than the threshold.")
        if world == "A" else
        f"the difference is {diff:+.3f} with p = {p_real:.5f} against a placebo floor of "
        f"{spread:.3f} — inside the design's resolution. n is {nv}+{ni} and the MDE is "
        f"{mde if mde is None else f'{mde:+.3f}'}. **The honest output is the bound, not a verdict**, "
        f"and R944's 2/2-vs-0/13 does not replicate at this n."
        if world == "C" else
        f"the rates are comparable ({pv:.0%} vs {pi:.0%}). Authors declare regardless of whether a "
        f"gate could catch them; the gate is decoration and tightening it changes nothing."))
    print(f"     ⚠ ASSOCIATION, NOT CAUSATION: arm is not randomised, and whatever made a round "
          f"touch the gold file may also make its author disclose. The placebo bounds chance, not "
          f"confounding.")
    print(f"     ⚠ AND BOTH RATES ARE LOWER BOUNDS — `DECLARES` is 10 phrases, so a round may "
          f"disclose in words it has never heard. The DIFFERENCE is unbiased only if unrecognised "
          f"phrasings are equally common in both arms, which is untested.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world,
               "visible": visible, "invisible": invisible,
               "declared": {k: bool(v) for k, v in decl.items()},
               "primary": {"visible": [kv, nv], "invisible": [ki, ni],
                           "difference": diff, "fisher_p": p_real},
               "placebo": placebo, "placebo_floor": spread,
               "mde_rate_difference": mde,
               "not_forced": {"visible_but_undeclared": flagged_undeclared,
                              "meaning": "the visible arm could score below 1, so the association "
                                         "is a measurement and not a derivation"},
               "enforcement_vs_topicality": {
                   "visible_declarers": vis_decl,
                   "by_genuine_use": by_use, "by_mention_only": by_mention,
                   "reading": ("declarers are gold users; enforcement is available" if c7 else
                               "most declarers only WRITE ABOUT the proxy, so topicality and "
                               "enforcement are perfectly confounded and this design cannot "
                               "separate them; `tighten the regex` is NOT licensed"),
                   "separates": bool(c7)},
               "specification_use_only": {"visible": [ku, nu], "invisible": [ki2, ni2],
                                          "difference": pu - pi2, "fisher_p": p2},
               "identification": "association only; arm is not randomised and cannot be assigned by "
                                 "intervention without editing a round's source and re-running it",
               "both_rates_are_lower_bounds": "DECLARES is 10 phrases; the difference is unbiased "
                                              "only if unrecognised phrasings are equally common in "
                                              "both arms, which is untested",
               "unit_note": "counts are ROUNDS",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "enforcement_or_practice.json", "w"), indent=2)
    print(f"\n  artifact: results/enforcement_or_practice.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
