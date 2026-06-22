# Solution Expert Agent

面向售前团队的自动化提案生成系统，通过 9 个可插拔 Skill 编排完整提案流程。

## 项目结构

```
.
├── SOUL.md                        # Agent 灵魂文档（身份、使命、能力定义）
├── docker-compose.yml             # Docker Compose 编排
├── Makefile                       # 构建/测试/运行快捷命令
├── .env.example                   # 环境变量模板
│
├── docs/                          # 项目文档
│   ├── architecture/              # 架构设计文档
│   └── plans/                     # 实施计划文档
│
├── data/                          # 三层数据架构文件
│   ├── l1/                        # L1 原始数据层（飞书文档、聊天记录）
│   ├── l2/                        # L2 知识层（知识点、关联关系、Qdrant 导入）
│   ├── l3/                        # L3 记忆层（用户偏好、会话记忆）
│   └── three_layer_summary.json   # 三层架构汇总报告
│
├── services/                      # 微服务
│   ├── orchestrator/              # 核心编排服务
│   │   ├── app/                   # FastAPI 应用
│   │   │   ├── db/                # 数据库模型与连接
│   │   │   ├── knowledge/         # 知识蒸馏模块
│   │   │   ├── llm/               # LLM 路由
│   │   │   ├── material_libraries/# 物料库加载器
│   │   │   ├── routers/           # API 路由
│   │   │   ├── vector_store/      # Qdrant 向量存储
│   │   │   ├── agent.py           # LangGraph 9 步工作流
│   │   │   ├── main.py            # FastAPI 入口
│   │   │   ├── scheduler.py       # 定时任务
│   │   │   └── worker.py          # Celery Worker
│   │   ├── skills/                # 9 个可插拔 Skill（S1-S9）
│   │   ├── scripts/               # 数据导入与初始化脚本
│   │   ├── tests/                 # 测试文件
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── web-chat/                  # 前端聊天界面（React + Vite）
│   ├── feishu-bot/                # 飞书机器人服务
│   └── nginx/                     # Nginx 反向代理配置
```

## 三层数据架构

| 层级 | 名称 | 存储 | 内容 |
|------|------|------|------|
| L1 | 原始数据层 | PostgreSQL | 飞书文档原文、聊天记录、小红书采集数据 |
| L2 | 知识层 | Qdrant + PostgreSQL | 结构化知识点、9 大知识集合、关联关系 |
| L3 | 记忆层 | PostgreSQL + Redis | 用户偏好、会话历史 |

## 九大技能（S1-S9）

| Skill | 名称 | 职责 |
|-------|------|------|
| S1 | 商机评估 | 判断是否跟进 + 项目分类 |
| S2 | 需求诊断 | 从沟通记录提取客户需求 |
| S3 | 行业洞察 | 采集小红书行业趋势与竞品数据 |
| S4 | 客户洞察 | 分析核心痛点与增长机会 |
| S5 | 方案设计 | 匹配增长模型，生成运营策略 |
| S6 | 案例匹配 | 4 维加权打分，TOP5 案例推荐 |
| S7 | 内容生成 | 生成 10 页标准 Slide |
| S8 | 格式输出 | 飞书 Slides / Docx / PPTX 导出 |
| S9 | 复盘归档 | 提案归档 + 知识库更新 |

## 快速开始

```bash
# 1. 复制环境变量
cp .env.example .env

# 2. 启动服务
make up

# 3. 初始化知识库
make init-knowledge-base

# 4. 运行测试
make test              # Docker 内
make test-local        # 本地
```

## 技术栈

- **后端**: Python 3.11 / FastAPI / LangGraph
- **数据**: PostgreSQL (pgvector) / Qdrant / Redis
- **LLM**: Ollama (本地) / Anthropic Claude (云端)
- **前端**: React + TypeScript + Vite
- **部署**: Docker Compose
