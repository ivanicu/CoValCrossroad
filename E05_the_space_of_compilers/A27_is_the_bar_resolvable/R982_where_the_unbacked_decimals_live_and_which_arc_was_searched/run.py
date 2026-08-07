#!/usr/bin/env python3
"""R982 — where do DEFINITION.md's unbacked decimals live, and which arc was ever searched?

⛔ WHY, AND THE PRIOR ART THAT MADE THIS ROUND POSSIBLE RATHER THAN REDUNDANT. R622 partitioned the
document's 642 decimals into T1 gate-verified (119, 18.5%), T2 anchorable-but-unenforced (507,
79.0%) and T3 unbacked (16, 2.5%). R625 then measured the floor those shares must be read against:
**an invented decimal matches an artifact value 35–38% of the time at four places, ~92% at three,
100% at two.** Both are reused here rather than re-derived, and neither is claimed as new.

⚠ TWO THINGS NOBODY HAS DONE, AND THE SECOND IS A DEFECT IN THE PRIOR ROUND.
 ① **R622 split by DOCUMENT (`DEFINITION.md` vs `STATEMENT.md`), never by HALF.** R981 has since
    shown that inside `DEFINITION.md` the 343 anchoring assertions divide 340 : 3 between the
    9,128-line evidence record and the 693-line statement a reader reads as the definition. So the
    18.5% T1 figure may be carried entirely by the half nobody reads, and that is checkable.
 ② **R622's scanner globs `A24/R*/results/*.json` — ONE ARC.** Its T3 therefore means *"absent from
    A24"*, not *"absent from every artifact"*. Every value produced by the A26 and A27 rounds the
    statement now cites — R920 through R980 — was outside its search by construction. Widening the
    scan can only move decimals OUT of T3, so R622's 16 is an UPPER bound and its direction is known.

ESTIMAND        ① the location of the T3 (unbacked, prose-only) decimals: statement half or record
                half. ② T1/T2/T3 per half, under the widened all-arc scan, with T2 read against the
                measured collision floor rather than at face value.
IDENTIFICATION  ① and ② exact given the scan: membership in a set of persisted value positions is
                decidable. ⚠ What is NOT identified is whether a T2 decimal is *the* value the
                sentence means — R949 measured that separately at 0.200 agreement — so T2 is
                "some artifact holds these digits", never "this claim is checked".
SCOPE           population : every decimal with 3 or 4 places in DEFINITION.md, split by the
                             currency gate's own `statement_region` so R981 and this read one text
                instrument : value positions in PARSED json (R622's v2 repair — raw substring
                             absorbed a fabricated number through the record of its own exposure)
                baseline   : R622's committed A24-only census, reproduced before widening
                regime     : 3–4 decimal places; the floor is ~92% at 3 and 100% at 2, so 2-place
                             decimals are EXCLUDED and the exclusion is counted
WORLDS          A HYGIENE     the unbacked decimals sit in the record. An evidence log carrying a
                              few prose numbers is untidy and not a claim about the definition.
                B THE DEFINITION CARRIES PROSE NUMBERS   they sit in the statement, so the part read
                              as the definition contains values no artifact holds.
                prediction matrix: A -> T3 concentrated in the record. B -> ≥1 T3 decimal in the
                statement region, named.
KILL            pre-registered, CONDITIONAL on the controls: 0 T3 decimals in the statement region
                ⇒ world B dead. Any ⇒ world A dead and each must be NAMED, not counted.
POSITIVE CTRL   reproduce R622 under ITS OWN scope: restricted to A24, the document census must
                return 642 / 119 / 507 / 16. An instrument that cannot re-derive a committed
                partition is not measuring this one.
NEGATIVE CTRL   a runtime-assembled decimal must land in T3 under both scans — the g=0 arm R622's
                own v1 failed, because raw text absorbed a fabricated number.
PLACEBO         a decimal drawn FROM an artifact but absent from derive() must land in T2, never T1.
NOISE FLOOR     the collision rate is RE-MEASURED here, 3 seeds × 4000 draws, rather than quoted
                from R625 — because it is the number the T2 share must be divided by.
MULTIPLICITY    every decimal classified; both halves reported; T3 members listed in full.
ARTIFACT        results/tiers_by_half.json with this file's source hash.
IMPOSSIBLE      construct validity — N/A: T1 means an artifact drift breaks the build, never that
                the number is correct. R622 states this and it is inherited, not weakened.
                cross-release — N/A: one document, one project.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import pathlib
import random
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
E05 = ROOT / "E05_the_space_of_compilers"
A24 = E05 / "A24_what_the_definition_costs"
DEF = E05 / "DEFINITION.md"
DEC = re.compile(r"(?<![\w.])(\d+\.\d{3,4})(?![\w])")
SEEDS = (1, 2, 3)
NDRAW = 4000


def load(rel, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def blob(globs):
    """value positions in PARSED json only — R622's v2 repair, reused verbatim in spirit"""
    vals, n = set(), 0

    def walk(o):
        if isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, (list, tuple)):
            for v in o:
                walk(v)
        elif isinstance(o, bool) or o is None:
            return
        elif isinstance(o, (int, float)):
            for f in (repr(o), f"{o:.4f}", f"{o:.3f}", f"{abs(o):.4f}", f"{abs(o):.3f}"):
                vals.add(f.lstrip("+"))
        elif isinstance(o, str) and DEC.fullmatch(o.strip().lstrip("+-")):
            vals.add(o.strip().lstrip("+-"))

    for g in globs:
        for f in sorted(g):
            try:
                walk(json.loads(f.read_text(errors="ignore")))
                n += 1
            except Exception:
                pass
    return vals, n


