#!/usr/bin/env python3
"""
R914 · the `transport_*` comparators are a DIFFERENT CORPUS — so comparator robustness has a price,
        not a loader bug.

⛔ WHY. R913 found that every admission decision in this arc used one comparator, `genericpool16`,
which **is itself one of R881's 99 scored arms** — and that the release's four other named
prompt-blind arms could not be loaded at all. Its closing sentence named two possibilities and
refused to pick: *"Either the difference is superficial and a two-line adapter unblocks the whole
comparator sweep, or it is a different unit of observation and the arms were never comparable,
which would itself explain why nobody used them."*

⭐ **ONE READ SETTLES IT, AND IT IS THE SECOND.** The satisfaction keys:
  · `sat_genericpool16.npz` → `04414715-5487-5885-9313-e7cc3f4601cb|0|A`
    — **3 fields**: CoVal prompt UUID, criterion index, response letter A/B/C/D
  · `sat_transport_*.npz`   → `c365|int10006|ut3170|0`
    — **4 fields**, and the ids are `c…` / `int…` / `ut…`, none of them UUIDs
**Different field count, different id space, different response indexing.** `score.py:58` splits on
exactly three, which is why it raised. **These arms live on another dataset** — which is what
`R427_does_the_definition_transport_at_all` says in its own name, and it is why nobody ever used
them as comparators here.

⭐⭐ **SO THE IMPOSSIBILITY REGISTER ENTRY WAS WRITTEN TOO CHEAPLY AND IS CORRECTED.** R913 recorded
*"would require a loader for the transport_* schema"*. A loader would produce numbers on a
different population — the arms are not comparable, so that requirement was wrong in the direction
that makes the work sound easy. **The real requirement is a prompt-blind arm on THIS corpus that is
not already a scored arm** — and R907 already priced exactly that object: a fixed checklist is not a
subset of `coval_full`, so it costs `k × 4 × 968` = **15,488 judge calls**.

ESTIMAND        whether the `transport_*` satisfaction keys index the same observational unit as
                `genericpool16`'s, and what the corrected register requirement is.
IDENTIFICATION  exact — the keys are read from the committed npz files.
SCOPE           population: the committed satisfaction files; instrument: the key grammar itself
                baseline:   `sat_genericpool16.npz`, which `score.py` parses by construction
                regime:     home release
WORLDS          A · same field count and id space -> superficial, an adapter unblocks the sweep
                B · different -> a different corpus; the arms were never comparable and the
                    register requirement must be rewritten with what it ACTUALLY needs
KILL            CONDITIONAL:
                  ⭐ ① POSITIVE: the `genericpool16` key must split into exactly 3 on `|` and its
                     first field must parse as a UUID. If the reference file does not match the
                     grammar `score.py` assumes, the comparison has no anchor.
                  ⭐ ② the difference must be STRUCTURAL, not cosmetic: field COUNT and id SHAPE
                     both checked, because a 3-vs-4 split alone could be a delimiter quirk.
                  ⭐ ③ the corrected requirement must be PRICED from a committed measurement, not
                     estimated here — R907's 15,488 is read from its artifact.
MULTIPLICITY    5 files × 2 structural properties; all printed.
ARTIFACT        results/transport_schema.json
IMPOSSIBLE      cross-release · construct validated · causally identified · independently
                replicated. ⚠ AND: this says the arms are on a different corpus. It does NOT say
                the definition fails to transport — R427 asked that and this round does not.
"""
import json, pathlib, re, subprocess
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
RES = ROOT / "corebench" / "results"
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
REFERENCE = "genericpool16"
OTHERS = ["transport_generic", "transport_randblind_s0",
          "transport_randblind_s1", "transport_randblind_s2"]
UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


def grammar(nm):
    f = RES / f"sat_{nm}.npz"
    if not f.exists():
        return None
    z = np.load(f, allow_pickle=True)
    keys = [str(k) for k in z["meta"][:2000]]
    fields = sorted({len(k.split("|")) for k in keys})
    first = keys[0].split("|")
    return {"arm": nm, "n_keys": int(len(z["meta"])), "field_counts": fields,
            "example": keys[0], "first_field_is_uuid": bool(UUID.match(first[0])),
            "last_field": first[-1]}


