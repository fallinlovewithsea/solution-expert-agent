import { ArrowRight, GitBranch, Package, FileOutput, Server, Workflow } from 'lucide-react';

interface StageDetailProps {
  activeStage: string;
}

const stageDetails: Record<string, {
  title: string;
  description: string;
  filePath: string;
  className: string;
  inputs: { label: string; source: string }[];
  outputs: { label: string; target: string }[];
  dataFlow: string[];
  features: string[];
  accentColor: string;
}> = {
  S1: {
    title: '商机评估',
    description: '基于 16 个已知客户库 + 9 行业风险评估，判断是否跟进该项目',
    filePath: 'skills/s1_opportunity.py',
    className: 'S1OpportunityAssessment',
    inputs: [
      { label: '客户初步需求', source: '用户输入 / 飞书消息' },
      { label: '行业信息', source: '自动识别 or 用户输入' },
      { label: '预算范围', source: '用户输入' },
    ],
    outputs: [
      { label: 'GO / NO-GO 决策', target: 'AgentState.opportunity_result' },
      { label: '项目分类', target: 'opportunity_result.project_type' },
      { label: '风险因素', target: 'opportunity_result.risk_factors' },
    ],
    dataFlow: ['已知客户库匹配', '行业风险评估 → INDUSTRY_RISK 映射表', '置信度打分 → 综合评估'],
    features: [
      '16 品牌已知客户快速识别',
      '9 行业风险矩阵评估',
      '置信度 / 风险分级 / 建议输出',
      '技能基础类: BaseSkill (skills/base.py)'
    ],
    accentColor: '#3498db'
  },
  S2: {
    title: '需求诊断',
    description: '使用 LLM 从客户沟通记录 / 招标文件中提取结构化需求',
    filePath: 'skills/s2_requirement.py',
    className: 'S2RequirementDiagnosis',
    inputs: [
      { label: '客户沟通记录 / RFP', source: '飞书 Bot → feishu-bot/main.py' },
      { label: '招标文件内容', source: 'lark-cli docs fetch' },
    ],
    outputs: [
      { label: '需求文档 (requirement_document)', target: 'AgentState → 传递至 S3/S4/S5' },
      { label: '品牌资源提取', target: 'brand_assets 字段' },
      { label: '缺失信息检测', target: '主动追问用户' },
    ],
    dataFlow: [
      'LLM 提取 (app.llm.router.get_llm task_type=light)',
      '写入 MemoryStore (app/db/memory.py)',
      'record_search / record_industry 双向记录'
    ],
    features: [
      'JSON 结构化提取：client_name / industry / sub_category / pain_points / goals / budget / timeline',
      '信息缺口检测与主动追问',
      '品牌色映射 (12 品牌预设颜色)',
      '竞品列表识别与提取'
    ],
    accentColor: '#e94560'
  },
  S3: {
    title: '行业洞察',
    description: '采集小红书行业数据、竞品数据、客户数据，并写入 L1 原始数据层',
    filePath: 'skills/s3_industry_insight.py',
    className: 'S3IndustryInsight',
    inputs: [
      { label: '行业 / 子品类', source: 'S2.requirement_document' },
      { label: '竞品名单', source: 'requirement_document.competitors' },
      { label: '客户品牌', source: 'requirement_document.client_name' },
    ],
    outputs: [
      { label: 'industry_analysis (行业分析)', target: 'L1 raw_xhs_data table' },
      { label: 'competitor_analysis (竞品分析)', target: '写入 PG + Qdrant 向量' },
      { label: 'client_diagnosis + growth_analysis', target: '传递至 S4 客户洞察' },
    ],
    dataFlow: [
      'XHSCollector.search_industry → search_competitor → search_client',
      '写入 raw_xhs_data (collect_type: industry / competitor / client)',
      'KnowledgeDistiller.distill_xhs_data → xhs_insights collection',
    ],
    features: [
      '小红书 3 维度数据采集 + 分析',
      'L1 → L2 分层数据架构（原始 / 蒸馏）',
      '行业关键词矩阵 INDUSTRY_KEYWORDS',
      'content_themes / hot_elements / content_gap 多维度输出'
    ],
    accentColor: '#16a085'
  },
  S4: {
    title: '客户洞察',
    description: '综合 S2 需求文档 + S3 行业洞察报告，分析核心痛点与增长机会',
    filePath: 'skills/s4_client_insight.py',
    className: 'S4ClientInsight',
    inputs: [
      { label: 'requirement_document', source: 'S2 输出' },
      { label: 'insight_report', source: 'S3 输出 (industry + growth_analysis)' },
    ],
    outputs: [
      { label: 'core_pain_points (核心痛点)', target: 'AgentState.client_insight' },
      { label: 'market_opportunities (市场机会)', target: '传递至 S5 方案设计' },
      { label: 'growth_model_mapping (增长模型映射)', target: 'S5.operation_strategy 依据' },
    ],
    dataFlow: [
      '需求诊断数据 ∩ 行业洞察数据 → 客户洞察',
      '痛点与行业机会交叉匹配',
      'growth_model 库检索（方法论）'
    ],
    features: [
      '痛点分类：内容 / 流量 / 转化 / 品牌',
      '增长模型匹配: K³FS 三层传播模型',
      '策略方向建议（platform_strategy / growth_strategy）',
    ],
    accentColor: '#8e44ad'
  },
  S5: {
    title: '方案设计',
    description: '匹配增长模型，生成运营策略 + 工具赋能 + 实施路径 + 预算规划',
    filePath: 'skills/s5_proposal_design.py',
    className: 'S5ProposalDesign',
    inputs: [
      { label: 'client_insight', source: 'S4 输出' },
      { label: 'insight_report', source: 'S3 输出' },
      { label: 'requirement_document', source: 'S2 输出' },
    ],
    outputs: [
      { label: 'full_proposal (完整方案 dict)', target: 'AgentState.full_proposal' },
      { label: 'operation_strategy (运营策略)', target: '包含行业洞察/客户诊断/竞品对标/增长/平台/执行' },
      { label: 'tool_empowerment + implementation_path', target: 'S7 内容生成依据' },
    ],
    dataFlow: [
      '加载标准提案框架（通用提案 7 步法）',
      '确定方案方向 → 按模块填充内容',
      '预算与资源规划'
    ],
    features: [
      '7 步标准提案框架',
      '运营策略（6 个子模块）+ 工具赋能（产品能力匹配）+ 实施路径',
      '案例模块预先留位，待 S6 匹配后填充',
      '产品方案能力检索 (product_solution / growth_model)'
    ],
    accentColor: '#d35400'
  },
  S6: {
    title: '案例匹配',
    description: '4 维加权打分（行业 40% + 类型 20% + 痛点 20% + 方案模块 20%）',
    filePath: 'skills/s6_case_match.py',
    className: 'S6CaseMatch',
    inputs: [
      { label: 'industry', source: 'S2.requirement_document' },
      { label: 'customer_type / sub_category', source: 'S2 输出' },
      { label: 'pain_points', source: 'S4.client_insight' },
      { label: 'solution_modules', source: 'S5.full_proposal' },
    ],
    outputs: [
      { label: 'matched_cases: 前 5 相关案例', target: 'AgentState.matched_cases' },
      { label: 'recommendation (推荐语)', target: 'S7 内容生成输入' },
    ],
    dataFlow: [
      'VectorStoreClient.search("case_labels", query, limit=20)',
      '向量库检索 → 4 维加权打分 → 排序',
      '降级: 内置 10+ 行业案例兜底'
    ],
    features: [
      'Qdrant 向量检索 (services/orchestrator/app/vector_store/client.py)',
      'relation_type: applied_in / similar_to / competes_with',
      '多维打分，行业权重最高',
      '10+ 标杆案例内置：飞鹤 / a2 / 英氏 / 林氏家居 / 领克 / 极氪 等'
    ],
    accentColor: '#27ae60'
  },
  S7: {
    title: '内容生成',
    description: '生成 10 页标准 Slide，优先使用方案数据，不足时 LLM 补充',
    filePath: 'skills/s7_content_gen.py',
    className: 'S7ContentGeneration',
    inputs: [
      { label: 'full_proposal', source: 'S5 输出' },
      { label: 'matched_cases', source: 'S6 输出' },
      { label: 'brand_assets', source: 'S2.brand_assets + brand color mapping' },
    ],
    outputs: [
      { label: 'slides: 10 页 Slide dict 列表', target: 'AgentState.slides' },
      { label: 'slide_count = 10', target: '传递至 S8 格式输出' },
    ],
    dataFlow: [
      'SLIDE_STRUCTURE 10 页模板 → 逐页生成',
      '数据优先填充 → 不足部分调用 LLM (task_type=light)',
      'HTML → Slide 中间格式便于 S8 转换'
    ],
    features: [
      '10 页标准结构：封面 / 公司介绍 / 行业洞察 / 客户诊断 / 竞品对标 / 解决方案 / 工具赋能 / 案例展示 / 实施路径 / 团队介绍',
      '9 种布局类型 (cover / two_column / chart_focus / bullet_cards / comparison_table / icon_grid / grid_cards / case_card / timeline)',
      '品牌色映射 S8 统一转换',
      'get_llm(task_type="light") 智能补充内容'
    ],
    accentColor: '#f39c12'
  },
  S8: {
    title: '格式输出',
    description: '生成飞书 Slides + Docx + PPTX 导出，应用品牌色映射',
    filePath: 'skills/s8_format_output.py',
    className: 'S8FormatOutput',
    inputs: [
      { label: 'slides (S7 生成的 10 页列表)', source: 'AgentState.slides' },
      { label: 'brand_assets + brand_name', source: 'S2 输出 + 品牌色映射' },
    ],
    outputs: [
      { label: 'slides_url: 飞书 Slides 链接', target: 'AgentState.slides_url' },
      { label: 'docx_url: 飞书 Docx 链接', target: 'AgentState.docx_url' },
      { label: 'pptx_path: 本地 PPTX 文件', target: '/data/exports/{brand}_{uuid}.pptx' },
    ],
    dataFlow: [
      'lark-cli slides +create → xml_presentation_id',
      'lark-cli slides xml_presentation.slide create 逐页创建',
      'lark-cli docs +create (API v2, 50000 字上限截断)',
      'python-pptx 生成专业 PPTX 到 /data/exports/',
      'MemoryStore.record_output_format(user_id, format_type)'
    ],
    features: [
      '飞书 Slides / Docx / PPTX 三格式并行',
      '12 品牌色预设映射 (飞鹤 / a2 / 英氏 / 金领冠 / 林氏家居 / 老庙 / 蒙牛 / 领克 / 极氪 / 利星行 / 可画 / 董酒)',
      'lark-cli 可用性检测 + 降级方案',
      'python-pptx 16:9 宽屏专业模板'
    ],
    accentColor: '#c0392b'
  },
  S9: {
    title: '复盘归档',
    description: '更新品牌库 / 竞品库 / 复盘库 + 写入 L3 记忆层，形成知识闭环',
    filePath: 'skills/s9_archive.py',
    className: 'S9Archive',
    inputs: [
      { label: 'final_proposal (完整方案)', source: 'S5 + S6 + S7 整合' },
      { label: 'review_comments (审核意见)', source: '人工审核节点 (human_review)' },
      { label: 'bid_result (中标结果)', source: '用户输入' },
      { label: 'user_id / session_id', source: 'L3 记忆层标识' },
    ],
    outputs: [
      { label: 'updated_libraries (已更新物料库列表)', target: 'AgentState.archive_result' },
      { label: 'review_report (复盘报告文本)', target: '可保存为飞书文档' },
    ],
    dataFlow: [
      'brand_info 表 UPSERT (品牌信息表，按行业索引)',
      'competitor_library 表更新 (写入 benchmark_data JSON)',
      'review_records 表插入新记录 → review_id 生成',
      'MemoryStore.save_session + record_bid_result + increment_interaction',
      'MaterialLibraryLoader 触发再次蒸馏（知识闭环）'
    ],
    features: [
      '8 大物料库自动更新：品牌库 / 竞品库 / 复盘库 + 关联库',
      'L3 Memory Layer 会话记忆：user_id, session_id, interaction 计数',
      'LangGraph human_review 节点阻塞式人工审核',
      '知识反哺：提案结束即丰富知识库，下次提案质量自动提升'
    ],
    accentColor: '#2c3e50'
  }
};

