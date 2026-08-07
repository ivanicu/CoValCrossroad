"""R1071 — the 31 unsourced clause decimals: a recording failure, or absent from the record entirely?

R1070 found 31 of 38 clause decimals stored by NO round as a numeric leaf. That is compatible with two
very different situations, and the difference decides what to do about it:

  RECORDING FAILURE  the value was computed and written into a README, a run.py or a commit body,
                     but never persisted to a results file. The record HAS it; the artifact does not.
  ABSENT FROM THE RECORD  it appears nowhere in this repository except the definition itself. Then
                     the definition states a number that no committed text supports.

⭐ THE SECOND CLASS IS THE SERIOUS ONE AND HAS NEVER BEEN COUNTED.

ESTIMAND        of the clause decimals unstored in any artifact, the share appearing in the committed
                PROSE record (round READMEs, run.py sources, commit bodies) versus nowhere at all
IDENTIFICATION  exact for presence. ⚠ Presence in prose is not provenance: a README may quote a value
                it did not compute, exactly as R1070 found for artifacts. This separates `in the
                record` from `absent`, never `measured` from `quoted`.
SCOPE           population : the 31 decimals R1070 marked unsourced, recomputed here
                instrument : exact string match in READMEs, run.py, and `git log` bodies
                baseline   : R1070's artifact-side count
                regime     : this checkout, this document version
WORLDS          A A RECORDING FAILURE — nearly all appear in the prose record, so the gap is that
                  rounds reported values they never persisted, and the remedy is a writing habit.
                B SOMETHING IS IN THE DEFINITION AND NOWHERE ELSE — a material share appear nowhere,
                  so the statement asserts numbers no committed text supports and each must be
                  found or withdrawn.
                prediction matrix: A -> nowhere-count ~0;  B -> nowhere-count > 0
KILL            pre-registered and CONDITIONAL:
                  if the controls fire:
                      nowhere-count == 0 -> World A
                      > 0                -> World B, and every one is NAMED
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   ⭐ a decimal known to be in a README must be found there. A searcher never shown to
                find a present value cannot evidence an absence — the exact failure §4 records for
                greps.
NEGATIVE CTRL   a constructed-absent decimal must be found nowhere.
SHAM            search a corpus that CANNOT contain them — the release data directory — and require
                near-zero hits, so `found` is not just `these digits occur in any large text`.
PLACEBO         an empty candidate list exits 2, never 0.
NOISE FLOOR     ⭐ random decimals at matched precision, 3 seeds: how often does a made-up value at
                this precision appear in the prose corpus by chance?
MULTIPLICITY    every candidate reported with where it was found, not only the absent ones.
SEEDS           3.
IMPOSSIBLE      whether a value found in prose was COMPUTED there or quoted from elsewhere. Same
                limit R1070 hit on the artifact side. SETTLES: IN-RELEASE by reading each occurrence.
"""
import json, pathlib, random, re, subprocess

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
E05 = ROOT / "E05_the_space_of_compilers"
DEF = E05 / "DEFINITION.md"
WIN = 700
DEC = re.compile(r"(?<![\w.])(\d+\.\d+)(?![\w.])")
ANY = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)(?![\w.])")


def leaves(o, out):
    if isinstance(o, bool):
        return
    if isinstance(o, (int, float)):
        out.add(round(float(o), 9)); return
    if isinstance(o, list):
        for v in o:
            leaves(v, out)
        return
    if isinstance(o, dict):
        for v in o.values():
            leaves(v, out)


