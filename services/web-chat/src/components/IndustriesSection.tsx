import { Globe, TrendingUp, Search, Database, Workflow } from 'lucide-react';
import { industries } from '../data/mockData';

// 行业与项目功能的映射
const industryCapabilityMap: Record<string, {
  dataSource: string;
  skillModules: string[];
  collection: string;
  color: string;
}> = {
  '母婴': {
    dataSource: '飞鹤 / a2 / 英氏 / 金领冠 / 松达 / 欧恩贝',
    skillModules: ['S1商机评估', 'S3行业洞察', 'S6案例匹配', 'S7内容生成'],
    collection: 'xhs_insights + case_labels + brand_info',
    color: '#1a5276'
  },
  '大健康': {
    dataSource: '派特生物 / 快克',
    skillModules: ['S2需求诊断', 'S4客户洞察', 'S9复盘归档'],
    collection: 'industry_strategy + competitor_analysis',
    color: '#27ae60'
  },
  '家居家装': {
    dataSource: '林氏家居',
    skillModules: ['S3行业洞察', 'S5方案设计', 'S7内容生成'],
    collection: 'case_labels (场景化展示)',
    color: '#2c3e50'
  },
  '汽车': {
    dataSource: '利星行 / 领克 / 极氪',
    skillModules: ['S1商机评估', 'S6案例匹配', 'S8格式输出'],
    collection: 'product_solution + case_labels',
    color: '#3498db'
  },
  '酒类': {
    dataSource: '董酒',
    skillModules: ['S5方案设计', 'S7内容生成', 'S8格式输出'],
    collection: 'brand_knowledge + case_labels',
    color: '#d35400'
  },
  '食品': {
    dataSource: '蒙牛',
    skillModules: ['S2需求诊断', 'S3行业洞察', 'S4客户洞察'],
    collection: 'industry_strategy + xhs_insights',
    color: '#2980b9'
  },
  '珠宝': {
    dataSource: '老庙',
    skillModules: ['S5方案设计', 'S7内容生成'],
    collection: 'brand_knowledge + case_labels',
    color: '#c0392b'
  },
  '设计': {
    dataSource: '可画 (Canva 代理)',
    skillModules: ['S6案例匹配', 'S8格式输出'],
    collection: 'product_solution (一键组图)',
    color: '#e74c3c'
  },
  '技术': {
    dataSource: 'SaaS / Ollama / AI 技术深度',
    skillModules: ['S1商机评估', 'S5方案设计', 'S7内容生成'],
    collection: 'methodology (核心方法论)',
    color: '#8e44ad'
  },
  '通用': {
    dataSource: '多行业快速适配',
    skillModules: ['全流程 S1-S9'],
    collection: 'business_process + review_records',
    color: '#2c3e50'
  }
};

export default function IndustriesSection() {
  return (
    <div className="bg-[#16213e]/50 backdrop-blur-sm rounded-2xl p-6 border border-white/5">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-emerald-500/20 flex items-center justify-center">
            <Globe className="w-4 h-4 text-emerald-400" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">覆盖行业与能力映射</h3>
            <p className="text-xs text-white/40">10 个行业赛道 · 映射至 Skill 模块与 Knowledge Collections</p>
          </div>
        </div>
        <div className="flex items-center gap-2 text-xs text-white/40 font-mono">
          <Search className="w-3.5 h-3.5 text-emerald-400" />
          <span>app/tools/research.py · 按需调用行业关键词矩阵</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {industries.map((industry) => {
          const capability = industryCapabilityMap[industry.name] || industryCapabilityMap['通用'];
          return (
            <div
              key={industry.id}
              className="bg-[#0f3460]/30 rounded-xl p-4 border border-white/5 hover:border-white/20 transition-all duration-200"
              style={{ borderLeft: `3px solid ${capability.color}` }}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Globe className="w-4 h-4" style={{ color: capability.color }} />
                  <span className="text-sm font-medium text-white">{industry.name}</span>
                </div>
                <div className="flex items-center gap-1 text-[10px] text-emerald-400/70 flex-shrink-0">
                  <TrendingUp className="w-3 h-3" />
                  <span className="truncate max-w-[150px]">{industry.highlight}</span>
                </div>
              </div>

              <p className="text-[11px] text-white/60 mb-3 leading-relaxed">{industry.coreStrategy}</p>

              <div className="space-y-2 pt-2 border-t border-white/5">
                <div className="flex items-start gap-1.5 text-[10px]">
                  <Database className="w-3 h-3 text-white/30 flex-shrink-0 mt-0.5" />
                  <div>
                    <span className="text-white/40">数据来源: </span>
                    <span className="text-white/60 font-mono">{capability.dataSource}</span>
                  </div>
                </div>
                <div className="flex items-start gap-1.5 text-[10px]">
                  <Workflow className="w-3 h-3 text-white/30 flex-shrink-0 mt-0.5" />
                  <div>
                    <span className="text-white/40">关联 Skill: </span>
                    <span className="text-white/60 font-mono">{capability.skillModules.join(' · ')}</span>
                  </div>
                </div>
                <div className="flex items-start gap-1.5 text-[10px]">
                  <Search className="w-3 h-3 text-white/30 flex-shrink-0 mt-0.5" />
                  <div>
                    <span className="text-white/40">知识库: </span>
                    <span className="text-white/60 font-mono">{capability.collection}</span>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* 行业关键词矩阵说明 */}
      <div className="mt-5 bg-[#0f3460]/30 rounded-xl p-4 border border-white/5">
        <div className="flex items-center gap-2 mb-3">
          <Search className="w-4 h-4 text-emerald-400" />
          <span className="text-xs font-semibold text-white/80">行业关键词矩阵 · INDUSTRY_KEYWORDS</span>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-2 text-[10px] text-white/50 font-mono">
          <div className="bg-white/5 rounded-lg p-2 border border-white/5 text-center">母婴 · 成分党 · 辅食</div>
          <div className="bg-white/5 rounded-lg p-2 border border-white/5 text-center">大健康 · 专业信任 · KOL</div>
          <div className="bg-white/5 rounded-lg p-2 border border-white/5 text-center">汽车 · 评测 · 新能源</div>
          <div className="bg-white/5 rounded-lg p-2 border border-white/5 text-center">家居 · 场景化 · 装修灵感</div>
          <div className="bg-white/5 rounded-lg p-2 border border-white/5 text-center">通用 · 品牌传播 · 转化闭环</div>
        </div>
      </div>
    </div>
  );
}
