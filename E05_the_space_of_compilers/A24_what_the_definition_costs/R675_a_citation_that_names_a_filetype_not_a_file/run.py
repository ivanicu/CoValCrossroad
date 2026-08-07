#!/usr/bin/env python3
"""
R675 -- a citation that names a FILE TYPE, not a file. And what that did to the 47.5%.

CHECK #276 ON R674's NEXT LINE -- ITS POPULATION IS EMPTY.
  R674's NEXT proposed splitting the 27 UNRESOLVABLE pairs into "never existed" vs "renamed since".
  Measured: 27 of 27 are neither. Every one is a bare basename matching 630 files in the tree --
  `run.py`, `README.md` -- so the resolver could not choose and dropped the pair. Zero missing, zero
  renamed. ⭐ AND I HAD WRITTEN LEDGER 748 IN THE SAME COMMIT: "a bucket named for what it lacks
  hides how many distinct causes are in it." I stated the law and undercounted the causes in the same
  breath, in the sentence the next round was meant to act on.

ESTIMAND        A: of the 27 under-specified pairs, the share that resolve when the path is read
                   relative to the CITING ARTIFACT's directory rather than the repository root.
                B: the headline verification rate once those pairs are admitted (R674: 47.5%).
IDENTIFICATION  A is exact for README-sourced pairs, which have a directory. A commit body has NO
                directory, so commit-sourced pairs are STRUCTURALLY unresolvable and are reported as
                a bound, never imputed.
SCOPE           population : the 27 under-specified (path, number) pairs; then all 107
                instrument : contextual path resolution + literal file read at HEAD
                             instrument unit = A (path, number) PAIR = claim unit. EQUAL.
                baseline   : R674's root-relative resolver, and a random-artifact floor
                regime     : files at HEAD
WORLDS          A CONTEXTUAL: the citations are fine and my resolver was wrong.
                B UNDER-SPECIFIED: the citations genuinely do not identify a file, and no resolver
                  can fix them -- the defect is in the writing.
KILL            pre-registered: fewer than 10 of 27 resolving contextually kills world A and
                estimand B is not computed.
POSITIVE CTRL   a pair citing its own round's file resolves to THAT file; fails at g=0 against a
                directory lacking it.
NEGATIVE CTRL   a bare basename from a commit body stays UNRESOLVABLE.
PLACEBO         a basename no file carries stays UNRESOLVABLE.
ARTIFACT        results/contextual_resolution.json
IMPOSSIBLE      a commit body carries no directory; resolving its bare basenames would require the
                round the commit touched, which is an inference, not a citation. Bounded, not imputed.
"""
from __future__ import annotations
import importlib.util, json, pathlib, random, re, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
spec = importlib.util.spec_from_file_location(
    "gate", ROOT / "assurance" / "next_line_quantifiers_are_computed.py")
gate = importlib.util.module_from_spec(spec); spec.loader.exec_module(gate)

PATH = re.compile(r"\b((?:[\w./-]+/)?[\w.-]+\.(?:json|py|md|csv|txt))\b")
NUM = re.compile(r"(?<![\w.])(\d[\d,]{0,9}(?:\.\d+)?)(?![\w.])")
SEED = 20260805


def pairs_from(text, src, ctx):
    out = []
    for pm in PATH.finditer(text):
        w = text[max(0, pm.start() - 240): pm.end() + 240]
        for nm in NUM.finditer(w):
            n = nm.group(1).replace(",", "")
            if len(n) >= 2 and n not in pm.group(1):
                out.append({"src": src, "path": pm.group(1), "num": n, "ctx": ctx})
    return out


def resolve_root(p):
    c = ROOT / p
    if c.is_file(): return c
    h = [f for f in ROOT.rglob(pathlib.Path(p).name) if "/_archive/" not in str(f)]
    return h[0] if len(h) == 1 else None


def resolve_ctx(p, ctx):
    """⭐ THE REPAIR: a round's README saying `run.py` means THAT round's run.py."""
    if ctx is None: return None
    c = pathlib.Path(ctx) / p
    return c if c.is_file() else None


def occurs(f, n):
    try: t = f.read_text(errors="ignore")
    except Exception: return False
    return bool(re.search(rf"(?<![\w.]){re.escape(n)}(?![\w.])", t))


