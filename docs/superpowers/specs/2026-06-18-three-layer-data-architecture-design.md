# 三层数据架构设计文档

> 版本: 1.0 | 日期: 2026-06-18 | 状态: 已确认

---

## 一、项目背景

### 1.1 需求来源

为解决方案专家 Agent 搭建三层数据架构，支撑提案生成全流程的数据存取需求。数据源为飞书历史文档（25份提案/通案/案例）和小红书公开数据实时采集。

### 1.2 设计目标

| 层级 | 定位 | 核心职责 |
|------|------|----------|
| 原始数据层（L1） | 原材料仓库 | 飞书文档原文 + 小红书采集数据，只存不改 |
| 知识层（L2） | 弹药库 | 从原始数据中蒸馏结构化知识，供 Agent 检索调用 |
| 记忆层（L3） | 长期记忆 | 用户偏好 + 客户操作历史，让 Agent 越用越懂用户 |

### 1.3 数据源范围

- 飞书文件夹 `EmcZfzpSul8rCcdhXvhcKpgWn7g` 中全部文档（25 份有效文件）
- 小红书公开数据采集（行业关键词笔记 / 竞品品牌账号 / 客户账号诊断）

---

## 二、方案选型：混合式存储（方案 C）

基于现有 Docker Compose 基础设施（PostgreSQL + Qdrant + Redis），不引入新组件，新增 6 张表 + 2 个 Qdrant collection。

| 层级 | 存储引擎 | 新增内容 |
|------|----------|----------|
| 原始数据层 | PostgreSQL + 文件系统 | 2 张表：`raw_documents`、`raw_xhs_data` |
| 知识层 | Qdrant + PostgreSQL | 2 个新 collection + 1 张表：`knowledge_relations` |
| 记忆层 | PostgreSQL + Redis | 2 张表：`user_preferences`、`session_memory` |

**与现有系统的关系**：现有 4 张表（brand_info / case_labels / proposal_records / review_records）和 6 个 Qdrant collection 全部保留，新表作为扩展而非替换。

---

## 三、原始数据层（L1）详细设计

### 3.1 表：`raw_documents` — 飞书文档原文

```sql
CREATE TABLE raw_documents (
    id SERIAL PRIMARY KEY,
    doc_name VARCHAR(500) NOT NULL,
    doc_type VARCHAR(50) NOT NULL,          -- slides / docx / file
    source_folder VARCHAR(300),              -- 来源文件夹路径
    feishu_token VARCHAR(200),               -- 飞书文件 token
    feishu_url VARCHAR(500),                 -- 飞书文件链接
    content TEXT NOT NULL,                   -- 文档完整 Markdown 内容
    collected_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_raw_docs_type ON raw_documents(doc_type);
CREATE INDEX idx_raw_docs_folder ON raw_documents(source_folder);
```

**字段说明**：

| 字段 | 说明 | 示例 |
|------|------|------|
| doc_name | 飞书中的文件名 | "飞鹤繁星计划升级方案" |
| doc_type | 文件类型 | slides / docx / file |
| source_folder | 从哪个文件夹来 | "飞鹤" / "行业通案/汽车类" |
| feishu_token | 飞书文件 token | "W0SGsB97nluTuHdNKrmcXaGMn0c" |
| feishu_url | 飞书文件链接 | "https://ycnm3444stv0.feishu.cn/slides/..." |
| content | 文档完整文本 | 通过 lark-cli docs +fetch 拉取的 Markdown |

### 3.2 表：`raw_xhs_data` — 小红书采集数据

