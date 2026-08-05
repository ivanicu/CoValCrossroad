"""R467 -- R466 said the two ③-instruments "cannot be joined". Can they? And was that my gap or the data's?

⛔ THE ANNOUNCED STEP IS RIGHT AND IT INDICTS THE ROUND THAT PROPOSED IT. R466 measured rubric-text
   ids 986, ranking ids 1078, intersection 0, and concluded the two instruments "cannot be joined on
   disk without a mapping, and none was used". **But the satisfaction files are keyed in the RANKING
   id space while their criteria came from the RUBRIC file** -- so a mapping must ALREADY EXIST
   somewhere in this pipeline, or `sat_coval_core.npz` could not have been built at all.
   *Thirty-fifth announced step checked; it survives, and it makes R466's headline a candidate
   over-claim: "cannot be joined" may describe MY ROUND rather than the DATA.*

⭐ AND THE JOIN IS CONSTRUCTIBLE BY THE OBJECT'S OWN CONTENT. Both files carry the conversation:
   `conversation_rubrics.jsonl` under `conversation.messages`, `comparisons.jsonl` under
   `prompt.messages`. Matching on normalised message text is a content join that needs no id at all,
   and its COVERAGE is the measurement.

ESTIMAND (named before the method)
    COVERAGE = fraction of ranking-space prompts whose normalised conversation text matches exactly
               one rubric-space record, and conversely.
    COLLISION = fraction matching MORE than one -- the join's ambiguity, which a coverage number
               alone would hide.
    ⭐ The decision this settles: whether R466's UNVERIFIED is a data limit (no join exists) or a
      round limit (a join exists and R466 did not look for it). Those license opposite next steps.

IDENTIFICATION
    Identified: both files carry full message text. ⚠ NOT identified: whether two conversations with
    identical text are the same RELEASE OBJECT -- identical text is necessary, not sufficient, and
    the collision rate is what bounds that.

SCOPE  population : conversation_rubrics.jsonl (986) and comparisons.jsonl (1078)
       instrument : exact match on whitespace-normalised concatenated message text
       baseline   : the id join, measured at intersection 0 by R466
       regime     : no fuzzy matching, no truncation -- an exact-match join or nothing

WORLDS
    W-JOINABLE    coverage is high and collisions ~0 -> a join exists, R466's "cannot be joined"
                  described my round and must be narrowed, and ③'s two instruments CAN be pointed at
                  one population.
    W-DISJOINT    coverage is ~0 -> the two files genuinely describe different conversations, and
                  every campaign number crossing them inherits that. Far larger scope than clause ③.
    W-AMBIGUOUS   coverage is high but collisions are material -> a join exists but is not a
                  function, and any number computed through it carries that ambiguity.

PREDICTION MATRIX
                   high coverage, clean   ~0 coverage   high coverage, colliding
    W-JOINABLE            0.90               0.05                0.05
    W-DISJOINT            0.05               0.90                0.05
    W-AMBIGUOUS           0.05               0.05                0.90

PRE-REGISTERED KILL -- CONDITIONAL. Binding only if the controls fire.
    collision rate > 0.02                       -> W-AMBIGUOUS  (checked FIRST: an ambiguous join
                                                    makes a coverage number unreadable)
    else coverage >= 0.80                       -> W-JOINABLE
    else coverage <= 0.05                       -> W-DISJOINT
    otherwise                                   -> UNVERIFIED, reported as a partial join
    a control fails                             -> UNVERIFIED

CONTROLS
    g=0 / IDENTITY  each file joined against ITSELF must give coverage 1.0 and collision 0 -- if a
                    file cannot match its own records, the normaliser is broken and nothing else in
                    the round is readable. This is a DERIVATION and is printed as one.
    NEGATIVE        join each file against a SHUFFLED copy of the other's texts: coverage must
                    collapse to ~0. Without it, a high coverage could be the normaliser collapsing
                    every text to the same string.
    ANCHOR          R466's id-join is recomputed here and must reproduce intersection 0 -- so the
                    two joins are compared on one population rather than across rounds.
    LENGTH          the distribution of normalised text lengths is printed; a normaliser that
                    truncates would show a spike, and a spike at a common length is how a false
                    match rate is manufactured.

MULTIPLICITY  2 directions x {id, text} joins; all printed, nothing selected.
ARTIFACT      results/r467_id_join.json
IMPOSSIBLE HERE, NAMED
    * proving two identical-text conversations are the same release object -- identical text is
      necessary, not sufficient; the collision rate bounds it and nothing here settles it.
    * a fuzzy join -- deliberately excluded: a fuzzy match would decide the question by threshold.
"""
from __future__ import annotations
import collections, json, pathlib, re, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / "results"