export default function StageDetail({ activeStage }: StageDetailProps) {
  const detail = stageDetails[activeStage];

  if (!detail) return null;

  return (
    <div className="bg-[#16213e]/50 backdrop-blur-sm rounded-2xl p-6 border border-white/5">
      <div className="flex items-start justify-between mb-5">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <span
              className="text-2xl font-bold text-white"
              style={{ textShadow: `0 0 20px ${detail.accentColor}80` }}
            >
              {activeStage}
            </span>
            <h3 className="text-xl font-semibold text-white">{detail.title}</h3>
          </div>
          <div className="flex items-center gap-2 text-xs text-white/40 font-mono">
            <Workflow className="w-3.5 h-3.5" style={{ color: detail.accentColor }} />
            <span>{detail.filePath}</span>
            <span className="text-white/20">::</span>
            <span style={{ color: detail.accentColor }}>{detail.className}</span>
          </div>
        </div>
      </div>

      <p className="text-sm text-white/70 mb-6 leading-relaxed">{detail.description}</p>

      <div className="grid grid-cols-2 gap-4 mb-5">
        <div className="bg-[#0f3460]/20 rounded-xl p-4 border border-white/5">
          <div className="flex items-center gap-2 mb-3">
            <Package className="w-4 h-4" style={{ color: detail.accentColor }} />
            <span className="text-xs font-semibold text-white/80">输入 Inputs</span>
          </div>
          <ul className="space-y-2.5">
            {detail.inputs.map((input, i) => (
              <li key={i} className="text-xs">
                <div className="text-white/80 font-medium">{input.label}</div>
                <div className="text-white/30 font-mono text-[10px] mt-0.5 pl-2 border-l-2 border-white/10">
                  ← {input.source}
                </div>
              </li>
            ))}
          </ul>
        </div>

        <div className="bg-[#0f3460]/20 rounded-xl p-4 border border-white/5">
          <div className="flex items-center gap-2 mb-3">
            <FileOutput className="w-4 h-4" style={{ color: detail.accentColor }} />
            <span className="text-xs font-semibold text-white/80">输出 Outputs</span>
          </div>
          <ul className="space-y-2.5">
            {detail.outputs.map((output, i) => (
              <li key={i} className="text-xs">
                <div className="text-white/80 font-medium">{output.label}</div>
                <div className="font-mono text-[10px] mt-0.5 pl-2 border-l-2 border-white/10" style={{ color: detail.accentColor + 'aa' }}>
                  → {output.target}
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4">
        <div className="bg-[#0f3460]/20 rounded-xl p-4 border border-white/5">
          <div className="flex items-center gap-2 mb-3">
            <GitBranch className="w-4 h-4" style={{ color: detail.accentColor }} />
            <span className="text-xs font-semibold text-white/80">数据流向 Data Flow</span>
          </div>
          <div className="flex flex-wrap gap-2 items-center">
            {detail.dataFlow.map((step, i) => (
              <div key={i} className="flex items-center gap-2">
                <span className="text-xs text-white/60 bg-white/5 px-2 py-1 rounded-lg border border-white/10">
                  {step}
                </span>
                {i < detail.dataFlow.length - 1 && (
                  <ArrowRight className="w-3 h-3 text-white/20" />
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="bg-[#0f3460]/20 rounded-xl p-4 border border-white/5">
          <div className="flex items-center gap-2 mb-3">
            <Server className="w-4 h-4" style={{ color: detail.accentColor }} />
            <span className="text-xs font-semibold text-white/80">核心能力 Features</span>
          </div>
          <div className="grid grid-cols-2 gap-2">
            {detail.features.map((feature, i) => (
              <div key={i} className="flex items-start gap-2 text-xs text-white/60">
                <span className="mt-1 w-1 h-1 rounded-full flex-shrink-0" style={{ backgroundColor: detail.accentColor }} />
                <span>{feature}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
