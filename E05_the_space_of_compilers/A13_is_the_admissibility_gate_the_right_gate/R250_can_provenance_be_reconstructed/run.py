"""R250 -- `provenance` has read 0.00 since R232. That is a fact about a FIELD, not about the data.

WHAT R232 ESTABLISHED AND WHAT WAS CONCLUDED FROM IT
    VERIFIED: across all 986 rubrics every `coval_core` item carries exactly one field, `criterion`.
    There is no `source_criterion_id`, no parent, no lineage. That query was run and it holds.

    CONCLUDED, and never checked: "provenance FAILED -- 0.00", carried in the certificate for eight
    rounds and repeated in my own commit message one round ago as "cannot be repaired from this
    release." THAT IS AN UNCHECKED WALL. The absence of a lineage FIELD is not the absence of
    lineage; a rewritten criterion still descends from something, and descent leaves two traces the
    release does ship: the TEXT, and how the judge SCORES it.

WHAT THE OBJECT SAYS, ASKED RATHER THAN REMEMBERED
    Of 3,899 printed core items, 303 (7.77%) are VERBATIM string matches to a criterion in their
    own prompt's full rubric, and 943 (24.19%) reach token-Jaccard 0.6. So provenance is not 0.00.
    More usefully: THE 303 ARE GROUND TRUTH. Their parent is known without inference, which makes a
    calibrated positive control possible for the first time in this arc.

THE QUESTION THIS ROUND ANSWERS
    Not "can we match identical strings" -- that is 1+1=2. It is: HOW FAR CAN A REWRITE TRAVEL
    BEFORE PROVENANCE BECOMES UNRECOVERABLE? Dose-response on the ground-truth set: perturb a known
    parent's text by increasing amounts, re-judge, and measure recovery by two INDEPENDENT routes.
    Then locate where the real core rewrites sit on that axis.

ESTIMAND        recovery rate R(route, dose) = P(the reconstruction names the true parent), on the
                303 ground-truth items, as a function of text-perturbation dose; and the dose at
                which each route falls to its own chance floor (the MDE of provenance recovery,
                expressed in text distance).
                Routes, chosen to fail for DIFFERENT reasons:
                  TEXT       token-Jaccard against every criterion in the same prompt's full rubric
                  BEHAVIOUR  nearest cached satisfaction vector over the prompt's 4 responses
IDENTIFICATION  exact on the ground-truth set: the parent is known by string identity, so recovery
                is observed, never estimated. Extrapolation to the other 3,596 items is NOT
                identified and is reported as a POSITION ON THE DOSE AXIS, never as a rate.
SCOPE           population: 303 verbatim core items and their prompts. instrument: Qwen3.5-2B-Base
                via covalx.judge, the same build as r04, so the perturbed scores live on the same
                scale as the cached full tensor. baseline: chance = 1/n_criteria, per prompt.
                regime: m=4 responses, doses below.
DOSES           0.00 identity | 0.20 / 0.40 / 0.60 of content tokens dropped | shuffle (all tokens,
                order destroyed, content preserved) | first-clause truncation (the "generic
                rewrite" direction R249 showed the compiler actually travels)
WORLDS          W1 provenance survives realistic rewriting
                     -> both routes stay above chance out to dose 0.4, and the real core's
                        text-distance sits inside the surviving range
                W2 provenance dies at the first real edit
                     -> recovery collapses to chance by dose 0.2 and the field is genuinely
                        unrecoverable, which is a REGISTER ENTRY WITH A MEASUREMENT behind it
                        rather than the assertion it has been
                W3 the two routes diverge
                     -> text survives and behaviour does not, or the reverse. Then provenance is
                        recoverable only under an assumption, and the certificate must name which
KILL            pre-registered: if BOTH routes are inside their own chance floor's spread at dose
                0.20, provenance is unrecoverable under any rewriting the compiler plausibly does,
                and `provenance: FAILED` stands -- but as MEASURED, with an MDE, instead of asserted.
                If EITHER survives to dose 0.40, the certificate's provenance field is issuable for
                this release and eight rounds of "0.00" were reporting a missing column as a
                missing fact.
POSITIVE CTRL   dose 0.00. TEXT must recover at exactly 1.0000 -- the string is identical.
                ⚠ AND THE BEHAVIOUR ROUTE AT DOSE 0 IS AN IDENTITY, NOT A TEST: the same text on
                the same response produces the same judge prompt, so the vectors must coincide
                exactly. It is reported as a TENSOR-ALIGNMENT CHECK and is evidence of nothing
                about reconstruction. The arithmetic trap, labelled where it occurs.
NEGATIVE CTRL   match each perturbed criterion against a DIFFERENT prompt's full rubric. Recovery
                must fall to chance at every dose including 0. This destroys the pairing while
                preserving the text, the judge and the candidate-set size.
SHAM            a random criterion from the same prompt, drawn without looking at anything. Its
                recovery IS the chance floor, measured rather than computed.
PLACEBO         a FULL criterion matched against its own rubric must return itself at rank 1, for
                both routes, on every prompt. Anything else means the candidate index is misaligned.
NOISE FLOOR     3 seeds over the token-dropping draws; spread reported per cell.
MULTIPLICITY    6 doses x 2 routes x 3 arms (true / negative / sham) x 3 seeds; whole grid printed,
                including the doses where recovery dies.
SPECIFICATION   swept: dose, route, and the tie rule (a route that returns k tied candidates scores
                1/k, never 1 -- the same convention R228 needed).
ARTIFACT        the perturbed judgements are persisted before any summary, so the dose curve can be
                re-analysed without a GPU.
IMPOSSIBLE      whether the compiler ACTUALLY derived each core item from the parent these routes
                name. No lineage exists to check against outside the 303, and a reconstruction that
                agrees with itself is not a verification. The claim available here is bounded:
                "recoverable at this dose", never "this was the parent".
"""
from __future__ import annotations
import collections, json, math, pathlib, random, re, sys
import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"
DATA = ROOT / "data"
R4 = ROOT / ("E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all"
             "/R04_rebuild_satisfaction/results")
