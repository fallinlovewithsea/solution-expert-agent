import { Globe, TrendingUp } from 'lucide-react';
import { industries } from '../data/mockData';

export default function IndustriesSection() {
  return (
    <div className="bg-[#16213e]/50 backdrop-blur-sm rounded-2xl p-6 border border-white/5">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-8 h-8 rounded-lg bg-emerald-500/20 flex items-center justify-center">
          <Globe className="w-4 h-4 text-emerald-400" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-white">覆盖行业</h3>
          <p className="text-xs text-white/40">10 个行业赛道</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {industries.map((industry) => (
          <div
            key={industry.id}
            className="bg-[#0f3460]/30 rounded-xl p-4 border border-white/5 hover:border-emerald-500/30 transition-all duration-200 group cursor-pointer"
          >
            <div className="flex items-center gap-2 mb-2">
              <Globe className="w-4 h-4 text-emerald-400/70" />
              <span className="text-sm font-medium text-white">{industry.name}</span>
            </div>
            <p className="text-xs text-white/60 mb-2">{industry.coreStrategy}</p>
            <div className="flex items-center gap-1 text-xs text-emerald-400/60">
              <TrendingUp className="w-3 h-3" />
              <span className="truncate">{industry.highlight}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
