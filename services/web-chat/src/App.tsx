import { useState } from 'react';
import Header from './components/Header';
import FlowOverview from './components/FlowOverview';
import StageDetail from './components/StageDetail';
import KnowledgeSection from './components/KnowledgeSection';
import ArchitectureSection from './components/ArchitectureSection';
import ProductsSection from './components/ProductsSection';
import BrandsSection from './components/BrandsSection';
import IndustriesSection from './components/IndustriesSection';
import OutputSection from './components/OutputSection';

function App() {
  const [activeStage, setActiveStage] = useState<string>('S1');

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#1a1a2e] via-[#16213e] to-[#0f3460]">
      <Header />

      <main className="pt-24 pb-12 px-6 max-w-[1400px] mx-auto">
        {/* 核心流程概览 */}
        <div className="mb-8">
          <FlowOverview activeStage={activeStage} onStageClick={setActiveStage} />
        </div>

        {/* 阶段详情 + 知识库 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <StageDetail activeStage={activeStage} />
          <KnowledgeSection />
        </div>

        {/* 系统架构概览 */}
        <div className="mb-8">
          <ArchitectureSection />
        </div>

        {/* 产品能力矩阵 */}
        <div className="mb-8">
          <ProductsSection />
        </div>

        {/* 服务品牌与行业覆盖 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <BrandsSection />
          <IndustriesSection />
        </div>

        {/* 输出成果 & 能力闭环 */}
        <div className="mb-8">
          <OutputSection />
        </div>
      </main>

      <footer className="py-8 text-center border-t border-white/10 bg-[#0f3460]/30">
        <div className="max-w-3xl mx-auto px-6">
          <p className="text-sm font-semibold text-white mb-1">解决方案专家 Agent Console</p>
          <p className="text-[11px] text-white/40 mb-2">
            Proposal Generation Expert Agent · v1.0
          </p>
          <p className="text-[10px] text-white/30 font-mono leading-relaxed">
            services/orchestrator/app/agent.py · LangGraph StateGraph · 9 Skills ·
            9 Knowledge Collections · 3 Layers · 6 Products · 16 Brands · 10 Industries
          </p>
          <div className="mt-3 flex flex-wrap justify-center gap-2 text-[10px] text-white/30">
            <span>PostgreSQL</span>
            <span>·</span>
            <span>Qdrant</span>
            <span>·</span>
            <span>Redis</span>
            <span>·</span>
            <span>Ollama</span>
            <span>·</span>
            <span>React + TypeScript</span>
            <span>·</span>
            <span>FastAPI</span>
            <span>·</span>
            <span>Nginx</span>
            <span>·</span>
            <span>Docker Compose</span>
          </div>
          <div className="mt-3 pt-3 border-t border-white/5 text-[10px] text-white/20">
            易美传播 (营销侧) · 弘摩科技 (技术侧) · 双品牌主体
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
