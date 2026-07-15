import { Zap, Wrench, CheckCircle2, Workflow, Cpu } from 'lucide-react';

const products = [
  {
    name: 'KOS 代发代管',
    maturity: '成熟',
    level: 100,
    description: '母婴 / 大健康 / 家居 3 大行业方案，400+ 账号矩阵化管理，品牌方统一内容供给',
    customers: '飞鹤 / 林氏家居 / 老庙 / 松达',
    color: '#27ae60',
    modules: [
      'app/tools/research.py (行业关键词矩阵 KOS 账号分析)',
      'app/skills/proposal.py → product_mapping 模块',
      'services/feishu-bot/main.py (飞书消息代发 Bot)'
    ]
  },
  {
    name: 'AIGC 内容制作',
    maturity: '成熟',
    level: 100,
    description: '日产 1000+ 文案、2000+ 图片，AI 智能润色改写、智能改图，真实笔记可展示',
    customers: '蒙牛 / a2 / 快克',
    color: '#f39c12',
    modules: [
      'app/skills/proposal.py (10 页审核稿与唯一 ProposalSpec)',
      'app/llm/router.py (get_llm task_type=light/heavy 智能路由)',
      'LLM + 模板双轨制：品牌笔记标准化 + 素人笔记 AI 生成'
    ]
  },
  {
    name: '内容罗盘',
    maturity: '成熟',
    level: 100,
    description: '一站式小红书 KOS 运营 SaaS 平台，9 大功能模块：设备管理 / 账号管理 / 养号 / 笔记发布 / 互动 / 评论 / 校验 / 截图工具 / 数据统计',
    customers: '利星行 / 领克 / 极氪',
    color: '#3498db',
    modules: [
      'services/web-chat/src/components/* (前端控制台 UI)',
      'services/nginx/nginx.conf (生产部署反向代理)',
      'Qdrant: xhs_insights collection (内容趋势数据底层)'
    ]
  },
  {
    name: 'AI Service',
    maturity: '成熟',
    level: 100,
    description: 'AIGC 内容生成 + 智能审核 + 自动核销 + 数据归因，构建 content→traffic→conversion→repeat 完整归因链',
    customers: '董酒 / 可画 / 老庙',
    color: '#8e44ad',
    modules: [
      'app/llm/router.py (本地 Ollama + Claude 混合推理)',
      'app/knowledge/distiller.py (KnowledgeDistiller 内容审核)',
      'app/db/memory.py (MemoryStore 归因数据记录)'
    ]
  },
  {
    name: 'AiHub 生图',
    maturity: 'Demo',
    level: 60,
    description: 'AI 换装生图，支持服装/场景变换，独立账号体系与素材管理',
    customers: '英氏 / 欧恩贝',
    color: '#e94560',
    modules: [
      'app/skills/proposal.py (案例展示 / 封面生图模块可集成)',
      'MaterialLibraryLoader 素材分类归档'
    ]
  },
  {
    name: '一键组图',
    maturity: '接口',
    level: 70,
    description: 'API 形式快速图片合成，支持批量图片组合与品牌水印处理',
    customers: '可画 (Canva 代理)',
    color: '#d35400',
    modules: [
      'app/tools/export.py → Slide 输出适配器',
      'python-pptx 图片插入 / 缩放 / 裁剪 API 封装',
      'brand color 映射表 (12 品牌预设颜色) — skills/s8_format_output.py _brand_color()'
    ]
  }
];

export default function ProductsSection() {
  return (
    <div className="bg-[#16213e]/50 backdrop-blur-sm rounded-2xl p-6 border border-white/5">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-[#f39c12]/20 flex items-center justify-center">
            <Wrench className="w-4 h-4 text-[#f39c12]" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">产品能力矩阵 (Product Capabilities)</h3>
            <p className="text-xs text-white/40 mt-0.5">6 大产品线 · 映射至核心 Skill 与工具能力</p>
          </div>
        </div>
        <div className="flex items-center gap-2 text-xs text-white/40">
          <Cpu className="w-3.5 h-3.5 text-[#f39c12]" />
          <span>app/skills/proposal.py · proposal_spec.strategy</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {products.map((product) => (
          <div
            key={product.name}
            className="bg-[#0f3460]/30 rounded-xl p-4 border border-white/5 hover:border-white/20 transition-all duration-200"
            style={{ borderTop: `2px solid ${product.color}60` }}
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-start gap-2">
                <Zap className="w-4 h-4 flex-shrink-0 mt-0.5" style={{ color: product.color }} />
                <span className="text-sm font-semibold text-white leading-tight">{product.name}</span>
              </div>
              <span
                className="text-[10px] font-semibold px-2 py-0.5 rounded-full flex-shrink-0"
                style={{
                  backgroundColor: `${product.color}20`,
                  color: product.color,
                  border: `1px solid ${product.color}40`
                }}
              >
                {product.maturity}
              </span>
            </div>

            <div className="mb-3">
              <div className="flex items-center justify-between text-[10px] text-white/40 mb-1.5">
                <span>成熟度</span>
                <span className="font-mono">{product.level}%</span>
              </div>
              <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${product.level}%`,
                    background: `linear-gradient(90deg, ${product.color}aa, ${product.color})`
                  }}
                />
              </div>
            </div>

            <p className="text-xs text-white/50 mb-3 leading-relaxed">{product.description}</p>

            <div className="mb-3">
              <div className="flex items-center gap-1.5 mb-2 text-[10px] text-white/40">
                <CheckCircle2 className="w-3 h-3" style={{ color: product.color }} />
                <span>服务客户</span>
              </div>
              <div className="text-[11px] text-white/60 font-mono leading-tight">
                {product.customers}
              </div>
            </div>

            <div>
              <div className="flex items-center gap-1.5 mb-2 text-[10px] text-white/40">
                <Workflow className="w-3 h-3" style={{ color: product.color }} />
                <span>关联代码模块</span>
              </div>
              <ul className="space-y-1.5">
                {product.modules.map((mod, i) => (
                  <li key={i} className="text-[10px] text-white/50 font-mono leading-tight pl-2 border-l border-white/10">
                    {mod}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
