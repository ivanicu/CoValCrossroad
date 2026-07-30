"""The frozen frame is irreplaceable. Verify its hashes on every run.

WHY THIS EXISTS
---------------
r45's frame is the only definition of the object H_fresh refers to. Its own verification
block says so: "r12's generation is stochastic and unseeded, so 'the fresh responses' is
not recoverable by re-running anything -- this file is the only definition of the object
H_fresh refers to."

So silent corruption of this file is UNRECOVERABLE. Not "expensive to redo" -- gone. The
human experiment it gates would be rankings of some responses, comparable to nothing.

WHY THIS ONE NEEDS NO JUDGEMENT
--------------------------------
Entries 176, 199 and 201 declined guards that would have had to GUESS -- which section a
finding belongs in, which quantity a CI describes, whether an omission was deliberate.
This one guesses nothing. It recomputes SHA-256 over stated bytes and compares. A
mismatch is not a reading; it is arithmetic.

WHAT IT CHECKS
--------------
  1. every response's sha256 equals sha256 of its own stored text
  2. every prompt's sha256 equals sha256 of its own stored prompt_text
  3. the manifest recomputes, by freeze.py's own recipe, to the stored manifest_sha256
  4. the leaf count is internally consistent: responses + prompts

POSITIVE CONTROL, run before any of it is believed: edit one character of one response
in memory and confirm the manifest MOVES. A hash check that cannot detect a changed byte
is not checking anything, and this refuses to report a pass without demonstrating it.
"""
from __future__ import annotations

import copy
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
FRAME = ROOT / "rounds/05_human_protocol_and_power/r45_protocol_freeze/results/r45_frozen_frame.json"


def sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def manifest_of(rows) -> str:
    """freeze.py's recipe, reproduced exactly: sorted leaves, newline-joined."""
    leaves = sorted(h for r in rows for h in
                    [r["prompt_sha256"]] + [x["sha256"] for x in r["original"]]
                    + [x["sha256"] for x in r["fresh"]] if h)
    return sha("\n".join(leaves)), len(leaves)