```sql
CREATE TABLE raw_xhs_data (
    id SERIAL PRIMARY KEY,
    collect_type VARCHAR(50) NOT NULL,       -- industry / competitor / client
    target_name VARCHAR(200) NOT NULL,       -- 行业名 / 品牌名 / 客户名
    keywords JSONB DEFAULT '[]',             -- 搜索关键词列表
    notes JSONB DEFAULT '[]',                -- 笔记列表（标题/互动量/作者/链接）
    comments JSONB DEFAULT '[]',             -- 评论数据
    analysis JSONB DEFAULT '{}',             -- LLM 分析结果
    collected_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_xhs_type ON raw_xhs_data(collect_type);
CREATE INDEX idx_xhs_target ON raw_xhs_data(target_name);
CREATE INDEX idx_xhs_collected ON raw_xhs_data(collected_at);
```

**字段说明**：

| 字段 | 说明 | 示例 |
|------|------|------|
| collect_type | 采集类型 | industry / competitor / client |
| target_name | 采集目标 | "母婴" / "伊利" / "飞鹤" |
| keywords | 搜索关键词 | ["宝宝奶粉怎么选", "奶粉测评"] |
| notes | 笔记列表 | JSON 数组，每项含 title/likes/comments/collects/author/url |
| comments | 评论数据 | JSON 数组，每项含 content/likes/author |
| analysis | LLM 分析结果 | content_themes/audience_interest/hot_elements/sentiment/content_gap |

### 3.3 文件存储

PPTX、PDF、图片等大文件不存数据库，存储到 `/data/raw/` 目录，按来源文件夹组织：

```
/data/raw/
├── feishu/
│   ├── 行业通案/
│   │   ├── 母婴/
│   │   ├── 大健康/
│   │   ├── 家居家装/
│   │   └── 汽车类/
│   ├── 飞鹤/
│   └── ...
├── xhs/
│   ├── industry/
│   ├── competitor/
│   └── client/
└── uploads/          # 用户手动上传
```

---

## 四、知识层（L2）详细设计

### 4.1 8 个 Qdrant 向量集合

基于飞书文档内容分析，从现有 6 个 collection 扩展为 8 个：

| 序号 | 集合名称 | 向量维度 | 内容来源 | 使用场景 |
|------|----------|----------|----------|----------|
| 1 | industry_strategy（已有） | 1024 | 行业通案中的洞察和方法论 | S3 行业洞察 |
| 2 | competitor_analysis（已有） | 1024 | 提案中的竞品对标 + 小红书实时采集 | S3 竞品分析 |
| 3 | growth_model（已有） | 1024 | KOS矩阵方法论、繁星计划方案 | S4 客户洞察 |
| 4 | product_solution（已有） | 1024 | 内容罗盘、账号托管、AI Service | S5 方案设计 |
| 5 | case_labels（已有） | 1024 | 飞鹤/林氏/老庙/蒙牛等成功案例 | S6 案例匹配 |
| 6 | proposal_review（已有） | 1024 | 复盘报告中的经验教训 | S9 复盘归档 |
| 7 | brand_knowledge（新增） | 1024 | 产品卖点、品牌故事、合规话术、评论模板 | S7 内容生成 |
| 8 | xhs_insights（新增） | 1024 | 小红书采集分析结果（爆文特征/舆情/内容空白） | S3 行业洞察 |

### 4.2 表：`knowledge_relations` — 知识关联关系

```sql
CREATE TABLE knowledge_relations (
    id SERIAL PRIMARY KEY,
    source_type VARCHAR(50) NOT NULL,         -- 知识类型
    source_id VARCHAR(200) NOT NULL,          -- 知识点标识
    target_type VARCHAR(50) NOT NULL,         -- 关联知识类型
    target_id VARCHAR(200) NOT NULL,          -- 关联知识点标识
    relation_type VARCHAR(100) NOT NULL,      -- 关系类型
    weight FLOAT DEFAULT 1.0,                -- 关联权重
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_kr_source ON knowledge_relations(source_type, source_id);
CREATE INDEX idx_kr_target ON knowledge_relations(target_type, target_id);
```

**关系类型示例**：

