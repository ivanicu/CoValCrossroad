#!/usr/bin/env python3
"""
R943 · the gate that guarantees a proxy-scored outcome is declared matches 13 rounds by a five-token
        regex, while 26 rounds load model machinery it never names — bound the blind side.

⛔ WHY THIS AND NOT ANOTHER HARNESS REPAIR. R928–R942 have all been instrument work, and §0.2 is
explicit that a programme auditing only itself produces nothing about its object. This round is on
the instrument **because the instrument is load-bearing for the deliverable**:
`assurance/outcome_variable_declared.py` is what guarantees every published number says whether a
MODEL scored it. `DEFINITION.md` already carries the finding that 10 of 11 claims are
instrument-dependent on a local 2B judge — **that bookkeeping is only as good as this gate's recall.**

⭐ **R942 MEASURED THE FALSE-POSITIVE DIRECTION AND FOUND ONE INSTANTLY** — the gate flags R942
itself, because `USES_GOLD` matched the literal `gold_fresh` that R942 WRITES INTO A FIXTURE and
never executes. A source-text regex cannot separate **mention** from **use**. That is a nuisance:
over-flagging costs a sentence, which the gate's own comment says it accepts.

⭐⭐⭐ **THE OTHER DIRECTION IS THE ONE THAT CAN CORRUPT THE DELIVERABLE.** `USES_GOLD` is five
alternatives — `a08_gold|gold_orig|gold_fresh|def gold\\(|--gold\\b` — naming ONE proxy by the file
it ships in. A round scoring against any other model outcome is invisible, publishes a number, and
the gate reports the corpus clean. The harness calls this *"a KNOWN OPEN HOLE"* in a footer and
attaches no number to it. **A named hole with no measurement is a hole nobody has to act on.**

⚠ **AND THE UNIT GAP IS ONLY PARTLY CLOSED HERE, WHICH IS WHY THE ANSWER IS A BOUND.**
  instrument unit : the round's `run.py` REFERENCES a proxy route outside strings and comments
  claim unit      : the round SCORES ITS OUTCOME against a model proxy
These are not equal. An AST pass fixes *mention vs use*; nothing here fixes *use vs scores-the-
outcome-with-it*. So the blind set is reported as an UPPER BOUND on candidates requiring a read, and
NOT as a count of undeclared rounds. Reporting it as the latter is the mistake this arc keeps
finding, and it would be the flattering direction — a bigger number for the gate's defect.

ESTIMAND        (a) of the rounds `USES_GOLD` matches, how many match only inside a string or a
                comment — the false-POSITIVE count; (b) how many rounds reference a model-proxy route
                the regex cannot name, outside strings and comments — an upper bound on the
                false-NEGATIVE candidates.
IDENTIFICATION  (a) exact: `ast` + `tokenize` give the byte spans of every string and comment, and a
                match is inside one or it is not. (b) PARTIAL: the route list is itself a regex, so
                it bounds rather than counts. Bounds, not a point, per G1.
SCOPE           population: every `E0*/A*/R*/run.py` in the repo — 889 files, enumerated not sampled
                instrument: the gate's own `USES_GOLD`, plus a route probe, both AST-filtered
                baseline:   the gate's committed behaviour: 13 raw matches, 3 rounds flagged
                regime:     HEAD, one release, one repo
WORLDS          A · the blind set is non-empty and some of its members publish results -> the gate's
                    recall is bounded well below 1, `DEFINITION.md`'s instrument bookkeeping rests on
                    a regex that names one proxy, and the footer's `known open hole` has a size
                B · the blind set is empty, or none of it publishes -> the five tokens happen to
                    cover every proxy route in this corpus, the hole is theoretical, and the gate's
                    recall is 1 on the population that matters
⛔ **AND MY FIRST TWO CONTROLS WERE CIRCULAR, WHICH READING THE OBJECT CAUGHT BEFORE THE RUN.** They
asserted `R422` and `R425` must classify as USE *because the gate flags them* — i.e. the classifier
was to be validated against the instrument it is auditing. Reading the two files kills the premise:
R422's only occurrence is at `run.py:113`, inside its docstring; R425's are docstring prose plus
`GOLD = re.compile(...)` at `:112`, a string literal in a round whose job is to CLASSIFY other
rounds' gold usage. **Neither loads the file. All three rounds the gate flags at HEAD are mentions.**
A control whose ground truth comes from the thing under test cannot fail in the direction that
matters — so both positives are now PLANTED, where the answer is known by construction.

KILL            CONDITIONAL — the classifier is checked on PLANTED sources with known ground truth,
                in both directions, because corpus cases inherit the gate's own verdict:
                  ⭐ ① POSITIVE / USE SIDE, PLANTED: a source with a module-level `np.load` of the
                     gold file must classify USE. ⚠ AND IT MUST FAIL AT g=0: the identical source
                     with that one line deleted must have NO match outside strings and comments.
                     A positive control that passes before the plant is the failure mode this file
                     opens with.
                  ⭐ ② POSITIVE / MENTION SIDE, PLANTED AND REAL: a source carrying the token only in
                     a docstring, a comment and a string constant must classify MENTION — and the
                     real `R942` must too, whose answer R942 measured independently: its only
                     occurrence is a literal it writes into a fixture and never executes.
                     **Two directions, and the plant's ground truth does not come from the gate.**
                  ⭐ ③ POPULATION CLOSED: matched + route-only + neither must equal the file count,
                     and unparseable files must be COUNTED and NAMED, never silently dropped. A gate
                     that examines nothing passes; so does an audit that drops what it cannot read.
                  ⭐ ④ UNITS DECLARED AND UNEQUAL: printed before any number, with the consequence
                     stated — the blind set is a bound on CANDIDATES, not a count of defects.
                  ⭐ ⑤ every candidate named, and the ones WITH published results separated from the
                     ones without, because only the former can reach a claim.
MULTIPLICITY    889 files × {gold-regex, route-probe} × {inside-string-or-comment, outside} — no
                selection, no threshold, nothing to correct; the whole population is reported.
ARTIFACT        results/blind_side.json
IMPOSSIBLE      independently replicated · cross-release · construct validated · criterion validated —
                one repo, one release; a second site would be required. ⚠ AND: `use vs scores-the-
                outcome-with-it` is NOT resolvable by any static pass. Closing it needs a read of each
                candidate, which is the next round's work and is named here rather than assumed away.
"""
import ast, io, json, pathlib, re, subprocess, tokenize

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)

