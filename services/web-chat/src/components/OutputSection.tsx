import { Presentation, FileText, Download, CheckCircle2, Workflow, Archive, Database } from 'lucide-react';
import { outputFormats } from '../data/mockData';

const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
  'Presentation': Presentation,
  'FileText': FileText,
  'Download': Download,
};

export default function OutputSection() {
  return (
    <div className="bg-[#16213e]/50 backdrop-blur-sm rounded-2xl p-6 border border-white/5">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-emerald-500/20 flex items-center justify-center">
            <Download className="w-4 h-4 text-emerald-400" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">输出成果 & 能力闭环</h3>
            <p className="text-xs text-white/40">飞书 Slides / Docx / PPTX + 知识反哺 L3 记忆层</p>
          </div>
        </div>
        <div className="flex items-center gap-2 text-xs text-white/40 font-mono">
          <Workflow className="w-3.5 h-3.5 text-emerald-400" />
          <span>skills/s8_format_output.py + skills/s9_archive.py</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-6">
        {outputFormats.map((format) => {
          const IconComponent = iconMap[format.icon] || FileText;
          return (
            <div
              key={format.id}
              className="bg-[#0f3460]/30 rounded-xl p-4 border border-white/5 hover:border-emerald-500/30 transition-all duration-200"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="w-10 h-10 rounded-xl bg-emerald-500/20 flex items-center justify-center">
                  <IconComponent className="w-5 h-5 text-emerald-400" />
                </div>
                <div className="flex items-center gap-1 text-xs text-emerald-400">
                  <CheckCircle2 className="w-3 h-3" />
                  <span>就绪</span>
                </div>
              </div>
              <h4 className="text-sm font-medium text-white mb-1">{format.name}</h4>
              <p className="text-xs text-white/50 mb-3 leading-relaxed">{format.description}</p>
              <div className="space-y-1.5 pt-3 border-t border-white/5">
                <div className="text-[10px] text-white/40 font-mono">
                  {format.id === 'slides' && '→ lark-cli slides +create'}
                  {format.id === 'docx' && '→ lark-cli docs +create'}
                  {format.id === 'pptx' && '→ python-pptx /data/exports/'}
                </div>
                <div className="text-[9px] text-white/30 font-mono">
                  {format.id === 'slides' && 'xml_presentation_id → slide create'}
                  {format.id === 'docx' && 'API v2 · 50000 字截断'}
                  {format.id === 'pptx' && '16:9 宽屏 · 品牌色映射'}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* 成果流转与知识反哺 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div className="bg-[#0f3460]/30 rounded-xl p-4 border border-white/5" style={{ borderLeft: '3px solid #8e44ad' }}>
          <div className="flex items-center gap-2 mb-3">
            <Archive className="w-4 h-4 text-[#8e44ad]" />
            <span className="text-xs font-semibold text-white/80">知识反哺流程 (Knowledge Feedback)</span>
          </div>
          <ul className="space-y-1.5 text-[10px] text-white/50 font-mono leading-relaxed">
            <li className="flex items-start gap-2">
              <span className="text-[#8e44ad]">•</span>
              <span>S9: _update_brand_info() → brand_info table UPSERT</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-[#8e44ad]">•</span>
              <span>S9: _update_case_library() → competitor_library / case_labels</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-[#8e44ad]">•</span>
              <span>S9: _update_review_library() → review_records table</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-[#8e44ad]">•</span>
              <span>MemoryStore.save_session() → L3 session_memory</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-[#8e44ad]">•</span>
              <span>MaterialLibraryLoader 触发 re-distill() 闭环</span>
            </li>
          </ul>
        </div>

        <div className="bg-[#0f3460]/30 rounded-xl p-4 border border-white/5" style={{ borderLeft: '3px solid #3498db' }}>
          <div className="flex items-center gap-2 mb-3">
            <Database className="w-4 h-4 text-[#3498db]" />
            <span className="text-xs font-semibold text-white/80">核心能力映射 (Core Capabilities)</span>
          </div>
          <div className="grid grid-cols-2 gap-2 text-[10px] text-white/50">
            <div className="bg-white/5 rounded-lg p-2 border border-white/5">
              <div className="text-white/70 font-medium mb-0.5">品牌色映射</div>
              <div className="font-mono text-white/30">12 品牌预设色</div>
            </div>
            <div className="bg-white/5 rounded-lg p-2 border border-white/5">
              <div className="text-white/70 font-medium mb-0.5">10 页标准结构</div>
              <div className="font-mono text-white/30">封面 → 实施路径</div>
            </div>
            <div className="bg-white/5 rounded-lg p-2 border border-white/5">
              <div className="text-white/70 font-medium mb-0.5">9 种布局类型</div>
              <div className="font-mono text-white/30">two_column / timeline 等</div>
            </div>
            <div className="bg-white/5 rounded-lg p-2 border border-white/5">
              <div className="text-white/70 font-medium mb-0.5">HTML 中间格式</div>
              <div className="font-mono text-white/30">→ Slides / Docx / PPTX</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
