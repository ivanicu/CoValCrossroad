# Stale, kept rather than deleted

`r79_d_internlm.npy` was written by the r79 run **before** the finite-value guard existed
(entry 134). Every value in it is NaN: internlm loads under the cache shim and returns
`hidden_states[1]` already NaN, so the array records a lineage that ran and did not work.

The current round **refuses** that lineage before computing `d`, so this file can no longer
be produced. It is moved here rather than deleted because a stale artifact that silently
disappears leaves no evidence that it once sat in `results/` looking like a result — which is
exactly how a superseded number gets quoted (entry 42, and r28's five metric files).

Do not read it as a measurement. It is the shape of a failure.
