---
name: job-fit-research
description: Research current campus, early-career, internship-conversion, or experienced-hire openings with claim-specific multi-source verification, then rank them by candidate fit, profile-independent job quality, and application value. Use when the user asks which jobs or companies to apply to, requests current openings or early-batch recruitment, specifies companies or filters, compares private, foreign, or state-owned employers, or wants evidence-based analysis of duties, eligibility, workload, compensation, business stability, career prospects, and application strategy. Also trigger on Chinese requests such as 校招、提前批、岗位推荐、岗位适配、国企私企外企对比、投什么岗位.
---

# Job Fit Research

为用户生成“当前仍可投、证据可追溯、适配度与岗位好坏分开评价”的岗位清单。匹配用户语言输出。

## 运行约束

开始前读取 [references/runtime-contract.md](references/runtime-contract.md)。遵守以下硬规则：

1. 当前岗位属于动态事实；没有联网检索能力时，不得凭记忆声称岗位仍开放。
2. 不假设宿主提供某个固定名称的工具。使用桌面端 Codex 实际暴露的网页搜索、浏览或文件工具。
3. 不依赖其他代理产品的环境变量、斜杠命令或模型私有推理格式。
4. 不展示隐藏思维过程；只展示判断所依据的事实、公式、置信度和缺口。
5. 完成每个检查点后再进入下一阶段。证据不够时降级结论，不补造信息。
6. 查真实岗位只认官网 ATS（雇主招聘系统）和官方招聘公众号菜单里的实际投递列表；招聘简章/宣传公告只能作为岗位类别与计划城市参考，不得单独作为“某岗位当前开放”或“某城市有岗”的证据。官网 ATS 打不开或未查到具体岗位时，状态至多标 `Likely open` 或 `Unverified`，不得标 `Open—verified`。
7. 社交平台/公众号流传的“XX城市神仙外企/福利榜单”只能作为发现线索：先核验该公司在该城市是否有注册实体（国家企业信用信息公示系统/天眼查等工商来源）以及岗位级锚点，再入报告；把同名本地公司当成跨国外企（如“合肥凯捷技术”≠凯捷 Capgemini）、或仅有销售代表/办事处却写成研发基地的，一律标注并纠正。

## 输入

将当前用户消息、会话上下文和用户提供的文件视为输入。支持自然语言，也支持下列 `key=value` 参数：

- `profile=<path|default|conversation>`：候选人档案；省略时优先读取 `profiles/default.yaml`。
- `company=<names>`：指定一个或多个公司。
- `ownership=<private|foreign|state-owned|central-soe|joint-venture|any>`
- `role=<keywords>`、`exclude_role=<keywords>`、`industry=<keywords>`、`city=<names>`
- `graduation=<year>`、`degree=<level>`、`batch=<early|autumn|spring|intern-conversion|all>`
- `employment=<full-time|internship|all>`、`salary_min=<amount>`、`max_intensity=<1-5>`
- `travel=<yes|no|limited>`、`deadline_before=<date>`、`freshness=<days>`、`count=<number>`
- `source_depth=<quick|standard|deep>`、`require_official=<yes|no>`
- `language=<zh|en|bilingual>`、`save=<path>`

输入复杂或含糊时读取 [references/parameters.md](references/parameters.md)。缺少可选条件时说明默认值并继续；只有缺失的硬约束会实质改变结果时才询问用户。

## 状态机

严格按顺序执行，并维护一个简短的工作状态：

`PARSE → PROFILE → SEARCH → VERIFY → EVIDENCE → SCORE → REPORT → AUDIT`

不得在 `VERIFY` 完成前评分，不得在 `AUDIT` 完成前给出确定性推荐。

## 1. PARSE：解析范围

提取公司、岗位族、城市、毕业年份、批次、雇佣类型、薪资、强度、出差和排除条件。区分：

- 硬约束：`必须`、`只要`、`不接受`、明确的资格条件；
- 软偏好：`最好`、`优先`、`不太想`；
- 列举式技术栈要求：任职要求中逐条列出的技术栈/语言/框架（如“熟练掌握 X，熟悉 Y/Z 至少一种”“熟练使用 A/B/C 任一”）默认按候选门槛处理，不得当作软偏好；候选人不满足任一列举项时 `eligibility` 不得给 5，等价能力（如 C++ 代替 Java）必须标注“未验证等价”并降低置信，投递前需与 HR 确认；
- 未知项：不能从用户输入或档案得到的事实。

选择模式：

