Docstring-only edit (2026-07-28): the provenance caveat was upgraded after r48 showed the
seed/write-in split is an identification, not a heuristic. No executable line changed.

**Partially verified.** A full re-run needs `--with-shuffled`, which requires the GPU judge, and
the round's own guard correctly **refused to overwrite** the stored result with a shuffled-arm-free
partial one. Of the 11 numbers computable without the GPU arm, **9 are identical**; the two that
moved are the write-in bootstrap CI endpoints (0.56318→0.56353, 0.58645→0.58658, ~3e-4). Point
estimates are unchanged. The CI wobble is resampling variation — omitting the shuffled arm changes
how much of the RNG stream is consumed — not an effect of the docstring edit.

The 610 fields that exist only in the stored result are the shuffled-arm outputs, which this
CPU-only re-run cannot produce.
