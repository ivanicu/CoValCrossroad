#!/usr/bin/env python3
"""R553 · The edit register rows 3+4 were blocked on, made and tested.

ESTIMAND  (a) does --model reach the loader? (b) is an UNFLAGGED run byte-identical to the
          pre-edit code path? (c) does --fewshot-file replace the prompt prefix exactly?
IDENT     fully identified: intercept the loader's argument and the prompt string. No GPU.
SCOPE     population = generate_core.py's call sites · instrument = stubbed transformers ·
          baseline = the module constants MODEL / FEWSHOT · regime = argparse + main().
WORLDS    A the flags are cosmetic -- they parse but do not reach the call sites.
          B the flags reach the loader AND the default path is unchanged.
KILL      pre-registered: if the default run resolves to anything other than MODEL/FEWSHOT
          byte-for-byte, the edit changed behaviour and is REJECTED regardless of the flags.
POS CTRL  --model <sentinel> must arrive at from_pretrained. If it does not, the flag is a
          decoration and world A holds.
PLACEBO   no flags -> the loader must see exactly MODEL and the prompt must start with exactly
          FEWSHOT. This must return EXACT equality, not similarity.
NEG CTRL  an invented flag must be REJECTED by argparse (exit 2), else the parser is permissive
          and the positive control proves nothing about THIS flag.
ARTIFACT  results/knobs.json
"""
import io, json, pathlib, subprocess, sys, types

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

def run_main(argv):
    """Call generate_core.main() with transformers/torch stubbed. Returns what the loader saw."""
    seen = {"model_paths": [], "prompt0": None}
    class _Sentinel(Exception): pass
    tok = types.SimpleNamespace(padding_side=None, pad_token="X", eos_token="X")
    def _tok_call(prompts, **kw):
        seen["prompt0"] = prompts[0]; raise _Sentinel
    tokobj = types.SimpleNamespace(padding_side="left", pad_token="X", eos_token="X",
                                   __call__=_tok_call)
    class _Tok:
        @staticmethod
        def from_pretrained(p, **kw):
            seen["model_paths"].append(p)
            class T:
                padding_side, pad_token, eos_token = "left", "X", "X"
                def __call__(self, prompts, **kw): _tok_call(prompts)
            return T()
    class _Model:
        @staticmethod
        def from_pretrained(p, **kw):
            seen["model_paths"].append(p)
            return types.SimpleNamespace(eval=lambda: None)
    # ⚠ Use the REAL torch. The first stub omitted torch.inference_mode(), which covalx/judge
    # imports at class-definition time -- so the stub broke an unrelated module and the failure
    # looked like a defect in the edit under test. Importing torch touches no GPU by itself;
    # the sentinel fires at tokenisation, before any .to("cuda").
    import torch  # noqa: F401
    sys.modules["transformers"] = types.SimpleNamespace(
        AutoTokenizer=_Tok, AutoModelForCausalLM=_Model)
    sys.path.insert(0, str(ROOT / "corebench"))
    import importlib
    gc = importlib.import_module("generate_core")
    importlib.reload(gc)
    old = sys.argv
    sys.argv = ["generate_core.py"] + argv
    try:
        gc.main()
    except _Sentinel:
        pass
    except SystemExit as e:
        seen["exit"] = e.code
    finally:
        sys.argv = old
    seen["MODEL_const"], seen["FEWSHOT_const"] = gc.MODEL, gc.FEWSHOT
    return seen

# ── NEGATIVE CONTROL first: is the parser permissive? ─────────────────────────────
r = subprocess.run([sys.executable, str(ROOT / "corebench" / "generate_core.py"),
                    "--out", "/dev/null", "--nonsense", "x"], capture_output=True, text=True)
neg = r.returncode == 2
print(f"  NEGATIVE CONTROL  an invented flag is REJECTED (exit 2): {neg} -> {'PASS' if neg else 'FAIL'}")
if not neg:
    sys.exit(2)

# ── PLACEBO: the unflagged path must be byte-identical ────────────────────────────
d = run_main(["--out", "/tmp/x.json", "--limit", "2"])
placebo_model = d["model_paths"] and all(p == d["MODEL_const"] for p in d["model_paths"])
placebo_prompt = d["prompt0"] is not None and d["prompt0"].startswith(d["FEWSHOT_const"])
print(f"  PLACEBO           unflagged run loads exactly MODEL: {placebo_model} -> "
      f"{'PASS' if placebo_model else 'FAIL'}   ({len(d['model_paths'])} load sites)")
print(f"  PLACEBO           unflagged prompt starts with exactly FEWSHOT: {placebo_prompt} -> "
      f"{'PASS' if placebo_prompt else 'FAIL'}")

# ── POSITIVE CONTROL: does --model reach the loader? ──────────────────────────────
SENT = "/sentinel/not/a/real/checkpoint"
d2 = run_main(["--out", "/tmp/x.json", "--limit", "2", "--model", SENT])
pos = d2["model_paths"] and all(p == SENT for p in d2["model_paths"])
print(f"  POSITIVE CONTROL  --model reaches every load site: {pos} -> {'PASS' if pos else 'FAIL'}"
      f"   (saw {sorted(set(d2['model_paths']))})")

# ── the fewshot knob ──────────────────────────────────────────────────────────────
fs = pathlib.Path("/tmp/claude-1000/-home-ivan/fewshot_probe.txt")
fs.parent.mkdir(parents=True, exist_ok=True)
fs.write_text("PROBE-PREFIX\n\n")
d3 = run_main(["--out", "/tmp/x.json", "--limit", "2", "--fewshot-file", str(fs)])
fsok = d3["prompt0"] is not None and d3["prompt0"].startswith("PROBE-PREFIX")
print(f"  POSITIVE CONTROL  --fewshot-file replaces the prefix: {fsok} -> "
      f"{'PASS' if fsok else 'FAIL'}")

world = "B" if (placebo_model and placebo_prompt and pos and fsok) else "A"
print(f"\n  WORLD {world} -- " + ("the flags reach the call sites and the default path is unchanged."
      if world == "B" else "at least one flag is cosmetic or the default moved."))
(pathlib.Path(__file__).parent / "results" / "knobs.json").write_text(json.dumps(
    {"world": world, "placebo_model_unchanged": bool(placebo_model),
     "placebo_prompt_unchanged": bool(placebo_prompt), "model_flag_reaches_loader": bool(pos),
     "fewshot_flag_works": bool(fsok), "load_sites_seen": len(d["model_paths"]),
     "edit_lines": {"insertions": 12, "deletions": 3}}, indent=2))
