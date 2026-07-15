import { Server, Database, Cpu, MemoryStick, HardDrive, ArrowRight, Boxes, Workflow, GitBranch } from 'lucide-react';

const architectureLayers = [
  {
    name: 'L1 · 原始数据层 (Raw Data Layer)',
    description: '原始文档 / 小红书采集数据 / 聊天记录等未加工信息',
    tech: 'PostgreSQL + 文件存储',
    color: '#3498db',
    components: [
      { name: 'raw_documents', detail: '飞书文档元数据与内容 (slides + docx)', icon: HardDrive },
      { name: 'raw_xhs_data', detail: '小红书行业/竞品/客户三维采集数据 (industry / competitor / client)', icon: Database },
      { name: '聊天记录 + 日历', detail: '多源数据整合：飞书 IM + Calendar events', icon: Boxes },
    ],
    connections: ['→ MaterialLibraryLoader._save_raw_document()', '→ XHSCollector.search_*()']
  },
  {
    name: 'L2 · 知识层 (Knowledge Layer)',
    description: '经 LLM 蒸馏后的结构化知识点 + 向量检索集合 + 关系网络',
    tech: 'Qdrant 向量库 + PostgreSQL',
    color: '#8e44ad',
    components: [
      { name: 'knowledge_points', detail: '44 条结构化知识点 (industry_strategy / product_solution / case_labels / brand_knowledge / proposal_review / xhs_insights / business_process + 2)', icon: Boxes },
      { name: 'knowledge_relations', detail: '9 大集合间关系网络 (belongs_to / applied_in / similar_to / competes_with)', icon: GitBranch },
      { name: 'Qdrant Collections', detail: '9 个 collection 对应 9 类知识，支持语义向量检索', icon: Database },
    ],
    connections: ['KnowledgeDistiller.distill_document()', 'distill_xhs_data() → xhs_insights collection']
  },
  {
    name: 'L3 · 记忆层 (Memory Layer)',
    description: '用户偏好、会话历史、交互记录，用于个性化 Agent 响应',
    tech: 'PostgreSQL + Redis 缓存',
    color: '#e94560',
    components: [
      { name: 'user_preferences', detail: '用户行业偏好、品牌历史、常用模板配置', icon: MemoryStick },
      { name: 'session_memory', detail: '会话级状态缓存：stage_in_progress / search_history / outputs', icon: Cpu },
      { name: 'interaction_tracking', detail: 'interactions 计数 + bid_result 记录 (中标/失败/待确认)', icon: Server },
    ],
    connections: [
      '审核通过后记录实际输出格式',
      '项目结束事件写入 review_feedback + bid_result',
      '归档成功后更新长期记忆与知识库'
    ]
  },
];

const serviceComponents = [
  {
    name: 'orchestrator',
    port: '8000',
    tech: 'FastAPI + LangGraph',
    role: '核心编排引擎',
    keyFiles: ['app/agent.py (LangGraph workflow)', 'app/routers/proposal.py (POST /generate)', 'app/vector_store/client.py (Qdrant)', 'app/db/database.py + memory.py'],
    color: '#e94560'
  },
  {
    name: 'web-chat',
    port: '3000 / 5173(dev)',
    tech: 'React + TypeScript + Vite',
    role: '售前团队控制台界面',
    keyFiles: ['src/App.tsx (主页面)', 'src/components/* (9 个可视化区块)', 'index.css (Tailwind CSS)'],
    color: '#3498db'
  },
  {
    name: 'feishu-bot',
    port: '8080',
    tech: 'FastAPI + lark-cli',
    role: '飞书消息 Bot 入口',
    keyFiles: ['main.py: POST /webhook', '接收飞书消息 → 转发至 orchestrator /generate', 'lark-cli 执行文档/Slides API'],
    color: '#16a085'
  },
  {
    name: 'worker',
    port: '—',
    tech: 'Python + Celery',
    role: '小红书数据采集 + 知识蒸馏任务',
    keyFiles: ['skills/xhs_collector.py (XHSCollector)', 'app/knowledge/distiller.py (KnowledgeDistiller)', 'material_libraries/loader.py'],
    color: '#f39c12'
  },
  {
    name: 'scheduler',
    port: '—',
    tech: 'APScheduler / Celery Beat',
    role: '物料库增量更新、数据清理定时任务',
    keyFiles: ['app/scheduler.py (定时触发)', '定时同步飞书文件夹变化 + re-distill'],
    color: '#d35400'
  },
  {
    name: 'qdrant',
    port: '6333',
    tech: '向量数据库',
    role: '9 大知识集合语义检索',
    keyFiles: ['app/vector_store/client.py (VectorStoreClient)', 'upsert() / search() API', '9 collections 对应 9 大知识集合'],
    color: '#8e44ad'
  },
  {
    name: 'postgresql',
    port: '5432',
    tech: '关系数据库 (pgvector)',
    role: 'L1/L2/L3 结构化数据存储',
    keyFiles: ['app/db/database.py (连接管理)', 'app/db/init.sql (初始化 schema)', 'raw_documents / knowledge_points / brand_info / review_records'],
    color: '#27ae60'
  },
  {
    name: 'redis',
    port: '6379',
    tech: '缓存 / 消息队列',
    role: 'L3 会话缓存 + 后台任务消息队列',
    keyFiles: ['app/db/memory.py (MemoryStore Redis 层)', 'Celery broker 队列任务'],
    color: '#c0392b'
  },
  {
    name: 'nginx',
    port: '80',
    tech: 'Nginx 反向代理',
    role: '统一入口 / 静态资源托管 / API 路由',
    keyFiles: ['services/nginx/nginx.conf', 'web-chat 静态 + orchestrator API 分发'],
    color: '#2c3e50'
  }
];

