/* Every string the page shows, in both languages.
   Kept in one file so a sentence has ONE home and the two versions cannot drift apart
   silently -- if a key is missing here the page prints the key, loudly, rather than
   falling back to English and looking translated when it is not. */
const I18N = {

/* ---- chrome ---- */
"eyebrow":            ["every prompt · every criterion · every round", "每一条问题 · 每一条准则 · 每一轮实验"],
"title":              ["CoVal Crossroad — <em>the whole object</em>", "CoVal Crossroad — <em>对象的全部</em>"],
"lede":               ["Every figure was recomputed from the release and this repository by <code>atlas/extract.py</code>, <code>extract_corpus.py</code> and <code>add_geometry.py</code>. Nothing is typed by hand. <b>Click any point to read that prompt in full</b> — its four answers, its rubric with every raw score, and all sixteen annotators' three rankings with their written reasons.",
                       "页面上每一个数字都由 <code>atlas/extract.py</code>、<code>extract_corpus.py</code>、<code>add_geometry.py</code> 从 release 和本仓库重新算出。没有一个是手打的。<b>点任意一点即可读完整条 prompt</b> —— 它的四个回答、带每个人原始打分的完整准则表、以及全部十六位标注者的三套排序和他们写下的理由。"],

/* ---- counts ---- */
"c.prompts":   ["prompts","问题"],
"c.answers":   ["candidate answers","候选回答"],
"c.annot":     ["annotators","标注者"],
"c.criteria":  ["criteria","准则"],
"c.world":     ["world rankings","world 排序"],
"c.rat":       ["rationales","书面理由"],
"c.neigh":     ["neighbourhoods","语义邻域"],
"c.rounds":    ["rounds","实验轮次"],
"c.commits":   ["commits","提交"],

/* ---- 01 ---- */
"s1.h":   ["The corpus, as a cloud","语料,作为一片点云"],
"s1.sub": ["One point per prompt, <b id='ncloud'></b> of them. Position is a t-SNE of Qwen3.5-0.8B mean-pooled embeddings — <span class='hot'>semantic neighbours land near each other</span>. Every other channel is switchable below. Hover to read the prompt; click to open it.",
           "一条 prompt 一个点,共 <b id='ncloud'></b> 条。位置是 Qwen3.5-0.8B 均值池化嵌入的 t-SNE —— <span class='hot'>语义相近的落在一起</span>。其余通道都可在下方切换。悬停读题,点击展开。"],
"lbl.proj": ["projection","投影"],
"lbl.hue":  ["colour","颜色"],
"lbl.size": ["size","大小"],
"lbl.find": ["find","搜索"],
"ph.find":  ["substring of the prompt…","输入 prompt 里的任意片段…"],

/* ---- hue / size channels ---- */
"h.cluster":     ["neighbourhood","语义邻域"],
"h.consensus":   ["consensus strength","共识强度"],
"h.split_rate":  ["personal≠world rate","personal≠world 比例"],
"h.negshare":    ["share of w<0 criteria","负权准则占比"],
"h.tie":         ["modal tie","众数平局"],
"h.has_rubric":  ["has a rubric","是否有 rubric"],
"h.n_ann":       ["annotators","标注者数"],
"z.n_crit":      ["criteria","准则数"],
"z.n_ann":       ["annotators","标注者数"],
"z.len_user":    ["prompt length","题目长度"],
"z.n_unacc":     ["unacceptable flags","unacceptable 标记数"],
"z.consensus":   ["consensus","共识强度"],

/* ---- projections ---- */
"p.tsne":  ["t-SNE","t-SNE"],
"p.umap":  ["UMAP","UMAP"],
"p.pca":   ["PCA","PCA 主成分"],
"p.mds":   ["MDS","MDS 多维标度"],
"p.grid":  ["sorted lattice","排序点阵"],
"p.swarm": ["beeswarm","蜂群图"],
"pn.tsne": ["neighbourhoods preserved, distances NOT — read near/far only","保住邻域,不保距离 —— 只能读「近/远」,不能读数值"],
"pn.umap": ["n_neighbors 25, min_dist 0.12 — more global structure than t-SNE, still not a metric","n_neighbors 25, min_dist 0.12 —— 比 t-SNE 多保住全局结构,但仍不是度量空间"],
"pn.pca":  ["linear, distances ARE meaningful; these 2 axes hold {V} of the variance","线性投影,距离是真的;这两根轴只装下 {V} 的方差"],
"pn.mds":  ["700 prompts embedded by stress majorisation; the rest snapped to their nearest neighbour — stated, not hidden","700 条用应力最小化真嵌入,其余贴到最近邻 —— 写出来,没有藏"],
"pn.grid": ["geometry discarded; ZERO occlusion and position exactly decodable — sorted by neighbourhood, then criteria count","几何全部丢弃;换来零遮挡、位置可精确解码 —— 按邻域排序,再按准则数"],
"pn.swarm":["x = consensus strength, y = collision-avoiding jitter only — a 1-D distribution with every point still separate","x = 共识强度,y 只是避让抖动 —— 一维分布,但每个点仍然分得开"],

"sil": ["<b>⚠ The structure is weak, and is shown rather than asserted.</b> Best silhouette over k∈{8,12,18,24} on the embeddings is <b>{A}</b> (at k=8); the best TF-IDF partition managed <b>{B}</b>. Both are far under the ≈0.25 at which a partition is normally called clean. <b>k=12 is a choice.</b> The cloud is drawn ungated so the separation you see is the separation there is.",
        "<b>⚠ 结构很弱,而且是展示出来的,不是宣称的。</b>嵌入空间上 k∈{8,12,18,24} 的最佳轮廓系数是 <b>{A}</b>(k=8 时);TF-IDF 最好只到 <b>{B}</b>。「干净划分」通常的门槛约 0.25,两者都远低于此。<b>k=12 是一个选择。</b>点云不做任何筛选地画出来,所以你看到的分离度就是实际存在的分离度。"],

/* ---- 01b layers ---- */
"s1b.h":   ["The audit, as layers over the corpus","审计结果,作为覆盖在语料上的图层"],
"s1b.sub": ["Every finding of the campaign, re-expressed as <b>the set of prompts it is about</b>, and painted onto the same cloud. <span class='hot'>z compares the layer's mean pairwise distance against 60 size-matched random draws</span> — near zero means the finding is spread uniformly and is <b>not</b> a property of any domain; strongly negative means it concentrates somewhere real. Click a layer to paint it; click again to clear.",
            "把这场 campaign 的每一条结论,改写成<b>它所关于的那批 prompt 的集合</b>,画到同一片点云上。<span class='hot'>z 是该图层的平均两两距离对比 60 次同规模随机抽样</span> —— 接近 0 表示这条结论均匀铺满全语料,<b>不是</b>任何领域的属性;强负值表示它真的聚集在某处。点一下上色,再点一下清除。"],
"lt.layer":  ["layer","图层"],
"lt.n":      ["n","条数"],
"lt.share":  ["share","占比"],
"lt.z":      ["z vs random","z(对比随机)"],
"lt.conc":   ["concentrated in","集中在"],
"lt.what":   ["what it is","这是什么"],
"v.CONC":    ["CONCENTRATED","高度聚集"],
"v.OVER":    ["over-dispersed","过度弥散"],
"v.UNI":     ["uniform","均匀"],
"lay.note":  ["Each layer is a finding re-expressed as a set of prompts. `z` compares the layer's mean pairwise distance in the t-SNE view against 60 size-matched random draws: z near 0 means the finding is spread uniformly over the corpus and is NOT a property of any domain; strongly negative means it concentrates.",
              "每个图层都是一条结论被改写成一批 prompt。`z` 把该图层在 t-SNE 视图中的平均两两距离,对比 60 次同规模随机抽样:z 接近 0 表示这条结论均匀分布在全语料上,不是任何领域的属性;强负值表示它确实聚集。"],
"lay.detail":["Mean pairwise distance in the t-SNE view is <b>{O}</b> against a size-matched random mean of <b>{N}</b> (sd {S}) — <b style='color:{C}'>z = {Z}</b>.",
              "在 t-SNE 视图中的平均两两距离为 <b>{O}</b>,同规模随机抽样均值为 <b>{N}</b>(标准差 {S}) —— <b style='color:{C}'>z = {Z}</b>。"],
"lay.conc":  ["This finding is <b>not evenly spread</b>: it lives somewhere in particular, and the cloud shows where.",
              "这条结论<b>不是均匀分布的</b>:它确实住在某个特定的地方,点云把那个地方指出来了。"],
"lay.over":  ["Spread <b>wider</b> than random — the finding avoids clustering.",
              "比随机<b>还要散</b> —— 这条结论刻意避开了聚集。"],
"lay.uni":   ["Statistically indistinguishable from a random subset of the corpus — <b>the domain is not the variable here.</b>",
              "在统计上与语料的随机子集无法区分 —— <b>在这里,领域不是那个变量。</b>"],

/* ---- 02 ---- */
"s2.h":   ["The twelve neighbourhoods, and how they differ","十二个语义邻域,以及它们的差别"],
"s2.sub": ["A cluster's name is the terms that most <b>separate</b> it from the rest of the corpus — computed, never assigned. The bars compare each neighbourhood against the corpus mean on seven measured axes, so <span class='hot'>a domain's character is a shape, not a label</span>.",
           "一个邻域的名字,是把它和语料其余部分<b>分隔开</b>得最厉害的那些词 —— 算出来的,不是指定的。条形图把每个邻域在七根实测轴上和全语料均值相比,所以<span class='hot'>一个领域的性格是一个形状,不是一个标签</span>。"],
"ax.crit":    ["criteria","准则数"],
"ax.ann":     ["annotators","标注者数"],
"ax.cons":    ["consensus","共识强度"],
"ax.split":   ["personal≠world","personal≠world"],
"ax.neg":     ["w<0 share","负权占比"],
"ax.tie":     ["modal ties","众数平局率"],
"ax.unacc":   ["any unacceptable","出现 unacceptable"],
"ax.len":     ["prompt length (chars)","题目长度(字符)"],
"ax.turns":   ["turns in the prompt","题目轮数"],
"btn.iso":    ["isolate in the cloud","在点云中单独显示"],
"cc.prompts": ["prompts","条 prompt"],

/* ---- 03 ---- */
"s3.h":   ["Do the domains behave differently?","这些领域的行为真的不同吗?"],
"s3.sub": ["Each row is one measured property; each mark is one neighbourhood. If domain mattered, the marks would spread. <span class='hot'>Where they collapse onto the corpus mean, the domain is not the variable.</span>",
           "每一行是一个实测属性,每一个点是一个邻域。如果领域真的起作用,这些点就会散开。<span class='hot'>凡是塌到全语料均值上的那一行,领域就不是那个变量。</span>"],
"s3.foot":["dashed line = corpus mean · % = (max−min)/mean, i.e. how much the domain moves this quantity",
           "虚线 = 全语料均值 · 百分数 =(最大−最小)/均值,即领域把这个量推动了多少"],
"s3.spread":["spread","跨度"],
"s3.arm.h":["and how each construction scores, by neighbourhood","以及每种构造在各邻域上的成绩"],
"s3.arm.c":["neighbourhood","邻域"],

/* ---- 04 ---- */
"s4.h":   ["One point, fully opened","把一个点完全打开"],
"s4.sub": ["The same object the drawer shows, printed here for the worked prompt. Four answers to <em>\"help me make it sting\"</em>: <b>A</b> obeys, <b>D</b> refuses politely, and thirteen of fourteen people put A last.",
           "抽屉里显示的同一个对象,这里用示例 prompt 印出来。对<em>「帮我写得扎心点」</em>的四个回答:<b>A</b> 照做,<b>D</b> 客气地不照做 —— 十四个人里有十三个把 A 排在最后。"],
"s4.p":   ["the prompt","题目"],

/* ---- 05 ---- */
"s5.h":   ["What each annotator did, in order","每个标注者做了什么,按顺序"],
"s5.sub": ["The order is the finding. <span class='hot'>Rankings come first; the criteria are written last</span> — so a criterion is not independent evidence, it is the same person's standard, authored after they had already decided. <b id='ovl'></b> of the people who scored a prompt's criteria also ranked it.",
           "顺序本身就是结论。<span class='hot'>先排序,最后才写准则</span> —— 所以准则不是独立证据,它是同一个人在已经做完判断之后写下的标准。给某条 prompt 的准则打分的人里,<b id='ovl'></b> 同时也给这条 prompt 排过序。"],
"f.s1":   ["unacceptable check","unacceptable 检查"],
"f.s1d":  ["which answers must be blocked","哪些回答必须封杀"],
"f.s2":   ["personal ranking","personal 排序"],
"f.s2d":  ["which you prefer, + written reason","你自己更喜欢哪个,+ 书面理由"],
"f.s3":   ["world ranking","world 排序"],
"f.s3d":  ["best for the world, + reason","对世界最好是哪个,+ 理由"],
"f.s4":   ["prompt ratings","题目层面评分"],
"f.s4d":  ["importance · representativeness · subjectivity","重要性 · 典型性 · 主观性"],
"f.s5":   ["write a criterion","写一条准则"],
"f.s5d":  ["a signed rule, −10…+10","一条带符号的规则,−10…+10"],
"f.tgt":  ["THE TARGET","这是标签"],
"f.feat": ["THE FEATURES","这是特征"],
"f.arrow":["the feature is authored AFTER the label — by the same person","特征是在标签之后写的 —— 而且是同一个人写的"],

/* ---- 06 ---- */
"s6.h":   ["The criterion field","准则场"],
"s6.sub": ["A criterion is a sentence about <b>any</b> answer, with a signed weight −10…+10. Annotators were trained to supply <b>both polarities</b>.",
           "一条准则是关于<b>任何</b>回答的一句话,带 −10…+10 的签名权重。标注者受过训练,被要求<b>正负都要写</b>。"],
"s6.c1":  ["weight × satisfaction spread — the worked prompt","权重 × 满足度方差 —— 示例 prompt"],
"s6.c2":  ["how many people scored each criterion — whole release","每条准则被多少人打过分 —— 全 release"],
"s6.c3":  ["the criteria, and the raw scores behind each weight","准则全表,以及每个权重背后的原始打分"],
"s6.x":   ["annotator weight  w","标注者权重 w"],
"s6.y1":  ["satisfaction","满足度"],
"s6.y2":  ["spread","方差"],
"s6.h1":  ["{N} criteria scored by exactly one person","{N} 条准则只有一个人打过分"],
"s6.h2":  ["{P} of the release","占全 release 的 {P}"],
"s6.note":["{P} of criteria are sign-contested — some annotators gave the same sentence a positive weight, others negative. The mean flattens that.",
           "{P} 的准则符号有争议 —— 同一句话有人给正分有人给负分。取平均把这件事压平了。"],

/* ---- 07 ---- */
"s7.h":   ["The machine that reads them","读它们的那台机器"],
"s7.sub": ["One yes/no question per (criterion × response). Nothing sampled — two logits at the final position. <b id='njudge'></b> such calls stand behind this page.",
           "每一对(准则 × 回答)问一个是非题。不采样 —— 只读最后位置上的两个 logit。这个页面背后有 <b id='njudge'></b> 次这样的调用。"],
"s7.c1":  ["the literal prompt sent to the judge","送进 judge 的完整原文"],
"s7.c2":  ["and the whole scoring rule","以及全部的打分规则"],
"s7.warn":["<b>⚠ There is no <span class='m'>w</span> in that sum.</b> Satisfying a criterion the annotators scored −10 <em>adds</em> exactly as much as one they scored +10.",
           "<b>⚠ 那个求和里没有 <span class='m'>w</span>。</b>满足一条标注者打了 −10 的准则,<em>加分</em>和满足一条 +10 的一模一样。"],
"s7.f":   ["hit       = how many of those six match the human modal class",
           "hit       = 这六个里有几个和人类众数一致"],

/* ---- 08 ---- */
"s8.h":   ["Ten ways to go from full to core","从 full 到 core 的十种走法"],
"s8.sub": ["Pick a rule; see what it selects and what it costs. Humans put <b>D &gt; B &gt; C &gt; A</b>.",
           "选一个规则,看它挑了什么、代价是什么。人类的排序是 <b>D &gt; B &gt; C &gt; A</b>。"],
"s8.c1":  ["selected criteria","被选中的准则"],
"s8.c2":  ["resulting totals y, and the verdict","得到的总分 y,以及判决"],
"s8.c3":  ["all ten, side by side","十种并排"],
"s8.mo":  ["machine order","机器排序"],
"s8.ho":  ["humans","人类"],
"s8.rw":  ["coval_core is a REWRITE, not a subset — judged from its own npz, no index list.","coval_core 是重写,不是子集 —— 用它自己的 npz 打分,没有索引列表。"],
"s8.nsel":["{K} criteria · {N} with w<0","{K} 条准则 · 其中 {N} 条 w<0"],
"th.constr":["construction","构造"],
"th.picked":["picked","选中"],
"th.hit":   ["hit","命中"],
"th.crit":  ["criterion","准则"],
"th.arm":   ["arm","arm"],
"th.n":     ["n","n"],

/* ---- 09 ---- */
"s9.h":   ["Why the good ones are good","好的为什么好"],
"s9.sub": ["Across all <b id='nmech'></b> prompts, agreement runs almost exactly <b>backwards</b> to how many negative-weight criteria a rule admits.",
           "在全部 <b id='nmech'></b> 条 prompt 上,命中率和一个规则放进来的负权准则数量几乎<b>完全反序</b>。"],
"s9.c1":  ["agreement vs. share of selected criteria with w < 0","命中率 vs 选中准则里 w < 0 的占比"],
"s9.c2":  ["and what happens if the sum is simply given the sign back","以及,如果直接把符号还给求和会怎样"],
"s9.x":   ["share of selected criteria with w < 0","选中准则里 w < 0 的占比"],
"s9.y":   ["agreement","命中率"],
"s9.prov":["Statistic: per-prompt mean pairwise agreement. <b style='color:var(--red)'>Not the campaign's A2</b> — not comparable to the leaderboard below.",
           "统计量:逐 prompt 的平均两两命中率。<b style='color:var(--red)'>不是 campaign 的 A2</b> —— 不能和下面的排行榜直接对照。"],
"s9.note":["<b>The decomposition.</b> <code>topw_k4</code> beats <code>topabs_k4</code> by <b>{D1}</b> against MDE {M1} — <b>{R}×</b>. What ordering by magnitude adds beyond merely excluding w&lt;0 is <b>{D2}</b> against MDE {M2} — resolved, but the smaller half. <b style='color:var(--gold)'>And giving the sum its signs back beats every selection rule without selecting anything.</b>",
           "<b>分解。</b><code>topw_k4</code> 比 <code>topabs_k4</code> 高 <b>{D1}</b>,对应 MDE {M1} —— <b>{R} 倍</b>。而「按大小排序」在「仅仅排除 w&lt;0」之外多贡献的部分是 <b>{D2}</b>,对应 MDE {M2} —— 可分辨,但是较小的那一半。<b style='color:var(--gold)'>而把符号还给求和,不挑任何东西就赢过了全部选择规则。</b>"],

/* ---- 10 ---- */
"s10.h":  ["The arm × metric hologram","arm × 指标 全息图"],
"s10.sub":["<b id='nlb'></b> arms × <b id='nmet'></b> metrics, verbatim from the committed leaderboard. Shade is the cell's position between that metric's min and max across arms. Hover for the raw value.",
           "<b id='nlb'></b> 个 arm × <b id='nmet'></b> 个指标,原样取自已提交的排行榜。深浅是该格在这个指标全部 arm 的最小值与最大值之间的位置。悬停看原始数值。"],
"s10.warn":["<b>⚠ Two arms named <code>r</code> and <code>t</code></b> carry full metric rows and appear in no round's documentation. Shown as found.",
            "<b>⚠ 有两个叫 <code>r</code> 和 <code>t</code> 的 arm</b>,带着完整的指标行,却不出现在任何一轮的文档里。原样展示,没有清洗。"],

/* ---- 11 ---- */
"s11.h":  ["The campaign, as its own cloud","这场 campaign,作为它自己的点云"],
"s11.sub":["<b id='nround'></b> rounds · <b id='narc'></b> arcs · <b id='nep'></b> epochs. Each mark is one round in order; height is persisted artifacts, faded means no README was written. Hover for the title.",
           "<b id='nround'></b> 轮 · <b id='narc'></b> 个 arc · <b id='nep'></b> 个 epoch。每一根是一轮,按顺序排;高度是留下的产物数量,变淡表示没写 README。悬停看标题。"],
"s11.foot":["each mark = one round, in order · height = persisted artifacts · faded = no README · ticks = arc boundaries",
            "每一根 = 一轮,按顺序 · 高度 = 留下的产物 · 变淡 = 没写 README · 刻度 = arc 边界"],
"s11.c1": ["rounds per arc","每个 arc 的轮数"],
"s11.c2": ["rounds that left no README","没留下 README 的轮次"],
"s11.d1": ["code + README","有代码 + 有 README"],
"s11.d2": ["code, no README","有代码,没 README"],
"s11.d3": ["{N} rounds ran code and left no README — the update happened, the writing did not.",
           "{N} 轮跑了代码却没留下 README —— 认知更新发生了,书写没有。"],
"s11.d4": ["{N} rounds carry no run.py.","{N} 轮没有 run.py。"],
"s11.rounds":["rounds","轮"],
"s11.art": ["artifacts","个产物"],
"s11.nord":["no README","无 README"],
"s11.nrun":["no run.py","无 run.py"],

/* ---- 12 ---- */
"s12.h":  ["What was shipped and never read","发布了、却从没被读过的东西"],
"s12.sub":["Every field in the release against the number of <code>*.py</code> files that mention it. <span class='hot'>Zero means the campaign never opened it.</span>",
           "release 里的每一个字段,对上本仓库中提到它的 <code>*.py</code> 文件数。<span class='hot'>零表示这场 campaign 从没打开过它。</span>"],
"s12.c1": ["field → files that touch it","字段 → 碰过它的文件数"],
"s12.c2": ["the largest unread object: OpenAI's own moderation scores","最大的未读对象:OpenAI 自己的 moderation 打分"],
"s12.prov":["{N} rows · {F} flagged ({P}) · read by 0 files.","{N} 行 · {F} 条被标记({P})· 被 0 个文件读取过。"],

/* ---- 13 ---- */
"s13.h":  ["Completeness ledger","完整性账本"],
"s13.sub":["A visualisation that will not state its own completeness is asserting it.",
           "一个不肯说出自己完整性的可视化,是在断言它。"],
"th.qty": ["quantity","量"],
"th.chan":["channel","通道"],
"th.occ": ["occlusion","遮挡"],
"th.res": ["recoverable resolution","可解码分辨率"],

/* ---- drawer ---- */
"d.close":  ["close ✕","关闭 ✕"],
"d.loading":["loading…","加载中…"],
"d.prompt": ["the prompt","题目"],
"d.four":   ["the four candidate answers","四个候选回答"],
"d.rubric": ["the rubric — coval_full, with every raw score","准则表 —— coval_full,含每一个原始打分"],
"d.core":   ["coval_core — the released 4, LM-distilled","coval_core —— 官方发布的 4 条,LM 蒸馏"],
"d.verd":   ["what each construction scored on this prompt","每种构造在这条 prompt 上的成绩"],
"d.rate":   ["prompt-level ratings","题目层面评分"],
"d.world":  ["the world rankings people gave","人们给出的 world 排序"],
"d.pers":   ["the personal rankings — same people, different question","personal 排序 —— 同一批人,不同的问题"],
"d.unacc":  ["unacceptable flags","unacceptable 标记"],
"d.every":  ["every annotator, verbatim — {N} people","全部标注者,逐字 —— {N} 人"],
"d.neigh":  ["neighbourhood","语义邻域"],
"d.nann":   ["annotators","标注者"],
"d.ncrit":  ["criteria","准则"],
"d.turns":  ["turns","轮数"],
"d.modal":  ["human modal class","人类众数类"],
"d.tie":    ["⚠ MODAL TIE — broken by file order","⚠ 众数平局 —— 靠文件顺序决出"],
"d.cons":   ["consensus strength","共识强度"],
"d.split":  ["personal ≠ world","personal ≠ world"],
"d.of":     ["of","/"],
"d.infull": ["IN full","在 full 里"],
"d.notin":  ["NOT in full","不在 full 里"],
"d.prior":  ["[prior assistant turn]","[前序 assistant 轮]"],
"d.dev":    ["[developer]","[developer]"],
"d.split_b":["SPLIT","分裂"],
"d.wworld": ["world:","world:"],
"d.wpers":  ["personal:","personal:"],
"d.wunacc": ["unacceptable:","unacceptable:"],
"d.imp":    ["importance","重要性"],
"d.rep":    ["representativeness","典型性"],
"d.subj":   ["subjectivity","主观性"],

/* ---- misc ---- */
"cloudprov":["{S} of {N} shown · {P} · colour = {H} · size = {Z}","显示 {S} / {N} · {P} · 颜色 = {H} · 大小 = {Z}"],
"lay.on":   ["LAYER — ","图层 — "],
"grid.fix": ["fixed (lattice)","固定(点阵)"],
"legend.click":["click to open","点击展开"],
};

const LANGS=["zh","en","both"], LANGNAME={zh:"中文",en:"EN",both:"双语"};
let LANG = localStorage.getItem("atlas_lang") || "zh";
function T(key,vars){
  const e=I18N[key];
  if(!e) return "⟪"+key+"⟫";
  let s = LANG==="en" ? e[0] : e[1];
  if(LANG==="both") s = e[0]+" <span class='zh2'>"+e[1]+"</span>";
  if(vars) for(const k in vars) s=s.split("{"+k+"}").join(vars[k]);
  return s;
}
function Tt(key,vars){const h=T(key,vars);const d=document.createElement('div');d.innerHTML=h;return d.textContent;}