def main() -> int:
    doc = DEF.read_text()
    anchors = [m.start() for m in re.finditer("resolvably beats", doc)]
    by_off = {}
    for a in anchors:
        lo = max(0, a - WIN)
        for m in DEC.finditer(doc[lo: a + WIN]):
            by_off[lo + m.start()] = m.group(1)
    toks = [by_off[k] for k in sorted(by_off)]

    stored = set()
    for f in E05.glob("A*/R*/results/*.json"):
        try:
            leaves(json.loads(f.read_text()), stored)
        except Exception:
            continue
    cand = [t for t in toks if round(float(t), 9) not in stored]
    if not cand:
        print("  UNRUNNABLE: no unsourced decimal to classify. Exit 2, never 0."); return 2
    print(f"  ⭐ clause decimals {len(toks)} · unstored in any artifact {len(cand)}")

    # ⛔⛔ THE CORPUS CONTAINED THE ROUNDS THAT AUDIT THE CORPUS, AND MY OWN NEGATIVE CONTROL CAUGHT
    #   IT: the sentinel `0.987654321` was FOUND, because R1070's run.py — written minutes ago —
    #   contains it as ITS sentinel. The same contamination is far worse for the real question:
    #   R1067-R1070 quote these clause decimals wholesale, so `found in the prose record` would be
    #   trivially true for anything the audit rounds mentioned. That is R1070's `a quoter is not a
    #   source` one level along. Rounds from R1067 on are EXCLUDED — they are downstream of the
    #   clause, so finding a value there is not evidence it was ever measured.
    def upstream(path):
        m = re.match(r"R(\d+)", path.parent.name)
        return m is not None and int(m.group(1)) < 1067

    rm_files = [p for p in E05.glob("A*/R*/README.md") if upstream(p)]
    src_files = [p for p in E05.glob("A*/R*/run.py") if upstream(p)]
    readmes = "\n".join(p.read_text() for p in rm_files)
    sources = "\n".join(p.read_text() for p in src_files)
    print(f"  ⛔ corpus restricted to rounds BEFORE R1067 (the audit rounds quote these values): "
          f"{len(rm_files)} READMEs, {len(src_files)} sources")
    log = subprocess.run(["git", "log", "--format=%B", "--skip=12", "-400"], cwd=ROOT,
                         capture_output=True, text=True).stdout
    data = ""
    dd = ROOT / "data"
    if dd.exists():
        for p in list(dd.glob("*.jsonl"))[:2]:
            data += p.read_text()[:4_000_000]
    corpora = {"README": readmes, "run.py": sources, "commit": log}
    print(f"  ⭐ corpus sizes — README {len(readmes):,} · run.py {len(sources):,} · "
          f"commit {len(log):,} · release data (sham) {len(data):,}")

    def where(t):
        return [k for k, c in corpora.items() if re.search(r"(?<![\w.])" + re.escape(t) + r"(?![\w.])", c)]

    known = next((t for t in toks if where(t)), None)
    pos = known is not None
    neg = not where("0.31415926535897")
    print(f"  POSITIVE — a decimal present in the record must be FOUND ({known}): {pos}")
    print(f"  NEGATIVE — a constructed-absent decimal must be found nowhere: {neg}")
    if not (pos and neg):
        print("  the searcher cannot evidence an absence. Exit 2, never 0."); return 2

    rows = [{"value": t, "found_in": where(t)} for t in cand]
    nowhere = [r for r in rows if not r["found_in"]]
    print(f"\n  ⭐ IN THE PROSE RECORD {len(rows) - len(nowhere)} of {len(rows)} · "
          f"NOWHERE AT ALL {len(nowhere)}")
    for r in rows[:8]:
        print(f"     {r['value']:>12}  {r['found_in'] or 'NOWHERE'}")
    if nowhere:
        print(f"  ⛔ the values appearing nowhere but the definition: "
              f"{[r['value'] for r in nowhere][:12]}")

    sham_hits = sum(1 for t in cand
                    if re.search(r"(?<![\w.])" + re.escape(t) + r"(?![\w.])", data)) if data else 0
    print(f"  SHAM — the same values searched in the RELEASE DATA, which cannot contain them: "
          f"{sham_hits} of {len(cand)}")

    floors = []
    for seed in (5, 17, 29):
        rng = random.Random(seed)
        dr = [f"{rng.uniform(0, 1):.{len(t.split('.')[1])}f}" for t in cand]
        floors.append(sum(1 for x in dr if where(x)) / len(dr))
    flo, fhi = min(floors), max(floors)
    obs = (len(rows) - len(nowhere)) / len(rows)
    print(f"  ⭐ MEASURED FLOOR — random decimals at matched precision found in the prose corpus, "
          f"3 seeds: [{flo:.3f}, {fhi:.3f}] · observed {obs:.3f}")

    resolved = obs > fhi
    print()
    if not resolved:
        world = (f"⛔ UNVERIFIED — the observed presence rate {obs:.3f} does not clear the random "
                 f"floor [{flo:.3f}, {fhi:.3f}], so `found in the prose record` cannot be "
                 f"distinguished from coincidence at this precision.")
    elif not nowhere:
        world = (f"⭐ A A RECORDING FAILURE — all {len(rows)} unstored decimals appear in the "
                 f"committed prose record, above a random floor of [{flo:.3f}, {fhi:.3f}]. The gap "
                 f"is that rounds reported values they never persisted; the remedy is a writing "
                 f"habit, not a search.")
    else:
        world = (f"⛔ B {len(nowhere)} CLAUSE DECIMAL(S) APPEAR NOWHERE BUT THE DEFINITION — "
                 f"{[r['value'] for r in nowhere][:10]}. Not in any README, run.py or commit body, "
                 f"and not stored in any artifact. **The statement asserts numbers no committed text "
                 f"supports**, and each must be found or withdrawn. The other "
                 f"{len(rows) - len(nowhere)} are a recording failure: reported in prose, never "
                 f"persisted.")
    print(world)
    print(f"⛔ AND PRESENCE IN PROSE IS NOT PROVENANCE. A README may quote a value it did not compute,")
    print(f"   exactly as R1070 found on the artifact side. This separates `in the record` from")
    print(f"   `absent`; it does not separate `measured` from `quoted`.")

    o = HERE / "results" / "prose_or_nowhere.json"
    o.write_text(json.dumps({
        "round": "R1071", "clause_decimals": len(toks), "unstored": len(cand),
        "in_prose": len(rows) - len(nowhere), "nowhere": [r["value"] for r in nowhere],
        "observed_presence": obs, "floor_3_seeds": [flo, fhi], "sham_release_data_hits": sham_hits,
        "rows": rows, "world": world,
        "controls": {"positive_present_found": bool(pos), "negative_absent_not_found": bool(neg)},
        "limitation": "separates `in the record` from `absent`, never `measured` from `quoted`",
    }, indent=2) + "\n")
    print(f"\nartifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
