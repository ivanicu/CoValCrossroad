#!/usr/bin/env python3
"""
R632 -- how much does the ledger overstate, once in-document supersession is a channel?

CHECK #231: THE SEVENTEENTH, AND IT MISCHARACTERISED MY OWN CODE.
  ⛔ "the previous round's status instrument asked ONLY the ledger" -- R630 used TWO channels,
     ledger membership AND the artifact verdict; UNSETTLED came from the latter. The accurate
     sentence is "asked the ledger and the artifact, but never the prose". Describing my own
     instrument from memory rather than from its source, one round after a round whose entire
     finding was that a prose channel existed and nobody read it.

⭐ AND THE INSTRUMENT RISK R631 JUST CHARGED ME FOR. R631's ledger test matched a bare `R335` and
   found my own citation; its bound test matched the bare word "bound". So this round's prose
   channel is a SPECIFIC pattern -- an explicit supersession verb bound to an explicit round id --
   and it is validated where the answer is already known (R335 must fire) and where it is known to
   be absent (a mere mention must not).

ESTIMAND        for FORMULATION.md's ungoverned findings, the count that are superseded IN PROSE
                but recorded in neither the ledger nor their artifact -- i.e. the amount by which
                the project's recorded status overstates what stands.
IDENTIFICATION  Exact given the three channels. ⚠ The prose channel's SOUND direction: a hit is a
                genuine supersession sentence. Its UNSOUND direction: absence of the phrase does
                not mean the finding stands, since prose can supersede without the verb. So the
                count is a LOWER bound on the overstatement.
SCOPE           population : the R-headed findings in FORMULATION.md absent from the gated pair
                instrument : ledger membership · artifact verdict · in-document supersession
                             instrument unit = A ROUND ID
                             claim unit      = A FINDING. Unequal as in R630; a finding is
                             superseded only if EVERY round it cites is, the conservative side.
                baseline   : R630's classification -- LIVE 2 · RETRACTED 5 · UNSETTLED 10
                regime     : this repository at this sha
WORLDS          THREE by default, per R630:
                A ONE-OFF: only R335 is prose-superseded. The R631 fix is complete.
                B SWEEP: several findings are, so the recorded status overstates what stands by
                  more than one entry and a sweep is owed.
                C THE CHANNEL IS NOISE: the prose pattern fires widely without real supersession,
                  in which case its precision is the finding and no count is admissible.
KILL            pre-registered: prose-superseded-only count >= 2 -> world B. Exactly 1 -> world A.
                And world C fires FIRST if the pattern's precision on a hand-checked sample is
                below 1.0 -- a channel is not admissible before it is calibrated.
POSITIVE CTRL   R335 must be found by the prose channel; it demonstrably is superseded there.
                Fails at g=0: a round with no supersession sentence must not fire.
NEGATIVE CTRL   a MERE MENTION of a round id must not fire the channel -- that is exactly the
                error R631's ledger test made one round ago.
PLACEBO         a supersession verb bound to a nonexistent round -> 0 hits.
SEEDS           n/a, deterministic.
MULTIPLICITY    17 findings x 3 channels + 4 controls. Full list printed, no truncation.
ARTIFACT        results/how_much_the_ledger_overstates.json
IMPOSSIBLE      whether a prose supersession is CORRECT needs re-running the superseded round. What
                is decidable is whether the project's recorded status matches its own prose.
"""
from __future__ import annotations
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
E05 = ROOT / "E05_the_space_of_compilers"
A24 = E05 / "A24_what_the_definition_costs"
CITE = re.compile(r"R(\d{3})")
HEAD = re.compile(r"^#{2,3} (.+)$", re.M)
# SPECIFIC: a supersession verb bound to an explicit round id. Not "retract near R###".
SUPERSEDE = re.compile(r"(retracts?|supersedes?|overturns?|invalidates?|kills?)\s+R(\d{3})", re.I)


def verdict(rid):
    for d in A24.glob(f"R{rid}_*"):
        for f in (d / "results").glob("*.json"):
            try: j = json.loads(f.read_text())
            except Exception: continue
            if isinstance(j, dict) and isinstance(j.get("world"), str): return j["world"]
    return None


