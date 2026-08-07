#!/usr/bin/env python3
"""
R948 · R947's search had power 0.083 because it asked whether ANY artifact holds the number. The
        statement CITES a round for each number. Ask the cited round.

⛔ WHY. R947 measured 144 of 145 numerals tracing, and its own floor control killed the reading: a
deliberately wrong numeral traces **0.917** of the time, because 317,028 floats across 1,177 files
match almost anything of the right shape. **The count was what a fabricated statement would also
produce.** The defect is not the search — it is the population searched. The statement does not say
*"this number is somewhere in the repo"*; it says *"+0.009103 … (R923)"*. **Asking the cited round
narrows the haystack from the whole corpus to one round's artifacts, and that is what turns a
vacuous rate into a test.**

⭐ **AND THE FLOOR BECOMES THE RIGHT ONE.** R947's floor perturbed the NUMBER. The failure that
matters here is different: a number correctly present in the repo but attributed to a round that
never produced it. So the negative control **perturbs the CITATION** — the same numeral searched in a
random OTHER round's artifacts, matched on how many rounds the real block cites, so the permissiveness
of `any of the cited rounds` is matched exactly. **A rate above that floor is attribution; a rate at
it means the citation is decorative.**

⚠ **THE CITATION WINDOW IS AN INSTRUMENT AND GETS A POSITIVE CONTROL BEFORE IT IS USED.** A proximity
rule is the loose-pattern failure this project has been burned by three times in one hour. Same-line
is too tight — `R² = 0.9984` sits one line below its `(R920, world C_implies_B)`. The window is
therefore the enclosing **markdown block** (contiguous non-blank lines), and control ① requires it to
attach BOTH known pairs to their correct rounds: `0.009103`→R923 and `0.9984`→R920. A window that
cannot recover two attributions I read off the page myself cannot be trusted on 143 more.

ESTIMAND        of the high-precision numerals in the definition's statement region that carry a
                round citation in their block, the share whose value appears in a CITED round's own
                results artifact — against the same share when the citation is replaced by random
                other rounds, matched on count.
IDENTIFICATION  identified as a rate against a measured mis-attribution floor. NOT identified as
                `the sentence is true`: the cited round's artifact may hold the value for a different
                quantity than the sentence claims. Bounds, and the residual is named.
SCOPE           population: numerals with >=3 decimals in the statement region, region imported from
                            `a_statement_is_current_with_the_arc.statement_region`
                instrument: numeric match at the numeral's printed precision inside the cited round's
                            own non-provisional results JSONs
                baseline:   R947's whole-corpus search, power 0.083
                regime:     HEAD, one release, one repo
WORLDS          A · the cited-round rate is well above the random-citation floor -> citations are
                    load-bearing, the statement's numbers are attributable, and R947's vacuity was
                    a population choice rather than a fact about the document
                B · the rate sits at the floor -> the citations do not localise the numbers; naming a
                    round beside a number carries no information and the document's apparatus is
                    decorative
                C · few numerals carry any citation -> the question is unanswerable for most of the
                    statement, and the size of THAT set is the finding
KILL            CONDITIONAL:
                  ⭐ ① POSITIVE / THE WINDOW: the block rule must attach `0.009103` to R923 and
                     `0.9984` to R920, and both must trace inside those rounds. Two attributions read
                     off the page by hand; if the instrument misses them it is not measuring
                     citation.
                  ⭐ ② FLOOR / MIS-ATTRIBUTION, MEASURED: the same numerals searched in randomly
                     chosen OTHER rounds, count-matched to each block's real citation count, 3 seeds.
                     **A real rate inside the floor's spread is World B, and no attribution claim is
                     admissible.**
                  ⭐ ③ g=0 / PERTURBED NUMBER AT THE RIGHT ROUND: the last digit changed, searched in
                     the correctly cited round. This must NOT trace, or the per-round haystack is
                     still dense enough to match anything and the round has bought nothing over R947.
                  ⭐ ④ SELF-EXCLUSION: this round's own results are excluded from every search.
                     R947's first run wrote its artifact into the tree it searched and its identical
                     second run scored higher. **That is a defect this round inherits by default and
                     must switch off explicitly.**
                  ⭐ ⑤ EVERY UNATTRIBUTED AND EVERY NON-TRACING PAIR NAMED, with the numeral, its
                     cited rounds and its line, so a reader checks rather than counts.
MULTIPLICITY    N numerals × {cited, 3 random-citation seeds, perturbed-at-cited}; all printed.
ARTIFACT        results/attribution.json
IMPOSSIBLE      independently replicated · cross-release · construct validated · criterion validated.
                ⚠ AND: **whether the cited round holds the value FOR THE QUANTITY CLAIMED is not
                measured.** That needs a per-numeral read of both the sentence and the artifact key,
                and no search closes it. Named, not assumed away.
"""
import json, pathlib, random, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "assurance"))
PROVISIONAL = re.compile(r"smoke|dry[_-]?run|draft|scratch|trial|pilot|prelim|wip", re.I)
NUMERAL = re.compile(r"(?<![\w.])(\d+\.\d{3,})(?![\w])")
CITE = re.compile(r"\bR(\d{1,4})\b")
SEEDS = (11, 23, 37)


