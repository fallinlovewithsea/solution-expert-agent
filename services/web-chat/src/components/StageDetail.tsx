import { ArrowRight, FileOutput, GitBranch, Package, Server, Workflow } from 'lucide-react';

interface StageDetailProps {
  activeStage: string;
}

const stageDetails: Record<string, {
  title: string;
  description: string;
  filePath: string;
  className: string;
  inputs: { label: string; source: string }[];
  outputs: { label: string; target: string }[];
  dataFlow: string[];
  features: string[];
  accentColor: string;
}> = {
  S1: {
    title: '需求简报',
    description: '从沟通记录或 RFP 中提取需求，只对真正影响方案方向的信息集中追问一次。',
    filePath: 'app/skills/brief.py',
    className: 'BriefSkill',
    inputs: [
      { label: '客户输入 / RFP', source: '用户输入' },
      { label: '研究模式', source: 'auto / fast / full' }
    ],
    outputs: [
      { label: 'brief', target: '统一需求简报' },
      { label: 'missing_info', target: '必要时暂停并追问' },
      { label: 'research_mode', target: '控制洞察深度' }
    ],
    dataFlow: ['结构化提取', '关键信息缺口判断', '快速 / 完整研究路由'],
    features: ['不再设置形式化 GO / NO-GO 节点', '预算与时间线作为风险提示', '已知客户优先复用历史知识'],
    accentColor: '#3498db'
  },
  S2: {
    title: '决策洞察',
    description: '围绕用户为什么产生问题、如何搜索、需要什么证据和如何转化，形成用户决策地图。',
    filePath: 'app/skills/insight.py',
    className: 'InsightSkill',
    inputs: [
      { label: 'brief', source: 'S1 需求简报' },
      { label: '研究数据', source: '按需调用 ResearchTool' }
    ],
    outputs: [
      { label: 'decision_map', target: 'S3 方案生成' },
      { label: 'limitations', target: '提案假设与数据局限' }
    ],
    dataFlow: ['Feed 需求激发', 'Search 搜索验证', '信任证据', '转化承接'],
    features: ['实时研究为可选工具', '六类搜索意图', 'KOL / KOC / KOS / 品牌号协同'],
    accentColor: '#16a085'
  },
  S3: {
    title: '方案生成',
    description: '一次性生成策略、案例、执行计划和标准页面，维护唯一 ProposalSpec。',
    filePath: 'app/skills/proposal.py',
    className: 'ProposalSkill',
    inputs: [
      { label: 'brief', source: 'S1' },
      { label: 'decision_map', source: 'S2' },
      { label: 'matched_cases', source: '内部调用 CaseRetrievalTool' }
    ],
    outputs: [
      { label: 'proposal_spec', target: '人工审核' },
      { label: 'slides', target: '审核通过后交给输出工具' }
    ],
    dataFlow: ['案例检索', '单次方案生成', '统一结构校验', '提交人工审核'],
    features: ['正文与页面共享唯一事实源', '固定 10 页标准结构', '审核前不创建对外文件', '项目结束后才允许归档'],
    accentColor: '#e94560'
  }
};

export default function StageDetail({ activeStage }: StageDetailProps) {
  const detail = stageDetails[activeStage];
  if (!detail) return null;

  return (
    <div className="bg-[#16213e]/50 backdrop-blur-sm rounded-2xl p-6 border border-white/5">
      <div className="flex items-start justify-between mb-5">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <span className="text-2xl font-bold text-white" style={{ textShadow: `0 0 20px ${detail.accentColor}80` }}>
              {activeStage}
            </span>
            <h3 className="text-xl font-semibold text-white">{detail.title}</h3>
          </div>
          <div className="flex items-center gap-2 text-xs text-white/40 font-mono">
            <Workflow className="w-3.5 h-3.5" style={{ color: detail.accentColor }} />
            <span>{detail.filePath}</span><span className="text-white/20">::</span><span style={{ color: detail.accentColor }}>{detail.className}</span>
          </div>
        </div>
      </div>

      <p className="text-sm text-white/70 mb-6 leading-relaxed">{detail.description}</p>

      <div className="grid grid-cols-2 gap-4 mb-5">
        <DetailList icon={Package} title="输入 Inputs" items={detail.inputs.map(item => ({ main: item.label, sub: `← ${item.source}` }))} color={detail.accentColor} />
        <DetailList icon={FileOutput} title="输出 Outputs" items={detail.outputs.map(item => ({ main: item.label, sub: `→ ${item.target}` }))} color={detail.accentColor} />
      </div>

      <div className="grid grid-cols-1 gap-4">
        <div className="bg-[#0f3460]/20 rounded-xl p-4 border border-white/5">
          <div className="flex items-center gap-2 mb-3"><GitBranch className="w-4 h-4" style={{ color: detail.accentColor }} /><span className="text-xs font-semibold text-white/80">数据流向</span></div>
          <div className="flex flex-wrap gap-2 items-center">
            {detail.dataFlow.map((step, index) => <div key={step} className="flex items-center gap-2"><span className="text-xs text-white/60 bg-white/5 px-2 py-1 rounded-lg border border-white/10">{step}</span>{index < detail.dataFlow.length - 1 && <ArrowRight className="w-3 h-3 text-white/20" />}</div>)}
          </div>
        </div>
        <div className="bg-[#0f3460]/20 rounded-xl p-4 border border-white/5">
          <div className="flex items-center gap-2 mb-3"><Server className="w-4 h-4" style={{ color: detail.accentColor }} /><span className="text-xs font-semibold text-white/80">核心能力</span></div>
          <div className="grid grid-cols-2 gap-2">{detail.features.map(feature => <div key={feature} className="flex items-start gap-2 text-xs text-white/60"><span className="mt-1 w-1 h-1 rounded-full flex-shrink-0" style={{ backgroundColor: detail.accentColor }} /><span>{feature}</span></div>)}</div>
        </div>
      </div>
    </div>
  );
}

function DetailList({ icon: Icon, title, items, color }: { icon: typeof Package; title: string; items: { main: string; sub: string }[]; color: string }) {
  return (
    <div className="bg-[#0f3460]/20 rounded-xl p-4 border border-white/5">
      <div className="flex items-center gap-2 mb-3"><Icon className="w-4 h-4" style={{ color }} /><span className="text-xs font-semibold text-white/80">{title}</span></div>
      <ul className="space-y-2.5">{items.map(item => <li key={item.main} className="text-xs"><div className="text-white/80 font-medium">{item.main}</div><div className="text-white/30 font-mono text-[10px] mt-0.5 pl-2 border-l-2 border-white/10">{item.sub}</div></li>)}</ul>
    </div>
  );
}
