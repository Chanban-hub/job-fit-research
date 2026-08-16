# job-fit-research

一个用于 Codex 桌面端的岗位调研 Skill：检索当前校招/实习/社招岗位，以官方 ATS 为准核验在招状态，并按「候选人适配度、岗位绝对质量、投递价值」三层评分，输出可执行的投递建议。

本 Skill 适合以下场景：

- 想知道某家公司现在有哪些岗位真正在招、哪些城市有岗、截止到什么时候；
- 想知道某个岗位和自己简历的匹配度，以及这个岗位本身值不值得去（薪资、加班、成长、出口）；
- 需要在多份 Offer / 多个投递方向之间排序，或持续跟踪一批公司的岗位变化。

---

## 目录结构

```text
job-fit-research/
├── SKILL.md                  # Skill 入口：执行状态机与硬规则（PARSE→PROFILE→SEARCH→VERIFY→EVIDENCE→SCORE→REPORT→AUDIT）
├── agents/
│   └── openai.yaml           # 界面显示名、短描述、默认提示词
├── profiles/
│   └── example.yaml          # 候选人档案模板（复制为 default.yaml 使用）
├── references/
│   ├── evaluation.md         # 三层评分公式、权重、推荐标签规则
│   ├── output-template.md    # 报告结构、证据标签、48 小时行动要求
│   ├── parameters.md         # 参数、默认值、自然语言筛选对照表
│   ├── runtime-contract.md   # 运行边界、降级策略、数据安全
│   ├── source-playbook.md    # 信源族、交叉验证、证据台账格式
│   └── ats-reverse-engineering.md  # ATS 逆向速查表（Moka/北森/自建系统实测接口）
└── scripts/
    └── score_jobs.py         # 确定性评分脚本（四个及以上岗位时运行）
```

---

## 安装

### 方式一：手动安装（推荐）

1. 把整个 `job-fit-research` 目录复制到 Codex 的 skills 目录：

   ```text
   ~/.codex/skills/job-fit-research/
   ```

   最终目录结构必须是：

   ```text
   ~/.codex/skills/
   └── job-fit-research/
       ├── SKILL.md
       ├── agents/
       ├── profiles/
       ├── references/
       └── scripts/
   ```

2. 在 Codex 中开启一个新会话（或重新加载会话），让系统识别新 Skill。
3. 验证：在对话里输入 `$job-fit-research` 或直接描述一个岗位调研需求，如果 Skill 正常响应即安装成功。

### 方式二：从 GitHub 安装

```bash
git clone https://github.com/Chanban-hub/job-fit-research.git
cp -r job-fit-research ~/.codex/skills/
```

> 注意：`SKILL.md` 必须在 `~/.codex/skills/job-fit-research/` 这一层，不要多套一层目录。

---

## 候选人档案配置（强烈建议先做）

Skill 的评分需要你的真实信息作为基准。第一次使用前：

1. 复制模板：

   ```text
   cp profiles/example.yaml profiles/default.yaml
   ```

2. 编辑 `profiles/default.yaml`，至少填写：

   | 字段 | 说明 | 示例 |
   |---|---|---|
   | `identity.graduation_year` | 毕业年份（用于资格校验） | `2028` |
   | `identity.highest_degree` | 最高学历 | `硕士` |
   | `identity.major` | 专业 | `计算机应用技术` |
   | `demonstrated_evidence` | 已证明能力：论文、实习、项目、竞赛，尽量带量化结果 | `一篇目标检测论文；一次端侧部署项目（示例）` |
   | `preferences.preferred_roles` | 优先岗位族，影响 career 维度打分 | `视觉算法工程师, 大模型算法工程师, 端侧AI算法工程师` |
   | `preferences.avoid_or_deprioritize` | 明确回避/降权方向 | `纯研究岗, 高强度后端, 互联网厂产品岗` |
   | `constraints` | 地点、薪资下限、强度上限、出差 | `city=不限; max_intensity=3` |

3. 隐私提示：`profiles/default.yaml` 含个人信息，本仓库默认通过 `.gitignore` 排除，不要提交。

4. 不想用默认档案时，可用 `profile=<路径>` 指定任意档案。

---

## 调用方式

### 触发

- 显式调用：`$job-fit-research ...`
- 自然语言触发：直接说「帮我查一下 XX 公司的校招」「对比一下国企和外企」「看看有没有 27 届能投的算法岗」等。

