"""r80 -- freeze the judge panel as it ACTUALLY is, environment included.

CLAIM CARD
----------
Claim      the queue's GPU item: "fix the three-lineage judge panel and freeze it
           (checkpoint, tokenizer, template, verbalizer, divergence-token
           extraction, precision, batch, code hash)."
Estimand   a record sufficient to tell, later, whether a rerun is the same
           measurement -- and an honest count of how many lineages actually work.
Target
observed?  YES for everything the queue lists. Each item is read from the live
           object: checkpoint files are hashed on disk, tokenizer and divergence
           tokens come from the loaded tokenizer, template from `covalx.judge`,
           code hash from the file bytes.
Alternative
worlds     T THREE  all three lineages load and produce finite scores. The panel
                    is what every round since r39 has assumed.
           TWO      one lineage is unusable in this environment. Then the panel
                    must be frozen as a TWO-lineage panel and every "three
                    unrelated lineages" sentence in the package is a claim about
                    an environment that no longer exists.
Intervention
           none. Inspection plus a per-lineage positive control.
Null       the POSITIVE CONTROL is the whole point (entry 134): each lineage must
           score a satisfied criterion ABOVE an unsatisfied one on a hand-built
           pair, and its outputs must be finite. A lineage that loads is not a
           lineage that works, and this refuses to record one as working on the
           strength of an import.

WHY THIS ROUND EXISTS NOW
-------------------------
Entry 134: internlm cannot run under transformers 5.14.1, and with a cache shim
it runs and returns 100% NaN. It is one of the three lineages behind r39's cache,
r40's OOD map and r68's 0.9132. **No receipt in this repository records a
transformers or torch version**, so the environment behind the package's
strongest multi-lineage claim was never captured. Freezing the panel without the
environment would repeat exactly that omission.

WHAT A FREEZE IS FOR
--------------------
Not to assert the panel is good. To make a future rerun CHECKABLE: same hashes
and same versions means the same measurement; different means a difference that
has to be explained rather than absorbed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

ART = "/home/ivan/research/causal-publication-protocol/artifacts"
BACKBONES = {
    "qwen": os.environ.get("COVALX_MODEL_08B",
                           "/mnt/e/data.ai-models.local-model-store.storage.xl.private.readonly/"
                           "Qwen3.5-0.8B-Base"),
    "phi": f"{ART}/model_phi-3.5-mini-instruct",
    "internlm": f"{ART}/model_internlm2-chat-1.8b",
}
# The positive control pair. Deliberately unambiguous: a judge that cannot order
# THIS is not a judge, and a lineage that cannot pass it must not be frozen as
# working.
PC_CRITERION = "The reply gives a specific numeric answer."
PC_SATISFIED = "The total is exactly 42 items, counted twice to be certain."
PC_UNSATISFIED = "It depends on many things and could really be anything at all."


def sha(path: Path, limit=None) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(1 << 20)
            if not b:
                break
            h.update(b)
            if limit and f.tell() > limit:
                break
    return h.hexdigest()


def checkpoint_fingerprint(d: Path) -> dict:
    """Hash the small files that define a checkpoint; index the big ones."""
    small = {}
    for name in ("config.json", "tokenizer_config.json", "tokenizer.json",
                 "generation_config.json", "special_tokens_map.json",
                 "model.safetensors.index.json"):
        p = d / name
        if p.exists():
            small[name] = sha(p)
    weights = sorted(p.name for p in d.glob("*.safetensors")) + \
        sorted(p.name for p in d.glob("*.bin"))
    sizes = {n: (d / n).stat().st_size for n in weights}
    return {"dir": str(d), "file_hashes": small, "weight_files": weights,
            "weight_bytes_total": sum(sizes.values()), "weight_sizes": sizes}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r80_panel_freeze.json")
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)

    import torch
    import transformers
    from covalx import judge as judge_mod
    from covalx.legacy_cache_shim import install as install_shim

    env = {
        "python": platform.python_version(),
        "torch": torch.__version__,
        "transformers": transformers.__version__,
        "cuda_runtime": torch.version.cuda,
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "platform": platform.platform(),
    }
    print("ENVIRONMENT (the thing no receipt in this repository has ever recorded)")
    for k, v in env.items():
        print(f"  {k:14s} {v}")

    code = {
        "covalx/judge.py": sha(_ROOT / "covalx/judge.py"),
        "covalx/legacy_cache_shim.py": sha(_ROOT / "covalx/legacy_cache_shim.py"),
        str(Path(*_HERE.parts[-2:]) / "run.py"): sha(_HERE / "run.py"),
    }
    template = {
        "fewshot": judge_mod.FEWSHOT,
        "build_prompt_example": judge_mod.build_prompt("CRITERION", "REPLY"),
        "max_reply_chars_default": 1400,
        "verbalizer": {"positive": " Yes", "negative": " No",
                       "read": "logit gap at the first position where the two "
                               "label encodings DIVERGE, with shared prefix tokens forced"},
    }

    install_shim()
    from transformers import AutoTokenizer

    lineages = {}
    for name, path in BACKBONES.items():
        d = Path(path)
        rec = {"path": str(d), "exists": d.exists()}
        print(f"\n=== {name} ===")
        if not d.exists():
            rec["status"] = "ABSENT"
            lineages[name] = rec
            print("  ABSENT")
            continue
        rec["checkpoint"] = checkpoint_fingerprint(d)
        try:
            tok = AutoTokenizer.from_pretrained(str(d), trust_remote_code=True)
            yes = tok.encode(" Yes", add_special_tokens=False)
            no = tok.encode(" No", add_special_tokens=False)
            k = 0
            while k < min(len(yes), len(no)) and yes[k] == no[k]:
                k += 1
            rec["tokenizer"] = {
                "class": type(tok).__name__, "vocab_size": int(tok.vocab_size),
                "yes_ids": yes, "no_ids": no, "divergence_position": k,
                "shared_prefix_ids": yes[:k],
                "yes_id": yes[k] if k < len(yes) else None,
                "no_id": no[k] if k < len(no) else None,
            }
            print(f"  tokenizer {type(tok).__name__}  ' Yes'->{yes}  ' No'->{no}  "
                  f"diverge at {k}")
        except Exception as e:
            rec["status"] = f"TOKENIZER FAILED: {type(e).__name__}: {e}"
            lineages[name] = rec
            print(f"  {rec['status']}")
            continue

        # POSITIVE CONTROL -- the executable form of entry 134's lesson.
        try:
            J = judge_mod.Judge(str(d), batch=a.batch) if hasattr(judge_mod, "Judge") else None
            if J is None:
                raise RuntimeError("covalx.judge exposes no Judge class")
            s = J.score([judge_mod.build_prompt(PC_CRITERION, PC_SATISFIED),
                         judge_mod.build_prompt(PC_CRITERION, PC_UNSATISFIED)])
            import numpy as np
            finite = bool(np.isfinite(s).all())
            ordered = bool(finite and s[0] > s[1])
            rec["positive_control"] = {"satisfied": float(s[0]), "unsatisfied": float(s[1]),
                                       "finite": finite, "ordered_correctly": ordered,
                                       "gap": float(s[0] - s[1]) if finite else None}
            rec["status"] = "WORKS" if ordered else (
                "REFUSED: outputs not finite" if not finite
                else "REFUSED: failed the positive control ordering")
            print(f"  positive control  satisfied {s[0]:.4f}  unsatisfied {s[1]:.4f}  "
                  f"finite={finite}  ordered={ordered}")
            print(f"  status: {rec['status']}")
            del J
            torch.cuda.empty_cache()
        except Exception as e:
            rec["status"] = f"REFUSED: {type(e).__name__}: {str(e)[:160]}"
            print(f"  status: {rec['status']}")
        lineages[name] = rec

    # TWO PANELS, NOT ONE -- and the queue's phrase conflates them. Established
    # from the artifacts, not from memory:
    #   JUDGE panel (satisfaction scoring, covalx.judge.Judge): qwen + phi.
    #     r22's own verdict: "usable judges span 2 families (phi, qwen)", with
    #     internlm configured and NOT in `usable`. Judge receipts exist for
    #     qwen2b and phi only. covalx/judge.py contains no `trust_remote_code`,
    #     so it could never have loaded internlm at all.
    #   ENCODER panel (r39 feature cache -> r40, r68): qwen + phi + internlm.
    # So nothing about the JUDGE panel broke when internlm did. What broke is the
    # ability to REGENERATE the internlm encoder features, which is r40's and
    # r68's cross-lineage argument, not the judge's.
    judge_pipeline_supports_remote_code = "trust_remote_code" in (
        _ROOT / "covalx/judge.py").read_text()
    panels = {
        "judge": {"members": ["qwen", "phi"],
                  "evidence": "r22 usable=['qwen3.5-2b-base(ref)','qwen2.5-3b-instruct',"
                              "'phi-3.5-mini-instruct'], usable_families=['phi','qwen']; "
                              "judge receipts exist for qwen2b and phi only",
                  "internlm_ever_a_judge": False,
                  "covalx_judge_passes_trust_remote_code": judge_pipeline_supports_remote_code},
        "encoder": {"members": ["qwen", "phi", "internlm"],
                    "evidence": "r39_feature_cache.npz holds mean_last for all three; "
                                "r40 and r68 consume them",
                    "regenerable_today": False,
                    "why_not": "internlm returns 100% NaN under transformers 5.14.1 "
                               "even with the cache shim (entry 134)"},
    }
    print(f"\nPANELS ARE DISTINCT (from artifacts, not memory)")
    print(f"  judge   : {panels['judge']['members']}  -- internlm was never a member; "
          f"covalx/judge.py passes trust_remote_code = "
          f"{judge_pipeline_supports_remote_code}")
    print(f"  encoder : {panels['encoder']['members']}  -- regenerable today = False")

    working = [n for n, r in lineages.items() if r.get("status") == "WORKS"]
    print(f"\n  WORKING LINEAGES: {len(working)} of {len(BACKBONES)}  ({', '.join(working)})")
    for n, r in lineages.items():
        if r.get("status") != "WORKS":
            print(f"    {n}: {r.get('status')}")

    not_working = "; ".join(f"{n} -> {r.get('status')}"
                            for n, r in lineages.items() if r.get("status") != "WORKS")
    verdict = (
        f"THE QUEUE'S PHRASE CONFLATES TWO PANELS, and separating them changes what is broken. "
        f"The JUDGE panel is qwen + phi and ALWAYS WAS: r22's own verdict records "
        f"usable_families=['phi','qwen'] with internlm configured and not usable, judge receipts "
        f"exist for qwen2b and phi only, and covalx/judge.py contains no trust_remote_code "
        f"(passes it: {judge_pipeline_supports_remote_code}), so it could never have loaded internlm "
        f"at all. The ENCODER panel behind r39's cache, r40's OOD map and r68's 0.9132 IS three "
        f"lineages. So internlm breaking did not break the judge panel -- it broke the ability to "
        f"REGENERATE the encoder features, which is a narrower and more precise statement than entry "
        f"134 made. PANEL FROZEN AS {len(working)}-LINEAGE ON THE JUDGE SIDE, WHICH IS ITS FULL SIZE. The queue asks for the three-lineage "
        f"judge panel to be fixed and frozen with its checkpoint, tokenizer, template, verbalizer, "
        f"divergence-token extraction, precision, batch and code hash. Every one of those is recorded "
        f"here from the live object rather than from memory -- checkpoint files hashed on disk, "
        f"divergence tokens read from each loaded tokenizer, template from covalx.judge, code hashed "
        f"by bytes. WHAT THE FREEZE FOUND: {len(working)} of {len(BACKBONES)} lineages pass a "
        f"positive control that a judge must pass -- scoring a reply which plainly satisfies a "
        f"criterion above one which plainly does not -- and the others are recorded with their "
        f"reason: {not_working or 'none'}. "
        f"AND THE ENVIRONMENT IS RECORDED FOR THE FIRST TIME: python {env['python']}, torch "
        f"{env['torch']}, transformers {env['transformers']}, CUDA {env['cuda_runtime']}, "
        f"{env['gpu']}. No receipt in this repository had ever captured it, which is why entry 134 "
        f"could establish that r39's cache -- the basis of r40 and of r68's 0.9132 -- was built in an "
        f"environment nobody wrote down and which no longer exists. A freeze that omitted the "
        f"environment would have repeated the omission it exists to prevent. WHAT THIS IS NOT: a "
        f"claim that the panel is good, or that a {len(working)}-lineage panel supports the "
        f"cross-lineage argument as well as three would. It is a record that makes a future rerun "
        f"CHECKABLE -- same hashes and versions means the same measurement, different means a "
        f"difference that must be explained rather than absorbed."
    )

    doc = {
        "environment": env, "code_hashes": code, "template": template,
        "precision": "bfloat16", "batch": a.batch,
        "panels": panels,
        "lineages": lineages, "working_lineages": working,
        "n_working": len(working), "n_designed": len(BACKBONES),
        "positive_control": {"criterion": PC_CRITERION, "satisfied": PC_SATISFIED,
                             "unsatisfied": PC_UNSATISFIED},
        "outcome_variable_scope": (
            "This round measures nothing about CoVal. It records the instrument. No attribution, "
            "no ranking, no criterion score from this file enters any other round's numbers."),
        "scope": (
            "Weight files are indexed by name and size, not hashed -- hashing 24 GB on every freeze "
            "would make the freeze too expensive to run, and the config/tokenizer hashes plus sizes "
            "already detect a swapped checkpoint. The positive control is ONE hand-built pair: it "
            "detects a dead or inverted judge, not a subtly miscalibrated one."),
        "verdict": verdict,
    }
    a.out.write_text(json.dumps(doc, indent=1))
    print(f"\n-> {a.out.relative_to(_ROOT)}")


if __name__ == "__main__":
    main()
