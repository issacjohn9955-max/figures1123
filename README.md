# 鸡 SV–环境绘图库（SV Figure Library）

**版本**：2026-11-22 ｜ **图册**：49 页合订本 ｜ **项目图**：27 张 ｜ **参照图**：19 张（覆盖 17 个模块）

本仓库完整收录该绘图库的交付内容：合订图册、27 张项目图与 19 张英文参照图的独立文件、全部绘图脚本、冻结输入表、样式快照、文件清单与校验值。目标只有一个——**任何人拿到这个仓库，都能看懂这套图在讲什么、能重画、能核对，不会把示意当结果**。

---

## 一、快速索引

| 需求 | 打开 |
|---|---|
| 通读全部图 | [`SV_figure_library.pdf`](SV_figure_library.pdf)（49 页合订本，11.4 MB） |
| 按编号 / 来源 / 模块查图 | [`SV_figure_library_20261122/figure_library_catalog.tsv`](SV_figure_library_20261122/figure_library_catalog.tsv) |
| 查参照图对应哪个仓库模块 | [`SV_figure_library_20261122/figure_sources.tsv`](SV_figure_library_20261122/figure_sources.tsv) |
| 重绘项目图 24–27 | `cd SV_figure_library_20261122 && python3 code/render_current.py` |
| 核对文件完整性 | [`SV_figure_library_20261122/MANIFEST.tsv`](SV_figure_library_20261122/MANIFEST.tsv)（118 个文件的 sha256） |
| 看两个来源仓库的说明 | [`绘图库_GitHub来源说明.docx`](绘图库_GitHub来源说明.docx) |

三份补充文档：

- [图册导读](docs/图册导读.md) —— 49 页怎么翻、编号规则、页码与文件的对应
- [复现指南](docs/复现指南.md) —— 环境、命令、参数、常见问题
- [数据与口径](docs/数据与口径.md) —— 哪些是实测、哪些是示意、哪些数字不能引用

---

## 二、目录结构

```
.
├── README.md                      本文件（中文总说明）
├── LICENSE                        MIT
├── SV_figure_library.pdf          49 页合订图册（与包内 deliverables/ 同名文件逐字节相同）
├── 绘图库_GitHub来源说明.docx       两个来源仓库的用途与来源说明（Word）
├── docs/
│   ├── 图册导读.md
│   ├── 复现指南.md
│   └── 数据与口径.md
└── SV_figure_library_20261122/    完整交付包（原样收录，118 个文件）
    ├── 使用说明.txt                发布者原始说明
    ├── MANIFEST.tsv               118 个文件的字节数与 sha256
    ├── figure_library_catalog.tsv  46 行图件目录：编号、页码、标题、来源、条件、sha256
    ├── figure_sources.tsv          19 张参照图 → 来源模块与固定提交
    ├── baseline/                   项目图 01–23（23 个 PDF，既有工作流图集）
    ├── figures/                    项目图 24–27（4 组 PNG 600 dpi + PDF）与统计小表
    ├── inputs/                     本轮绘图所用的冻结输入表与底图（11 个文件）
    ├── deliverables/               合订图册、项目索引、参照图索引、校验 JSON
    ├── code/
    │   ├── render_current.py       重绘 24–27
    │   └── build_library.py        在原工作区组装图册与索引
    ├── style/                      主题与配色快照（theme.json / palettes.json）
    └── references/                 19 张参照图 PDF + source/（17 个模块的说明与脚本副本）
```

> `SV_figure_library.pdf` 在仓库根目录与包内 `deliverables/` 各存一份，二者 sha256 完全一致（`fb99a65a…`）。根目录这份是为了"进仓库第一眼就能看到"，包内那份保证交付包自足；如无必要可删根目录副本，不影响任何流程。

---

## 三、这套图讲什么

一句话：**用当前鸡 SV 队列回答"结构变异的地理来源、环境关联与跨方法证据"，并把用于对照的图型集中成册。**