def main() -> int:
    rng = random.Random(SEED)
    P = []
    for s in subprocess.run(["git", "log", "--format=%H"], cwd=ROOT,
                            capture_output=True, text=True).stdout.split():
        b = subprocess.run(["git", "log", "-1", "--format=%B", s], cwd=ROOT,
                           capture_output=True, text=True).stdout
        ms = list(re.finditer(r"^NEXT:\s*(.*?)(?:\n\n|\Z)", b, re.S | re.M))
        if ms: P += pairs_from(" ".join(ms[-1].group(1).split()), "commit", None)
    for f in sorted(ROOT.rglob("README.md")):
        if "/_archive/" in str(f): continue
        m = re.search(r"^##+\s*NEXT\b(.*?)(?=\n##\s|\Z)", f.read_text(errors="ignore"), re.M | re.S)
        if m: P += pairs_from(" ".join(m.group(1).split()), "readme", f.parent)

    under = [p for p in P if resolve_root(p["path"]) is None]

    print("─── CONTROLS ───")
    a24 = HERE.parent
    posdir = HERE
    pos = resolve_ctx("run.py", posdir)
    posok = pos is not None and pos.parent == posdir
    print(f"  POSITIVE  a pair citing its own round's file resolves to THAT file -> "
          f"{pos.parent.name if pos else None} -> {'PASS' if posok else '⛔ FAIL'}")
    g0 = resolve_ctx("run.py", a24)
    print(f"  g=0       the same control must FAIL against a directory lacking it -> {g0} -> "
          f"{'PASS — it can fail' if g0 is None else '⛔ FAIL — cannot fail'}")
    neg = resolve_ctx("run.py", None)
    print(f"  NEGATIVE  a bare basename from a commit body (no directory) stays UNRESOLVABLE -> "
          f"{neg} -> {'PASS' if neg is None else '⛔ FAIL'}")
    plc = resolve_ctx("no_such_file_anywhere.json", posdir)
    print(f"  PLACEBO   a basename no file carries stays UNRESOLVABLE -> {plc} -> "
          f"{'PASS' if plc is None else '⛔ FAIL'}")
    ctl = posok and g0 is None and neg is None and plc is None

    nr = sum(1 for p in under if p["src"] == "readme")
    nc = len(under) - nr
    rec = [p for p in under if resolve_ctx(p["path"], p["ctx"]) is not None]
    print(f"\n─── A · WHERE THE 27 ACTUALLY LIVE ───")
    print(f"  under-specified pairs      : {len(under)}")
    print(f"  ⭐ README-sourced (HAVE a directory) : {nr}")
    print(f"  ⭐ commit-sourced (have NONE)        : {nc}  <- STRUCTURALLY unresolvable, bounded not imputed")
    share = len(rec) / len(under) if under else 0.0
    print(f"  recovered by contextual resolution   : {len(rec)}  ({share:.1%})")
    print(f"  registered 85% [60,100] -> "
          f"{'INSIDE' if 0.60 <= share <= 1.0 else '⛔ OUTSIDE'}, error {share-0.85:+.1%}")
    killed = len(rec) < 10
    print(f"  pre-registered kill (<10 recovered)  -> "
          f"{'⭐ FIRES — world A dies, estimand B not computed' if killed else 'does not fire'}")

    out = {"controls_ok": ctl, "seed": SEED, "under_specified": len(under),
           "readme_sourced": nr, "commit_sourced": nc, "recovered": len(rec),
           "recovery_share": share, "kill_fired": killed,
           "registered": "A 85% [60,100]; B 50% [40,62]; kill if <10 recovered",
           "check276": ("R674's NEXT proposed splitting the 27 into 'never existed' vs 'renamed'. "
                        "All 27 are a third cause: a bare basename matching 630 files. Both proposed "
                        "causes have population zero."),
           "impossible": ("a commit body carries no directory; resolving its bare basenames needs an "
                          "inference about which round it touched, which is not a citation.")}

    if killed or not ctl:
        world = ("⭐ WORLD B — UNDER-SPECIFIED. The kill fires: only "
                 f"{len(rec)} of {len(under)} pairs recover. {nc} of the {len(under)} are cited from "
                 f"COMMIT BODIES, which carry no directory at all, so no resolver can place them — "
                 f"the defect is in the WRITING, not in my instrument. R674's 47.5% is therefore "
                 f"measured over the citations that IDENTIFY a file, and the {len(under)} that name "
                 f"a file TYPE are correctly outside it. ⚠ Estimand B is NOT computed, per the "
                 f"pre-registration.") if killed else "UNVERIFIED — a control did not fire."
        print(f"\n─── VERDICT ───\n  {world}")
    else:
        dec = ok = 0
        arts = [f for f in ROOT.rglob("*.json") if "/_archive/" not in str(f)]
        rok = rtot = 0
        for p in P:
            f = resolve_root(p["path"]) or resolve_ctx(p["path"], p["ctx"])
            if f is None: continue
            dec += 1; ok += occurs(f, p["num"])
            if arts: rok += occurs(rng.choice(arts), p["num"]); rtot += 1
        rate = ok / dec if dec else 0.0
        rnd = rok / rtot if rtot else 0.0
        print(f"\n─── B · THE HEADLINE, RE-MEASURED ───")
        print(f"  decidable pairs : {dec}  (R674: 80)")
        print(f"  ⭐ verified      : {ok}  ({rate:.1%})   R674 measured 47.5%")
        print(f"  random baseline : {rnd:.1%}   lift {rate-rnd:+.1%}")
        print(f"  registered B 50% [40,62] -> "
              f"{'INSIDE' if 0.40 <= rate <= 0.62 else '⛔ OUTSIDE'}, error {rate-0.50:+.1%}")
        print(f"  DIRECTIONAL: admitting them RAISES the rate -> "
              f"{'HOLDS' if rate > 0.475 else '⛔ FAILS — it lowered it'}")
        world = (f"A CONTEXTUAL — {share:.1%} of under-specified pairs recover, and the headline "
                 f"moves 47.5% -> {rate:.1%} against a {rnd:.1%} random floor.")
        out |= {"decidable": dec, "verified": ok, "rate": rate, "random_baseline": rnd,
                "directional_holds": rate > 0.475}
        print(f"\n─── VERDICT ───\n  {world}")

    sha = subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True).stdout.strip()
    out |= {"world": world, "tree_sha": sha}
    print(f"\n  MULTIPLICITY: {len(P)} pairs, {len(under)} under-specified, 4 controls.")
    print(f"  ⭐ tree sha: {sha[:12]}   seed: {SEED}")
    (HERE/"results").mkdir(exist_ok=True)
    (HERE/"results"/"contextual_resolution.json").write_text(json.dumps(out, indent=2))
    print(f"  wrote {HERE/'results'/'contextual_resolution.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
