"""R1052 — 13 artifacts carry a provenance stamp. Has any of them ever been checked against history?

R1051 established that all 16 flagged rounds re-derive their committed values, and counted 13
artifacts carrying a `commit`/`head` stamp and 3 carrying none. R1051's NEXT proposed tracing the 3
unstamped ones through git.

⛔ THAT NEXT IS ANSWERING THE WEAKER QUESTION. Re-derivation ALREADY established provenance for all
   16, including the unstamped 3, and re-derivation is strictly stronger than a stamp: it shows the
   code produces the file, where a stamp only asserts which commit was checked out. So the live
   question is not "can the 3 be traced" but **"is the stamp on the other 13 worth anything?"**

⭐ AND IT HAS A FALSIFIABLE PREDICTION. The stamp records HEAD at RUN time; the artifact is committed
   AFTER that run. So for every honestly-stamped artifact the stamped hash must be an ANCESTOR of the
   commit that introduced the file. If it is not — if the stamp names a commit unrelated to where the
   file landed — the stamp is decorative, and 13 artifacts carry an unverified claim about themselves.

ESTIMAND        of the stamped artifacts, the share whose stamped hash is an ancestor of the commit
                that introduced that artifact file
IDENTIFICATION  exact. Both are git facts. ⚠ One legitimate exception is named BEFORE the run: an
                artifact re-run and amended into the SAME commit would stamp that commit's PARENT,
                which is still an ancestor — so the prediction survives amendment. An artifact
                stamped with a hash from a DIFFERENT branch would not be an ancestor and is the
                failure this looks for.
SCOPE           population : the stamped artifacts among R1050's flagged rounds
                instrument : git merge-base --is-ancestor
                baseline   : R1051's census, 13 stamped of 16
                regime     : this repository, this history
WORLDS          A THE STAMP IS SOUND — every stamped hash is an ancestor of its artifact's
                  introducing commit. The stamp is verifiable, and the reason it has never caught
                  anything is that nothing was wrong, not that it cannot see.
                B THE STAMP IS DECORATIVE — some stamped hash is not an ancestor. Then the field
                  asserts a provenance it does not have, on artifacts the definition cites, and it
                  has never been checked because nothing in this repository checks it.
                prediction matrix: A -> non-ancestor count 0   B -> > 0
KILL            pre-registered and CONDITIONAL:
                  if the controls fire:
                      any stamped hash NOT an ancestor of its introducing commit -> World B
                      none                                                       -> World A
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   the ancestry test must return FALSE for a hash known not to be an ancestor — the
                CURRENT HEAD is not an ancestor of any past introducing commit. A test never shown to
                return False is silence.
NEGATIVE CTRL   the introducing commit must be an ancestor of ITSELF (git treats this as true), and
                the repository root commit must be an ancestor of HEAD.
PLACEBO         an artifact with no stamp contributes no denominator - reported, never scored.
NOISE FLOOR     ⭐ the share of RANDOM commits from this history that pass the ancestry test is
                measured. If most commits are ancestors of the introducing commit, passing carries no
                information and the verdict is UNVERIFIED regardless.
MULTIPLICITY    every stamped artifact reported with its verdict, not only failures.
SEEDS           3 for the random-commit floor; spread reported.
IMPOSSIBLE      whether the stamped commit is the one the code ACTUALLY ran under, as opposed to
                merely an ancestor. Ancestry is necessary, not sufficient.
                SETTLES: OUT-OF-RELEASE - it would need a record of the run, which is the very thing
                the stamp was supposed to be.
"""
import json, pathlib, random, re, subprocess

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
STAMPS = ("commit", "head")


def git(*a):
    r = subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def is_ancestor(a, b):
    return subprocess.run(["git", "merge-base", "--is-ancestor", a, b],
                          cwd=ROOT, capture_output=True).returncode == 0


