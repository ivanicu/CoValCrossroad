"""r220 -- the Compiler Tournament. Eight arms, seven axes, four instruments.

Read PREREGISTRATION.md first: the arms, the axes, the five death conditions and the
register of what this site structurally cannot measure were all fixed before this ran.

WHAT THIS IS NOT
    It is not a Core v2. Building one and showing it beats the official Core, on our
    instrument, on our candidate set, against our own target, is a result whose sign is
    decided by the setup. This runs eight compilers -- including the official one, the
    uncompressed rubric, and a size-matched random floor -- against each other on axes
    that can each independently veto a winner.

ZERO GPU
    Every arm is a subset or reweighting of criteria whose satisfaction is already cached
    (r04 + r164), so the whole grid is arithmetic on cached tensors. No arm gets a compute
    advantage over another, which is itself a control.

THE DECLARED CIRCULARITY
    D_decision is fitted to reproduce B_full's ranking on the same four responses on which
    its regret is measured. Its regret is therefore ~0 BY CONSTRUCTION. It is printed so the
    tautology is visible, and it is excluded from every verdict.
"""
from __future__ import annotations

import json, math, pathlib, sys, re
from collections import defaultdict, Counter
import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"
DATA = ROOT / "data"
R4 = ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results"
R164 = ROOT / "E04_no_fraction_only_an_equivalence_class/A02_the_chain_from_a_person_to_the_standard/R164_instrument/results"
L = "ABCD"
K_CORE = 4                      # the official core's own size; not a tuned hyper-parameter
RAND_SEEDS = list(range(20))
BOOT_SEEDS = list(range(12))

# prohibition surface, for E_typed. A marker list is a PROXY for a deontic type and is only
# sound in one direction: a hit is evidence of a prohibition, a miss is not evidence of none.
PROHIB = re.compile(r"\b(never|not|don't|do not|avoid|refrain|must not|should not|"
                    r"without|no |refuse|prohibit|forbid)\b", re.I)


# ------------------------------------------------------------------ loading
def load_sat(p):
    d = np.load(p, allow_pickle=True)
    o = defaultdict(dict)
    for k, v in zip(d["meta"], d["sat"]):
        pid, i, ltr = str(k).split("|")
        o[pid][(int(i), ltr)] = float(v)
    return o


def parse_rank(s):
    if not s or (">" not in s and "=" not in s):
        return None
    blocks = [b.split("=") for b in str(s).split(">")]
    seen, pts, k = set(), np.full(4, np.nan), 0
    for b in blocks:
        ls = [x.strip() for x in b if x.strip() in L]
        if not ls:
            return None
        share = np.mean([3 - (k + i) for i in range(len(ls))])
        for x in ls:
            if x in seen:
                return None
            seen.add(x); pts[L.index(x)] = share
        k += len(ls)
    return None if np.isnan(pts).any() else pts


def parse_veto(block):
    out = set()
    for e in block or []:
        for r in (e.get("rating") or []):
            t = str(r).strip()
            if t and t[0] in L and "unacceptable" in t.lower():
                out.add(t[0])
    return out


def kendall_pairs(pts):
    """(a,b) pairs where a is strictly above b in this human ranking."""
    return [(i, j) for i in range(4) for j in range(4)
            if i != j and pts[i] > pts[j]]


def content_toks(s):
    return set(w for w in re.findall(r"[a-z']+", str(s).lower()) if len(w) > 3)


# ------------------------------------------------------------------ arms
def greedy_decision_subset(Wv, S, k):
    """Choose <=k criteria whose weighted sum best reproduces the FULL ranking over A-D.
    Fitted on the build instrument only. Deterministic, no randomness to seed."""
    n = len(Wv)
    full = (Wv[:, None] * S).sum(0)
    target = np.argsort(np.argsort(-full))
    chosen, cur = [], np.zeros(4)
    for _ in range(min(k, n)):
        best, bi = None, None
        for i in range(n):
            if i in chosen:
                continue
            y = cur + Wv[i] * S[i]
            r = np.argsort(np.argsort(-y))
            # agreement on the full ranking, tie-broken by agreement on the winner
            sc = (float((r == target).sum()), float(np.argmax(y) == np.argmax(full)))
            if best is None or sc > best:
                best, bi = sc, i
        if bi is None:
            break
        chosen.append(bi); cur = cur + Wv[bi] * S[bi]
    return chosen


