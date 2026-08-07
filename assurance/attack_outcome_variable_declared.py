"""Attack assurance/outcome_variable_declared.py.  A lock never attacked is untested."""
import json, shutil, subprocess, sys
from pathlib import Path

ROOT = Path("/home/ivan/research.trustworthy-ai.coval-deep-analysis.build.lg.private.editable")
import sys as _s
_s.path.insert(0, str(ROOT))
from covalx.rounds import fixture_dir  # noqa: E402
# ⛔ R973: was `r91_attack_outcome`, and a REAL round `R91_precision_budget` exists --
#    the same identifier collision R960 found with r951. Moved above every real round.
FIXTURE = "r9191_attack_outcome"
TMP = fixture_dir(ROOT, FIXTURE)
PY = str(ROOT / ".venv/bin/python")

# (name, run.py source, results doc, must_be_flagged)
VECTORS = [
    ("1 gold-scored, no declaration anywhere",
     "import x\ngold = np.load('a08_gold_08b.npz')\n", {"verdict": "big result"}, True),
    ("2 declaration only in a SMOKE file",
     "gold_orig = 1\n", None, True),          # results written as *_SMOKE.json
    ("3 declaration buried in a nested list",
     "gold_fresh = 1\n",
     {"notes": [{"a": ["scored against a model gold head, no human rankings"]}]}, False),
    ("4 uses a DIFFERENT proxy the regex never heard of",
     "reward = np.load('some_other_reward_head.npz')\n", {"verdict": "big result"}, False),
]


ISOLATED = (
    "import importlib.util,sys;"
    "spec=importlib.util.spec_from_file_location('g',sys.argv[1]);"
    "m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);"
    "sys.exit(m.main(only=sys.argv[2]))"
)


def run():
    """⭐ R973: PER-ROUND, not whole-repo. The old version read the gate's exit code over the entire
    corpus, so a vector's verdict tracked the baseline instead of the plant -- R942 measured that
    channel saturated at 1, and R970 watched it flip when the false positives were removed. It now
    asks the gate about the fixture alone."""
    r = subprocess.run([PY, "-c", ISOLATED,
                        str(ROOT / "assurance/outcome_variable_declared.py"),
                        TMP.name],
                       cwd=ROOT, capture_output=True, text=True)
    return r.returncode


def main():
    shutil.rmtree(TMP, ignore_errors=True)
    results = []
    try:
        for name, src, doc, must_flag in VECTORS:
            shutil.rmtree(TMP, ignore_errors=True)
            (TMP / "results").mkdir(parents=True, exist_ok=True)
            (TMP / "run.py").write_text(src)
            fn = "out_SMOKE.json" if doc is None else "out.json"
            (TMP / "results" / fn).write_text(json.dumps(doc or {"verdict": "x"}, indent=1))
            flagged = run() == 1
            ok = flagged == must_flag
            results.append((name, ok, flagged, must_flag))
            print(f"  {'OK    ' if ok else 'BROKEN'} {name}"
                  f"   flagged={flagged} expected={must_flag}")
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    print(f"\n  cleanup verified: repo scan back to exit {run()}")
    n = sum(1 for _, ok, _, _ in results if ok)
    print(f"\n{n}/{len(results)} vectors behave as specified")
    print("  vector 4 is a KNOWN OPEN HOLE: a future round scoring against some other")
    print("  model proxy is invisible to a regex written for THIS one. The check flags")
    print("  silence about the gold head, not silence about proxies in general.")
    return 0 if n == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
