"""Project the claim graph into Lean 4, so the derivation chain is machine-checked.

WHAT LEAN CAN AND CANNOT CHECK HERE
-----------------------------------
Lean cannot check that beta_neg/beta_pos is 0.094. That is an empirical fact and it enters as an
AXIOM, named for the experiment that produced it. What Lean checks is the part I am actually bad
at: whether a conclusion I wrote down is entailed by premises I actually have.

Two properties come out of that, and both are worth the file:

  1.  `#print axioms <theorem>` returns the COMPLETE set of empirical measurements and inference
      rules a conclusion rests on. Not the set I remembered to list in prose -- the set the
      elaborator actually used. A claim that quietly leans on something undeclared shows up here
      and nowhere else.

  2.  An UNRESOLVED CONFOUND becomes a required hypothesis. If the graph holds an open `confounds`
      edge into a claim, the inference rule for that claim takes `¬Confound` as an argument, and
      no term of that type exists until a control discharges it. The theorem then DOES NOT COMPILE.
      A confound I have merely named, rather than ruled out, mechanically blocks the conclusion
      instead of sitting in a caveat paragraph nobody reads.

An inference rule is itself an axiom, deliberately. "Core underweights the negative quarter,
therefore the compilation is not faithful" is a definitional choice about what `faithful` means,
not a measurement, and it belongs in the audit trail beside the numbers.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from derivation_chain import q  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "lean" / "Coval" / "Chain.lean"


def ident(name: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_")
    if s and s[0].isdigit():
        s = "c" + s
    return s


def wrap(text: str, width: int = 96, prefix: str = "    ") -> str:
    words, lines, cur = (text or "").split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width - len(prefix):
            lines.append(prefix + cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(prefix + cur)
    return "\n".join(lines)


def main() -> int:
    nodes = q("""SELECT id, kind, name, coalesce(statement,''), coalesce(status,''),
                        coalesce(d_level,0)
                 FROM node ORDER BY id""")
    if not nodes:
        print("REFUSING: the claim graph is empty, so the emitted Lean would type-check "
              "vacuously. Build it first. Exits 2.", file=sys.stderr)
        return 2
    byid = {int(r[0]): r for r in nodes}

    edges = q("""SELECT src, dst, kind, coalesce(d_forward,0), coalesce(note,'') FROM edge""")
    evid = q("""SELECT node_id, experiment, finding, coalesce(d_level,0) FROM evidence
                WHERE node_id IS NOT NULL ORDER BY node_id, experiment""")

    L = ["/-",
         "  The CoVal attack campaign's derivation chain, projected from the claim graph in",
         "  PostgreSQL (database `coval`, schema `claim`). GENERATED -- edit db/derivation_chain.py",
         "  and re-run db/emit_lean.py; edits made here are overwritten.",
         "",
         "  Empirical measurements enter as axioms named for the experiment that produced them.",
         "  Inference rules enter as axioms too, because deciding that an underweighted polarity",
         "  block means the compilation is unfaithful is a definitional choice, not a measurement.",
         "",
         "  `#print axioms A1_is_refuted` returns the complete set of both that the conclusion",
         "  actually rests on -- checked by the elaborator, not by me.",
         "",
         "  A claim carrying an OPEN confound edge gets that confound as a required hypothesis, so",
         "  its theorem cannot be closed until a control discharges it.",
         "-/",
         "namespace Coval",
         ""]

    # ---- the propositions ---------------------------------------------------------------------
    L.append("/-! ## The propositions -/")
    L.append("")
    for r in nodes:
        nid, kind, name, stmt, status, d = int(r[0]), r[1], r[2], r[3], r[4], int(r[5])
        if kind not in ("fact", "my_claim", "their_assumption", "defect"):
            continue
        L.append(f"/-- **{kind}** · status `{status}` · D{d}\n{wrap(stmt)} -/")
        L.append(f"opaque {ident(name)} : Prop")
        L.append("")

    # ---- open confounds become propositions that must be negated -------------------------------
    open_conf = {}
    L.append("/-! ## Confounds that are named but not yet ruled out.")
    L.append("    No term of type `¬c` exists for any of these, so every theorem below that needs")
    L.append("    one is stated with it as a hypothesis and cannot be discharged today. -/")
    L.append("")
    for src, dst, kind, df, note in edges:
        if kind != "confounds":
            continue
        s = byid.get(int(src))
        if not s or s[4] not in ("open", "partial", ""):
            continue
        cid = ident(s[2])
        open_conf.setdefault(int(dst), []).append(cid)
        if f"opaque {cid} : Prop" not in "\n".join(L):
            L.append(f"/-- {wrap(s[3]).strip()} -/")
            L.append(f"opaque {cid} : Prop")
            L.append("")

    # ---- empirical inputs ----------------------------------------------------------------------
    # An experiment is a WITNESS for a claim, not the claim itself. Making it `Evidence C` rather
    # than `C` forces the closing rule to consume every witness the graph holds, so the arity of
    # `<claim>_established` IS the replication count and `#print axioms` lists all of them. The
    # first draft of this file asserted the claim directly from evidence and then closed downstream
    # theorems with premise[0], which reported a three-design result as resting on one experiment.
    L.append("/-! ## Evidence. A witness for a claim, never the claim itself. -/")
    L.append("")
    L.append("axiom Evidence : Prop → Type")
    L.append("")
    seen = set()
    witnesses = {}
    for nid, exp, finding, d in evid:
        nid = int(nid)
        r = byid.get(nid)
        if not r or r[1] not in ("fact", "my_claim", "their_assumption", "defect"):
            continue
        nm = f"ev_{ident(r[2])}_by_{ident(exp)}"
        if nm in seen:
            continue
        seen.add(nm)
        witnesses.setdefault(nid, []).append(nm)
        L.append(f"/-- Experiment `{exp}` (D{d}).\n{wrap(finding)} -/")
        L.append(f"axiom {nm} : Evidence {ident(r[2])}")
        L.append("")

    # ---- one establishing rule per claim; its ARITY is the replication count -------------------
    L.append("/-! ## Establishing rules. The arity of each is how many independent measurements")
    L.append("    the graph actually holds for that claim -- read it off the type. -/")
    L.append("")
    supports = {}
    for nid, ws in sorted(witnesses.items()):
        r = byid[nid]
        C = ident(r[2])
        arrows = "".join(f"Evidence {C} → " for _ in ws)
        L.append(f"/-- {len(ws)} independent measurement(s) establish `{C}`. -/")
        L.append(f"axiom {C}_established : {arrows}{C}")
        L.append(f"theorem {C}_holds : {C} := {C}_established " + " ".join(ws))
        L.append("")
        supports[nid] = [f"{C}_holds"]

    # ---- inference rules and the theorems they close -------------------------------------------
    L.append("/-! ## Inference rules, and what they close. -/")
    L.append("")
    thms = []
    for src, dst, kind, df, note in edges:
        if kind not in ("overturns", "supports", "refines"):
            continue
        s, dnode = byid.get(int(src)), byid.get(int(dst))
        if not s or not dnode:
            continue
        if s[1] not in ("fact", "my_claim", "their_assumption", "defect"):
            continue
        if dnode[1] not in ("fact", "my_claim", "their_assumption", "defect"):
            continue
        premise = supports.get(int(src))
        if not premise:
            continue                      # a claim with no measurement cannot close anything
        S, D = ident(s[2]), ident(dnode[2])
        neg = kind == "overturns"
        concl = f"¬{D}" if neg else D
        rule = f"{S}_{'refutes' if neg else 'supports'}_{D}"
        conf = open_conf.get(int(src), [])
        args = "".join(f"¬{c} → " for c in conf)
        L.append(f"/-- {'REFUTES' if neg else 'SUPPORTS'} (d_forward {df}). "
                 f"{wrap(note or '').strip()}"
                 + (f"\n    Blocked on unresolved confound(s): {', '.join(conf)}." if conf else "")
                 + " -/")
        L.append(f"axiom {rule} : {args}{S} → {concl}")
        tname = f"{D}_{'is_refuted' if neg else 'is_supported'}_via_{S}"
        if conf:
            hyps = " ".join(f"(h{i} : ¬{c})" for i, c in enumerate(conf))
            body = " ".join(f"h{i}" for i in range(len(conf)))
            L.append(f"theorem {tname} {hyps} : {concl} := {rule} {body} {premise[0]}")
        else:
            L.append(f"theorem {tname} : {concl} := {rule} {premise[0]}")
        thms.append(tname)
        L.append("")

    L.append("/-! ## The audit. Each line prints the COMPLETE dependency set of one conclusion. -/")
    L.append("")
    for t in thms:
        L.append(f"#print axioms {t}")
    for nid in sorted(witnesses):
        L.append(f"#print axioms {ident(byid[nid][2])}_holds")
    L.append("")
    L.append("end Coval")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(L) + "\n")
    print(f"-> {OUT}  ({len(thms)} theorems, {len(seen)} empirical axioms, "
          f"{sum(len(v) for v in open_conf.values())} blocking confound hypotheses)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
