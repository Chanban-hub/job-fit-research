# Evaluation rubric

## Contents

1. Eligibility gate
2. Candidate-fit score
3. Absolute job-quality score
4. Application-value score
5. Opening confidence
6. Work intensity
7. Compensation
8. Career prospects
9. Ranking JSON schema

## 1. Eligibility gate

Check before scoring:

- graduation year or permitted graduation window;
- degree level;
- required major or professional qualification;
- language requirement;
- location or work authorization;
- internship duration and days per week when applicable.

Mark `hard_gate_failed: true` only when a stated mandatory requirement is not met. Unclear evidence is not a failed gate; it lowers confidence.

### 列举式技术栈要求（语言/框架清单）

JD 的“任职要求”里逐条列出的技术栈（如“熟练掌握 Python，熟悉 TypeScript/Go/Java 至少一种”“熟练使用 Tornado/Django/Flask 任一”）没有“优先/加分”等软化词时，默认按候选门槛处理：

- 候选人不满足任一列举项：`eligibility` 不得高于 4；若该技能属于岗位核心职责且无任何等效证据，不得高于 3；
- 等价能力替代（如 C++ 代替 Java、FastAPI 代替 Django）：必须在报告 Gap 中标注“未验证等价”，`eligibility` 最高 4，并建议投递前与 HR/招聘者确认后再决定是否投入；
- 完全无法满足且该技能是岗位核心依赖：`hard_gate_failed: true`；
- 每个评分岗位必须在 fit 理由中写明 JD 技术栈清单的逐条勾选结果，缺失项必须进入 Gap，不得因为 Python 强或方向匹配而跳过清单。

### 个人偏好降权（profile 的 `company_scoped_preferences`）

候选档可能声明“某类公司/某类岗位降权”（例如互联网厂产品岗降权）。命中降权范围时：

- `constraints` 不得超过 3，`career` 不得超过 3.5（岗位偏离候选人的目标路径）；
- 推荐标签最高为 `conditional`，不得进入 priority/apply 的常规排序；
- 若同公司存在未命中降权的技术/算法/工程岗位，降权岗位的排名一律置于其后；
- 用户当轮明确点名要该类岗位时，本规则不适用，恢复常规评分。

### 候选人算法岗权重（profile 的 `role_weight_rules`）

候选档可能声明算法岗权重（如“无顶会条款的视觉算法岗均按常规权重评估”）。命中时：

- 视觉算法、大模型算法、端侧/边缘算法岗（JD 无顶会/顶刊条款）按常规 fit/quality 公式评分并参与排序，不因候选人有产品/解决方案倾向而降权；
- 产品/解决方案岗不得自动排在算法岗之前（互联网厂产品岗降权规则仍适用）；
- 算法岗 JD 含顶会条款时，仍执行“顶会条款→competition≤3，最高 conditional”。

## 2. Candidate-fit score

Answer: **How well does this candidate fit this role?**

Score each dimension from 0 to 5.

| Dimension | Weight | 5 | 3 | 0–1 |
|---|---:|---|---|---|
| eligibility | 25% | Meets every gate with direct evidence | Likely eligible; one item unclear | Fails or probably fails a hard gate |
| skills | 25% | Most central duties already demonstrated | Transferable overlap but meaningful learning needed | Core work is outside demonstrated ability |
| evidence | 20% | Multiple quantified, verifiable examples | General experience without strong artifact or metric | Keyword-only or no evidence |
| career | 15% | Directly supports the candidate's target path | Useful but indirect | Pulls the candidate away from the target path |
| competition | 10% | Credible relative to the likely applicant pool | Stretch but plausible | Screening bar is far above current evidence |
| constraints | 5% | Meets personal location, travel, workload and pay needs | One soft tradeoff | Violates a hard personal constraint |

```text
fit = 20 × (
  0.25×eligibility +
  0.25×skills +
  0.20×evidence +
  0.15×career +
  0.10×competition +
  0.05×constraints
)
```

Cap fit at 49 if a hard gate fails.

Fit bands:

- 85–100: excellent fit;
- 70–84: good fit;
- 55–69: plausible with gaps;
- 40–54: weak or stretch;
- below 40: poor fit.

Do not use employer prestige, general pay level, or general stability as fit evidence. Those belong in job quality.

### 顶会/顶刊条款的强制降分（任何出现位置均触发）

只要 JD 出现「顶会/顶刊」「顶级会议/期刊」或点名顶级会议/期刊（ACL、CVPR、ICCV、ECCV、ICML、NeurIPS、TPAMI 等），或出现「高水平论文」等同类表述——无论位于硬性任职要求还是加分项/优先项——且候选人没有顶级论文（普通期刊/会议论文不算顶级），一律按以下规则处理：

