#!/usr/bin/env python3
"""
corebench/generate_core.py -- the definition's last untested clause.

The definition says a core is a REWRITING, which permits criteria found NOWHERE in the
source rubric. Every candidate scored so far selects from coval_full, so nothing tests it.

⚠ THE GENERATOR MUST NOT SEE coval_full. If it does it will paraphrase, the criteria will be
traceable, and the round measures paraphrase quality instead of the clause. It sees the
CONVERSATION and the FOUR RESPONSES only. That is also a built-in leak detector: the
provenance family should come back near zero traceable, and if it does not, either the model
reconstructed the rubric from the responses -- which would be the more interesting result --
or I leaked it, which is a bug.

ESTIMAND        A1 of a generated k=4 core against topw_k4, paired over the same prompts.
SCOPE           population : 968 prompts    instrument : Qwen3.5-2B-Base, greedy
                baseline   : topw_k4        regime     : k=4, exact-class
WORLDS          A ties or beats topw_k4 -> the rewriting clause is vindicated: novel
                  criteria can preserve verdicts
                B loses separably -> the source rubric carries something generation cannot
                  reconstruct from the responses alone, and "rewriting" is descriptive of
                  what CoVal did rather than a licence
KILL            pre-registered: paired CI on (generated - topw). Below zero and excluding
                it -> world B.
POSITIVE CTRL   parse rate: the fraction of prompts yielding k>=1 usable criteria, reported
                before any score. A generator that fails to parse is not a finding about
                cores.
SHAM            generate from a DIFFERENT prompt's conversation, size- and compute-matched.
                Prompt-specific content must beat it, or the criteria are generic filler.
LEAK CHECK      provenance I1/I2/I4 on the generated core. Near zero is expected BY
                CONSTRUCTION; high values mean the rubric leaked or was reconstructed.
"""
from __future__ import annotations
import argparse, json, pathlib, sys, time
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
MODEL = "/mnt/e/data.ai-models.local-model-store.storage.xl.private.readonly/Qwen3.5-2B-Base"
K = 4

FEWSHOT = (
    "Write four short evaluation criteria for judging replies to a user message.\n"
    "Each criterion is one line, starts with '- ', and states a property a good reply has.\n\n"
    "User message: My landlord won't return my deposit.\n"
    "Criteria:\n"
    "- The reply explains the tenant's legal options concretely.\n"
    "- The reply avoids promising a specific legal outcome.\n"
    "- The reply suggests documenting communication in writing.\n"
    "- The reply recommends consulting a local tenancy service.\n\n"
)


def text_of(msgs, limit=900):
    out = []
    for m in msgs:
        c = m.get("content")
        if isinstance(c, list):
            c = " ".join(x.get("text", "") if isinstance(x, dict) else str(x) for x in c)
        out.append(str(c))
    return " ".join(out)[:limit]


