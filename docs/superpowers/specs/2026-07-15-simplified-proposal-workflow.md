# 解决方案专家简化工作流设计

> 状态：当前设计基线  
> 日期：2026-07-15  
> 替代：2026-06-18 版本中的 9 Skill 串行提案流程

## 一、设计目标

将原先 9 个串行 Skill 简化为 3 个业务级 Skill，减少重复理解、重复生成和无效状态传递；同时把研究、检索、输出和归档放回正确的工具或生命周期边界。

核心原则：

1. Skill 代表一次完整、可解释的业务判断，不代表每个代码步骤；
2. 提案只维护一份 `proposal_spec`，正文、页面和格式输出共享同一事实源；
3. 研究深度按项目选择，不强制每次刷新全部小红书数据；
4. 审核前不创建对外文件；
5. 没有真实审核意见和项目结果时，不得写入复盘知识库。

## 二、目标流程

```text
用户输入 / RFP
      ↓
S1 需求简报
      ├─ 关键信息不足 → awaiting_input → 结束本次运行
      └─ 信息足够 → 选择 fast / full 研究模式
      ↓
S2 决策洞察
      ├─ fast：现有需求与知识框架
      └─ full：调用小红书研究工具
      ↓
S3 方案生成
      ├─ 内部调用案例检索工具
      └─ 生成唯一 proposal_spec + 10 页审核稿
      ↓
awaiting_review
      ├─ 驳回 → revision_required
      └─ 通过 → 按需调用 Slides / Docx / PPTX 输出工具
      ↓
项目结束并取得结果
      ↓
复盘归档事件
```

## 三、能力边界

| 类型 | 能力 | 是否进入主流程 |
|------|------|----------------|
| Core Skill | 需求简报 | 是 |
| Core Skill | 决策洞察 | 是 |
| Core Skill | 方案生成 | 是 |
| Tool | 小红书研究采集 | 按需 |
| Tool | 案例检索 | 由方案生成内部调用 |
| Tool | 格式输出 | 审核通过后调用 |
| Lifecycle | 复盘归档 | 项目结束后独立调用 |

## 四、统一状态

主流程只维护以下核心字段：

```text
user_input
brief
research_mode
research_data
decision_map
limitations
proposal_spec
review_status
outputs
archive_result
```

旧状态中的 `opportunity_result`、`requirement_document`、`client_insight`、`full_proposal`、`slides` 等不再分别作为事实源。

## 五、API 生命周期

### 生成审核稿

`POST /api/proposal/generate`

- 返回 `awaiting_input`：信息不足；
- 返回 `awaiting_review`：已生成审核稿；
- 不在此接口执行格式输出或归档。

### 审核与输出

`POST /api/proposal/{request_id}/review`

- 驳回：进入 `revision_required`；
- 通过：根据请求格式调用输出工具；
- 默认只输出 PPTX，避免无条件同时创建三种文件。

### 项目归档

`POST /api/proposal/{request_id}/archive`

- 仅接受已经审核通过的方案；
- 必须提供真实 `bid_result` 或项目结果；
- 失败时不得伪装成归档成功。

## 六、兼容与迁移

旧的 `skills/s1_*.py` 至 `skills/s9_*.py` 暂时保留，作为研究、案例、输出和归档工具的兼容实现。新主流程不再直接串联这些文件。

待以下条件满足后再删除旧代码：

1. 新三步工作流测试稳定；
2. 前端不再依赖九阶段数据；
3. 输出与归档工具已有独立测试；
4. 数据库连接和持久化实现完成；
5. 历史 API 调用方完成迁移。
