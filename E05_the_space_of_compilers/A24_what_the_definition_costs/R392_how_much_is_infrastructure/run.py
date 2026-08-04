"""R392 -- how much of the backfill population is INFRASTRUCTURE rather than result?

R391 classified three silent rounds and found two consumed by later code. Its NEXT proposed running
the same detector over the whole population, because every round with a consumer is one that must
NOT be backfilled, and the standing denominator of 226 is an upper bound nobody has tested.

⛔ AND R391'S DETECTOR HAS A FLAW THAT DID NOT MATTER AT n=3 AND WOULD AT n=226. It counted a round
   as "consumed" if another source named EITHER its artifact file OR its directory. Those are not
   the same relation. Naming a directory is often a PROSE CITATION -- R21's own docstring opens
   "r15 and r20 both rest on a neighbour arm chosen by cosine", which is an argument about those
   rounds, not a read of their output. At three rounds the merge was tolerable; over 226 it would
   inflate the infrastructure count with every literature reference in the corpus.
   So the two channels are SPLIT here and both are reported, and R391's merged count is corrected
   rather than quietly superseded.

⛔ ARITHMETIC TRAP, answered before the run. Could this come out otherwise? YES, and the two
   channels can disagree, which is the point of splitting them. A corpus of instrument-building
   rounds could be mostly consumed; a corpus of independent experiments could be almost entirely
   unconsumed. Nothing in the design forces either.
   ⚠ What IS forced and is excluded: a round names its own artifact, because it writes it. Self
   references are removed before any count.

ESTIMAND        over the backfill population (rounds with an artifact, a run.py and no finding site):
                (a) ARTIFACT CONSUMPTION -- how many have their artifact FILE named by another
                    source. This is a real dependency.
                (b) NAME MENTION -- how many have their DIRECTORY named by another source. This
                    includes prose citation and is an upper bound on (a).
                Both reported; (a) is the estimand the decision rests on.

IDENTIFICATION  Exact for literal references in committed source. NOT identified: a consumer that
                builds its path dynamically or reads through a helper. That blind spot biases (a)
                DOWNWARD -- toward "not infrastructure, so backfill it" -- which is the direction
                that creates work rather than excuses it, and it is named in the verdict.

SCOPE           population: the backfill rounds R389 enumerated · instrument: literal substring
                search over every round/assurance/covalx source · baseline: two consumption edges
                committed before this question · regime: HEAD.

WORLDS
  W-MOSTLY-INFRASTRUCTURE  a large share have their artifact read. The denominator of the backfill
                           debt is materially smaller than 226, and the corpus is largely a machine
                           whose parts feed each other.
  W-MOSTLY-RESULTS         few do. The rounds are independent experiments, the denominator stands,
                           and the debt is as large as it looked.
  W-SPLIT                  a substantial minority -- and then the two counts are the estimate.

PREDICTION MATRIX
  W-MOSTLY-INFRASTRUCTURE -> artifact-consumed >= 50%
  W-MOSTLY-RESULTS        -> artifact-consumed <= 20%
  W-SPLIT                 -> between

PRE-REGISTERED KILL -- conditional on the controls, never on a share alone.
    if both known artifact edges are found and the nowhere-file returns zero
       and the prose-citation control behaves as described:
        a = share of the population whose ARTIFACT is named by another source
        if a >= 0.50   -> W-MOSTLY-INFRASTRUCTURE
        elif a <= 0.20 -> W-MOSTLY-RESULTS
        else           -> W-SPLIT, and both channels are the estimate
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

CONTROLS
  ARTIFACT (+)  two edges committed BEFORE this question, by other rounds, for other purposes:
                `sat_genericpool16_fresh.npz` read by R371, `r371_power.json` read by R372.
  ARTIFACT (-)  a filename that exists nowhere returns zero consumers.
  CHANNEL       the two channels must not be equal. If NAME and ARTIFACT return the same set, the
                split is decorative and the correction to R391 is unsupported -- so the difference
                is computed and printed, not asserted.
  SELF          a round's own directory is excluded from its own consumer set.
  EMPTY         fewer than 100 sources searched, or fewer than 50 population rounds -> exit 2.

MULTIPLICITY    two channels over one population; both counts printed, and the disagreement between
                them is printed too.
SEEDS           none -- static search.
ARTIFACT        results/r392_infrastructure_share.json with the source hash.

IMPOSSIBLE HERE
  dynamic paths        -- invisible; biases the estimand DOWNWARD, toward more work rather than less.
  whether a consumed round also HAD a finding -- being read and having something to say are
                          different, and only the second is what the debt is about.
  a second release     -- one release.

EXIT
    0  controls hold and the population is classified
    1  a control misbehaved -- UNVERIFIED
    2  the corpus or population is too small -- never a silent pass
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
R389 = HERE.parent / "R389_the_reading_burden" / "results" / "r389_reading_burden.json"
KNOWN = (("sat_genericpool16_fresh.npz", "R371"), ("r371_power.json", "R372"))
# ⛔ THE NEGATIVE CONTROL FAILED ON ITS FIRST TOKEN, AND THE REASON IS ITSELF A FINDING. R391 used
#   `zzq_no_such_artifact_zzq.json` as ITS nowhere-file, so that string is now IN THE CORPUS — inside
#   R391's committed source — and searching for it returns 1 consumer. **A corpus absorbs its own
#   instruments**, which means a nowhere-token is only nowhere until a round uses it. The control
#   caught it because a nowhere-file with a consumer is impossible by construction; the token is
#   replaced, and the mechanism is recorded rather than the string quietly swapped.
NOWHERE = "zzq_r392_absent_token_never_written_zzq.json"
sys.path.insert(0, str(ROOT / "covalx"))
try:
    from stamp import stamp
except Exception:
    def stamp(f):
        return {"source_sha256": hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest(),
                "source_name": pathlib.Path(f).name}


def main() -> int:
    if not R389.exists():
        print("  UNRUNNABLE: R389's artifact absent. Exit 2, never 0."); return 2
    pop_names = sorted(json.loads(R389.read_text())["rows"])
    if len(pop_names) < 50:
        print(f"  UNRUNNABLE: population {len(pop_names)}. Exit 2, never 0."); return 2

    sources = {}
    for pat in ("E0*/A*/R*/*.py", "assurance/*.py", "covalx/*.py"):
        for p in sorted(ROOT.glob(pat)):
            if HERE in p.parents:
                continue
            try:
                sources[p] = p.read_text()
            except Exception:
                continue
    if len(sources) < 100:
        print(f"  UNRUNNABLE: only {len(sources)} sources. Exit 2, never 0."); return 2

    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True,
                          text=True).stdout.strip()[:12]
    print(f"R392 · how much of the population is infrastructure?   HEAD {head}\n")
    print(f"  ⛔ R391 counted a round as consumed if another source named EITHER its artifact OR its")
    print(f"     directory. Those are different relations: naming a directory is often a PROSE")
    print(f"     CITATION — R21's docstring opens \"r15 and r20 both rest on a neighbour arm\", an")
    print(f"     argument about those rounds, not a read of their output. At n=3 the merge was")
    print(f"     tolerable; over {len(pop_names)} it would inflate infrastructure with every")
    print(f"     literature reference in the corpus. The channels are SPLIT here.\n")
    print(f"  {len(sources)} sources searched · {len(pop_names)} population rounds")

    dirs = {}
    for name in pop_names:
        d = next((q for q in ROOT.glob(f"E0*/A*/{name}") if q.is_dir()), None)
        dirs[name] = d

    def hits(token, own_dir):
        return sorted(str(p.relative_to(ROOT)) for p, t in sources.items()
                      if token in t and (own_dir is None or own_dir not in p.parents))

    # ---- CONTROLS ------------------------------------------------------------------------------
    known_ok = {}
    for tok, expect in KNOWN:
        known_ok[tok] = any(expect in h for h in hits(tok, None))
    pos_ok = all(known_ok.values())
    neg_ok = (len(hits(NOWHERE, None)) == 0)
    print(f"\n  CONTROLS")
    print(f"    ARTIFACT (+)  {known_ok}  {'PASS' if pos_ok else 'FAIL'}")
    print(f"    ARTIFACT (-)  a filename existing nowhere -> "
          f"{len(hits(NOWHERE, None))} consumers  {'PASS' if neg_ok else 'FAIL'}")
    if not (pos_ok and neg_ok):
        print("\n  UNVERIFIED — the detector is blind in one direction. Exit 1."); return 1

    # ---- the two channels ------------------------------------------------------------------------
    rows = {}
    for name in pop_names:
        d = dirs[name]
        if d is None:
            rows[name] = dict(present=False); continue
        arts = sorted(f.name for f in (d / "results").glob("*")) if (d / "results").is_dir() else []
        acons = set()
        for a in arts:
            acons.update(hits(a, d))
        ncons = set(hits(name, d))
        rows[name] = dict(present=True, artifacts=arts,
                          artifact_consumers=sorted(acons), name_mentions=sorted(ncons))
    live = {k: v for k, v in rows.items() if v.get("present")}
    art_c = [k for k, v in live.items() if v["artifact_consumers"]]
    name_c = [k for k, v in live.items() if v["name_mentions"]]
    both = set(art_c) & set(name_c)
    name_only = sorted(set(name_c) - set(art_c))
    a_share = len(art_c) / len(live)
    n_share = len(name_c) / len(live)
    chan_ok = (set(art_c) != set(name_c))
    print(f"\n  THE TWO CHANNELS — measured separately, on purpose")
    print(f"    artifact CONSUMED (a real dependency) : {len(art_c):>4} of {len(live)}  "
          f"({a_share:.0%})")
    print(f"    name MENTIONED (citation or read)     : {len(name_c):>4} of {len(live)}  "
          f"({n_share:.0%})")
    print(f"    mentioned but artifact NOT read       : {len(name_only):>4}   "
          f"<- R391's merge would have counted these as infrastructure")
    print(f"    CHANNEL control: the two sets differ: {chan_ok}  "
          f"{'PASS' if chan_ok else 'FAIL — the split is decorative'}")
    if not chan_ok:
        print("\n  UNVERIFIED — the two channels are identical, so R391's correction is")
        print("  unsupported and the split says nothing. Exit 1.")
        return 1

    print(f"\n  ⭐ AND THIS CORRECTS R391 ON ITS OWN THREE ROUNDS:")
    for k in ("R144_information_loss", "R147_tracking_vs_serving",
              "R150_does_the_veto_do_anything"):
        if k in live:
            v = live[k]
            print(f"    {k:<38} artifact {len(v['artifact_consumers'])}  "
                  f"name {len(v['name_mentions'])}")

    # ---- VERDICT -------------------------------------------------------------------------------
    print()
    if a_share >= 0.50:
        print(f"  W-MOSTLY-INFRASTRUCTURE — {len(art_c)} of {len(live)} ({a_share:.0%}) have their")
        print(f"  ARTIFACT read by other code. The backfill denominator is materially smaller than")
        print(f"  it looked, and the corpus is largely a machine whose parts feed each other.")
        v = "W_MOSTLY_INFRASTRUCTURE"
    elif a_share <= 0.20:
        print(f"  W-MOSTLY-RESULTS — only {len(art_c)} of {len(live)} ({a_share:.0%}) have their")
        print(f"  artifact read. These are independent experiments, the denominator STANDS, and the")
        print(f"  debt is as large as it looked.")
        v = "W_MOSTLY_RESULTS"
    else:
        print(f"  W-SPLIT — {len(art_c)} of {len(live)} ({a_share:.0%}) are consumed as data and")
        print(f"  {len(name_only)} more are only CITED. Both counts are the estimate: the first is")
        print(f"  what must not be backfilled, the second is what a merged detector would have")
        print(f"  wrongly excused.")
        v = "W_SPLIT"

    print(f"\n  ⚠ THE BLIND SPOT BIASES THE ESTIMAND DOWNWARD. A consumer building its path")
    print(f"    dynamically is invisible, so the artifact count is a FLOOR — and the direction is")
    print(f"    the one that creates work rather than excuses it, which is the safer way to be")
    print(f"    wrong about a debt.")
    print(f"  ⚠ AND BEING READ IS NOT HAVING SOMETHING TO SAY. A consumed round is infrastructure;")
    print(f"    whether it ALSO had a finding is the question the debt is about, and this does not")
    print(f"    answer it.")

    art = dict(stamp(str(SELF)), head=head, n_sources=len(sources), n_population=len(live),
               artifact_consumed=art_c, name_mentioned=name_c, name_only=name_only,
               artifact_share=a_share, name_share=n_share, rows=rows,
               controls=dict(known=known_ok, pos_ok=pos_ok, neg_ok=neg_ok, channel_ok=chan_ok),
               verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r392_infrastructure_share.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