- **公司模式**：逐一检索所有指定公司，每家公司都必须有结论，包括“未找到可验证的当前岗位”。
- **筛选模式**：跨公司检索，直到达到所需数量或可信来源已耗尽。

记录检索日期、时区、默认值和停止条件，全部使用绝对日期。

## 2. PROFILE：建立候选人模型

读取指定档案。若档案不可用，从会话、简历或用户材料中提取证据。分为：

- 硬资格：毕业年份、学历、专业、语言、工作许可、实习时长；
- 已证明能力：项目、论文、实习、工具、领导力、写作和跨部门协作；
- 偏好与限制：地点、公司类型、工作强度、出差、薪资、编码强度；
- 弱证据与缺口。

不得把用户自述的弱项改写成强项，不得把“接触过”升级为“熟练掌握”。

### 检查点 A

进入检索前确认：检索范围、候选人硬资格、硬约束、软偏好均已列出。若无法确认毕业年份等关键资格，可以继续搜索，但必须把资格标为 `Unclear`。

## 3. SEARCH：建立检索矩阵

检索前完整读取 [references/source-playbook.md](references/source-playbook.md)。

对公司、岗位同义词、城市、毕业年份、批次名称、官方 ATS 域名和官方招聘公众号建立查询矩阵。中英文关键词并用。每家公司优先检索并打开其官方招聘公众号（认证主体为公司或其 HR 主体）的最新推文和网申入口，与官网/ATS 交叉确认；公众号信源占比应高于普通聚合站，并在证据账本中单独标注。优先定位具体职位页面，而不是只看宣传页或搜索摘要。

默认检索深度：

- `quick`：一个高权威岗位来源，只给有直接证据的质量信号；
- `standard`：官方岗位锚点，并为岗位质量增加至少两个相互独立的来源家族；
- `deep`：官方岗位锚点，加薪资、工时、所有制/稳定性、发展出口等至少四个独立来源家族。

默认所有岗位做 `standard`，最终前三名做 `deep`。不要为了凑够 `count` 而降低标准。

## 4. VERIFY：核验岗位状态

打开来源页面并核验每个候选岗位：

1. 公司及法律实体或子公司；
2. 准确职位名称和地点；
3. 毕业年份、学历、专业、语言等资格；
4. 发布日期、截止日期和当前申请状态；
5. 可直接申请的链接；
6. 职责与要求。

岗位级核验锚点只允许是：官网 ATS 中的具体职位页，或官方招聘公众号菜单里能直接进入投递的具体岗位。招聘简章、宣传页、聚合站转载中的岗位名与城市列表一律只用于发现与类别参考；若官网 ATS 中查不到对应具体岗位（如只看到“可选城市含某地”而无实际职位页），该“某城市有岗”的主张必须标 `Unverified`，不得进入已核验清单。

状态只能使用：

- `Open—verified`：官方页面或 ATS 当前可申请；
- `Likely open`：有当前日期公告，但申请状态不清楚；
- `Pipeline`：实习、人才池或转正路径，不是正式校招岗位；
- `Unverified`：只有聚合站或转载；
- `Closed/expired`：已关闭或过期。

搜索结果摘要不能独立支持高置信结论。`Pipeline` 和 `Unverified` 不得冒充正式提前批岗位。

### 检查点 B

逐项检查每个入围岗位是否具备“具体职位 + 地点 + 资格 + 当前状态 + 直达链接”。缺任一项就降低状态或移入观察名单；硬资格失败则不得进入投递组合。

## 5. EVIDENCE：建立主张—证据账本

每个入围岗位记录：

- 主张类型与结论；
- 来源 URL、发布日期和本次检查日期；
- 来源家族、独立性和权威等级；
- 置信度；
- 冲突或缺失证据。

岗位状态和职责优先使用公司官网或官方 ATS。薪资、工时与文化使用适合该主张的补充来源，并明确标注 `Official`、`Employee report`、`Market estimate` 或 `Inference`。同源转载不算交叉验证。

禁止：

- 将“面议/有竞争力”编成薪资范围；
- 用实习薪资代替校招全职薪资；
- 不写年份和城市就引用旧 offer；
- 根据公司名称猜所有制；
- 根据口号判断 WLB；
- 隐瞒相互冲突的信源。

## 6. SCORE：三层评分

评分前完整读取 [references/evaluation.md](references/evaluation.md)。先做硬资格门控，再分别计算：