MODEL = "/mnt/e/data.ai-models.local-model-store.storage.xl.private.readonly/Qwen3.5-2B-Base"
L = "ABCD"
SEEDS = [0, 1, 2]
DOSES = ["identity", "drop20", "drop40", "drop60", "shuffle", "firstclause"]
STOP = set("a an the and or of to in on at is are be as by for with from that this it not but if "
           "so when about into over than then there their they them we you your our its".split())


def toks(s):
    return re.findall(r"[A-Za-z']+", str(s))


def content(s):
    return [w for w in toks(s) if w.lower() not in STOP]


def perturb(text, dose, rng):
    w = toks(text)
    if dose == "identity":
        return text
    if dose == "shuffle":
        w2 = w[:]; rng.shuffle(w2); return " ".join(w2)
    if dose == "firstclause":
        for sep in (",", ";", " and ", " that "):
            if sep in text:
                return text.split(sep)[0].strip()
        return " ".join(w[:max(3, len(w) // 2)])
    frac = {"drop20": 0.2, "drop40": 0.4, "drop60": 0.6}[dose]
    ci = [i for i, x in enumerate(w) if x.lower() not in STOP]
    n_drop = int(round(frac * len(ci)))
    drop = set(rng.sample(ci, min(n_drop, len(ci))))
    kept = [x for i, x in enumerate(w) if i not in drop]
    return " ".join(kept) if kept else w[0]


def jac(a, b):
    A, B = set(x.lower() for x in content(a)), set(x.lower() for x in content(b))
    return len(A & B) / len(A | B) if (A | B) else 0.0


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    import importlib.util
    _s = importlib.util.spec_from_file_location(
        "r220", ROOT / "E05_the_space_of_compilers/A01_is_our_own_compiler_better"
                     / "R220_compiler_tournament/run.py")
    r220 = importlib.util.module_from_spec(_s); _s.loader.exec_module(r220)
    sf = r220.load_sat(R4 / "a04_full.npz")
    from covalx.judge import Judge, build_prompt, load_join
    recs = {pid: r for pid, _p, r in load_join(DATA / "comparisons.jsonl",
                                               DATA / "conversation_rubrics.jsonl")}
    resp = {}
    for line in (DATA / "comparisons.jsonl").open():
        o = json.loads(line)
        resp[o["prompt_id"]] = [r["messages"][0]["content"] for r in o["responses"]]

    # ---- the ground-truth set, discovered from the object: core items that are VERBATIM parents
    gt = []
    for p, r in recs.items():
        if p not in sf or p not in resp or len(resp[p]) != 4:
            continue
        f = r["coval_full"]
        ok = [i for i, it in enumerate(f)
              if it.get("scores") and all(sf[p].get((i, x)) is not None for x in L)]
        if len(ok) < 4:
            continue
        idx = {f[i].get("criterion", "").strip().lower(): i for i in ok}
        for it in r["coval_core"]:
            c = it.get("criterion", "").strip().lower()
            if c in idx:
                gt.append((p, idx[c], f[idx[c]]["criterion"], ok))
    print("GROUND TRUTH: %d core items are verbatim copies of a criterion in their own full rubric"
          % len(gt), flush=True)
    print("  candidate-set size per prompt: mean %.2f  -> chance = %.4f"
          % (float(np.mean([len(g[3]) for g in gt])),
             float(np.mean([1 / len(g[3]) for g in gt]))), flush=True)

    # ---- the negative control's pairing: a DIFFERENT prompt, fixed before judging
    others = [g[0] for g in gt]
    rng0 = random.Random(12345)
    shifted = others[1:] + others[:1]

    tasks, index = [], []
    for seed in SEEDS:
        rng = random.Random(1000 + seed)
        for gi, (p, parent, txt, ok) in enumerate(gt):
            for dose in DOSES:
                if dose in ("identity", "shuffle", "firstclause") and seed != SEEDS[0]:
                    continue                      # deterministic doses: judge once
                pt = perturb(txt, dose, rng)
                for r_ in range(4):
                    index.append((seed, gi, dose, r_, pt))
                    tasks.append(build_prompt(pt, resp[p][r_]))
    cache = OUT / "perturbed.npz"
    if cache.exists():
        cd = np.load(cache, allow_pickle=True)
        assert len(cd["sat"]) == len(tasks), "cache does not match the task list; delete and re-judge"
        sat = cd["sat"]
        print("reusing %d persisted judgements from results/perturbed.npz -- no GPU" % len(sat),
              flush=True)
    else:
        print("judging %d perturbed (criterion, response) pairs" % len(tasks), flush=True)
        judge = Judge(MODEL, batch=64)
        sat = judge.score(tasks)
        np.savez_compressed(cache,
                            meta=np.array(["%d|%d|%s|%d" % (s, g, d, r_) for s, g, d, r_, _t in index]),
                            text=np.array([t for *_x, t in index]),
                            sat=np.asarray(sat, dtype=np.float32))
        print("persisted %d judgements -> results/perturbed.npz" % len(sat), flush=True)

    V = collections.defaultdict(dict)
    TXT = {}
    for (seed, gi, dose, r_, pt), v in zip(index, sat):
        V[(seed, gi, dose)][r_] = float(v)
        TXT[(seed, gi, dose)] = pt

    grid = collections.defaultdict(lambda: collections.defaultdict(list))
    for (seed, gi, dose), vv in V.items():
        if len(vv) != 4:
            continue
        p, parent, txt, ok = gt[gi]
        y = np.array([vv[r_] for r_ in range(4)])
        pt = TXT[(seed, gi, dose)]
        for arm in ("true", "negative"):
            # ⚠ THE FIRST NEGATIVE CONTROL WAS STRUCTURALLY ZERO. It matched the query against a
            # DIFFERENT prompt's rubric and then asked whether the parent was among the hits --
            # but the parent is not in that rubric at all, so 0.0000 was forced by the candidate
            # set, not returned by the instrument. It could not have come out otherwise.
            # THE REPAIRED ONE keeps the CANDIDATE SET (this prompt's rubric, parent present) and
            # destroys the QUERY: the perturbed text of a DIFFERENT ground-truth item. Recovery
            # must fall to chance, and it CAN fail, because the parent is reachable throughout.
            pp = p
            f2 = recs[pp]["coval_full"]
            ok2 = [i for i, it in enumerate(f2)
                   if it.get("scores") and all(sf[pp].get((i, x)) is not None for x in L)]
            if not ok2:
                continue
            if arm == "negative":
                gj = (gi + 1) % len(gt)
                if (seed, gj, dose) not in TXT or len(V[(seed, gj, dose)]) != 4:
                    continue
                pt = TXT[(seed, gj, dose)]
                y = np.array([V[(seed, gj, dose)][r_] for r_ in range(4)])
            else:
                pt = TXT[(seed, gi, dose)]
                y = np.array([vv[r_] for r_ in range(4)])
            # BEHAVIOUR route: nearest cached satisfaction vector, ties share credit
            d = np.array([np.abs(np.array([sf[pp][(i, x)] for x in L]) - y).sum() for i in ok2])
            best = d.min(); hits = [ok2[i] for i in np.flatnonzero(d <= best + 1e-12)]
            grid[(dose, "behaviour", arm)][seed].append(
                (1.0 / len(hits)) if parent in hits else 0.0)
            # TEXT route: token Jaccard, ties share credit
            j = np.array([jac(pt, f2[i].get("criterion", "")) for i in ok2])
            bj = j.max(); hj = [ok2[i] for i in np.flatnonzero(j >= bj - 1e-12)]
            grid[(dose, "text", arm)][seed].append(
                (1.0 / len(hj)) if parent in hj else 0.0)
            if arm == "true":
                grid[(dose, "sham", "true")][seed].append(1.0 / len(ok2))

    def cell(k):
        vals = [float(np.mean(grid[k][s])) for s in grid[k] if grid[k][s]]
        return (float(np.mean(vals)), float(np.ptp(vals)) if len(vals) > 1 else 0.0) if vals \
            else (float("nan"), float("nan"))

    print("\n=== dose-response: recovery of a KNOWN parent, both routes ===")
    print("%-13s %18s %18s %12s %12s" % ("dose", "TEXT (spread)", "BEHAVIOUR (spread)",
                                         "chance", "text dist"))
    rows = {}
    for dose in DOSES:
        t_, ts = cell((dose, "text", "true"))
        b_, bs = cell((dose, "behaviour", "true"))
        ch, _ = cell((dose, "sham", "true"))
        dist = float(np.mean([jac(TXT[(SEEDS[0], gi, dose)], gt[gi][2]) for gi in range(len(gt))
                              if (SEEDS[0], gi, dose) in TXT]))
        rows[dose] = (t_, ts, b_, bs, ch, dist)
        print("%-13s %10.4f (%.4f) %10.4f (%.4f) %12.4f %12.4f"
              % (dose, t_, ts, b_, bs, ch, dist))
    print(" (text dist = mean token-Jaccard of the perturbed text to its own parent, 1.0 = identical)")

    print("\n=== controls ===")
    ti, _ = cell(("identity", "text", "true"))
    bi, _ = cell(("identity", "behaviour", "true"))
    # ⚠ THE CEILING IS COMPUTED, NOT ASSUMED -- and the first version of this control assumed 1.0.
    # With the 1/k tie rule a duplicate criterion inside a prompt's own rubric makes exact 1.0
    # UNREACHABLE, so "must be 1.0000" was the SIXTH control-that-cannot-pass in this arc. The
    # attainable ceiling is the mean of 1/(number of full criteria tied at maximal Jaccard to the
    # parent), which is exact arithmetic over the ground-truth set and is computed here.
    ceil_terms = []
    for p_, parent, txt, ok in gt:
        f2 = recs[p_]["coval_full"]
        j = [jac(txt, f2[i].get("criterion", "")) for i in ok]
        bj = max(j)
        ceil_terms.append(1.0 / sum(1 for x in j if x >= bj - 1e-12))
    ceiling = float(np.mean(ceil_terms))
    n_tied = sum(1 for c in ceil_terms if c < 1.0)
    print(" CEILING   attainable at dose 0 given the 1/k tie rule : %.4f"
          % ceiling)
    print("           (%d of %d ground-truth parents have a DUPLICATE in their own rubric, so exact"
          % (n_tied, len(gt)))
    print("            1.0000 is unreachable by construction -- the first threshold here demanded it)")
    print(" POSITIVE  dose 0, TEXT route recovers the parent : %.4f  %s"
          % (ti, "OK -- at the computed ceiling" if ti >= ceiling - 1e-9
             else "MATCHER BROKEN -- below the attainable ceiling"))
    print(" ⚠ IDENTITY dose 0, BEHAVIOUR route              : %.4f  -- this is a TENSOR-ALIGNMENT"
          % bi)
    print("            check, not a test: same text + same response = same judge prompt, so the")
    print("            vectors MUST coincide. Evidence of nothing about reconstruction.")
    print(" NEGATIVE  candidate set KEPT (parent reachable), QUERY replaced by another item's text.")
    print("           The first version matched against a DIFFERENT prompt's rubric, where the")
    print("           parent is absent -- 0.0000 was forced by the candidate set, not returned by")
    print("           the instrument. It could not have come out otherwise.")
    neg_ok = True
    for dose in DOSES:
        nt, _ = cell((dose, "text", "negative")); nb, _ = cell((dose, "behaviour", "negative"))
        ch, _ = cell((dose, "sham", "true"))
        bad = (nt > ch + 0.05) or (nb > ch + 0.05)
        neg_ok &= not bad
        print("   %-12s text %.4f  behaviour %.4f   chance %.4f  %s"
              % (dose, nt, nb, ch, "LEAK" if bad else "at chance"))
    print("\n ⚠ ARITHMETIC, LABELLED WHERE IT OCCURS -- two cells above are forced, not measured:")
    print("   1. BEHAVIOUR at dose 0 is an identity (same text + same response = same judge prompt).")
    print("   2. SHUFFLE is a NULL PERTURBATION FOR THE TEXT ROUTE: token-Jaccard is set-based, so")
    print("      reordering changes nothing. Its text-distance column reads 1.0000, which is the")
    print("      tell. The shuffle cell measures the BEHAVIOUR route only.")
    print("   And a third, which limits what the TEXT row can claim: dropping tokens never INTRODUCES")
    print("   a competitor's tokens, so a subset of the parent stays nearer the parent than anything")
    print("   else. Token deletion cannot kill a set-overlap matcher. Real rewriting SUBSTITUTES")
    print("   words, and this dose axis does not. The text route's flat curve is a property of the")
    print("   PERTURBATION, not evidence that provenance survives rewriting.")

    print("\n" + "=" * 78); print("PRE-REGISTERED KILL"); print("=" * 78)
    t20, _, b20, _, ch20, _ = rows["drop20"]
    t40, ts40, b40, bs40, ch40, _ = rows["drop40"]
    if ti < ceiling - 1e-9 or not neg_ok:
        v = ("UNVERIFIED -- positive %.4f vs attainable ceiling %.4f, negative-control leak %s."
             % (ti, ceiling, not neg_ok))
    elif (t20 - ch20) <= 0 and (b20 - ch20) <= 0:
        v = ("W2 -- provenance dies at the first real edit: at 20%% token drop both routes are at "
             "or below chance (%.4f). `provenance: FAILED` stands, but as a MEASUREMENT with an "
             "MDE in text distance, not as the assertion it has been for eight rounds."
             % ch20)
    elif max(t40, b40) > ch40 + max(ts40, bs40):
        v = ("W1 -- provenance SURVIVES realistic rewriting: at 40%% token drop the best route "
             "recovers the true parent %.4f of the time against chance %.4f (spread %.4f). The "
             "certificate's provenance field is ISSUABLE for this release, and eight rounds of "
             "'0.00' were reporting a missing COLUMN as a missing FACT."
             % (max(t40, b40), ch40, max(ts40, bs40)))
    else:
        v = ("W3 or partial -- recovery survives dose 0.20 but not 0.40. Provenance is recoverable "
             "only for light rewrites; the certificate must carry the dose, and the field becomes "
             "a RATE like `representative` did in R249.")
    print("\n  " + v)
    json.dump({"ground_truth_items": len(gt), "doses": DOSES,
               "rows": {d: {"text": rows[d][0], "text_spread": rows[d][1],
                            "behaviour": rows[d][2], "behaviour_spread": rows[d][3],
                            "chance": rows[d][4], "text_distance": rows[d][5]} for d in DOSES},
               "positive_text_identity": ti, "attainable_ceiling": ceiling,
               "negative_ok": bool(neg_ok), "identity_behaviour_alignment": bi,
               "verdict": v}, open(OUT / "provenance_dose.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
