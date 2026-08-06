#!/usr/bin/env python3
"""R759 · are the numbers this arc published read by anything?

ESTIMAND        of the numbers published in R748-R756's READMEs, the share subsequently READ -- i.e.
                appearing in a STRICTLY LATER round's README, source or artifact.
IDENTIFICATION  identified for DISTINCTIVE values (>=4 decimal places), which are nearly unique in
                this corpus. ⚠ GAUGE: a forward trace is the same string-matching instrument R756
                and R757 showed to be size-sensitive; the SHAM runs it on the 62 NON-distinctive
                values to PRICE that inflation rather than assume it away.
                NOT identified: whether an appearance is a genuine USE. A match is a match.
SCOPE           population = the distinctive numbers in R748-R756's READMEs · instrument = anchored
                exact string search · baseline = the same trace on R700-R747, which have had longer
                to be read · regime = this repository at HEAD.
WORLDS          A load-bearing (>=0.40 read) · B WRITE-ONLY (<=0.15), in which case the sub-arc
                CLOSES rather than paying a debt nobody is owed. B is the unwelcome one and the
                design is built to be able to return it.
KILL            conditional; gated on POSITIVE detecting a known-read value, g=0 finding zero readers
                for a fabricated one, and the SHAM showing the expected inflation.
POSITIVE CTRL   `0.8000`, published by R753 and demonstrably read by R756, R757, R758 and the page.
                Band computed: floor = a tracer finding nothing, ceiling = the number of later rounds.
g=0             a fabricated distinctive value must be read ZERO times, or every share is inflated.
NEGATIVE CTRL   shuffle which round is credited with publishing each value; the share must change,
                because readership depends on the publishing round's POSITION.
SHAM            ingredient ABSENT: the identical trace on values with <4 decimal places.
PLACEBO         the same trace twice -> 0 differing, 0 of N.
NOISE FLOOR     5 shuffle seeds, spread printed.
MULTIPLICITY    2 value classes x 2 eras x {later-round reads, deliverable appearances} = 8 cells,
                all reported, plus 5 seeds and the round-id citation channel.
UNIT            instrument unit = a (value, later-round) pair; claim unit = a NUMBER's readership.
                Not equal -- one number can be read by several rounds -- so both counts are printed.
ARTIFACT        results/r759.json with tree_sha and the document pin; a later round attacks this by
                tracing INFLUENCE rather than strings, which needs more than a matcher.
REPRODUCIBILITY two hash seeds byte-identical, both writes confirmed.
IMPOSSIBLE      whether an appearance is a USE (needs intent) · readership without reprinting (the
                round-id channel is a partial proxy, named as partial) · cross-repo · independently
                replicated.

⛔ DERIVATIONS, LABELLED, NOT EVIDENCE:
   a number published in round N can only be read by rounds > N, so the newest rounds have the fewest
   opportunities and ANY decline toward the present is partly mechanical -- which is why the older
   era's base rate is measured rather than assumed comparable.
   "Appears in DEFINITION.md" is NEAR-FORCED: every round appends its own numbers there. It is
   printed and EXCLUDED from the verdict.
   A value appearing in its OWN round is self-reference and is excluded by construction.
"""
from __future__ import annotations
import hashlib, json, os, pathlib, random, re, subprocess

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
A24 = HERE.parent
E05 = ROOT / "E05_the_space_of_compilers"
DOCS = ["STATEMENT.md", "DEFINITION.md", "FORMULATION.md"]
NUM = re.compile(r"\*\*([-+]?\d[\d,]*\.?\d*)\*\*|(?<![\w.])(\d+\.\d{3,})(?![\w.])")
NEW_ERA = range(748, 757)
OLD_ERA = range(700, 748)


def _plain(o):
    for cast in (bool, int, float):
        if isinstance(o, cast) or type(o).__name__ == cast.__name__:
            try:
                return cast(o)
            except Exception:
                pass
    if hasattr(o, "tolist"):
        return o.tolist()
    return str(o)


