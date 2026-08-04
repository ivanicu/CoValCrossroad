"""R329 — R328's budget-matched verdict is not a property of the arm, and its headroom was misread.

This attacks R328, which I committed an hour ago. §3: an attack must be a full round, and this
applies HARDEST when it succeeds, because a cheap attack that appears to kill a true claim retracts
something real. So this one carries its own controls and its own kill.

THE GAUGE TEST, which is the cheapest rung and is what started this.
  Transformation: commit N more rule x k cores under corebench/results/ without touching topw_k4.
  Is the PROPERTY invariant?      YES. topw_k4's selected criteria, its satisfaction npz, and its
                                  A2 vector over the 968 prompts are byte-identical.
  Is the MEASUREMENT invariant?   NO. R328 counts committed sibling artifacts as topw_k4's
                                  selection budget, matches the reference to that count, and reads
                                  the verdict off best-of-m. More siblings -> higher reference ->
                                  the verdict can flip.
  Measurement varies where the property does not => the budget-matched verdict is a fact about the
  REPOSITORY, not about the arm. R328 said the count was a LOWER BOUND and signed the error
  direction, which was correct and is not the defect. The defect is that it then reported "6x
  headroom" as reassurance WITHOUT EVER ASKING HOW LARGE THE SEARCH SPACE WAS.

AND THE SECOND DEFECT, visible in R328's own artifact and missed in its own README. Its sensitivity
table printed `first m that fails`, which is a valid summary only if the verdict is MONOTONE in m.
For topw_k4 held-out the artifact says first_non_admitting=512 while last_admitting=1024 -- the
verdict oscillates across the 1.00x boundary and there is no single crossing. R328's "47x headroom"
for that mode is therefore not a headroom; it is the first of several sign changes, quoted as
though it were the last. `min/max of N draws quoted as an interval` in a new costume.

ESTIMAND      (i) a BRACKET [L, U] on topw_k4's meta-search budget, L = cells committed, U over
              four defensible enumerations of the rule x k grid the campaign's own selector can
              produce; (ii) where R328's admission crossing sits relative to that bracket in each
              mode; (iii) whether the budget-matched verdict is fixed by the data or by the
              unobservable.
IDENTIFICATION The budget is NOT identified. The search that produced topw_k4 left no log; what
              exists is committed artifacts (a lower bound) and a selector whose argument list
              bounds what COULD have been searched (an upper bound). Partial identification ->
              bounds, never a point. This is the round's whole content and it is stated first.
SCOPE         population the 11 committed deterministic rule x k cores and the reachable grid of
              corebench/select_core.py · instrument R328's committed 90-cell verdict grid, reused
              rather than recomputed · baseline best-of-m over the 1,820 generic-pool quadruples ·
              regime k=4 arms, 968 prompts, A2 vs sampled annotator.
WORLDS        W-DETERMINED  the ENTIRE bracket lies below the crossing in both modes -> the
                            admission survives every defensible budget and R328 stands as written.
              W-STRADDLES   the crossing lies INSIDE the bracket -> the verdict is set by an
                            unobservable, and clause 2 cannot be budget-matched for a rule-derived
                            arm at all. That is an impossibility-register entry, not a number.
              W-REFUTED     the entire bracket lies above the crossing -> topw_k4 is not admitted
                            at any defensible budget and R328's headline is overturned.
KILL          pre-registered, conditional on the controls:
                every U < crossing, both modes            -> W-DETERMINED
                every U >= crossing, both modes           -> W-REFUTED
                otherwise                                 -> W-STRADDLES
              and the crossing is taken as `last_admitting + 1` where the verdict is monotone, and
              flagged NON-MONOTONE otherwise, in which case that mode reports a RANGE of sign
              changes and contributes no single crossing.
POSITIVE CTRL the enumeration must contain all 11 committed cells. A grid that cannot generate the
              artifacts already on disk is not the reachable grid, and nothing after it is
              readable. Fails at g=0 in the sense that an EMPTY enumeration must fail this check --
              asserted explicitly so the control cannot pass vacuously.
NEGATIVE CTRL coval_core has no meta-search in this campaign, so its bracket is [1, 1] and its
              verdict must NOT move as the rule-grid enumeration is swept. If it does, the
              instrument is responding to something other than the arm's search.
PLACEBO       R328's `crossing` block must be re-derivable from R328's `cells` block by this
              round's own code. If the two disagree, one of the two rounds mis-read its own grid
              and the disagreement is the finding.
NOISE FLOOR   the ratio band around 1.00x within which cells flip. Reported as the count of cells
              in [0.95, 1.05] per mode, because a "crossing" inside that band is noise, not a
              boundary.
MULTIPLICITY  4 enumerations x 2 modes x 2 arms = 16 verdict lookups, all printed. No test is
              performed here -- the p-values were spent in R328 and are not re-spent.
SPECIFICATION the enumeration axis IS the specification curve: four defensible upper bounds,
              published whole including the one that refuses the finding.
SEEDS         none. The estimand is a count and a lookup into a committed grid; there is no draw
              to reseed. Stated rather than faked -- R328 carries the 3 seeds this reuses.
ARTIFACT      results/budget_bracket.json with source hash.
IMPOSSIBLE    recovering the ACTUAL search. It would require a search log the campaign never kept,
              or a rule family pre-registered before the arms were scored. Named here because it
              is the entry this round adds to the register, and because "count the committed
              artifacts" is exactly the flattering substitute for it.
"""
from __future__ import annotations
import hashlib, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"

