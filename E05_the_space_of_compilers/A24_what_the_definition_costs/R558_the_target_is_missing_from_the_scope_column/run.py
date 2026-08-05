#!/usr/bin/env python3
"""R558 · The claim set's scope column omits the axis that empties the definition.

R288 swept six agreement TARGETS over 968 prompts and got FOUR distinct admitted sets, two of
them empty and one excluding `coval_core` itself. Every headline extension count on the statement
-- 5, 0, 0 -- is computed at the A2 target. If the scope column does not name the target, those
numbers are being read as unconditional.

ESTIMAND  of the claims in the statement's "What stands" table, how many state the TARGET in
          their scope column?
IDENT     fully identified: both are text on one page, and R288's artifact fixes which claims are
          target-dependent.
SCOPE     population = the numbered rows of the claim table · instrument = an anchored row parse ·
          baseline = every row naming its target · regime = the current STATEMENT.md.
WORLDS    A the scope column names the target -> the numbers are already conditioned and the
            register row is the only defect.
          B it does not -> the deliverable's headline counts read as unconditional while a
            documented axis on disk sends them to zero.
KILL      pre-registered: >=1 row naming a target-family token in its scope -> partial WORLD A;
          zero -> WORLD B.
POS CTRL  the parse must FIND the scope column's existing tokens (judge, prompts, arms), else a
          zero for "target" is silence rather than a measurement.
NEG CTRL  an invented scope token must appear in no row.
ARTIFACT  results/scope_gap.json
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
stmt = (ROOT / "E05_the_space_of_compilers" / "STATEMENT.md").read_text()
sweep = json.loads((ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs" /
                    "R288_does_the_partition_survive_the_target" / "results" /
                    "target_sweep.json").read_text())

# the claim table's numbered rows: | **N** | claim | scope |
rows = re.findall(r"^\|\s*\*\*(\d+)\*\*\s*\|(.+?)\|(.+?)\|\s*$", stmt, re.M)
claims = [(int(n), c.strip(), s.strip()) for n, c, s in rows if int(n) <= 10][:10]
if len(claims) < 5:
    print(f"  parsed only {len(claims)} claim rows -> UNRUNNABLE"); sys.exit(2)

TARGET_TOK = ("target", "a2·", "a2 ", "a2-", "annot", "consensus", "held-out annotator")
KNOWN_TOK  = ("judge", "prompt", "arms", "release")
FAKE_TOK   = ("zzscopetoken9q",)

def has(s, toks): return any(t in s.lower() for t in toks)

n_known = sum(has(s, KNOWN_TOK) for _n, _c, s in claims)
n_fake  = sum(has(s, FAKE_TOK) for _n, _c, s in claims)
print(f"  POSITIVE CONTROL  rows whose scope names a KNOWN axis (judge/prompts/arms): "
      f"{n_known} of {len(claims)} -> {'PASS' if n_known else 'FAIL -- parse is blind'}")
print(f"  NEGATIVE CONTROL  rows matching an invented token: {n_fake} -> "
      f"{'PASS' if n_fake == 0 else 'FAIL'}")
if not n_known or n_fake:
    sys.exit(2)

named = [n for n, _c, s in claims if has(s, TARGET_TOK)]
print(f"\n  claim rows parsed: {len(claims)}")
print(f"  rows whose SCOPE names the target: {len(named)}  {named}")

adm = sweep["admitted"]
empt = [t for t, a in adm.items() if not a]
nocore = [t for t, a in adm.items() if a and "coval_core" not in a]
print(f"\n  R288, {sweep['n_prompts']} prompts, {len(sweep['targets'])} targets -> "
      f"{len(sweep['distinct_sets'])} DISTINCT admitted sets")
print(f"    targets under which the definition is EMPTY      : {len(empt)}  {empt}")
print(f"    targets under which `coval_core` is NOT admitted : {len(nocore)}  {nocore}")

world = "A" if named else "B"
print(f"\n  WORLD {world} -- " + (
    "the scope column already conditions on the target."
    if world == "A" else
    "no claim row names the target, so every extension count on the page reads as "
    "unconditional while two of six targets send it to zero."))
(pathlib.Path(__file__).parent / "results" / "scope_gap.json").write_text(json.dumps(
    {"world": world, "n_claim_rows": len(claims), "rows_naming_target": named,
     "rows_naming_known_axis": n_known, "n_targets": len(sweep["targets"]),
     "n_distinct_admitted_sets": len(sweep["distinct_sets"]),
     "targets_empty": empt, "targets_excluding_coval_core": nocore,
     "admitted": adm}, indent=2))
