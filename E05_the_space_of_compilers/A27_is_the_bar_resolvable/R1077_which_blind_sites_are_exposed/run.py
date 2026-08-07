"""R1077 — 34 precision-blind sites is not 34 defects. Which of them can actually meet a prose value?

R1076 counted 38 value-membership implementations, 34 comparing floats exactly, and shipped
`assurance/valuematch.py` so the fix has one home. But R1076 said plainly what it could not: **a
precision-blind test is not thereby wrong.** Exactness is correct when both sides come from the same
computation, and fails only when one side is a value that was DISPLAYED before it was compared.

⭐ SO THE RISK SET IS SMALLER THAN THE COUNT, AND THE SEPARATOR IS CHEAP: a round whose source never
   reads prose — no `.md`, no regex over document text — cannot put a displayed value on either side
   of its comparison. That is the sound direction; the converse is not, because a round may read
   prose for entirely unrelated reasons.

⛔ P6, WRITTEN BEFORE THE RUN.
   PROPERTY    the exact comparison can meet a value that was displayed before being compared
   PROXY       the round's source reads prose (a `.md` file, or a regex over document text)
   IMPLICATION reads no prose ==> cannot be exposed                        [SOUND]
               reads prose   ==> is exposed                                [NOT SOUND: the prose may
                                 be read for titles, sections, or anything else]
   SAFE SIDE   rule only on `cannot be exposed`. Prose-reading returns AT-RISK, never CONFIRMED.

ESTIMAND        of R1076's precision-blind sites, how many sit in rounds that read prose at all
IDENTIFICATION  exact for the proxy. ⚠ AT-RISK is an UPPER bound on exposure by construction, and
                the round says so rather than reporting it as a defect count.
SCOPE           population : R1076's 34 exact-comparison sites
                instrument : does the containing source read `.md` or regex over document text
                baseline   : R1076's count of 34
                regime     : this checkout
WORLDS          A THE RISK IS CONCENTRATED — few sites sit in prose-reading rounds, so the 34 is
                  mostly harmless and the real exposure is a short, nameable list.
                B THE RISK IS WIDESPREAD — most do, so the exact comparison is genuinely dangerous
                  across the arc and `valuematch` needs adopting rather than merely existing.
                prediction matrix: A -> at-risk share low;  B -> high
KILL            pre-registered and CONDITIONAL:
                  if the controls fire:
                      at-risk share <= 0.30 -> World A, name the exposed sites
                      >= 0.60               -> World B
                      otherwise              -> report, claim neither
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   ⭐ R1070 — the round whose exact test caused R1075's retraction by comparing against a
                value read from the statement — MUST classify AT-RISK. A separator that misses the
                one confirmed case cannot triage the rest.
NEGATIVE CTRL   a round that provably reads no prose must classify NOT-EXPOSED; R923, which reads
                only `.npz` and prior artifacts, is the check.
PLACEBO         a site whose file cannot be read contributes UNKNOWN, never NOT-EXPOSED.
NOISE FLOOR     N/A - this is a property of committed source. Stated, not omitted.
MULTIPLICITY    every site reported with its verdict, not only the exposed ones.
SEEDS           N/A.
IMPOSSIBLE      whether an AT-RISK site actually compares a displayed value. That needs the dataflow,
                not the file list. SETTLES: IN-RELEASE by reading each at-risk site, which is the
                point of narrowing 34 to that list.
"""
import ast, json, pathlib, re

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
# ⛔⛔ THE FIRST PROXY MATCHED MENTIONS, NOT READS, AND ITS OWN NEGATIVE CONTROL CAUGHT IT. Every
#   round's docstring discusses `DEFINITION` and READMEs, so a bare word search classifies the whole
#   arc as prose-reading. §4's `a grep is a measuring instrument` row. The fix is not a tighter word
#   list: it is to STRIP comments and docstrings first, then look only for an actual `.md` file
#   operation in executable code.
PROSE = (re.compile(r"""\.md['"]"""), re.compile(r"""\bDEF\.read_text\("""),
         re.compile(r"""glob\([^)]*\.md"""))


