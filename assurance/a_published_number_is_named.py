#!/usr/bin/env python3
"""A number a round PUBLISHES must sit at a path that names it in the round's own words.

⛔ WHY THIS GATE EXISTS, measured not supposed. R948 established that the definition's numbers are
attributable to the round that produced them: 0.831 against a mis-attribution floor of [0.338,
0.353], and 13/13 against 0/13 where the citation window is well-posed. R949 then asked the question
that actually matters to a reader — does the cited round hold the value FOR THE QUANTITY the sentence
claims — and found agreement of 0.200 against a within-round permutation floor of [0.096, 0.139].
Separated, so a real signal; and far below a ceiling of 0.983, so nearly all of the gap is real
divergence rather than unusable keys.

**The diagnosis was disjoint naming.** `cells[0].gap` holds the number the statement calls a *price*.
Both are correct and they share no word, so no lexical bridge can verify quantity-level attribution
and the residual needs a human read — per number, forever.

⭐ **THIS GATE STOPS THE DIVERGENCE GROWING.** It cannot repair 900 committed rounds and does not
try; a gate that fails on all history is a gate nobody runs. It binds from a floor round number
onward: if a round's README states a number, the round's artifact must hold that number at a path
whose name shares vocabulary with how the README says it.

⛔ **AND THE RULE MUST NOT READ THE STATEMENT.** The tempting version — rename artifact keys to
whatever the sentence calls them — makes agreement 1.0 by construction. That is a derivation wearing
a measurement's clothes. So the two sides come from two authors' independent acts: the README
sentence is prose the round wrote about its finding, and the path is the schema the round wrote for
its data. **The gate checks they agree; it never manufactures the agreement.**

⚠ PROXY LEDGER, because this check is sound in one direction only:
  PROPERTY   : a reader can tell which quantity a published number is
  PROXY      : the holding path shares a stemmed token with the README phrase around the number
  IMPLICATION: shares a token => the names are related. **No shared token does NOT imply unnamed** —
               `gap` and `price` can both be right.
  SAFE SIDE  : a non-match is reported as UNNAMED-BY-THIS-CHECK and the gate FAILS on it, because
               this is a forward-looking convention rather than a verdict about correctness. The
               remedy for a false positive is to name the key, which costs a word and is the point.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from covalx.rounds import iter_round_dirs  # noqa: E402  -- depth is expressed once, in that module

# ⛔ THE GLOB IS NOT HARD-CODED HERE, and the first draft of this file got it wrong in the exact
# documented way. `E0*/A*/R*` misses `E99_fixtures/A01_planted`, where every attack harness plants,
# so the lock would have been untestable and its attack would have reported vectors it never ran --
# R928's failure, reproduced by a gate written after reading R928. `covalx/rounds.py` exists so a
# gate that asks it cannot be wrong about where a round lives.
FLOOR_ROUND = 950          # binds from R950 on; history is out of scope and says so
PROVISIONAL = re.compile(r"smoke|dry[_-]?run|draft|scratch|trial|pilot|prelim|wip", re.I)
NUMERAL = re.compile(r"(?<![\w.])(\d+\.\d{3,})(?![\w])")
WORD = re.compile(r"[a-z]{3,}")
STOP = {"the", "and", "not", "for", "that", "this", "with", "its", "was", "are", "under", "than",
        "every", "each", "from", "one", "two", "all", "but", "has", "have", "own", "same", "only",
        "any", "how", "what", "which", "when", "then", "also", "into", "over", "out", "per", "see",
        "does", "did", "can", "cannot", "must", "here", "there", "they", "them", "their", "it",
        "round", "results", "artifact", "value", "number"}


def toks(s):
    return {w for w in WORD.findall(s.lower()) if w not in STOP}


def stem(w):
    for suf in ("ing", "ed", "es", "s"):
        if len(w) > 4 and w.endswith(suf):
            return w[: -len(suf)]
    return w


def stems(ws):
    return {stem(w) for w in ws}


def paths_holding(doc, want, d, prefix=""):
    out = []
    if isinstance(doc, dict):
        for k, v in doc.items():
            out += paths_holding(v, want, d, f"{prefix}.{k}" if prefix else k)
    elif isinstance(doc, list):
        for i, v in enumerate(doc):
            out += paths_holding(v, want, d, f"{prefix}[{i}]")
    elif isinstance(doc, bool):
        pass
    elif isinstance(doc, (int, float)):
        if round(float(doc), d) == want:
            out.append(prefix)
    elif isinstance(doc, str):
        for m in NUMERAL.finditer(doc):
            if round(float(m.group(1)), d) == want:
                out.append(prefix)
                break
    return out


def path_tokens(paths):
    if not paths:
        return set()
    return stems(set().union(*[toks(p.replace(".", " ").replace("_", " ")) for p in paths]))


def audit_round(d: pathlib.Path):
    """-> (rows, n_readme_numbers). One row per README number that the artifact also holds."""
    readme = d / "README.md"
    if not readme.exists():
        return [], 0
    text = readme.read_text(errors="replace")
    docs = []
    for f in sorted(d.glob("results/**/*.json")):
        if PROVISIONAL.search(f.name) or "_smoke_archive" in f.parts:
            continue
        try:
            docs.append(json.loads(f.read_text()))
        except Exception:
            continue
    rows, seen = [], set()
    flat = " ".join(text.splitlines())
    for m in NUMERAL.finditer(flat):
        s = m.group(1)
        if s in seen:
            continue
        seen.add(s)
        dgt = len(s.split(".")[1])
        want = round(float(s), dgt)
        hits = [p for doc in docs for p in paths_holding(doc, want, dgt)]
        if not hits:
            continue                        # stated but not in the artifact: a different gate's job
        phrase = flat[max(0, m.start() - 60): m.end() + 60]
        rows.append({"numeral": s, "paths": sorted(set(hits))[:4], "phrase": phrase.strip(),
                     "named": bool(path_tokens(sorted(set(hits))) & stems(toks(phrase)))})
    return rows, len(seen)


def main() -> int:
    rounds = []
    for d in iter_round_dirs(ROOT):
        m = re.match(r"[Rr](\d+)_", d.name)
        if m and int(m.group(1)) >= FLOOR_ROUND:
            rounds.append(d)
    print(f"a published number is named — binds from R{FLOOR_ROUND} onward, "
          f"{len(rounds)} round(s) in scope")

    if not rounds:
        print("  EMPTY POPULATION: no round at or above the floor. A gate that examines nothing "
              "must not pass.")
        print("  Exit 2, never 0.")
        return 2

    bad, total, examined = [], 0, 0
    for d in rounds:
        rows, n_stated = audit_round(d)
        if not rows:
            print(f"  {d.name:<52} no README number is held by the artifact — SKIPPED "
                  f"({n_stated} stated)")
            continue
        examined += 1
        named = sum(r["named"] for r in rows)
        total += len(rows)
        print(f"  {d.name:<52} {named}/{len(rows)} named")
        for r in rows:
            if not r["named"]:
                bad.append((d.name, r))
                print(f"     UNNAMED  {r['numeral']:<12} at {r['paths'][:2]}")
                print(f"              README says: …{r['phrase'][:88]}…")

    if not examined:
        print("\n  EMPTY POPULATION: every in-scope round was skipped, so nothing was checked.")
        print("  Exit 2, never 0.")
        return 2

    if bad:
        print(f"\n{len(bad)} of {total} published numbers sit at a path that shares no word with "
              f"the sentence stating them.")
        print("  Name the key as the README names the quantity. `cells[0].gap` for what the text "
              "calls a price is how R949 measured 0.200 agreement across 115 pairs.")
        print("  ⚠ UNNAMED-BY-THIS-CHECK is not `wrong`: `gap` and `price` can both be correct. "
              "This is a forward-looking convention, and the remedy costs one word.")
        return 1

    print(f"\nAll {total} published numbers across {examined} round(s) sit at a path that names "
          f"them in the round's own words.")
    print("  This says nothing about whether the number is RIGHT — only that a reader can tell "
          "which quantity it is.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