def parse(gen):
    crit = []
    for line in gen.split("\n"):
        line = line.strip()
        if line.startswith("- ") and len(line) > 12:
            crit.append(line[2:].strip())
        elif crit and not line:
            break
    return crit[:K]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--sham", action="store_true",
                    help="generate from a DIFFERENT prompt's conversation")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--batch", type=int, default=16)
    # ⭐ ADDED 2026-08-04 (R433). REUSE, NOT REBUILD: the FEWSHOT, `parse`, the generation loop and
    #    the sham are unchanged and shared between corpora, so a difference between the two arms
    #    cannot be a difference between two generators. Only the LOADER is new, because
    #    `load_join` is hardcoded to the home release's two files.
    #    ⚠ On the second corpus the unit is the CONVERSATION, not the prompt: `judge_transport`
    #    keys satisfaction as `conv|inter|resp|j`, and clause ② speaks of a core generated from
    #    the conversation. Generating per interaction would silently answer a different question.
    ap.add_argument("--corpus", default="home", choices=("home", "second"))
    ap.add_argument("--second-path", default=str(ROOT / "data" / "utterances.jsonl"))
    ap.add_argument("--convs", type=int, default=2200)
    ap.add_argument("--seed", type=int, default=0)
    # ⭐ ADDED 2026-08-05 (R553). Register rows 3+4 were priced as "a generation round" for five
    # rounds; R549/R552 established the FIRST blocker is not compute but these two absent knobs.
    # Every default below reproduces the module constants EXACTLY, so an unflagged run is
    # byte-identical to every run before this edit -- that is the placebo the round tests.
    ap.add_argument("--model", default=MODEL,
                    help="generator checkpoint; default = the module constant, unchanged")
    ap.add_argument("--fewshot-file", default=None,
                    help="file whose contents replace FEWSHOT; default None = the constant")
    a = ap.parse_args()

    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    if a.corpus == "home":
        from covalx.judge import load_join
        joined = load_join(ROOT / "data" / "comparisons.jsonl",
                           ROOT / "data" / "conversation_rubrics.jsonl")
        items = [(pid, text_of(pr["prompt"]["messages"])) for pid, pr, _r in joined]
    else:
        # the SAME conversation sample judge_transport draws, so the generated core covers exactly
        # the interactions that will be scored -- a mismatch here would silently shrink the arm.
        # ⛔ THE SAMPLE MUST COME FROM THE JUDGE'S OWN SAMPLER, NOT FROM MATCHING TWO SEEDS.
        #    The first version drew 2,200 conversations from ALL 8,011 in the file. `load_second`
        #    draws from only those with a USABLE interaction (>=2 distinct scored responses), which
        #    is a smaller set -- so the same seed and the same count gave two DIFFERENT samples, and
        #    coverage came back 1,644/2,200 = 0.7473, below this round's own pre-registered 0.80
        #    gate, with 1,870 interactions dropped. The gate caught it, which is the gate working;
        #    lowering it would have been the move AMENDMENT 1 forbids.
        #    Importing the sampler makes alignment a property of the code rather than of my
        #    remembering to pass matching flags. Two producers that must agree on a population
        #    should share the function that defines it.
        sys.path.insert(0, str(ROOT / "corebench"))
        import judge_transport as JT
        data = JT.load_second(pathlib.Path(a.second_path), a.convs, a.seed)
        texts = {}
        for cid, _iid, prompt, _cands in data:
            if prompt:
                texts.setdefault(cid, [])
                if prompt not in texts[cid]:
                    texts[cid].append(prompt)
        items = [(c, " ".join(v)[:900]) for c, v in texts.items()]
        print(f"  corpus=second · conversations {len(items)} · unit = CONVERSATION · "
              f"sample taken FROM judge_transport.load_second (shared sampler)", flush=True)
    if a.limit:
        items = items[:a.limit]
    if a.sham:                              # SHAM: same generator, wrong conversation
        items = [(items[i][0], items[(i + 1) % len(items)][1]) for i in range(len(items))]

    fewshot = (pathlib.Path(a.fewshot_file).read_text() if a.fewshot_file else FEWSHOT)
    tok = AutoTokenizer.from_pretrained(a.model)
    tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16,
                                                 device_map="cuda")
    model.eval()

    out, t0 = {}, time.time()
    for i in range(0, len(items), a.batch):
        chunk = items[i:i + a.batch]
        prompts = [fewshot + f"User message: {c}\nCriteria:\n" for _p, c in chunk]
        enc = tok(prompts, return_tensors="pt", padding=True, truncation=True,
                  max_length=768).to("cuda")
        with torch.no_grad():
            g = model.generate(**enc, max_new_tokens=110, do_sample=False,
                               pad_token_id=tok.pad_token_id)
        for (pid, _c), row in zip(chunk, g):
            txt = tok.decode(row[enc["input_ids"].shape[1]:], skip_special_tokens=True)
            cs = parse(txt)
            if cs:
                out[pid] = cs
        if i % (a.batch * 20) == 0:
            print(f"  {i}/{len(items)}  parsed {len(out)}  {time.time()-t0:.0f}s", flush=True)

    p = pathlib.Path(a.out); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out))
    ks = [len(v) for v in out.values()]
    print(f"\n  PARSE RATE: {len(out)}/{len(items)} = {len(out)/len(items):.4f}")
    print(f"  mean k = {np.mean(ks):.2f}   wrote {p}   {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
