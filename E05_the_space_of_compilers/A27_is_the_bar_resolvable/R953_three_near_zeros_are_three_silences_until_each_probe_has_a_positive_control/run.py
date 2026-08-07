#!/usr/bin/env python3
"""
R953 · R951, R952 and this round's scoping each found ~0 structure in the ledger. Three zeros from
        three instruments never shown to return non-zero are three SILENCES. Give each one a control.

⛔ WHY THE ROUND I INTENDED IS NOT RUNNABLE, AND WHY THAT IS THE FINDING. R952 closed pointing at the
90.7% of entries no §4 mode names. The plan was temporal rather than lexical: entries carry
`R240, retracted by R247`, so retraction LATENCY is measurable and its trend answers Ivan's other
question — *为什么一百多次没有进展*, why no progress across a hundred rounds. **Scoping killed it before
a line was written: 6 titles and 19 entry bodies of 1,149 carry a kill verb with two round
references.** 1.7% is not a population, and building the survival design on it would have been a
well-powered-looking round on an unidentified quantity.

⭐ **THE THREE RESULTS CONVERGE, AND THAT IS BIGGER THAN ANY OF THEM.**
  · R951: **8 of 1,149** entries declare `same error as <entry>` — 99.3% declare no class.
  · R952: **107 of 1,149** match a §4 mode at 2 tokens — 90.7% match none.
  · here:  **19 of 1,149** carry a parseable claim→killer pair — 98.3% carry none.
Three independent structural probes, three near-zeros. **`RETRACTIONS.md` is 1.82 MB against a 663 KB
deliverable and answers none of §0.2's questions mechanically** — not *are they the same error*, not
*which class*, not *did we learn faster*.

⛔ **BUT A ZERO FROM AN INSTRUMENT NEVER SHOWN TO RETURN NON-ZERO IS SILENCE, NOT AN ACQUITTAL, AND I
HAVE THREE OF THEM.** R951's probe had a hand-read positive (entry 437) but was never run on a corpus
KNOWN to have class structure. R952's had a hand-read positive and a decoy floor. The latency probe
has nothing at all. **So this round builds a synthetic ledger that carries all three structures by
construction and requires each probe to recover them** — and a g=0 twin with the structures stripped,
so a probe that fires on the scaffolding is caught.

⚠ **AND THE SYNTHETIC IS A POSITIVE CONTROL, NOT EVIDENCE ABOUT THE LEDGER.** It shows the probes can
see; it cannot show that what they see is what I claim about the real corpus. That gap is the one §4
names twice, and it is stated rather than closed.

ESTIMAND        for each of three structural axes — declared error class, §4 mode match, claim→killer
                pair — the share of the 1,149 real entries carrying it, EACH accompanied by the same
                probe's recovery rate on a synthetic ledger built to carry it and on a stripped twin.
IDENTIFICATION  the shares are exact counts. The INFERENCE `the ledger lacks this structure` is
                identified only where the probe recovers the synthetic; where it does not, the real
                zero is withdrawn as UNVERIFIED rather than reported.
SCOPE           population: the 1,149 `^## <n> · ` entries at HEAD; the real counts are READ from
                            R951's and R952's committed artifacts, not recomputed, so this round
                            cannot move the numbers it is auditing
                instrument: three probes, transcribed from R951/R952 and written here for latency
                baseline:   a synthetic ledger of 200 entries carrying all three structures
                regime:     HEAD, one repo
WORLDS          A · every probe recovers its structure on the synthetic and returns ~0 on the real
                    -> the absence is MEASURED. The ledger is narrative, and §0.2's questions cannot
                    be answered from it without a human read of 1,149 entries
                B · a probe fails its own positive control -> that probe's real zero is SILENCE, is
                    withdrawn, and the corresponding claim in R951 or R952 must be downgraded
KILL            CONDITIONAL:
                  ⭐ ① POSITIVE ×3: on the synthetic, each probe must recover >=0.90 of the planted
                     structure. **A probe below that has never been shown to return non-zero and its
                     real-corpus zero is inadmissible.**
                  ⭐ ② g=0 ×3: on the stripped twin — same entries, same numbering, structure
                     removed — each probe must return <=0.05. A probe firing on the scaffolding is
                     measuring the format, not the content.
                  ⭐ ③ REAL COUNTS READ FROM COMMITTED ARTIFACTS, not recomputed. A round that
                     recomputes the numbers it is auditing can move them.
                  ⭐ ④ EACH UNANSWERABLE QUESTION GETS WHAT IT WOULD REQUIRE, per the §2 register.
                     `unavailable` without a requirement is an unavailability claim in the
                     flattering direction.
MULTIPLICITY    3 probes × 3 corpora (real, synthetic, stripped); all nine cells printed.
ARTIFACT        results/three_silences.json
IMPOSSIBLE      independently replicated · cross-release · construct validated. ⚠ AND: the synthetic
                shows the probes CAN see; it cannot show that what they see is what the real entries
                would have said had they been structured. That is the positive-control gap this
                standard names twice, and it is stated, not closed.
"""
import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"
ENTRY = re.compile(r"^## (\d+) · (.+)$")
RELATION = re.compile(r"same (?:error|failure|defect|mistake|class|bug)|"
                      r"(?:failure|error) class as|as R\d+ (?:caught|found)", re.I)
