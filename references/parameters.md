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

## Examples

```text
$job-fit-research company=华为,中兴,西门子 role=产品经理,解决方案 graduation=2027 city=上海,杭州 count=8
```

```text
$job-fit-research ownership=国企,央企 industry=云计算,智能制造 max_intensity=3 salary_min=180000 count=10
```

```text
$job-fit-research 外企优先，上海或苏州，不要纯开发岗，可以接受数据分析和AI产品实习，要求有留用机会
```

```text
$job-fit-research profile=/absolute/path/profile.yaml company=字节跳动 source_depth=deep
```

```text
$job-fit-research 对比 previous-jobs.json，只报告新开放、关闭和截止日期变化的岗位
```

```text
$job-fit-research company=西门子,施耐德 source_depth=deep require_official=yes，交叉验证薪资、工时和留用情况
```

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
