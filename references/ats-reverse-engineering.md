# ATS 逆向速查表（已实测）

本文档汇总在真实校招核验中验证过的招聘系统接口特征，用于快速定位「某家公司岗位是否在招」的官方数据源。

> 使用边界：只用于读取公开岗位信息。不要写入账号 Cookie、Token、验证码等敏感内容；不要绕过登录态去获取非公开数据。

## 0. 通用方法论

1. 打开官网首页，抓取 HTML，找 `<script src=...>` 入口 JS。
2. 下载入口 JS，搜索 `baseURL`、`/api/`、`position`、`list`、`search`、`query` 等关键词定位接口路径。
3. 纯前端路由（`#/xxx`）的页面逻辑通常在按需加载的 chunk 里：
   - 从 webpack 加载器（形如 `c.u=function(t){...}` / `e.u=function`）解析「chunk 名 → hash」映射；
   - 拼出 chunk URL（常见格式 `{name}-{hash}.chunk.min.js` 或 `{id}.{hash}.js`）；
   - 下载对应页面 chunk，看它实际调用的接口和请求参数。
4. 用常见路径探测：`/api/position/list`、`/api/job/list`、`/api/Jobad/GetJobAdPageList`、`/api/outer/ats-apply/website/jobs/v2` 等。
5. 分页：优先 `pageSize=200~1000` 一次拉全量；不行就循环 `pageNum/offset`。
6. 返回乱码时依次尝试 `utf-8 / gbk / latin1` 解码。
7. 只有「官方 ATS 返回 status=open/在招 + 岗位 ID + 发布时间」才标 `Open—verified`；页面打不开时降级为 `Likely open / Unverified`。

## 1. Moka（app.mokahr.com 或公司自有域）

已实测：货拉拉 `huolalahr/98660`、安踏集团 `antahr/142914`（campus.anta.com）。

### 站点特征

- URL：`https://app.mokahr.com/campus-recruitment/<orgId>/<siteId>`，或公司自有域 `https://<company>.com/campus-recruitment/<orgId>/<siteId>/`。
- 公司官网的「校园招聘」导航可能指向 Moka 短链（`app.mokahr.com/su/<code>`）或直接跳转 Moka 站点。

### 岗位列表

```http
POST /api/outer/ats-apply/website/jobs/v2
Host: app.mokahr.com（或公司自有域）
Content-Type: application/json;charset=UTF-8
Origin / Referer: 站点 URL
```

请求体：

```json
{
  "orgId": "<orgId>",
  "siteId": "<siteId>",
  "limit": 30,
  "offset": 0,
  "needStat": true,
  "jobIdTopList": [],
  "departmentIds": [],
  "customFields": {},
  "site": "campus",
  "locale": "zh-CN"
}
```

响应为加密 JSON：`data` 是 base64，`necromancer` 是密钥。

```text
算法：AES-CBC
IV：de7c21ed8d6f50fe（utf-8）
密钥：Buffer.from(resp.necromancer, "utf-8")
  长度 32 → aes-256-cbc
  长度 16 → aes-128-cbc
```

解密后关键字段：`jobStats.total`（总数）、`jobs[]`（`id/title/zhineng/commitment/locations/status/openedAt/publishedAt/jobDescription`）。

### 岗位详情

```http
POST /api/outer/ats-apply/website/job
```

请求体：

```json
{
  "orgId": "<orgId>",
  "isInviteResume": false,
  "jobId": "<jobId>",
  "siteId": "<siteId>",
  "locale": "zh-CN"
}
```

加密方式同上。

### 实用提示

- 用 `zhineng.name`（算法类/开发类/产品类）和 `commitment`（全职/实习）过滤。
- `status=open` 表示在招；`closedAt` 用于判断是否已关闭。
- 部分站点 URL 带 `?project=<id>` 项目过滤；若接口支持，在请求体加 `projectId`。
- 同一公司可能有多个 `siteId`，官网导航里逐条找。

## 2. 北森 zhiye（xxx.zhiye.com / join.xxx.cn）

