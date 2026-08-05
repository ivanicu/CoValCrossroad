r"""A name asserting a property of the RELEASE must resolve to ONE set, corpus-wide.

⛔ THE DEFECT THIS EXISTS FOR (R689, R690, R691).
   `PUBLISHED_FIVE` was bound in R360 to {coval_core, topw_k3, topw_k4, topw_k6, topw_k8} and in
   R442 to {coval_core, topabs_k4, topvar_k4, topw_k4, topwvar_k4} -- 12.8 HOURS apart, same author,
   no retraction in the ledger at the time. Four of five members in each were never named by
   `data/DATASET_CARD.md`; the release ships ONE core. The mislabel propagated through five rounds
   and is the mechanism behind R676's "the number five is stable, the membership is not".

⚠ WHY NOT A GATE ON THE RETRACTION LEDGER. R691 measured it: no retraction existed when the second
   binding was written, so a ledger gate would have had nothing to warn against. The enforceable
   invariant is NAMING, not history.

THE RULE, and it is deliberately narrow:
   a literal whose NAME asserts a release property (PUBLISH/RELEASE/COVAL/PAPER/OFFICIAL/SHIPPED/
   CARD) must (a) resolve to the same member set everywhere it is bound, and (b) contain only
   members the release's own documentation names.

⚠ WHAT IT CANNOT DO: a release claim under a NEUTRAL name (`FIVE`, `TARGET`) is invisible to it, so
   passing is a floor and never a certificate. Stated here rather than discovered later.
"""
from __future__ import annotations
import ast, json, pathlib, re, sys
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
CARD = ROOT / "data" / "DATASET_CARD.md"
RELEASEY = re.compile(r"(PUBLISH|RELEASE|COVAL|PAPER|OFFICIAL|SHIPPED|CARD)", re.I)
FREEZE = pathlib.Path(__file__).resolve().parent / "KNOWN_RELEASE_NAME_COLLISIONS.json"
SELF = re.compile(r"R689|R690|R691")          # rounds that DOCUMENT the defect


def named_sets(src):
    try: tree = ast.parse(src)
    except SyntaxError: return []
    out = []
    for n in ast.walk(tree):
        if not isinstance(n, ast.Assign) or not isinstance(n.value, (ast.List, ast.Set, ast.Tuple)):
            continue
        ms = [e.value for e in n.value.elts
              if isinstance(e, ast.Constant) and isinstance(e.value, str)]
        if ms:
            out += [{"name": t.id, "members": ms} for t in n.targets if isinstance(t, ast.Name)]
    return out


def main() -> int:
    if not CARD.is_file():
        print("  UNRUNNABLE: data/DATASET_CARD.md absent -- cannot check membership. Exit 2.")
        return 2
    card = CARD.read_text(errors="ignore")

    # POSITIVE CONTROL: the rule must be able to FIRE. A synthetic collision must be detected.
    probe = defaultdict(set)
    probe["X_PUBLISHED"].update({("a", "b"), ("a", "c")})
    fires = sum(1 for v in probe.values() if len(v) > 1) == 1
    print(f"  POSITIVE CONTROL  a synthetic collision is detected: {fires}")
    if not fires:
        print("  the rule cannot fire -- a pass would be silence. Exit 2."); return 2

    byname, files = defaultdict(set), defaultdict(set)
    scanned = 0
    for f in sorted(ROOT.rglob("run.py")):
        s = str(f)
        if "/_archive/" in s or SELF.search(s): continue
        scanned += 1
        for d in named_sets(f.read_text(errors="ignore")):
            if RELEASEY.search(d["name"]):
                byname[d["name"]].add(tuple(sorted(d["members"])))
                files[d["name"]].add(str(f.relative_to(ROOT)))

    if scanned == 0:
        print("  UNRUNNABLE: 0 files scanned -- an empty population never passes. Exit 2."); return 2

    known = set(json.loads(FREEZE.read_text())["names"]) if FREEZE.exists() else set()
    collisions = {k: v for k, v in byname.items() if len(v) > 1}
    unnamed = {k: [m for v in vs for m in v if m not in card]
               for k, vs in byname.items()}
    unnamed = {k: sorted(set(v)) for k, v in unnamed.items() if v}

    print(f"  scanned {scanned} run.py   release-asserting names: {len(byname)}")
    new_col = {k: v for k, v in collisions.items() if k not in known}
    new_unn = {k: v for k, v in unnamed.items() if k not in known}
    for k, vs in collisions.items():
        print(f"    {k}: {len(vs)} distinct sets  {'(known)' if k in known else 'NEW'}")
    for k, v in unnamed.items():
        print(f"    {k}: {len(v)} member(s) the card never names  {'(known)' if k in known else 'NEW'}")

    if new_col or new_unn:
        print(f"\n  NEW -- a release-asserting name that does not resolve to one carded set:")
        for k in sorted(set(new_col) | set(new_unn)):
            print(f"    {k}  in {sorted(files[k])}")
        print(f"  Either rename it (it is a claim about OUR arms), or fix its members.")
        return 1
    print(f"  PASS -- every release-asserting name resolves to one set the card names.")
    print(f"  (floor, not certificate: a release claim under a neutral name is invisible here.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