- **项目图 27 张**：20 张来自实测结果，7 张是合成/版式示意（编号 05–08、21–23）。
- **参照图 19 张**：来自公开仓库 [`issacjohn9955-max/Figures`](https://github.com/issacjohn9955-max/Figures) 的 17 个模块，固定提交 `2128a965825251e39fedf6599ab2efd182c89d1a`，仅作版式参照。
- **24–27 是本轮重绘的四张**：原产地分布、偏 RDA 排序、跨方法证据汇总、偏秩相关与 LFMM2 配对统计；配套冻结表在 `inputs/`，可原样复现。
- **风格来源**：另一个仓库 [`1577377232/Genomics-Figure-Styles`](https://github.com/1577377232/Genomics-Figure-Styles) 的配色、字体层级与导出规范；本套图读取的是 `style/` 下的本地快照，不依赖网络。

---

## 四、27 张项目图

按内容可分成六组，编号与页码见下表（页码指合订图册）：

- **01–04 证据与地理**：跨方法证据、原产地与位置证据、候选重叠、结构/地理校正的敏感性
- **05–08 单环境与预测（合成示意）**：单环境 vs 联合 LFMM、区域关联与 LD、外部验证、配对预测
- **09–11 采样与背景**：采样规模、环境相关与共线性、SV 背景结构（PCA）
- **12–16 扫描与诊断**：全基因组偏秩扫描、候选位点、RDA 轴检验、LFMM2 的 K 敏感性、QQ 诊断
- **17–20 可检测性与局部信号**：基因型可检测性、联合 Manhattan、局部 SV–BIO3、气候范围
- **21–23 机器学习（合成示意）**：模型比较、留出预测与增量误差、五模型指标
- **24–27 本轮重绘（实测）**：原产地、偏 RDA、跨方法、配对统计

| 编号 | 页码 | 标题 | 数据性质 | 文件 |
|---|---|---|---|---|
| 01 | 3 | Cross-method evidence and testability | 实测 | `baseline/01_evidence.pdf` |
| 02 | 4 | Representative origins and location evidence | 实测 | `baseline/02_origins.pdf` |
| 03 | 5 | Candidate overlap across location and identity settings | 实测 | `baseline/03_scenario.pdf` |
| 04 | 6 | Sensitivity to structure and geographic adjustment | 实测 | `baseline/04_adjustment.pdf` |
| 05 | 7 | Single-environment vs joint LFMM effects | 合成/版式 | `baseline/05_lfmm.pdf` |
| 06 | 8 | Regional association, annotation, LD and conditional effect | 合成/版式 | `baseline/06_region.pdf` |
| 07 | 9 | Effects in held-out regions and external cohorts | 合成/版式 | `baseline/07_validate.pdf` |
| 08 | 10 | Paired prediction of an origin-climate variable | 合成/版式 | `baseline/08_prediction.pdf` |
| 09 | 11 | Sampling groups and sample sizes | 实测 | `baseline/09_sampling.pdf` |
| 10 | 12 | Environmental correlation and covariate collinearity | 实测 | `baseline/10_environment.pdf` |
| 11 | 13 | Background genetic structure (SV PCA) | 实测 | `baseline/11_pca.pdf` |
| 12 | 14 | Genome-wide partial-rank scan | 实测 | `baseline/12_scan.pdf` |
| 13 | 15 | Focal SV: frequency, adjusted ranks and group influence | 实测 | `baseline/13_candidate.pdf` |
| 14 | 16 | RDA axis tests and loading threshold sensitivity | 实测 | `baseline/14_rda.pdf` |
| 15 | 17 | LFMM2 count and direction sensitivity to K | 实测 | `baseline/15_lfmm_k.pdf` |
| 16 | 18 | LFMM2 QQ and genomic-control diagnostics | 实测 | `baseline/16_qq.pdf` |
| 17 | 19 | Observed genotype availability | 实测 | `baseline/17_17_input_callability.pdf` |
| 18 | 20 | Joint LFMM2 Manhattan scans | 实测 | `baseline/18_18_LFMM2_scan.pdf` |
| 19 | 21 | Local SV–BIO3 signals | 实测 | `baseline/19_19_focal_SV_signal.pdf` |
| 20 | 22 | Climate ranges by coordinate group | 实测 | `baseline/20_20_environment_coverage.pdf` |
| 21 | 23 | Matched LFMM2 model comparison | 合成/版式 | `baseline/21_21_lfmm_fitted_demo.pdf` |
| 22 | 24 | Holdout predictions and paired incremental error | 合成/版式 | `baseline/22_22_ml_oof_and_gain.pdf` |
| 23 | 25 | Five-model prediction metrics | 合成/版式 | `baseline/23_23_ml_metrics.pdf` |
| 24 | 26 | Representative origins across the main cohort | 实测 | `figures/24_origin_world_asia.pdf` |
| 25 | 27 | Partial RDA ordination and axis tests | 实测 | `figures/25_partial_rda_ordination.pdf` |
| 26 | 28 | Cross-method evidence across analysis cohorts | 实测 | `figures/26_cross_method_summary.pdf` |
| 27 | 29 | Partial-rank and LFMM2 statistics on matched SVs | 实测 | `figures/27_paired_statistics.pdf` |

---

## 五、19 张参照图

参照图的定位是**版式参照，不是结果**。每张都注明了"历史队列"或"合成版式"的来源性质，以及在什么条件下才能正式使用。原始模块路径指向固定提交，可逐条回查。

| 编号 | 页码 | 标题 | 来源模块 | 使用条件 |
|---|---|---|---|---|
| F01 | 31 | World map and China detail | `world_distribution_map` | Rebuild for the chosen cohort and location evidence. |
| F02 | 32 | Province counts | `china_sampling_map` | Use where provenance supports province-level assignment. |
| F03 | 33 | Site map with regional detail | `china_sampling_map` | Requires verified sites and boundary data. |
| F04 | 34 | Side-by-side marker PCA | `fig1b_pca` | Requires paired SNP and SV data for the same individuals. |
| F05 | 35 | TE PCA by climate zone | `pca_climate_zone` | Requires climate-zone assignments for the plotted individuals. |
| F06 | 36 | SNP PCA by climate zone | `pca_climate_zone` | Requires matched SNP PCA and climate zones. |
| F07 | 37 | Tree and admixture alignment | `fig1c_tree_admixture` | Requires a matched tree, ancestry proportions and IDs. |
| F08 | 38 | Climate context and environment correlations | `fig2_environment` | Requires matched WorldClim rasters and environmental metadata. |
| F09 | 39 | Ordination, environmental vectors and axis tests | `fig3_rda` | Use component values and scores from a single fitted model. |
| F10 | 40 | Evidence across association methods | `fig4_evidence` | Keep SV–environment pairs and unique SV alleles distinct. |
| F11 | 41 | TE composition and family enrichment | `fig5_te` | Requires validated TE annotation and eligible background. |
| F12 | 42 | Genome-wide Circos with TE structures | `fig1_chicken_GRCg7b_circos` | Requires a shared reference build and defined density tracks. |
| F13 | 43 | Association-statistic comparison | `corr_ci_scatter` | Use aligned statistics. Inference requires an appropriate dependence model. |
| F14 | 44 | Environment-by-method radar | `gea_driver_radar` | Use a common counting unit and document tested denominators. |
| F15 | 45 | Association statistics with marginal views | `gea_marginal_scatter` | Use summary statistics from matched loci and environments. |
| F16 | 46 | Niche overlap and a null distribution | `niche_overlap_null` | Use a documented environmental space and a defined null model. |
| F17 | 47 | Unique and shared environmental associations | `te_factor_polar` | Requires a fixed significance rule and an explicit unit of counting. |
| F18 | 48 | Isolation by distance and environment | `te_ibe_adaptive_neutral` | Requires distances, site groups and a permutation design. |
| F19 | 49 | Climate driver contribution | `variable_contribution` | Requires a defined importance metric and matching fitted model. |

---

## 六、图册怎么读

1. **第 1 页**是项目索引，列 01–27 的编号、标题与页码；**第 30 页**是参照图索引，列 F01–F19。
2. 项目图从**第 3 页**起，参照图从**第 31 页**起；目录表 `figure_library_catalog.tsv` 的 `gallery_page` 字段就是页码。
3. 每张图在合订本里保留原始矢量，可放大看细节；密集统计量的分箱是栅格层。
4. 想单独取某一张，从 `baseline/` 或 `figures/` 取同名 PDF，`catalog` 的 `file` 字段给了相对路径。

---

## 七、复现

```bash
cd SV_figure_library_20261122
python3 code/render_current.py            # 用 inputs/ + style/ 重绘 24–27 到 figures/
```

依赖 Python 3、numpy、matplotlib（个别流程用 pandas）。默认读取包内的 `inputs/`、`style/`，输出到 `figures/`；替换研究结果时可指定：

```bash
python3 code/render_current.py \
  --inputs /path/to/new_inputs \
  --output /path/to/out \
  --style  style
```

若要把一套已完成的队列结果正式并入，用 `--run <目录> --evidence-tables <表> --basemap <底图>`，脚本会先做归一化再出图。底图为 Natural Earth 1:110m。

`code/build_library.py` 是在原工作区组装合订本与索引用的，依赖发布者的本地目录结构，仓库内仅作存档。

细节与排错见 [复现指南](docs/复现指南.md)。

---

## 八、数据与口径（务必先读）

- **实测 vs 示意**：编号 05–08、21–23 共 7 张为合成/版式示意，**图上的坐标、P 值、计数不得作为结果引用**；其余 20 张来自实测结果。
- **参照图不等于结果**：F01–F19 是历史队列或合成版式的英文图，作用是给出版式与坐标轴写法，**其数值属于来源研究或历史队列**。
- **可复现的边界**：24–27 由 `inputs/` 的冻结表驱动，逐位可复现；01–23 是既有工作流图集，仓库内只保留成图，不含其上游分析脚本与原始数据。
- **不包含个体级数据**：本仓库只有聚合表与成图，没有基因型矩阵、表型表或原始测序数据。

完整口径见 [数据与口径](docs/数据与口径.md)。

---

## 九、完整性校验

`MANIFEST.tsv` 记录包内全部 118 个文件的字节数与 sha256，一行一个：

```bash
cd SV_figure_library_20261122
python3 - <<'PY'
import csv, hashlib, pathlib
bad = 0
for r in csv.DictReader(open('MANIFEST.tsv', encoding='utf-8'), delimiter='\t'):
    p = pathlib.Path(r['path'])
    h = hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
    if h != r['sha256']:
        bad += 1; print('MISMATCH', r['path'])
print('ok' if not bad else f'{bad} mismatched')
PY
```

`deliverables/validation.json` 给出发布时的自检结果：

```json
{"status": "PASS", "project_figures": {"observed": 20, "synthetic": 7},
 "reference_figures": 19, "reference_modules": 17, "gallery_pages": 49,
 "gallery_sha256": "fb99a65a…", "upstream_commit": "2128a965…"}
```

---

## 十、来源与版本

| 项 | 值 |
|---|---|
| 绘图库版本 | 2026-11-22 |
| 合订本页数 | 49（项目图 27 + 参照图 19，另 3 页索引） |
| 参照图上游 | `issacjohn9955-max/Figures` @ `2128a965825251e39fedf6599ab2efd182c89d1a` |
| 风格上游 | `1577377232/Genomics-Figure-Styles` |
| 合订本 sha256 | `fb99a65ab234ff212f352022ad702d80167a1906ff240212078c4316b9ff689e` |
| 文件总数 | 118（交付包）+ 本文档与根目录副本 |

来源说明另见 [`绘图库_GitHub来源说明.docx`](绘图库_GitHub来源说明.docx)。

---

## 十一、许可

代码采用仓库根目录的 [MIT License](LICENSE)。

图形内容的版权与使用条件随来源而定：项目图 24–27 为本项目结果；01–23 为既有工作流图集；F01–F19 为来源仓库的参照图，其版权归原图作者，正式使用前请按 `figure_sources.tsv` 的 `condition` 列替换为当前队列结果。引用本图册时，请同时引用来源研究。