| 关系类型 | 说明 | 示例 |
|----------|------|------|
| belongs_to | 归属关系 | "飞鹤案例" belongs_to "母婴行业策略" |
| applied_in | 应用关系 | "KOS矩阵增长模型" applied_in "飞鹤繁星计划方案" |
| similar_to | 相似关系 | "飞鹤方案" similar_to "金领冠方案" |
| competes_with | 竞品关系 | "伊利" competes_with "飞鹤" |

### 4.3 知识蒸馏流程

```
飞书文档 → lark-cli docs +fetch 拉取原文
    → 存入 raw_documents（L1）
    → 触发 LLM 提取关键知识点
    → 生成向量嵌入 → 存入对应 Qdrant collection
    → 提取实体关系 → 写入 knowledge_relations 表
```

小红书采集数据同理：采集 → 存 L1 → LLM 分析 → 存 L2 的 xhs_insights 集合。

---

## 五、记忆层（L3）详细设计

### 5.1 表：`user_preferences` — 用户使用习惯

```sql
CREATE TABLE user_preferences (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,            -- 飞书用户 ID
    preferred_industries JSONB DEFAULT '[]',  -- 偏好的行业赛道
    preferred_templates JSONB DEFAULT '[]',   -- 常用提案模板
    budget_range VARCHAR(100),                -- 常用预算档位
    output_formats JSONB DEFAULT '[]',        -- 输出格式偏好
    search_history JSONB DEFAULT '[]',        -- 历史搜索关键词
    interaction_count INTEGER DEFAULT 0,      -- 总交互次数
    last_active_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_up_user ON user_preferences(user_id);
```

**字段说明**：

| 字段 | 说明 | 示例 |
|------|------|------|
| preferred_industries | 偏好的行业 | ["母婴", "大健康"] |
| preferred_templates | 常用模板 | ["KOS矩阵全链路管理通案"] |
| budget_range | 常用预算档位 | "50-200万" |
| output_formats | 输出偏好 | ["slides", "pptx"] |
| search_history | 最近搜索 | ["飞鹤", "繁星计划", "KOS矩阵"] |

### 5.2 表：`session_memory` — 客户操作历史

```sql
CREATE TABLE session_memory (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,         -- 会话标识
    user_id VARCHAR(100) NOT NULL,            -- 操作人
    client_name VARCHAR(200) NOT NULL,        -- 客户名称
    industry VARCHAR(100),                    -- 行业
    stage VARCHAR(50),                        -- 当前阶段
    proposal_id INTEGER REFERENCES proposal_records(id),
    review_feedback TEXT,                     -- 审核反馈
    bid_result VARCHAR(50),                   -- 中标结果
    key_notes TEXT,                           -- 关键备注
    context JSONB DEFAULT '{}',              -- 完整上下文快照
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_sm_session ON session_memory(session_id);
CREATE INDEX idx_sm_client ON session_memory(client_name);
CREATE INDEX idx_sm_user ON session_memory(user_id);
```

**字段说明**：

| 字段 | 说明 | 示例 |
|------|------|------|
| session_id | 会话标识 | "sess_feihe_20260618_001" |
| client_name | 客户名称 | "飞鹤" |
| stage | 当前阶段 | "s5_proposal_design" |
| review_feedback | 审核反馈 | "预算部分需要细化，竞品对标数据太旧" |
| bid_result | 中标结果 | "中标" / "丢单" / "进行中" |
| context | 完整上下文快照 | AgentState 序列化 JSON |

### 5.3 Redis 缓存策略

| 缓存类型 | Key 格式 | TTL | 说明 |
|----------|----------|-----|------|
| 当前会话 | `session:{session_id}` | 24h | 正在进行的 Agent 会话状态 |
| 用户偏好 | `user_pref:{user_id}` | 1h | 热数据缓存，命中直接返回 |
| 客户历史 | `client:{client_name}` | 30min | 最近操作的客户上下文 |
| 知识检索 | `search:{query_hash}` | 10min | 重复查询的向量检索结果 |

---

## 六、数据流与集成

### 6.1 数据流向

