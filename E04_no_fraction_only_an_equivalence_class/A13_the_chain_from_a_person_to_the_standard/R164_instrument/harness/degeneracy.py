"""Task 4: is a04_full.npz / a04_core.npz degenerate anywhere -- saturated at 0/1, constant
per criterion, identical across responses? A judge that outputs near-constant values for a
criterion contributes nothing but noise to every arm that uses it.
"""
import numpy as np
from collections import defaultdict

ROOT = "/home/ivan/research.trustworthy-ai.coval-deep-analysis.build.lg.private.editable"

for name, path in [("full", f"{ROOT}/E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results/a04_full.npz"),
                    ("core", f"{ROOT}/E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results/a04_core.npz")]:
    z = np.load(path, allow_pickle=True)
    sat, meta = z["sat"], z["meta"]
    print(f"\n=== {name}: {len(sat)} rows ===")
    print(f"  global: mean={sat.mean():.4f} sd={sat.std():.4f} "
          f"min={sat.min():.4f} max={sat.max():.4f}")
    sat_hi = (sat > 0.99).mean()
    sat_lo = (sat < 0.01).mean()
    print(f"  saturated >0.99: {sat_hi:.2%}   saturated <0.01: {sat_lo:.2%}   "
          f"combined: {sat_hi+sat_lo:.2%}")

    # group by (promptid, criterion_index) -> 4 responses
    groups = defaultdict(dict)
    for s, m in zip(sat, meta):
        pid, ci, lab = str(m).split("|")
        groups[(pid, ci)][lab] = float(s)

    within_sd = []
    all_same_sign_of_mean = []
    n_const = 0
    for key, d in groups.items():
        vals = np.array(list(d.values()))
        if len(vals) < 2:
            continue
        within_sd.append(float(vals.std()))
        if vals.std() < 1e-6:
            n_const += 1
    within_sd = np.array(within_sd)
    print(f"  criterion x prompt groups with >=2 responses: {len(within_sd)}")
    print(f"  within-group (across-response) sd: mean={within_sd.mean():.4f} "
          f"median={np.median(within_sd):.4f}")
    print(f"  groups with within-group sd < 1e-6 (all 4 responses tied): "
          f"{n_const} ({n_const/max(len(within_sd),1):.2%})")
    thresh = 0.02
    n_flat = (within_sd < thresh).sum()
    print(f"  groups with within-group sd < {thresh}: {n_flat} ({n_flat/max(len(within_sd),1):.2%}) "
          f"-- these criteria cannot discriminate among this prompt's 4 responses at all")

    # per-criterion-TEXT degeneracy: some criteria might be constant across the WHOLE dataset
    # (same criterion text always scores ~same value regardless of prompt/response) -- would mean
    # the "criterion" isn't being read, only some generic prior. Group by criterion index position
    # doesn't identify repeated criterion text; approximate via (ci) only within a prompt already
    # covered above. Report the tail: which fraction of criteria carry near-zero discriminative sd.
