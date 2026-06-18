// 9个流程阶段数据
export const stages = [
  {
    id: 'S1',
    name: '商机评估',
    description: '基于16个已知客户库+9行业风险评估，判断是否跟进',
    status: 'completed' as const,
    inputs: ['客户初步需求', '行业', '预算'],
    outputs: ['评估结论（跟进/放弃）', '项目分类'],
    icon: 'Target'
  },
  {
    id: 'S2',
    name: '需求诊断',
    description: '从沟通记录中提取客户行业、痛点、预算、竞品、时间线',
    status: 'in_progress' as const,
    inputs: ['客户沟通记录', '招标文件'],
    outputs: ['需求文档', '品牌资源提取'],
    icon: 'ClipboardList'
  },
  {
    id: 'S3',
    name: '行业洞察',
    description: '采集小红书行业趋势、竞品数据、客户现状',
    status: 'pending' as const,
    inputs: ['行业关键词', '竞品品牌号', '客户账号'],
    outputs: ['行业分析报告', '竞品分析', '客户诊断'],
    icon: 'TrendingUp'
  },
  {
    id: 'S4',
    name: '客户洞察',
    description: '综合需求+行业数据，分析核心痛点与增长机会',
    status: 'pending' as const,
    inputs: ['需求文档', '行业洞察报告'],
    outputs: ['客户洞察汇总文档'],
    icon: 'UserSearch'
  },
  {
    id: 'S5',
    name: '方案设计',
    description: '匹配增长模型，生成运营策略+工具赋能+案例展示+实施路径',
    status: 'pending' as const,
    inputs: ['客户洞察', '行业数据', '标准提案框架'],
    outputs: ['品牌增长全案方案'],
    icon: 'FileText'
  },
  {
    id: 'S6',
    name: '案例匹配',
    description: '4维加权打分（行业40%+类型20%+痛点20%+方案模块20%）',
    status: 'pending' as const,
    inputs: ['行业', '客户类型', '痛点', '方案模块'],
    outputs: ['TOP5匹配案例'],
    icon: 'Copy'
  },
  {
    id: 'S7',
    name: '内容生成',
    description: '生成10页标准Slide，优先使用提案数据',
    status: 'pending' as const,
    inputs: ['品牌增长全案方案', '匹配案例', '品牌素材'],
    outputs: ['方案PPT初稿'],
    icon: 'PenTool'
  },
  {
    id: 'S8',
    name: '格式输出',
    description: '输出为飞书Slides/Docx/PPTX，支持12品牌色映射',
    status: 'pending' as const,
    inputs: ['方案PPT初稿'],
    outputs: ['飞书Slides', '飞书Docx', 'PPTX文件'],
    icon: 'Download'
  },
  {
    id: 'S9',
    name: '复盘归档',
    description: '更新品牌库、竞品库、复盘库+写入L3记忆层',
    status: 'pending' as const,
    inputs: ['提案终稿', '竞标结果'],
    outputs: ['归档资料', '物料库更新', '复盘报告'],
    icon: 'Archive'
  }
];

// 9大知识集合
export const knowledgeCollections = [
  {
    id: 'methodology',
    name: '核心方法论',
    description: '5大方法论+1子模型，覆盖用户转化链路、K³FS、AIGC等',
    count: 6,
    source: '飞书文档库'
  },
  {
    id: 'industry_strategy',
    name: '行业KOS矩阵策略',
    description: '行业KOS矩阵营销策略，覆盖母婴/大健康/家居等',
    count: 5,
    source: '飞书文档库'
  },
  {
    id: 'competitor_analysis',
    name: '行业竞品格局',
    description: '行业竞品格局分析，竞品投放策略拆解',
    count: 2,
    source: '飞书文档库'
  },
  {
    id: 'product_solution',
    name: '产品方案能力',
    description: '6大产品线完整能力介绍与报价体系',
    count: 6,
    source: '飞书文档库'
  },
  {
    id: 'case_labels',
    name: '客户案例标签',
    description: '历史成功案例标签，支持4维加权匹配',
    count: 12,
    source: '飞书文档库+聊天记录'
  },
  {
    id: 'proposal_review',
    name: '提案复盘方法论',
    description: '提案复盘与持续优化方法论',
    count: 2,
    source: '飞书文档库'
  },
  {
    id: 'brand_knowledge',
    name: '品牌知识定位',
    description: '品牌知识与定位，易美传播+弘摩科技双品牌',
    count: 3,
    source: '飞书文档库'
  },
  {
    id: 'xhs_insights',
    name: '小红书趋势洞察',
    description: '小红书内容趋势洞察，实时采集行业数据',
    count: 3,
    source: '飞书文档库'
  },
  {
    id: 'business_process',
    name: '商务流程团队',
    description: '商务流程与团队知识，双品牌合同体系',
    count: 5,
    source: '飞书文档库+聊天记录+日历'
  }
];

