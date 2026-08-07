#!/usr/bin/env python3
"""A string literal used as a detector marker must match at least one real line.

⛔ WHY, and it is the FIFTH instance of one class in a single session. A marker that matches nothing
is indistinguishable from a corpus containing nothing — the same silence-versus-absence problem as a
zero from an instrument that has never returned non-zero, moved from data into vocabulary.

  · three ANNOTATION ANCHORS written from memory of a line rather than read from it. All three
    aborted; all three were caught because the commit refuses when an annotation fails.
  · one DETECTOR MARKER: R886's `KILL ④` tested for the literal `"CI-lower"` while the text it was
    meant to find says `"CI lower bound"`. **Hyphen versus space.** The round printed
    *"the headline is behind its evidence"* after the headline had already been fixed, and no guard
    was watching, because the annotation guard checks that text LANDED, never that a checker can
    SEE it.

**The three anchors had a guard. The marker did not.** This is that guard.

PROXY LEDGER
  PROPERTY    the marker can fire on this corpus
  PROXY       the literal occurs at least once in the repo's text
  IMPLICATION **no occurrence anywhere ⇒ cannot fire** is SOUND.
              **occurs somewhere ⇒ points at the right corpus** is NOT — a marker may match in a
              file the detector never reads. This rules on IMPOSSIBILITY only.
  SAFE SIDE   flags markers with zero occurrences. A matching marker is UNVERIFIED, never certified.

⛔⛔⛔ AND THE FIRST REAL RUN OVERTURNED THAT IMPLICATION FOR HALF THE CORPUS — A DIRECTION ERROR IN
MY OWN PROXY LEDGER, WHICH IS THE ONE THING THIS LEDGER EXISTS TO PREVENT.
Of the 5 markers flagged, `no_withdrawn_framings.py::"the arm scores 0.5667 against its own floor"`
matches nothing **because the corpus is clean**. It is an ABSENCE-ASSERTION: the gate FAILS when the
marker is found. **For an absence-marker, matching nothing is the PASS condition, not the defect.**

⭐ So `no occurrence ⇒ cannot fire` is sound **only for markers that assert PRESENCE**, and the two
polarities are not separable by AST — `if m in text: FAIL` and `if m in text: PASS` are the same
node. **The baseline below therefore mixes real dead markers with correctly-silent absence-markers,
and freezing it asserts only "this is the state at this commit", never "these are 5 defects."**
This is the same error the whole session has been about, in its purest form: *`∂≠0 ⇒ in the ancestor
set` used backwards.* I built a presence-test and wrote an implication that covers both directions.

⚠ **What the gate is therefore FOR, narrowly and honestly:** it catches a marker that appears in
NEITHER the corpus NOR any other file — a new one entering the baseline is worth reading, because
R886's `"CI-lower"` would have entered exactly that way. It does not, and cannot, certify that the
5 frozen entries are broken. Splitting them needs a polarity annotation the sources do not carry.

⚠ It sees only literals passed to `in` / `.search` / `.match` / `.find` / `re.compile`. A marker
built by f-string or concatenation is invisible to it, and that is named here rather than discovered.

⛔⛔ AND THE POSITIVE CONTROL DIED OF ITS OWN POST-MORTEM, WHICH IS THE ROUND'S REAL FINDING.
The first version used the REAL dead literal `"CI-lower"` — the one that could not fire an hour
earlier. It now occurs **5 times**, because I wrote about it: in R886's docstring, in the fix
comment, in this file. **Documenting a dead marker resurrects it.** The audit's prose becomes part
of the audited corpus — R883's self-inclusion in a new costume, where an inventory of findings
joined the population it was inventorying.

**So a dead-marker control cannot survive its own write-up**, and the honest consequences are:
  · the POSITIVE arm uses a literal absent BY CONSTRUCTION and says so. It is not a real corpus
    item — the weakness this session has caught three times — **stated, not hidden.**
    ⛔⛔ AND IT RESURRECTED TOO, ON THE FIRST TRY. Writing the absent string out in full put it in
    this file, which `corpus_text()` reads, so `count == 0` was false the moment I named it.
    **Any string named as absent becomes present by being named.** It is now assembled from
    fragments at runtime. ⭐ **The gate's own declared blind spot — concatenated markers are
    invisible to the AST scan — is what makes its control possible. The limitation is the remedy.**
  · the g=0 arm stays REAL: `"CORRECTED R886"`, a stamp that genuinely occurs.
  · the scan EXCLUDES each marker's own defining file, so a gate never validates its own literal.
**A control whose subject can be changed by writing about it is a control with an expiry date.**

⛔⛔⛔ THIRD RESURRECTION, AND IT MOVED FROM THE CONTROL INTO THE RESULT. The first real run flagged
**5**; the freeze recorded **4**. Writing the fifth marker's literal into the paragraph above put it
in the corpus, so it stopped being dead **between the run and the freeze** — no error, no diff, a
true positive deleted by being described. ⭐ **An audit that quotes its subject alters its
population.** The first two instances only broke a control; this one changed the measurement. The
general rule, and it is why this file carries three post-mortems instead of one:
**when the corpus includes the report, the report is an intervention on the corpus.**
"""
import ast, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
FROZEN = pathlib.Path(__file__).resolve().parent / "KNOWN_DEAD_MARKERS.json"
MIN_LEN = 6              # shorter literals collide with ordinary prose and say nothing
SEARCHY = {"search", "match", "fullmatch", "find", "findall", "index", "compile", "startswith",
           "endswith"}


