#!/usr/bin/env bash
# corebench/rebuild_selection_08b.sh -- rebuild every SELECTION arm under the 0.8B judge.
#
# ZERO judge calls. Each of these arms is a subset of `coval_full`, so once `coval_full` has been
# judged at 0.8B (sat08_full.npz, pueue 627) its satisfaction is already there. This is the same
# property select_core.py exploits to make the 2B selection arms free; nothing about it was
# specific to 2B.
#
# ⚠ TWO SPECIFICATIONS, BECAUSE FIVE ARMS CHANGE IDENTITY UNDER A NEW JUDGE.
# `topvar_k`, `topwvar_k`, `oracle_k`, `greedy_k` and `indep_k` consume SATISFACTION to choose
# their criteria. Re-run under 0.8B they select a DIFFERENT criterion set, so a `judge effect'
# measured on them would be a judge effect plus an arm change -- the confound R301 exists to
# avoid. The other rules (random_k, topw_k, topabs_k, full) select on the rubric's own importance
# weights or on nothing, and the two specifications coincide for them EXACTLY.
#
#   _08b   FROZEN   selection frozen at 2B, values from 0.8B. The estimand: what the JUDGE does,
#                   holding the arm fixed. PRIMARY.
#   _08bR  RERUN    the rule itself re-run under 0.8B. The alternative specification, published
#                   beside it. Emitted only for the five arms where it can differ.
set -u
cd "$(dirname "$0")/.."
PY=.venv/bin/python
F=corebench/results/sat08_full.npz
S=E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results/a04_full.npz
[ -s "$F" ] || { echo "!! $F absent -- 627 has not finished. Nothing rebuilt."; exit 2; }

frozen() { $PY corebench/select_core.py --full-npz "$F" --select-npz "$S" --tag-suffix _08b  "$@"; }
rerun()  { $PY corebench/select_core.py --full-npz "$F"                    --tag-suffix _08bR "$@"; }

echo "===== FROZEN (_08b): selection fixed at 2B, scored at 0.8B ====="
for k in 2 3 4 6 8 12; do
  for s in 0 1 2; do frozen --rule random_k --k $k --seed $s; done
done
for k in 1 2 3 4 6 8 12; do frozen --rule topw_k --k $k; done
for r in topabs_k topvar_k topwvar_k; do frozen --rule $r --k 4; done
frozen --rule oracle_k --k 4
for r in oracle_k greedy_k indep_k; do frozen --rule $r --k 4 --fit-parity 1; done

echo; echo "===== RERUN (_08bR): the rule itself re-run under 0.8B, 5 arms only ====="
for r in topvar_k topwvar_k; do rerun --rule $r --k 4; done
rerun --rule oracle_k --k 4
for r in greedy_k indep_k; do rerun --rule $r --k 4 --fit-parity 1; done

echo
echo "== frozen arms : $(ls corebench/results/sat_*_08b.npz  2>/dev/null | wc -l)"
echo "== rerun  arms : $(ls corebench/results/sat_*_08bR.npz 2>/dev/null | wc -l)"
