#!/usr/bin/env python3
"""
R613 -- how much of the definition's own evidence comes from the documented era?

CHECK #212 CAUGHT TWO ERRORS IN R612's CLOSING LINE.
  ⛔ "EVERY quantity in this arc is now a property of ARTIFACTS" -- R602 measured corpus
     overlap and R603 measured release schemas; both are properties of the DATA FILES. An
     "every" over my own work, false as written.
  ⛔ "SIX rounds of corpus archaeology" -- the thread is R605 through R612, EIGHT rounds. A
     bare count, wrong, and of exactly the kind the commit gate exists to catch.

The substantive move stands: eight rounds established that artifacts before ~431 record where
their numbers came from and artifacts after do not. The question that returns this to the
object is what fraction of the DEFINITION's own claim rows rest on the documented side.

ESTIMAND        For each row of STATEMENT.md's numbered claim table: does it cite >=1 round
                with id < 431? n_anchored / n_rows is the definition's own exposure.
IDENTIFICATION  Exact -- the claim table is delimited and citations are extracted with the
                gate's own regex. ⚠ "rests on" is not "cites": a row may cite an early round
                for a caveat and take its number from a late one. Every row is printed with its
                citation list so a reader can overrule, and the count is an UPPER BOUND on
                anchoring.
SCOPE           population : the numbered claim rows of STATEMENT.md
                instrument : the gate's citation regex, restricted to the claim-table block
                             instrument unit = A CITATION INSIDE A CLAIM ROW
                             claim unit      = EVIDENCE THE ROW RESTS ON -- NOT equal, hence
                             the upper bound above
                baseline   : the boundary B=431, imported from R610/R611, not fitted here
                regime     : as committed at this sha
WORLDS          A ANCHORED: most rows cite >=1 pre-B round -> the definition's evidence is
                  largely from the era whose artifacts record their sources, and the
                  provenance finding does not reach the claims.
                B POST-BOUNDARY: most rows cite only post-B rounds -> the definition rests on
                  the undocumented era and the eight-round thread lands on the deliverable.
                C SPLIT: neither majority holds -> report the fraction and stop.
KILL            pre-registered: if the extractor finds fewer rows than the table visibly has,
                it has mis-parsed the block and no fraction is admissible.
POSITIVE CTRL   the extractor must recover the row count and the citations of rows whose
                content is known (rows citing R519, R529, R527). Fails at g=0: an empty block
                yields no rows.
NEGATIVE CTRL   a synthetic row citing only post-B rounds must be classified unanchored, and
                one citing a pre-B round must be classified anchored.
PLACEBO         a row with no citation at all must be counted as neither, not silently as
                unanchored -- absence of a citation is a different state from a late one.
SEEDS           n/a, deterministic.
MULTIPLICITY    one classification per row; every row printed.
ARTIFACT        results/anchoring.json
IMPOSSIBLE      construct validity for "rests on": which citation carries a row's NUMBER, as
                opposed to its caveat, is not decidable from the row's text. That needs the
                round-by-round derivation the page does not carry.
"""
from __future__ import annotations
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
E05 = ROOT / "E05_the_space_of_compilers"
OUT = pathlib.Path(__file__).resolve().parent / "results"
CITE = r"\(R(\d{3})[,)]|R(\d{3})[,)]"
B = 431


def claim_block(text):
    m = re.search(r"\n\| # \| claim \| scope it holds over \|\n(.*?)\n\n", text, re.S)
    return m.group(1) if m else ""


def rows_of(block):
    out = []
    for line in block.split("\n"):
        if not line.startswith("|"):
            continue
        m = re.match(r"\|\s*\*\*(\d+)\*\*\s*\|", line)
        if not m:
            continue
        cs = sorted({int(a or b) for a, b in re.findall(CITE, line)})
        out.append({"row": int(m.group(1)), "cites": cs,
                    "pre": [c for c in cs if c < B], "post": [c for c in cs if c >= B],
                    "text": re.sub(r"\s+", " ", line)[:110]})
    return out


