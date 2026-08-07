#!/usr/bin/env python3
"""⛔⛔ NOT A GATE. NOT WIRED. KEPT AS A MEASURED NEGATIVE SO NOBODY BUILDS IT AGAIN.

R1030 measured that 5 of 7 NEXT lines proposed an existing subject and named the repair: wire a
prior-art check into `preflight.py`'s `--next` path. **This file IS that repair, built and then
measured against the four REAL committed NEXT lines it was supposed to catch. It catches 0 of 4.**

    R1027 -> R921/R918 certification            green
    R1028 -> R472_the_register_half_complies    green
    R1029 -> assurance/register_requirements.py green
    R1030 -> preflight already accepted --next  green

⛔ AND THE CALIBRATION PASSED, WHICH IS THE WHOLE LESSON. Its POSITIVE control fires — because I
   wrote the control's text to contain R472's title words. The real R1028 NEXT says "whether each
   entry names a requirement"; R472's title says "the register half complies". **Same subject,
   different words.** That is §4's row verbatim: *a control validated only against cases you
   invented is validated against your imagination* — committed while building the repair for a
   different failure.

⭐ WHY NO LEXICAL GATE REACHES THIS. Prior art in this repository is SEMANTIC. A round is named for
   its question, a NEXT is written in fresh prose, and the two describe one subject with disjoint
   vocabulary. Substring matching (`next_gradient_is_new`), path indexing, separator normalisation
   and title-word overlap were each tried and each fails on the same gap. Lowering the threshold
   does not help: at a permissive setting everything matches everything, which R1030 already
   measured as a manufactured 7/7.

⚠ NOT WIRED INTO `preflight.py`, DELIBERATELY. A gate with measured recall 0/4 that exits 0 would
   manufacture assurance — §4's `check that cannot fail`, installed on purpose. The honest state is
   that this defect has no mechanical detector, and the only thing that has ever caught it is
   reading the round listing before writing the NEXT.

⚠ WHAT DID WORK, AND IT IS NOT CODE: `preflight.py` already accepts `--next`, and
   `preflight_log.jsonl` records `next_checked` — 4 of 15, with a clean split (R1019–R1021: 4 of 4;
   R1022–R1030: 0 of 11) at exactly the point the session's context was compacted. The capability
   never degraded; the memory of it did.

The implementation below is kept intact so a later round can attack it rather than rebuild it.
"""

from __future__ import annotations
import pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
E05 = ROOT / "E05_the_space_of_compilers"
THRESHOLD = 0.80          # share of a round title's content words that must appear in the NEXT
MIN_WORDS = 3             # below this a title is too generic to be evidence of anything
STOP = {"the", "a", "an", "is", "are", "was", "were", "of", "in", "on", "to", "and", "or", "it",
        "its", "this", "that", "at", "by", "for", "not", "no", "does", "do", "did", "can", "any",
        "what", "which", "how", "why", "with", "from", "be", "been", "has", "have", "had", "as",
        "own", "one", "two", "all", "we", "i", "my", "you", "there", "their", "them", "they"}


def rounds():
    """every round directory as (id, content-words) — the form prior art actually takes here."""
    out = []
    for p in sorted(E05.glob("A*/R*")):
        if not p.is_dir():
            continue
        m = re.match(r"R(\d+)_(.+)", p.name)
        if not m:
            continue
        words = [w for w in re.split(r"[^a-z0-9]+", m.group(2).lower()) if w and w not in STOP]
        out.append((int(m.group(1)), p.name, words))
    return out


def overlaps(text, rs, before=None):
    """rounds whose title's content words are >= THRESHOLD contained in `text`"""
    t = set(re.split(r"[^a-z0-9]+", text.lower()))
    hits = []
    for num, name, words in rs:
        if before is not None and num >= before:
            continue
        if len(words) < MIN_WORDS:
            continue
        share = sum(w in t for w in words) / len(words)
        if share >= THRESHOLD:
            hits.append((num, name, round(share, 3)))
    return sorted(hits, key=lambda x: -x[2])


def cited(text, num):
    return re.search(rf"\bR0*{num}\b", text) is not None


def main() -> int:
    text = " ".join(a for a in sys.argv[1:] if a.strip())
    rs = rounds()
    if not rs:
        print("  UNRUNNABLE: no round directories found. Exit 2, never 0.")
        return 2
    if not text.strip():
        print("  UNRUNNABLE: no NEXT text given; a blank line cannot be checked. Exit 2, never 0.")
        return 2

    # ---------- CALIBRATION, before any verdict: the threshold must separate KNOWN cases ----------
    # R1029's NEXT proposed a typed entry template; R472 is the prior art. Both strings are
    # committed, so this is a positive control with a known answer rather than an invented one.
    pos_text = ("re-score the register on whether each entry names a requirement, the register "
                "half complies")
    neg_text = ("measure whether the judge's logit gap is calibrated against human disagreement on "
                "unrelated corpora")
    pos = overlaps(pos_text, rs)
    neg = overlaps(neg_text, rs)
    pos_ok = any("register_half_complies" in n for _i, n, _s in pos)
    neg_ok = not neg
    empty_ok = not overlaps("", rs)
    print(f"  CALIBRATION — the threshold must separate two cases whose answer is KNOWN:")
    print(f"     POSITIVE  a NEXT restating R472's subject must find it            : "
          f"{'PASS' if pos_ok else '⛔ FAIL'}  {[n for _i, n, _s in pos][:2]}")
    print(f"     NEGATIVE  a NEXT about an unrelated subject must find nothing     : "
          f"{'PASS' if neg_ok else '⛔ FAIL'}  {[n for _i, n, _s in neg][:2]}")
    print(f"     g=0       the empty string must find nothing, not everything      : "
          f"{'PASS' if empty_ok else '⛔ FAIL'}")
    if not (pos_ok and neg_ok and empty_ok):
        print("  the threshold does not separate the known cases. Exit 2, never 0.")
        return 2

    hits = overlaps(text, rs)
    uncited = [(n, nm, s) for n, nm, s in hits if not cited(text, n)]
    print(f"\n  {len(rs)} round directories searched · {len(hits)} overlap at "
          f"share >= {THRESHOLD}")
    for n, nm, s in hits[:8]:
        print(f"     R{n:<6}{s:>6}  {nm[:64]}   {'CITED' if cited(text, n) else '⛔ NOT CITED'}")

    if uncited:
        print(f"\n  ⛔ RED — {len(uncited)} earlier round(s) share this NEXT's subject and are NOT "
              f"named in it.")
        print(f"     Naming the round is the whole remedy and costs one clause. This gate does NOT")
        print(f"     ask you to abstain: R1027–R1029 each produced a real result on an existing")
        print(f"     subject, and the cost was the part of each round spent rediscovering it.")
        return 1

    if hits:
        print(f"\n  GREEN — every overlapping round is cited in the NEXT.")
        return 0
    print(f"\n  ⚠ UNVERIFIED, not clean — no round TITLE overlaps this NEXT's wording. A subject can")
    print(f"     exist under words a title never used, so silence here is the absence of evidence")
    print(f"     and not evidence of novelty. This gate rules on PRESENCE of uncited prior art only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
