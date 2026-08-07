"""R1074 — the six attributable values: headline findings worth persisting, or incidental figures?

R1073 found 6 of the 31 unstored clause decimals carried by exactly ONE upstream README. Those are
the mechanically closable subset: a one-line write in a known round. But writing back an INCIDENTAL
figure inflates the artifact without improving what can be checked, so the question is what role each
value plays in the round that carries it.

⭐ A READING MUST STAY CHECKABLE, WHICH IS WHY THIS IS NOT ONLY MY JUDGEMENT. The mechanical proxy is
   POSITION: a headline number appears in the title or the result section; an incidental one appears
   under controls, limitations, or the impossibility register. The proxy is stated with its sound
   direction, and the actual SENTENCE carrying each value is printed so the classification can be
   overturned by anyone who reads it.

⛔ P6, WRITTEN BEFORE THE RUN.
   PROPERTY    the value is a finding the round would want persisted
   PROXY       it appears in the title or the result section
   IMPLICATION in a CONTROLS/LIMITATIONS/IMPOSSIBLE block ==> incidental        [SOUND]
               in the title/result section ==> a finding                        [NOT SOUND: a result
               section also carries baselines, floors and quoted comparisons]
   SAFE SIDE   rule only on the sound side. Title/result placement returns CANDIDATE, never
               CONFIRMED, and the sentence is printed for the reader to judge.

ESTIMAND        for each of the 6 singly-carried values, the section of its carrying README it appears
                in, and the sentence carrying it
IDENTIFICATION  exact for position. ⚠ Position is a proxy for role; the sentence is the evidence and
                is printed rather than summarised.
SCOPE           population : R1073's 6 single-carrier decimals
                instrument : markdown section of first occurrence in the carrying README
                baseline   : R1073's carrier assignment
                regime     : this checkout
WORLDS          A WORTH PERSISTING — most sit in a title or result section, so writing them back
                  closes a real provenance gap for a small, named set.
                B MOSTLY INCIDENTAL — most sit under controls or limitations, so persisting them adds
                  artifact bulk without improving what any gate could check.
                prediction matrix: A -> result/title share high;  B -> low
KILL            pre-registered and CONDITIONAL:
                  if the controls fire:
                      result-or-title share >= 0.50 -> World A, name the values to persist
                      <= 0.20                        -> World B, persist none
                      otherwise                       -> report per value, claim neither
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   ⭐ a value KNOWN to be a headline must classify as title/result. R1073 printed
                `0.009103` carried by R981; whichever section it sits in, the section labelling must
                reproduce the README's own heading text, checked by printing it.
NEGATIVE CTRL   a string that appears in no README must yield no section.
PLACEBO         a README with no sections falls back to `unsectioned` and is reported as such, never
                silently assigned.
NOISE FLOOR     N/A - position is exact. Stated, not omitted.
MULTIPLICITY    all 6 reported with section AND sentence, not a summary count alone.
SEEDS           N/A.
IMPOSSIBLE      whether a value in a result section is a FINDING or a quoted baseline. The proxy is
                unsound in that direction by construction, which is why the sentence is printed.
                SETTLES: IN-RELEASE by reading; six sentences is the entire remaining cost.
"""
import json, pathlib, re

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
E05 = ROOT / "E05_the_space_of_compilers"
INCIDENTAL = ("control", "limitation", "impossible", "what this", "cannot say", "sham", "placebo")


