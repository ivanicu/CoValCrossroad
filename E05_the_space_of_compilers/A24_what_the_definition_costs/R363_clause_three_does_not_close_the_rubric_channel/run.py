"""R363 — clause ③ excludes arms that read the RANKINGS, and not arms that read the RUBRIC.

`DEFINITION.md`'s clause ③ is the one part of the definition with no judge index: *"uses no
information from that prompt's own human labels -- not from the construction, and not from any half
of them."* It is the campaign's last unconditional claim. **And it has never been checked against
the code that builds the arms.**

Every round that applies clause ③ does it the same way, and I wrote the line five times:

    USES_PROMPT_LABELS = {"oracle_k4", "oracle_k4_fit1", "greedy_k4_fit1", "indep_k4_fit1"}

**That is a hand-written answer key**, duplicated across R294, R301, R359 and R360, and clause ③ is
`a not in USES_PROMPT_LABELS`. Read from the source rather than from the list:
`corebench/select_core.py:102` opens `data/comparisons.jsonl` -- the rankings -- **only** when
`rule in ("oracle_k", "indep_k", "greedy_k")`. So the key is CORRECT about the rankings, and the
four arms are exactly the instances of those three rules. That half survives its first audit.

**The half that does not is `topw_k`, which supplies FOUR of the published five.** Its selection is
`sorted(ok, key=lambda i: -w[i])` with

    w = {i: mean(s["score"] for s in items[i]["scores"])}          # select_core.py:132

and `items` comes from `conversation_rubrics.jsonl`. The source comment says *"Non-leaky: the
weights come from the rubric, not from the outcome."* **That is true about the FILE.** This round
asks whether it is true about the INFORMATION -- because a rubric is written by an annotator, and
this release's headline finding is that authoring happens AFTER ranking.

⛔ ARITHMETIC TRAP, and it is the reason for the sham. "The rubric scorers are the same people as
   the rankers" would be FORCED and meaningless if the release used a small fixed annotator panel:
   with 16 people doing every prompt, any two prompts would overlap at 100% and the number would
   say nothing about provenance. So the estimand is the overlap MINUS what a cross-prompt pairing
   gives, and the cross-prompt version is computed on the same data by the same code.

ESTIMAND        Per prompt p: `|A_rubric(p) ∩ A_rank(p)| / |A_rubric(p)|`, where `A_rubric` is the
                set of annotators who assigned an importance score to any criterion of p, and
                `A_rank` the set whose rankings define p's target. And the SHAM: the same quantity
                with `A_rank` taken from a DIFFERENT prompt.

IDENTIFICATION  Exact and a CENSUS, not a sample: both sets are enumerable per prompt and the
                annotator id space is shared between the two files (verified -- the same id appears
                in both for the same prompt). The join is by MESSAGE CONTENT, not by id, because
                the two files use different conversation-id spaces; `covalx.judge.load_join` is the
                campaign's own joiner and its diagnostic is printed rather than assumed.
                NOT identified here: how much of any arm's advantage is ATTRIBUTABLE to this
                channel. That needs the weights recomputed from held-out annotators and is stated
                as the next round, not implied by this one.

SCOPE           the CoVal release's 968 joined prompts · no judge is involved at any point, so this
                result is instrument-free -- the one place in this campaign where that is true, and
                it is true because the quantity is a property of the DATA's provenance structure.

WORLDS
  W-CHANNEL-OPEN   same-prompt overlap is high AND the cross-prompt sham is low. The people who
                   score criterion importance are the people whose rankings are the target, and
                   clause ③ -- which excludes only ranking-readers -- does not close it.
  W-NO-CHANNEL     overlap is low. The rubric is scored by a different panel and `topw_k`'s weights
                   carry no evaluation-annotator information.
  W-FORCED         overlap is high AND the sham is comparably high. Then the release uses a small
                   fixed panel, the overlap is an artefact of pool size, and it licenses nothing.

PREDICTION MATRIX
  W-CHANNEL-OPEN -> same >> sham, and the annotator pool is large relative to per-prompt panels
  W-NO-CHANNEL   -> same is low
  W-FORCED       -> same ~ sham
The three differ on the SAME-minus-SHAM contrast, computed by one function on both.

PRE-REGISTERED KILL -- conditional.
    if join_ok and placebo_ok and pool_ok:
        if mean(same) < 0.25                       -> W-NO-CHANNEL
        elif mean(same) < 2 * mean(sham)           -> W-FORCED
        else                                        -> W-CHANNEL-OPEN
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

SHAM            `A_rubric(p)` against `A_rank(q)` for a random q != p, one draw per prompt, 3 seeds.
                This is the same operation minus the ingredient (being the SAME prompt), and it is
                what distinguishes a provenance fact from a pool-size fact.
PLACEBO         `A_rubric(p)` against itself: exactly 1.0 at every prompt.
POOL CONTROL    the total distinct annotator count in the release, printed. A pool barely larger
                than a per-prompt panel would make the sham uninformative, so the number is stated
                rather than assumed adequate.
JOIN CONTROL    `load_join`'s own diagnostic -- how many prompts matched canonically, how many
                fuzzily, how many not at all -- printed every run. An unmatched remainder is a
                population this round did not see, and it is named.
MULTIPLICITY    one estimand, one sham, 968 prompts; the full distribution is persisted, not just
                its median.
SEEDS           3 on the sham's random pairing; each reported, never averaged into one number.
ARTIFACT        results/r363_rubric_channel.json with the source hash.

IMPOSSIBLE HERE
  the channel's SIZE      -- needs `topw_k` rebuilt from held-out annotators' weights and rescored.
                             Named as the next round rather than gestured at.
  cross-release           -- one release.

EXIT
    0  controls hold and the channel is classified
    1  a control misbehaved -- UNVERIFIED
    2  an input is missing or nothing joined -- never a silent pass
"""
from __future__ import annotations
import hashlib, json, pathlib, random, statistics as st, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "covalx"))
try:
    from stamp import stamp                                  # noqa: E402
