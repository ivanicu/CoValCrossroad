"""judge_transport -- score a committed criterion set against the SECOND corpus.

WHY THIS EXISTS. `judge_core.py` hardcodes `load_join(data/comparisons.jsonl, ...)`, so every arm in
this campaign is scored against ONE release. `DEFINITION.md`'s own table has carried
`transfer to another release: one release` as a wall, and R398 retracted it: `data/utterances.jsonl`
holds 68,371 human-scored rows over 8,011 conversations and had been referenced by zero rounds.

Seven rounds have since READ that corpus -- existence (R398), estimand (R399), depth confound (R400),
harness (R402), statability (R403), clustering (R412), score-clustering (R413). NONE calls
`select_core` or `judge_core` on it. Six rounds of `can we?` and none of `here is the number`.

⛔ AND THE CHEAPEST TRANSPORT TEST NEEDS NO CRITERION GENERATION AT ALL. The second corpus has no
   rubric, so any prompt-SPECIFIC core would have to be generated first -- a second GPU job and a
   second set of assumptions. But `core_generic.json` is PROMPT-BLIND by construction: fixed criteria
   that never see the prompt. It transports as-is, and it is the arm §4's sham row identified as
   carrying five-sixths of what the instrument achieves. So the floor of the transport question is
   answerable now, and it is honest about what it cannot answer: nothing here speaks to a
   prompt-specific core.

REUSE, NOT REBUILD (prior-art gate). `covalx.judge.build_prompt` and `covalx.judge.Judge.score` are
used unchanged; this file adds a LOADER and nothing else. No judging logic is reimplemented.

PROVENANCE. Writes the same `provenance` field `judge_core.py` writes, because
`assurance/a_scored_artifact_records_its_configuration.py` requires a producer to record what made
its output -- and four rounds were once spent inferring what those fields state.

UNIT. R413 measured `kappa_chosen = 1.0` and `p_in_argmax = 1.0` WITHIN a conversation: the chosen
response is always the score-argmax there. So the independent unit is the CONVERSATION, n_eff = 8,076
of 27,151 interactions (deff 3.317). The sampler therefore samples CONVERSATIONS, never rows --
sampling rows would inflate n by 3.3x and every interval computed from it would be too narrow.
"""
from __future__ import annotations
import argparse
import collections
import hashlib
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
MODEL = "/mnt/e/data.ai-models.local-model-store.storage.xl.private.readonly/Qwen3.5-2B-Base"
PRODUCER_SHA256 = hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()


