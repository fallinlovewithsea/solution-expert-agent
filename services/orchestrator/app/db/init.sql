-- 品牌信息表
CREATE TABLE IF NOT EXISTS brand_info (
    id SERIAL PRIMARY KEY,
    brand_name VARCHAR(200) NOT NULL UNIQUE,
    industry VARCHAR(100) NOT NULL,
    sub_category VARCHAR(200),
    contact_history JSONB DEFAULT '[]',
    current_status TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 案例标签表
CREATE TABLE IF NOT EXISTS case_labels (
    id SERIAL PRIMARY KEY,
    case_name VARCHAR(300) NOT NULL,
    industry VARCHAR(100) NOT NULL,
    scene VARCHAR(100) NOT NULL,
    playbook VARCHAR(100) NOT NULL,
    customer_feedback TEXT,
    key_metrics JSONB DEFAULT '{}',
    source_url VARCHAR(500),
    relevance_score FLOAT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 提案记录表
CREATE TABLE IF NOT EXISTS proposal_records (
    id SERIAL PRIMARY KEY,
    client_name VARCHAR(200) NOT NULL,
    industry VARCHAR(100) NOT NULL,
    project_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'draft',
    slides_url VARCHAR(500),
    docx_url VARCHAR(500),
    bid_result VARCHAR(50),
    review_notes JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 复盘记录表
CREATE TABLE IF NOT EXISTS review_records (
    id SERIAL PRIMARY KEY,
    proposal_id INTEGER REFERENCES proposal_records(id),
    success_factors JSONB DEFAULT '[]',
    lessons_learned JSONB DEFAULT '[]',
    improvements JSONB DEFAULT '[]',
    extracted_data JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_brand_industry ON brand_info(industry);
CREATE INDEX IF NOT EXISTS idx_case_industry ON case_labels(industry);
CREATE INDEX IF NOT EXISTS idx_case_scene ON case_labels(scene);
CREATE INDEX IF NOT EXISTS idx_proposal_client ON proposal_records(client_name);
CREATE INDEX IF NOT EXISTS idx_proposal_status ON proposal_records(status);

-- ============================================
-- 三层数据架构：新增表
-- ============================================

-- L1: 飞书文档原文
CREATE TABLE IF NOT EXISTS raw_documents (
    id SERIAL PRIMARY KEY,
    doc_name VARCHAR(500) NOT NULL,
    doc_type VARCHAR(50) NOT NULL,
    source_folder VARCHAR(300),
    feishu_token VARCHAR(200),
    feishu_url VARCHAR(500),
    content TEXT NOT NULL,
    collected_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_raw_docs_type ON raw_documents(doc_type);
CREATE INDEX IF NOT EXISTS idx_raw_docs_folder ON raw_documents(source_folder);

-- L1: 小红书采集数据
CREATE TABLE IF NOT EXISTS raw_xhs_data (
    id SERIAL PRIMARY KEY,
    collect_type VARCHAR(50) NOT NULL,
    target_name VARCHAR(200) NOT NULL,
    keywords JSONB DEFAULT '[]',
    notes JSONB DEFAULT '[]',
    comments JSONB DEFAULT '[]',
    analysis JSONB DEFAULT '{}',
    collected_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_xhs_type ON raw_xhs_data(collect_type);
CREATE INDEX IF NOT EXISTS idx_xhs_target ON raw_xhs_data(target_name);
CREATE INDEX IF NOT EXISTS idx_xhs_collected ON raw_xhs_data(collected_at);

-- L2: 知识关联关系
CREATE TABLE IF NOT EXISTS knowledge_relations (
    id SERIAL PRIMARY KEY,
    source_type VARCHAR(50) NOT NULL,
    source_id VARCHAR(200) NOT NULL,
    target_type VARCHAR(50) NOT NULL,
    target_id VARCHAR(200) NOT NULL,
    relation_type VARCHAR(100) NOT NULL,
    weight FLOAT DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_kr_source ON knowledge_relations(source_type, source_id);
CREATE INDEX IF NOT EXISTS idx_kr_target ON knowledge_relations(target_type, target_id);

-- L3: 用户使用习惯
CREATE TABLE IF NOT EXISTS user_preferences (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    preferred_industries JSONB DEFAULT '[]',
    preferred_templates JSONB DEFAULT '[]',
    budget_range VARCHAR(100),
    output_formats JSONB DEFAULT '[]',
    search_history JSONB DEFAULT '[]',
    interaction_count INTEGER DEFAULT 0,
    last_active_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_up_user ON user_preferences(user_id);

-- L3: 客户操作历史
CREATE TABLE IF NOT EXISTS session_memory (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    user_id VARCHAR(100) NOT NULL,
    client_name VARCHAR(200) NOT NULL,
    industry VARCHAR(100),
    stage VARCHAR(50),
    proposal_id INTEGER REFERENCES proposal_records(id),
    review_feedback TEXT,
    bid_result VARCHAR(50),
    key_notes TEXT,
    context JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sm_session ON session_memory(session_id);
CREATE INDEX IF NOT EXISTS idx_sm_client ON session_memory(client_name);
CREATE INDEX IF NOT EXISTS idx_sm_user ON session_memory(user_id);

-- 焦虑映射表（销售提案心理学模型）
CREATE TABLE IF NOT EXISTS anxiety_mapping (
    id SERIAL PRIMARY KEY,
    client_name VARCHAR(200) NOT NULL,
    industry VARCHAR(100),
    fear_analysis JSONB DEFAULT '{}',
    bid_result VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_anxiety_client ON anxiety_mapping(client_name);
CREATE INDEX IF NOT EXISTS idx_anxiety_industry ON anxiety_mapping(industry);