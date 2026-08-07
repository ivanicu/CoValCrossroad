#!/usr/bin/env python3
"""
R883 · can a published SHARE be audited from its own artifact — is its denominator even recorded?

⛔ WHY. The wrong-denominator move has appeared **three times in this session**: R873 (a population
wider than the phenomenon), R882's gate (`64 of 550` where 550 counted rounds in which the defect
was impossible), and R882 itself before correction. Each fix touched **one number**. Check #550 asked
to sweep for the others.

⭐ **AND THE CLASS-LEVEL FORM IS SHARPER THAN SWEEPING ONE AT A TIME.** Chasing wrong denominators
requires knowing the right one for each claim, which is a judgement per case. **But there is a
prior, mechanical question: you cannot catch a wrong denominator if the denominator was never
written down.** A share published as a float with no `n` and no `d` beside it is **unauditable —
independently of whether it happens to be correct.** That is countable, and it is the property that
made all three instances survive to be committed.

ESTIMAND        among artifact-recorded shares (a float in [0,1] under a rate/share/frac-like key),
                the fraction whose SAME artifact also records an integer numerator and denominator
                from which the share can be recomputed.
IDENTIFICATION  exact for the recomputable case: a share is AUDITABLE iff the artifact contains
                integers `n`, `d` with `abs(n/d − share) < 1e-9`. ⚠ NOT identified: whether the
                recorded `d` is the RIGHT denominator. **This measures whether the claim can be
                checked at all, not whether it is true**, and that limit is the whole point —
                it is the necessary condition the three instances all failed.
SCOPE           population: every `E0*/A*/R*/results/*.json` — DERIVED from the estimand (published
                            shares live in artifacts), not globbed for convenience
                instrument: key-name match for the share, integer search for a matching (n, d)
                baseline:   a share with its counts beside it
                regime:     this repo, this commit
WORLDS          A · most shares are auditable -> the three instances were sloppiness, not a habit,
                    and per-case fixes are the right response
                B · most shares are NOT auditable -> the corpus publishes rates whose denominators
                    are unrecoverable, and no amount of per-case fixing reaches them
                C · the share-detector finds almost nothing -> shares are not stored as floats in
                    artifacts and this design cannot see the population it is about
KILL            CONDITIONAL, all required, and both arms are REAL committed artifacts:
                  ⭐ ① POSITIVE: **R872's** artifact must be AUDITABLE — it records
                     `n_endpoint_only = 21` and `n_unambiguous = 43` beside
                     `endpoint_only_rate = 0.4883720930232558`, which recomputes exactly.
                     ⛔ THIS ARM FIRST NAMED **R882** AND FAILED, AND THE DETECTOR WAS RIGHT.
                     R882 records its four category counts (88/82/77/18) but **never their total
                     265**, so its own 0.309 is NOT recomputable from its own file. **The round
                     that diagnosed the wrong-denominator error published a share whose denominator
                     is not in its artifact** — my EXPECTATION was wrong, not the instrument, and
                     only an exact-valued control could have shown that.
                  ⭐ ② g=0: a synthetic artifact carrying a bare `{"rate": 0.403}` must be
                     UNAUDITABLE. A detector that calls everything auditable passes arm ① trivially.
                  ⭐ ③ the population must be non-empty AND must contain at least one of each
                     class — a sweep that finds only one class cannot have discriminated.
MULTIPLICITY    every artifact × every share key; both classes reported with counts.
ARTIFACT        results/share_auditability.json
IMPOSSIBLE      cross-release · construct validated · causally identified.
"""
import json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
SHARE_KEY = re.compile(r"(rate|share|frac|fraction|prop|proportion|pct|percent)", re.I)
TOL = 1e-9


