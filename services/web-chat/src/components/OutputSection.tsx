import { Presentation, FileText, Download, CheckCircle2 } from 'lucide-react';
import { outputFormats } from '../data/mockData';

const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
  'Presentation': Presentation,
  'FileText': FileText,
  'Download': Download,
};

export default function OutputSection() {
  return (
    <div className="bg-[#16213e]/50 backdrop-blur-sm rounded-2xl p-6 border border-white/5">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-8 h-8 rounded-lg bg-emerald-500/20 flex items-center justify-center">
          <Download className="w-4 h-4 text-emerald-400" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-white">输出成果</h3>
          <p className="text-xs text-white/40">提案格式支持</p>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3">
        {outputFormats.map((format) => {
          const IconComponent = iconMap[format.icon] || FileText;
          return (
            <div
              key={format.id}
              className="bg-[#0f3460]/30 rounded-xl p-4 border border-white/5 hover:border-emerald-500/30 transition-all duration-200 text-center"
            >
              <div className="w-10 h-10 rounded-xl bg-emerald-500/20 flex items-center justify-center mx-auto mb-3">
                <IconComponent className="w-5 h-5 text-emerald-400" />
              </div>
              <h4 className="text-sm font-medium text-white mb-1">{format.name}</h4>
              <p className="text-xs text-white/50 mb-2 line-clamp-2">{format.description}</p>
              <div className="flex items-center justify-center gap-1 text-xs text-emerald-400">
                <CheckCircle2 className="w-3 h-3" />
                <span>就绪</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
