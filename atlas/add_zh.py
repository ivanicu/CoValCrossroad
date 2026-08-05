"""Chinese for the data-driven strings: layer labels, layer findings, projection notes.

These live in corpus.json rather than i18n.js because they are keyed to objects the
extractor produces. One home per string: if a layer is added upstream and no zh exists,
the page prints the key loudly instead of silently showing English as though translated.
"""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
C = json.loads((ROOT / "atlas/corpus.json").read_text())

ZL = {
"no_rubric": ("无 rubric —— 被静默丢弃",
  "110 条 prompt(10.2%)带着比较和排序,却没有 rubric 行,所以这场 campaign 的每一轮都只跑了 968 条,"
  "而且从没解释过缺掉的那 110 条。"),
"modal_tie": ("众数目标是平局",
  "所谓「人类答案」是出现最多的那个两两类。在这些 prompt 上有两个类出现次数相同,胜者由字典插入顺序决定。"),
"all_tie": ("人类把四个全判平",
  "众数类全是 0:一个空的 core 按构造就能拿 6/6。"),
"core_beats_topw": ("coval_core 赢过 topw_k4",
  "官方发布的 core 和最高权重规则在汇总上无法区分(0.6092 vs 0.6090)。但逐条看它们一直在分歧 —— 这是官方赢的那批。"),
"topw_beats_core": ("topw_k4 赢过 coval_core",
  "同一个比较,反过来。如果汇总上的平手是一个恒等式,这两个集合都会是空的;它们不是,而它们规模几乎相等,"
  "正是汇总平手的成因。"),
"sign_rescue": ("符号救回了求和",
  "在这里 full_weighted(Σ w·sat)严格赢过 full(Σ sat)。这就是那个机制:无符号求和把 −10 的准则当成 +10 一样加。"),
"sign_hurts": ("符号反而害了求和",
  "上一个图层的对照。如果加符号是普遍改进,这个集合就该是空的。它不是 —— 所以符号是一个有代价的机制,不是白拿的胜利。"),
"full_beats_all": ("没有任何 k=4 的 core 赢过 full",
  "选择在这里严格失败:整份准则表的成绩高过所有试过的四条规则。"),
"topabs_collapse": ("topabs_k4 崩塌",
  "|w| 规则六个里只中 2 个或更少。它按绝对值挑选,于是把 −10 的准则放进来,而无符号求和随后把它们当成加分。"),
"all_arms_fail": ("所有构造都失败",
  "没有任何 arm 到 4/6。无论整份准则表还是任何 core,都没能还原这条 prompt 的人类排序。"),
"all_arms_win": ("所有构造都成功",
  "每个 arm 都到 5/6 以上 —— 这条 prompt 对整个家族都太容易,因此分辨不出任何东西。"),
"split_heavy": ("三分之一的标注者 personal ≠ world",
  "这场 campaign 只用 world 排序。在这里至少三分之一的标注者,被问到个人偏好时给出了不同的排序 —— "
  "所以「用哪个作为目标」是一个有可见代价的选择。"),
"unacceptable": ("有人把某个回答标为不可接受",
  "unacceptable 这个块从没被任何一轮当作目标使用过。这些是它触发的 prompt。"),
"neg_heavy": ("三分之一的准则带 w < 0",
  "无符号聚合器在这里可摧毁的东西最多。"),
"core_not_in_full": ("发布的 core 与 full 无一字重合",
  "coval_core 是一个会合并、取反、挑选的 LM 蒸馏 —— card 自己说它可能「偏离数据」。在这里它没有任何一条准则"
  "逐字出现在它所蒸馏的那份准则表里。"),
}
ZP = {
"tsne":  ("t-SNE","保住邻域,不保距离 —— 只能读「近/远」,不能读数值"),
"umap":  ("UMAP","n_neighbors 25, min_dist 0.12 —— 比 t-SNE 多保住全局结构,但仍不是度量空间"),
"pca":   ("PCA 主成分","线性投影,距离是真的;这两根轴只装下全部方差的一小部分(见英文行)"),
"mds":   ("MDS 多维标度","700 条用应力最小化真嵌入,其余贴到最近邻 —— 写出来了,没有藏"),
"grid":  ("排序点阵","几何全部丢弃;换来零遮挡、位置可精确解码 —— 按邻域排序,再按准则数"),
"swarm": ("蜂群图","x = 共识强度,y 只是避让抖动 —— 一维分布,但每个点仍然分得开"),
}
miss = []
for L in C["layers"]:
    if L["key"] in ZL:
        L["label_zh"], L["finding_zh"] = ZL[L["key"]]
    else:
        miss.append(L["key"])
for k, v in C["projections"].items():
    if k in ZP:
        v["label_zh"], v["note_zh"] = ZP[k]
    else:
        miss.append("proj:" + k)
C["layer_note_zh"] = ("每个图层都是一条结论被改写成一批 prompt。`z` 把该图层在 t-SNE 视图中的平均两两距离,"
                      "对比 60 次同规模随机抽样:z 接近 0 表示这条结论均匀分布在全语料上,不是任何领域的属性;"
                      "强负值表示它确实聚集。")
C["caveat_zh"] = ("结构很弱,而且是展示出来的,不是宣称的。k∈{8,12,18,24} 上最佳轮廓系数远低于「干净划分」"
                  "通常的 ≈0.25;TF-IDF 更低。k=12 是一个选择。邻域的名字是把它和其余部分分隔得最厉害的词,"
                  "算出来的,不是指定的。")
(ROOT / "atlas/corpus.json").write_text(json.dumps(C, ensure_ascii=False))
print("layers with zh:", sum(1 for L in C["layers"] if "label_zh" in L), "/", len(C["layers"]))
print("projections with zh:", sum(1 for v in C["projections"].values() if "label_zh" in v), "/", len(C["projections"]))
print("MISSING:", miss or "none")