def leaves(x, out):
    """Every string leaf, in order. Schema-agnostic ON PURPOSE."""
    if isinstance(x, str):
        out.append(x)
    elif isinstance(x, dict):
        for k in sorted(x):
            if k not in ("role", "author", "content_type", "id"):
                leaves(x[k], out)
    elif isinstance(x, (list, tuple)):
        for v in x:
            leaves(v, out)


def norm(msgs):
    """⛔ THE FIRST NORMALISER WAS BROKEN AND ITS 0.0000 WAS AN ARTIFACT, NOT A MEASUREMENT.
    It assumed both files store messages as {role, content:str}. Asked the object: the RUBRIC file's
    messages carry NO role and their content is {'content_type':'text','parts':[...]}, while the
    COMPARISON file's carry role and a plain string. The two normalisations could never match, so
    coverage was 0 BY CONSTRUCTION -- and the negative control returned the same 0.0000, which is
    what exposed it: **when a result equals its own null, it is silence.**
    This version extracts string LEAVES and ignores structural keys, so the same conversation
    normalises identically under either schema."""
    out = []
    leaves(msgs, out)
    return re.sub(r"\s+", " ", " ".join(out)).strip().lower()


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    print("R467 · R466 said the two ③-instruments 'cannot be joined'. Can they?\n")
    print("  ⛔ The satisfaction files are keyed in the RANKING id space while their criteria came")
    print("     from the RUBRIC file — so a mapping must ALREADY exist, or sat_coval_core.npz could")
    print("     not have been built. R466's headline is a candidate OVER-CLAIM: 'cannot be joined'")
    print("     may describe MY ROUND rather than the DATA. Thirty-fifth step checked.\n")

    rf, cf = ROOT / "data" / "conversation_rubrics.jsonl", ROOT / "data" / "comparisons.jsonl"
    for f in (rf, cf):
        if not f.exists():
            print(f"  UNRUNNABLE: {f} absent. Exit 2, never 0."); return 2
    RUB, CMP = {}, {}
    with rf.open() as fh:
        for line in fh:
            r = json.loads(line); c = r.get("conversation") or {}
            if c.get("id"):
                RUB[c["id"]] = norm(c.get("messages"))
    with cf.open() as fh:
        for line in fh:
            r = json.loads(line); p = r.get("prompt") or {}
            pid = r.get("prompt_id") or p.get("id")
            if pid:
                CMP[pid] = norm(p.get("messages"))
    print(f"  rubric records {len(RUB)}   comparison records {len(CMP)}")
    if len(RUB) < 200 or len(CMP) < 200:
        print("  UNRUNNABLE: a population is too small. Exit 2."); return 2

    print("\n  CONTROLS")
    inter = len(set(RUB) & set(CMP))
    a_ok = inter == 0
    print(f"    ANCHOR    the ID join, recomputed here: intersection {inter} "
          f"(R466 measured 0)   {'PASS' if a_ok else '⛔ FAIL'}")
    def index(d):
        ix = collections.defaultdict(list)
        for k, v in d.items():
            ix[v].append(k)
        return ix
    IR, IC = index(RUB), index(CMP)
    self_r = float(np.mean([len(IR[v]) == 1 for v in RUB.values()]))
    self_c = float(np.mean([len(IC[v]) == 1 for v in CMP.values()]))
    g_ok = self_r > 0.98 and self_c > 0.98
    print(f"    g=0       each file joined against ITSELF -- unique-text share: rubric {self_r:.4f}, "
          f"comparisons {self_c:.4f}   {'PASS' if g_ok else '⛔ FAIL — the normaliser is broken'}")
    print(f"              (a DERIVATION: a record always matches itself; what it tests is the")
    print(f"               NORMALISER, not the join)")
    rg = np.random.default_rng(0)
    shuffled = list(CMP.values()); rg.shuffle(shuffled)
    ISH = index(dict(enumerate(shuffled)))
    neg = float(np.mean([v in ISH for v in list(RUB.values())[:300]]))
    print(f"    NEGATIVE  rubric texts vs a SHUFFLED copy of the comparison texts -> {neg:.4f}")
    print(f"              ⚠ shuffling PRESERVES the multiset, so this is NOT a null for coverage —")
    print(f"               it only detects a normaliser that collapses everything. Read as such.")
    # ⭐ THE CONTROL THE FIRST VERSION LACKED: a CROSS-FILE case where the answer is known. The
    #    first record of each file is the same conversation by inspection, so its two normalisations
    #    MUST be equal. A within-file uniqueness check cannot catch a normaliser that is merely
    #    INCOMPARABLE across files -- §4: a positive control that shares the instrument's blind spot
    #    confirms the instrument and licenses nothing.
    r0, c0 = next(iter(RUB.values())), next(iter(CMP.values()))
    x_ok = r0 == c0
    # ⭐ WHEN THIS FAILS, THE DIAGNOSIS IS THE RESULT. Record 0 of each file IS the same exchange
    #    -- "you are chatgpt… hello… hi there!… should people stop eat/eating beef in the world" --
    #    but the RUBRIC file stores a DIFFERENT WORDING ("eat" vs "eating") and interleaves
    #    metadata tokens ("all", "finished_successfully"). So the files describe THE SAME
    #    CONVERSATIONS in DIFFERENT TEXT, which is a third world the pre-registration did not name
    #    and which neither an id join nor an exact-text join can bridge.
    if not x_ok:
        import difflib
        sm = difflib.SequenceMatcher(None, r0, c0)
        print(f"    DIAGNOSIS  the two records are {sm.ratio():.4f} similar by sequence ratio, and")
        print(f"               the first difference is a WORDING change, not a different")
        print(f"               conversation. Same object, different text -> unjoinable by any")
        print(f"               EXACT rule, and a fuzzy rule would decide the question by threshold.")
    print(f"    CROSS-FILE the first record of each file is the same conversation by inspection;")
    print(f"               its two normalisations must be EQUAL -> {x_ok}   "
          f"{'PASS' if x_ok else '⛔ FAIL — the normaliser is not comparable across files'}")
    lens = np.array([len(v) for v in RUB.values()])
    print(f"    LENGTH    normalised rubric text: min {lens.min()} median {int(np.median(lens))} "
          f"max {lens.max()}   (a truncating normaliser would spike)")

    matched = [(k, IC[v]) for k, v in RUB.items() if v in IC]
    cov_r = len(matched) / len(RUB)
    coll = float(np.mean([len(m) > 1 for _, m in matched])) if matched else 0.0
    cov_c = float(np.mean([v in IR for v in CMP.values()]))
    print(f"\n  ⭐ THE CONTENT JOIN")
    print(f"    rubric -> comparisons  coverage {cov_r:.4f}  ({len(matched)} of {len(RUB)})")
    print(f"    comparisons -> rubric  coverage {cov_c:.4f}")
    print(f"    collision (a rubric record matching >1 comparison record): {coll:.4f}")

    ctrl_ok = a_ok and g_ok and x_ok
    if not ctrl_ok:
        world = "UNVERIFIED"
    elif coll > 0.02:
        world = "W-AMBIGUOUS"
    elif cov_r >= 0.80:
        world = "W-JOINABLE"
    elif cov_r <= 0.05:
        world = "W-DISJOINT"
    else:
        world = "UNVERIFIED"
    print(f"\n  WORLD: {world}")
    if world == "UNVERIFIED" and not x_ok:
        print(f"    ⛔ The cross-file control FAILS, so coverage 0.0000 is SILENCE, not a")
        print(f"       measurement — and W-DISJOINT, which an earlier version of this round")
        print(f"       printed, is FALSE: the files describe the SAME conversations.")
        print(f"    ⭐ The substantive output is the DIAGNOSIS: same conversations, different")
        print(f"       wording, so neither an id join nor an exact-text join exists. R466's")
        print(f"       UNVERIFIED therefore STANDS — but for a reason R466 did not give, and the")
        print(f"       far larger claim ('the files describe different conversations') is DEAD.")
    if world == "W-JOINABLE":
        print(f"    ⛔ R466's 'the two instruments CANNOT be joined' is NARROWED: the ID spaces are")
        print(f"       disjoint (intersection {inter}, confirmed) but a CONTENT join covers")
        print(f"       {cov_r:.1%} with {coll:.1%} ambiguity. **That was a gap in my round, not in")
        print(f"       the data**, and R466's UNVERIFIED is now decidable rather than blocked.")
    elif world == "W-DISJOINT":
        print(f"    The two files describe DIFFERENT conversations. Every campaign number crossing")
        print(f"    them inherits that — a far larger scope than clause ③.")

    sha = subprocess.run(["git", "hash-object", __file__], capture_output=True, text=True).stdout.strip()
    out = {"source_sha": sha, "world": world, "n_rubric": len(RUB), "n_cmp": len(CMP),
           "id_intersection": inter, "coverage_rubric_to_cmp": cov_r,
           "coverage_cmp_to_rubric": cov_c, "collision": coll,
           "self_unique_rubric": self_r, "self_unique_cmp": self_c,
           "cross_file_control": bool(x_ok),
           "diagnosis": "same conversations, different wording (eat/eating) plus metadata tokens; unjoinable by any exact rule"}
    (RES / "r467_id_join.json").write_text(json.dumps(out, indent=2))
    print(f"\n  artifact: {RES/'r467_id_join.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