### 支持的参数（`key=value` 形式）

| 参数 | 含义 | 示例 |
|---|---|---|
| `company` | 公司名，多个用逗号分隔 | `company=星河科技,蓝云集团` |
| `role` / `exclude_role` | 岗位关键词 / 排除关键词 | `role=算法,AI` `exclude_role=销售` |
| `ownership` | 企业性质 | `ownership=国企,央企` / `foreign` / `private` |
| `industry` | 行业关键词 | `industry=云计算,智能制造` |
| `city` | 城市 | `city=深圳,上海` |
| `graduation` | 毕业年份 | `graduation=2028` |
| `degree` | 学历要求 | `degree=硕士` |
| `batch` | 批次 | `batch=early` / `autumn` / `spring` / `intern-conversion` |
| `employment` | 全职/实习 | `employment=full-time` / `internship` |
| `salary_min` | 年薪下限（按总包比较） | `salary_min=200000` |
| `max_intensity` | 工作强度上限（1-5） | `max_intensity=3`（对应「不太卷」） |
| `travel` | 出差 | `travel=no` / `limited` |
| `deadline_before` | 截止日期前 | `deadline_before=2026-09-30` |
| `freshness` | 信息新鲜度（天） | `freshness=30` |
| `count` | 返回岗位数量 | `count=8` |
| `source_depth` | 检索深度 | `quick` / `standard`（默认）/ `deep` |
| `require_official` | 只要官方 ATS 确认 | `require_official=yes` |
| `language` | 输出语言 | `language=zh` |
| `save` | 保存报告路径 | `save=D:\report.md` |
| `profile` | 候选人档案路径 | `profile=D:\profile.yaml` |

### 参数优先级

当多处信息冲突时，按以下顺序生效：

1. 本次调用里明确写的参数（`must`/`必须`/`不接受` 视为硬约束）；
2. 当前对话上下文；
3. 所选档案（`profile`）里的值；
4. Skill 默认值。

### 调用示例

```text
# 查两家公司的 27 届校招，做标准深度
$job-fit-research company=星河科技,蓝云集团 graduation=2028 source_depth=standard

# 只要官方确认、薪资 20 万以上、强度 3 以内
$job-fit-research ownership=国企,央企 industry=云计算,智能制造 max_intensity=3 salary_min=180000 require_official=yes

# 外企优先，上海或苏州，不要纯开发岗，接受数据分析/AI 产品实习并要求留用机会
$job-fit-research 外企优先，上海或苏州，不要纯开发岗，可以接受数据分析和AI产品实习，要求有留用机会

# 用指定档案做深度调研
$job-fit-research profile=/absolute/path/profile.yaml company=远山智能 source_depth=deep

# 对比上次快照，只报告新增、关闭和截止变化的岗位
$job-fit-research 对比 previous-jobs.json，只报告新开放、关闭和截止日期变化的岗位
```

---

## 执行流程（Skill 会按此顺序工作）

1. **PARSE**：解析你的公司、岗位、城市、毕业年份、批次、硬约束与软偏好。
2. **PROFILE**：读取候选人档案，建立能力清单与缺口清单。
3. **SEARCH**：定位官方招聘入口（官网 ATS / 官方公众号），建立查询矩阵。
4. **VERIFY**：逐岗位核验「公司主体 + 岗位名 + 城市 + 资格 + 发布时间/截止 + 直达链接 + 职责要求」。
5. **EVIDENCE**：为每个结论记录来源、日期、信源族、置信度与冲突。
6. **SCORE**：分别计算候选人适配度、岗位绝对质量、投递价值。
7. **REPORT**：输出排名表、薪资成长、职业发展、缺口、48 小时行动。
8. **AUDIT**：逐项自查后才会给出最终推荐。

---

## 评分说明

### 三个分数

| 分数 | 回答的问题 | 组成 |
|---|---|---|
| Fit（适配度） | 这个岗位有多适合「你」？ | 资格 25% + 技能 25% + 证据 20% + 职业方向 15% + 竞争 10% + 个人约束 5% |
| Job quality（岗位质量） | 这个岗位本身好不好（与候选人无关）？ | WLB 25% + 成长 20% + 薪酬 15% + 平台 15% + 流动 15% + 稳定 10% |
| Application value（投递价值） | 你该不该把精力花在这里？ | Fit 45% + Job quality 40% + 开放置信度 15% |

