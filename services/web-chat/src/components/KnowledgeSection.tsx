import { Database, GitBranch, Boxes, BookOpen, Search, Workflow } from 'lucide-react';

const knowledgeCollections = [
  {
    id: 'industry_strategy',
    name: '行业策略库',
    description: '各行业小红书 KOS 营销策略与经验汇总',
    count: 5,
    source: 'skills/s3_industry_insight.py: industry_keywords 驱动',
    layer: 'L2 · Qdrant Collection',
    linkedSkills: ['S3 行业洞察', 'S5 方案设计'],
    accent: '#16a085'
  },
  {
    id: 'competitor_analysis',
    name: '竞品格局库',
    description: '竞品矩阵、投放策略、KOS 账号对比数据',
    count: 2,
    source: 'skills/s6_case_match.py 案例匹配参考',
    layer: 'L2 · Qdrant + PG',
    linkedSkills: ['S3 行业洞察', 'S6 案例匹配'],
    accent: '#c0392b'
  },
  {
    id: 'growth_model',
    name: '增长模型库',
    description: 'K³FS 三层传播模型 / AIGC 内容生产体系 / KOS 矩阵运营',
    count: 5,
    source: 'SOUL.md 方法论章节 · 飞书文档蒸馏',
    layer: 'L2 · Qdrant (methodology 集合包含)',
    linkedSkills: ['S4 客户洞察', 'S5 方案设计'],
    accent: '#8e44ad'
  },
  {
    id: 'product_solution',
    name: '产品方案库',
    description: '6 大产品能力介绍、报价体系、Demo 说明',
    count: 6,
    source: 'MaterialLibraryLoader 分类归档',
    layer: 'L2 · Qdrant Collection',
    linkedSkills: ['S5 方案设计 (工具赋能模块)'],
    accent: '#3498db'
  },
  {
    id: 'case_labels',
    name: '案例标签库',
    description: '飞鹤/英氏/林氏家居/极氪等 10+ 行业案例',
    count: 12,
    source: 'VectorStoreClient.search("case_labels", ...)',
    layer: 'L2 · Qdrant + PG',
    linkedSkills: ['S6 案例匹配 (4 维加权打分)'],
    accent: '#27ae60'
  },
  {
    id: 'proposal_review',
    name: '提案复盘库',
    description: '历史提案 review 记录，用于持续优化',
    count: 2,
    source: 'skills/s9_archive.py: _update_review_library()',
    layer: 'L3 · review_records table',
    linkedSkills: ['S9 复盘归档 (知识反哺)'],
    accent: '#f39c12'
  },
  {
    id: 'brand_knowledge',
    name: '品牌知识定位',
    description: '16 品牌行业分类 + 易美传播 vs 弘摩科技主体区分',
    count: 3,
    source: 'skills/s1_opportunity.py: KNOWN_CLIENTS 列表',
    layer: 'L2 · PG brand_info table',
    linkedSkills: ['S1 商机评估', 'S8 格式输出 (品牌色)'],
    accent: '#e94560'
  },
  {
    id: 'xhs_insights',
    name: '小红书趋势洞察',
    description: '行业关键词 / 爆文特征 / 内容主题 / 受众兴趣',
    count: 3,
    source: 'skills/xhs_collector.py: XHSCollector 采集',
    layer: 'L2 · xhs_insights collection (Qdrant)',
    linkedSkills: ['S3 行业洞察 (KnowledgeDistiller.distill_xhs_data)'],
    accent: '#d35400'
  },
  {
    id: 'business_process',
    name: '商务流程团队知识',
    description: '双品牌合同体系 / 演示流程 / 试用申请 / 最佳实践',
    count: 5,
    source: '飞书文档 + 聊天记录 + 日历多源整合',
    layer: 'L2 · PG 结构化存储',
    linkedSkills: ['S8 格式输出 (合同输出)', 'feishu-bot 集成'],
    accent: '#2980b9'
  }
];

export default function KnowledgeSection() {
  return (
    <div className="bg-[#16213e]/50 backdrop-blur-sm rounded-2xl p-6 border border-white/5">
      <div className="flex items-center justify-between mb-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-[#e94560]/20 flex items-center justify-center">
              <Database className="w-4 h-4 text-[#e94560]" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">知识库概览 (Knowledge Collections)</h3>
              <p className="text-xs text-white/40 mt-0.5">
                L2 知识层 · 9 大集合 · Qdrant 向量库 + PostgreSQL
              </p>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2 text-xs text-white/50">
          <BookOpen className="w-3.5 h-3.5 text-[#16a085]" />
          <span>app/knowledge/distiller.py</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {knowledgeCollections.map((item) => (
          <div
            key={item.id}
            className="bg-[#0f3460]/30 rounded-xl p-4 border border-white/5 hover:border-white/15 transition-all duration-200 group"
            style={{
              borderTopColor: `${item.accent}40`,
              borderTopWidth: '2px'
            }}
          >
            <div className="flex items-start justify-between mb-2.5">
              <div className="flex items-center gap-2">
                <Boxes className="w-3.5 h-3.5" style={{ color: item.accent }} />
                <span className="text-sm font-semibold text-white">{item.name}</span>
              </div>
              <span
                className="text-[10px] font-semibold px-2 py-0.5 rounded-full"
                style={{
                  backgroundColor: `${item.accent}20`,
                  color: item.accent
                }}
              >
                {item.count} 条
              </span>
            </div>

            <p className="text-xs text-white/50 mb-3 leading-relaxed">{item.description}</p>

            <div className="space-y-2">
              <div className="flex items-start gap-1.5 text-[10px]">
                <Search className="w-3 h-3 text-white/30 flex-shrink-0 mt-0.5" />
                <span className="text-white/40 font-mono leading-tight break-all">{item.source}</span>
              </div>
              <div className="flex items-start gap-1.5 text-[10px]">
                <GitBranch className="w-3 h-3 text-white/30 flex-shrink-0 mt-0.5" />
                <span className="text-white/40 leading-tight">{item.layer}</span>
              </div>
              <div className="flex items-start gap-1.5 text-[10px]">
                <Workflow className="w-3 h-3 text-white/30 flex-shrink-0 mt-0.5" />
                <span className="text-white/40 leading-tight">
                  关联 Skill: {item.linkedSkills.join(' · ')}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