已实测：奥马冰箱 `homa-hr.zhiye.com`；货拉拉官网 `join.huolala.cn`（社招，校招跳 Moka）。

### 站点特征

- 首页 HTML 内嵌 `var BSGlobal = {...}`，包含：
  - `PortalId`（站点唯一标识）；
  - `tenantInfo.Id`（租户 ID，出现在图片/CDN 路径）；
  - `staticPath`（前端静态资源路径）；
  - 导航配置（含「校园招聘」等页面的 PageId）。
- 静态资源特征：`stcms.beisen.com`、`portal-oss.zhiye.com`、`acdn.bstatics.com`。

### 岗位列表

```http
POST /api/Jobad/GetJobAdPageList
Content-Type: application/json;charset=UTF-8
Origin / Referer: 站点 URL
```

请求体（校招）：

```json
{
  "PortalId": "<PortalId>",
  "PageIndex": 0,
  "PageSize": 100,
  "BusinessType": 2,
  "Category": ["2"],
  "KeyWords": "",
  "SpecialType": 0
}
```

参数说明：

| 参数 | 含义 | 备注 |
|---|---|---|
| `BusinessType` | 2=校招 | 不带时可能返回全量（含社招） |
| `Category` | ["2"]=校园招聘分类 | 奥马返回 28 岗；不带 Category 会混入社招 |
| `PageIndex` | 从 0 开始 | |

返回字段（列表自带完整 JD）：`JobAdId / JobAdName / LocNames / Kind / Duty / Require / ChangeDate / EndTime / Status / Degree`。

### 岗位详情

```http
POST /api/Jobad/GetJobAdDetail
```

请求体：`{ "JobAdId": "<id>", "Id": "<id>", "PortalId": "<PortalId>" }`

> 部分站点（如奥马）该接口返回 500，但列表接口已自带 `Duty/Require`，直接用列表字段即可。

### 实用提示

- 前端 chunk 命名：`staticPath + "{chunk名}-{hash}.chunk.min.js"`；webpack 加载器里有两个 map（chunk 名 map + hash map）。
- 货拉拉官网虽然是北森门户，但其「校园招聘」导航 URL 指向 Moka——先看导航配置，别在北森接口里找校招。

## 3. 自建系统：顺丰科技（campus.sf-express.com）

### 站点特征

- 纯前端 SPA；JS 在 `/cr/static/js/app.<hash>.js`，chunk 由 `manifest.<hash>.js` 提供（`{id}.{hash}.js`）。
- API base：`window.location.protocol + "//" + host + "/api/"`。

### 岗位列表

```http
GET /api/web/position/query?pageNum=1&pageSize=200&time=<毫秒时间戳>
```

必须带请求头：

```http
cr-service: https%3A%2F%2Fcampus.sf-express.com%2F
Referer: https://campus.sf-express.com/positionList
Origin: https://campus.sf-express.com
```

返回分页 JSON：`list[] / total`。字段：`id / positionName / demandCity / educationName / seasonType(2=应届) / postDuty / jobRequirement / createDate / orgSource`。

筛选项字典：`GET /api/web/position/queryDict/<category>`（`intern`、`positionType`、`workCity` 等）。

### 实用提示

- `orgSourceName` 区分主体（顺丰科技 / 顺丰总部）。
- 岗位详情页 `/postDetail/<id>`，投递页 `/apply?id=<id>`。

## 4. 自建系统：大华股份（job.dahuatech.com）

### 站点特征

- SPA；入口 `app.<hash>.js`，页面 chunk 形如 `chunk-<name>.<hash>.js`（如 CampusPosition 页面 = `chunk-0cd936eb.<hash>.js`）。
- API base：`/talent-pool/api`。

### 岗位列表

```http
POST /talent-pool/api/bs-info/list-position-by-search
```

请求体：

```json
{
  "companyCategory": "",
  "positionCategory": "",
  "workPlaceCode": "",
  "jobTitle": "",
  "recruitType": 2
}
```

