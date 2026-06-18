import { Check, Circle, Loader2 } from 'lucide-react';
import { stages } from '../data/mockData';

interface FlowOverviewProps {
  activeStage: string;
  onStageClick: (stageId: string) => void;
}

export default function FlowOverview({ activeStage, onStageClick }: FlowOverviewProps) {
  const getStatusIcon = (status: string, id: string, isActive: boolean) => {
    if (status === 'completed') {
      return <Check className="w-4 h-4 text-emerald-400" />;
    }
    if (status === 'in_progress') {
      return <Loader2 className="w-4 h-4 text-[#e94560] animate-spin" />;
    }
    if (isActive) {
      return <Circle className="w-4 h-4 text-[#e94560]" fill="#e94560" />;
    }
    return <Circle className="w-4 h-4 text-white/30" />;
  };

  return (
    <div className="bg-[#16213e]/50 backdrop-blur-sm rounded-2xl p-6 border border-white/5">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-white">提案生成流程</h2>
        <span className="text-xs text-white/40">S1 - S9</span>
      </div>
      <div className="flex items-center gap-2 overflow-x-auto pb-2">
        {stages.map((stage, index) => {
          const isActive = activeStage === stage.id;
          const isCompleted = stage.status === 'completed';
          const isInProgress = stage.status === 'in_progress';

          return (
            <div key={stage.id} className="flex items-center">
              <button
                onClick={() => onStageClick(stage.id)}
                className={`
                  relative flex flex-col items-center gap-2 px-3 py-3 rounded-xl
                  transition-all duration-200 min-w-[80px]
                  ${isActive
                    ? 'bg-[#e94560]/20 border border-[#e94560]/50 shadow-lg shadow-[#e94560]/10'
                    : isCompleted
                      ? 'bg-emerald-500/10 border border-emerald-500/30 hover:bg-emerald-500/20'
                      : isInProgress
                        ? 'bg-[#0f3460]/50 border border-[#0f3460] hover:bg-[#0f3460]/70'
                        : 'bg-white/5 border border-white/10 hover:bg-white/10'
                  }
                `}
              >
                <div className="flex items-center gap-1.5">
                  <span className={`
                    text-xs font-bold
                    ${isActive || isCompleted || isInProgress ? 'text-white' : 'text-white/40'}
                  `}>
                    {stage.id}
                  </span>
                  {getStatusIcon(stage.status, stage.id, isActive)}
                </div>
                <span className={`
                  text-xs text-center leading-tight
                  ${isActive ? 'text-white font-medium' : 'text-white/50'}
                `}>
                  {stage.name}
                </span>
              </button>
              {index < stages.length - 1 && (
                <div className={`
                  w-6 h-0.5 mx-1
                  ${index < stages.findIndex(s => s.id === activeStage)
                    ? 'bg-emerald-500/50'
                    : 'bg-white/10'
                  }
                `} />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
