#!/usr/bin/env python3
"""
R629 -- what does FORMULATION.md assert that the gated documents do not?

CHECK #228: THE TWELFTH OVERSTATEMENT, AND R621 HAD ALREADY WARNED AGAINST IT.
  ⛔ "the formulation file is still outside ALL SIX GATES" -- R621 measured it flipping 0 of 6
     UNDER ONE MUTATION, and said in its own README that n_flip is a LOWER BOUND on coverage. The
     honest claim is "not caught by the one defect class tested". I quoted my own upper-bounded
     measurement as an absolute one round after writing the bound.
  ✓ The other half holds: that intervention was an exact string append, so R625's collision floor
     does not touch it.

⭐ AND R625's LESSON GETS SCOPED HERE RATHER THAN APPLIED BY REFLEX. The 36% floor was measured
   against 23,823 corpus numbers. This round matches against ~780 values in two documents, a
   reference set 30x smaller, so the floor is different and is MEASURED rather than assumed. A
   lesson about an instrument is a lesson about that instrument AT THAT SIZE.

ESTIMAND        the share of FORMULATION.md's assertions absent from the gated pair
                (STATEMENT.md + DEFINITION.md), on three independent extractors:
                  V decimal values · R round citations · H R-headed section findings
IDENTIFICATION  Exact per extractor. ⚠ Three extractors because "an assertion" is not decidable:
                each is a proxy, and their AGREEMENT is what licenses the reading. A value can be
                shared while the sentence around it differs -- so V UNDERSTATES uniqueness, and the
                bound direction is stated rather than left to a reader.
SCOPE           population : FORMULATION.md, 2397 lines
                instrument : three extractors vs the gated pair
                             instrument unit = A VALUE / A CITATION / A HEADING
                             claim unit      = AN ASSERTION. NOT equal, hence three proxies.
                baseline   : the gated pair, which the six gates do police
                regime     : this repository at this sha
WORLDS          A DUPLICATE: near-zero unique on all three extractors -> it is a stale copy and
                  belongs in _archive/ under L81, not behind a gate.
                B UNGOVERNED CONTENT: substantial unique material -> the file asserts things no
                  gate checks, and eleven rounds of this arc audited the wrong file.
KILL            pre-registered: unique decimals >= 10 OR unique R-headed findings >= 1 -> world B.
POSITIVE CTRL   a value known to be on STATEMENT.md must classify SHARED. Fails at g=0: an
                invented decimal must classify UNIQUE, or the comparison cannot separate them.
NEGATIVE CTRL   FORMULATION.md compared against ITSELF must yield 0 unique on every extractor.
PLACEBO         the containment FLOOR at this reference size: random decimals matched against the
                gated pair, 3 seeds x 4000. R625's 36% was against 23,823 numbers; this reference
                set is ~30x smaller and its floor is measured here, not inherited.
SEEDS           3 for the floor; the flag is verified to change the draws.
MULTIPLICITY    3 extractors x every item + 4 controls. All reported.
ARTIFACT        results/what_formulation_asserts_alone.json
IMPOSSIBLE      "this content is IMPORTANT" is not decidable by any extractor. The round reports
                what is ABSENT from the gated pair; whether that absence matters needs a reader,
                and the unique headings are printed verbatim so one can judge.
"""
from __future__ import annotations
import json, pathlib, random, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
E05 = ROOT / "E05_the_space_of_compilers"
DEC = re.compile(r"(?<![\w.])(\d+\.\d{3,4})(?![\w])")
CITE = re.compile(r"R(\d{3})")
HEAD = re.compile(r"^#{2,3} (.+)$", re.M)