def load_second(path: pathlib.Path, limit_convs: int, seed: int):
    """-> [(conv_id, interaction_id, prompt, [(resp_id, text, score, chosen)])], sampled BY CONVERSATION."""
    by_inter = collections.defaultdict(list)
    conv_of = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            iid = str(r.get("interaction_id") or r.get("prompt_id") or r.get("id"))
            cid = str(r.get("conversation_id") or iid)
            conv_of[iid] = cid
            by_inter[iid].append(r)
    # keep only interactions with >=2 distinct responses AND a usable human signal
    usable = {}
    for iid, rows in by_inter.items():
        seen, cand = set(), []
        for r in rows:
            t = (r.get("model_response") or "").strip()
            s = r.get("score")
            if not t or s is None or t in seen:
                continue
            seen.add(t)
            # `utterance_id` is the row identity in this release -- verified against the object,
            # not guessed. `response_id` does not exist here; falling back to a positional index
            # would make two runs' ids depend on iteration order.
            cand.append((str(r.get("utterance_id") or r.get("response_id") or len(cand)), t,
                         float(s), bool(r.get("if_chosen")), int(r.get("turn") or 0)))
        if len(cand) >= 2:
            usable[iid] = (rows[0].get("user_prompt") or "", cand)
    convs = sorted({conv_of[i] for i in usable})
    rng = np.random.default_rng(seed)
    if limit_convs and limit_convs < len(convs):
        convs = sorted(rng.choice(convs, size=limit_convs, replace=False).tolist())
    keep = set(convs)
    return [(conv_of[i], i, usable[i][0], usable[i][1])
            for i in sorted(usable) if conv_of[i] in keep]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--core", required=True, help="a committed core_*.json. A PROMPT-BLIND core "
                    "(e.g. core_generic.json) transports as-is; a prompt-keyed one does not and "
                    "this script REFUSES it rather than silently scoring a mismatch.")
    ap.add_argument("--out", required=True)
    ap.add_argument("--corpus", default=str(ROOT / "data" / "utterances.jsonl"))
    ap.add_argument("--convs", type=int, default=2200,
                    help="conversations, NOT rows. R413: the chosen response is the score-argmax "
                         "within a conversation (kappa 1.0), so the conversation is the unit.")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--max-reply", type=int, default=1400)
    a = ap.parse_args()

    corpus = pathlib.Path(a.corpus)
    if not corpus.exists():
        print(f"  UNRUNNABLE: {corpus} absent. Exit 2, never 0."); return 2
    core = json.loads(pathlib.Path(a.core).read_text())

    # A prompt-keyed core maps prompt-id -> criteria and those ids do NOT exist in the second
    # corpus. Scoring it here would silently drop every prompt and emit an empty artifact, which
    # would read as a clean run. Refuse instead.
    # ⭐ EXTENDED 2026-08-04 (R433). A CONVERSATION-KEYED core is now accepted; a PROMPT-keyed one is
    #    still refused. The distinction is not cosmetic and it is checked against the corpus rather
    #    than guessed from the file: a dict whose keys are conversation ids OF THIS CORPUS is
    #    clause ②'s SUBJECT -- a prompt-specific core -- and is exactly what every round so far has
    #    lacked. A dict whose keys are the home release's prompt ids still cannot transport, and
    #    scoring it would emit an empty artifact that reads as a clean run.
    per_conv = None
    if isinstance(core, dict):
        vals = list(core.values())
        crit = vals[0] if vals else []
        if len(core) > 1 and not all(v == crit for v in vals):
            data_probe = load_second(corpus, a.convs, a.seed)
            corpus_convs = {d[0] for d in data_probe}
            overlap = len(corpus_convs & set(core))
            if overlap < 0.5 * len(corpus_convs):
                print(f"  REFUSING: {a.core} is keyed on ids this corpus does not have "
                      f"({overlap}/{len(corpus_convs)} conversations covered). Scoring it would emit "
                      f"an empty artifact that reads as a clean run. Exit 2.")
                return 2
            per_conv = {k: [c for c in v if str(c).strip()] for k, v in core.items()}
            crit = vals[0]
            print(f"  CONVERSATION-KEYED core accepted: {overlap}/{len(corpus_convs)} conversations "
                  f"covered. This is clause ②'s SUBJECT, not its comparator.", flush=True)
    else:
        crit = list(core)
    crit = [c for c in crit if str(c).strip()]
    if not crit:
        print("  UNRUNNABLE: the core carries no criteria. An empty population is not a pass. Exit 2.")
        return 2

    data = load_second(corpus, a.convs, a.seed)
    if not data:
        print("  UNRUNNABLE: no usable interaction. Exit 2, never 0."); return 2
    if per_conv is not None:
        # ⚠ an interaction whose conversation the generator failed to parse has NO criteria. It is
        #   DROPPED and COUNTED, never silently scored with someone else's core -- that would be
        #   the sham (wrong-conversation criteria) leaking into the real arm.
        before = len(data)
        data = [d for d in data if per_conv.get(d[0])]
        print(f"  dropped for no generated core: {before - len(data)} of {before} interactions",
              flush=True)
        if not data:
            print("  UNRUNNABLE: every interaction dropped. Exit 2."); return 2

    from covalx.judge import Judge, build_prompt
    prompts, meta = [], []
    ks = set()
    for cid, iid, _pr, cands in data:
        cs = per_conv[cid] if per_conv is not None else crit
        ks.add(len(cs))
        for rid, text, score, chosen, _turn in cands:
            for j, c in enumerate(cs):
                prompts.append(build_prompt(c, text, max_reply=a.max_reply))
                meta.append(f"{cid}|{iid}|{rid}|{j}")
    print(f"  corpus     : {corpus.name}", flush=True)
    print(f"  criteria   : {sorted(ks)} per conversation "
          f"({'CONVERSATION-KEYED' if per_conv is not None else 'prompt-blind'})", flush=True)
    print(f"  convs      : {len({d[0] for d in data})}  interactions: {len(data)}", flush=True)
    print(f"  judge calls: {len(prompts):,}", flush=True)

    j = Judge(a.model, batch=a.batch)
    sat = j.score(prompts) if hasattr(j, "score") else j(prompts)

    tgt = [{"conv": cid, "inter": iid,
            "resp": [{"id": rid, "score": s, "chosen": ch, "len": len(t), "turn": tn}
                     for rid, t, s, ch, tn in cands]}
           for cid, iid, _pr, cands in data]
    prov = {"core": str(a.core), "corpus": str(corpus), "model": str(a.model),
            "batch": int(a.batch), "convs": int(a.convs), "seed": int(a.seed),
            "n_convs": len({d[0] for d in data}), "n_interactions": len(data),
            "n_calls": len(prompts),
            "producer": "corebench/judge_transport.py", "producer_sha256": PRODUCER_SHA256,
            # ⛔ THE HASH MUST COVER WHAT WAS ACTUALLY USED. Before this fix `criteria_sha256` hashed
            #    `crit`, which for a conversation-keyed core is merely the FIRST conversation's four
            #    lines -- so a 2,200-set arm would have been stamped as though it ran one set, and
            #    two different generated arms could carry the SAME hash. A provenance field that
            #    cannot distinguish the arms it stamps is worse than none: it looks like a check.
            "core_mode": "conversation_keyed" if per_conv is not None else "prompt_blind",
            "n_criteria": (sorted(ks) if per_conv is not None else len(crit)),
            "n_criterion_sets": (len(per_conv) if per_conv is not None else 1),
            "criteria_sha256": hashlib.sha256(json.dumps(
                {k: sorted(v) for k, v in sorted(per_conv.items())} if per_conv is not None
                else sorted(crit), sort_keys=True).encode()).hexdigest()}
    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out, meta=np.array(meta), sat=np.asarray(sat, np.float32),
                        targets=np.array(json.dumps(tgt)),
                        provenance=np.array(json.dumps(prov, sort_keys=True)))
    print(f"  wrote {out}  sha256[:12] "
          f"{hashlib.sha256(out.read_bytes()).hexdigest()[:12]}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
