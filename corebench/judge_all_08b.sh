#!/usr/bin/env bash
# corebench/judge_all_08b.sh -- bring the JUDGE axis to full arm width at Qwen3.5-0.8B-Base.
#
# WHY THIS IS ONE RUN AND NOT THIRTY-EIGHT. My closing sentence last round read
# "judging the remaining 38 arms at 0.8B is about 40 minutes of GPU". That was costed by
# counting ARMS. But `select_core.py` states in its own docstring that a selection core is a
# SUBSET of `coval_full`, so its satisfaction is already in the full npz and costs
# "0 judge calls". That property is not specific to 2B: judge `coval_full` ONCE at 0.8B and
# every one of the 34 selection arms becomes free at 0.8B too.
#
# So the axis costs: 1 full judging + the arms that are GENERATED and therefore have no
# entry in any full npz -- `promptecho` (criteria echoed from the prompt) and the five shams
# (right criteria, WRONG prompt: those criterion x response pairs exist in no rubric).
#
#   full          59936 calls   -> unlocks 34 selection arms for free
#   full_sham     59936
#   topw_k4_sham  15488
#   gen_sham      15472
#   coval_core_sham 15312
#   promptecho     6368
#   promptecho_sham 6368
#   -------------------------
#   178880 calls. At the 2B rate (59936 in 1013 s, R04) that is ~50 min; 0.8B is smaller.
#
# Already at 0.8B and skipped: coval_core, gen, generic, random_k4_s0, topw_k4.
set -u
cd "$(dirname "$0")/.."
M=/mnt/e/data.ai-models.local-model-store.storage.xl.private.readonly/Qwen3.5-0.8B-Base
PY=.venv/bin/python

for tag in full full_sham topw_k4_sham gen_sham coval_core_sham promptecho promptecho_sham; do
  out=corebench/results/sat08_${tag}.npz
  if [ -s "$out" ]; then echo "== $tag  already present, skipping"; continue; fi
  echo "== $tag  -> $out"
  $PY corebench/judge_core.py --core corebench/results/core_${tag}.json \
      --model "$M" --out "$out" --batch 64 || echo "!! $tag FAILED (exit $?)"
done
echo "== done"; ls -la corebench/results/sat08_*.npz