1. `competition` 不得超过 3，不得因“仅出现在加分项/优先项”而恢复常规评分（通常 3.5–4 的默认值一律不可用）；
2. 推荐标签最高为 `conditional`，不得标记 `priority` 或 `apply`；即使投递价值 ≥80、适配度 ≥70 或用户当轮点名该岗位，也不得提升标签；`conditional` 以下的标签（stretch/skip）维持原判断；
3. 报告与台账必须在 Gap/理由中标注「顶会条款→competition≤3，最高 conditional」；
4. 本规则只作用于 `competition` 与推荐标签；`skills`、`evidence` 仍按实际证据打分，不得因顶会条款额外加减分；
5. 若 JD 完全没有顶会/顶刊/高水平论文表述，且候选人论文/项目直接对口，`competition` 按实际申请池正常评分，不受本规则限制。

## 3. Absolute job-quality score

Answer: **Is this a good job in itself, independent of this candidate?**

Benchmark a graduate role against reasonably comparable roles:

- same country and city or cost-of-living tier;
- similar degree and experience level;
- same broad role family;
- same recruiting cycle where possible.

Do not compare a Suzhou graduate support role directly with a senior Silicon Valley engineering role.

Score each dimension from 0 to 5.

### WLB-first rule (岗位绝对价值优先 WLB)

Score absolute job quality with WLB as the first criterion:

- Default mode `quality_basis=wlb_first`: sustainability (WLB) has the highest weight. Evaluate working hours, predictability, overtime, travel, on-call and quota pressure before compensation.
- Fallback mode `quality_basis=salary_growth_fallback`: use when sustainability evidence is weak or unknown, or the role's WLB is clearly poor and still being considered. Then judge the job mainly by salary, growth and upward space (晋升通道、职级天花板、外部市场价值), and record the switch and its reason in the report.

Default weights (WLB-first):

| Dimension | Weight | Evaluate |
|---|---:|---|
| sustainability | 25% | Work hours, predictability, overtime, travel, on-call, quota pressure, and physical or emotional load |
| growth | 20% | Mentorship, real ownership, role clarity, learning density, quality of projects, and promotion opportunity |
| compensation | 15% | Guaranteed cash, realistic bonus, benefits, pay transparency, and value relative to the comparable market |
| platform | 15% | Business importance, team resources, data/customer access, brand signal, and internal mobility |
| mobility | 15% | Transferability of skills, external exits, avoidance of proprietary or administrative lock-in |
| stability | 10% | Business health, funding, policy/cycle exposure, layoff or outsourcing risk, and role durability |

Fallback weights (salary + growth + upward space):

| Dimension | Weight | Evaluate |
|---|---:|---|
| compensation | 25% | Guaranteed cash, realistic bonus, benefits, pay transparency, and value relative to the comparable market |
| growth | 25% | Mentorship, real ownership, role clarity, learning density, promotion ladder, ceiling and external market value |
| platform | 15% | Business importance, team resources, data/customer access, brand signal, and internal mobility |
| mobility | 15% | Transferability of skills, external exits, avoidance of proprietary or administrative lock-in |
| sustainability | 10% | Work hours, predictability, overtime, travel, on-call, quota pressure, and physical or emotional load |
| stability | 10% | Business health, funding, policy/cycle exposure, layoff or outsourcing risk, and role durability |

For sustainability, 5 means sustainable and predictable; 0 means chronically damaging or highly unpredictable. Do not insert the raw intensity score without reversing and considering predictability.

```text
raw_quality (wlb_first) = 20 × (
  0.25×sustainability +
  0.20×growth +
  0.15×compensation +
  0.15×platform +
  0.15×mobility +
  0.10×stability
)
```

```text
raw_quality (salary_growth_fallback) = 20 × (
  0.25×compensation +
  0.25×growth +
  0.15×platform +
  0.15×mobility +
  0.10×sustainability +
  0.10×stability
)
```

Give `quality_confidence` from 0 to 5:

- 5: current official compensation plus role/team-specific workload and development evidence;
- 4: several current, consistent and role-specific sources;
- 3: credible comparable evidence with some team uncertainty;
- 2: mostly company-level reports or older comparables;
- 1: sparse anecdotes or broad industry assumptions;
- 0: no responsible basis.

Shrink uncertain estimates toward neutral:

```text
job_quality = 50 + (raw_quality - 50) × quality_confidence / 5
```

If one component is unknown, use 2.5 rather than guessing and reduce `quality_confidence`.

Choose `quality_basis` as follows: default to `wlb_first`; switch to `salary_growth_fallback` only when sustainability evidence cannot be responsibly scored (low workload confidence) or when the role is clearly poor on WLB but remains under consideration on salary/growth grounds. Never switch silently: state the reason in the report and keep the same component scores, only the weights change.

Quality bands:

- 85–100: exceptional;
- 70–84: good;
- 55–69: above average or acceptable with tradeoffs;
- 40–54: below average;
- below 40: poor.

Set `severe_quality_risk: true` only for evidence-backed major risks such as disguised labor dispatch, pay arrears, illegal or misleading recruitment, extreme sustained workload, a collapsing business, or a role with little real work. Cap job quality at 49 and list the evidence. Do not mark a risk severe from one anonymous complaint.