except Exception:                                            # pragma: no cover
    def stamp(f):
        return {"source_sha256": hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest(),
                "source_name": pathlib.Path(f).name}
from covalx.judge import load_join                           # noqa: E402

SEEDS = (0, 1, 2)


def main() -> int:
    cmp_f = ROOT / "data" / "comparisons.jsonl"
    rub_f = ROOT / "data" / "conversation_rubrics.jsonl"
    for f in (cmp_f, rub_f):
        if not f.exists():
            print(f"  UNRUNNABLE: {f.name} absent. Exit 2, never 0."); return 2

    print("R363 · does clause ③ close the RUBRIC channel, or only the RANKING channel?\n")
    print("  read from source, not from the answer key:")
    print("    select_core.py:102  opens comparisons.jsonl only for oracle_k / indep_k / greedy_k")
    print("    select_core.py:132  w = mean importance score, from conversation_rubrics.jsonl")
    print("    -> the hand-written USES_PROMPT_LABELS set is CORRECT about the rankings.")
    print("    -> `topw_k` selects on w. This round asks who wrote w.\n")

    J = load_join(cmp_f, rub_f)
    if not J:
        print("  UNRUNNABLE: nothing joined. Exit 2, never 0."); return 2

    RA, CA = {}, {}
    for pid, prec, rrec in J:
        RA[pid] = {s["annotator_id"]
                   for it in (rrec.get("coval_full") or [])
                   for s in (it.get("scores") or []) if s.get("annotator_id")}
        CA[pid] = {a["annotator_id"]
                   for a in prec.get("metadata", {}).get("assessments", [])
                   if a.get("annotator_id")}
    pids = [p for p in RA if RA[p] and CA[p]]
    if not pids:
        print("  UNRUNNABLE: no prompt carries both sets. Exit 2, never 0."); return 2

    pool = set().union(*RA.values()) | set().union(*CA.values())
    same = [len(RA[p] & CA[p]) / len(RA[p]) for p in pids]
    SHAM = {}
    for s in SEEDS:
        rng = random.Random(s)
        vals = []
        for p in pids:
            q = rng.choice(pids)
            while q == p:
                q = rng.choice(pids)
            vals.append(len(RA[p] & CA[q]) / len(RA[p]))
        SHAM[s] = vals
    sham_mean = st.mean([st.mean(SHAM[s]) for s in SEEDS])

    print(f"  {len(pids)} prompts carry both sets · {len(pool)} DISTINCT annotators in the release")
    print(f"  per prompt: {st.median([len(RA[p]) for p in pids]):.0f} rubric scorers, "
          f"{st.median([len(CA[p]) for p in pids]):.0f} rankers (medians)\n")
    print(f"    {'quantity':>34}{'median':>9}{'mean':>9}{'min':>7}")
    print(f"    {'SAME prompt  |A_rub ∩ A_rank|/|A_rub|':>34}{st.median(same):>9.3f}"
          f"{st.mean(same):>9.3f}{min(same):>7.2f}")
    for s in SEEDS:
        print(f"    {f'SHAM seed {s}  vs a DIFFERENT prompt':>34}{st.median(SHAM[s]):>9.3f}"
              f"{st.mean(SHAM[s]):>9.3f}{min(SHAM[s]):>7.2f}")
    print(f"\n    ratio same/sham  {st.mean(same)/max(sham_mean,1e-9):.1f}x")
    allr = sum(1 for f in same if f >= 0.999)
    print(f"    prompts where EVERY rubric scorer also ranked: {allr} of {len(pids)} "
          f"({100*allr/len(pids):.1f}%)")
    print(f"    prompts with ZERO overlap: {sum(1 for f in same if f == 0)}")

    # ---- controls -----------------------------------------------------------------------------
    plac = all(len(RA[p] & RA[p]) / len(RA[p]) == 1.0 for p in pids)
    pool_ok = len(pool) > 5 * st.median([len(CA[p]) for p in pids])
    join_ok = len(pids) > 0
    print(f"\n  PLACEBO   a rubric-scorer set against ITSELF: 1.000 at every prompt  "
          f"{'PASS' if plac else 'FAIL'}")
    print(f"  POOL      {len(pool)} distinct annotators vs a median panel of "
          f"{st.median([len(CA[p]) for p in pids]):.0f} — the sham is informative only if the pool")
    print(f"            is much larger than a panel  {'PASS' if pool_ok else 'FAIL'}")
    print(f"  JOIN      the joiner's own diagnostic is printed above by `load_join`; "
          f"{len(J)} prompts joined")
    print(f"            ⚠ the unmatched remainder it reports is a population this round did NOT")
    print(f"            see, and it is named there rather than folded into the denominator.")

    ctrl_ok = plac and pool_ok and join_ok
    m = st.mean(same)
    print()
    if not ctrl_ok:
        print("  UNVERIFIED — a control misbehaved; the numbers above are silence.")
        v = "UNVERIFIED"
    elif m < 0.25:
        print(f"  W-NO-CHANNEL — same-prompt overlap {m:.3f}: the rubric is scored by a different")
        print(f"  panel, and `topw_k`'s weights carry no evaluation-annotator information.")
        v = "W_NO_CHANNEL"
    elif m < 2 * sham_mean:
        print(f"  W-FORCED — overlap {m:.3f} against a sham of {sham_mean:.3f}. The release uses a")
        print(f"  small fixed panel, so the overlap is an artefact of pool size and licenses nothing.")
        v = "W_FORCED"
    else:
        print(f"  W-CHANNEL-OPEN — the annotators who score criterion IMPORTANCE are, at "
              f"{m:.1%},")
        print(f"  the same people whose RANKINGS define that prompt's target. The cross-prompt sham")
        print(f"  is {sham_mean:.3f}, so this is provenance and not pool size ("
              f"{m/max(sham_mean,1e-9):.0f}x).")
        print(f"\n  ⛔ WHAT IT MEANS FOR THE DEFINITION, and the two halves are DIFFERENT KINDS.")
        print(f"     MEASURED: the overlap above, a census over {len(pids)} prompts.")
        print(f"     DERIVED (from that census + this release's own headline that rubrics are")
        print(f"       authored AFTER ranking): `topw_k`'s selection weights are written by the")
        print(f"       very annotators whose rankings it is later scored against. So `producible")
        print(f"       from the conversation alone` is FALSE of `topw_k` as constructed — it is")
        print(f"       produced from the conversation PLUS a post-ranking artefact of the same")
        print(f"       people. Clause ③ excludes RANKING readers and does not exclude this.")
        print(f"     UNMEASURED: how much of `topw_k`'s advantage is attributable to the channel.")
        print(f"       That needs the weights rebuilt from held-out annotators, and it is the next")
        print(f"       round rather than something this one may imply.")
        print(f"  ⚠ And the scope that makes this unusual here: NO JUDGE IS INVOLVED. It is a fact")
        print(f"    about the release's provenance structure, so unlike every other clause it")
        print(f"    carries no instrument index.")
        v = "W_CHANNEL_OPEN"

    art = dict(stamp(str(SELF)), n_prompts=len(pids), n_annotators=len(pool),
               median_rubric_scorers=st.median([len(RA[p]) for p in pids]),
               median_rankers=st.median([len(CA[p]) for p in pids]),
               same=dict(median=st.median(same), mean=st.mean(same), min=min(same)),
               sham={str(s): dict(median=st.median(SHAM[s]), mean=st.mean(SHAM[s])) for s in SEEDS},
               sham_mean=sham_mean, ratio=st.mean(same) / max(sham_mean, 1e-9),
               all_overlap_prompts=allr, zero_overlap_prompts=sum(1 for f in same if f == 0),
               controls=dict(placebo=plac, pool=pool_ok, join=join_ok), verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r363_rubric_channel.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0 if ctrl_ok else 1


if __name__ == "__main__":
    sys.exit(main())
