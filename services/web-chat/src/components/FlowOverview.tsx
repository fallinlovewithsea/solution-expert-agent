import { Target, ClipboardList, TrendingUp, Users, FileText, Copy, PenTool, Download, Archive, CheckCircle2, Loader2, ArrowRight, FolderKanban } from 'lucide-react';

interface FlowOverviewProps {
  activeStage: string;
  onStageClick: (stageId: string) => void;
}

const stageData = [
  {
    id: 'S1',
    name: '商机评估',
    shortDesc: '客户初筛',
    module: 'skills.s1_opportunity.S1OpportunityAssessment',
    filePath: 'skills/s1_opportunity.py',
    status: '已完成',
    icon: Target,
    accent: '#3498db'
  },
  {
    id: 'S2',
    name: '需求诊断',
    shortDesc: 'LLM 提取需求',
    module: 'skills.s2_requirement.S2RequirementDiagnosis',
    filePath: 'skills/s2_requirement.py',
    status: '进行中',
    icon: ClipboardList,
    accent: '#e94560'
  },
  {
    id: 'S3',
    name: '行业洞察',
    shortDesc: '小红书数据采集',
    module: 'skills.s3_industry_insight.S3IndustryInsight',
    filePath: 'skills/s3_industry_insight.py',
    status: '待执行',
    icon: TrendingUp,
    accent: '#16a085'
  },
  {
    id: 'S4',
    name: '客户洞察',
    shortDesc: '痛点分析',
    module: 'skills.s4_client_insight.S4ClientInsight',
    filePath: 'skills/s4_client_insight.py',
    status: '待执行',
    icon: Users,
    accent: '#8e44ad'
  },
  {
    id: 'S5',
    name: '方案设计',
    shortDesc: '增长模型匹配',
    module: 'skills.s5_proposal_design.S5ProposalDesign',
    filePath: 'skills/s5_proposal_design.py',
    status: '待执行',
    icon: FileText,
    accent: '#d35400'
  },
  {
    id: 'S6',
    name: '案例匹配',
    shortDesc: '4 维加权打分',
    module: 'skills.s6_case_match.S6CaseMatch',
    filePath: 'skills/s6_case_match.py',
    status: '待执行',
    icon: Copy,
    accent: '#27ae60'
  },
  {
    id: 'S7',
    name: '内容生成',
    shortDesc: '10 页 Slide',
    module: 'skills.s7_content_gen.S7ContentGeneration',
    filePath: 'skills/s7_content_gen.py',
    status: '待执行',
    icon: PenTool,
    accent: '#f39c12'
  },
  {
    id: 'S8',
    name: '格式输出',
    shortDesc: 'Slides + Docx + PPTX',
    module: 'skills.s8_format_output.S8FormatOutput',
    filePath: 'skills/s8_format_output.py',
    status: '待执行',
    icon: Download,
    accent: '#c0392b'
  },
  {
    id: 'S9',
    name: '复盘归档',
    shortDesc: '反哺知识库',
    module: 'skills.s9_archive.S9Archive',
    filePath: 'skills/s9_archive.py',
    status: '待执行',
    icon: Archive,
    accent: '#2c3e50'
  }
];

export default function FlowOverview({ activeStage, onStageClick }: FlowOverviewProps) {
  return (
    <div className="bg-[#16213e]/50 backdrop-blur-sm rounded-2xl p-6 border border-white/5">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-semibold text-white">提案生成流程</h2>
          <p className="text-xs text-white/40 mt-0.5">
            LangGraph 编排 · 9 个 Skill 串联 · skills/ 目录
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs text-white/50">
          <FolderKanban className="w-4 h-4 text-[#e94560]" />
          <span>services/orchestrator/app/agent.py</span>
        </div>
      </div>

      <div className="flex items-stretch gap-2 overflow-x-auto pb-2">
        {stageData.map((stage, index) => {
          const Icon = stage.icon;
          const isActive = activeStage === stage.id;
          const isCompleted = stage.id === 'S1';
          const isInProgress = stage.id === 'S2';

          return (
            <div key={stage.id} className="flex items-stretch">
              <button
                onClick={() => onStageClick(stage.id)}
                className={`
                  relative flex flex-col items-center gap-2 px-3 py-3 rounded-xl
                  transition-all duration-200 min-w-[120px] border
                  ${isActive
                    ? 'bg-[#e94560]/15 border-[#e94560]/60 shadow-lg shadow-[#e94560]/10 scale-[1.02]'
                    : 'bg-white/5 border-white/10 hover:bg-white/10 hover:border-white/20'
                  }
                `}
                style={isActive ? {} : { borderTop: `2px solid ${stage.accent}40` }}
              >
                <div className="flex items-center gap-2 w-full">
                  <div
                    className="w-7 h-7 rounded-lg flex items-center justify-center text-sm font-bold text-white"
                    style={{ backgroundColor: `${stage.accent}40`, border: `1px solid ${stage.accent}60` }}
                  >
                    {stage.id}
                  </div>
                  <div className="flex-1">
                    <div className="text-xs font-semibold text-white text-left leading-tight">
                      {stage.name}
                    </div>
                    <div className="text-[10px] text-white/40 text-left mt-0.5">
                      {stage.shortDesc}
                    </div>
                  </div>
                  <div className="flex-shrink-0">
                    {isCompleted && <CheckCircle2 className="w-4 h-4 text-emerald-400" />}
                    {isInProgress && <Loader2 className="w-4 h-4 text-[#e94560] animate-spin" />}
                    {!isCompleted && !isInProgress && (
                      <Icon className="w-4 h-4 text-white/30" style={{ color: stage.accent + '80' }} />
                    )}
                  </div>
                </div>

                <div className="w-full mt-1 pt-2 border-t border-white/5">
                  <div className="text-[9px] text-white/30 font-mono text-left truncate" title={stage.filePath}>
                    {stage.filePath}
                  </div>
                </div>
              </button>

              {index < stageData.length - 1 && (
                <div className="flex items-center px-1">
                  <ArrowRight className="w-3 h-3 text-white/20" />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