Quality is not moral certainty. State the benchmark, confidence, team/location uncertainty, and the two strongest positive and negative drivers.

## 4. Application-value score

Use this to rank where the candidate should spend application effort:

```text
application_value =
  0.45×fit +
  0.40×job_quality +
  0.15×opening_confidence×20
```

If a hard eligibility gate fails, set application value to 0. A high-quality but low-fit role may still be a worthwhile stretch; a high-fit but poor-quality role should not become a priority.

Recommendation rules:

- `priority`: application value at least 80 and fit at least 70;
- `apply`: application value at least 65 and fit at least 60;
- `stretch`: job quality at least 70 but fit below 60;
- `conditional`: application value at least 50 with a material tradeoff;
- `skip/quality-risk`: job quality below 40 or an evidence-backed severe risk;
- `ineligible`: hard gate failed;
- `skip`: otherwise.

Explain exceptions rather than mechanically following the label.

命中「顶会/顶刊/高水平论文」条款的岗位，即使按公式算出 `priority` 或 `apply`，推荐标签也必须降为 `conditional`（见“顶会/顶刊条款的强制降分”），不得以任何理由例外。

## 5. Opening confidence

Score from 0 to 5:

- 5: official role page, current dates, application action available;
- 4: official campaign plus active ATS list, role status slightly unclear;
- 3: current university/government posting with direct company application path;
- 2: current reputable job platform or recruiter repost only;
- 1: old, cached, or undated secondary evidence;
- 0: closed, contradicted, or not found.

A recommendation normally requires at least 3. Separate 1–2 into “needs verification.”

## 6. Work intensity

Give one rating from 1 to 5 and a confidence level.

WLB is the first criterion of absolute job quality: score work intensity with the same evidence discipline as compensation. If workload evidence is too weak for a responsible rating, mark the confidence low and switch to `salary_growth_fallback` instead of guessing.

Evaluate:

- explicit hours, shifts, on-call or overtime;
- delivery or launch cycles;
- travel and customer-site work;
- performance competition or sales quota;
- incident responsibility;
- regional and team variation.

Interpretation:

- 1: predictable schedule, rare deadline peaks;
- 2: generally regular with occasional peaks;
- 3: recurring project peaks, travel, or limited on-call;
- 4: frequent peaks, high delivery pressure, substantial travel, or regular overtime;
- 5: sustained high pressure, intense performance competition, or heavy on-call.

Label facts and inference separately. Employer-wide culture reports cannot prove a specific team's hours.

## 7. Compensation

Always state compensation type and confidence:

- `Official—high`: current role gives a range or package.
- `Comparable—medium`: same company, city, level, and similar role within two recruiting cycles.
- `Reported—low/medium`: dated employee offer or compensation database with sample limitations.
- `Estimated—low`: industry/city estimate only.
- `Unknown`: no responsible range available.

Normalize when possible:

- monthly base × months;
- target bonus versus guaranteed pay;
- annual total cash;
- equity, sign-on, subsidy and benefits separately;
- internship daily or monthly pay separately from graduate pay.

Never combine incompatible evidence into a precise single number. Give a range and name the largest uncertainty.

每个岗位必须同时给出「薪资成长」结论：起薪总包 → 2–3 年（调薪/职级/绩效）→ 3–5 年出口预期，每段标注 `Official` / `Reported` / `Market estimate` / `Inference` / `Unknown`。不得编造精确数字；无证据时写区间并标 `Unknown`，说明最大不确定性。

## 8. Career prospects

Distinguish:

- candidate-specific alignment, which belongs in fit;
- general learning, mobility and stability, which belong in job quality.

Explain:

- 2–3 year learning: domain, product ownership, technical depth, customer exposure;
- 3–5 year exits: senior role, adjacent functions, external marketability;
- ceiling: compensation and responsibility;
- lock-in: proprietary stack, narrow industry, administrative work, low ownership;
- resilience: exposure to automation, outsourcing, policy, or cyclical demand.

每个岗位必须输出明确的「职业发展」结论（而非泛泛而谈），至少覆盖：2–3 年学习密度与项目所有权、3–5 年晋升路径与外部出口、天花板/锁定、抗风险能力；无法评估的项写 `Unknown` 并说明原因。

## 9. Ranking JSON schema

Use component scores from 0 to 5:

```json
{
  "jobs": [
    {
      "company": "Example",
      "role": "AI Product Manager",
      "hard_gate_failed": false,
      "severe_quality_risk": false,
      "quality_basis": "wlb_first",
      "fit_scores": {
        "eligibility": 5,
        "skills": 4,
        "evidence": 4,
        "career": 5,
        "competition": 3,
        "constraints": 4
      },
      "quality_scores": {
        "compensation": 4,
        "sustainability": 3,
        "growth": 5,
        "platform": 5,
        "mobility": 5,
        "stability": 4
      },
      "quality_confidence": 3,
      "opening_confidence": 5
    }
  ]
}
```

The script outputs candidate fit, raw and confidence-adjusted job quality, application value, and a recommendation. It places ineligible roles last.