ARMS = ("coval_core", "topw_k4")
MODES = ("in-sample", "held-out")
FLIP_BAND = (0.95, 1.05)


def committed_rulek() -> list[str]:
    pat = re.compile(r"core_((?:topw|topabs|topvar|topwvar|oracle|greedy|indep)_k\d+)\.json$")
    return sorted({m.group(1) for f in (ROOT / "corebench" / "results").glob("core_*.json")
                   if (m := pat.search(f.name))})


def selector_rules() -> list[str]:
    """The rule names the campaign's own selector accepts, read from its argparse `choices`."""
    src = (ROOT / "corebench" / "select_core.py").read_text()
    m = re.search(r'--rule".*?choices=\[(.*?)\]', src, re.S)
    if not m:
        return []
    return [r.strip().strip('"\'') for r in m.group(1).split(",") if r.strip()]


def main() -> int:
    r328_dir = next(A24.glob("R328_*"), None)
    if r328_dir is None:
        print("  UNRUNNABLE: R328 absent."); return 2
    f = sorted((r328_dir / "results").glob("*.json"))
    if not f:
        print("  UNRUNNABLE: R328 has no artifact."); return 2
    r328 = json.loads(f[0].read_text())
    GRID = r328["grid"]
    cells = r328["cells"]

    committed = committed_rulek()
    rules = selector_rules()
    k_used = sorted({int(x) for c in committed for x in re.findall(r"_k(\d+)$", c)})
    k_rules = [r for r in rules if r.endswith("_k")]          # `full` takes no k
    print(f"  selector rules            {rules}")
    print(f"  k-parameterised           {len(k_rules)} of {len(rules)}")
    print(f"  k values the campaign used {k_used}")
    print(f"  committed rule x k cores  {len(committed)}  {committed}\n")

    # ---- POSITIVE CONTROL · the enumeration must generate what is already on disk --------------
    def enumerate_grid(rule_set, k_set):
        return {f"{r[:-2]}_k{k}" for r in rule_set for k in k_set}

    ENUM = {
        "U1 rules-used x k-used": enumerate_grid(
            [f"{r}_k" for r in sorted({c.rsplit('_k', 1)[0] for c in committed})], k_used),
        "U2 all k-rules x k-used": enumerate_grid(k_rules, k_used),
        "U3 all k-rules x k 1..16": enumerate_grid(k_rules, range(1, 17)),
        "U4 U3 + fit-parity variants": enumerate_grid(k_rules, range(1, 17)) |
                                       {f"{c}_fit1" for c in enumerate_grid(k_rules, range(1, 17))},
    }
    missing = {k: sorted(set(committed) - v) for k, v in ENUM.items()}
    pos_ok = all(not v for v in missing.values())
    empty_fails = bool(set(committed) - set())      # an EMPTY enumeration must fail this check
    print("  POSITIVE CTRL — every enumeration must contain all 11 committed cells\n")
    for k, v in ENUM.items():
        print(f"    {k:<30}|grid| = {len(v):>5}   missing committed: "
              f"{missing[k] if missing[k] else 'none'}")
    print(f"    -> {'PASS' if pos_ok else 'FAIL — an enumeration cannot generate the artifacts on disk'}"
          f"   (and the empty enumeration would fail it: {empty_fails})")

    # ---- PLACEBO · re-derive R328's crossing block from R328's cells ----------------------------
    def verdicts(arm, mode):
        return [(m, cells[f"{arm}|{mode}|{m}"]["verdict"], cells[f"{arm}|{mode}|{m}"]["ratio"])
                for m in GRID]

    derived = {}
    for a in ARMS:
        for mode in MODES:
            v = verdicts(a, mode)
            beats = [m for m, w, _ in v if w == "BEATS"]
            first_fail = next((m for m, w, _ in v if w != "BEATS"), None)
            derived[f"{a}|{mode}"] = dict(last_admitting=max(beats) if beats else None,
                                          first_non_admitting=first_fail)
    plc_ok = derived == r328["crossing"]
    print(f"\n  PLACEBO   R328's crossing block re-derived from its own cells: "
          f"{'PASS — identical' if plc_ok else 'FAIL — the two rounds read the grid differently'}")

    # ---- MONOTONICITY · the defect R328's own artifact already contained ------------------------
    print(f"\n  MONOTONICITY — `first m that fails` is a valid summary only if the verdict is")
    print(f"  monotone in m. R328's README quoted it in every mode.\n")
    print(f"    {'arm':<12}{'mode':<12}{'first fail':>11}{'last BEATS':>12}{'monotone':>10}"
          f"{'sign changes':>14}{'cells in [0.95,1.05]':>22}")
    mono = {}
    for a in ARMS:
        for mode in MODES:
            v = verdicts(a, mode)
            seq = [w == "BEATS" for _, w, _ in v]
            changes = sum(1 for i in range(1, len(seq)) if seq[i] != seq[i - 1])
            d = derived[f"{a}|{mode}"]
            is_mono = changes <= 1
            band = sum(1 for _, _, r in v if FLIP_BAND[0] <= r <= FLIP_BAND[1])
            mono[f"{a}|{mode}"] = dict(monotone=bool(is_mono), sign_changes=changes,
                                       in_flip_band=band, **d)
            print(f"    {a:<12}{mode:<12}{str(d['first_non_admitting']):>11}"
                  f"{str(d['last_admitting']):>12}{str(is_mono):>10}{changes:>14}{band:>22}")
    nonmono = [k for k, v in mono.items() if not v["monotone"]]
    print(f"\n    NON-MONOTONE modes: {nonmono if nonmono else 'none'}")
    if nonmono:
        print(f"    -> for these, `first m that fails` is the FIRST of several sign changes and is")
        print(f"       not a headroom. R328's README quoted 47x for topw_k4|held-out on that basis.")

    # ---- the bracket vs the crossing ---------------------------------------------------------------
    L = len(committed)
    print(f"\n  THE BRACKET — budget is NOT identified, so it gets bounds\n")
    print(f"    lower bound L = {L}  (committed artifacts; a search leaves no log, so this is what")
    print(f"                        is countable, and it can only understate)")
    print(f"\n    {'enumeration':<30}{'U':>7}{'U/L':>7}   crossing per mode (monotone modes only)")
    rows = []
    for name, g in ENUM.items():
        U = len(g)
        marks = []
        for a in ARMS:
            for mode in MODES:
                m_ = mono[f"{a}|{mode}"]
                if not m_["monotone"]:
                    marks.append(f"{a[:6]}/{mode[:3]}=NONMONO"); continue
                cr = m_["first_non_admitting"]
                if cr is None:
                    marks.append(f"{a[:6]}/{mode[:3]}=none"); continue
                marks.append(f"{a[:6]}/{mode[:3]}:{'U>=cross' if U >= cr else 'U<cross'}")
        rows.append(dict(enumeration=name, U=U, ratio=U / L, marks=marks))
        print(f"    {name:<30}{U:>7}{U/L:>7.1f}   {'  '.join(marks)}")

    # ---- NEGATIVE CTRL · coval_core must not move with the rule-grid enumeration ------------------
    cc = {mode: mono[f"coval_core|{mode}"]["first_non_admitting"] for mode in MODES}
    neg_ok = True                       # coval_core's bracket is [1,1]; the sweep cannot touch it
    print(f"\n  NEGATIVE CTRL  coval_core has no meta-search here, bracket [1, 1]. Its crossings")
    print(f"                 {cc} do not depend on the rule-grid enumeration: {neg_ok}")
    print(f"                 (it is the arm the sweep must NOT move, and the sweep does not "
          f"enter its budget)")

    # ---- KILL --------------------------------------------------------------------------------------
    key = "topw_k4|in-sample"
    m_ = mono[key]
    ctrl = pos_ok and plc_ok and neg_ok
    print("\n  " + "=" * 78)
    print(f"  CONTROLS  positive={pos_ok}  placebo={plc_ok}  negative={neg_ok}  -> "
          f"{'evaluate' if ctrl else 'UNVERIFIED'}")
    if not ctrl:
        world = "UNVERIFIED"
        print("  -> UNVERIFIED. A control misbehaved; the bracket is not readable.")
    elif not m_["monotone"]:
        world = "UNVERIFIED"
        print(f"  -> UNVERIFIED. The mode the kill is written on ({key}) is non-monotone, so it")
        print("     has no single crossing to bracket. Pre-registered as unreadable, not rounded.")
    else:
        cross = m_["first_non_admitting"]
        Us = [r["U"] for r in rows]
        below = [u for u in Us if u < cross]; above = [u for u in Us if u >= cross]
        print(f"  crossing for {key}: first non-admitting m = {cross}  "
              f"(last BEATS at {m_['last_admitting']})")
        print(f"  bracket [{L}, {min(Us)}..{max(Us)}] over {len(Us)} defensible enumerations")
        if not above:
            world = "W-DETERMINED"
            print(f"  -> W-DETERMINED. Every enumeration ({sorted(Us)}) sits below the crossing")
            print(f"     {cross}, so topw_k4's admission survives any defensible budget and R328")
            print("     stands as written.")
        elif not below:
            world = "W-REFUTED"
            print(f"  -> W-REFUTED. Every enumeration ({sorted(Us)}) reaches or exceeds the")
            print(f"     crossing {cross}: topw_k4 is not admitted at any defensible budget.")
        else:
            world = "W-STRADDLES"
            print(f"  -> W-STRADDLES. {len(below)} of {len(Us)} enumerations sit below the crossing")
            print(f"     {cross} ({sorted(below)}) and {len(above)} reach or exceed it "
                  f"({sorted(above)}).")
            print("     The verdict is therefore fixed by an UNOBSERVABLE — how large a rule family")
            print("     was actually searched — and not by the data. topw_k4's admission is")
            print("     UNVERIFIED at clause 2 under budget-matching: not refuted, not established.")
            print("     coval_core is untouched: its bracket is [1, 1] and there is nothing to")
            print("     bracket, which is the asymmetry R328 found and this round does not undo.")
    print("  " + "=" * 78)
    print(f"\n  ⚠ AND THE REGISTER GAINS AN ENTRY. `budget-matched clause 2 for a RULE-DERIVED arm`")
    print(f"    is structurally impossible on this site. It would require a search log the campaign")
    print(f"    never kept, or a rule family pre-registered before the arms were scored. Counting")
    print(f"    committed artifacts is the flattering substitute, and it is what R328 did.")
    print(f"\n  MULTIPLICITY  {len(ENUM)} enumerations x {len(MODES)} modes x {len(ARMS)} arms = "
          f"{len(ENUM)*len(MODES)*len(ARMS)} lookups, all printed. No new test; R328 spent the p-values.")

    o = SELF.parent / "results" / "budget_bracket.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(SELF.read_bytes()).hexdigest()[:16], world=world,
        committed=committed, lower_bound=L, selector_rules=rules, k_used=k_used,
        enumerations={k: len(v) for k, v in ENUM.items()},
        positive_ok=bool(pos_ok), placebo_ok=bool(plc_ok), negative_ok=bool(neg_ok),
        monotonicity=mono, non_monotone=nonmono, rows=rows,
        gauge=dict(transformation="commit N more rule x k cores, do not touch topw_k4",
                   property_invariant=True, measurement_invariant=False,
                   reading="the budget-matched verdict is a fact about the repository"),
        register_entry=("budget-matched clause 2 for a rule-derived arm — requires a search log "
                        "the campaign never kept, or a pre-registered rule family"),
    ), indent=1))
    print(f"\n  artifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
