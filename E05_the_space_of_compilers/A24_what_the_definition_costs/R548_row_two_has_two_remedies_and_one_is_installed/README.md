# R548 · Row 2 names two remedies and one is already installed

**Decision this makes safe:** what row 2 — now the cheapest *reachable* entry *(R547)* — actually costs.

Its remedy column reads **"quantisation, or offload"**. The cost column collapses both into
**"an install"**.

| path | packages | present |
|---|---|---|
| quantisation | `bitsandbytes`, `optimum`, `auto_gptq`, `awq` | **none** |
| **offload** | `accelerate` | ⭐ **YES** |

**WORLD B — the single label understates what is reachable.** Quantisation needs an install;
**offload does not.**

## Controls
- **Positive** — packages R540 used on this venv (`torch`, `transformers`) must resolve: both do.
  A prober that cannot see known packages cannot report an absence.
- **Negative** — an invented module must not resolve: it doesn't.

⚠ **NOT measured: whether offload is fast enough** for 15,472 judge calls. That needs a 7B offloaded
run through pueue — **a measurement, not an install.** ⭐ **R540–R542 cost three rounds to establish
that modelling a runtime is worthless, so this round does not model it.**

⚠ **An environment fact — it expires at the next infra event.**