def markers(src):
    """-> {literal} used as a search marker. Literals only; f-strings are invisible (declared)."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            for op, cmp_ in zip(node.ops, node.comparators):
                if isinstance(op, (ast.In, ast.NotIn)) and isinstance(node.left, ast.Constant) \
                        and isinstance(node.left.value, str):
                    out.add(node.left.value)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr in SEARCHY:
            for a in node.args:
                if isinstance(a, ast.Constant) and isinstance(a.value, str):
                    out.add(a.value)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr == "compile":
            for a in node.args:
                if isinstance(a, ast.Constant) and isinstance(a.value, str):
                    out.add(a.value)
    return {m for m in out
            if len(m) >= MIN_LEN and not any(c in m for c in "\\^$*+?[]|()")}


def corpus_text():
    buf = []
    for pat in ("assurance/*.py", "E0*/A*/R*/run.py", "E0*/*.md", "*.md"):
        for f in ROOT.glob(pat):
            try:
                buf.append(f.read_text(encoding="utf-8", errors="ignore"))
            except Exception:
                pass
    return "\n".join(buf)


def controls(text) -> bool:
    # ⛔⛔ BUILT AT RUNTIME, AND THIS IS THE SECOND RESURRECTION. The previous version wrote the
    # absent literal out in full — which PUT IT IN THIS FILE, and `corpus_text()` reads
    # assurance/*.py, so `count == 0` was false the moment I named it. **Any string named as
    # absent becomes present by being named.** So it is assembled from fragments and never appears
    # whole anywhere. ⭐ The gate's own declared blind spot — concatenated markers are invisible to
    # the AST scan — is exactly what makes its control possible. The limitation is the remedy.
    dead = "zz" + "q-marker-" + "absent-by-" + "constr" + "uction"
    live = "CORRECTED R886"                      # REAL: the stamp R886's fix left behind
    p1 = text.count(dead) == 0
    p2 = live in text
    print(f"  POSITIVE  a marker absent BY CONSTRUCTION is seen as dead: {p1}  "
          f"{'PASS' if p1 else 'FAIL'}")
    print(f"     ⚠ SYNTHETIC, and that is a WEAKNESS, stated rather than hidden. The real dead")
    print(f"       literal 'CI'+'-lower' now occurs {text.count('CI' + chr(45) + 'lower')} times")
    print(f"       because I documented its failure. Documenting a dead marker RESURRECTS it, so")
    print(f"       a dead-marker control cannot survive its own write-up.")
    print(f"  g=0       the REAL live stamp {live!r} DOES occur: {p2}  {'PASS' if p2 else 'FAIL'}")
    return p1 and p2


def main() -> int:
    text = corpus_text()
    if not text:
        print("  OBSERVED NOTHING: empty corpus. Exit 2, never 0.")
        return 2
    if not controls(text):
        print("\n  UNVERIFIED: the detector failed its own controls. Exit 2, never 0.")
        return 2

    dead, scanned, unparsed = [], 0, []
    for f in sorted((ROOT / "assurance").glob("*.py")):
        ms = markers(f.read_text(encoding="utf-8", errors="ignore"))
        if ms is None:
            unparsed.append(f.name); continue
        scanned += 1
        own = f.read_text(encoding="utf-8", errors="ignore")
        for m in sorted(ms):
            # a marker never validates itself: subtract its own file's occurrences
            if text.count(m) - own.count(m) <= 0:
                dead.append(f"{f.name}::{m}")
    total = len(list((ROOT / "assurance").glob("*.py")))
    assert scanned + len(unparsed) == total, "partition does not sum"   # R885's lesson, applied
    frozen = set(json.loads(FROZEN.read_text())["keys"]) if FROZEN.exists() else set()
    new = [d for d in dead if d not in frozen]
    print(f"\n  {scanned} scanned + {len(unparsed)} unparseable = {total} gate file(s)  "
          f"[partition asserted]")
    print(f"  {len(dead)} marker(s) that occur nowhere but their own file · {len(frozen)} frozen · "
          f"{len(new)} NEW")
    if new:
        print(f"\n  FAIL: {len(new)} marker(s) cannot fire on this corpus:")
        for d in new[:10]:
            print(f"    {d}")
        print("  Read the marker from the text it is meant to match, never from memory of it.")
        print("  R886's KILL ④ printed the wrong verdict for exactly this reason.")
        return 1
    print("\n  PASS: no NEW dead marker. ⚠ A matching marker is UNVERIFIED, never certified — it")
    print("  may match in a file the detector never reads. This rules on IMPOSSIBILITY only, and")
    print("  markers built by f-string or concatenation are invisible to it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