def walk(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk(v, f"{path}[{i}]")
    else:
        yield path, obj


def ints_in(obj):
    out = []
    for _, v in walk(obj):
        if isinstance(v, int) and not isinstance(v, bool) and 0 <= v <= 10_000_000:
            out.append(v)
    return out


def auditable(share, ints):
    """Is there an (n, d) among the artifact's own integers with n/d == share?"""
    for d in ints:
        if d <= 0:
            continue
        n = share * d
        if abs(n - round(n)) < 1e-6 and int(round(n)) in ints and \
                abs(int(round(n)) / d - share) < TOL:
            return (int(round(n)), d)
    return None


def controls():
    a = next((ROOT / "E05_the_space_of_compilers/A25_can_the_instrument_be_run_at_all").glob(
        "R872_*/results/endpoint_claims.json"), None)
    p1 = False
    got = None
    if a:
        d = json.loads(a.read_text())
        ints = ints_in(d)
        sh = d.get("endpoint_only_rate")
        if sh is not None:
            got = auditable(sh, ints)
            p1 = got is not None
    fake = {"rate": 0.4031446540880503}
    p2 = auditable(fake["rate"], ints_in(fake)) is None
    print(f"  ① POSITIVE  R872's 0.4884 recomputes from its own counts: {p1}  "
          f"{'PASS' if p1 else 'FAIL'}" + (f"   -> {got[0]}/{got[1]}" if got else ""))
    print(f"  ② g=0       a bare {{'rate': 0.403}} with no counts is UNAUDITABLE: {p2}  "
          f"{'PASS' if p2 else 'FAIL'}")
    print("    Arm ② exists because a detector that calls everything auditable passes ① by luck.")
    return p1 and p2


def main() -> int:
    if not controls():
        print("\n  UNVERIFIED: the detector failed its own controls. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED"}, open(OUT / "share_auditability.json", "w"), indent=2)
        return 2

    rows, bad_json = [], 0
    for f in sorted(ROOT.glob("E0*/A*/R*/results/*.json")):
        try:
            obj = json.loads(f.read_text())
        except Exception:
            bad_json += 1; continue
        ints = ints_in(obj)
        for path, v in walk(obj):
            if not isinstance(v, float) or isinstance(v, bool):
                continue
            leaf = path.split(".")[-1].split("[")[0]
            if not SHARE_KEY.search(leaf) or not (0.0 <= v <= 1.0):
                continue
            hit = auditable(v, ints)
            rows.append({"file": str(f.relative_to(ROOT)), "key": path, "share": v,
                         "auditable": hit is not None,
                         "recomputed_as": (f"{hit[0]}/{hit[1]}" if hit else None)})
    if not rows:
        print("\n  OBSERVED NOTHING: no share-like float found in any artifact. This design cannot")
        print("  see the population it is about. Exit 2, never 0.")
        return 2

    ok = [r for r in rows if r["auditable"]]
    no = [r for r in rows if not r["auditable"]]
    k3 = bool(ok) and bool(no)
    print(f"\n  ③ population contains BOTH classes (a sweep finding one cannot discriminate): "
          f"{k3}  {'PASS' if k3 else 'FAIL'}")
    if not k3:
        print("\n  UNVERIFIED: only one class present. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "n": len(rows)},
                  open(OUT / "share_auditability.json", "w"), indent=2)
        return 2

    N = len(rows)
    share_ok = len(ok) / N
    files = {r["file"] for r in rows}
    print(f"\n  {N} published share(s) across {len(files)} artifact(s)"
          + (f" · {bad_json} unreadable JSON (UNEXAMINED, not clean)" if bad_json else ""))
    print(f"    AUDITABLE   {len(ok):>4}  {share_ok:>7.3f}   (n/d recomputable from the same file)")
    print(f"    UNAUDITABLE {len(no):>4}  {1-share_ok:>7.3f}")
    print(f"\n  a few UNAUDITABLE shares — the denominator is not in the file at all:")
    for r in no[:6]:
        print(f"    {r['file'].split('/')[-3][:42]:<42} {r['key'][:34]:<34} {r['share']:.4f}")

    world = "A" if share_ok >= 1 - share_ok else "B"
    print(f"\n  ⭐ WORLD {world}: " + {
        "A": "most published shares are auditable — the three wrong-denominator instances were"
             " sloppiness rather than a habit, and per-case fixes are the right response",
        "B": "most published shares are NOT auditable — the corpus publishes rates whose"
             " denominators are unrecoverable from their own artifacts, and no amount of per-case"
             " fixing reaches them"}[world])
    print(f"     ⚠ AUDITABLE means CHECKABLE, never CORRECT. Whether a recorded `d` is the RIGHT")
    print(f"       denominator is a judgement per claim; this measures only whether the claim can")
    print(f"       be checked at all — the necessary condition all three instances failed.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "n_shares": N, "n_files": len(files),
               "n_auditable": len(ok), "n_unauditable": len(no),
               "auditable_share": share_ok, "unreadable_json": bad_json,
               "means": "AUDITABLE = recomputable from integers in the same artifact; it does NOT "
                        "mean the denominator is the right one",
               "rows": rows[:1500]},
              open(OUT / "share_auditability.json", "w"), indent=2)
    print(f"\n  artifact: results/share_auditability.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