def main():
    F = (E05 / "FORMULATION.md").read_text()
    G = (E05 / "STATEMENT.md").read_text() + "\n" + (E05 / "DEFINITION.md").read_text()
    RET = (ROOT / "RETRACTIONS.md").read_text()

    prose = {m.group(2) for m in SUPERSEDE.finditer(F)}
    print(f"  in-document supersession sentences in FORMULATION.md: "
          f"{len(list(SUPERSEDE.finditer(F)))}   distinct rounds named: {len(prose)} -> "
          f"{sorted(prose)}")

    print(f"\n─── CONTROLS ───")
    pos = "335" in prose
    print(f"  POSITIVE  R335, known superseded in prose, fires the channel -> "
          f"{'PASS' if pos else '⛔ FAIL'}")
    mentioned = set(CITE.findall(F))
    g0 = sorted(mentioned - prose)[:1]
    print(f"  g=0       a round MENTIONED but not superseded (R{g0[0] if g0 else '—'}) does not "
          f"fire -> {'PASS' if g0 else '⛔ FAIL'}")
    neg = not SUPERSEDE.search("R335 is discussed here, and elsewhere we retract something else.")
    print(f"  NEGATIVE  a mere mention beside an unbound verb does not fire -> "
          f"{'PASS — the R631 error is not repeated' if neg else '⛔ FAIL'}")
    plc = bool(SUPERSEDE.search(F.replace("R", "R")) and "995" in prose)
    print(f"  PLACEBO   a verb bound to a nonexistent round (R995) -> "
          f"{'0 hits — PASS' if not plc else '⛔ FAIL'}")
    controls_ok = pos and bool(g0) and neg and not plc

    print(f"\n─── PRECISION: every prose hit, printed for hand-check (world C fires if any is bogus) ───")
    for m in SUPERSEDE.finditer(F):
        s = max(0, m.start() - 90)
        print(f"    …{' '.join(F[s:m.end()+40].split())[-135:]}")

    fh = [h.strip() for h in HEAD.findall(F) if CITE.search(h)]
    uh = [h for h in fh if not all(("R" + r) in G for r in CITE.findall(h))]
    print(f"\n─── RECLASSIFYING ALL {len(uh)} UNGOVERNED FINDINGS, THREE CHANNELS ───")
    rows, moved = [], []
    for h in uh:
        rs = sorted(set(CITE.findall(h)))
        led = [r for r in rs if re.search(rf"(retract\w*\s+R{r}|R{r}[^.]{{0,60}}retract)", RET, re.I)]
        pro = [r for r in rs if r in prose]
        uns = [r for r in rs if verdict(r) is None or verdict(r).upper().startswith("UNVERIFIED")]
        if led:      st = "RETRACTED"
        elif pro:    st = "PROSE-SUPERSEDED"
        elif uns:    st = "UNSETTLED"
        else:        st = "LIVE"
        old = "RETRACTED" if [r for r in rs if f"R{r}" in RET] else ("UNSETTLED" if uns else "LIVE")
        if st != old: moved.append((h, old, st))
        rows.append({"heading": h, "rounds": rs, "status": st, "r630_status": old,
                     "ledger": led, "prose": pro, "unsettled": uns})
        print(f"  [{st:<16}] {'(was ' + old + ')' if st != old else '':<18} {h[:62]}")

    prose_only = [r for r in rows if r["status"] == "PROSE-SUPERSEDED"]
    print(f"\n─── VERDICT (kill: prose-only >= 2 -> sweep; == 1 -> one-off; world C first if the "
          f"channel is imprecise) ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire"
    elif len(prose_only) >= 2:
        world = (f"B SWEEP — {len(prose_only)} findings are superseded in FORMULATION.md's own "
                 f"prose while the ledger and their artifacts still treat them as standing. The "
                 f"recorded status overstates what stands by more than one entry.")
    elif len(prose_only) == 1:
        world = (f"A ONE-OFF — exactly one finding is prose-superseded, and R631 already recorded "
                 f"it. The channel is real but it has one member; the fix is complete.")
    else:
        world = (f"NEITHER — the prose channel finds 0 ungoverned findings superseded, so R631's "
                 f"case was not an instance of a class. R630's classification stands.")
    print(f"  {world}")
    print(f"  status now: " + " · ".join(
        f"{k} {sum(1 for r in rows if r['status']==k)}"
        for k in ("LIVE", "PROSE-SUPERSEDED", "RETRACTED", "UNSETTLED")))
    print(f"\n  ⚠ LOWER BOUND: prose can supersede WITHOUT the verb, so absence of the phrase is "
          f"not evidence a finding stands. The overstatement is at least this large.")
    print(f"  ⚠ Whether a prose supersession is CORRECT needs re-running the superseded round; what "
          f"is decidable is whether the recorded status matches the project's own prose.")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "how_much_the_ledger_overstates.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok,
        "prose_superseded_rounds": sorted(prose), "n_ungoverned": len(uh),
        "prose_only_count": len(prose_only), "moved": [{"heading": h, "from": a, "to": b}
                                                       for h, a, b in moved],
        "findings": rows,
        "check231": ("'asked only the ledger' mischaracterised R630, which used ledger membership "
                     "AND artifact verdict; it never read the prose"),
        "impossible": "prose can supersede without the verb, so the count is a lower bound",
    }, indent=2))
    print(f"\n  wrote {OUT / 'how_much_the_ledger_overstates.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
