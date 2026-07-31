"""One `status` enum is doing six incompatible jobs, and the orphan check was reading it as one.

The standing check "every retracted claim must have an incoming kill edge" reported K1-polarity-
retention as an orphan. K1 is not a claim. It is a KNIFE -- an attack vector -- and `refuted` on a
knife does not mean "this is false". It means the attack was blunted. A blunted attack needs no
edge overturning it, so the check was demanding a kill edge for a node whose status word happens to
be spelled the same as a claim's.

That is the failure HB8 exists to prevent: one axis carrying different meanings for different types.
Six kinds share one status vocabulary and it means something different in each:

    my_claim         refuted -> the claim is FALSE                  (needs a kill edge)
    their_assumption refuted -> their premise is FALSE              (needs a kill edge)
    knife            refuted -> the attack was BLUNTED              (needs nothing)
    defect           settled -> the defect is REAL and recorded     (needs nothing)
    control          open    -> the control has not been RUN        (needs nothing)
    instrument       partial -> the instrument is bounded, not sound

Reading `refuted` uniformly makes the check demand kill edges from knives, and six defect nodes
carrying `refuted` produced six more false positives on top. Six false alarms around one real signal
is a check nobody reads, which is how a check stops being a check.

THE FIX IS A DOMAIN PER KIND, ENFORCED, not a note in a docstring -- prose is not enforcement. This
module declares which statuses each kind may take, verifies the live graph against it, and exposes
the predicate the orphan check should have been using all along.

It also surfaces a real inconsistency in my own data: twelve defect nodes exist and six carry
`settled` while six carry `refuted`, for no reason anyone recorded. Two words for one state is the
drift an enum is supposed to make impossible.
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from derivation_chain import q  # noqa: E402

# what each kind's status is ALLOWED to say, and what the word means there
DOMAIN: dict[str, dict[str, str]] = {
    "my_claim": {
        "settled": "established at its stated D-level and scope",
        "partial": "established under a narrower scope than first claimed",
        "open": "not yet decided",
        "refuted": "FALSE -- requires an incoming overturns edge naming what killed it",
    },
    "their_assumption": {
        "settled": "holds", "partial": "holds under a narrower reading",
        "open": "not yet tested",
        "refuted": "FALSE -- requires an incoming overturns edge",
    },
    "fact": {"settled": "measured", "partial": "measured with a stated limitation",
             "open": "not yet measured"},
    "knife": {
        "open": "the attack has not been run",
        "partial": "the attack landed on part of the target",
        "refuted": "BLUNTED -- the attack did not land. NOT a claim about truth, and it needs no "
                   "kill edge; reading this word as a claim's 'refuted' is what broke the check",
        "settled": "the attack landed and its result is recorded",
    },
    "control": {"settled": "run, with its result recorded", "open": "not yet run",
                "partial": "run but underpowered for its purpose"},
    "instrument": {"settled": "validated", "partial": "bounded, not sound",
                   "open": "unvalidated"},
    "defect": {"settled": "REAL, recorded, and its catching mechanism named"},
    "result": {"settled": "recorded", "partial": "recorded with a limitation", "open": "pending"},
}

# only these kinds mean "this statement is false" by `refuted`
FALSITY_KINDS = ("my_claim", "their_assumption")


def needs_kill_edge(kind: str, status: str) -> bool:
    """The predicate the orphan check should use. A knife that was blunted is not an unexplained
    retraction, and neither is a defect that is simply on record."""
    return status == "refuted" and kind in FALSITY_KINDS


def normalise() -> int:
    """Bring out-of-domain statuses into their kind's domain. Explicit, never automatic.

    Six defect nodes from earlier phases carry `refuted` where the only legal value is `settled`.
    A defect is either on record or absent; `refuted` on one reads as "this defect turned out not
    to be a defect", which is not what any of the six mean -- every one of them is a real error that
    really happened. Rewriting is gated behind a flag rather than run on import, because a schema
    audit that silently edits the thing it audits cannot be trusted to report on it.
    """
    n = 0
    for kind, allowed in DOMAIN.items():
        if len(allowed) != 1:
            continue                       # only kinds with a single legal value are unambiguous
        only = next(iter(allowed))
        rows = q("SELECT id, name FROM node WHERE kind=%s AND coalesce(status,'') <> %s",
                 (kind, only))
        for nid, name in rows:
            q("UPDATE node SET status=%s WHERE id=%s", (only, nid))
            print(f"   {kind}: {name[:52]} -> {only}")
            n += 1
    print(f"normalised {n} node(s)")
    return n


def audit() -> int:
    rows = q("SELECT id, kind, name, coalesce(status,'NULL') FROM node ORDER BY kind, name")
    bad = [(k, n, s) for _i, k, n, s in rows
           if k in DOMAIN and s not in DOMAIN[k] and s != "NULL"]
    unknown_kind = sorted({k for _i, k, _n, _s in rows if k not in DOMAIN})
    print(f"nodes {len(rows)}   kinds {len({r[1] for r in rows})}")
    if unknown_kind:
        print(f"KINDS WITH NO DECLARED DOMAIN (named, not ignored): {unknown_kind}")
    print(f"\nstatus values outside their kind's domain: {len(bad)}")
    for k, n, s in bad:
        print(f"   {k:18s} {n[:44]:44s} status={s!r} allowed={sorted(DOMAIN[k])}")

    # the drift an enum is meant to prevent: one state spelled two ways
    print("\nstatus spread within a kind (two words for one state is drift):")
    for kind, in q("SELECT DISTINCT kind FROM node ORDER BY kind"):
        vals = q("SELECT coalesce(status,'NULL'), count(*) FROM node WHERE kind=%s "
                 "GROUP BY 1 ORDER BY 2 DESC", (kind,))
        allowed = DOMAIN.get(kind, {})
        flag = ""
        if kind == "defect" and len(vals) > 1:
            flag = "   <- DRIFT: a defect is either on record or absent; there is no second state"
        print(f"   {kind:18s} " + "  ".join(f"{v}={c}" for v, c in vals) + flag)

    # the orphan check, using the predicate rather than the bare word
    orphans = []
    for nid, kind, name, status in rows:
        if needs_kill_edge(kind, status):
            got = q("SELECT 1 FROM edge WHERE dst=%s AND kind='overturns' LIMIT 1", (nid,))
            if not got:
                orphans.append((kind, name))
    print(f"\nretracted-with-no-kill-edge, scoped to kinds where refuted means FALSE: "
          f"{len(orphans)}")
    for k, n in orphans:
        print(f"   {k}: {n}")
    if not orphans:
        print("   (none) -- and the previous count of 7 was six knives-and-defects plus this "
              "vocabulary error, not seven unexplained retractions")
    return 0


if __name__ == "__main__":
    if "--fix" in sys.argv:
        normalise()
    raise SystemExit(audit())
