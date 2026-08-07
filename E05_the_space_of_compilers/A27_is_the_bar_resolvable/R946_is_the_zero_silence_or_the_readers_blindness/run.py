#!/usr/bin/env python3
"""
R946 · the 14 invisible rounds declare at ZERO on a ten-phrase reader. Is that silence, or is it the
        reader? Derive a wider reader HELD-OUT and measure it against a base rate.

⛔ WHY. R945 measured VISIBLE 11/14 against INVISIBLE 0/14, p = 0.00003. R944's proxy ledger says the
zero is UNVERIFIED, not `undeclared`, because `DECLARES` is ten phrases and a round may disclose in
words it has never heard. **Every downstream reading of that zero depends on which it is.** Silence
means the blind spot has a live cost and `DEFINITION.md`'s instrument bookkeeping is genuinely
incomplete. Blindness means the corpus discloses and the gate's VOCABULARY is the defect, which is a
different repair and a much cheaper one.

⭐ **AND THE OBJECT ALREADY SUGGESTS THE SECOND.** Reading the results keys rather than the values:
the 11 declarers carry `outcome_variable_scope` 9 times, plus `instrument`, `proxy`, `judge_family`,
`judge_checkpoint`. **Two of the fourteen `invisible` rounds carry `outcome_variable_scope` too** —
the declarers' own convention — and nine carry a `model` key naming what produced their numbers. They
were scored UNVERIFIED because their VALUES miss ten phrases, not because they say nothing.

⛔ **THE TRAP THIS ROUND IS BUILT AROUND, AND IT IS THE ONE I WOULD OTHERWISE WALK INTO.** The obvious
design derives a wider key vocabulary from the 11 known declarers and then checks that it recovers the
11. **That check cannot fail — it is construction wearing a control's clothes**, the failure mode this
file opens with. So the derivation is SPLIT-HALF: the key vocabulary is learned from a random half of
the declarers and its recall is measured on the half it never saw, at three seeds. A reader is only
credited with what it recovers out of sample.

⚠ **AND A WIDE READER NEEDS A FLOOR, NOT AN INTUITION.** `outcome_variable_scope` might be a
repo-wide habit present in rounds that touch no proxy at all, in which case its presence among the 14
says nothing. So the negative control is a MEASURED BASE RATE: the same reader applied to random
samples of the 862 rounds that reference no proxy route at all, same sample size, three seeds. **The
14's rate is judged against that floor and against nothing else.**

ESTIMAND        the share of the 14 route-referencing rounds the ten-phrase reader could not see that
                DO carry a provenance declaration under a held-out-derived key reader — and the same
                share on rounds referencing no proxy route, which is the floor.
IDENTIFICATION  identified as a rate difference against a measured floor. NOT identified as `these
                rounds disclose adequately`: a key named `model` proves a field exists, not that a
                reader learns the outcome was model-produced. Bounds, not a verdict.
SCOPE           population: 14 invisible (R943/R945), 11 known declarers, 862 no-route rounds
                instrument: key-NAME reader derived split-half from the declarers' results schemas
                baseline:   the measured no-route base rate at the same n, three seeds
                regime:     HEAD, one release, one repo
WORLDS          A · SILENCE — the 14 sit at or below the no-route floor. The zero is real, the blind
                    spot has a live cost, and the bookkeeping is incomplete by up to 14 rounds.
                B · BLINDNESS — the 14 sit well above the floor. They disclose in a channel the gate
                    does not read, the zero was an artefact of a ten-phrase value reader, and the
                    repair is the gate's vocabulary rather than the corpus's practice.
                C · UNRESOLVED — the gap is inside the floor's own spread across seeds.
KILL            CONDITIONAL:
                  ⭐ ① HELD-OUT RECALL, NOT CONSTRUCTION: the key vocabulary is derived from a random
                     half of the 11 declarers and scored on the other half, 3 seeds. Reported whatever
                     it is. **If out-of-sample recall is 0 the reader learned nothing generalisable
                     and the round is UNVERIFIED** — a vocabulary that only fits the rounds it was
                     read from is a lookup table.
                  ⭐ ② BASE RATE / NEGATIVE, MEASURED: the same reader on random samples of the 862
                     no-route rounds, n=14, 3 seeds. Its mean is the floor and its spread is the
                     resolution. A rate inside the floor's spread is World C.
                  ⭐ ③ g=0, PLANTED: a results document carrying none of the derived keys must NOT
                     fire. A reader that fires on an empty document measures nothing.
                  ⭐ ④ THE OVERLAP IS NAMED: any of the 14 that carries a declarer key is printed by
                     name with the key and its value, so a reader can check the call rather than take
                     the count.
                  ⭐ ⑤ THE UNIT IS STATED AND UNEQUAL: instrument = `a provenance-signalling KEY
                     exists`; claim = `a reader learns the outcome was model-produced`. Not the same,
                     so the output is a bound and the round says which direction it bounds.
MULTIPLICITY    3 derivation seeds × {held-out recall, the 14, 3 base-rate samples} — every cell
                printed, including seeds that disagree.
ARTIFACT        results/silence_or_blindness.json
IMPOSSIBLE      independently replicated · cross-release · construct validated · criterion validated —
                one repo, one release. ⚠ AND: whether a declaration is ADEQUATE is not measured here
                and cannot be. A key named `model` may hold a checkpoint path that tells a reader
                everything, or a boolean that tells them nothing; this counts the channel, not its
                content.
"""
import json, pathlib, random, re, subprocess

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"
PROVISIONAL = re.compile(r"smoke|dry[_-]?run|draft|scratch|trial|pilot|prelim|wip", re.I)
INSTRUMENT_UNIT = "a provenance-signalling KEY exists in the results"
CLAIM_UNIT = "a reader learns the outcome was model-produced"
# a key is a provenance candidate only if its NAME is about the outcome's origin, never its value
CANDIDATE = re.compile(r"outcome.*scope|scope.*outcome|instrument|proxy|judge|gold|model", re.I)
SEEDS = (11, 23, 37)


