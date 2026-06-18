import { Briefcase } from 'lucide-react';
import { brands } from '../data/mockData';

const industryColors: Record<string, string> = {
  '母婴': 'bg-pink-500/20 text-pink-300 border-pink-500/30',
  '大健康': 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
  '家居家装': 'bg-amber-500/20 text-amber-300 border-amber-500/30',
  '汽车': 'bg-blue-500/20 text-blue-300 border-blue-500/30',
  '酒类': 'bg-purple-500/20 text-purple-300 border-purple-500/30',
  '食品': 'bg-orange-500/20 text-orange-300 border-orange-500/30',
  '珠宝': 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
  '设计': 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30',
};

export default function BrandsSection() {
  return (
    <div className="bg-[#16213e]/50 backdrop-blur-sm rounded-2xl p-6 border border-white/5">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-8 h-8 rounded-lg bg-[#e94560]/20 flex items-center justify-center">
          <Briefcase className="w-4 h-4 text-[#e94560]" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-white">服务品牌</h3>
          <p className="text-xs text-white/40">16 个品牌客户</p>
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {brands.map((brand) => (
          <div
            key={brand.id}
            className={`
              px-3 py-2 rounded-lg border text-sm font-medium
              transition-all duration-200 hover:scale-105 cursor-pointer
              ${industryColors[brand.industry] || 'bg-white/10 text-white/70 border-white/20'}
            `}
          >
            <span className="text-white">{brand.name}</span>
          </div>
        ))}
      </div>

      <div className="mt-4 pt-4 border-t border-white/5">
        <div className="flex flex-wrap gap-2">
          {Object.entries(industryColors).map(([industry, colorClass]) => (
            <div
              key={industry}
              className={`px-2 py-1 rounded text-xs border ${colorClass}`}
            >
              {industry}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
