-- L3: 记忆层
BEGIN;

-- user_preferences
INSERT INTO user_preferences (user_id, preferred_industries, preferred_templates, budget_range, output_formats) VALUES ('default_user', '["母婴","大健康","家居家装","汽车"]', '["繁星计划","KOS矩阵全链路管理通案","AI Service解决方案"]', '50-200万', '["slides","docx","html"]');

-- session_memory
INSERT INTO session_memory (session_id, user_id, client_name, industry, stage, key_notes, context) VALUES ('session_example_001', 'default_user', '飞鹤', '母婴', '方案生成', '客户关注KOS矩阵规模化和搜索占位，已使用繁星计划模板', '{"last_template": "繁星计划升级方案", "last_industry": "母婴", "last_brand": "飞鹤", "last_output": "slides"}');
INSERT INTO session_memory (session_id, user_id, client_name, industry, stage, key_notes, context) VALUES ('session_example_002', 'default_user', '林氏家居', '家居家装', '需求诊断', '客户需要KOS代发代管，关注内容质量和矩阵规模', '{"last_template": "KOS矩阵全链路管理通案", "last_industry": "家居家装", "last_brand": "林氏家居", "last_output": "slides"}');

COMMIT;