def code_only(txt):
    """executable source with comments and docstrings removed — a mention is not a read"""
    try:
        tree = ast.parse(txt)
    except Exception:
        return txt
    doc_spans = []
    for nd in ast.walk(tree):
        if isinstance(nd, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            b = getattr(nd, "body", [])
            if b and isinstance(b[0], ast.Expr) and isinstance(b[0].value, ast.Constant) \
                    and isinstance(b[0].value.value, str):
                doc_spans.append((b[0].lineno, b[0].end_lineno))
    keep = []
    for i, line in enumerate(txt.splitlines(), 1):
        if any(a <= i <= b for a, b in doc_spans):
            continue
        keep.append(line.split("#", 1)[0])
    return "\n".join(keep)


def main() -> int:
    src = next(ROOT.glob("E05_the_space_of_compilers/A27*/R1076_*/results/"
                         "membership_tests.json"), None)
    if src is None:
        print("  UNRUNNABLE: R1076's artifact is missing. Exit 2, never 0."); return 2
    rows = [r for r in json.loads(src.read_text())["rows"] if r["kind"] == "exact"]
    if not rows:
        print("  UNRUNNABLE: no precision-blind site. Exit 2, never 0."); return 2

    cache = {}

    def reads_prose(rel):
        if rel in cache:
            return cache[rel]
        p = ROOT / rel
        try:
            txt = p.read_text()
        except Exception:
            cache[rel] = None; return None
        hit = any(rx.search(code_only(txt)) for rx in PROSE)
        cache[rel] = hit
        return hit

    # ---------- controls ----------
    r1070 = next((str(p.relative_to(ROOT)) for p in
                  ROOT.glob("E05_the_space_of_compilers/A27*/R1070_*/run.py")), None)
    r923 = next((str(p.relative_to(ROOT)) for p in
                 ROOT.glob("E05_the_space_of_compilers/A*/R923_*/run.py")), None)
    pos = r1070 is not None and reads_prose(r1070) is True
    neg = r923 is not None and reads_prose(r923) is False
    print(f"  POSITIVE — R1070, the round whose exact test caused R1075's retraction, must read "
          f"prose: {pos}")
    print(f"  NEGATIVE — R923, which reads only .npz and prior artifacts, must not: {neg}")
    if not (pos and neg):
        print("  the separator cannot be read either way. Exit 2, never 0."); return 2

    out = []
    for r in rows:
        v = reads_prose(r["file"])
        out.append({**r, "verdict": "UNKNOWN" if v is None else
                    ("AT-RISK" if v else "NOT-EXPOSED")})
    at = [o for o in out if o["verdict"] == "AT-RISK"]
    safe = [o for o in out if o["verdict"] == "NOT-EXPOSED"]
    unk = [o for o in out if o["verdict"] == "UNKNOWN"]
    share = len(at) / len(out)
    print(f"\n  ⭐ precision-blind sites {len(out)} · AT-RISK {len(at)} · NOT-EXPOSED {len(safe)} · "
          f"UNKNOWN {len(unk)} · at-risk share {share:.3f}")
    for o in at[:10]:
        print(f"     AT-RISK  {o['name']:<16} {o['file']}")

    print()
    if share <= 0.30:
        world = (f"⭐ A THE RISK IS CONCENTRATED — {len(at)} of {len(out)} ({share:.3f}) "
                 f"precision-blind sites sit in rounds that read prose at all. The other "
                 f"{len(safe)} compare values that never left a computation, where exactness is "
                 f"correct. **34 blind sites is not 34 defects**, and the list to read is short.")
    elif share >= 0.60:
        world = (f"⛔ B THE RISK IS WIDESPREAD — {len(at)} of {len(out)} ({share:.3f}) sit in "
                 f"prose-reading rounds, so the exact comparison is genuinely dangerous across this "
                 f"arc and `valuematch` needs ADOPTING rather than merely existing.")
    else:
        world = (f"⭐ NEITHER BAND — at-risk {share:.3f} ({len(at)} of {len(out)}). Reported; the "
                 f"actionable set is the {len(at)} named above.")
    print(world)
    print(f"⛔ AND AT-RISK IS AN UPPER BOUND BY CONSTRUCTION. A round may read prose for titles or")
    print(f"   sections and never compare a displayed value. The sound direction is the other one:")
    print(f"   {len(safe)} sites CANNOT be exposed, and that is the claim this round actually makes.")

    o_ = HERE / "results" / "exposed_sites.json"
    o_.write_text(json.dumps({
        "round": "R1077", "sites": len(out), "at_risk": len(at), "not_exposed": len(safe),
        "unknown": len(unk), "at_risk_share": share, "rows": out, "world": world,
        "proxy_ledger": {"property": "the exact comparison can meet a displayed value",
                         "proxy": "the round's source reads prose",
                         "sound": "reads no prose => cannot be exposed",
                         "unsound": "reads prose => is exposed",
                         "safe_side": "prose-reading returns AT-RISK, never CONFIRMED"},
        "controls": {"positive_R1070_at_risk": bool(pos), "negative_R923_safe": bool(neg)},
        "limitation": "AT-RISK is an upper bound; the sound claim is which sites cannot be exposed",
    }, indent=2) + "\n")
    print(f"\nartifact {o_.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