def main() -> int:
    ref = grammar(REFERENCE)
    if ref is None:
        print("  UNRUNNABLE: reference file missing. Exit 2, never 0.")
        return 2
    c1 = ref["field_counts"] == [3] and ref["first_field_is_uuid"]
    print(f"  ① POSITIVE the reference matches the grammar score.py assumes:")
    print(f"     {REFERENCE:<24} fields {ref['field_counts']}  uuid {ref['first_field_is_uuid']}  "
          f"e.g. {ref['example']}")
    print(f"     {c1}  {'PASS' if c1 else 'FAIL'}   (score.py:58 splits on exactly 3)")

    rows, missing = [ref], []
    for nm in OTHERS:
        g = grammar(nm)
        (rows.append(g) if g else missing.append(nm))
    print(f"\n  ⭐ ② KEY GRAMMAR, all {len(rows)} files — field COUNT and id SHAPE both checked,")
    print(f"     because a 3-vs-4 split alone could be a delimiter quirk:")
    print(f"     {'arm':<26}{'keys':>8}{'fields':>9}  {'uuid?':<7}{'last':<10}example")
    for g in rows:
        print(f"     {g['arm']:<26}{g['n_keys']:>8}{str(g['field_counts']):>9}  "
              f"{str(g['first_field_is_uuid']):<7}{g['last_field']:<10}{g['example']}")
    if missing:
        print(f"     ⚠ ABSENT and NAMED: {missing}")

    alt = [g for g in rows if g["arm"] != REFERENCE]
    diff_fields = all(g["field_counts"] != ref["field_counts"] for g in alt)
    diff_ids = all(not g["first_field_is_uuid"] for g in alt)
    c2 = bool(alt) and diff_fields and diff_ids
    print(f"\n     different field count from the reference: {diff_fields}")
    print(f"     none of their first fields is a UUID:      {diff_ids}")
    print(f"     ② STRUCTURAL, not cosmetic: {c2}  {'PASS' if c2 else 'FAIL'}")

    r907 = next(A24.glob("R907_*/results/expansion_cost.json"), None)
    price = None
    if r907:
        for k in json.loads(r907.read_text()).get("kinds", []):
            if k.get("kind") == "FIXED_CHECKLIST":
                price = k.get("judge_calls_per_new_arm")
    c3 = price is not None
    print(f"  ③ the corrected requirement PRICED from R907's committed artifact, not estimated "
          f"here: {price} judge calls: {c3}  {'PASS' if c3 else 'FAIL'}")
    if not (c1 and c2 and c3):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "rows": rows},
                  open(OUT / "transport_schema.json", "w"), indent=2)
        return 2

    print(f"\n  ⭐⭐⭐ WORLD B: the `transport_*` arms are on a DIFFERENT CORPUS — 4 fields against")
    print(f"     3, non-UUID ids, a numeric last field instead of a response letter. **They were")
    print(f"     never comparable**, which is why nobody used them as comparators, and")
    print(f"     `R427_does_the_definition_transport_at_all` says so in its own name.")
    print(f"\n  ⛔ SO R913's REGISTER ENTRY WAS WRITTEN TOO CHEAPLY AND IS CORRECTED. It said")
    print(f"     `would require a loader for the transport_* schema`. **A loader would produce")
    print(f"     numbers on a different population** — that requirement was wrong in the direction")
    print(f"     that makes the work sound easy, which is the flattering direction the standard")
    print(f"     forbids for unavailability claims.")
    print(f"     CORRECTED: comparator robustness requires **a prompt-blind arm on THIS corpus")
    print(f"     that is not already a scored arm**, and R907 already priced that object at")
    print(f"     **{price:,} judge calls** — a fixed checklist is not a subset of `coval_full`.")
    print(f"\n  ⚠ AND THIS DOES NOT SAY THE DEFINITION FAILS TO TRANSPORT. R427 asked that")
    print(f"    question; this round only establishes that its arms cannot serve as comparators")
    print(f"    for the population every number in this arc was computed on.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": "B", "reference": ref, "alternatives": alt,
               "absent": missing,
               "structural_difference": {"field_count": diff_fields, "id_shape": diff_ids},
               "corrects_R913_register_entry": {
                   "was": "would require a loader for the transport_* satisfaction schema",
                   "why_wrong": "a loader would produce numbers on a DIFFERENT population; the "
                                "arms are not comparable, so the requirement understated the work "
                                "— wrong in the flattering direction",
                   "corrected": "a prompt-blind arm on THIS corpus that is not already a scored arm",
                   "price_judge_calls": price,
                   "price_source": "R907's committed measurement, read not estimated"},
               "does_not_say": "that the definition fails to transport — R427 asked that",
               "unit_note": "field counts are KEY SEGMENTS; price is JUDGE CALLS",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "transport_schema.json", "w"), indent=2)
    print(f"\n  artifact: results/transport_schema.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