def main() -> int:
    src = next(ROOT.glob("E05_the_space_of_compilers/A27*/R1051_*/results/reran_the_flagged.json"))
    census = json.loads(src.read_text())["stamp_census"]
    stamped, unstamped = census["stamped"], census["unstamped"]
    if not stamped:
        print("  UNRUNNABLE: no stamped artifact. Exit 2, never 0."); return 2

    rows = []
    for rid in stamped:
        ds = [p for p in ROOT.glob(f"E05_the_space_of_compilers/A*/{rid}_*") if p.is_dir()]
        arts = sorted((ds[0] / "results").glob("*.json")) if ds else []
        if not arts:
            rows.append({"round": rid, "status": "NO_ARTIFACT"}); continue
        rel = str(arts[0].relative_to(ROOT))
        intro = git("log", "--diff-filter=A", "--format=%H", "--", rel)
        intro = intro.split("\n")[-1] if intro else None
        try:
            top = json.loads(arts[0].read_text())
        except Exception:
            rows.append({"round": rid, "status": "UNPARSEABLE"}); continue
        # ⛔⛔ R1051's CENSUS MATCHED THE KEY NAME AND NOT THE VALUE TYPE, AND THAT IS THE ROUND'S
        #   FIRST FINDING. Four artifacts have a `head` field holding a TITLE STRING — "the four
        #   cla...", "does the ext..." — which R1051 counted as a provenance stamp. A git hash is
        #   40 hex characters; a headline is not. The instrument's unit was `a key called
        #   commit/head`; the claim's unit is `a git hash`. Same mismatch as the five before it.
        val = next((top[k] for k in STAMPS if k in top), None)
        if not (isinstance(val, str) and re.fullmatch(r"[0-9a-f]{7,40}", val.strip())):
            rows.append({"round": rid, "status": "NOT_A_HASH", "intro": intro,
                         "field": (val or "")[:28]}); continue
        val = val.strip()
        if not intro:
            rows.append({"round": rid, "status": "NO_INTRO", "stamp": val[:12]}); continue
        exists = git("cat-file", "-t", val) == "commit"
        rows.append({"round": rid, "status": "CHECKED", "intro": intro[:12], "stamp": val[:12],
                     "stamp_exists": exists,
                     "ancestor_of_intro": is_ancestor(val, intro) if exists else False})

    checked = [r for r in rows if r["status"] == "CHECKED"]
    if not checked:
        print("  UNRUNNABLE: no stamped artifact could be checked. Exit 2, never 0."); return 2

    head = git("rev-parse", "HEAD")
    ex = checked[0]["intro"]
    pos = not is_ancestor(head, ex)
    neg = is_ancestor(ex, ex) and is_ancestor(git("rev-list", "--max-parents=0", "HEAD").split("\n")[0], head)
    print(f"  POSITIVE — the ancestry test must return FALSE for the CURRENT HEAD vs a past "
          f"introducing commit: {pos}")
    print(f"  NEGATIVE — a commit is an ancestor of itself, and the root is an ancestor of HEAD: {neg}")
    if not (pos and neg):
        print("  the ancestry test does not discriminate. Exit 2, never 0."); return 2

    allc = git("rev-list", "HEAD").split("\n")
    floors = []
    for seed in (7, 19, 37):
        rng = random.Random(seed)
        hits = 0
        for r in checked:
            c = rng.choice(allc)
            hits += is_ancestor(c, r["intro"])
        floors.append(hits / len(checked))
    flo, fhi = min(floors), max(floors)

    bad = [r["round"] for r in checked if not r["ancestor_of_intro"]]
    missing = [r["round"] for r in checked if not r["stamp_exists"]]
    nothash = [r["round"] for r in rows if r["status"] == "NOT_A_HASH"]
    print(f"\n  ⛔⛔ R1051's CENSUS IS RETRACTED HERE. Artifacts whose `commit`/`head` field is NOT")
    print(f"     a git hash but a TITLE STRING: {len(nothash)} {nothash}")
    print(f"     ⭐ so the true provenance-stamp count is {len(checked)}, not {len(stamped)}, and the")
    print(f"     rounds carrying no usable stamp number {len(unstamped) + len(nothash)}, not "
          f"{len(unstamped)}.")
    bm = json.loads(src.read_text())["stamp_census"]["byte_mismatch"]
    print(f"     ⭐⭐ AND THE TRUE-STAMP SET IS EXACTLY THE BYTE-MISMATCH SET: "
          f"{sorted(r['round'] for r in checked) == sorted(bm)} — which is the mechanism R1051")
    print(f"     scoped to 9 without being able to say why. A stamp that tracks HEAD changes on")
    print(f"     every re-run; a title does not.")
    obs = 1 - len(bad) / len(checked)
    print(f"\n  ⭐ stamped {len(stamped)} · unstamped (no denominator) {len(unstamped)} · "
          f"checked {len(checked)} · stamp names a commit that does not exist {len(missing)}")
    print(f"  ⭐ ancestor of its own introducing commit: {len(checked) - len(bad)} of {len(checked)} "
          f"= {obs:.3f}")
    print(f"  ⭐ MEASURED FLOOR — a RANDOM commit from this history passes the same test at "
          f"[{flo:.3f}, {fhi:.3f}] over 3 seeds")
    for r in checked[:6]:
        print(f"     {r['round']:>6} stamp {r['stamp']} intro {r['intro']} "
              f"exists={r['stamp_exists']} ancestor={r['ancestor_of_intro']}")

    informative = obs > fhi
    print()
    if not informative:
        world = (f"⛔ UNVERIFIED — the observed pass rate {obs:.3f} is not above the random-commit "
                 f"floor [{flo:.3f}, {fhi:.3f}]. Most commits in this history are ancestors of the "
                 f"introducing commit, so passing the ancestry test carries no information about the "
                 f"stamp and neither world is separable by this design.")
    elif bad:
        world = (f"⭐ B THE STAMP IS DECORATIVE FOR {len(bad)} ARTIFACT(S) — {bad} carry a hash that "
                 f"is NOT an ancestor of the commit that introduced them, so the field asserts a "
                 f"provenance it does not have, on artifacts this definition cites.")
    else:
        world = (f"⭐ A THE STAMP IS SOUND AND HAS NOW BEEN CHECKED — all {len(checked)} stamped "
                 f"hashes are ancestors of their own introducing commit, at {obs:.3f} against a "
                 f"random-commit floor of [{flo:.3f}, {fhi:.3f}]. ⚠ AND THE REASON THIS IS WORTH "
                 f"RECORDING IS NOT THE PASS: nothing in this repository had ever run this check, so "
                 f"until now the field was an unverified claim that 13 artifacts made about "
                 f"themselves. A stamp nobody verifies is a comment.")
    print(world)
    print(f"⛔ AND ANCESTRY IS NECESSARY, NEVER SUFFICIENT. It cannot show the stamped commit is the")
    print(f"   one the code actually ran under — only that it precedes where the file landed. The")
    print(f"   sufficient evidence is RE-DERIVATION, which R1051 already has for all 16, and which is")
    print(f"   why the 3 unstamped artifacts are no worse off than the 13 stamped ones.")

    # ⛔⛔ FINDING 3, FOUND WHILE COMMITTING THIS ROUND AND RETRACTING R1049's COUNT. This round's
    #   own fact registered GREEN with nothing written, and only ONE of its two patterns matched
    #   anything. Reading the gate's source settles why: `ok = any(re.search(p, region) for p in
    #   pats)`. It passes on ANY pattern. R1049's multi-home predicate was `all(homes >= 2)` —
    #   modelled from memory rather than read — so it required EVERY pattern to have a second home.
    #   Under `any()` semantics one loose pattern is enough to carry the pass, so the correct
    #   predicate is `any(homes >= 2)` and R1049's 16 is an UNDERCOUNT.
    import ast as _ast
    reg = (ROOT / "assurance/a_statement_is_current_with_the_arc.py").read_text()
    doc = (ROOT / "E05_the_space_of_compilers/DEFINITION.md").read_text()

    def _homes(pat, text, cap=8):
        n, cur = 0, text
        for _ in range(cap):
            m = re.search(pat, cur, re.I | re.S)
            if not m:
                break
            n += 1
            cur = cur[:m.start()] + cur[m.end():]
        return n

    facts_p, unreadable = [], 0
    for nd in _ast.walk(_ast.parse(reg)):
        if not (isinstance(nd, _ast.Call) and isinstance(nd.func, _ast.Attribute)
                and nd.func.attr == "append" and nd.args
                and isinstance(nd.args[0], _ast.Tuple)):
            continue
        el = nd.args[0].elts
        if len(el) < 4 or not isinstance(el[0], _ast.Constant):
            continue
        if not isinstance(el[3], _ast.List):
            unreadable += 1; continue
        ps = [x.value for x in el[3].elts if isinstance(x, _ast.Constant)]
        if len(ps) != len(el[3].elts):
            unreadable += 1; continue
        facts_p.append((el[0].value, ps))
    h = {rid: [_homes(x, doc) for x in ps] for rid, ps in facts_p}
    all_pred = [r for r, v in h.items() if v and all(x >= 2 for x in v)]
    any_pred = [r for r, v in h.items() if v and any(x >= 2 for x in v)]
    print(f"\n  ⛔⛔ FINDING 3 — R1049's COUNT IS RETRACTED. The gate is `ok = any(...)`, so ONE")
    print(f"     loose pattern carries the pass. R1049 used `all(homes >= 2)`; the correct predicate")
    print(f"     is `any(homes >= 2)`.")
    print(f"     unattributable under `all`  (R1049's number): {len(all_pred)} of {len(facts_p)}")
    print(f"     unattributable under `any`  (corrected)     : {len(any_pred)} of {len(facts_p)}")
    print(f"     newly flagged: {sorted(set(any_pred) - set(all_pred))[:12]}")
    print(f"     ⚠ patterns not statically readable, reported not dropped: {unreadable}")

    out = HERE / "results" / "stamp_vs_history.json"
    out.write_text(json.dumps({
        "round": "R1052", "stamped": len(stamped), "unstamped": len(unstamped),
        "checked": len(checked), "not_ancestor": bad, "stamp_missing_from_history": missing,
        "pass_rate": obs, "random_commit_floor_3_seeds": [flo, fhi], "informative": bool(informative),
        "controls": {"positive_head_not_ancestor": bool(pos), "negative_self_and_root": bool(neg)},
        "R1049_recount": {"gate_rule": "any", "all_predicate": len(all_pred),
                          "any_predicate": len(any_pred), "population": len(facts_p),
                          "newly_flagged": sorted(set(any_pred) - set(all_pred)),
                          "unreadable": unreadable},
        "detail": rows, "world": world,
        "limitation": "ancestry is necessary, not sufficient; re-derivation is the sufficient test "
                      "and R1051 already has it for all 16",
    }, indent=2) + "\n")
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