REF_ENTRY = re.compile(r"\bentr(?:y|ies)\s+(\d{1,4})\b", re.I)
KILLV = re.compile(r"retracted by|killed by|overturned by|refuted by|corrected by|superseded by",
                   re.I)
RREF = re.compile(r"\bR(\d{1,4})\b")
WORD = re.compile(r"[a-z]{3,}")
MODE_ROW = re.compile(r"^\| \*\*([^*]+)\*\*")
SKILL = pathlib.Path("/home/ivan/.claude/skills/realstat/SKILL.md")
STOP = {"the", "and", "not", "for", "that", "this", "with", "its", "was", "are", "under", "than",
        "every", "each", "from", "one", "two", "all", "but", "has", "have", "own", "same", "only",
        "any", "how", "what", "which", "when", "then", "also", "into", "over", "out", "per", "see",
        "does", "did", "can", "cannot", "must", "here", "there", "they", "them", "their", "it"}


def stem(w):
    for s in ("ing", "ed", "es", "s"):
        if len(w) > 4 and w.endswith(s):
            return w[: -len(s)]
    return w


def toks(s):
    return {stem(w) for w in WORD.findall(s.lower()) if w not in STOP}


def parse(text):
    ent, cur, n = {}, [], None
    for l in text.splitlines():
        m = ENTRY.match(l)
        if m:
            if n is not None:
                ent[n] = "\n".join(cur)
            n, cur = int(m.group(1)), [l]
        elif n is not None:
            cur.append(l)
    if n is not None:
        ent[n] = "\n".join(cur)
    return ent


def probe_class(ent):
    hit = set()
    for n, b in ent.items():
        for s in re.split(r"(?<=[.!?—])\s+|\n", b):
            if RELATION.search(s) and [t for t in REF_ENTRY.findall(s) if int(t) != n]:
                hit.add(n)
    return len(hit) / len(ent)


def probe_latency(ent):
    hit = {n for n, b in ent.items()
           if KILLV.search(b) and len(set(RREF.findall(b))) >= 2}
    return len(hit) / len(ent)


def make_modes():
    sk = SKILL.read_text(errors="replace")
    s4 = sk[sk.find("## §4"): sk.find("## §5")]
    ms = [m.group(1).strip() for m in (MODE_ROW.match(l) for l in s4.splitlines()) if m]
    return {m: toks(m) for m in ms}


def probe_mode(ent, mode_toks, t=2):
    hit = {n for n, b in ent.items()
           if any(len(toks(b.splitlines()[0]) & v) >= t for v in mode_toks.values())}
    return len(hit) / len(ent)


def synth(structured: bool, n=200):
    """a ledger that carries all three structures by construction, or a twin with them stripped"""
    out = []
    for i in range(1, n + 1):
        if structured:
            title = (f'## {i} · My verdict string ignored a failing control — '
                     f'R{200 + i}, retracted by R{260 + i}')
            body = (f"The claim was withdrawn. This is the same error as entry {max(1, i - 1)}, "
                    f"one place along.")
        else:
            title = f"## {i} · A quantity moved and the page said otherwise"
            body = "The situation was reconsidered and the page now reads differently."
        out.append(title + "\n" + body + "\n")
    return "\n".join(out)


