import { Briefcase, MapPin, BookOpen, Workflow, Search } from 'lucide-react';

const brandData = [
  { name: '飞鹤', industry: '母婴', color: '#1a5276', tags: ['繁星计划', 'KOS 矩阵第一'] },
  { name: 'a2', industry: '母婴', color: '#7b2d8b', tags: ['15天1.5万篇', '霸屏率70%'] },
  { name: '英氏', industry: '母婴', color: '#27ae60', tags: ['辅食行业', 'KOS 全链路'] },
  { name: '金领冠', industry: '母婴', color: '#e67e22', tags: ['专利配方背书', '增长迅速'] },
  { name: '松达', industry: '母婴', color: '#16a085', tags: ['成分党测评', '内容日历'] },
  { name: '欧恩贝', industry: '母婴', color: '#8e44ad', tags: ['AiHub 生图集成', '品牌素材'] },
  { name: '派特生物', industry: '大健康', color: '#27ae60', tags: ['专业信任建立', '真实效果'] },
  { name: '快克', industry: '大健康', color: '#e94560', tags: ['行业数据覆盖', '健康话题'] },
  { name: '蒙牛', industry: '食品', color: '#2980b9', tags: ['内容合规经验', '大健康品类'] },
  { name: '林氏家居', industry: '家居家装', color: '#2c3e50', tags: ['场景化内容', '3倍单品展示'] },
  { name: '老庙', industry: '珠宝', color: '#c0392b', tags: ['品牌年轻化', '小红书种草'] },
  { name: '可画', industry: '设计', color: '#e74c3c', tags: ['Canva 代理', '一键组图接口'] },
  { name: '董酒', industry: '酒类', color: '#d35400', tags: ['高端品鉴', '收藏价值'] },
  { name: '利星行', industry: '汽车', color: '#34495e', tags: ['新车评测', '微信+小红书'] },
  { name: '领克', industry: '汽车', color: '#16a085', tags: ['新能源赛道', 'KOS 矩阵'] },
  { name: '极氪', industry: '汽车', color: '#8e44ad', tags: ['高端新能源', '品牌声量'] },
];

const industryGroups: Record<string, string[]> = {
  '母婴 (6)': ['飞鹤', 'a2', '英氏', '金领冠', '松达', '欧恩贝'],
  '大健康 (2)': ['派特生物', '快克'],
  '家居家装 (1)': ['林氏家居'],
  '汽车 (3)': ['利星行', '领克', '极氪'],
  '酒类 (1)': ['董酒'],
  '食品 (1)': ['蒙牛'],
  '珠宝 (1)': ['老庙'],
  '设计 (1)': ['可画'],
};

const industries = [
  { name: '母婴', coreStrategy: '专业测评+矩阵规模化+评论区运营+搜索占位', highlight: '成分党测评、内容日历、AI 保障稳定性', color: '#1a5276' },
  { name: '大健康', coreStrategy: '医生/KOL背书+用户证言+合规审查', highlight: '专业信任建立、真实效果数据、长期搜索价值', color: '#27ae60' },
  { name: '家居家装', coreStrategy: '场景化内容+装修灵感+软装搭配', highlight: '场景化展示效果比单品好 3 倍', color: '#2c3e50' },
  { name: '汽车', coreStrategy: '新车评测+KOS矩阵+微信/小红书双平台', highlight: '新能源赛道、经销商协同、线索转化', color: '#3498db' },
  { name: '酒类', coreStrategy: '品牌故事+场景营销+品鉴内容', highlight: '高端品鉴、收藏价值、圈层传播', color: '#d35400' },
  { name: '食品', coreStrategy: '口味测评+场景种草+UGC裂变', highlight: '真实体验分享、垂类达人矩阵', color: '#2980b9' },
  { name: '珠宝', coreStrategy: '设计美学+高端定制+节日营销', highlight: '品牌文化故事背书策略', color: '#c0392b' },
  { name: '设计', coreStrategy: '创意展示+工具赋能+案例分享', highlight: '设计师人设打造 + Canva 工具集成', color: '#e74c3c' },
  { name: '技术', coreStrategy: '技术解读+产品对比+场景应用', highlight: 'SaaS/Ollama/AI 技术深度', color: '#8e44ad' },
  { name: '通用', coreStrategy: '品牌传播+用户互动+转化闭环', highlight: '通用方法论，支持多行业快速适配', color: '#2c3e50' },
];