分数为 0-100；85+ 优秀，70-84 良好，55-69 可接受但有取舍，40-54 偏弱，<40 不推荐。

### 推荐标签

- `priority`：投递价值 ≥80 且适配度 ≥70，可优先投；
- `apply`：投递价值 ≥65 且适配度 ≥60，建议投；
- `conditional`：有明显取舍（如硬性缺口、顶会条款、方向偏离），可投但设条件；
- `stretch`：岗位质量高但当前适配度不足，值得冲刺；
- `skip`：方向不符、质量过低或有严重风险；
- `ineligible`：硬性资格不满足（如学历、毕业年份、语言）。

### 硬规则（内置）

- 岗位状态只认官方 ATS / 官方公众号菜单里的真实投递列表；招聘简章、聚合站转载只做线索，不能单独证明「在招」。
- JD 出现「顶会/顶刊/高水平论文」条款（无论放在加分项还是优先项）：竞争分封顶 3，推荐标签最高 `conditional`。
- 薪资与加班必须区分证据等级：`Official / Reported / Market estimate / Inference / Unknown`，没有可靠数据就写 `Unknown`，不编数字。
- WLB 优先：默认先评工作可持续性（加班/出差/值班），再评薪资与成长。

---

## 输出说明

每次调研结束会得到：

1. **核对信息表**：公司、校招状态、官方入口、在招规模、城市、截止时间；
2. **岗位排名表**：Fit / Job quality / Application value / 强度 / 建议标签；
3. **每个岗位的明细块**：匹配证据、最大缺口、薪资成长（起薪→2-3 年→3-5 年）、职业发展（2-3 年学习 / 3-5 年出口 / 天花板与风险）；
4. **证据覆盖表**：官方在招、公众号、薪资、工时、稳定性、出口各由哪些信源支撑；
5. **48 小时行动清单**：先投什么、简历怎么改、面试补什么、投前要确认什么。

配合 `save=<path>` 可把报告保存为 Markdown；配合台账脚本可把结果写入 Excel 岗位跟踪表（每家公司一行，保留核验日期与证据来源）。

---

## 自定义与扩展

- **改权重/评分规则**：编辑 `references/evaluation.md`，不要直接改 SKILL.md 里的引用说明。
- **改输出格式**：编辑 `references/output-template.md`。
- **改信源与交叉验证策略**：编辑 `references/source-playbook.md`。
- **查公司招聘系统接口**：Moka / 北森 zhiye / 自建系统等已实测接口见 `references/ats-reverse-engineering.md`。
- **改个人偏好规则**：编辑 `profiles/default.yaml` 的 `preferences` 与 `constraints`；注意 SKILL.md 里的硬规则（顶会降级、官方 ATS 优先）默认不可绕过，如需修改请先确认自己的真实需求。
- **新增公司支持**：如果某家公司的招聘系统（Moka / 北森 / 自建）已在本 Skill 的参考资料之外，可在 `references/source-playbook.md` 里补充该 ATS 的域名与接口特征，方便下次复用。

---

## 常见问题

### 1. 网络不可用 / 搜索工具失效

Skill 会降级为 `offline analysis`：只分析你提供的岗位链接、截图或 JD 文本，并明确标注知识截止，绝不把记忆里的岗位当作当前在招。

### 2. 官方页面打不开，只有高校就业网/聚合站信息

状态最多标为 `Likely open` 或 `Unverified`，不会写进「已验证」推荐组；你可以之后重开官方页面刷新。

### 3. 本机没有 Python

四个及以上岗位的评分脚本无法运行时，Skill 会按 `evaluation.md` 的公式手算，并在报告中标注「人工计算」，不会静默跳过。

### 4. 代理/网络问题（Windows 用户常见）

如果你的 git 全局配置了本地代理（如 `http://127.0.0.1:<代理端口>`）但代理没开，git 操作会失败；可临时用 `git -c http.proxy= -c https.proxy= push ...` 绕过，或启动代理后重试。

### 5. 隐私

个人档案（`profiles/default.yaml`）默认不提交到本仓库；如果 fork 或公开发布，请检查自己的档案是否被 `.gitignore` 排除。

---

## 许可

本仓库暂未指定开源许可证。如需对外使用，请先根据你的发布意图添加 LICENSE 文件。