INSTRUMENT_UNIT = "run.py references a proxy route outside strings and comments"
CLAIM_UNIT = "the round scores its outcome against a model proxy"

# the gate's own regex, transcribed from assurance/outcome_variable_declared.py:49
USES_GOLD = re.compile(r"a08_gold|gold_orig|gold_fresh|def gold\(|--gold\b")
# routes the gate cannot name. deliberately broad: this BOUNDS the blind side, it does not count it.
ROUTE = re.compile(r"AutoModel|from_pretrained|\.safetensors|reward_model|judge_model|"
                   r"score_model|cross_encoder|AutoTokenizer|sentence_transformers|"
                   r"SentenceTransformer|\.gguf|llama_cpp|vllm")


def masked_spans(src: str):
    """byte spans of every string literal and every comment — where a token is MENTIONED, not used"""
    spans, lines = [], src.splitlines(keepends=True)
    offs, t = [0], 0
    for l in lines:
        t += len(l)
        offs.append(t)

    def abs_off(row, col):
        return offs[row - 1] + col

    tree = ast.parse(src)
    for n in ast.walk(tree):
        if isinstance(n, ast.Constant) and isinstance(n.value, str) and n.end_lineno:
            spans.append((abs_off(n.lineno, n.col_offset), abs_off(n.end_lineno, n.end_col_offset)))
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type == tokenize.COMMENT:
                spans.append((abs_off(tok.start[0], tok.start[1]),
                              abs_off(tok.end[0], tok.end[1])))
    except (tokenize.TokenError, IndentationError):
        pass                       # comments only refine the mask; a partial mask is reported below
    return spans