export default function ArchitectureSection() {
  return (
    <div className="bg-[#16213e]/50 backdrop-blur-sm rounded-2xl p-6 border border-white/5">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-[#8e44ad]/20 flex items-center justify-center">
            <Server className="w-4 h-4 text-[#8e44ad]" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">系统架构概览 (System Architecture)</h3>
            <p className="text-xs text-white/40 mt-0.5">三层数据架构 + 9 大服务组件 · docker-compose.yml</p>
          </div>
        </div>
        <div className="text-xs text-white/40 font-mono">
          services/orchestrator/app/agent.py (LangGraph create_proposal_workflow)
        </div>
      </div>

      {/* 三层数据架构 */}
      <div className="mb-8">
        <h4 className="text-sm font-semibold text-white/80 mb-4 flex items-center gap-2">
          <Database className="w-4 h-4 text-[#e94560]" />
          三层数据架构 (Three-Layer Data Architecture)
        </h4>
        <div className="space-y-4">
          {architectureLayers.map((layer) => (
            <div
              key={layer.name}
              className="bg-[#0f3460]/30 rounded-xl p-4 border border-white/5"
              style={{ borderLeft: `3px solid ${layer.color}` }}
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-semibold text-white">{layer.name}</span>
                </div>
                <span className="text-[10px] text-white/40 font-mono">{layer.tech}</span>
              </div>
              <p className="text-xs text-white/50 mb-4">{layer.description}</p>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-2 mb-3">
                {layer.components.map((comp, i) => {
                  const IconComponent = comp.icon;
                  return (
                    <div key={i} className="bg-white/5 rounded-lg p-3 border border-white/5">
                      <div className="flex items-start gap-2">
                        <IconComponent className="w-3.5 h-3.5 flex-shrink-0 mt-0.5" style={{ color: layer.color }} />
                        <div>
                          <div className="text-xs font-semibold text-white/90">{comp.name}</div>
                          <div className="text-[10px] text-white/40 mt-0.5 leading-tight">{comp.detail}</div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>

              <div className="flex flex-wrap gap-2 items-center">
                <ArrowRight className="w-3 h-3 text-white/30" />
                {layer.connections.map((conn, i) => (
                  <span
                    key={i}
                    className="text-[10px] font-mono text-white/50 bg-white/5 px-2 py-1 rounded border border-white/10"
                  >
                    {conn}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 服务组件 */}
      <div>
        <h4 className="text-sm font-semibold text-white/80 mb-4 flex items-center gap-2">
          <Workflow className="w-4 h-4 text-[#16a085]" />
          服务组件 (Service Components) · Docker Network
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {serviceComponents.map((svc) => (
            <div
              key={svc.name}
              className="bg-[#0f3460]/30 rounded-xl p-4 border border-white/5 hover:border-white/20 transition-all"
              style={{ borderTop: `2px solid ${svc.color}60` }}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-bold text-white font-mono">{svc.name}</span>
                <span className="text-[10px] font-mono text-white/40">:{svc.port}</span>
              </div>
              <div className="text-[10px] mb-3" style={{ color: svc.color }}>
                {svc.role} · {svc.tech}
              </div>
              <ul className="space-y-1.5">
                {svc.keyFiles.map((file, i) => (
                  <li key={i} className="text-[10px] text-white/50 font-mono leading-tight pl-2 border-l border-white/10">
                    {file}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