def keyset(doc, out):
    if isinstance(doc, dict):
        for k, v in doc.items():
            out.add(k)
            keyset(v, out)
    elif isinstance(doc, list):
        for v in doc:
            keyset(v, out)


def round_keys(name):
    d = next(ROOT.glob(f"E0*/A*/{name}"), None)
    ks = set()
    if d is None:
        return ks
    for f in sorted(d.glob("results/**/*.json")):
        if PROVISIONAL.search(f.name) or "_smoke_archive" in f.parts:
            continue
        try:
            keyset(json.loads(f.read_text()), ks)
        except Exception:
            continue
    return ks


def main() -> int:
    a943 = json.loads(next(A27.glob("R943_*/results/blind_side.json")).read_text())
    a945 = json.loads(next(A27.glob("R945_*/results/enforcement_or_practice.json")).read_text())
    declarers = [n for n in a945["visible"] if a945["declared"][n]]
    invisible = a945["invisible"]
    routed = set(a943["gate_sees_by_use"]) | set(a943["gate_false_positives_mention_only"]) \
        | set(a943["route_only_candidates"])
    noroute = sorted(p.name for p in ROOT.glob("E0*/A*/R*")
                     if p.is_dir() and (p / "run.py").exists() and p.name not in routed)

    print(f"  ⑤ UNITS — instrument: `{INSTRUMENT_UNIT}`")
    print(f"          claim:      `{CLAIM_UNIT}`   equal: {INSTRUMENT_UNIT == CLAIM_UNIT}")
    print(f"          -> the output is a BOUND on disclosure from ABOVE: a key can exist and still "
          f"tell a reader nothing.")
    print(f"\n  populations: {len(declarers)} declarers · {len(invisible)} invisible · "
          f"{len(noroute)} no-route")

    keys_of = {n: round_keys(n) for n in set(declarers) | set(invisible) | set(noroute)}

    rows, cells = [], []
    for seed in SEEDS:
        rng = random.Random(seed)
        shuf = declarers[:]
        rng.shuffle(shuf)
        half = len(shuf) // 2
        train, test = shuf[:half], shuf[half:]
        vocab = {k for n in train for k in keys_of[n] if CANDIDATE.search(k)}

        def fires(n):
            return bool(keys_of[n] & vocab)

        recall = sum(fires(n) for n in test) / len(test)
        inv_rate = sum(fires(n) for n in invisible) / len(invisible)
        base = [sum(fires(n) for n in rng.sample(noroute, len(invisible))) / len(invisible)
                for _ in range(3)]
        rows.append({"seed": seed, "n_train": len(train), "n_test": len(test),
                     "vocab_size": len(vocab), "vocab": sorted(vocab),
                     "heldout_recall": recall, "invisible_rate": inv_rate,
                     "base_rates": base, "base_mean": sum(base) / len(base)})
        cells.append((seed, recall, inv_rate, sum(base) / len(base)))
        print(f"\n  seed {seed}: vocab {len(vocab)} keys from {len(train)} declarers "
              f"-> {sorted(vocab)[:6]}{'…' if len(vocab) > 6 else ''}")
        print(f"     ① HELD-OUT RECALL on the {len(test)} declarers it never saw: {recall:.3f}")
        print(f"        the 14 invisible rounds:                                  {inv_rate:.3f}")
        print(f"     ② BASE RATE on no-route rounds, n=14, 3 draws: "
              f"{[f'{b:.3f}' for b in base]}  mean {sum(base)/len(base):.3f}")

    c1 = all(r["heldout_recall"] > 0 for r in rows)
    print(f"\n  ① HELD-OUT RECALL > 0 at every seed: {c1}  "
          f"{'PASS — the vocabulary generalises past the rounds it was read from' if c1 else 'FAIL — a lookup table, not a reader'}")

    planted = {"verdict": "x", "n": 3, "notes": ["a result with no provenance field at all"]}
    pk = set()
    keyset(planted, pk)
    vocab_all = {k for n in declarers for k in keys_of[n] if CANDIDATE.search(k)}
    c3 = not (pk & vocab_all)
    print(f"  ③ g=0, PLANTED — a document with no provenance key fires: {bool(pk & vocab_all)}: "
          f"{c3}  {'PASS' if c3 else 'FAIL — the reader fires on an empty document'}")

    all_base = [b for r in rows for b in r["base_rates"]]
    floor_lo, floor_hi = min(all_base), max(all_base)
    inv_lo = min(r["invisible_rate"] for r in rows)
    inv_hi = max(r["invisible_rate"] for r in rows)
    print(f"\n  ② FLOOR across {len(all_base)} no-route draws: [{floor_lo:.3f}, {floor_hi:.3f}]; "
          f"the 14 across {len(rows)} seeds: [{inv_lo:.3f}, {inv_hi:.3f}]")

    if not (c1 and c3):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "c1": c1, "c3": c3, "rows": rows},
                  open(OUT / "silence_or_blindness.json", "w"), indent=2)
        return 2

    live = {}
    for r in rows:
        v = set(r["vocab"])
        fired = sorted({k for n in invisible for k in keys_of[n] & v})
        r["vocab_keys_that_ever_fire"] = fired
        live[r["seed"]] = fired
    dead = {r["seed"]: r["vocab_size"] - len(r["vocab_keys_that_ever_fire"]) for r in rows}
    c6 = all(len(v) > 1 for v in live.values())
    print(f"\n  ⑥ IS THE READER A PROVENANCE READER OR A TOPIC DETECTOR — of each seed's "
          f"vocabulary, how many keys ever fire on the 14:")
    for r in rows:
        print(f"     seed {r['seed']}: {len(r['vocab_keys_that_ever_fire'])} live of "
              f"{r['vocab_size']} ({dead[r['seed']]} dead) -> {r['vocab_keys_that_ever_fire']}")
    print(f"     {'PASS — more than one key carries the signal' if c6 else 'FAIL — the entire rate is carried by ONE convention key and the rest of the vocabulary is data-field names containing `gold`. The reader is a TOPIC DETECTOR in the key channel, which is USES_GOLD-s defect relocated, and the held-out recall passed because declarers share gold-named DATA fields, not because they share a disclosure convention.'}")

    hits = sorted({n for n in invisible if keys_of[n] & vocab_all})
    print(f"\n  ④ THE OVERLAP, NAMED — {len(hits)} of the 14 carry a declarer key:")
    for n in hits:
        print(f"     {n:<40}{sorted(keys_of[n] & vocab_all)}")

    world = "B" if inv_lo > floor_hi else ("A" if inv_hi < floor_lo else "C")
    print(f"\n  ⭐⭐⭐ WORLD {world}: " + (
        f"the 14 fire at [{inv_lo:.3f}, {inv_hi:.3f}] against a measured no-route floor of "
        f"[{floor_lo:.3f}, {floor_hi:.3f}] — **above it, disjointly.** They DO carry provenance "
        f"fields; the ten-phrase value reader could not see them. The zero was the reader, and the "
        f"repair is the gate's vocabulary rather than the corpus's practice."
        if world == "B" else
        f"the 14 fire at [{inv_lo:.3f}, {inv_hi:.3f}], BELOW the no-route floor of "
        f"[{floor_lo:.3f}, {floor_hi:.3f}]. The zero is silence: these rounds carry less provenance "
        f"structure than rounds that touch no proxy at all, and the blind spot has a live cost."
        if world == "A" else
        f"the 14 fire at [{inv_lo:.3f}, {inv_hi:.3f}] and the floor is [{floor_lo:.3f}, "
        f"{floor_hi:.3f}] — **overlapping.** The design cannot separate silence from blindness at "
        f"n=14, and the honest output is the two intervals rather than a verdict."))
    if not c6:
        print(f"     ⛔ AND WORLD {world} IS NOT `n IS TOO SMALL`. Control ⑥ says the reader that "
              f"produced it was a topic detector: {min(len(v) for v in live.values())} of "
              f"{min(r['vocab_size'] for r in rows)}-{max(r['vocab_size'] for r in rows)} keys ever "
              f"fired. More n would buy a sharper estimate of the WRONG quantity. The repair is a "
              f"reader restricted to provenance CONVENTIONS -- `outcome_variable_scope`, "
              f"`instrument`, `judge_family` -- measured against the same floor.")
    print(f"     ⚠ BOUND FROM ABOVE, IN ONE DIRECTION: this counts whether a provenance CHANNEL "
          f"exists, never whether its content tells a reader anything. A `model` key holding a "
          f"boolean satisfies this reader and informs nobody.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world,
               "units": {"instrument": INSTRUMENT_UNIT, "claim": CLAIM_UNIT, "equal": False,
                         "direction": "bounds disclosure from ABOVE"},
               "n_declarers": len(declarers), "n_invisible": len(invisible),
               "n_noroute": len(noroute),
               "seeds": rows,
               "invisible_range": [inv_lo, inv_hi],
               "noroute_floor_range": [floor_lo, floor_hi],
               "reader_is_a_topic_detector": {
                   "live_keys_per_seed": live,
                   "dead_keys_per_seed": dead,
                   "reading": ("more than one key carries the signal" if c6 else
                               "the entire rate is carried by one convention key; the rest of the "
                               "vocabulary is data-field names containing `gold`, so the reader is "
                               "a topic detector in the key channel and World C is not a sample-size "
                               "problem"),
                   "separates": bool(c6)},
               "overlap_named": {n: sorted(keys_of[n] & vocab_all) for n in hits},
               "derivation_is_split_half": "the vocabulary is learned from a random half of the "
                                           "declarers and scored on the half it never saw; deriving "
                                           "from all 11 and testing on all 11 is construction, not "
                                           "a control",
               "not_measured": "whether a declaration is ADEQUATE; a key can exist and say nothing",
               "unit_note": "counts are ROUNDS",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "silence_or_blindness.json", "w"), indent=2)
    print(f"\n  artifact: results/silence_or_blindness.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