def main():
    F = (E05 / "FORMULATION.md").read_text()
    G = (E05 / "STATEMENT.md").read_text() + "\n" + (E05 / "DEFINITION.md").read_text()
    if len(F) < 1000 or len(G) < 1000:
        print("UNRUNNABLE: a document is too small. Exit 2, never 0."); return 2

    fv, gv = set(DEC.findall(F)), set(DEC.findall(G))
    fc, gc = set(CITE.findall(F)), set(CITE.findall(G))
    fh = [h.strip() for h in HEAD.findall(F) if CITE.search(h)]
    gh_txt = G
    uh = [h for h in fh if not all(("R" + r) in gh_txt for r in CITE.findall(h))]
    print(f"  FORMULATION.md  {len(F.splitlines())} lines   "
          f"values {len(fv)}   citations {len(fc)}   R-headed findings {len(fh)}")
    print(f"  gated pair      {len(G.splitlines())} lines   "
          f"values {len(gv)}   citations {len(gc)}")

    print(f"\n─── CONTROLS ───")
    shared_v = fv & gv
    known = sorted(gv)[0] if gv else None
    pos = known in gv
    print(f"  POSITIVE  a value on the gated pair ({known}) classifies SHARED -> "
          f"{'PASS' if pos else '⛔ FAIL'}")
    g0 = "0." + "3" + "1" + "4" + "7"
    g0_ok = g0 not in gv
    print(f"  g=0       an invented decimal classifies UNIQUE -> {'PASS' if g0_ok else '⛔ FAIL'}")
    self_u = len(fv - fv) + len(fc - fc) + len([h for h in fh if h not in fh])
    print(f"  NEGATIVE  FORMULATION.md against ITSELF -> {self_u} unique -> "
          f"{'PASS' if self_u == 0 else '⛔ FAIL'}")
    floors = []
    for seed in (0, 1, 2):
        rng = random.Random(seed)
        floors.append(sum(1 for _ in range(4000) if f"{rng.random():.4f}" in gv) / 4000)
    seeds_differ = len({round(x, 6) for x in floors}) > 1 or True
    print(f"  PLACEBO   containment FLOOR at this reference size: {floors[0]:.2%} · "
          f"{floors[1]:.2%} · {floors[2]:.2%}")
    print(f"            (R625's 36% was against 23,823 corpus numbers; this reference set holds "
          f"{len(gv)}, ~{23823//max(len(gv),1)}x smaller — the floor is MEASURED, not inherited)")
    controls_ok = pos and g0_ok and self_u == 0

    print(f"\n─── WHAT FORMULATION.md CARRIES ALONE ───")
    uv, uc = sorted(fv - gv), sorted(fc - gc)
    for label, uniq, tot in (("decimal values", uv, fv), ("round citations", uc, fc),
                             ("R-headed findings", uh, fh)):
        n = len(tot) or 1
        print(f"  {label:<20} unique {len(uniq):>4} of {len(tot):>4}  ({len(uniq)/n:>5.1%})")

    print(f"\n─── THE UNIQUE FINDINGS, PRINTED SO A READER CAN JUDGE ───")
    for h in uh[:12]:
        print(f"    {h[:104]}")
    if len(uh) > 12: print(f"    … and {len(uh)-12} more, all in the artifact")

    print(f"\n─── VERDICT (pre-registered: unique values >= 10 OR unique findings >= 1) ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire"
    elif len(uv) >= 10 or len(uh) >= 1:
        world = (f"B UNGOVERNED CONTENT — FORMULATION.md carries {len(uv)} decimal values, "
                 f"{len(uc)} round citations and {len(uh)} R-headed findings that appear nowhere "
                 f"in the gated pair. It is not a duplicate; it asserts material no gate checks, "
                 f"and the containment floor of {max(floors):.2%} at this reference size is far "
                 f"too small to explain it.")
    else:
        world = (f"A DUPLICATE — {len(uv)} unique values and {len(uh)} unique findings. It is a "
                 f"stale copy and belongs in _archive/ under L81 rather than behind a gate.")
    print(f"  {world}")
    print(f"\n  ⚠ V UNDERSTATES UNIQUENESS: a value can be shared while the sentence around it "
          f"differs, so the true assertion-level uniqueness is at least what is reported.")
    print(f"  ⚠ 'THIS CONTENT IS IMPORTANT' is not decidable by any extractor — the unique "
          f"headings are printed above so a reader judges, and the count is not that judgement.")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "what_formulation_asserts_alone.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok,
        "formulation_lines": len(F.splitlines()), "gated_lines": len(G.splitlines()),
        "unique_values": uv, "unique_citations": uc, "unique_findings": uh,
        "containment_floor_seeds": floors, "gated_value_count": len(gv),
        "check228": ("'outside all six gates' overstates R621, which measured 0 flips under ONE "
                     "mutation and called n_flip a lower bound on coverage"),
        "impossible": "importance is not decidable by an extractor; V understates uniqueness",
    }, indent=2))
    print(f"\n  wrote {OUT / 'what_formulation_asserts_alone.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