```
飞书文件夹 / 小红书
        │
        ▼
┌─────────────────┐
│  原始数据层 (L1)  │  ← 只存不改，保持原样
│  raw_documents   │
│  raw_xhs_data    │
└────────┬────────┘
         │ 知识蒸馏（LLM 提取 + 向量化）
         ▼
┌─────────────────┐
│   知识层 (L2)    │  ← 结构化 + 可检索
│  8 个 Qdrant 集合 │
│  knowledge_relations │
└────────┬────────┘
         │ Agent 交互沉淀
         ▼
┌─────────────────┐
│   记忆层 (L3)    │  ← 偏好 + 历史
│  user_preferences│
│  session_memory  │
│  Redis 缓存      │
└─────────────────┘
```

### 6.2 与 Agent Skill 的集成点

| Skill | 读取 L1 | 读取 L2 | 写入 L3 |
|-------|---------|---------|---------|
| S2 需求诊断 | 读取品牌信息 | 检索 brand_knowledge | 更新 search_history |
| S3 行业洞察 | 读取 raw_xhs_data | 检索 industry_strategy / competitor_analysis / xhs_insights | — |
| S4 客户洞察 | — | 检索 growth_model | — |
| S5 方案设计 | — | 检索 product_solution / industry_strategy | — |
| S6 案例匹配 | — | 检索 case_labels | — |
| S7 内容生成 | 读取 raw_documents | 检索 brand_knowledge / proposal_review | — |
| S8 格式输出 | — | — | 记录输出格式偏好 |
| S9 复盘归档 | — | 更新 proposal_review | 更新 session_memory / user_preferences |

### 6.3 定时任务

| 任务 | 频率 | 说明 |
|------|------|------|
| 飞书文档增量同步 | 每日 2:00 | 检测飞书文件夹新增/修改，拉取原文入 L1 |
| 小红书数据采集 | 每日 3:00 | 按行业关键词采集最新笔记，入 L1 → 蒸馏入 L2 |
| 知识蒸馏 | 文档/采集完成后 | 触发 LLM 提取知识点，更新 L2 |
| Redis 热数据刷新 | 每小时 | 将高频访问的 L2 检索结果预加载到 Redis |

---

## 七、与现有系统的兼容性

### 7.1 保留不变

- 现有 4 张表（brand_info / case_labels / proposal_records / review_records）
- 现有 6 个 Qdrant collection（industry_strategy / competitor_analysis / growth_model / product_solution / case_labels / proposal_review）
- 现有数据库连接配置（database.py）
- 现有 Celery Worker 和 Scheduler

### 7.2 需要修改

| 文件 | 修改内容 |
|------|----------|
| `db/init.sql` | 追加 6 张新表的 DDL |
| `db/models.py` | 追加 6 个 Pydantic 模型 |
| `vector_store/client.py` | 追加 2 个新 collection 的初始化 |
| `material_libraries/loader.py` | 新增知识蒸馏逻辑（文档 → 向量 → 关系表） |
| `agent.py` | AgentState 新增 memory 相关字段 |
| `skills/s3_industry_insight.py` | 保存原始采集数据到 raw_xhs_data |
| `skills/s9_archive.py` | 写入 session_memory 和 user_preferences |
| `docker-compose.yml` | 无需修改 |

---

## 八、验收标准

| 验收项 | 标准 |
|--------|------|
| 飞书文档导入 | 25 份文档原文全部存入 raw_documents |
| 小红书采集存储 | 采集数据存入 raw_xhs_data，JSON 结构完整 |
| 知识蒸馏 | 8 个 Qdrant collection 均已初始化并包含知识条目 |
| 知识关联 | knowledge_relations 表包含行业-案例-方案之间的关联 |
| 用户偏好 | user_preferences 正确记录行业偏好和模板偏好 |
| 会话记忆 | session_memory 记录每次提案的完整上下文 |
| 缓存策略 | Redis 热数据命中率 > 60% |
| 兼容性 | 现有 17 个测试全部通过，新增表不影响旧功能 |