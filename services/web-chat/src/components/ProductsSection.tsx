import { Box, Zap, CheckCircle2 } from 'lucide-react';
import { products } from '../data/mockData';

const maturityColors = {
  '成熟': 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  'Demo': 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  '有接口': 'bg-blue-500/20 text-blue-400 border-blue-500/30',
};

export default function ProductsSection() {
  return (
    <div className="bg-[#16213e]/50 backdrop-blur-sm rounded-2xl p-6 border border-white/5">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-8 h-8 rounded-lg bg-[#e94560]/20 flex items-center justify-center">
          <Box className="w-4 h-4 text-[#e94560]" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-white">产品能力</h3>
          <p className="text-xs text-white/40">6 大产品线</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {products.map((product) => (
          <div
            key={product.id}
            className="bg-[#0f3460]/30 rounded-xl p-4 border border-white/5 hover:border-[#e94560]/30 transition-all duration-200 group"
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2">
                <Zap className="w-4 h-4 text-[#e94560]" />
                <span className="text-sm font-medium text-white">{product.name}</span>
              </div>
              <span className={`
                px-2 py-0.5 rounded text-xs font-medium border
                ${maturityColors[product.maturity as keyof typeof maturityColors] || maturityColors['成熟']}
              `}>
                {product.maturity}
              </span>
            </div>

            <div className="mb-3">
              <div className="flex items-center justify-between text-xs text-white/40 mb-1">
                <span>成熟度</span>
                <span>{product.maturityLevel}%</span>
              </div>
              <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-[#e94560] to-[#0f3460] rounded-full transition-all duration-500"
                  style={{ width: `${product.maturityLevel}%` }}
                />
              </div>
            </div>

            <p className="text-xs text-white/60 mb-2 line-clamp-2">{product.coreAbility}</p>

            <div className="flex items-center gap-1 text-xs text-white/40">
              <CheckCircle2 className="w-3 h-3 text-emerald-400/60" />
              <span className="truncate">{product.customers}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
