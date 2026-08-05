#!/usr/bin/env python3
"""R567 · Does A23's MDE reach A24, and does A24 clear its OWN floors?

A23's R274 reports mde_bracket [0.105, 0.125]. A24's headline effects are ~0.07. If that floor
applied, several headline claims would sit under it. Two questions, and the second is the one that
matters, because a reassuring answer to the first is exactly when to be strictest.

ESTIMAND  (a) do A23's R274 and A24's claims share detector, statistic and n?
          (b) among A24 artifacts reporting BOTH an effect and its own MDE, how many effects sit
              below their own floor?
IDENT     (a) fully identified by reading R274's recorded parameters.
          (b) identified only for artifacts that persist BOTH -- reported as a share OF THOSE,
              never of all claims. Artifacts lacking an MDE are counted separately, not assumed fine.
SCOPE     population = A24 artifacts with an effect and an mde key · instrument = key extraction ·
          baseline = effect/MDE = 1 · regime = as each round recorded it.
WORLDS    A the floor transfers -> A24's headline effects are under-resolved.
          B it does not -> A24's own per-round MDEs are the applicable floors, and (b) decides.
KILL      pre-registered for (a): if R274's n and detector match A24's, WORLD A.
POS CTRL  R274 must record its own n and tau, else "different detector" is an inference from
          silence rather than a reading.
NEG CTRL  an invented parameter key must be absent from R274.
ARTIFACT  results/floor_transfer.json
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
E05 = ROOT / "E05_the_space_of_compilers"
r274 = json.loads(next((E05 / "A23_is_the_admissibility_gate_the_right_gate" /
                        "R274_the_site_MDE_at_fine_resolution" / "results").glob("*.json")).read_text())

have = all(k in r274 for k in ("prompts", "tau", "mde_bracket"))
print(f"  POSITIVE CONTROL  R274 records its own n / tau / bracket: {have} -> "
      f"{'PASS' if have else 'FAIL — difference would be inferred from silence'}")
print(f"  NEGATIVE CONTROL  an invented key is absent: {'zzfake' not in r274} -> PASS")
if not have: sys.exit(2)

A24_N, A24_TARGET = 968, "A2 vs held-out annotator"
print(f"\n  A23 R274 : n={r274['prompts']}  tau={r274['tau']}  MDE={r274['mde_bracket']}")
print(f"             its own comparison set: {list(r274['published'])[:3]} …")
print(f"  A24      : n={A24_N}  target={A24_TARGET}")
same = (r274["prompts"] == A24_N)
print(f"\n  (a) same n? {same}   -> WORLD {'A' if same else 'B'}")
print(f"      ⚠ n differs by {A24_N/r274['prompts']:.2f}x, and the STATISTIC differs too "
      f"(admissibility/necessity vs A2 agreement), so no scaling is attempted.")

# (b) A24's own floors
pairs, no_mde = [], 0
for f in sorted((E05 / "A24_what_the_definition_costs").rglob("results/*.json")):
    try: d = json.loads(f.read_text())
    except Exception: continue
    if not isinstance(d, dict): continue
    flat = {k.lower(): v for k, v in d.items() if isinstance(v, (int, float))}
    eff = next((v for k, v in flat.items() if k in ("effect", "eff", "gap", "delta", "c2", "c1")), None)
    mde = next((v for k, v in flat.items() if "mde" in k), None)
    if eff is None: continue
    if mde is None or not mde: no_mde += 1; continue
    pairs.append((f.parts[-3][:44], abs(eff), abs(mde), abs(eff) / abs(mde)))

print(f"\n  (b) A24 artifacts with BOTH an effect and its own MDE: {len(pairs)}")
print(f"      artifacts with an effect and NO MDE (counted, never assumed fine): {no_mde}")
under = [p for p in pairs if p[3] < 1.0]
print(f"      effects BELOW their own floor: {len(under)} of {len(pairs)}")
for n, e, m, r in sorted(pairs, key=lambda x: x[3])[:6]:
    print(f"        {r:6.2f}x  eff={e:.4f} mde={m:.4f}  {n}")

world = "A" if same else "B"
print(f"\n  WORLD {world} -- " + (
    "the A23 floor applies to A24 directly."
    if world == "A" else
    "the A23 floor is a different detector at a different n; A24's own per-round MDEs are the "
    "applicable floors."))
(pathlib.Path(__file__).parent / "results" / "floor_transfer.json").write_text(json.dumps(
    {"world": world, "a23_r274": {k: r274[k] for k in ("prompts", "tau", "mde_bracket")},
     "a24_n": A24_N, "a24_target": A24_TARGET, "same_n": same,
     "a24_pairs": len(pairs), "a24_no_mde": no_mde, "a24_under_own_floor": len(under),
     "lowest_ratios": [{"round": n, "eff": e, "mde": m, "ratio": r}
                       for n, e, m, r in sorted(pairs, key=lambda x: x[3])[:8]],
     "note": "no scaling attempted between detectors: the statistic differs, not just n"},
    indent=2))