def medoid_clusters(texts, k):
    """ICAI-SHAPED, not ICAI: cluster the rubric lexically and keep one real criterion per
    cluster. No text is generated, because generating text would require re-choosing the
    instrument per arm."""
    T = [content_toks(t) for t in texts]
    n = len(T)
    if n <= k:
        return list(range(n))
    sim = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            u = T[i] | T[j]
            sim[i, j] = len(T[i] & T[j]) / len(u) if u else 0.0
    # k-medoids, deterministic init at the k most central items
    med = list(np.argsort(-sim.sum(1))[:k])
    for _ in range(20):
        assign = np.argmax(sim[:, med], axis=1)
        new = []
        for c in range(k):
            mem = np.where(assign == c)[0]
            new.append(int(mem[np.argmax(sim[np.ix_(mem, mem)].sum(1))]) if len(mem) else med[c])
        if new == med:
            break
        med = new
    return med


def arm_scores(arm, ok, Wv, Sfull, core_S, texts, rng=None, dsubset=None):
    """Return y over A-D, and the criterion count the reader must read."""
    if arm == "A_official":
        if core_S is None or not len(core_S):
            return None, 0
        return core_S.sum(0), len(core_S)
    if arm == "B_full":
        return (Wv[:, None] * Sfull).sum(0), len(ok)
    if arm == "C_signed_topk":
        idx = list(np.argsort(-np.abs(Wv))[:K_CORE])
        return (Wv[idx, None] * Sfull[idx]).sum(0), len(idx)
    if arm == "D_decision":
        idx = dsubset
        if not idx:
            return None, 0
        return (Wv[idx, None] * Sfull[idx]).sum(0), len(idx)
    if arm == "E_typed":
        idx = dsubset
        if not idx:
            return None, 0
        soft = [i for i in idx if not PROHIB.search(texts[i])]
        hard = [i for i in idx if PROHIB.search(texts[i])]
        y = (Wv[soft, None] * Sfull[soft]).sum(0) if soft else np.zeros(4)
        # non-compensatory: a response failing a prohibition-typed criterion is excluded,
        # never merely penalised. If everything is excluded the filter is inapplicable.
        alive = np.ones(4, bool)
        for i in hard:
            viol = (Sfull[i] > 0.5) if Wv[i] < 0 else (Sfull[i] < 0.5)
            nxt = alive & ~viol
            if nxt.any():           # a filter that excludes everything is inapplicable,
                alive = nxt         # not satisfied -- see P6, the unsound direction
        y = np.where(alive, y, -np.inf)
        return y, len(idx)
    if arm == "F_random":
        idx = list(rng.choice(len(ok), size=min(K_CORE, len(ok)), replace=False))
        return (Wv[idx, None] * Sfull[idx]).sum(0), len(idx)
    if arm == "G_medoid":
        idx = medoid_clusters(texts, K_CORE)
        return (Wv[idx, None] * Sfull[idx]).sum(0), len(idx)
    if arm == "H_sign_only":
        return (np.sign(Wv)[:, None] * Sfull).sum(0), len(ok)
    raise ValueError(arm)


ARMS = ["A_official", "B_full", "C_signed_topk", "D_decision", "E_typed",
        "F_random", "G_medoid", "H_sign_only"]


