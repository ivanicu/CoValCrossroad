"""The validation certificate: what a compiled core must ship for its claim to be FALSIFIABLE.

E05 arrived at a formulation --

    core = (Q, class, representative, certificate)
        admissible only if  log2|H(Q)| <= H_have

-- and then said "the certificate says which is which" without ever specifying its fields. A
formulation whose certificate is unspecified is not a formulation, it is a slogan. This file is the
schema, and the point of it is that it can FAIL.

THE RULE THAT MAKES IT A CERTIFICATE AND NOT A BADGE
    Every field is THREE-VALUED, never boolean:
        MEASURED      a value, WITH its population, instrument, baseline and regime
        NOT_MEASURED  and what it would require -- never "planned", never omitted
        FAILED        the measurement was made and the core did not meet it
    A field left blank is NOT_MEASURED. Silence is never a pass, and an omitted row is the
    flattering-direction unavailability claim realstat §2 forbids.

⚠ AND THE CERTIFICATE MUST BE ABLE TO COME BACK BAD. `emit()` refuses to issue one where every
    field is MEASURED-and-passing unless the register is non-empty, because a site with no
    structural limits has not looked for any. That refusal is the check-that-cannot-fail guard
    (realstat §4) pointed at this file itself.
"""
from __future__ import annotations
import json

MEASURED, NOT_MEASURED, FAILED = "MEASURED", "NOT_MEASURED", "FAILED"

REQUIRED = [
    ("Q",                 "the declared query family. Without it no other row means anything."),
    ("identifiability",   "log2|H(Q)| against H_have, and the verdict."),
    ("class_agreement",   "the rate the declared class survives, with its FLOOR and CEILING."),
    ("representative",    "which printed items are IDENTIFIED and which are CHOSEN."),
    ("instrument",        "the named judge(s), and how far the claim moves across them."),
    ("transport",         "does it hold on candidates the core never saw?"),
    ("provenance",        "share of output rules with a resolvable source."),
]


class Field:
    def __init__(self, status, value=None, scope=None, requires=None, note=None):
        if status not in (MEASURED, NOT_MEASURED, FAILED):
            raise ValueError("status must be three-valued, got %r" % status)
        if status == MEASURED and scope is None:
            raise ValueError("a MEASURED field without a SCOPE is the failure mode that produced "
                             "eleven of twelve retractions in this programme: a correct number "
                             "reported without the population it holds over")
        if status == NOT_MEASURED and not requires:
            raise ValueError("a NOT_MEASURED field must say what it would REQUIRE. 'planned' is an "
                             "unavailability claim in the flattering direction (realstat §2)")
        self.status, self.value, self.scope = status, value, scope
        self.requires, self.note = requires, note

    def asdict(self):
        return {k: v for k, v in
                {"status": self.status, "value": self.value, "scope": self.scope,
                 "requires": self.requires, "note": self.note}.items() if v is not None}


def emit(name: str, fields: dict, register: list[str]) -> dict:
    """Issue a certificate, or refuse. Refusal is a valid and common outcome."""
    missing = [k for k, _ in REQUIRED if k not in fields]
    for k in missing:
        fields[k] = Field(NOT_MEASURED, requires="not addressed by the issuer")
    if not register:
        raise ValueError(
            "refusing to issue: the register is empty. A site with no structural limits has not "
            "looked for any, and a certificate every core passes is a badge. State what this site "
            "cannot measure, or do not certify.")
    counts = {s: sum(1 for f in fields.values() if f.status == s)
              for s in (MEASURED, NOT_MEASURED, FAILED)}
    admissible = counts[FAILED] == 0 and fields["Q"].status == MEASURED
    return {"core": name, "fields": {k: v.asdict() for k, v in fields.items()},
            "counts": counts, "register": register,
            "admissible": admissible,
            "reading": ("ADMISSIBLE for the declared Q -- which is not the same as correct, and "
                        "says nothing about any other Q" if admissible else
                        "NOT ADMISSIBLE: " + ("Q undeclared" if fields["Q"].status != MEASURED
                                              else "%d field(s) FAILED" % counts[FAILED]))}


def render(cert: dict) -> str:
    out = ["CERTIFICATE  %s" % cert["core"], "=" * 78]
    for k, _desc in REQUIRED:
        f = cert["fields"][k]
        out.append("%-16s %-13s %s" % (k, f["status"], f.get("value", "")))
        for tag in ("scope", "requires", "note"):
            if f.get(tag):
                out.append("%-16s   %-9s %s" % ("", tag, f[tag]))
    out += ["", "counts           %s" % cert["counts"],
            "register         %d entr%s:" % (len(cert["register"]),
                                             "y" if len(cert["register"]) == 1 else "ies")]
    out += ["                 - %s" % r for r in cert["register"]]
    out += ["", cert["reading"]]
    return "\n".join(out)