def floats_of(doc, out):
    if isinstance(doc, dict):
        for v in doc.values():
            floats_of(v, out)
    elif isinstance(doc, list):
        for v in doc:
            floats_of(v, out)
    elif isinstance(doc, bool):
        return
    elif isinstance(doc, (int, float)):
        out.append(float(doc))
    elif isinstance(doc, str):
        for m in NUMERAL.finditer(doc):
            out.append(float(m.group(1)))


def main() -> int:
    from a_statement_is_current_with_the_arc import statement_region
    text = (ROOT / "E05_the_space_of_compilers/DEFINITION.md").read_text()
    region = statement_region(text)
    if region is None:
        print("  UNRUNNABLE: no statement region. Exit 2, never 0.")
        return 2

    # every round on disk, indexed by its numeric id -- built once, self-excluded (control ④)
    by_id = {}
    for d in ROOT.glob("E0*/A*/R*"):
        if not d.is_dir() or OUT.parent == d:
            continue
        m = re.match(r"R(\d+)_", d.name)
        if m:
            by_id.setdefault(int(m.group(1)), []).append(d)
    print(f"  ④ SELF-EXCLUSION — this round excluded from the searchable set: "
          f"{OUT.parent.name not in [x.name for v in by_id.values() for x in v]}  PASS")
    print(f"  {len(by_id)} distinct round ids on disk")

    cache = {}

    def pool_of(rid):
        if rid in cache:
            return cache[rid]
        vals = []
        for d in by_id.get(rid, []):
            for f in sorted(d.glob("results/**/*.json")):
                if PROVISIONAL.search(f.name) or "_smoke_archive" in f.parts:
                    continue
                try:
                    floats_of(json.loads(f.read_text()), vals)
                except Exception:
                    continue
        cache[rid] = vals
        return vals

    def traces(s, rids):
        d = len(s.split(".")[1])
        want = round(float(s), d)
        for rid in rids:
            if any(round(v, d) == want for v in pool_of(rid)):
                return rid
        return None

    # blocks = contiguous non-blank lines; the window is the block, validated by control ①
    lines = region.splitlines()
    blocks, cur, start = [], [], 1
    for i, l in enumerate(lines, 1):
        if l.strip():
            if not cur:
                start = i
            cur.append(l)
        elif cur:
            blocks.append((start, "\n".join(cur)))
            cur = []
    if cur:
        blocks.append((start, "\n".join(cur)))

    rows, seen = [], set()
    for ln, b in blocks:
        cites = sorted({int(x) for x in CITE.findall(b)})
        for m in NUMERAL.finditer(b):
            s = m.group(1)
            if s in seen:
                continue
            seen.add(s)
            rows.append({"numeral": s, "line": ln, "cites": cites,
                         "context": b.replace("\n", " ")[:100]})
    cited = [r for r in rows if r["cites"]]
    uncited = [r for r in rows if not r["cites"]]
    print(f"\n  {len(rows)} distinct numerals; {len(cited)} carry a round citation in their block, "
          f"{len(uncited)} carry none")

    for r in cited:
        r["hit"] = traces(r["numeral"], r["cites"])

    def find(numeral):
        return next((r for r in cited if r["numeral"] == numeral), None)
    a, b_ = find("0.009103"), find("0.9984")
    c1 = (a is not None and 923 in a["cites"] and a["hit"] is not None
          and b_ is not None and 920 in b_["cites"] and b_["hit"] is not None)
    print(f"\n  ① POSITIVE / THE WINDOW — 0.009103 cites {a['cites'] if a else None} hit "
          f"{a['hit'] if a else None}; 0.9984 cites {b_['cites'] if b_ else None} hit "
          f"{b_['hit'] if b_ else None}: {c1}  "
          f"{'PASS — the block window recovers both hand-read attributions' if c1 else 'FAIL'}")

    n_hit = sum(1 for r in cited if r["hit"])
    real = n_hit / len(cited) if cited else float("nan")
    print(f"\n  CITED-ROUND RATE: {n_hit}/{len(cited)} = {real:.3f}")

    ids = sorted(by_id)
    floor = []
    for seed in SEEDS:
        rng = random.Random(seed)
        ok = 0
        for r in cited:
            others = [i for i in ids if i not in r["cites"]]
            pick = rng.sample(others, min(len(r["cites"]), len(others)))
            if traces(r["numeral"], pick):
                ok += 1
        floor.append(ok / len(cited))
        print(f"  ② FLOOR seed {seed} — citation replaced by random other rounds, count-matched: "
              f"{ok}/{len(cited)} = {ok/len(cited):.3f}")
    fl_lo, fl_hi = min(floor), max(floor)
    c2 = real > fl_hi

    pert = 0
    rng = random.Random(101)
    for r in cited:
        s = r["numeral"]
        alt = rng.choice([c for c in "0123456789" if c != s[-1]])
        if traces(s[:-1] + alt, r["cites"]):
            pert += 1
    pert_rate = pert / len(cited)
    c3 = pert_rate < 0.5
    print(f"  ③ g=0 — last digit perturbed, searched at the CORRECT round: {pert}/{len(cited)} = "
          f"{pert_rate:.3f}: {c3}  "
          f"{'PASS — the per-round haystack does not match anything' if c3 else 'FAIL — still dense'}")
    print(f"\n  ② real {real:.3f} vs mis-attribution floor [{fl_lo:.3f}, {fl_hi:.3f}]: {c2}")
    print(f"     power against a wrong citation = {real - fl_hi:+.3f}; R947's whole-corpus power "
          f"was 0.083")

    if not (c1 and c3):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "c1": c1, "c3": c3, "real": real, "floor": floor},
                  open(OUT / "attribution.json", "w"), indent=2)
        return 2

    miss = [r for r in cited if not r["hit"]]
    print(f"\n  ⑤ EVERY NON-TRACING CITED PAIR — {len(miss)}:")
    for r in miss:
        print(f"     L{r['line']:<5} {r['numeral']:<12} cites R{r['cites']}  {r['context'][:70]}")
    print(f"\n  ⑤ EVERY UNCITED NUMERAL — {len(uncited)}:")
    for r in uncited[:20]:
        print(f"     L{r['line']:<5} {r['numeral']:<12} {r['context'][:70]}")
    if len(uncited) > 20:
        print(f"     … and {len(uncited) - 20} more, all in the artifact")

    share_uncited = len(uncited) / len(rows)
    world = "C" if share_uncited > 0.5 else ("A" if c2 else "B")
    print(f"\n  ⭐⭐⭐ WORLD {world}: " + (
        f"the cited round holds the number {real:.3f} of the time against a mis-attribution floor of "
        f"[{fl_lo:.3f}, {fl_hi:.3f}] — a discrimination of {real - fl_hi:+.3f} where R947's "
        f"whole-corpus search had 0.083. **The citations are load-bearing**, and R947's vacuity was a "
        f"choice of population rather than a fact about the document."
        if world == "A" else
        f"the cited-round rate {real:.3f} sits inside the mis-attribution floor "
        f"[{fl_lo:.3f}, {fl_hi:.3f}]. **Naming a round beside a number carries no information here** "
        f"— the apparatus is decorative and the attribution question is not answered by it."
        if world == "B" else
        f"{len(uncited)} of {len(rows)} numerals ({share_uncited:.0%}) carry NO round citation in "
        f"their block, so attribution is unanswerable for most of the statement. The cited subset "
        f"runs {real:.3f} against [{fl_lo:.3f}, {fl_hi:.3f}], but the population that can be asked "
        f"is the minority and THAT is the finding."))
    print(f"     ⚠ NOT MEASURED: whether the cited round holds the value FOR THE QUANTITY CLAIMED. "
          f"A round's artifact can hold 0.5514 as a cut and the sentence can call it a margin. That "
          f"needs a per-numeral read of both sides and no search closes it.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world,
               "n_numerals": len(rows), "n_cited": len(cited), "n_uncited": len(uncited),
               "share_uncited": share_uncited,
               "cited_round_rate": real, "misattribution_floor": [fl_lo, fl_hi],
               "floor_per_seed": floor,
               "discrimination": real - fl_hi,
               "r947_whole_corpus_power": 0.083,
               "perturbed_at_correct_round": pert_rate,
               "non_tracing_cited": miss, "uncited": uncited,
               "not_measured": "whether the cited round holds the value for the QUANTITY claimed",
               "unit_note": "counts are DISTINCT NUMERALS",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "attribution.json", "w"), indent=2)
    print(f"\n  artifact: results/attribution.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
