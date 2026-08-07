"""R391 -- the three silent rounds: are they STEPS another round consumes, or orphans?

R390 ran 8 of the 68 untitled rounds. Five state a verdict in their output; three do not --
R144_information_loss, R147_tracking_vs_serving and R150_does_the_veto_do_anything. Those three are
the first population in this line whose honest disposition might be "no finding" rather than
"unwritten finding", and the two dispositions demand opposite actions:

  · a STEP -- a computation a later round consumes -- is INFRASTRUCTURE. Marking it "no finding"
    would retract work that was never wrong, and writing a finding for it would invent a result for
    a script never asked to produce one.
  · an ORPHAN -- consumed by nothing, stating nothing -- is neither, and saying so is the finding.

⛔ THE INSTRUMENT IS A SEARCH, SO IT GETS A CONTROL WITH AN ANSWER I DID NOT PRODUCE HERE. "Grep the
   corpus for anything that reads their artifacts" is exactly the class this campaign has been burned
   by four times. The control is a consumption edge established EARLIER, by a different round, for a
   different purpose: R371 reads R370's `sat_genericpool16_fresh.npz`, and R372 reads R371's
   `r371_power.json`. Those edges exist in committed code and were built before this question was
   asked, so the detector must find them or every zero it reports below is silence.

⛔ ARITHMETIC TRAP, answered before the run. Could this come out otherwise? YES. An artifact is free
   to be read by many rounds, by one, or by none, and the corpus contains 400+ scripts either way.
   ⚠ What IS forced and is excluded: a round trivially "reads" its OWN artifact -- it writes it. Self
   references are removed before any count, or every round would score as its own consumer.

ESTIMAND        for each of the three silent rounds: the number of OTHER rounds whose source names
                its artifact file or its directory. Reported per round with the consumers named,
                never as a bare count.

IDENTIFICATION  Exact for references reachable by a literal string search of committed source. NOT
                identified: a consumer that builds the path dynamically, or that reads the artifact
                through a helper. That is a real blind spot and it biases toward ORPHAN, which is
                the flattering direction for a round that wants to close a question -- so it is
                named here and repeated in the verdict.

SCOPE           population: 3 silent rounds x every run.py in the corpus · instrument: literal
                substring search over committed source · baseline: two known consumption edges ·
                regime: HEAD.

WORLDS
  W-STEPS       all three are consumed. They are infrastructure; mark them as such and do not
                backfill. The debt shrinks by three and the reason is recorded.
  W-ORPHANS     none is consumed. They state nothing and nothing uses them -- the honest disposition
                is "no stated finding, no downstream consumer", which is a fact about the corpus and
                not a defect in the rounds.
  W-MIXED       some of each, and the per-round answer is the finding rather than the share.

PREDICTION MATRIX
  W-STEPS   -> every one has >= 1 external consumer
  W-ORPHANS -> all three have 0
  W-MIXED   -> between, named per round

PRE-REGISTERED KILL -- conditional on the control, never on the counts alone.
    if the detector finds BOTH known edges:
        c = number of the three with >= 1 external consumer
        if c == 3 -> W-STEPS ; elif c == 0 -> W-ORPHANS ; else -> W-MIXED, named per round
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

CONTROLS
  DETECTOR (+)  two consumption edges committed BEFORE this question existed -- R370 -> R371 and
                R371 -> R372 -- must both be found. Their answer comes from those rounds, not here.
  DETECTOR (-)  a filename that exists nowhere must return zero consumers, so that zero is shown to
                be attainable rather than assumed.
  SELF          a round's own source is excluded from its own consumer set. Otherwise every round
                is its own consumer and the measure is vacuous.
  EMPTY         if fewer than 100 source files are searched, exit 2 -- a zero over a lost corpus is
                the failure this whole line is about.

MULTIPLICITY    3 rounds x 2 reference forms, every hit printed with its consumer named.
SEEDS           none -- static search.
ARTIFACT        results/r391_step_or_orphan.json with the source hash.

IMPOSSIBLE HERE
  dynamically-built paths  -- invisible to a literal search, and the bias is toward ORPHAN, which is
                              the flattering direction. Named, not waved at.
  whether a consumed round HAD a finding -- being useful and stating a finding are different, and
                              only the second is what the backfill debt is about.
  a second release         -- one release.

EXIT
    0  the control holds and the three are classified
    1  the control failed -- UNVERIFIED
    2  the corpus is too small to search -- never a silent pass
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
SILENT = ("R144_information_loss", "R147_tracking_vs_serving", "R150_does_the_veto_do_anything")
KNOWN_EDGES = (("sat_genericpool16_fresh.npz", "R371"), ("r371_power.json", "R372"))
NOWHERE = "zzq_no_such_artifact_zzq.json"
sys.path.insert(0, str(ROOT / "covalx"))
try:
    from stamp import stamp
except Exception:
    def stamp(f):
        return {"source_sha256": hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest(),
                "source_name": pathlib.Path(f).name}


def main() -> int:
    sources = {}
    for p in sorted(ROOT.glob("E0*/A*/R*/*.py")):
        if HERE in p.parents:
            continue
        try:
            sources[p] = p.read_text()
        except Exception:
            continue
    for p in sorted(ROOT.glob("assurance/*.py")) + sorted(ROOT.glob("covalx/*.py")):
        try:
            sources[p] = p.read_text()
        except Exception:
            continue
    if len(sources) < 100:
        print(f"  UNRUNNABLE: only {len(sources)} source files searched. Exit 2, never 0."); return 2

    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True,
                          text=True).stdout.strip()[:12]
    print(f"R391 · step or orphan?   HEAD {head}\n")
    print(f"  {len(sources)} source files searched (round sources + assurance + covalx)\n")

    def consumers(token: str, exclude_dir: pathlib.Path | None):
        out = []
        for p, txt in sources.items():
            if exclude_dir is not None and exclude_dir in p.parents:
                continue
            if token in txt:
                out.append(str(p.relative_to(ROOT)))
        return sorted(out)

    # ---- CONTROLS ------------------------------------------------------------------------------
    found = {}
    for tok, expect in KNOWN_EDGES:
        cs = consumers(tok, None)
        found[tok] = [c for c in cs if expect in c]
    pos_ok = all(found[t] for t, _ in KNOWN_EDGES)
    neg = consumers(NOWHERE, None)
    neg_ok = (len(neg) == 0)
    print(f"  CONTROLS on the consumption detector")
    for tok, expect in KNOWN_EDGES:
        print(f"    DETECTOR (+)  `{tok}` is read by {expect}: "
              f"{bool(found[tok])}   {found[tok][:1]}")
    print(f"                  both edges were committed BEFORE this question existed  "
          f"{'PASS' if pos_ok else 'FAIL — every zero below would be silence'}")
    print(f"    DETECTOR (-)  a filename that exists nowhere has {len(neg)} consumers  "
          f"{'PASS' if neg_ok else 'FAIL'}")
    if not (pos_ok and neg_ok):
        print("\n  UNVERIFIED — the detector is blind in one direction. Exit 1."); return 1

    # ---- the three ------------------------------------------------------------------------------
    print(f"\n  THE THREE SILENT ROUNDS — consumers named, never counted alone")
    rows = {}
    for name in SILENT:
        d = next((q for q in ROOT.glob(f"E0*/A*/{name}") if q.is_dir()), None)
        if d is None:
            rows[name] = dict(present=False); print(f"    {name:<38} ABSENT"); continue
        arts = sorted(f.name for f in (d / "results").glob("*")) if (d / "results").is_dir() else []
        cs = set()
        for a in arts:
            cs.update(consumers(a, d))
        cs.update(consumers(name, d))
        rows[name] = dict(present=True, artifacts=arts, consumers=sorted(cs))
        print(f"    {name:<38}{len(cs):>3} consumer(s)   artifacts: {arts}")
        for c in sorted(cs)[:4]:
            print(f"        <- {c}")
    live = {k: v for k, v in rows.items() if v.get("present")}
    consumed = [k for k, v in live.items() if v["consumers"]]

    # ---- VERDICT -------------------------------------------------------------------------------
    print()
    if len(consumed) == len(live) and live:
        print(f"  W-STEPS — all {len(live)} are consumed by other rounds. They are INFRASTRUCTURE:")
        print(f"  marking them `no finding` would retract work that was never wrong, and writing a")
        print(f"  finding for them would invent a result for a script never asked to produce one.")
        print(f"  The backfill debt shrinks by {len(live)}, and the reason is recorded rather than")
        print(f"  the count merely reduced.")
        v = "W_STEPS"
    elif not consumed:
        print(f"  W-ORPHANS — none of the {len(live)} is read by any other round, and none states a")
        print(f"  verdict. The honest disposition is `no stated finding, no downstream consumer` —")
        print(f"  a fact about the corpus, not a defect in the rounds, and not something a")
        print(f"  backfilled paragraph can repair.")
        v = "W_ORPHANS"
    else:
        print(f"  W-MIXED — {len(consumed)} of {len(live)} are consumed: {consumed}.")
        print(f"  The per-round answer IS the finding: the consumed ones are infrastructure and the")
        print(f"  rest are orphans, and a single share over three rounds would say less than the")
        print(f"  three names do.")
        v = "W_MIXED"

    print(f"\n  ⚠ THE BLIND SPOT BIASES TOWARD ORPHAN, which is the flattering direction for a round")
    print(f"    that wants to close a question. A consumer building its path dynamically, or reading")
    print(f"    through a helper, is invisible to a literal search — so `0 consumers` is a bound on")
    print(f"    what this instrument can see, never a proof that nothing reads it.")
    print(f"  ⚠ AND BEING USEFUL IS NOT STATING A FINDING. A consumed round is infrastructure; that")
    print(f"    says nothing about whether it also had something to report.")

    art = dict(stamp(str(SELF)), head=head, n_sources=len(sources), rows=rows,
               consumed=consumed,
               controls=dict(known_edges={t: found[t] for t, _ in KNOWN_EDGES},
                             pos_ok=pos_ok, nowhere_consumers=len(neg), neg_ok=neg_ok),
               verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r391_step_or_orphan.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
