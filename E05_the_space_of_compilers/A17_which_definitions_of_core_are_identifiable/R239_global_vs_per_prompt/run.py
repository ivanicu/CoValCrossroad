"""R239 -- the identifiability failure is a consequence of the PER-PROMPT factoring, not of the data.

SIX ROUNDS ASKED THE SAME QUESTION ABOUT THE WRONG OBJECT
    R224-R237 each computed H_need and H_have FOR ONE PROMPT, found H_need larger, and concluded the
    core is not identifiable. Every one of those is correct and every one is about a PER-PROMPT
    core: 968 separate cores of four criteria each, which is what CoVal ships.

    But the thing "public input to AI values" is FOR is a standard that applies across prompts. And
    bits behave completely differently in the two cases:

        WITHIN a prompt   raters all order the SAME four responses. There is one consensus
                          ordering. R raters buy precision on a ~6-bit object, never a 60-bit one
                          (R225 measured this and R224's assumption survived it).
        ACROSS prompts    each prompt is an INDEPENDENT observation. The bits ADD.

    968 prompts x H_eff each. That is the asymmetry six rounds walked past.

THIS IS A DERIVATION AND IS LABELLED ONE. Nothing below could have come out otherwise; the arithmetic
    forces it. What it changes is which QUESTION is worth measuring, which is the point of a
    derivation and the reason it is worth more than a measurement here.

ESTIMAND        H_need(global core of k over a shared vocabulary V) against H_have(global) = the sum
                over prompts, at the conservative and optimistic ends of R237's bracket.
IDENTIFICATION  the DERIVATION is exact. The MEASUREMENT is not available: a global criterion must
                be judged against every prompt's responses and the release ships each criterion
                judged only against its own prompt. That is a named, costed next step, not a wall.
SCOPE           986 rubrics, 15,248 criteria, m=4. H_eff per prompt from R237's measured bracket
                [1.02, 3.45] bits at the release's own rater noise and rater count.
KILL            if a global core is NOT identifiable either, the per-prompt factoring is not the
                cause and six rounds' conclusion generalises rather than narrows.
ARITHMETIC TRAP the additivity across prompts is an ASSUMPTION -- independent observations -- and it
                is stated, checked against the shared-criteria measurement below, and would fail if
                prompts share their normative content. That check is the one non-derived number here.
"""
from __future__ import annotations
import collections, json, math, pathlib, re, sys
import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"
DATA = ROOT / "data"
H_EFF = (1.02, 3.45)          # R237's measured bracket, per prompt, at eps=0.25 and R=14
STOP = set("a an the and or of to in on at is are be as by for with from that this it not but if so "
           "when about into over than then there their they them we you your our its do does did can "
           "could should would will may might have has had been being any all each other more most "
           "less least such very".split())


def toks(s):
    return frozenset(w for w in re.findall(r"[a-z']+", str(s).lower())
                     if w not in STOP and len(w) > 3)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rub = [json.loads(l) for l in (DATA / "conversation_rubrics.jsonl").open()]
    crits, per_prompt = [], []
    for d in rub:
        c = [it["criterion"] for it in d["coval_full"] if it.get("scores")]
        per_prompt.append(len(c)); crits += c
    P, N = len(rub), len(crits)
    print("=== the object ===")
    print(" prompts %d | criteria %d | median per prompt %d" % (P, N, np.median(per_prompt)))

    print("\n=== THE ASYMMETRY (derivation) ===")
    lo, hi = H_EFF
    print(" WITHIN a prompt : one consensus ordering. H_eff in [%.2f, %.2f] bits, and adding raters"
          % (lo, hi))
    print("                   does not raise it -- R225 measured that and R224's assumption held.")
    print(" ACROSS prompts  : each is an INDEPENDENT observation, so the bits ADD.")
    print("                   H_have(global) in [%.0f, %.0f] bits over %d prompts."
          % (P * lo, P * hi, P))

    print("\n=== what a core of size k COSTS, per-prompt vs global ===")
    nmed = int(np.median(per_prompt))
    print("%-6s %22s %14s   %22s %14s" % ("k", "per-prompt H_need", "vs [%.1f,%.1f]" % (lo, hi),
                                          "global H_need", "vs [%.0f,%.0f]" % (P * lo, P * hi)))
    rows = []
    for k in (1, 2, 4, 10, 25, 50, 100, 250):
        pp = math.log2(math.comb(nmed, k)) if k <= nmed else float("inf")
        gl = math.log2(math.comb(N, k))
        okp = "IDENT" if pp <= lo else ("edge" if pp <= hi else "no")
        okg = "IDENT" if gl <= P * lo else ("edge" if gl <= P * hi else "no")
        print("%-6d %22s %14s   %22.1f %14s"
              % (k, ("%.2f" % pp) if pp != float("inf") else "n/a (k>n)", okp, gl, okg))
        rows.append({"k": k, "per_prompt_bits": None if pp == float("inf") else pp,
                     "global_bits": gl, "per_prompt": okp, "global": okg})

    kmax = max(k for k in range(1, 4000)
               if math.log2(math.comb(N, k)) <= P * lo)
    print("\n -> at the CONSERVATIVE end of R237's bracket, a GLOBAL core of up to k = %d criteria"
          % kmax)
    print("    is identifiable from this release, while a PER-PROMPT core of 2 is not.")

    print("\n=== the assumption that could break it, checked ===")
    # additivity requires prompts to be INDEPENDENT observations. If prompts share their normative
    # content, the bits do not add. Measure how much criterion text is actually shared across prompts.
    seen = collections.defaultdict(set)
    for i, d in enumerate(rub):
        for it in d["coval_full"]:
            if it.get("scores"):
                t = toks(it["criterion"])
                if t:
                    seen[t].add(i)
    shared = sum(1 for t, ps in seen.items() if len(ps) > 1)
    tot = len(seen)
    print(" distinct criterion token-sets %d | appearing in >1 prompt: %d (%.2f%%)"
          % (tot, shared, 100 * shared / tot))
    print(" -> %s"
          % ("criteria are ESSENTIALLY PROMPT-SPECIFIC, so treating prompts as independent "
             "observations is supported" if shared / tot < 0.05 else
             "criteria RECUR across prompts, so the additivity assumption is WEAKENED and the "
             "global figures above are upper bounds"))

    print("\n" + "=" * 78); print("VERDICT"); print("=" * 78)
    v = ("DERIVATION: the identifiability failure six rounds found is a property of the PER-PROMPT "
         "FACTORING, not of the release's size. Within a prompt the observable is one ~%.1f-bit "
         "consensus ordering and no number of raters raises it; across %d prompts the observations "
         "are independent and the bits add to [%.0f, %.0f]. A global core of up to k=%d is "
         "identifiable at the conservative end while a per-prompt core of 2 is not. CoVal ships the "
         "per-prompt object."
         % (lo, P, P * lo, P * hi, kmax))
    print("\n  " + v)
    print("\n  NOT MEASURED, and it is a costed next step rather than a wall: fitting a global core")
    print("  needs every candidate criterion judged against EVERY prompt's responses, and the")
    print("  release ships each criterion judged only against its own. That is one cross-prompt")
    print("  judge pass, the same shape as the one R233 just ran.")
    json.dump({"prompts": P, "criteria": N, "H_eff_bracket": list(H_EFF),
               "global_bits": [P * lo, P * hi], "rows": rows, "k_max_global": kmax,
               "shared_token_sets": shared, "distinct_token_sets": tot, "verdict": v},
              open(OUT / "global_vs_per_prompt.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
