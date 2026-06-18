import { BookOpen, Database, ArrowRight } from 'lucide-react';
import { knowledgeCollections } from '../data/mockData';

export default function KnowledgeSection() {
  return (
    <div className="bg-[#16213e]/50 backdrop-blur-sm rounded-2xl p-6 border border-white/5">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-8 h-8 rounded-lg bg-[#e94560]/20 flex items-center justify-center">
          <Database className="w-4 h-4 text-[#e94560]" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-white">知识库概览</h3>
          <p className="text-xs text-white/40">9 大知识集合</p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-3">
        {knowledgeCollections.map((item) => (
          <div
            key={item.id}
            className="bg-[#0f3460]/30 rounded-xl p-4 border border-white/5 hover:border-[#e94560]/30 transition-all duration-200 group cursor-pointer"
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-[#e94560]/70" />
                <span className="text-sm font-medium text-white">{item.name}</span>
              </div>
              <span className="text-xs text-[#e94560] font-medium bg-[#e94560]/10 px-2 py-0.5 rounded">
                {item.count} 条
              </span>
            </div>
            <p className="text-xs text-white/50 mb-2 line-clamp-2">{item.description}</p>
            <div className="flex items-center gap-1 text-xs text-white/30">
              <span>来源:</span>
              <span className="text-white/40">{item.source}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
