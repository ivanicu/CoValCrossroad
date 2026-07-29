"""Restore the two `DynamicCache` methods transformers 5.x removed.

WHY THIS EXISTS
---------------
`model_internlm2-chat-1.8b` ships its own `modeling_internlm2.py` (trust_remote_code)
which calls `DynamicCache.from_legacy_cache(...)` and `.to_legacy_cache()`. Both
were removed in transformers 5.x. Under transformers 5.14.1 the model raises
`AttributeError` on the first forward pass, so **internlm cannot run in this
environment at all**.

That matters well beyond one round. internlm is one of the three pretraining
lineages behind r39's feature cache, r40's OOD map, and r68's inter-lineage
reliability of **0.9132** -- the number that sets r40's detection floor at 0.188
and is the strongest refutation in the exhaustion ledger. The cache still
contains internlm because it was built when internlm still loaded; **no receipt
in this repository records the transformers or torch version of any run**, so the
environment that produced it was never captured and has since changed.

So the three-lineage argument was, until this shim, **not reproducible on this
machine** -- not wrong, but unrepeatable, which is a different and quieter kind
of failure.

WHAT THE SHIM DOES, AND WHY IT IS NOT A GUESS
----------------------------------------------
It reimplements the two methods against the structure actually present in
transformers 5.14.1, read off the object rather than assumed:

    DynamicCache().layers -> [DynamicLayer, ...]
    DynamicLayer.keys, DynamicLayer.values -> Tensor

`to_legacy_cache` returns the tuple-of-(key, value) form the old API returned;
`from_legacy_cache` rebuilds a DynamicCache from that form via the supported
`update()` path.

**It raises rather than returning an empty structure if the internals change.**
An empty cache would let the model run and produce plausible numbers from a
broken cache, which is the failure mode this repository has logged repeatedly:
a check that fails toward PASS. A loud AttributeError is the correct behaviour
for a shim whose assumption has expired.

⚠ IT RESTORES EXECUTION, NOT CORRECTNESS -- VERIFIED THE HARD WAY
------------------------------------------------------------------
With this shim installed, `model_internlm2-chat-1.8b` **loads and completes a
forward pass, and every value it returns is NaN.** Diagnosed layer by layer under
float32 with eager attention on a single unpadded input:

    hidden_states[0]  (embedding output)      finite
    hidden_states[1]  (after block 1)         ALREADY NaN

So the incompatibility is not the cache API alone; the vendored attention/MLP
code is broken against this transformers version in a way no shim reaches. The
shim turned an honest crash into a silent numerical corruption, which is strictly
worse -- a crash cannot be averaged into a result.

**Therefore: never treat "it loads" as "it works".** Any caller must check that
the outputs are finite before using them. r79 does, and refuses the lineage.
Restoring internlm properly needs a separate environment with a pinned older
transformers, not a patch to this one.

SCOPE
-----
Only for models whose vendored modeling code predates the removal. It does not
change any supported code path: transformers itself no longer calls these
methods. Verify with `python -m covalx.legacy_cache_shim`, which installs the
shim and round-trips a cache.
"""
from __future__ import annotations


def install() -> bool:
    """Add the removed methods if absent. Returns True if anything was patched."""
    from transformers.cache_utils import DynamicCache

    patched = False

    if not hasattr(DynamicCache, "to_legacy_cache"):
        def to_legacy_cache(self):
            layers = getattr(self, "layers", None)
            if layers is None:
                raise AttributeError(
                    "legacy_cache_shim: DynamicCache has no `.layers`; the internal "
                    "structure this shim was written against (transformers 5.14.1) has "
                    "changed. Refusing to return an empty cache, which would let a model "
                    "run on a broken one.")
            out = []
            for i, layer in enumerate(layers):
                if not (hasattr(layer, "keys") and hasattr(layer, "values")):
                    raise AttributeError(
                        f"legacy_cache_shim: layer {i} ({type(layer).__name__}) exposes no "
                        f"`.keys`/`.values`; refusing to guess.")
                if layer.keys is None or layer.values is None:
                    continue
                out.append((layer.keys, layer.values))
            return tuple(out)

        DynamicCache.to_legacy_cache = to_legacy_cache
        patched = True

    if not hasattr(DynamicCache, "from_legacy_cache"):
        @classmethod
        def from_legacy_cache(cls, past_key_values=None):
            cache = cls()
            if past_key_values:
                for i, (k, v) in enumerate(past_key_values):
                    cache.update(k, v, i)
            return cache

        DynamicCache.from_legacy_cache = from_legacy_cache
        patched = True

    return patched


if __name__ == "__main__":
    import torch
    from transformers.cache_utils import DynamicCache

    print("patched:", install())
    c = DynamicCache()
    k = torch.arange(24, dtype=torch.float32).reshape(1, 2, 3, 4)
    v = k * 2
    c.update(k, v, 0)
    legacy = c.to_legacy_cache()
    assert len(legacy) == 1, f"expected 1 layer, got {len(legacy)}"
    back = DynamicCache.from_legacy_cache(legacy)
    k2, v2 = back.to_legacy_cache()[0]
    assert torch.equal(k, k2) and torch.equal(v, v2), "round trip changed the tensors"
    print("round trip exact:", tuple(k2.shape), tuple(v2.shape))
    print("OK")