def main() -> int:
    if not FRAME.exists():
        print("FINDING: the frozen frame is ABSENT. H_fresh has no admissibility gate and the "
              "responses it refers to are undefined.")
        return 1
    d = json.loads(FRAME.read_text())
    rows = d["prompts"]

    # ---- POSITIVE CONTROL, before anything is believed -------------------------
    base, _ = manifest_of(rows)
    probe = copy.deepcopy(rows)
    probe[0]["original"][0]["text"] += "x"
    probe[0]["original"][0]["sha256"] = sha(probe[0]["original"][0]["text"])
    moved, _ = manifest_of(probe)
    print(f"positive control: one character edited -> manifest "
          f"{'CHANGES' if moved != base else 'UNCHANGED'}")
    if moved == base:
        print("\nFINDING: the manifest does not move when a response changes, so it cannot "
              "detect corruption and a pass would mean nothing.")
        return 1

    # ---- the SAMPLING DESIGN, which item 7 freezes alongside the payload -------
    # Judgement-free arithmetic, same standard as the hashes: cell sizes must match the
    # declared counts, every prompt must carry its own cell's weight, and the weights
    # must be exact inverse-probability weights -- sum(weight x cell_size) recovers the
    # 250-prompt population r12 drew from, and each weight equals stratum/sample.
    sizes: dict = {}
    for r in rows:
        sizes[r["cell"]] = sizes.get(r["cell"], 0) + 1
    w, decl = d["sampling_weights"], d["cells"]
    wrong_w = [(r["pid"], r["cell"]) for r in rows
               if abs(r["sampling_weight"] - w[r["cell"]]) > 1e-12]
    pop = sum(w[k] * decl[k] for k in decl)
    strata = {k: w[k] * decl[k] for k in decl}
    non_int = [k for k, v in strata.items() if abs(v - round(v)) > 1e-9]
    resp_shape = {(len(r["original"]), len(r["fresh"])) for r in rows}
    print(f"  cell sizes match declared          : {sizes == decl}")
    print(f"  prompts carrying their cell weight : {len(rows) - len(wrong_w)}/{len(rows)}")
    print(f"  sum(weight x cell) = population    : {pop:.1f}  strata "
          f"{ {k: round(v) for k, v in strata.items()} }")
    print(f"  responses per prompt (orig, fresh) : {resp_shape}")

    # ---- the cell labels must BE a threshold cross ------------------------------
    # The boundaries are not stored, but they are recoverable: if the 2x2 is a threshold
    # split on the stored `distance` and `disagreement`, then max(low) < min(high) on
    # each axis. If the groups overlap, the labels do not correspond to any threshold on
    # the values in the file, and the strata the weights assume are not the strata
    # present. Entry 203 called this unverifiable; it is not -- it is unstored, which is
    # a different thing (entry 204).
    axes = {}
    for axis, low, hi in (("disagreement", "low_disagree", "high_disagree"),
                          ("distance", "low_dist", "high_dist")):
        L = [r[axis] for r in rows if low in r["cell"]]
        H = [r[axis] for r in rows if hi in r["cell"]]
        axes[axis] = {"n_low": len(L), "n_high": len(H), "max_low": max(L), "min_high": min(H),
                      "separable": max(L) < min(H)}
        a = axes[axis]
        print(f"  {axis:<13} threshold-separable: {a['separable']}"
              + (f"  boundary in ({a['max_low']:.6f}, {a['min_high']:.6f})" if a["separable"]
                 else f"  OVERLAP {a['max_low'] - a['min_high']:+.6f}"))
    unsep = [k for k, v in axes.items() if not v["separable"]]

    # The strata marginals test r38's declared rule (`>= median` on each axis) without
    # needing the 250 prompts themselves. A median split gives 125/125 -- unless values
    # are TIED at the median, which `>=` sends to the high side. Reported because the
    # asymmetry is a design fact a reader would otherwise mis-assume (entry 205).
    S = {k: round(w[k] * decl[k]) for k in decl}
    marg = {
        "disagreement": (S["low_disagree_low_dist"] + S["low_disagree_high_dist"],
                         S["high_disagree_low_dist"] + S["high_disagree_high_dist"]),
        "distance": (S["low_disagree_low_dist"] + S["high_disagree_low_dist"],
                     S["low_disagree_high_dist"] + S["high_disagree_high_dist"]),
    }
    half = round(pop / 2)
    for axis, (a, b) in marg.items():
        note = "exact median split" if a == b == half else f"{b - half} tied at the median -> high"
        print(f"  {axis:<13} strata marginal {a}/{b} of {round(pop)}   ({note})")
    bad_marg = [k for k, (a, b) in marg.items() if a + b != round(pop)]

    bad_r = [(r["pid"], arm, i) for r in rows for arm in ("original", "fresh")
             for i, x in enumerate(r[arm]) if sha(x["text"]) != x["sha256"]]
    bad_p = [r["pid"] for r in rows if sha(r["prompt_text"]) != r["prompt_sha256"]]
    got, n_leaves = manifest_of(rows)
    n_resp = sum(len(r["original"]) + len(r["fresh"]) for r in rows)

    print(f"\n{len(rows)} prompts, {n_resp} responses, {n_leaves} manifest leaves")
    print(f"  response text -> sha256 mismatches : {len(bad_r)}")
    print(f"  prompt  text  -> sha256 mismatches : {len(bad_p)}")
    print(f"  manifest recomputes to stored value: {got == d['manifest_sha256']}")
    print(f"  leaf count = responses + prompts   : {n_leaves == n_resp + len(rows)}")

    fail = 0
    if bad_r or bad_p:
        fail = 1
        print(f"\nFINDING: {len(bad_r) + len(bad_p)} stored hash(es) do not match their own text. "
              f"The payload has been edited since the freeze.")
        for x in (bad_r[:5] + [(p, 'prompt', 0) for p in bad_p[:5]]):
            print(f"    {x}")
    if got != d["manifest_sha256"]:
        fail = 1
        print(f"\nFINDING: the manifest recomputes to {got}, not the stored "
              f"{d['manifest_sha256']}. The frame no longer defines the object H_fresh refers to.")
    if sizes != decl:
        fail = 1
        print(f"\nFINDING: observed cell sizes {sizes} do not match the declared {decl}. The "
              f"stratification the sampling weights assume is not the one in the file.")
    if wrong_w:
        fail = 1
        print(f"\nFINDING: {len(wrong_w)} prompt(s) carry a weight that is not their cell's. Every "
              f"weighted estimate drawn from this frame would be wrong: {wrong_w[:5]}")
    if non_int:
        fail = 1
        print(f"\nFINDING: weight x cell_size is not an integer for {non_int}, so the weights are "
              f"not inverse-probability weights over whole strata.")
    if len(resp_shape) != 1:
        fail = 1
        print(f"\nFINDING: prompts differ in response counts {resp_shape}; the frame is not the "
              f"balanced 4-original/4-fresh design it declares.")
    if bad_marg:
        fail = 1
        print(f"\nFINDING: on {bad_marg} the strata marginals do not sum to the population "
              f"{round(pop)}; the 2x2 does not partition what the weights say it does.")
    if unsep:
        fail = 1
        print(f"\nFINDING: on {unsep} the cell labels are NOT separable by any threshold on the "
              f"stored values -- the groups overlap. The strata the sampling weights assume are "
              f"not the strata present in the file.")
    if n_leaves != n_resp + len(rows):
        fail = 1
        print(f"\nFINDING: {n_leaves} leaves against {n_resp} responses + {len(rows)} prompts.")
    if fail:
        print("\n1 gate(s) failed.")
        return 1
    print("\nthe frozen frame verifies: every hash matches its text and the manifest is intact.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