# ------------------------------------------------------------------ main
def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    INSTR = {
        "base":       (load_sat(R4 / "a04_full.npz"),      load_sat(R4 / "a04_core.npz")),
        "phi":        (load_sat(R164 / "sat_full_phi.npz"), load_sat(R164 / "sat_core_phi.npz")),
        "qwen3b":     (load_sat(R164 / "sat_full_qwen3b.npz"),
                       load_sat(R164 / "sat_core_qwen3b.npz")),
        "swapped":    (load_sat(R164 / "sat_full_variant_swapped.npz"),
                       load_sat(R164 / "sat_core_variant_swapped.npz")),
        "no_fewshot": (load_sat(R164 / "sat_full_variant_no_fewshot.npz"),
                       load_sat(R164 / "sat_core_variant_no_fewshot.npz")),
    }
    from covalx.judge import load_join
    recs = {pid: r for pid, _p, r in load_join(DATA / "comparisons.jsonl",
                                               DATA / "conversation_rubrics.jsonl")}
    ann = defaultdict(list)
    for line in (DATA / "merged_comparisons_annotators.jsonl").open():
        r = json.loads(line)
        ann[r["prompt_id"]].append(r)

    base_sf = INSTR["base"][0]
    pids = sorted(p for p in base_sf if p in recs and p in ann)

    # hits[instrument][arm] = [n_correct_pairs, n_pairs]; per-group and per-prompt kept too
    hits = {ins: {a: [0, 0] for a in ARMS} for ins in INSTR}
    grp = {ins: {a: defaultdict(lambda: [0, 0]) for a in ARMS} for ins in INSTR}
    regret = {ins: {a: [] for a in ARMS} for ins in INSTR}
    vetoed = {ins: {a: [0, 0] for a in ARMS} for ins in INSTR}
    kcrit, kchar = defaultdict(list), defaultdict(list)
    rand_seed_acc = {ins: defaultdict(lambda: [0, 0]) for ins in INSTR}
    transport = {a: Counter() for a in ARMS}
    boot_incl = defaultdict(Counter)     # criterion text -> times selected by D over bootstraps
    boot_acc = defaultdict(lambda: [0, 0])
    n_used = 0
    n_longform = 0
    veto_chance = []
    veto_maj_chance = []
    vetoed_maj = {ins: {a: [0, 0] for a in ARMS} for ins in INSTR}
    nfull = {}
    long_raters = []

    for p in pids:
        f = recs[p]["coval_full"]
        ok = [i for i, it in enumerate(f)
              if it.get("scores") and all(base_sf[p].get((i, x)) is not None for x in L)]
        if len(ok) < K_CORE:
            continue
        texts = [str(f[i].get("criterion", "")) for i in ok]
        raw = {i: [float(s_["score"]) for s_ in f[i]["scores"]] for i in ok}
        aid = {i: [s_["annotator_id"] for s_ in f[i]["scores"]] for i in ok}
        Wv = np.array([np.mean(raw[i]) for i in ok], float)

        # ---- human rankings, and the demographic group of each rater
        rank_rows, veto, has_long, n_long_raters = [], set(), False, 0
        veto_votes = {}
        for a in ann[p]:
            rb = a.get("ranking_blocks") or {}
            v = parse_veto(rb.get("unacceptable"))
            # ⚠ the first version tested `"unacceptable" in rb`, and the KEY is present on
            # every row -- empty for short form. So "long-form only" was computed on 100% of
            # prompts. Long form is marked by a NON-EMPTY personal block: 4,901 of 18,384
            # assessments, 26.66%, exactly the audited coverage.
            if rb.get("personal"):
                has_long = True
                n_long_raters += 1
            veto |= v
            for a_, cnt in ((x, 1) for x in parse_veto(rb.get("unacceptable"))):
                veto_votes[a_] = veto_votes.get(a_, 0) + cnt
            for e in (rb.get("world") or []):
                pts = parse_rank(e.get("ranking"))
                if pts is not None:
                    dem = (a.get("demographics") or {})
                    rank_rows.append((pts, dem))
        if not rank_rows:
            continue
        n_used += 1
        if has_long:
            # ⚠ P5: a rate with no floor is not a measurement. If the UNION of long-form
            # raters' vetoes covers 2.4 of the 4 responses, then picking uniformly at random
            # already "violates" 60% of the time and every arm scoring 60% is scoring chance.
            veto_chance.append(len(veto) / 4.0)
            maj = {a_ for a_, v in veto_votes.items() if v > n_long_raters / 2}
            veto_maj_chance.append(len(maj) / 4.0)
            veto_major = maj
        else:
            veto_major = set()
        n_longform += int(has_long)
        long_raters.append(n_long_raters)
        nfull[p] = len(ok)

        dsub_cache = {}
        for ins, (sf, sc) in INSTR.items():
            if p not in sf:
                continue
            Sfull = np.array([[sf[p][(i, x)] for x in L] for i in ok], float)
            ci = sorted({k[0] for k in (sc.get(p) or {})})
            core_S = (np.array([[sc[p][(j, x)] for x in L] for j in ci], float)
                      if ci and all((j, x) in sc[p] for j in ci for x in L) else None)
            # D is fitted ONCE, on the build instrument, and reused everywhere else
            if "D" not in dsub_cache:
                Sb = np.array([[base_sf[p][(i, x)] for x in L] for i in ok], float)
                dsub_cache["D"] = greedy_decision_subset(Wv, Sb, K_CORE)
            dsub = dsub_cache["D"]
            y_full = (Wv[:, None] * Sfull).sum(0)
            span = float(y_full.max() - y_full.min()) or 1.0

            for arm in ARMS:
                if arm == "F_random":
                    # ⚠ THE FIRST VERSION OF THIS AVERAGED THE 20 SEEDS' SCORE VECTORS AND
                    # SCORED THE AVERAGE. That is not a size-4 arm -- an ensemble of 20
                    # random 4-subsets approximates the FULL weighted sum, so the "floor"
                    # came out at 0.6848, above every real 4-criterion compiler, and K2 read
                    # REFUTED off a control that was secretly the reference arm. The floor is
                    # the per-seed distribution; a single draw of four criteria is the object
                    # the compressed arms have to beat.
                    accs = []
                    for s in RAND_SEEDS:
                        rng = np.random.default_rng(abs(hash((p, s))) % (2 ** 32))
                        y, kc = arm_scores(arm, ok, Wv, Sfull, core_S, texts, rng=rng)
                        c = sum(1 for pts, _ in rank_rows for i, j in kendall_pairs(pts)
                                if y[i] > y[j])
                        t = sum(len(kendall_pairs(pts)) for pts, _ in rank_rows)
                        rand_seed_acc[ins][s][0] += c; rand_seed_acc[ins][s][1] += t
                        hits[ins][arm][0] += c; hits[ins][arm][1] += t
                        for pts, dem in rank_rows:
                            for i, j in kendall_pairs(pts):
                                g_ok = int(y[i] > y[j])
                                for gk, gv in dem.items():
                                    g = grp[ins][arm][(gk, str(gv))]
                                    g[0] += g_ok; g[1] += 1
                        w = int(np.argmax(y))
                        regret[ins][arm].append(
                            (float(y_full.max()) - float(y_full[w])) / span)
                        if has_long:
                            vetoed[ins][arm][0] += int(L[w] in veto)
                            vetoed[ins][arm][1] += 1
                            vetoed_maj[ins][arm][0] += int(L[w] in veto_major)
                            vetoed_maj[ins][arm][1] += 1
                    if ins == "base":
                        kcrit[arm].append(kc)
                        kchar[arm].append(int(np.mean([len(t_) for t_ in texts]) * kc))
                    continue
                else:
                    y, kc = arm_scores(arm, ok, Wv, Sfull, core_S, texts, dsubset=dsub)
                if y is None or not np.isfinite(y).any():
                    continue
                if ins == "base":
                    kcrit[arm].append(kc)
                    kchar[arm].append(sum(len(texts[i]) for i in range(len(ok)))
                                      if arm in ("B_full", "H_sign_only")
                                      else int(np.mean([len(t) for t in texts]) * kc))
                for pts, dem in rank_rows:
                    for i, j in kendall_pairs(pts):
                        good = int(y[i] > y[j])
                        hits[ins][arm][0] += good; hits[ins][arm][1] += 1
                        for gk, gv in dem.items():
                            g = grp[ins][arm][(gk, str(gv))]
                            g[0] += good; g[1] += 1
                w = int(np.argmax(y))
                regret[ins][arm].append((float(y_full.max()) - float(y_full[w])) / span)
                if has_long:
                    vetoed[ins][arm][0] += int(L[w] in veto); vetoed[ins][arm][1] += 1
                    vetoed_maj[ins][arm][0] += int(L[w] in veto_major)
                    vetoed_maj[ins][arm][1] += 1

        # ---- transport: delete one source criterion, does the arm move as Full moves?
        Sb = np.array([[base_sf[p][(i, x)] for x in L] for i in ok], float)
        base_full = (Wv[:, None] * Sb).sum(0)
        for d in range(len(ok)):
            keep = [i for i in range(len(ok)) if i != d]
            fd = (Wv[keep, None] * Sb[keep]).sum(0)
            dfull = np.sign((base_full[0] - base_full[1]) - (fd[0] - fd[1]))
            for arm in ARMS:
                if arm in ("F_random",):
                    continue
                if arm == "A_official":
                    transport[arm]["NOT_IDENTIFIED_no_lineage"] += 1
                    continue
                try:
                    y0, _ = arm_scores(arm, ok, Wv, Sb, None, texts,
                                       dsubset=dsub_cache.get("D"))
                    sub = greedy_decision_subset(Wv[keep], Sb[keep], K_CORE) \
                        if arm in ("D_decision", "E_typed") else None
                    y1, _ = arm_scores(arm, keep, Wv[keep], Sb[keep], None,
                                       [texts[i] for i in keep], dsubset=sub)
                except Exception:
                    continue
                if y0 is None or y1 is None or not np.isfinite(y0).all() \
                        or not np.isfinite(y1).all():
                    transport[arm]["NOT_IDENTIFIED_undefined"] += 1
                    continue
                darm = np.sign((y0[0] - y0[1]) - (y1[0] - y1[1]))
                if dfull == 0:
                    transport[arm]["NOT_IDENTIFIED_source_flat"] += 1
                elif darm == 0:
                    transport[arm]["lost"] += 1
                elif darm == dfull:
                    transport[arm]["same_direction"] += 1
                else:
                    transport[arm]["inverted"] += 1

        # ---- K5: bootstrap annotators, does D's SUBSET move while accuracy stays flat?
        allA = sorted({a for i in ok for a in aid[i]})
        if len(allA) >= 4:
            for s in BOOT_SEEDS:
                rng = np.random.default_rng(abs(hash((p, "boot", s))) % (2 ** 32))
                take = set(rng.choice(allA, size=len(allA), replace=True))
                Wb = np.array([np.mean([v for v, a in zip(raw[i], aid[i]) if a in take]
                                       or [np.mean(raw[i])]) for i in ok], float)
                sub = greedy_decision_subset(Wb, Sb, K_CORE)
                for i in sub:
                    boot_incl[p][texts[i]] += 1
                y = (Wb[sub, None] * Sb[sub]).sum(0)
                c = sum(1 for pts, _ in rank_rows for i, j in kendall_pairs(pts) if y[i] > y[j])
                t = sum(len(kendall_pairs(pts)) for pts, _ in rank_rows)
                boot_acc[s][0] += c; boot_acc[s][1] += t

    # ------------------------------------------------------------------ assemble
    def acc(d):
        return d[0] / d[1] if d[1] else float("nan")

    res = {"prompts_used": n_used, "prompts_longform": n_longform,
           "longform_raters_per_prompt_median": float(np.median(long_raters)) if long_raters else None,
           "instruments": list(INSTR), "arms": ARMS, "K_core": K_CORE}
    res["rank_acc"] = {ins: {a: acc(hits[ins][a]) for a in ARMS} for ins in INSTR}
    res["pairs"] = {ins: {a: hits[ins][a][1] for a in ARMS} for ins in INSTR}
    res["regret"] = {ins: {a: (float(np.mean(regret[ins][a])) if regret[ins][a] else None)
                           for a in ARMS} for ins in INSTR}
    res["veto_rate"] = {ins: {a: (vetoed[ins][a][0] / vetoed[ins][a][1]
                                  if vetoed[ins][a][1] else None) for a in ARMS}
                        for ins in INSTR}
    res["veto_rate_majority"] = {ins: {a: (vetoed_maj[ins][a][0] / vetoed_maj[ins][a][1]
                                           if vetoed_maj[ins][a][1] else None) for a in ARMS}
                                 for ins in INSTR}
    res["veto_chance_floor"] = float(np.mean(veto_chance)) if veto_chance else None
    res["veto_majority_chance_floor"] = float(np.mean(veto_maj_chance)) if veto_maj_chance else None
    res["K"] = {a: {"criteria_median": float(np.median(kcrit[a])) if kcrit[a] else None,
                    "chars_median": float(np.median(kchar[a])) if kchar[a] else None}
                for a in ARMS}
    res["worst_group"] = {}
    for ins in INSTR:
        res["worst_group"][ins] = {}
        for a in ARMS:
            gs = [(k, acc(v), v[1]) for k, v in grp[ins][a].items() if v[1] >= 2000]
            if not gs:
                res["worst_group"][ins][a] = None; continue
            gs.sort(key=lambda t: t[1])
            res["worst_group"][ins][a] = {"worst": gs[0][1], "group": "|".join(gs[0][0]),
                                          "best": gs[-1][1], "spread": gs[-1][1] - gs[0][1],
                                          "n_groups": len(gs)}
    res["transport"] = {a: dict(transport[a]) for a in ARMS}
    res["random_floor_seed_spread"] = {
        ins: {"mean": float(np.mean([acc(v) for v in rand_seed_acc[ins].values()])),
              "min": float(np.min([acc(v) for v in rand_seed_acc[ins].values()])),
              "max": float(np.max([acc(v) for v in rand_seed_acc[ins].values()]))}
        for ins in INSTR}
    incl, chance = [], []
    for p, c in boot_incl.items():
        tot = sum(c.values()) / K_CORE if c else 0
        for t, n in c.items():
            incl.append(n / tot if tot else 0)
        if p in nfull and nfull[p]:
            # if selection were random, each criterion enters with probability k/n
            chance += [min(1.0, K_CORE / nfull[p])] * len(c)
    res["bootstrap"] = {
        "acc_by_seed": {str(s): acc(v) for s, v in sorted(boot_acc.items())},
        "acc_spread": (max(acc(v) for v in boot_acc.values())
                       - min(acc(v) for v in boot_acc.values())) if boot_acc else None,
        "inclusion_prob_median": float(np.median(incl)) if incl else None,
        "inclusion_prob_share_above_0.9": float(np.mean([x >= 0.9 for x in incl])) if incl else None,
        "inclusion_prob_share_below_0.5": float(np.mean([x < 0.5 for x in incl])) if incl else None,
        "chance_inclusion": float(np.mean(chance)) if chance else None,
        "distinct_criteria_ever_selected": len(incl),
    }
    (OUT / "tournament.json").write_text(json.dumps(res, indent=1))

    # ------------------------------------------------------------------ report
    print("prompts used %d   long-form subset %d (%.1f%%)"
          % (n_used, n_longform, 100 * n_longform / max(n_used, 1)))
    print("\n=== rank_acc : predicting the humans' own world rankings ===")
    print("%-15s %s" % ("arm", "  ".join("%10s" % i for i in INSTR)))
    for a in ARMS:
        print("%-15s %s" % (a, "  ".join("%10.4f" % res["rank_acc"][i][a] for i in INSTR)))
    rf = res["random_floor_seed_spread"]
    print("%-15s %s   <- 20-seed spread of the size-matched floor"
          % ("F_random range", "  ".join("%4.3f-%4.3f" % (rf[i]["min"], rf[i]["max"])
                                         for i in INSTR)))

    print("\n=== regret in B_full's own units (D_decision CIRCULAR, excluded from verdicts) ===")
    for a in ARMS:
        print("%-15s %s%s" % (a, "  ".join("%10.4f" % (res["regret"][i][a] or float("nan"))
                                           for i in INSTR),
                              "   <- fitted to this" if a == "D_decision" else ""))

    print("\n=== veto_rate : picks a response somebody called unacceptable (long-form only) ===")
    for a in ARMS:
        print("%-15s %s" % (a, "  ".join("%10s" % (("%.4f" % res["veto_rate"][i][a])
                                                   if res["veto_rate"][i][a] is not None else "--")
                                         for i in INSTR)))

    print("   chance floor (uniform pick) union %.4f   majority %.4f"
          % (res["veto_chance_floor"], res["veto_majority_chance_floor"]))
    print("\n=== veto_rate, MAJORITY of long-form raters (a real constraint, not a union) ===")
    for a in ARMS:
        print("%-15s %s" % (a, "  ".join("%10s" % (("%.4f" % res["veto_rate_majority"][i][a])
              if res["veto_rate_majority"][i][a] is not None else "--") for i in INSTR)))
    print("   chance floor %.4f" % res["veto_majority_chance_floor"])
    print("\n=== worst_group on base : is the loss concentrated? ===")
    for a in ARMS:
        w = res["worst_group"]["base"][a]
        print("%-15s worst %.4f  best %.4f  spread %.4f  (%s)"
              % (a, w["worst"], w["best"], w["spread"], w["group"][:44]) if w else a)

    forced = float(np.mean([max(0.0, (n - K_CORE) / n) for n in nfull.values()]))
    res["transport_forced_lost_share"] = forced
    print("\n=== transport : delete a source criterion, does the arm move as Full moves? ===")
    print("  ARITHMETIC BASELINE: a k-of-n compiler CANNOT react to a criterion it dropped, so")
    print("  lost >= %.1f%% is forced by k=%d and median n, not measured. Only INVERTED is a"
          % (100 * forced, K_CORE))
    print("  finding: the arm moved, and it moved the WRONG WAY.")
    for a in ARMS:
        t = transport[a]
        tot = sum(t.values()) or 1
        ident = t["same_direction"] + t["inverted"] + t["lost"]
        print("%-15s same %5.1f%%  inverted %5.1f%%  lost %5.1f%% (forced %4.1f%%)"
              "   NOT IDENTIFIED %5.1f%%"
              % (a, 100 * t["same_direction"] / max(ident, 1), 100 * t["inverted"] / max(ident, 1),
                 100 * t["lost"] / max(ident, 1),
                 100 * forced if a not in ("B_full", "H_sign_only") else 0.0,
                 100 * (tot - ident) / tot))

    print("\n=== K : what a human must read ===")
    for a in ARMS:
        k = res["K"][a]
        print("%-15s criteria %5s   chars %6s"
              % (a, k["criteria_median"], k["chars_median"]))

    b = res["bootstrap"]
    print("\n=== K5 : bootstrap annotators, does the SELECTED SUBSET move? ===")
    print(" accuracy spread across %d bootstraps : %.4f" % (len(BOOT_SEEDS), b["acc_spread"]))
    print(" inclusion probability   median %.3f | share >=0.9 %.3f | share <0.5 %.3f"
          % (b["inclusion_prob_median"], b["inclusion_prob_share_above_0.9"],
             b["inclusion_prob_share_below_0.5"]))

    # ------------------------------------------------------------------ death conditions
    print("\n" + "=" * 78)
    print("PRE-REGISTERED DEATH CONDITIONS")
    print("=" * 78)
    ra = res["rank_acc"]

    def verdict(name, claim, cond, detail):
        v = "SUPPORTED" if cond is True else ("REFUTED" if cond is False else "NOT IDENTIFIED")
        print("%-4s %-52s %s\n     %s" % (name, claim, v, detail))
        return v

    ev = ["phi", "qwen3b"]
    d_adv = {i: ra[i]["D_decision"] - ra[i]["A_official"] for i in ev}
    k1 = all(d_adv[i] > 0 for i in ev)
    verdicts = {}
    verdicts["K1"] = verdict("K1", "D_decision more faithful than A_official", k1,
                             "advantage on evaluation judges: " +
                             ", ".join("%s %+0.4f" % (i, d_adv[i]) for i in ev) +
                             "  | on the build judge: base %+0.4f"
                             % (ra["base"]["D_decision"] - ra["base"]["A_official"]))
    # the floor is the BEST single random draw, not the mean: an arm that only beats the
    # average random subset has not beaten "pick four at random and get lucky".
    k2 = all(ra[i]["D_decision"] > rf[i]["max"] for i in ev)
    verdicts["K2"] = verdict("K2", "decision-fitting beats a size-matched random draw", k2,
                             "  ".join("%s: D %0.4f vs random draws [%0.4f, %0.4f]"
                                       % (i, ra[i]["D_decision"], rf[i]["min"], rf[i]["max"])
                                       for i in ev))
    k2b = all(ra[i]["A_official"] > rf[i]["max"] for i in ev)
    verdicts["K2_official"] = verdict("K2*", "the OFFICIAL core beats a random draw too", k2b,
                                      "  ".join("%s: A %0.4f vs random draws [%0.4f, %0.4f]"
                                                % (i, ra[i]["A_official"], rf[i]["min"],
                                                   rf[i]["max"]) for i in ev))
    vb = res["veto_rate_majority"]["base"]
    k3 = (None if vb["E_typed"] is None or vb["D_decision"] is None
          else vb["E_typed"] < vb["D_decision"])
    verdicts["K3"] = verdict("K3", "typing prevents type collapse", k3,
                             "majority-veto rate  E_typed %.4f  vs  D_decision %.4f  "
                             "(chance %.4f)"
                             % (vb["E_typed"], vb["D_decision"],
                                res["veto_majority_chance_floor"]))
    wg = res["worst_group"]["base"]
    comp = ["A_official", "C_signed_topk", "D_decision", "E_typed", "G_medoid"]
    k4 = all((wg["B_full"]["worst"] - wg[a]["worst"]) <=
             (ra["base"]["B_full"] - ra["base"][a]) + 1e-9 for a in comp if wg.get(a))
    verdicts["K4"] = verdict("K4", "compression preserves pluralism", k4,
                             "  ".join("%s worst-deficit %+0.4f vs mean-deficit %+0.4f"
                                       % (a, wg["B_full"]["worst"] - wg[a]["worst"],
                                          ra["base"]["B_full"] - ra["base"][a])
                                       for a in comp if wg.get(a)))
    # ⚠ the first version fired this off "share >= 0.9 exceeds 0.5", and 0.5 was a round
    # number I picked -- the exact failure the preregistration forbids two paragraphs above
    # its own verdict table. The floor is what inclusion would be if selection were random:
    # k/n per criterion, measured on the same prompts.
    chance = b.get("chance_inclusion")
    k5 = (None if chance is None else
          (b["inclusion_prob_median"] > chance and b["inclusion_prob_share_below_0.5"] < 0.10))
    verdicts["K5"] = verdict("K5", "selection is stable enough to name ONE Core", k5,
                             "median inclusion %.3f vs chance %.3f -- selection is far from "
                             "random -- but %.1f%% of chosen criteria appear in under half the "
                             "bootstraps while accuracy moves only %.4f, so the right output is "
                             "an inclusion table, not a rubric"
                             % (b["inclusion_prob_median"], chance,
                                100 * b["inclusion_prob_share_below_0.5"], b["acc_spread"]))
    res["verdicts"] = verdicts
    (OUT / "tournament.json").write_text(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