`recruitType=2` 表示校招。返回 `data[]`：`id / jobTitle / jobCategroyDescription / workingPlace / publishDate`。

### 岗位详情

```http
POST /talent-pool/api/bs-info/query-position
```

请求体：`{ "id": "<岗位UUID>" }`

返回：`jobTitle / salaryText / endDate / headCount / duty / requirements`。

### 其他接口

- `GET /campus-part/get-label`：导航/标签（校园招聘分类）。
- `POST /campus-part/query-banner`：banner，body `{ "type": 3, "id": <项目id> }`。
- `GET /campus-part/campus-introduce`、`GET /campus-part/home-info`：校招介绍页。

### 实用提示

- URL fragment 里的 `?id=11` 是校招项目 ID，但岗位列表接口不依赖它，直接用 `recruitType=2` 全量拉。
- 投递跳转 `https://dahua.zhiye.com/form?fromPage=job&jobAdId=<id>`。

## 5. 自建系统：腾讯（join.qq.com）

### 岗位列表

```http
POST /api/v1/position/searchPosition
Content-Type: application/json
```

请求体：

```json
{
  "keyword": "",
  "bgList": [],
  "workCountryType": 1,
  "workCityList": [],
  "recruitCityList": [],
  "positionFidList": [],
  "pageIndex": 1,
  "pageSize": 1000,
  "projectId": "1"
}
```

返回 `data.positionList[]`：`postId / positionTitle / workCities / bgs / recruitLabelName`。

### 岗位详情

```http
GET /api/v1/jobDetails/getJobDetailsByPostId?postId=<postId>
```

### 项目映射

```http
GET /api/v1/position/getProjectMapping
```

（例如 `p_9` = AI 产品经理培训生专项。）

### 实用提示

- `projectId` 不支持合并传参（如 `"1,9"` 返回 0）；页面 `query=p_1,p_9` 是前端合并筛选，后端按单 project 分别拉取再合并。
- 用 `recruitLabelName` 区分：「应届毕业生」「应届毕业生 青云计划」「AI产品经理培训生」「应届实习」「实习生 青云计划」「日常实习」。
- 青云计划大量岗位含顶会条款，用正则扫描 `CVPR|ICCV|ECCV|ICML|NeurIPS|TPAMI|ACL|KDD|SIGIR|顶级会议|高水平论文`。

## 6. 已实测公司 → 系统速查

| 公司 | 系统 | 入口 | 关键接口 |
|---|---|---|---|
| 货拉拉 | Moka | `app.mokahr.com/campus-recruitment/huolalahr/98660` | `POST /api/outer/ats-apply/website/jobs/v2` |
| 安踏集团 | Moka | `campus.anta.com/campus-recruitment/antahr/142914` | 同上 |
| 奥马冰箱 | 北森 zhiye | `homa-hr.zhiye.com` | `POST /api/Jobad/GetJobAdPageList` |
| 货拉拉官网 | 北森 zhiye（社招） | `join.huolala.cn` | 同上（校招实际跳 Moka） |
| 顺丰科技 | 自建 | `campus.sf-express.com` | `GET /api/web/position/query` |
| 大华股份 | 自建 | `job.dahuatech.com` | `POST /talent-pool/api/bs-info/list-position-by-search` |
| 腾讯 | 自建 | `join.qq.com` | `POST /api/v1/position/searchPosition` |

## 7. 常见坑

- 官网是北森/自建门户，但「校园招聘」导航指向另一个系统（货拉拉 → Moka）：先解析导航配置再动手。
- 列表接口不带分类参数会混入社招/实习：优先带 `Category` / `recruitType` / `recruitLabelName` 过滤。
- 加密响应（Moka）不解密就以为没数据：用文档里的 IV/算法解密。
- 中文乱码：依次试 `utf-8 / gbk / latin1`，不要凭乱码下结论。
- 岗位「是否在招」以接口 `status=open` / 官方页面为准；聚合站快照只能当线索。
- 顶会条款扫描要覆盖加分项与优先项，不能只看任职要求正文。