export default function BrandsSection() {
  return (
    <div className="bg-[#16213e]/50 backdrop-blur-sm rounded-2xl p-6 border border-white/5">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-[#e94560]/20 flex items-center justify-center">
            <Briefcase className="w-4 h-4 text-[#e94560]" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">服务品牌与行业覆盖 (Brands × Industries)</h3>
            <p className="text-xs text-white/40 mt-0.5">16 品牌 · 10 行业 · brand_info table + case_labels collection</p>
          </div>
        </div>
        <div className="flex items-center gap-2 text-xs text-white/40 font-mono">
          <Search className="w-3.5 h-3.5 text-[#16a085]" />
          <span>skills/s1_opportunity.py: KNOWN_CLIENTS</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
        <div className="lg:col-span-2">
          <h4 className="text-sm font-semibold text-white/80 mb-3 flex items-center gap-2">
            <MapPin className="w-4 h-4 text-[#16a085]" />
            行业 × 品牌矩阵 (Industry × Brand Matrix)
          </h4>
          <div className="space-y-2">
            {Object.entries(industryGroups).map(([industry, brands]) => {
              const industryInfo = industries.find(i => industry.startsWith(i.name));
              const industryColor = industryInfo?.color || '#16a085';
              return (
                <div
                  key={industry}
                  className="bg-[#0f3460]/30 rounded-xl p-3 border border-white/5"
                  style={{ borderLeft: `3px solid ${industryColor}` }}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-semibold text-white">{industry}</span>
                    <span className="text-[10px] text-white/40 font-mono">
                      {industryInfo?.coreStrategy || ''}
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {brands.map((brand) => {
                      const bd = brandData.find(b => b.name === brand);
                      return (
                        <span
                          key={brand}
                          className="text-xs px-2 py-1 rounded-lg font-medium"
                          style={{
                            backgroundColor: `${bd?.color}20`,
                            color: bd?.color,
                            border: `1px solid ${bd?.color}40`
                          }}
                        >
                          {brand}
                        </span>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div>
          <h4 className="text-sm font-semibold text-white/80 mb-3 flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-[#8e44ad]" />
            品牌亮点知识库 (Brand Highlights & Tags)
          </h4>
          <div className="grid grid-cols-1 gap-2 max-h-[450px] overflow-y-auto pr-2">
            {brandData.map((brand) => (
              <div
                key={brand.name}
                className="bg-[#0f3460]/30 rounded-xl p-3 border border-white/5 hover:border-white/15 transition-all"
                style={{ borderLeft: `2px solid ${brand.color}` }}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-semibold text-white">{brand.name}</span>
                  <span className="text-[10px] text-white/40 px-1.5 py-0.5 bg-white/5 rounded">
                    {brand.industry}
                  </span>
                </div>
                <div className="flex flex-wrap gap-1 mb-1">
                  {brand.tags.map((tag) => (
                    <span
                      key={tag}
                      className="text-[10px] text-white/60 bg-white/5 px-1.5 py-0.5 rounded border border-white/5"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
                <div className="text-[9px] font-mono text-white/30 mt-1 pt-1 border-t border-white/5">
                  品牌色: {brand.color}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-[#0f3460]/30 rounded-xl p-4 border border-white/5">
        <div className="flex items-center gap-2 mb-3">
          <Workflow className="w-4 h-4 text-[#e94560]" />
          <span className="text-xs font-semibold text-white/80">知识库数据流向 (Data Flow)</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-[11px] text-white/60 font-mono leading-relaxed">
          <div className="bg-white/5 rounded-lg p-3">
            <span className="text-[#3498db]">brand_info</span> table
            <div className="text-white/30 text-[10px] mt-1">skills/s9_archive.py: _update_brand_info() (L2 PG)</div>
            <div className="text-[10px] text-white/40 mt-1">
              ← S1 KNOWN_CLIENTS · S5 product_solution · → S7 品牌色映射
            </div>
          </div>
          <div className="bg-white/5 rounded-lg p-3">
            <span className="text-[#16a085]">case_labels</span> collection
            <div className="text-white/30 text-[10px] mt-1">VectorStoreClient.search("case_labels", ...) (Qdrant)</div>
            <div className="text-[10px] text-white/40 mt-1">
              ← S6 案例匹配 4 维加权 · 10+ 内置案例 · → S7 案例展示页
            </div>
          </div>
          <div className="bg-white/5 rounded-lg p-3">
            <span className="text-[#d35400]">xhs_insights</span> collection
            <div className="text-white/30 text-[10px] mt-1">KnowledgeDistiller.distill_xhs_data() (Qdrant)</div>
            <div className="text-[10px] text-white/40 mt-1">
              ← XHSCollector 三维度采集 · → S3 行业洞察 / S4 客户洞察
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