1. **候选人适配度**：资格、技能匹配、履历证据、职业方向、竞争现实性、个人约束；
2. **岗位绝对质量**：默认 WLB 优先（`quality_basis=wlb_first`），先评工作可持续性/强度，再评薪酬福利、学习与所有权、平台资源、外部流动性和稳定性；当 WLB 证据不足或明确较差时，切换为薪资+成长+上升空间模式（`quality_basis=salary_growth_fallback`），并在报告中标注切换依据；
3. **投递价值**：综合适配度、岗位绝对质量和岗位开放置信度。

JD 出现「顶会/顶刊」「高水平论文」或点名顶级会议/期刊时（无论硬性任职要求还是加分项/优先项），按 [references/evaluation.md](references/evaluation.md) 的强制降分规则处理：候选人不具备顶级论文时 `competition` 不得超过 3，推荐标签最高为 `conditional`（不得标记 `priority` 或 `apply`），并在报告与台账的 Gap/理由中标注「顶会条款→competition≤3，最高 conditional」。

岗位绝对质量必须以同城市、同岗位族、相近学历层级的岗位为参照，不能使用候选人档案。低置信度判断向中性分收缩。每个分数只保留合理精度，并给出决定分数的 2–3 条事实。

四个及以上岗位且证据足够时，可生成符合 `references/evaluation.md` 的 JSON，然后运行：

```text
python <skill-directory>/scripts/score_jobs.py <input.json> --format markdown
```

`<skill-directory>` 是当前 `SKILL.md` 所在的绝对目录，不是环境变量。若 Python 不可用，按评分参考中的公式人工计算并标明；岗位少于四个或证据明显不足时不运行脚本。

## 7. REPORT：生成可执行结果

输出前读取 [references/output-template.md](references/output-template.md)，并按岗位数量压缩格式。必须包含：

只报告当前处于投递期且有证据的岗位。未到开放时间（如仅有“预计 X 月开放”）和已过截止/已关闭的岗位一律不写入报告正文与排名，也不作为推荐或提醒出现；此类信息最多保留在内部观察清单，不向用户展示。

1. 检索日期、范围、默认值、信源深度和限制；
2. 排名清单；
3. 用户要求的公司类型覆盖；
4. 靠近对应主张的直达链接；
5. 适配度、岗位绝对质量和投递价值三个独立分数；
6. 薪资与工作强度的证据等级和置信度，以及每个岗位的职业发展与薪资成长（起薪→2–3 年→3–5 年，证据等级标注）；
7. `priority / apply / conditional / stretch / skip` 建议；
8. 未来 48 小时行动；
9. 未找到、未验证、已过期和资格不符的诚实说明。

当 `save=<path>` 时，保存报告以及结构化快照，至少包含公司、岗位、状态、截止日期、URL、三项分数、检查日期、信源覆盖和主张置信度。否则仅在聊天中输出。

## 8. AUDIT：最终审计

提交前逐项回答 `yes/no`：

- 所有“当前开放”结论是否有打开过的岗位页支持？
- 是否对每个入围岗位的任职要求做过逐条技术栈/语言/框架勾选，且缺失项没有拿到 eligibility=5？
- 是否把明确事实、员工报告、市场估计和推断区分开？
- 是否把适配度与岗位绝对质量分开？
- 是否披露硬资格失败、信源冲突和未知薪资？
- 是否包含所有指定公司或解释为什么没有结果？
- 是否所有日期都是绝对日期？
- 是否没有因满足数量要求而塞入过期或无关岗位？
- 是否排除了未到开放时间和已过截止/已关闭的岗位？

任一项为 `no` 时先修正；无法修正则降低置信度并在限制中说明。

## 更新与对比

收到旧快照时，重新打开每个官方岗位链接，标记新增、变化、关闭和临近截止岗位；保留旧检查日期，不静默覆盖历史薪资证据。先总结变化，再给刷新后的排名。

## 资源

- [profiles/default.yaml](profiles/default.yaml)：当前个性化候选人档案，可替换或覆盖。
- [profiles/example.yaml](profiles/example.yaml)：通用档案结构。
- [references/runtime-contract.md](references/runtime-contract.md)：Codex/DeepSeek 运行边界与降级策略。
- [references/parameters.md](references/parameters.md)：筛选条件、默认值和调用示例。
- [references/source-playbook.md](references/source-playbook.md)：信源家族、交叉验证和区域检索方法。
- [references/evaluation.md](references/evaluation.md)：适配度、岗位绝对质量、投递价值、薪资、工时和发展评分。
- [references/output-template.md](references/output-template.md)：报告结构和证据标签。
- [scripts/score_jobs.py](scripts/score_jobs.py)：四个及以上岗位的确定性评分脚本。
