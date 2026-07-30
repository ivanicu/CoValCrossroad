# r22_cross_family

**Every judge in this repository has been Qwen3.5. If the attribution is a
family artifact, everything built on it falls.**

r10 varied judge SIZE (2B vs 0.8B) and prompt TEMPLATE, and found the attribution
stable at 0.064 +- 0.017. It did not vary the model FAMILY, and that is the larger
assumption: all four numbers came from the same pretraining lineage, so a shared
inductive bias would show up as agreement rather than as an error.

Three genuinely different families are on this machine, from a sibling project:

    InternLM2ForCausalLM   internlm2-chat-1.8b
    Phi3ForCausalLM        phi-3.5-mini-instruct
    Qwen2ForCausalLM       qwen2.5-3b-instruct     (different generation, instruct)

against the reference Qwen3.5-2B-Base.

Each judge grades the same 300 prompts under three criterion sources -- own,
nearest-topic, random -- against the same REAL human rankings. No gold model.

PER-JUDGE POSITIVE CONTROL. A judge whose own-rubric arm cannot beat chance on
human rankings cannot be used to decompose anything, and its attribution is noise.
Any judge below 0.55 pairwise is reported and EXCLUDED from the summary, the same
rule that r19 had to apply retroactively.

Known confound, stated up front: the three new judges are instruction-tuned and the
reference is a base model, and all four are prompted in the same completion-style
few-shot format. A weak result from an instruct model in that format is ambiguous
between family and format, which is what the positive control is there to catch.