def classify(src: str, rx: re.Pattern):
    """-> (n_matches, n_outside_strings_and_comments). outside > 0 means USE, else MENTION."""
    hits = list(rx.finditer(src))
    if not hits:
        return 0, 0
    spans = masked_spans(src)
    outside = sum(1 for m in hits
                  if not any(a <= m.start() < b for a, b in spans))
    return len(hits), outside


PLANT_USE = ('''"""a docstring mentioning a08_gold and nothing else"""
import numpy as np
# a comment mentioning gold_orig
SRC = "gold_fresh = 1"
gold_orig = np.load("a08_gold_08b.npz")
''')
PLANT_G0 = "\n".join(l for l in PLANT_USE.splitlines() if not l.startswith("gold_orig =")) + "\n"
PLANT_MENTION = PLANT_G0


def main() -> int:
    print(f"  ④ UNITS — instrument: `{INSTRUMENT_UNIT}`")
    print(f"          claim:      `{CLAIM_UNIT}`")
    print(f"          equal: {INSTRUMENT_UNIT == CLAIM_UNIT}  -> the blind set below is an UPPER "
          f"BOUND on candidates requiring a read, NOT a count of undeclared rounds")

    files = sorted(ROOT.glob("E0*/A*/R*/run.py"))
    if not files:
        print("  UNRUNNABLE: empty population. Exit 2, never 0.")
        return 2

    gold_use, gold_mention, route_use, unparseable, neither = [], [], [], [], 0
    for f in files:
        src = f.read_text(errors="replace")
        rnd = f.parent.name
        try:
            g_n, g_out = classify(src, USES_GOLD)
            r_n, r_out = classify(src, ROUTE)
        except SyntaxError as e:
            unparseable.append({"round": rnd, "error": str(e).split("(")[0].strip()})
            continue
        if g_n and g_out:
            gold_use.append(rnd)
        elif g_n:
            gold_mention.append(rnd)
        if r_out and not (g_n and g_out):
            route_use.append(rnd)
        if not g_n and not r_out:
            neither += 1

    closed = len(gold_use) + len(gold_mention) + len(route_use) + neither + len(unparseable)
    # a round can be BOTH gold-mention and route-use; count the overlap so the ledger is honest
    overlap = len(set(gold_mention) & set(route_use))
    c3 = (closed - overlap) == len(files)
    print(f"\n  ③ POPULATION CLOSED — {len(files)} files = gold-USE {len(gold_use)} + gold-MENTION "
          f"{len(gold_mention)} + route-only {len(route_use)} + neither {neither} + unparseable "
          f"{len(unparseable)} - overlap {overlap} = {closed - overlap}: {c3}  "
          f"{'PASS' if c3 else 'FAIL'}")
    if unparseable:
        print(f"     unparseable, NAMED not dropped: {[u['round'][:34] for u in unparseable]}")

    def has(lst, pfx):
        return any(r.startswith(pfx) for r in lst)

    pu_n, pu_out = classify(PLANT_USE, USES_GOLD)
    g0_n, g0_out = classify(PLANT_G0, USES_GOLD)
    c1 = pu_out > 0 and g0_out == 0
    print(f"\n  ① POSITIVE / USE SIDE, PLANTED — planted source: {pu_n} matches, {pu_out} outside "
          f"strings and comments (must be >0); the SAME source with the load line deleted: {g0_n} "
          f"matches, {g0_out} outside (must be 0): {c1}")
    print(f"     {'PASS — recovers a planted use AND does not fire at g=0' if c1 else 'FAIL'}")

    pm_n, pm_out = classify(PLANT_MENTION, USES_GOLD)
    c2 = (pm_n > 0 and pm_out == 0) and has(gold_mention, "R942") and not has(gold_use, "R942")
    print(f"  ② POSITIVE / MENTION SIDE, PLANTED AND REAL — planted mention-only source: {pm_n} "
          f"matches, {pm_out} outside (must be 0); and the real R942 classifies MENTION "
          f"{has(gold_mention, 'R942')}: {c2}")
    print(f"     {'PASS — a docstring, a comment and a string constant are all masked' if c2 else 'FAIL'}")

    print(f"\n  ⛔ AND THE ROUNDS THE GATE ACTUALLY FLAGS AT HEAD — R422, R425, R942 — classify as: "
          f"{[('USE' if has(gold_use, p) else 'MENTION' if has(gold_mention, p) else 'no match') for p in ('R422', 'R425', 'R942')]}")

    if not (c1 and c2 and c3):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "c1": c1, "c2": c2, "c3": c3,
                   "gold_use": gold_use, "gold_mention": gold_mention,
                   "route_only": route_use, "unparseable": unparseable},
                  open(OUT / "blind_side.json", "w"), indent=2)
        return 2

    published = [r for r in route_use
                 if any((ROOT.glob(f"E0*/A*/{r}/results/**/*.json")))]
    silent = [r for r in route_use if r not in published]

    print(f"\n  ⑤ EVERY CANDIDATE NAMED — {len(route_use)} rounds reference a proxy route the gate's "
          f"five tokens cannot name:")
    print(f"     WITH published results ({len(published)}) — these can reach a claim:")
    for r in published:
        print(f"        {r}")
    print(f"     WITHOUT results ({len(silent)}) — cannot reach a claim:")
    for r in silent:
        print(f"        {r}")
    print(f"\n     FALSE POSITIVES of the gate ({len(gold_mention)}) — the token appears only inside "
          f"a string or a comment: {gold_mention}")

    world = "A" if published else "B"
    seen = len(gold_use)
    print(f"\n  ⭐⭐⭐ WORLD {world}: the gate sees {seen} round(s) by USE of its five tokens; "
          f"{len(route_use)} more reference a proxy route it cannot name, {len(published)} of them "
          f"with published results.")
    if world == "A":
        print(f"     So its recall over `references a proxy route` is at most "
              f"{seen}/{seen + len(route_use)} = {seen/(seen+len(route_use)):.2f}, and the footer's "
              f"`KNOWN OPEN HOLE` has a size for the first time.")
        print(f"     ⚠ AT MOST, NOT EXACTLY: referencing a route is not scoring an outcome with it, "
              f"and no static pass can close that. Each of the {len(published)} needs a read before "
              f"any of them is called undeclared. That read is the next round, not this one.")
    else:
        print(f"     The five tokens cover every proxy route in this corpus that publishes, so the "
              f"hole is theoretical here and the gate's recall is 1 on the population that matters.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world,
               "n_files": len(files),
               "units": {"instrument": INSTRUMENT_UNIT, "claim": CLAIM_UNIT, "equal": False,
                         "consequence": "the blind set is an upper bound on candidates, not a "
                                        "count of undeclared rounds"},
               "gate_sees_by_use": gold_use,
               "rounds_the_gate_flags_at_head": {
                   p: ("USE" if any(r.startswith(p) for r in gold_use)
                       else "MENTION" if any(r.startswith(p) for r in gold_mention)
                       else "no match") for p in ("R422", "R425", "R942")},
               "controls_are_planted_because":
                   "corpus cases inherit the gate's own verdict; a control validated against the "
                   "instrument it audits cannot fail in the direction that matters",
               "gate_false_positives_mention_only": gold_mention,
               "route_only_candidates": route_use,
               "route_only_with_results": published,
               "route_only_without_results": silent,
               "neither": neither,
               "unparseable": unparseable,
               "recall_upper_bound": (len(gold_use) / (len(gold_use) + len(route_use))
                                      if route_use else 1.0),
               "recall_is_an_upper_bound_because":
                   "referencing a proxy route is not scoring an outcome against it; closing that "
                   "needs a read of each candidate, which no static pass can do",
               "route_probe_is_itself_a_regex":
                   "so the candidate set is also a lower bound on the true blind population",
               "unit_note": "counts are ROUNDS (directories with a run.py)",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "blind_side.json", "w"), indent=2)
    print(f"\n  artifact: results/blind_side.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