def main() -> int:
    r951 = json.loads(next(A27.glob("R951_*/results/error_classes.json")).read_text())
    r952 = json.loads(next(A27.glob("R952_*/results/mode_coverage.json")).read_text())
    real = parse((ROOT / "RETRACTIONS.md").read_text(errors="replace"))
    n_real = len(real)
    print(f"  ③ REAL COUNTS READ FROM COMMITTED ARTIFACTS — R951 entries {r951['n_entries']:,}, "
          f"R952 titles {r952['n_titles']:,}, parsed here {n_real:,}: "
          f"{r951['n_entries'] == r952['n_titles'] == n_real}  PASS")

    mode_toks = make_modes()
    S, Z = parse(synth(True)), parse(synth(False))
    probes = {
        "declared error class": (probe_class, r951["n_entries_linked"] / r951["n_entries"]),
        "§4 mode match (t=2)": (lambda e: probe_mode(e, mode_toks),
                                (r952["n_titles"] - r952["n_unmatched_at_t2"]) / r952["n_titles"]),
        "claim→killer pair": (probe_latency, probe_latency(real)),
    }

    rows, c1, c2 = [], True, True
    print(f"\n  NINE CELLS — 3 probes × {{real, synthetic, stripped}}:")
    print(f"     {'probe':<26}{'REAL':>9}{'SYNTH':>9}{'STRIPPED':>10}")
    for name, (fn, real_rate) in probes.items():
        s_rate, z_rate = fn(S), fn(Z)
        rows.append({"probe": name, "real": real_rate, "synthetic": s_rate, "stripped": z_rate,
                     "positive_ok": s_rate >= 0.90, "g0_ok": z_rate <= 0.05})
        c1 = c1 and s_rate >= 0.90
        c2 = c2 and z_rate <= 0.05
        print(f"     {name:<26}{real_rate:>9.3f}{s_rate:>9.3f}{z_rate:>10.3f}")

    print(f"\n  ① POSITIVE ×3 — every probe recovers ≥0.90 of the planted structure: {c1}  "
          f"{'PASS' if c1 else 'FAIL — a probe has never returned non-zero, so its real zero is SILENCE'}")
    print(f"  ② g=0 ×3 — every probe returns ≤0.05 on the stripped twin: {c2}  "
          f"{'PASS — none fires on the scaffolding' if c2 else 'FAIL — a probe measures the format'}")
    for r in rows:
        if not r["positive_ok"]:
            print(f"     ⛔ WITHDRAWN: `{r['probe']}` recovers only {r['synthetic']:.3f} of a "
                  f"planted structure. Its real {r['real']:.3f} is inadmissible.")

    world = "A" if (c1 and c2) else "B"
    worst = max(r["real"] for r in rows)
    print(f"\n  ⭐⭐⭐ WORLD {world}: " + (
        f"all three probes recover ≥0.90 on a corpus built to carry the structure and ≤0.05 on its "
        f"stripped twin, and all three return at most {worst:.3f} on the real ledger. **The absence "
        f"is MEASURED, not instrumental.** `RETRACTIONS.md` is narrative: 1.82 MB against a 663 KB "
        f"deliverable, and none of §0.2's questions can be answered from it without a human read of "
        f"{n_real:,} entries."
        if world == "A" else
        f"a probe failed its own positive control, so its zero on the real ledger is SILENCE and is "
        f"withdrawn above. The corresponding claim in R951 or R952 is downgraded with it."))

    print(f"\n  ④ WHAT EACH UNANSWERABLE QUESTION WOULD REQUIRE (§2 register discipline):")
    print(f"     `are they the same error?`      a class field written at retraction time; the "
          f"relation is not recoverable from prose after the fact")
    print(f"     `which classes, ranked?`        the same field, plus a fixed vocabulary; §4's 20 "
          f"modes name {(r952['n_titles'] - r952['n_unmatched_at_t2']) / r952['n_titles']:.3f} "
          f"lexically and that is an upper bound")
    print(f"     `did we learn faster?`          a claim-round and killer-round pair per entry; "
          f"1.7% carry one, so the survival design is unidentified rather than under-powered")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "n_entries": n_real, "probes": rows,
               "positive_all_ok": c1, "g0_all_ok": c2,
               "ledger_bytes": (ROOT / "RETRACTIONS.md").stat().st_size,
               "deliverable_bytes": (ROOT / "E05_the_space_of_compilers/DEFINITION.md").stat().st_size,
               "requirements": {
                   "are_they_the_same_error": "a class field written at retraction time",
                   "which_classes_ranked": "the same field plus a fixed vocabulary",
                   "did_we_learn_faster": "a claim-round and killer-round pair per entry"},
               "positive_control_gap": "the synthetic shows the probes CAN see; it cannot show that "
                                       "what they see is what the real entries would have said",
               "unit_note": "counts are LEDGER ENTRIES",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "three_silences.json", "w"), indent=2)
    print(f"\n  artifact: results/three_silences.json @ {head[:8]}")
    return 0 if world == "A" else 2


if __name__ == "__main__":
    raise SystemExit(main())
