# North Star — a conservation law for normative information

*The research direction this repository is aimed at. Not a summary of what it has found; a statement
of what would count as having answered the question, and what would kill the framing.*

---

## The one sentence

> **Normative information is the set of source distinctions required to answer a declared family of
> normative queries. It is preserved when intervening on a distinction changes downstream behaviour
> in the predicted direction — and not when the downstream object merely agrees with it.**

Everything below is either a consequence of that sentence or an attempt to falsify it.

---

## Why there is no single number

A pipeline does not preserve "73.4% of normative information", and asking for that number is the
error this project made for sixty rounds.

What a norm carries depends on what the downstream system must be able to answer. Two normative
objects `N` and `N'` carry the same information *for a study* iff they are indistinguishable on
every query that study declares:

```
N ~_Q N'   ⟺   q(N, x) = q(N', x)   for all q ∈ Q, all x ∈ X
```

So normative information is the **equivalence class** `[N]_Q`, not the text. Declaring `Q` is not a
preliminary to the measurement — **declaring `Q` is most of the result**, and any framework that
hides its `Q` inside a supremum has moved the choice rather than made it.

**This is the first discipline: publish `Q` before measuring, and report what changes when `Q`
changes.**

---

## Three source objects, never one

Conflating these makes authorised compression indistinguishable from damage.

| | object | what loss here means |
|---|---|---|
| **Z** | the individual inputs `(N_1 … N_n)` — who said what, who dissented, who vetoed | aggregation *necessarily* loses some of this |
| **G** | `G = A(Z)`, the collective norm under a **publicly declared** rule `A` | loss here is a **social choice**, not an error — *if* `A` was declared |
| **S** | the authorised behaviour set, after legitimate expert enrichment | loss here is either domain necessity or machine distortion |

A change is only a **defect** if it is not licensed at the layer where it happened. Without the
three layers, "the pipeline lost information" cannot be distinguished from "the pipeline did what
it said it would do".

---

## The falsifiable core — three claims that can die

An atlas that always applies is not a theory. These are the load-bearing claims, each with the
observation that kills it.

### C1 · Preservation is causal, not correlational

A distinction reached the output iff **removing it changes the output**. Agreement is not
preservation: a participant whose view matches the majority scores perfect alignment while
contributing nothing, and a participant who moved the outcome may end up far from it.

> **Killed by:** influence (Shapley/Banzhaf over the aggregation) correlating ≈1.0 with alignment
> (cosine) across participants. Then the distinction is empty and sixty rounds of correlational
> measurement were fine.

### C2 · Type is not compressible to magnitude

A veto is not a large negative weight. A right is not a strong preference. An uncertainty is not a
mid-scale rating. **Type coercion is a loss that no similarity metric can see**, because the
compressed object can be arbitrarily close to the source in every continuous measure while
answering a different question.

> **Killed by:** a scalar-weighted rubric reproducing non-compensation behaviour — the thing a veto
> does and a weight cannot — as well as an explicitly typed one. Then type is decorative.

### C3 · Loss has shapes, and they do not average

Deletion, inversion, weakening, scope drift, exception erasure, provenance stripping, behavioural
inertness, synergy destruction. These are **different failures with different remedies**, and a
mean "retention score" over them is a number whose components point in different directions.

> **Killed by:** the shape indicators loading on one factor. If a single component explains them,
> one score was right and the taxonomy is ornament.

---

## The conservation law

The goal is not a score. It is a statement of **what may be compressed and what may not** — the
normative analogue of a conservation law, where the content is the partition, not the total.

| class | distinctions | status |
|---|---|---|
| **Must be causally preserved** | polarity · scope · non-compensability (veto) · exception conditions | intervening on these must move behaviour, in direction |
| **Recoverable is enough** | content wording · provenance *when not load-bearing for authority* · redundant restatements | must be decodable; need not steer |
| **Licensed to drop** | duplicates · criteria that are entailed by others · phrasing variance | only if the licence is declared at the layer where it happens |
| **Type errors when lost** | veto → scalar · uncertainty → certainty · right → preference · personal → world · expert constraint → public preference | not degradation — a category change, and no continuous metric detects it |

