#!/usr/bin/env python3
"""A published SHARE must carry the two integers it was computed from.

⛔ WHY, measured. R883 swept every artifact in the corpus: **3,014 published shares across 417
files, of which 1,788 (59.3%) cannot be recomputed from any two integers in the same file.** A
share with no `n` and no `d` beside it is **unauditable independently of whether it is correct** —
and that is the property that let the wrong-denominator error survive to be committed **three
times in one session** (R873's over-wide population, the `64 of 550` that was really `64 of 159`,
and R882's own uncorrected rate).

**None of those three was caught by review. They were caught by later rounds that happened to
recompute the same thing.** The necessary condition they all failed is not "was the denominator
right" — it is **"was the denominator written down at all"**, and that is mechanical.

⭐ **THIS GATE IMPORTS R883's `auditable()` RATHER THAN RE-IMPLEMENTING IT.** A second
implementation would make the gate's count and the round's count two different quantities wearing
one name — the borrowed-quantity error this project has spent a dozen rounds catching. If R883's
definition is wrong, both move together and the disagreement stays visible.

PROXY LEDGER
  PROPERTY    the published share can be checked by a reader
  PROXY       two integers in the same artifact reproduce it to 1e-9
  IMPLICATION **no such pair ⇒ not checkable from this file** is SOUND.
              **such a pair exists ⇒ the share is CORRECT** is NOT — the recorded `d` may still be
              the wrong denominator, which is exactly what happened three times. This rules on
              CHECKABILITY only and says so rather than implying more.
  SAFE SIDE   flags shares with no recoverable counts. An auditable share is UNVERIFIED, never
              certified.

⚠ A coincidental pair can satisfy the proxy — with enough integers in a file, some `n/d` will match
by luck. That inflates the auditable side, so the 59.3% unauditable is a LOWER bound on the
problem, not an upper one. Named here rather than discovered later.
"""
import importlib.util, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
FROZEN = pathlib.Path(__file__).resolve().parent / "KNOWN_UNAUDITABLE_SHARES.json"
R883 = next(ROOT.glob("E0*/A*/R883_*/run.py"), None)


def _load_r883():
    if R883 is None:
        return None
    spec = importlib.util.spec_from_file_location("r883", R883)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def scan(m):
    rows = []
    for f in sorted(ROOT.glob("E0*/A*/R*/results/*.json")):
        try:
            obj = json.loads(f.read_text())
        except Exception:
            continue
        ints = m.ints_in(obj)
        for path, v in m.walk(obj):
            if not isinstance(v, float) or isinstance(v, bool):
                continue
            leaf = path.split(".")[-1].split("[")[0]
            if not m.SHARE_KEY.search(leaf) or not (0.0 <= v <= 1.0):
                continue
            if m.auditable(v, ints) is None:
                rows.append(f"{f.relative_to(ROOT)}::{path}")
    return rows


def controls(m) -> bool:
    a = next(ROOT.glob("E0*/A*/R872_*/results/endpoint_claims.json"), None)
    p1 = False
    if a:
        d = json.loads(a.read_text())
        p1 = m.auditable(d.get("endpoint_only_rate"), m.ints_in(d)) is not None
    fake = {"rate": 0.4031446540880503}
    p2 = m.auditable(fake["rate"], m.ints_in(fake)) is None
    print(f"  POSITIVE  R872's REAL 0.4884 recomputes as 21/43, not flagged: {p1}  "
          f"{'PASS' if p1 else 'FAIL'}")
    print(f"  g=0       a bare {{'rate': 0.403}} with no counts IS flagged: {p2}  "
          f"{'PASS' if p2 else 'FAIL'}")
    print("    Both arms are the ones R883 used. This gate imports its `auditable()` rather than")
    print("    re-implementing it, so the gate and the round cannot drift into two quantities.")
    return p1 and p2


def main() -> int:
    m = _load_r883()
    if m is None:
        print("  UNRUNNABLE: R883's module not found, so the shared definition is unavailable.")
        print("  Exit 2, never 0 — re-implementing it here is exactly what this file refuses.")
        return 2
    if not controls(m):
        print("\n  UNVERIFIED: the detector failed its own controls. Exit 2, never 0.")
        return 2
    rows = scan(m)
    if not rows and not FROZEN.exists():
        print("\n  OBSERVED NOTHING: no unauditable share and no baseline. A check with no")
        print("  population has not passed — it has not run. Exit 2, never 0.")
        return 2
    frozen = set(json.loads(FROZEN.read_text())["keys"]) if FROZEN.exists() else set()
    new = [r for r in rows if r not in frozen]
    print(f"\n  {len(rows)} unauditable share(s) · {len(frozen)} frozen · {len(new)} NEW")
    if new:
        print(f"\n  FAIL: {len(new)} share(s) published with no counts to recompute them:")
        for r in new[:10]:
            print(f"    {r}")
        print("  Write the numerator and denominator into the artifact beside the share.")
        print("  59.3% of this corpus is unauditable and three wrong denominators reached")
        print("  commit because nothing could have checked them.")
        return 1
    print("\n  PASS: no NEW unauditable share. ⚠ An auditable share is UNVERIFIED, never")
    print("  certified — the recorded denominator may still be the WRONG one, which is what")
    print("  happened three times. This rules on CHECKABILITY only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
