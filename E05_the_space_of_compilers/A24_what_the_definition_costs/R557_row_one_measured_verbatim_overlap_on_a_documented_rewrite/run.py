#!/usr/bin/env python3
"""R557 · Row 1's "6.6% reconstructible" used an EXACT-MATCH instrument on a documented REWRITE.

Row 1 blocks ③' on the released core because only 6.6% of core criteria appear VERBATIM in
coval_full, and asks for the field `coval_core[i].source_rubric_item_ids`. But the dataset card
documents a REWRITE AND MERGE before selection -- so a rewrite is exactly what verbatim matching
cannot see. The row named an OBJECT (that field) where the requirement is a PROPERTY: a
recoverable mapping from core item to source items.

ESTIMAND  can a core item's source items be recovered by SIMILARITY rather than by identity?
          Reported as top-1 accuracy on cases where the answer is known, then as a sharpness
          distribution where it is not.
IDENT     PARTIALLY identified. There is no ground-truth mapping -- that absence is the row.
          So: identified on the VERBATIM subset (source known), and only BOUNDED elsewhere,
          via how sharp the match is. No point estimate of accuracy on the unknown 93.4%.
SCOPE     population = prompts carrying both coval_full and coval_core · instrument = TF-IDF
          word+char n-grams · baseline = matching against a DIFFERENT prompt's rubric ·
          regime = per-prompt candidate sets.
WORLDS    A the instrument cannot recover even the KNOWN cases -> row 1 stands as written and
            the field really is the only route.
          B it recovers the known cases -> "6.6%" measured the wrong thing, and the row's
            price is wrong: partial recovery is available here with no new field.
KILL      pre-registered: top-1 on the verbatim subset < 0.90 -> WORLD A, instrument unfit,
          verdict UNVERIFIED rather than a claim about the 93.4%.
POS CTRL  the verbatim subset IS the positive control: the source is known by construction.
PLACEBO   match each core item against a DIFFERENT prompt's rubric. Must collapse; if it does
          not, the similarity is generic and says nothing about provenance.
ARTIFACT  results/row_one.json
"""
import json, pathlib, re, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from sklearn.feature_extraction.text import TfidfVectorizer
from covalx.judge import load_join

def norm(s): return re.sub(r"\s+", " ", str(s).strip().lower())

joined = load_join(ROOT / "data" / "comparisons.jsonl",
                   ROOT / "data" / "conversation_rubrics.jsonl")
prompts = []
for pid, _pr, rub in joined:
    full = [norm(c["criterion"] if isinstance(c, dict) else c) for c in rub.get("coval_full", [])]
    core = [norm(c["criterion"] if isinstance(c, dict) else c) for c in rub.get("coval_core", [])]
    if len(full) >= 2 and core:
        prompts.append((pid, full, core))
if not prompts:
    print("  no prompts with both rubrics -> UNRUNNABLE"); sys.exit(2)
print(f"  prompts with both coval_full and coval_core: {len(prompts)}")

# the KNOWN subset: a core item appearing verbatim in its own prompt's full rubric
known = [(i, j, full.index(c))
         for i, (pid, full, core) in enumerate(prompts)
         for j, c in enumerate(core) if c in full]
n_core = sum(len(c) for _p, _f, c in prompts)
print(f"  core items total: {n_core}   verbatim-matchable (source KNOWN): {len(known)} "
      f"= {len(known)/n_core:.1%}")
if not known:
    print("  no known cases -> the positive control is impossible -> UNRUNNABLE"); sys.exit(2)

vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=1)
vec.fit([t for _p, f, c in prompts for t in f + c])

def rank(core_text, cands):
    M = vec.transform(cands); q = vec.transform([core_text])
    sims = (M @ q.T).toarray().ravel()
    order = np.argsort(-sims)
    return order, sims

# ── POSITIVE CONTROL: recover the known sources ───────────────────────────────────
hits, margins = 0, []
for i, j, tgt in known:
    _pid, full, core = prompts[i]
    order, sims = rank(core[j], full)
    hits += int(order[0] == tgt)
    if len(sims) > 1:
        margins.append(float(sims[order[0]] - sims[order[1]]))
top1 = hits / len(known)
print(f"\n  POSITIVE CONTROL  top-1 on the KNOWN subset: {top1:.4f} of {len(known)} "
      f"-> {'PASS' if top1 >= 0.90 else 'FAIL (kill fires: instrument unfit)'}")

# ── PLACEBO: match against a DIFFERENT prompt's rubric ─────────────────────────────
rng = np.random.default_rng(0)
pl_hits = 0
for i, j, _tgt in known:
    _pid, _full, core = prompts[i]
    k = int(rng.integers(0, len(prompts)))
    if k == i: k = (k + 1) % len(prompts)
    other = prompts[k][1]
    order, sims = rank(core[j], other)
    # "hit" = the wrong-prompt best match scores at least as well as the right-prompt best
    _o2, s2 = rank(core[j], prompts[i][1])
    pl_hits += int(sims.max() >= s2.max())
placebo = pl_hits / len(known)
print(f"  PLACEBO           wrong-prompt rubric matches as well: {placebo:.4f} -> "
      f"{'PASS' if placebo < 0.10 else 'FAIL -- similarity is generic'}")

if top1 < 0.90:
    world = "A"
elif placebo >= 0.10:
    world = "A"
else:
    world = "B"

# ── the BOUND on the unknown 93.4%: how sharp is the match where truth is unavailable ──
unk_margin = []
for i, (pid, full, core) in enumerate(prompts):
    for j, c in enumerate(core):
        if c in full: continue
        order, sims = rank(c, full)
        if len(sims) > 1:
            unk_margin.append(float(sims[order[0]] - sims[order[1]]))
kn_m, un_m = np.array(margins), np.array(unk_margin)
print(f"\n  top1-minus-top2 margin   KNOWN  median {np.median(kn_m):.4f}  n={len(kn_m)}")
print(f"                           UNKNOWN median {np.median(un_m):.4f}  n={len(un_m)}")
frac_sharp = float((un_m >= np.percentile(kn_m, 10)).mean())
print(f"  unknown items whose margin clears the KNOWN set's 10th percentile: {frac_sharp:.1%}")
print(f"  ⚠ that is a BOUND on identifiability, not an accuracy -- no ground truth exists here.")

print(f"\n  WORLD {world} -- " + (
    "similarity recovers the known sources and collapses on the wrong prompt; '6.6% verbatim' "
    "measured identity, not recoverability."
    if world == "B" else
    "the instrument fails its own control; row 1 stands and this is UNVERIFIED."))
(pathlib.Path(__file__).parent / "results" / "row_one.json").write_text(json.dumps(
    {"world": world, "n_prompts": len(prompts), "n_core_items": n_core,
     "n_known_verbatim": len(known), "verbatim_share": len(known)/n_core,
     "pos_ctrl_top1": top1, "placebo_wrongprompt_ge": placebo,
     "margin_known_median": float(np.median(kn_m)), "margin_unknown_median": float(np.median(un_m)),
     "unknown_frac_clearing_known_p10": frac_sharp,
     "identification": "partial: accuracy identified only on the verbatim subset; elsewhere a "
                       "sharpness BOUND, because no ground-truth mapping exists -- that absence "
                       "IS register row 1"}, indent=2))