// 16个服务品牌
export const brands = [
  { id: 'feihe', name: '飞鹤', industry: '母婴' },
  { id: 'yingshi', name: '英氏', industry: '母婴' },
  { id: 'jinlingguan', name: '金领冠', industry: '母婴' },
  { id: 'paiute', name: '派特生物', industry: '大健康' },
  { id: 'kuaike', name: '快克', industry: '大健康' },
  { id: 'mengniu', name: '蒙牛', industry: '食品' },
  { id: 'laomiao', name: '老庙', industry: '珠宝' },
  { id: 'linshi', name: '林氏家居', industry: '家居家装' },
  { id: 'kehua', name: '可画', industry: '设计' },
  { id: 'dongjiu', name: '董酒', industry: '酒类' },
  { id: 'songsong', name: '松达', industry: '母婴' },
  { id: 'ouenbei', name: '欧恩贝', industry: '母婴' },
  { id: 'a2', name: 'a2', industry: '母婴' },
  { id: 'lixing', name: '利星行', industry: '汽车' },
  { id: 'lingke', name: '领克', industry: '汽车' },
  { id: 'jike', name: '极氪', industry: '汽车' }
];

// 10个覆盖行业
export const industries = [
  {
    id: 'mother_baby',
    name: '母婴',
    coreStrategy: '专业测评+矩阵规模化+评论区运营+搜索占位',
    highlight: '成分党测评、内容日历、AI保障矩阵稳定性'
  },
  {
    id: 'big_health',
    name: '大健康',
    coreStrategy: '医生/KOL背书+用户证言+合规审查',
    highlight: '专业信任建立、真实效果、长期搜索价值'
  },
  {
    id: 'home_decor',
    name: '家居家装',
    coreStrategy: '场景化内容+装修灵感+软装搭配',
    highlight: '场景化展示效果3倍于单品'
  },
  {
    id: 'automotive',
    name: '汽车',
    coreStrategy: 'KOS矩阵+体验内容+搜索拦截',
    highlight: '专业评测+用户真实反馈'
  },
  {
    id: 'liquor',
    name: '酒类',
    coreStrategy: '品牌故事+场景营销+品鉴内容',
    highlight: '高端品鉴+收藏价值'
  },
  {
    id: 'food',
    name: '食品',
    coreStrategy: '口味测评+场景种草+UGC裂变',
    highlight: '真实体验分享'
  },
  {
    id: 'jewelry',
    name: '珠宝',
    coreStrategy: '设计美学+高端定制+节日营销',
    highlight: '设计理念+工艺传承'
  },
  {
    id: 'design',
    name: '设计',
    coreStrategy: '创意展示+工具赋能+案例分享',
    highlight: '设计师人设+作品展示'
  },
  {
    id: 'tech',
    name: '技术',
    coreStrategy: '技术解读+产品对比+场景应用',
    highlight: '专业背书+技术深度'
  },
  {
    id: 'general',
    name: '通用',
    coreStrategy: '品牌传播+用户互动+转化闭环',
    highlight: '通用方法论适用多行业'
  }
];

// 6大产品能力
export const products = [
  {
    id: 'kos',
    name: 'KOS代发代管',
    maturity: '成熟',
    maturityLevel: 100,
    coreAbility: '母婴/大健康/家居3大行业方案，400+账号矩阵化管理',
    customers: '飞鹤、林氏家居、松达'
  },
  {
    id: 'aigc_content',
    name: 'AIGC内容制作',
    maturity: '成熟',
    maturityLevel: 100,
    coreAbility: '日产1000+文案、2000+图片，AI智能润色改写',
    customers: '蒙牛、a2、快克'
  },
  {
    id: 'content_compass',
    name: '内容罗盘',
    maturity: '成熟',
    maturityLevel: 100,
    coreAbility: '一站式小红书KOS运营SaaS平台，9大功能模块',
    customers: '利星行、领克、极氪'
  },
  {
    id: 'ai_service',
    name: 'AI Service',
    maturity: '成熟',
    maturityLevel: 100,
    coreAbility: 'AIGC内容生成+智能审核+自动核销+数据归因',
    customers: '老庙、董酒'
  },
  {
    id: 'aihub',
    name: 'AiHub生图',
    maturity: 'Demo',
    maturityLevel: 60,
    coreAbility: 'AI换装生图，支持服装/场景变换',
    customers: '英氏、欧恩贝'
  },
  {
    id: 'image_group',
    name: '一键组图',
    maturity: '有接口',
    maturityLevel: 70,
    coreAbility: 'API形式快速图片合成，支持批量图片组合',
    customers: '可画'
  }
];

// 输出成果格式
export const outputFormats = [
  {
    id: 'slides',
    name: '飞书 Slides',
    description: '演示版提案PPT，支持品牌色映射',
    status: 'ready' as const,
    icon: 'Presentation'
  },
  {
    id: 'docx',
    name: '飞书 Docx',
    description: '详细版方案文档，支持多人协作',
    status: 'ready' as const,
    icon: 'FileText'
  },
  {
    id: 'pptx',
    name: 'PPTX 文件',
    description: '本地可编辑版本，方便二次修改',
    status: 'ready' as const,
    icon: 'Download'
  }
];
