import { ArrowRight, CheckCircle2, ClipboardList, FileText, FolderKanban, Loader2, Search } from 'lucide-react';

interface FlowOverviewProps {
  activeStage: string;
  onStageClick: (stageId: string) => void;
}

const stageData = [
  {
    id: 'S1',
    name: '需求简报',
    shortDesc: '需求提取与缺口判断',
    filePath: 'app/skills/brief.py',
    icon: ClipboardList,
    accent: '#3498db'
  },
  {
    id: 'S2',
    name: '决策洞察',
    shortDesc: '用户决策地图',
    filePath: 'app/skills/insight.py',
    icon: Search,
    accent: '#16a085'
  },
  {
    id: 'S3',
    name: '方案生成',
    shortDesc: '唯一 ProposalSpec',
    filePath: 'app/skills/proposal.py',
    icon: FileText,
    accent: '#e94560'
  }
];

export default function FlowOverview({ activeStage, onStageClick }: FlowOverviewProps) {
  return (
    <div className="bg-[#16213e]/50 backdrop-blur-sm rounded-2xl p-6 border border-white/5">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-semibold text-white">提案生成流程</h2>
          <p className="text-xs text-white/40 mt-0.5">
            3 个核心 Skill · 审核后按需输出 · 项目结束后归档
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs text-white/50">
          <FolderKanban className="w-4 h-4 text-[#e94560]" />
          <span>services/orchestrator/app/agent.py</span>
        </div>
      </div>

      <div className="flex items-stretch gap-3 overflow-x-auto pb-2">
        {stageData.map((stage, index) => {
          const Icon = stage.icon;
          const isActive = activeStage === stage.id;
          const isCompleted = stage.id === 'S1';
          const isInProgress = stage.id === 'S2';

          return (
            <div key={stage.id} className="flex items-stretch flex-1">
              <button
                onClick={() => onStageClick(stage.id)}
                className={`relative flex flex-col gap-2 px-4 py-4 rounded-xl transition-all duration-200 min-w-[190px] w-full border ${
                  isActive
                    ? 'bg-[#e94560]/15 border-[#e94560]/60 shadow-lg shadow-[#e94560]/10 scale-[1.02]'
                    : 'bg-white/5 border-white/10 hover:bg-white/10 hover:border-white/20'
                }`}
                style={isActive ? {} : { borderTop: `2px solid ${stage.accent}40` }}
              >
                <div className="flex items-center gap-3 w-full">
                  <div
                    className="w-9 h-9 rounded-lg flex items-center justify-center text-sm font-bold text-white"
                    style={{ backgroundColor: `${stage.accent}40`, border: `1px solid ${stage.accent}60` }}
                  >
                    {stage.id}
                  </div>
                  <div className="flex-1">
                    <div className="text-sm font-semibold text-white text-left">{stage.name}</div>
                    <div className="text-[11px] text-white/40 text-left mt-0.5">{stage.shortDesc}</div>
                  </div>
                  {isCompleted && <CheckCircle2 className="w-4 h-4 text-emerald-400" />}
                  {isInProgress && <Loader2 className="w-4 h-4 text-[#e94560] animate-spin" />}
                  {!isCompleted && !isInProgress && <Icon className="w-4 h-4" style={{ color: stage.accent }} />}
                </div>
                <div className="text-[10px] text-white/30 font-mono text-left border-t border-white/5 pt-2">
                  {stage.filePath}
                </div>
              </button>
              {index < stageData.length - 1 && (
                <div className="flex items-center px-2">
                  <ArrowRight className="w-4 h-4 text-white/20" />
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="mt-4 text-xs text-white/40 border-t border-white/5 pt-4">
        工具：小红书研究 · 案例检索 · 格式输出　｜　生命周期：人工审核 · 项目结果 · 复盘归档
      </div>
    </div>
  );
}