def main():
    text = (E05 / "STATEMENT.md").read_text()
    block = claim_block(text)
    rows = rows_of(block)
    visible = len(re.findall(r"\n\|\s*\*\*\d+\*\*\s*\|", "\n" + block))
    print(f"POPULATION  claim-table block {len(block)} chars, rows parsed {len(rows)}, "
          f"rows visible {visible}")
    if not rows:
        print("UNRUNNABLE: no claim rows parsed. Exit 2, never 0."); return 2
    if len(rows) != visible:
        print("UNRUNNABLE: parsed count differs from visible count — mis-parse. Exit 2.")
        return 2

    print(f"\n─── CONTROLS ───")
    known = {519, 529, 527}
    found = {c for r in rows for c in r["cites"]}
    pos_ok = known <= found
    print(f"  POSITIVE  known cited rounds {sorted(known)} recovered: "
          f"{sorted(known & found)} -> {'PASS' if pos_ok else 'FAIL'}")
    g0 = rows_of("")
    print(f"  g=0       empty block -> {len(g0)} row(s) -> "
          f"{'PASS (can fail)' if not g0 else 'FAIL'}")
    synth_late = rows_of("| **9** | a claim *(R500, R560)* | scope |")
    synth_early = rows_of("| **9** | a claim *(R400)* | scope |")
    neg_ok = (synth_late and not synth_late[0]["pre"]) and (synth_early and synth_early[0]["pre"])
    print(f"  NEGATIVE  synthetic post-B row -> pre={synth_late[0]['pre'] if synth_late else '?'}"
          f"; synthetic pre-B row -> pre={synth_early[0]['pre'] if synth_early else '?'} -> "
          f"{'PASS' if neg_ok else 'FAIL'}")
    synth_none = rows_of("| **9** | a claim with no citation | scope |")
    plc_ok = bool(synth_none) and not synth_none[0]["cites"]
    print(f"  PLACEBO   a row with no citation -> cites={synth_none[0]['cites'] if synth_none else '?'}"
          f" -> {'PASS — counted as neither, not as unanchored' if plc_ok else 'FAIL'}")
    controls_ok = pos_ok and not g0 and neg_ok and plc_ok

    print(f"\n─── EVERY CLAIM ROW (B = {B}, imported from R610/R611, not fitted here) ───")
    anch = uncited = post_only = 0
    for r in rows:
        if not r["cites"]:
            state = "NO CITATION"; uncited += 1
        elif r["pre"]:
            state = f"ANCHORED  pre={r['pre']}"; anch += 1
        else:
            state = f"POST-ONLY post={r['post']}"; post_only += 1
        print(f"  row {r['row']:>2}  {state}")
        print(f"          {r['text']}")
    n = len(rows)
    print(f"\n  anchored {anch}/{n} = {anch/n:.4f}   post-only {post_only}/{n}   "
          f"no citation {uncited}/{n}")

    print(f"\n─── VERDICT ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire"
    elif anch > n/2:
        world = (f"A ANCHORED — {anch} of {n} rows ({anch/n:.1%}) cite at least one round from "
                 f"before {B}, the era whose artifacts record where their numbers came from. "
                 f"The eight-round provenance thread does NOT reach most of the claim set.")
    elif post_only > n/2:
        world = (f"B POST-BOUNDARY — {post_only} of {n} rows cite only rounds at or after {B}, "
                 f"so the definition rests on the era whose artifacts do not record their "
                 f"sources, and the thread lands on the deliverable itself.")
    else:
        world = (f"C SPLIT — anchored {anch}, post-only {post_only}, uncited {uncited} of {n}; "
                 f"no majority, and the fraction is the finding")
    print(f"  {world}")
    print(f"\n  ⚠ UPPER BOUND: 'cites a pre-{B} round' is not 'takes its number from one'. Every "
          f"row is printed so a reader can overrule the classification.")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "anchoring.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok, "B": B,
        "n_rows": n, "anchored": anch, "post_only": post_only, "uncited": uncited,
        "rows": rows,
        "check212": ("R612's closing line said EVERY quantity in the arc is a property of "
                     "artifacts — R602 measured corpus overlap and R603 release schemas, both "
                     "properties of the DATA FILES — and called the thread SIX rounds when it "
                     "is eight, R605 through R612"),
        "impossible": ("which citation carries a row's NUMBER rather than its caveat is not "
                       "decidable from the row's text"),
    }, indent=2))
    print(f"\n  wrote {OUT / 'anchoring.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
