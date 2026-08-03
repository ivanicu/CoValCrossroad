# R16_minority_regret

**The fair arena for conflict-aware aggregation.**

r06 ranked aggregation rules by how well their core predicts the AGGREGATE human
ranking. That is the objective utility and majority rules are built to maximise,
so conflict-aware losing there says nothing — it was measured with the wrong ruler.

The claim conflict-aware actually makes is about the people a consensus core
leaves behind. So measure that: split each prompt's raters into blocs, and score
every rule by the satisfaction of its WORST-OFF bloc.

r01 is what licenses this: rater agreement persists across disjoint prompts and
survives removal of response style, so the blocs are a real structure in the data
rather than a partition I invented.

CPU only. No judge, no gold model — this reads the released signed ratings directly.
