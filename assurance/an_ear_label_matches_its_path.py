"""A document's EAR self-label must be its own address, because the path is the address.

P16 makes `E##·A##·R###` a citation. A citation is only an address if it is UNIQUE on its own,
without its path -- that is precisely why Ivan's rule numbers A and R globally continuous rather
than restarting them inside each epoch.

⛔ WHAT THIS WAS BUILT FROM. On 2026-08-06 the arc README at `A24_what_the_definition_costs`
opened with `# A16 - what the definition costs`, and `A23_is_the_admissibility_gate_the_right_gate`
opened with `# A13 - table of contents`. Both A16 and A13 are REAL, DIFFERENT arcs. That is the
worst failure available to an identifier: the citation does not dangle, it RESOLVES, and it
resolves somewhere else. Sweeping the tree found 31 of them -- every one an offset fossil of the
per-epoch numbering that was in force before the arcs were renumbered continuously. The
directories were renamed; the documents that named themselves were not.

    E02  A01->A04 A02->A05 A03->A06          E04  A01->A12 ... A04->A15
    E03  A01->A07 ... A05->A11               E05  irregular -- those arcs were re-CUT, not shifted

⭐ THE PATH IS THE AUTHORITY, never the prose. A directory rename is a real move performed by a
real command; a heading is a sentence someone typed. When they disagree the sentence is wrong.

PROXY LEDGER (P6) -- this check is sound in ONE direction only.
    PROPERTY   every document that names itself, names itself correctly
    PROXY      three self-label forms in the first 6 lines: a `# A24 ...` heading, an
               `**Arc E05·A24**` stamp, an `**E05 · A24 · R825**` stamp
    IMPLICATION  mismatch => a real defect (SOUND). no mismatch => NOT a clean bill: a document
               carrying no self-label at all passes VACUOUSLY.
    SAFE SIDE  the vacuous population is COUNTED AND PRINTED on every run. A check whose
               population is mostly vacuous is a check that has stopped measuring, and the only
               way to know that is to make it say so out loud.
    NOT IN SCOPE  cross-references. "diagnosis added at R340" inside R141 is legitimate prose and
               a naive scan flags 100+ of them. Only SELF-labels can disagree with the path.

EXIT
    0  every self-label addresses its own document
    1  a self-label names a different E/A/R than the one it lives in
    2  no document carries a self-label at all -- the check has no population, never a silent pass
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

SELF = [
    # ⛔ `\b` HERE WAS A FALSE NEGATIVE AND THE VACUOUS COUNT IS WHAT EXPOSED IT. The R-level
    # READMEs label themselves `# R01_rater_structure` -- the directory name, underscore and all.
    # `[EAR]\d{2,3}\b` does not match that, because the character after the digits is `_`, which
    # is a word character, so there is no boundary. 21 documents that DO name themselves were
    # being counted as carrying no label, i.e. passing vacuously. Printing the vacuous population
    # is the only reason this was ever visible: the check was GREEN both before and after.
    re.compile(r"^#\s+([EAR]\d{2,3})(?!\d)", re.M),                          # "# A24 - ", "# R01_x"
    re.compile(r"\*\*Arc\s+(E\d{2})[·.](A\d{2})", re.M),                     # "**Arc E05·A24**"
    re.compile(r"\*\*(E\d{2})\s*[·.]\s*(A\d{2})\s*[·.]\s*(R\d{2,3})", re.M),  # "**E05 · A24 · R825**"
]
HEAD_LINES = 6


def own_of(path):
    return {k: next((p.split("_")[0] for p in path.parts
                     if re.fullmatch(k + r"\d+.*", p)), None) for k in "EAR"}


def violations(text, path):
    own = own_of(path)
    head = "".join(text.splitlines(True)[:HEAD_LINES])
    out, labelled = [], False
    for rx in SELF:
        for m in rx.finditer(head):
            for gi in range(1, (m.lastindex or 0) + 1):
                tok = m.group(gi)
                mine = own[tok[0]]
                if mine:
                    labelled = True
                    if tok != mine:
                        out.append((tok, mine))
    return out, labelled


def main():
    docs = sorted(ROOT.glob("E*/**/README.md"))
    bad, labelled, vacuous = [], 0, []
    for md in docs:
        v, lab = violations(md.read_text(encoding="utf-8", errors="replace"), md)
        labelled += lab
        if not lab:
            vacuous.append(md.relative_to(ROOT))
        for tok, mine in v:
            bad.append((md.relative_to(ROOT), tok, mine))

    # POSITIVE CONTROL -- the check must FAIL on a document it is told is wrong. A gate that has
    # never returned non-zero is silence, not an acquittal (P5).
    probe = pathlib.Path("E05_the_space_of_compilers/A24_what_the_definition_costs/README.md")
    pos, _ = violations("# A16 - a heading that names a different arc\n", probe)
    if not pos:
        print("  ⛔ POSITIVE CONTROL FAILED: the check does not fire on a known-bad heading.")
        return 2
    print(f"  positive control: fires on a planted `# A16` in A24 -> {pos[0][0]} != {pos[0][1]}  PASS")

    print(f"  population: {len(docs)} READMEs · {labelled} carry a self-label · "
          f"{len(vacuous)} carry none and pass VACUOUSLY (not a clean bill -- see the proxy ledger)")
    # NAME them while they are few. A count says the gap exists; the list says where it is, and a
    # gap nobody can point at is the one that grows back.
    for p in vacuous[:12]:
        print(f"       outside the check: {p}")
    if not labelled:
        print("  ⛔ no document carries a self-label. The check has no population. Exit 2.")
        return 2
    if bad:
        print(f"  ⛔ {len(bad)} self-labels name a different E/A/R than the path they live in:")
        for f, tok, mine in bad:
            print(f"       says {tok:<5} path says {mine:<5} :: {f}")
        return 1
    print("  ✓ every self-label addresses its own document")
    return 0


if __name__ == "__main__":
    sys.exit(main())