def main() -> int:
    cur = load("assurance/a_statement_is_current_with_the_arc.py", "sc")
    dm = load("assurance/definition_matches_the_record.py", "dm")
    gv = set()
    for _lbl, pair in dm.derive().items():
        v = pair[0] if isinstance(pair, (list, tuple)) else pair
        if v is None:
            continue
        for f in (repr(v), f"{v:.4f}", f"{v:.3f}") if isinstance(v, (int, float)) else (str(v),):
            gv.add(f.lstrip("+"))

    # ⛔ THIS ROUND WRITES INTO THE CORPUS IT SCANS. Two consecutive runs read 784 then 785
    #    artifacts and the record's T3 moved 7 -> 0, because run #2 saw run #1's own output. That is
    #    R947's self-contamination at a new site, and it is excluded rather than tolerated.
    SELF = HERE.resolve()
    def not_self(paths):
        return [f for f in paths if SELF not in f.resolve().parents]
    narrow, n_narrow = blob([not_self(A24.glob("R*/results/*.json"))])
    wide, n_wide = blob([not_self(E05.glob("A*/R*/results/*.json"))])
    print(f"artifacts scanned — A24 only {n_narrow}   ALL arcs {n_wide}")
    print(f"value positions   — A24 only {len(narrow)}   ALL arcs {len(wide)}")

    text = DEF.read_text()
    stmt = cur.statement_region(text)
    if stmt is None:
        print("  UNRUNNABLE: statement region did not load. Exit 2, never 0.")
        return 2
    rec = text.replace(stmt, "")

    def tier(dec, vals):
        return "T1" if dec in gv else ("T2" if dec in vals else "T3")

    def census(txt, vals):
        """⛔ THE UNIT IS A DISTINCT DECIMAL, NOT AN OCCURRENCE, AND THAT COST THREE CONTROL
        FAILURES. R622's source reads `decs = sorted(set(DEC.findall(...)))`; mine counted every
        occurrence, giving 952 where it committed 642 on the identical revision. Same regex, same
        text, different unit — the §4 remedy is to name the instrument's unit and the claim's unit
        as two strings and require them EQUAL, and here they were not."""
        c = {"T1": [], "T2": [], "T3": []}
        for dec in sorted(set(DEC.findall(txt))):
            c[tier(dec, vals)].append(dec)
        return c

    # ── POSITIVE CONTROL: reproduce R622 under ITS scope, on the WHOLE document.
    r622 = json.loads((A24 / "R622_how_much_of_the_definition_is_re_derived"
                       / "results/definition_anchoring_tiers.json").read_text())
    want = r622["per_document"]["DEFINITION.md"]
    # ⛔ v1's CONTROL COULD NOT FAIL. It compared today's document to R622's committed counts with
    #    `>=`, which passes almost anything — and it passed on 4004 against 642, a six-fold gap I
    #    would have reported as a reproduction. §4's very first row, built for the fifth time.
    #    ⭐ The baseline has to be THE DOCUMENT R622 SAW, and git has it. Exact equality or nothing.
    # ⛔ AND `git log -1` GAVE THE WRONG REVISION. It returns the LATEST commit touching the
    #    artifact, not the one that CREATED it, so the "document R622 saw" was a document from days
    #    later. --diff-filter=A --reverse is the addition.
    r622_sha = subprocess.run(
        ["git", "log", "--reverse", "--diff-filter=A", "--format=%H", "--",
         "E05_the_space_of_compilers/A24_what_the_definition_costs/"
         "R622_how_much_of_the_definition_is_re_derived/results/definition_anchoring_tiers.json"],
        cwd=ROOT, capture_output=True, text=True).stdout.split()[0]
    old = subprocess.run(["git", "show", f"{r622_sha}:E05_the_space_of_compilers/DEFINITION.md"],
                         cwd=ROOT, capture_output=True, text=True)
    print(f"\nPOSITIVE CONTROL  reproduce R622 on THE DOCUMENT IT SAW ({r622_sha[:8]})")
    if old.returncode != 0:
        print("  ⛔ that revision of DEFINITION.md could not be read — control UNRUNNABLE.")
        pos_ok, repro = False, None
    else:
        got = census(old.stdout, narrow)
        repro = {k: len(v) for k, v in got.items()}
        n_old = sum(repro.values())
        print(f"  committed  n={want['n']}  T1={want['T1']}  T2={want['T2']}  T3={want['T3']}")
        print(f"  reproduced n={n_old}  T1={repro['T1']}  T2={repro['T2']}  T3={repro['T3']}")
        # ⚠ ONLY `n` IS REPRODUCIBLE, AND SAYING SO IS THE POINT. T1 depends on derive(), whose
        #   label list has grown since R622; T2/T3 depend on the A24 artifact set, which has also
        #   grown. Both differences are DIRECTIONAL (more labels, more artifacts -> higher T1, lower
        #   T3) and neither can be undone from here. So the control tests the component this round's
        #   estimand actually rests on -- the decimal extractor -- against a committed number, and
        #   states the two it cannot test instead of loosening the comparison until everything fits.
        pos_ok = n_old == want["n"]
        print(f"  EXACT reproduction of n required: {pos_ok}   "
              f"(T1 {repro['T1']} vs {want['T1']} and T3 {repro['T3']} vs {want['T3']} are NOT "
              f"reproducible: derive() and the A24 corpus have both grown)")
    now_all = census(text, narrow)
    print(f"  (for contrast, today's document under the same A24 scope: "
          f"n={sum(len(v) for v in now_all.values())}, T1={len(now_all['T1'])})")

    # ── NEGATIVE / PLACEBO
    ghost = "0." + "8675" + "309"
    neg_ok = ghost not in wide and ghost not in narrow and tier(ghost, wide) == "T3"
    from_art = next((v for v in sorted(wide) if v not in gv and DEC.fullmatch(v)), None)
    plac_ok = from_art is not None and tier(from_art, wide) == "T2"
    print(f"NEGATIVE CONTROL  a runtime-assembled decimal lands in T3: {neg_ok}")
    print(f"PLACEBO           a decimal drawn from an artifact but not derive() lands in T2: "
          f"{plac_ok} ({from_art})")

    # ── NOISE FLOOR: re-measure the collision rate rather than quoting R625.
    floors = []
    for s in SEEDS:
        rng = random.Random(s)
        hit = sum(1 for _ in range(NDRAW) if f"{rng.random():.4f}" in wide)
        floors.append(hit / NDRAW)
    print(f"NOISE FLOOR       an invented 4-place decimal matches an artifact value "
          f"{', '.join(f'{f:.1%}' for f in floors)}  (R625 measured 35–38% on a narrower scan)")
    ctrl_ok = pos_ok and neg_ok and plac_ok

    # ── THE SPLIT, under the WIDENED scan.
    print(f"\nTIERS BY HALF, all-arc scan")
    print(f"  {'half':<12}{'n':>6}{'T1':>7}{'T2':>7}{'T3':>7}   T1 share")
    halves = {}
    for name, txt in (("statement", stmt), ("record", rec), ("whole", text)):
        c = census(txt, wide)
        n = sum(len(v) for v in c.values())
        halves[name] = {k: len(v) for k, v in c.items()} | {"n": n, "T3_members": sorted(set(c["T3"]))}
        print(f"  {name:<12}{n:>6}{len(c['T1']):>7}{len(c['T2']):>7}{len(c['T3']):>7}"
              f"   {(len(c['T1'])/n if n else 0):>8.1%}")

    t3_stmt = halves["statement"]["T3_members"]
    # ⚠ price the count against the floor rather than reading 0 as clean.
    miss = 1 - sum(floors) / len(floors)
    cand = halves["statement"]["n"] - halves["statement"]["T1"]
    print(f"\n  ⚠ FLOOR PRICING: the miss rate is {miss:.1%}, so if all {cand} non-T1 statement "
          f"decimals were INVENTED, {cand*miss:.1f} would land in T3 by chance alone.")
    print(f"\n  T3 in the STATEMENT region: {len(t3_stmt)}"
          + (f" -> {t3_stmt}" if t3_stmt else " (none)"))
    print(f"  T3 in the RECORD region:    {halves['record']['T3']}")

    if not ctrl_ok:
        world = "UNVERIFIED — a control failed; the partition certifies nothing"
    elif not t3_stmt:
        world = ("A HYGIENE — every unbacked decimal sits in the evidence record; the statement "
                 "carries none")
    else:
        world = (f"B THE DEFINITION CARRIES PROSE NUMBERS — {len(t3_stmt)} decimal(s) in the "
                 f"statement region are held by no artifact: {t3_stmt}")
    print(f"\n⭐ {world}")

    out = HERE / "results" / "tiers_by_half.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head=subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                            text=True).stdout.strip()[:8],
        artifacts_a24_only=n_narrow, artifacts_all_arcs=n_wide,
        values_a24_only=len(narrow), values_all_arcs=len(wide),
        r622_committed=want, reproduced_under_a24_scope=repro,
        halves=halves, collision_floor=floors, seeds=list(SEEDS), ndraw=NDRAW,
        expected_t3_if_all_invented=(halves["statement"]["n"] - halves["statement"]["T1"])
        * (1 - sum(floors) / len(floors)),
        controls={"positive_reproduces_r622": pos_ok, "negative_ghost_t3": neg_ok,
                  "placebo_artifact_value_t2": plac_ok, "all_ok": ctrl_ok},
        world=world,
        note="T2 means an artifact holds these digits, never that the claim is checked; R949 "
             "measured quantity-level agreement separately at 0.200. And T2 must be read against "
             "the collision floor above, not at face value.",
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
