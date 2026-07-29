# Stale, kept rather than deleted

`r79_d_internlm.npy` was written by the r79 run **before** the finite-value guard existed
(entry 134). Every value in it is NaN: internlm loads under the cache shim and returns
`hidden_states[1]` already NaN, so the array records a lineage that ran and did not work.

The current round **refuses** that lineage before computing `d`, so this file can no longer
be produced. It is moved here rather than deleted because a stale artifact that silently
disappears leaves no evidence that it once sat in `results/` looking like a result — which is
exactly how a superseded number gets quoted (entry 42, and r28's five metric files).

Do not read it as a measurement. It is the shape of a failure.

## The two internlm embedding caches, moved 2026-07-29

`r79_emb_crit_internlm.npy` (72 MB) and `r79_emb_resp_internlm.npy` (31 MB) are **entirely
NaN** — 26,611,712 values, every one. They are the cache written before the finite guard
existed.

They were **poison for r79's own reuse path**: `if cc.exists() and rc.exists(): C, R =
np.load(...)` would load them on the next run, and the guard would then report internlm as
"produced non-finite embeddings" — true, but attributing to the *model* what came from a
*cache*. A correct refusal for the wrong reason is still a wrong reason.

Moved rather than deleted, on the same principle as the d-array above.