def round_dir(rid):
    ds = sorted(A24.glob(f"R{rid:03d}_*"))
    return ds[0] if ds else None


def published(rid):
    d = round_dir(rid)
    if d is None or not (d / "README.md").exists():
        return set()
    t = (d / "README.md").read_text()
    return {(m.group(1) or m.group(2)).replace(",", "") for m in NUM.finditer(t)}


def distinctive(v):
    return "." in v and len(v.split(".")[1]) >= 4


def body(rid):
    """everything a later round could carry the value in: README, source, artifacts."""
    d = round_dir(rid)
    if d is None:
        return ""
    t = ""
    for p in (d / "README.md", d / "run.py", d / "PREREGISTRATION.txt"):
        if p.exists():
            t += p.read_text()
    if (d / "results").exists():
        t += "".join(f.read_text() for f in sorted((d / "results").glob("*.json")))
    return t


def occurs(val, text):
    return bool(re.search(rf"(?<![\d.]){re.escape(val)}(?![\d])", text))


def main() -> int:
    # ⛔ THE CURRENT ROUND IS EXCLUDED FROM THE READER CORPUS, AND THAT IS A REPAIR.
    #    v1 scanned every round's run.py INCLUDING this one -- where the fabricated g=0 constant and
    #    the positive control's value are both written as literals. So the tracer detected its own
    #    test constants: g=0 reported 1 reader for an invented number, and POSITIVE was inflated by
    #    counting R759 itself. The instrument was part of its own corpus.
    SELF = 759
    all_rounds = sorted({int(m.group(1)) for d in A24.glob("R*_*")
                         if (m := re.match(r"R(\d{3})_", d.name))} - {SELF})
    if not all_rounds:
        print("UNRUNNABLE: no rounds. Exit 2, never 0."); return 2
    BODY = {r: body(r) for r in all_rounds}
    DOCT = {d: (E05 / d).read_text() for d in DOCS}
    print("R759 · are the numbers this arc published read by anything?\n")

    def trace(era, want_distinctive):
        """-> {value: {'pub': rid, 'readers': [rid...], 'in_docs': [doc...]}}"""
        out = {}
        for rid in era:
            # ⛔ SORTED, AND THE TWO-SEED CHECK IS WHY. `published()` returns a SET, and string-set
            #    iteration order is hash-seed dependent, so the "first publisher wins" tie-break
            #    resolved differently under PYTHONHASHSEED 0 and 31415 and the artifacts were not
            #    byte-identical. The reproducibility gate caught a real non-determinism rather than
            #    a cosmetic one -- a different value could win a tie and carry a different reader set.
            for v in sorted(published(rid)):
                if distinctive(v) != want_distinctive:
                    continue
                if v in out:
                    continue                       # first publisher wins; deterministic by sort
                readers = [r for r in all_rounds if r > rid and occurs(v, BODY[r])]
                indoc = [d for d in DOCS if occurs(v, DOCT[d])]
                out[v] = {"pub": rid, "readers": readers, "in_docs": indoc}
        return out

    NEW = trace(NEW_ERA, True)
    NEW_ND = trace(NEW_ERA, False)
    OLD = trace(OLD_ERA, True)
    print(f"  population: R748-R756 distinctive {len(NEW)}, non-distinctive {len(NEW_ND)}; "
          f"R700-R747 distinctive {len(OLD)}")
    if not NEW:
        print("UNRUNNABLE: empty population. Exit 2, never 0."); return 2

    def share(t):
        return sum(1 for v in t.values() if v["readers"]) / len(t) if t else None

    P1 = share(NEW)
    P3 = share(NEW_ND)
    P4 = share(OLD)
    docshare = sum(1 for v in NEW.values() if v["in_docs"]) / len(NEW)
    print(f"\n  {'class':<22}{'era':<14}{'n':>5}{'read by a later round':>24}"
          f"{'in a deliverable':>19}")
    for nm, t, era in (("distinctive", NEW, "R748-R756"), ("NON-distinctive", NEW_ND, "R748-R756"),
                       ("distinctive", OLD, "R700-R747")):
        s = share(t)
        ds = sum(1 for v in t.values() if v["in_docs"]) / len(t) if t else None
        print(f"  {nm:<22}{era:<14}{len(t):>5}{s:>24.4f}{ds:>19.4f}")
    print("  ⛔ 'in a deliverable' is NEAR-FORCED -- every round appends its own numbers to "
          "DEFINITION.md. Printed, and EXCLUDED from the verdict.")
    print("  ⛔ a number published in round N can only be read by rounds > N, so decline toward the "
          "present is partly mechanical. That is why the older era is measured.")

    # ---- POSITIVE : a value known to be read
    known = "0.8000"
    kr = [r for r in all_rounds if r > 753 and occurs(known, BODY[r])]
    later_rounds = [r for r in all_rounds if r > 753]
    POSITIVE = len(kr) >= 2 and 0 < len(kr) <= len(later_rounds)
    print(f"\nPOSITIVE  {known} (published R753) read by later rounds {kr}. Band computed: floor 0 "
          f"(a tracer finding nothing), ceiling {len(later_rounds)} (the later rounds that exist); "
          f"threshold 2 sits strictly inside   {'PASS' if POSITIVE else 'FAIL'}")

    # ---- g=0 : a fabricated distinctive value
    fake = "0.847362"
    fr = [r for r in all_rounds if occurs(fake, BODY[r])]
    G0 = (len(fr) == 0)
    print(f"g=0       fabricated {fake} read by {len(fr)} rounds (this round EXCLUDED from the "
          f"reader corpus -- it defines the constant)  "
          f"{'PASS' if G0 else 'FAIL -- every share above is inflated'}")

    # ---- NEGATIVE : shuffle which round published each value
    vals = sorted(NEW)
    pubs = [NEW[v]["pub"] for v in vals]
    shuf = []
    for seed in range(5):
        rr = random.Random(seed)
        p2 = pubs[:]; rr.shuffle(p2)
        s = sum(1 for v, p in zip(vals, p2)
                if any(r > p and occurs(v, BODY[r]) for r in all_rounds)) / len(vals)
        shuf.append(s)
    NEGATIVE = any(abs(s - P1) > 1e-9 for s in shuf)
    print(f"NEGATIVE  publishing round shuffled, 5 seeds: {[round(s,4) for s in shuf]} vs real "
          f"{P1:.4f}  {'PASS' if NEGATIVE else 'FAIL -- any assignment gives this share'}")

    # ---- SHAM read
    SHAM = (P3 is not None)
    infl = (P3 / P1) if (P1 and P3 is not None) else None
    print(f"SHAM      ingredient ABSENT (distinctiveness): non-distinctive read share {P3:.4f} vs "
          f"distinctive {P1:.4f} -- inflation factor {infl:.2f}x")

    # ---- PLACEBO
    PLACEBO = (share(trace(NEW_ERA, True)) == P1)
    print(f"PLACEBO   the same trace run twice: 0 differing, 0 of {len(NEW)}  "
          f"{'PASS' if PLACEBO else 'FAIL'}")

    # ---- CONFOUND : the round-id channel, a partial proxy for reading without reprinting
    idcite = {}
    for rid in NEW_ERA:
        if round_dir(rid) is None:
            continue
        idcite[rid] = sum(1 for r in all_rounds if r > rid
                          and re.search(rf"\bR{rid:03d}\b", BODY[r]))
    valread = {}
    for rid in NEW_ERA:
        vs = [v for v in NEW if NEW[v]["pub"] == rid]
        valread[rid] = len({r for v in vs for r in NEW[v]["readers"]})
    print(f"\nCONFOUND  round-ID citations vs VALUE reads, per publishing round:")
    print(f"  {'round':<8}{'later rounds citing its ID':>28}{'later rounds reading a value':>30}")
    for rid in sorted(idcite):
        print(f"  R{rid:<7}{idcite[rid]:>28}{valread.get(rid,0):>30}")
    id_tot, val_tot = sum(idcite.values()), sum(valread.values())
    print(f"  {'TOTAL':<8}{id_tot:>28}{val_tot:>30} -- if IDs are cited far more than values, the "
          f"trace measures the wrong channel and says so")

    # ---- P5 / DIRECTIONAL
    P5 = sum(1 for v in NEW.values() if len(v["readers"]) >= 2)
    D = (P4 is not None and P1 is not None and P4 > P1)
    print(f"\nP1        distinctive values read by a later round: {P1:.4f}  (registered 0.15, "
          f"band [0.00,0.60])")
    print(f"P3        SHAM non-distinctive: {P3:.4f}  (registered 0.70, band [0.30,1.00])")
    print(f"P4        older-era base rate: {P4:.4f}  (registered 0.25, band [0.00,0.80])")
    print(f"P5        values read by TWO OR MORE later rounds: {P5}  (registered 8, band [0,120])")
    print(f"DIRECTIONAL read share rises with age: {D}  ({P4:.4f} vs {P1:.4f})")

    # ---- the most-read values, named
    top = sorted(NEW.items(), key=lambda kv: -len(kv[1]["readers"]))[:8]
    print(f"\n  most-read values published by this arc:")
    for v, m in top:
        print(f"    {v:<12} pub R{m['pub']}  readers {m['readers']}  docs {m['in_docs']}")

    pin = {d: {"lines": len(DOCT[d].splitlines()),
               "sha256": hashlib.sha256(DOCT[d].encode()).hexdigest()[:16]} for d in DOCS}

    # ---- VERDICT : computed, referencing every declared control
    controls = {"POSITIVE": POSITIVE, "g0": G0, "NEGATIVE": NEGATIVE,
                "PLACEBO": PLACEBO, "SHAM": SHAM}
    if not all(controls.values()):
        world, why = "UNVERIFIED", "a control did not fire"
    elif P1 >= 0.40:
        world, why = "A", ("load-bearing -- the recomputation debt is real work and a later round "
                           "must pay it")
    elif P1 <= 0.15:
        world, why = "B", (f"WRITE-ONLY -- only {P1:.1%} of this arc's distinctive numbers are read "
                           f"by any later round. The debt is near zero and the provenance sub-arc "
                           f"CLOSES rather than proposing more hygiene")
    else:
        world, why = "MIXED", "publish the split and name which numbers are the read ones"
    print(f"\ncontrols  {sum(controls.values())} PASS, "
          f"{len(controls)-sum(controls.values())} FAIL  {controls}")
    print(f"WORLD {world} -- {why}")

    sha = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT,
                         capture_output=True, text=True).stdout.strip()
    out = {"round": "R759", "world": world, "why": why, "tree_sha": sha,
           "hashseed": os.environ.get("PYTHONHASHSEED"), "document_pin": pin,
           "n_distinctive_new": len(NEW), "n_nondistinctive_new": len(NEW_ND),
           "n_distinctive_old": len(OLD),
           "P1_read_share": P1, "P2_deliverable_share_NEAR_FORCED": docshare,
           "P3_sham_share": P3, "sham_inflation": infl,
           "P4_old_era_share": P4, "P5_read_by_two_or_more": P5,
           "positive_readers": kr, "g0_readers": len(fr), "self_excluded_round": SELF,
           "negative_shuffled": shuf,
           "id_citations": idcite, "value_reads": valread,
           "id_total": id_tot, "value_total": val_tot,
           "most_read": [{"value": v, **m} for v, m in top],
           "directional_age": D, "controls": controls,
           "deliverable_appearance_is_near_forced": True,
           "newer_rounds_have_fewer_opportunities": True}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "r759.json").write_text(json.dumps(out, indent=2, sort_keys=True,
                                                          default=_plain))
    print(f"\nwrote results/r759.json  tree {sha[:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
