import { ArrowRight, Package, FileOutput } from 'lucide-react';
import { stages } from '../data/mockData';

interface StageDetailProps {
  activeStage: string;
}

export default function StageDetail({ activeStage }: StageDetailProps) {
  const stage = stages.find(s => s.id === activeStage);

  if (!stage) {
    return null;
  }

  const statusColors = {
    completed: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
    in_progress: 'bg-[#e94560]/20 text-[#e94560] border-[#e94560]/30',
    pending: 'bg-white/10 text-white/50 border-white/20'
  };

  const statusLabels = {
    completed: '已完成',
    in_progress: '进行中',
    pending: '待开始'
  };

  return (
    <div className="bg-[#16213e]/50 backdrop-blur-sm rounded-2xl p-6 border border-white/5">
      <div className="flex items-start justify-between mb-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <span className="text-2xl font-bold text-white">{stage.id}</span>
            <h3 className="text-xl font-semibold text-white">{stage.name}</h3>
          </div>
          <span className={`
            inline-block px-3 py-1 rounded-full text-xs font-medium border
            ${statusColors[stage.status]}
          `}>
            {statusLabels[stage.status]}
          </span>
        </div>
      </div>

      <p className="text-white/70 mb-6 leading-relaxed">
        {stage.description}
      </p>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-[#0f3460]/30 rounded-xl p-4 border border-white/5">
          <div className="flex items-center gap-2 mb-3">
            <Package className="w-4 h-4 text-[#e94560]" />
            <span className="text-sm font-medium text-white/70">输入</span>
          </div>
          <ul className="space-y-2">
            {stage.inputs.map((input, i) => (
              <li key={i} className="flex items-center gap-2 text-sm text-white/60">
                <ArrowRight className="w-3 h-3 text-[#e94560]/60" />
                {input}
              </li>
            ))}
          </ul>
        </div>

        <div className="bg-[#0f3460]/30 rounded-xl p-4 border border-white/5">
          <div className="flex items-center gap-2 mb-3">
            <FileOutput className="w-4 h-4 text-emerald-400" />
            <span className="text-sm font-medium text-white/70">输出</span>
          </div>
          <ul className="space-y-2">
            {stage.outputs.map((output, i) => (
              <li key={i} className="flex items-center gap-2 text-sm text-white/60">
                <ArrowRight className="w-3 h-3 text-emerald-400/60" />
                {output}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