**The research programme is to fill this table empirically rather than by stipulation.** Every row
is currently an assertion. Each becomes a finding when an intervention shows the class behaves as
claimed.

---

## The probe problem — the largest loss, and it is invisible

A participant's normative disposition is a function over **all possible responses**. The
elicitation projects it onto **four points**.

Everything measurable in CoVal — every metric family, every loss shape, this entire document —
lives *after* that projection. Contrasts among four responses span three dimensions, so:

> **However many criteria people wrote and however many numbers they attached, at most three
> independent normative distinctions can reach a decision among four responses.** That is
> arithmetic, not a finding.

The projection is plausibly the largest single loss in the chain and **no measurement downstream of
it can see it**. It is why this repository's dimension-based measure read 3.00 everywhere including
its own null, and why that measure was retired as a check that cannot fail.

**Consequence:** loss must be measured as **angle and influence**, never as rank or dimension. You
cannot lose a dimension you never had; you can only be rotated away from what people wanted.

---

## What this data can and cannot support

Honest ladder. The middle column is why this repository will not answer the question alone.

| | measurable now | requires new elicitation |
|---|---|---|
| **source** | ratings and criteria *as written after seeing the responses* | response-blind norms, written before candidates exist |
| **type** | polarity from the sign of a weight | veto vs. weight, right vs. preference, declared uncertainty |
| **scope** | — | applicability conditions, exception clauses |
| **influence** | Shapley over the aggregation, on the shipped rankings | influence on *behaviour*, which needs a model |
| **behaviour** | the compiled standard's decision on four responses | a model trained under the standard, on fresh responses |
| **authority** | sole-authored criteria, via the rating-count signature | expert enrichment ledger, separated from public input |

**The chain terminates at the decision, not at behaviour.** `Y` — what a model does under this
standard — is not in the release and no arithmetic recovers it. Any end-to-end number quoted to `Y`
is fabricated.

---

## What the next elicitation must collect

Ordered by how much each unlocks, not by cost.

1. **Response-blind source norms** — written before candidates exist. Without this the source is
   already contaminated: criteria written after ranking partly describe the answer already chosen
   (measured here at +0.0478 on a same-texts comparison).
2. **Typed fields** — polarity, scope, exception, priority, non-compensability, uncertainty, as
   separate slots. A single −10..+10 scale forces every type into magnitude.
3. **Author witnesses** — a positive, a negative and a boundary example per criterion. Turns a
   criterion from a sentence into a testable predicate.
4. **A compilation receipt** — every merge, rewrite, delete and type conversion, with its source.
   Lineage is the field whose absence blocks the most questions here.
5. **Fresh responses** — the same standard applied to candidates nobody wrote criteria about. The
   only defence against candidate-set overfitting.
6. **Multiple executors** — the same norm given to several judges. Separates the norm from its
   reader.

---

## What would kill this framing entirely

Not "which claim is wrong" but "was the object wrong".

- **If influence tracks alignment**, preservation is correlational and C1 is decoration.
- **If typed and untyped rubrics behave identically under intervention**, the type ontology is a
  vocabulary rather than a structure.
- **If the loss shapes collapse to one factor**, the conservation table is a single scalar wearing
  a costume, and a retention score was right all along.
- **If a person's induced ordering is unstable across response sets**, then what was elicited is a
  property of the probe, not of the person, and *nothing* downstream is measuring values.

The fourth is the deepest and the cheapest to check.

---

## The discipline this comes from

Every line above exists because something in this repository failed:

- a dimension measure that read 3.00 including its null — *a check that cannot fail*
- an "information loss" reported as a cosine between a person's rubric and **their own** ranking,
  with the pipeline nowhere in it
- a Čech H¹ computed exactly, positive-controlled, and returning ≈0 — because the obstruction was
  never cohomological
- one prompt counted 929 times, producing a finding that had to be withdrawn, and then a
  *retraction whose stated mechanism was also wrong*

**The north star is not a target to hit. It is the shape of the question that survives after the
wrong versions have been killed** — and the count of wrong versions is in
[`RETRACTIONS.md`](RETRACTIONS.md), currently 235.