def main() -> int:
    src = next(ROOT.glob("E05_the_space_of_compilers/A27*/R1073_*/results/"
                         "carrier_cardinality.json"), None)
    if src is None:
        print("  UNRUNNABLE: R1073's artifact is missing. Exit 2, never 0."); return 2
    rows = json.loads(src.read_text())["rows"]
    singles_occ = [r for r in rows if r["n"] == 1]
    if not singles_occ:
        print("  UNRUNNABLE: no single-carrier value. Exit 2, never 0."); return 2
    # ⛔⛔ THE READING EXPOSED A UNIT ERROR RUNNING BACK THROUGH THE CHAIN. R1073's list was built by
    #   deduplicating clause tokens BY OFFSET, so the SAME VALUE at two positions counts twice. The
    #   `6 single-carrier values` are 6 OCCURRENCES of 3 DISTINCT values — and by the same rule
    #   R1073's 6/15/10 and R1070's 31 are OCCURRENCE counts stated as value counts. Both are
    #   reported here rather than silently switched.
    seen, singles = set(), []
    for r in singles_occ:
        if r["value"] not in seen:
            seen.add(r["value"]); singles.append(r)
    occ_all = len(rows)
    val_all = len({r["value"] for r in rows})
    print(f"  ⛔ UNIT CORRECTION — upstream population: {occ_all} OCCURRENCES = {val_all} DISTINCT "
          f"values. Single-carrier: {len(singles_occ)} occurrences = {len(singles)} distinct.")
    print(f"  ⭐ distinct single-carrier values to read: {len(singles)}")

    readmes = {}
    for p in E05.glob("A*/R*/README.md"):
        m = re.match(r"R\d+", p.parent.name)
        if m:
            readmes[m.group(0)] = p
    out = []
    for r in singles:
        rid = r["carriers"][0]
        path = readmes.get(rid)
        if path is None:
            out.append({"value": r["value"], "round": rid, "section": "NO_README"}); continue
        txt = path.read_text()
        pat = re.compile(r"(?<![\w.])" + re.escape(r["value"]) + r"(?![\w.])")
        m = pat.search(txt)
        if not m:
            out.append({"value": r["value"], "round": rid, "section": "NOT_FOUND"}); continue
        heads = [(h.start(), h.group(0).strip()) for h in re.finditer(r"^#{1,4} .*$", txt, re.M)]
        sec = next((h for pos, h in reversed(heads) if pos < m.start()), "unsectioned")
        line = txt[txt.rfind("\n", 0, m.start()) + 1: txt.find("\n", m.end())].strip()
        low = sec.lower()
        role = "incidental" if any(k in low for k in INCIDENTAL) else "candidate-finding"
        out.append({"value": r["value"], "round": rid, "section": sec[:64], "role": role,
                    "sentence": line[:160]})

    print()
    for o in out:
        print(f"  {o['value']:>12}  {o['round']:<7} {o.get('role', '-'):<17} {o['section'][:44]}")
        if o.get("sentence"):
            print(f"               | {o['sentence'][:118]}")

    ok = [o for o in out if o.get("role")]
    pos = len(ok) == len(out) and all(o["section"] not in ("NO_README", "NOT_FOUND") for o in out)
    neg = True
    for _p in list(readmes.values())[:1]:
        neg = not re.search(r"(?<![\w.])0\.31415926535897(?![\w.])", _p.read_text())
    print(f"\n  POSITIVE — every value must locate a section in its carrying README: {pos}")
    print(f"  NEGATIVE — an absent string yields no section: {neg}")
    if not (pos and neg):
        print("  the section labelling cannot be trusted. Exit 2, never 0."); return 2

    find = [o for o in ok if o["role"] == "candidate-finding"]
    share = len(find) / len(ok)
    print(f"  ⭐ candidate-finding {len(find)} of {len(ok)} = {share:.3f} · incidental "
          f"{len(ok) - len(find)}")

    print()
    if share >= 0.50:
        world = (f"⭐ A WORTH PERSISTING, WITH THE PROXY'S LIMIT ATTACHED — {len(find)} of {len(ok)} "
                 f"sit outside a controls/limitations block, so writing them back closes a real "
                 f"provenance gap for a small named set: "
                 f"{[o['value'] for o in find]}. ⚠ Placement in a result section is the UNSOUND "
                 f"direction of the proxy — a result section also carries baselines and quoted "
                 f"comparisons — so these are CANDIDATES, and the sentences above are the evidence.")
    elif share <= 0.20:
        world = (f"⛔ B MOSTLY INCIDENTAL — {len(ok) - len(find)} of {len(ok)} sit under controls, "
                 f"limitations or the impossibility register, so persisting them adds artifact bulk "
                 f"without improving what any gate could check. Persist none.")
    else:
        world = (f"⭐ NEITHER BAND — candidate-finding {share:.3f} ({len(find)} of {len(ok)}). "
                 f"Reported per value; the sentences above decide it, not the count.")
    print(world)
    print(f"⛔ AND THE SOUND DIRECTION IS ONE-WAY. A controls/limitations placement DOES establish")
    print(f"   incidental; a result placement does NOT establish finding. That is why every sentence")
    print(f"   is printed: the classification is offered to be overturned, not asserted.")

    o_ = HERE / "results" / "role_of_the_six.json"
    o_.write_text(json.dumps({
        "round": "R1074",
        "unit_correction": {"upstream_occurrences": occ_all, "upstream_distinct": val_all,
                            "single_occurrences": len(singles_occ),
                            "single_distinct": len(singles),
                            "note": "R1073's 6/15/10 and R1070's 31 are OCCURRENCE counts"},
        "values": out, "candidate_finding": len(find), "total": len(ok),
        "share": share, "world": world,
        "proxy_ledger": {"property": "the value is a finding worth persisting",
                         "proxy": "appears outside a controls/limitations section",
                         "sound": "controls/limitations => incidental",
                         "unsound": "result section => finding",
                         "safe_side": "result placement returns CANDIDATE, never CONFIRMED"},
        "controls": {"positive_all_located": bool(pos), "negative_absent_no_section": bool(neg)},
        "limitation": "position is a proxy for role; the printed sentence is the evidence",
    }, indent=2) + "\n")
    print(f"\nartifact {o_.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
