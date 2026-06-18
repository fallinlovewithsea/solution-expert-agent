import { useState } from 'react';
import Header from './components/Header';
import FlowOverview from './components/FlowOverview';
import StageDetail from './components/StageDetail';
import KnowledgeSection from './components/KnowledgeSection';
import BrandsSection from './components/BrandsSection';
import IndustriesSection from './components/IndustriesSection';
import ProductsSection from './components/ProductsSection';
import OutputSection from './components/OutputSection';

function App() {
  const [activeStage, setActiveStage] = useState('S1');

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#1a1a2e] via-[#16213e] to-[#0f3460]">
      <Header />

      <main className="pt-24 pb-12 px-6 max-w-7xl mx-auto">
        {/* Flow Overview */}
        <div className="mb-8">
          <FlowOverview activeStage={activeStage} onStageClick={setActiveStage} />
        </div>

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Stage Detail - Takes 1 column */}
          <div className="lg:col-span-1">
            <StageDetail activeStage={activeStage} />
          </div>

          {/* Knowledge Section - Takes 2 columns */}
          <div className="lg:col-span-2">
            <KnowledgeSection />
          </div>
        </div>

        {/* Brands Section */}
        <div className="mb-8">
          <BrandsSection />
        </div>

        {/* Industries Section */}
        <div className="mb-8">
          <IndustriesSection />
        </div>

        {/* Products Section */}
        <div className="mb-8">
          <ProductsSection />
        </div>

        {/* Output Section */}
        <div className="mb-8">
          <OutputSection />
        </div>
      </main>

      {/* Footer */}
      <footer className="py-6 text-center text-xs text-white/30 border-t border-white/5">
        <p>解决方案专家 Agent 控制台 v1.0 | 数据架构版本 7.0</p>
        <p className="mt-1">易美传播 · 弘摩科技</p>
      </footer>
    </div>
  );
}

export default App;
