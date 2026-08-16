# Parameters and invocation

## Input precedence

Use this order when values conflict:

1. explicit constraints in the current invocation;
2. current conversation;
3. selected profile file;
4. defaults below.

Treat `must`, `only`, `不接受`, `必须`, and `排除` as hard constraints. Treat `prefer`, `最好`, and `优先` as soft preferences.

## Defaults

- Search date: current system date.
- Profile: `profiles/default.yaml` if it exists.
- Graduation year: profile value.
- Major: profile value; if unset, do not assume any major restriction.
- Batch: early, autumn, spring, and internship-conversion routes; label each accurately.
- Employment: full-time; include internships only when conversion routes are requested or no formal foreign-company batch is open.
- Ownership: any, but preserve requested category coverage.
- Freshness: 90 days for campaign announcements and 45 days for individual role pages, unless the page itself shows a future deadline.
- Count: 8 roles for a broad request; 1–3 roles per company in company mode.
- Language: match the user.
- Results: current or likely-open roles only. Put pipelines in a separate section.
- Source depth: `standard` for all roles and `deep` for the final top three.
- Official requirement: prefer official vacancy evidence; allow a government/university mirror as `Likely open` when the employer page is inaccessible.

## Accepted natural-language filters

Normalize common expressions:

| User wording | Filter |
|---|---|
| 国企、央企 | `ownership=state-owned,central-soe` |
| 外企、欧美企业 | `ownership=foreign` |
| 不太卷、WLB | `max_intensity=3` as a soft preference unless explicitly mandatory |
| 不想写太多代码 | favor product, solution, evaluation, consulting, operations; do not automatically exclude all technical roles |
| 提前批 | `batch=early`; do not silently substitute autumn recruitment |
| 留用实习 | `batch=intern-conversion employment=internship` |
| 应届生 | match graduation-year eligibility, not merely “0–3 years” |
| 薪资20万以上 | compare estimated annual total cash, and distinguish base salary from total compensation |
| 只要官网确认 | `require_official=yes` |
| 多找信源、深度调查 | `source_depth=deep` |
| 快速看看 | `source_depth=quick` |
| 法学/法务/合规 | `major=法学 role=法务,合规,知识产权` |
| 医药/临床/药企 | `major=药学,临床医学 role=医学信息,药物警戒,医药代表` |
| 会计/金融 | `major=会计,金融 role=财务,审计,风控,投研` |
| 设计/艺术 | `major=设计 role=UI,UX,平面,陈列,工业设计` |

## Examples

```text
$job-fit-research company=星河科技,蓝云集团 role=算法工程师,产品经理 graduation=2028 city=成都,武汉 count=8
```

```text
$job-fit-research company=星河科技,蓝云集团 role=法务,合规,市场 graduation=2028 major=法学
```

```text
$job-fit-research major=会计,金融 role=财务,审计,风控 city=成都,武汉 source_depth=standard
```

```text
$job-fit-research ownership=国企,央企 industry=云计算,智能制造 max_intensity=3 salary_min=180000 count=10
```

```text
$job-fit-research 外企优先，上海或苏州，不要纯开发岗，可以接受数据分析和AI产品实习，要求有留用机会
```

```text
$job-fit-research profile=/absolute/path/profile.yaml company=远山智能 source_depth=deep
```

```text
$job-fit-research 对比 previous-jobs.json，只报告新开放、关闭和截止日期变化的岗位
```

```text
$job-fit-research company=星河科技,蓝云集团 source_depth=deep require_official=yes，交叉验证薪资、工时和留用情况
```

## 专业 → 岗位族速查（示例词典）

以下仅为常用映射示例，实际以 JD 原文和候选人档案为准：

| 专业/背景 | 常见岗位族 |
|---|---|
| 法学 | 法务、合规、知识产权、律师助理、争议解决 |
| 会计/金融 | 财务、审计、风控、投研、资金管理 |
| 医学/药学 | 医学信息、药物警戒、医药代表、临床协调、医学写作 |
| 设计/艺术 | UI/UX、平面、陈列、工业设计、游戏美术 |
| 教育/师范 | 教研、课程产品、培训、教育运营 |
| 土木/机械/电气 | 工程、工艺、设备、项目、质量管理 |
| 新闻/中文/传播 | 内容、文案、运营、公关、品牌 |
| 市场/广告 | 市场、品牌、投放、渠道、数据分析 |

## Company mode

For each specified company:

1. locate its official China or global careers portal;
2. identify the relevant graduate campaign;
3. open role-level pages;
4. check subsidiary, city, graduate-year and language restrictions;
5. report at least one of: verified role, pipeline route, no matching role, or insufficient evidence.
6. deep-check compensation, workload, business-unit relevance, and exit paths for the best matching role.

Never omit a requested company merely because nothing was found.

## Filter mode

Create a query matrix across:

- employer type;
- preferred roles and synonyms;
- cities;
- graduation year and batch naming;
- official ATS domains and university/government mirrors.

Stop when:

- the requested number of independently verified roles is reached; or
- additional searches produce only duplicates, expired pages, reposts, or hard-ineligible roles.

Explain which condition ended the search.

## Source depth

- `quick`: verify the opening with one high-authority source; give only clearly supported quality signals and mark gaps.
- `standard`: verify the opening, add at least two independent source families for job quality, and disclose contradictions.
- `deep`: use an official vacancy anchor plus claim-specific sources for compensation, workload, ownership, business stability, and exits; target at least four independent source families.

Never lower verification standards merely to satisfy `count`. If `require_official=yes`, exclude roles without an accessible employer/ATS role page from the ranked shortlist and place official campaign-only results in a separate watchlist.
