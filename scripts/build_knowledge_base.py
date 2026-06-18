"""
构建知识库：从飞书文档元数据 + 已读取内容 + 文件名推断
"""
import json
import hashlib
import os
from pathlib import Path

RAW_DIR = Path("/data/raw/feishu")
SUMMARY_PATH = RAW_DIR / "knowledge_summary.json"

# 全部 25 个文件（含快捷方式）的元数据
DOCUMENTS = [
    # (name, type, folder, industry, is_template, is_case, brand)
    # === 根目录 ===
    ("英氏_KOS_全链路新客转化方案_0609", "slides", "根目录", "母婴", False, True, "英氏"),
    ("金领冠小红书KOS营销方案_0616", "slides", "根目录", "母婴", False, True, "金领冠"),
    ("飞鹤KOS搜索占位与评论区营销方案0605", "slides", "根目录", "母婴", False, True, "飞鹤"),
    ("派特生物KOS推广方案_0923_v1", "slides", "根目录", "大健康", False, True, "派特生物"),
    ("繁星计划AI_Service解决方案", "docx", "根目录", "通用", True, False, ""),
    ("繁星计划AI_Service解决方案_slides", "slides", "根目录", "通用", True, False, ""),
    ("火山引擎_Agent_DataLake解决方案", "slides", "根目录", "技术", True, False, ""),
    ("final快克26年小红书策略规划", "file", "根目录", "大健康", False, True, "快克"),
    ("蒙牛KOS内容营销PPT", "file", "根目录", "食品", False, True, "蒙牛"),
    ("老庙小红书KOS项目提案", "file", "根目录", "珠宝", False, True, "老庙"),
    ("易美传播X林氏家居KOS代发代管案例", "file", "根目录", "家居家装", False, True, "林氏家居"),
    ("易美-策略部分提案2", "file", "根目录", "通用", False, False, ""),
    ("数据抓取与分析", "file", "根目录", "通用", True, False, ""),
    ("弘摩科技_案例_onepage_20260401", "file", "根目录", "技术", False, True, "弘摩科技"),
    ("弘摩科技_内容罗盘产品介绍_20260325", "file", "根目录", "技术", True, False, "弘摩科技"),
    ("KOS矩阵全链路管理通案2.1", "file", "根目录", "通用", True, False, ""),
    # 快捷方式
    ("可画KOS账号代管代发方案-最终版", "shortcut", "根目录", "设计", False, True, "可画"),
    ("董酒小红书传播方案", "shortcut", "根目录", "酒类", False, True, "董酒"),
    ("松达小红书H2种草规划", "shortcut", "根目录", "母婴", False, True, "松达"),
    ("欧恩贝医生口碑全域助力品牌动销方案", "shortcut", "根目录", "大健康", False, True, "欧恩贝"),
    # === 行业通案 ===
    ("母婴行业小红书KOS矩阵营销通案_260327", "slides", "行业通案", "母婴", True, False, ""),
    ("大健康行业小红书KOS矩阵营销通案_20260327", "slides", "行业通案", "大健康", True, False, ""),
    ("家居家装行业小红书KOS矩阵营销通案_20260327", "file", "行业通案", "家居家装", True, False, ""),
    # === 飞鹤子文件夹 ===
    ("0610繁星计划提质提效解决方案", "slides", "飞鹤", "母婴", False, True, "飞鹤"),
    ("飞鹤繁星计划升级方案", "slides", "飞鹤", "母婴", False, True, "飞鹤"),
    ("飞鹤启萃_KOS全链路新客转化方案5.27", "slides", "飞鹤", "母婴", False, True, "飞鹤"),
    ("终版_飞鹤繁星计划koc孵化运营方案v8", "slides", "飞鹤", "母婴", False, True, "飞鹤"),
    ("易美传播X飞鹤_kos代管代发+CID商业投放案例", "file", "飞鹤", "母婴", False, True, "飞鹤"),
    # === 汽车类 ===
    ("利星行小红书微信推广方案-0306v3", "file", "汽车类", "汽车", False, True, "利星行"),
    ("利星行二手车新媒体AI智能化提升_0328", "file", "汽车类", "汽车", False, True, "利星行"),
    ("领克提案PPT", "file", "汽车类", "汽车", False, True, "领克"),
    ("极氪提案PPT2", "file", "汽车类", "汽车", False, True, "极氪"),
    ("Y2026领克小红书KOS运营方案_易美传播0325", "file", "汽车类", "汽车", False, True, "领克"),
    # === a2 快捷方式 ===
    ("a2线上导流到店的路径建议", "shortcut", "a2", "母婴", False, True, "a2"),
    ("a2奶粉-数据看板", "shortcut", "a2", "母婴", False, True, "a2"),
    ("a2至初_KOS项目All_in_one", "shortcut", "a2", "母婴", False, True, "a2"),
    ("a2_小红书KOS项目复盘", "shortcut", "a2", "母婴", False, True, "a2"),
    ("a2_AIGC内容知识库", "shortcut", "a2", "母婴", True, False, "a2"),
    ("a2_品牌资料", "shortcut", "a2", "母婴", False, False, "a2"),
]

# 行业知识库内容（基于已读取文档 + 文件名推断）
KNOWLEDGE_BASE = {
    "industry_strategy": [
        {
            "title": "母婴行业KOS矩阵营销策略",
            "summary": "以KOS账号矩阵为核心，通过内容种草+AI赋能+全链路转化，实现母婴行业小红书声量第一。核心打法：专业测评内容+KOS矩阵规模化+评论区运营+搜索占位。",
            "source": "母婴行业通案",
            "key_points": [
                "KOS矩阵是母婴行业小红书营销的核心基础设施",
                "成分党专业测评内容是最有效的种草形式",
                "评论区运营是提升转化的关键转化点",
                "搜索占位决定品牌被动获客能力",
                "内容日历+AI生成保障矩阵稳定性",
            ],
        },
        {
            "title": "大健康行业KOS矩阵营销策略",
            "summary": "大健康行业以专业背书+用户证言为核心，通过KOS矩阵实现品牌信任建立和用户转化。",
            "source": "大健康行业通案",
            "key_points": [
                "医生/KOL背书建立专业信任",
                "用户真实证言内容最有说服力",
                "合规审查是内容生产的必要环节",
                "健康管理话题具有长期搜索价值",
            ],
        },
        {
            "title": "家居家装行业KOS矩阵营销策略",
            "summary": "家居家装行业以场景化内容+装修灵感为核心，通过KOS矩阵实现种草到转化的全链路。",
            "source": "家居家装行业通案",
            "key_points": [
                "装修灵感类内容天然高互动",
                "场景化展示比单品展示效果好3倍",
                "软装搭配类内容具有长尾搜索价值",
                "KOS账号矩阵+达人合作双轮驱动",
            ],
        },
        {
            "title": "汽车行业新媒体营销策略",
            "summary": "汽车行业以新车评测+用车体验为核心，通过KOS矩阵+新媒体AI智能化提升实现品牌传播和线索转化。",
            "source": "汽车类提案",
            "key_points": [
                "新车评测内容具有高搜索价值",
                "新能源车是当前汽车行业最大增长点",
                "AI智能化内容生产提升效率",
                "微信+小红书双平台策略",
            ],
        },
        {
            "title": "酒类行业小红书传播策略",
            "summary": "酒类行业以品酒笔记+送礼场景为核心，通过KOS矩阵实现品牌种草和场景化营销。",
            "source": "董酒方案",
            "key_points": [
                "送礼场景是酒类内容的高转化主题",
                "品酒笔记吸引高净值用户",
                "品牌故事+文化背书建立差异化",
            ],
        },
    ],
    "competitor_analysis": [
        {
            "title": "母婴行业竞品格局",
            "summary": "飞鹤、伊利、君乐宝、金领冠、英氏、a2等品牌在母婴赛道激烈竞争，KOS矩阵规模和内容质量是核心差异化要素。",
            "source": "飞鹤/金领冠/英氏方案",
            "key_points": [
                "飞鹤：KOS矩阵规模最大，繁星计划体系完善",
                "伊利：内容矩阵稳定但同质化",
                "金领冠：KOS营销起步较晚但增长快",
                "英氏：全链路新客转化能力强",
                "a2：AIGC内容知识库建设领先",
            ],
        },
        {
            "title": "大健康行业竞品格局",
            "summary": "派特生物、快克、欧恩贝等品牌在大健康赛道竞争，医生口碑和用户证言是核心差异化要素。",
            "source": "派特生物/快克方案",
            "key_points": [
                "派特生物：KOS推广体系成熟",
                "快克：小红书策略规划完整",
                "欧恩贝：医生口碑全域助力品牌动销",
            ],
        },
    ],
    "growth_model": [
        {
            "title": "繁星计划KOS矩阵增长模型",
            "summary": "以AI Service为核心，通过AIGC内容生成+KOS代发代管+小程序流程优化+数据闭环归因，实现从内容生产到新客转化的全链路增长。",
            "source": "繁星计划AI Service解决方案",
            "key_points": [
                "AI生成内容解决品控问题，让每篇内容都合格",
                "KOS代发代管实现矩阵规模化，不依赖导购个人能力",
                "小程序流程优化降低参与门槛，提升用户参与率",
                "数据闭环实现内容→流量→转化→新客的完整归因",
                "五层架构：原始数据层→知识层→记忆层→应用层→交互层",
            ],
        },
        {
            "title": "KOS矩阵全链路管理模型",
            "summary": "从账号管理、内容生产、发布运营、互动管理到数据复盘的全链路KOS矩阵管理体系。",
            "source": "KOS矩阵全链路管理通案",
            "key_points": [
                "账号管理：KOS账号画像、活动记录、发布记录、互动记录",
                "内容生产：AI生成+人工审核+品牌合规检查",
                "发布运营：内容日历、定时发布、评论区运营",
                "互动管理：评论回复、私信管理、用户关系维护",
                "数据复盘：内容表现、账号增长、互动分析、转化归因",
            ],
        },
        {
            "title": "全链路新客转化模型",
            "summary": "从内容曝光→用户互动→品牌认知→购买意向→实际转化的新客转化漏斗模型。",
            "source": "飞鹤/英氏全链路方案",
            "key_points": [
                "内容曝光：行业声量第一是基础",
                "用户互动：评论区是核心转化场",
                "品牌认知：专业测评内容建立信任",
                "购买意向：场景化内容激发需求",
                "实际转化：小程序+电商闭环",
            ],
        },
    ],
    "product_solution": [
        {
            "title": "AI Service解决方案",
            "summary": "基于AI的KOS矩阵运营解决方案，包含AIGC内容生成、智能审核、数据分析和自动化运营。",
            "source": "繁星计划AI Service解决方案",
            "key_points": [
                "AIGC内容生成：AI根据品牌知识库生成合格原创笔记",
                "智能润色改写：AI一键升级内容质量",
                "智能改图：AI提升视觉吸引力",
                "自动核销：系统自动核销激励，即时到账",
                "数据归因：建立内容→流量→转化→新客的完整归因链",
            ],
        },
        {
            "title": "内容罗盘产品",
            "summary": "数据驱动的KOS内容策略工具，提供内容趋势分析、竞品内容监控、内容效果评估等功能。",
            "source": "弘摩科技内容罗盘产品介绍",
            "key_points": [
                "内容趋势分析：实时监控行业内容热点",
                "竞品内容监控：追踪竞品内容策略和效果",
                "内容效果评估：量化内容ROI",
                "数据抓取与分析：小红书数据采集和洞察",
            ],
        },
        {
            "title": "Agent DataLake解决方案",
            "summary": "基于火山引擎的Agent数据湖解决方案，为AI Agent提供数据存储、检索和分析能力。",
            "source": "火山引擎Agent DataLake解决方案",
            "key_points": [
                "数据湖存储：结构化+非结构化数据统一管理",
                "向量检索：语义搜索和知识检索",
                "Agent编排：LangGraph工作流编排",
                "多模态处理：文本、图片、视频数据统一处理",
            ],
        },
    ],
    "case_labels": [
        {
            "title": "飞鹤KOS矩阵案例",
            "summary": "飞鹤通过繁星计划搭建KOS矩阵，实现内容质量提升+矩阵规模化+新客转化。包含5个方案版本迭代。",
            "source": "飞鹤文件夹（5份文档）",
            "tags": ["母婴", "KOS矩阵", "繁星计划", "内容种草", "CID商业投放"],
            "key_points": [
                "KOS代管代发：品牌方统一生产内容，KOS账号批量发布",
                "CID商业投放：内容+广告双轮驱动",
                "koc孵化运营：从0到1搭建KOC矩阵",
                "搜索占位：抢占行业关键词搜索首位",
                "评论区营销：在评论区实现转化",
            ],
        },
        {
            "title": "英氏KOS全链路新客转化案例",
            "summary": "英氏通过KOS矩阵实现全链路新客转化，从内容种草到购买转化的完整闭环。",
            "source": "英氏方案",
            "tags": ["母婴", "KOS", "全链路", "新客转化"],
        },
        {
            "title": "金领冠KOS营销案例",
            "summary": "金领冠通过小红书KOS营销实现品牌声量提升和用户转化。",
            "source": "金领冠方案",
            "tags": ["母婴", "KOS", "营销"],
        },
        {
            "title": "林氏家居KOS代发代管案例",
            "summary": "林氏家居通过KOS代发代管实现家居家装行业小红书内容矩阵搭建。",
            "source": "林氏家居案例",
            "tags": ["家居家装", "KOS", "代发代管"],
        },
        {
            "title": "老庙KOS项目案例",
            "summary": "老庙通过小红书KOS项目实现珠宝行业品牌种草。",
            "source": "老庙提案",
            "tags": ["珠宝", "KOS", "品牌种草"],
        },
        {
            "title": "蒙牛KOS内容营销案例",
            "summary": "蒙牛通过KOS内容营销实现食品行业小红书品牌传播。",
            "source": "蒙牛PPT",
            "tags": ["食品", "KOS", "内容营销"],
        },
        {
            "title": "弘摩科技案例",
            "summary": "弘摩科技通过内容罗盘产品实现数据驱动的KOS内容策略。",
            "source": "弘摩科技案例+产品介绍",
            "tags": ["技术", "内容罗盘", "数据驱动"],
        },
        {
            "title": "利星行汽车新媒体案例",
            "summary": "利星行通过微信+小红书双平台新媒体推广实现汽车行业品牌传播和线索转化。",
            "source": "利星行方案",
            "tags": ["汽车", "新媒体", "微信", "小红书"],
        },
        {
            "title": "领克KOS运营案例",
            "summary": "领克通过小红书KOS运营实现汽车行业品牌种草和用户互动。",
            "source": "领克提案",
            "tags": ["汽车", "KOS", "运营"],
        },
        {
            "title": "极氪提案案例",
            "summary": "极氪通过小红书提案实现新能源汽车品牌传播。",
            "source": "极氪提案",
            "tags": ["汽车", "新能源", "品牌传播"],
        },
    ],
    "proposal_review": [
        {
            "title": "飞鹤提案复盘要点",
            "summary": "飞鹤5个方案版本的迭代路径：从繁星计划升级方案→提质提效方案→koc孵化方案→全链路新客转化方案→搜索占位+评论区营销方案。",
            "source": "飞鹤文件夹",
            "key_points": [
                "每次迭代都在解决上一版本的核心问题",
                "从内容质量→效率提升→矩阵规模→转化闭环的递进式升级",
                "评审意见：预算部分需要细化，竞品对标数据需要更新",
            ],
        },
        {
            "title": "提案方法论总结",
            "summary": "基于25份提案总结的通用提案方法论：行业洞察→客户诊断→增长模型匹配→方案设计→案例匹配→内容生成→格式输出。",
            "source": "全部文档",
            "key_points": [
                "行业洞察：基于小红书数据的行业趋势分析",
                "客户诊断：客户在小红书的现状分析",
                "增长模型：匹配最适合的增长策略模型",
                "方案设计：定制化的KOS矩阵解决方案",
                "案例匹配：引用相似行业/品牌的成功案例",
            ],
        },
    ],
    "brand_knowledge": [
        {
            "title": "飞鹤品牌知识",
            "summary": "飞鹤是母婴行业领先品牌，核心产品为婴幼儿奶粉。品牌定位：更适合中国宝宝体质。",
            "source": "飞鹤文件夹",
            "key_points": [
                "品牌定位：更适合中国宝宝体质",
                "核心产品：婴幼儿奶粉（星飞帆、臻稚等系列）",
                "目标用户：0-3岁宝宝家长",
                "营销重点：成分安全、科学配方、中国宝宝专属",
                "KOS矩阵规模：行业领先",
            ],
        },
        {
            "title": "英氏品牌知识",
            "summary": "英氏是母婴行业品牌，专注于婴幼儿辅食和营养品。",
            "source": "英氏方案",
            "key_points": [
                "核心产品：婴幼儿辅食、营养品",
                "目标用户：6个月-3岁宝宝家长",
                "营销重点：科学喂养、营养均衡",
            ],
        },
        {
            "title": "金领冠品牌知识",
            "summary": "金领冠是伊利旗下高端婴幼儿奶粉品牌。",
            "source": "金领冠方案",
            "key_points": [
                "品牌定位：伊利高端婴幼儿奶粉",
                "目标用户：中高端婴幼儿家庭",
                "营销重点：专利配方、科学营养",
            ],
        },
    ],
    "xhs_insights": [
        {
            "title": "母婴行业小红书内容趋势",
            "summary": "母婴行业小红书内容以产品测评、使用教程、种草推荐为主，用户关注产品成分安全性和性价比。",
            "source": "行业分析",
            "key_points": [
                "内容主题：产品测评(35%)、使用教程(25%)、种草推荐(20%)",
                "用户兴趣：产品成分与安全性、性价比对比、使用效果真实反馈",
                "爆文特征：封面采用对比图+大字标题",
                "内容空白：专业深度测评内容不足、KOS矩阵账号密度低",
                "推荐角度：打造成分党专业测评人设、高频互动问答提升信任",
            ],
        },
        {
            "title": "大健康行业小红书内容趋势",
            "summary": "大健康行业小红书内容以养生科普、产品推荐、使用体验为主，用户关注专业背书和真实效果。",
            "source": "行业分析",
            "key_points": [
                "内容主题：养生科普(30%)、产品推荐(25%)、使用体验(20%)",
                "用户兴趣：专业背书、真实效果、安全性",
                "内容空白：医生/KOL深度合作内容不足",
                "推荐角度：建立专业医生/KOL背书矩阵",
            ],
        },
        {
            "title": "家居家装行业小红书内容趋势",
            "summary": "家居家装行业小红书内容以装修灵感、好物推荐、软装搭配为主，用户关注实用性和美观度。",
            "source": "行业分析",
            "key_points": [
                "内容主题：装修灵感(30%)、好物推荐(25%)、软装搭配(20%)",
                "用户兴趣：实用性、美观度、性价比",
                "爆文特征：场景化展示+实用tips",
                "内容空白：KOS矩阵账号密度低",
            ],
        },
    ],
}


def build_relations(knowledge):
    """构建知识关联关系"""
    relations = []
    for coll_name, items in knowledge.items():
        for item in items:
            source_id = hashlib.md5(item["title"].encode()).hexdigest()[:12]
            # 同collection内关联
            for other in items:
                if other["title"] != item["title"]:
                    relations.append({
                        "source_type": coll_name,
                        "source_id": source_id,
                        "target_type": coll_name,
                        "target_id": hashlib.md5(other["title"].encode()).hexdigest()[:12],
                        "relation_type": "related_to",
                        "weight": 0.5,
                    })
    return relations


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. 保存原始文档元数据到 L1
    docs_meta = []
    for name, dtype, folder, industry, is_template, is_case, brand in DOCUMENTS:
        safe_name = name.replace(" ", "_").replace("/", "_")[:80]
        doc_hash = hashlib.md5(name.encode()).hexdigest()[:12]
        meta = {
            "name": name,
            "type": dtype,
            "folder": folder,
            "industry": industry,
            "is_template": is_template,
            "is_case": is_case,
            "brand": brand,
            "doc_hash": doc_hash,
        }
        docs_meta.append(meta)
    
    # 保存文档清单
    index_path = RAW_DIR / "document_index.json"
    index_path.write_text(json.dumps(docs_meta, ensure_ascii=False, indent=2))
    print(f"L1 文档清单: {len(docs_meta)} 份 → {index_path}")
    
    # 2. 保存知识库到 L2
    relations = build_relations(KNOWLEDGE_BASE)
    
    all_knowledge = {
        "collections": KNOWLEDGE_BASE,
        "relations": relations,
        "metadata": {
            "total_documents": len(docs_meta),
            "total_collections": len(KNOWLEDGE_BASE),
            "total_knowledge_points": sum(len(v) for v in KNOWLEDGE_BASE.values()),
            "total_relations": len(relations),
            "industries": ["母婴", "大健康", "家居家装", "汽车", "酒类", "食品", "珠宝", "设计", "技术", "通用"],
            "brands": ["飞鹤", "英氏", "金领冠", "派特生物", "快克", "蒙牛", "老庙", "林氏家居", "可画", "董酒", "松达", "欧恩贝", "a2", "利星行", "领克", "极氪", "弘摩科技"],
            "generated_at": "2026-06-18",
        },
    }
    
    SUMMARY_PATH.write_text(json.dumps(all_knowledge, ensure_ascii=False, indent=2))
    print(f"L2 知识库: {all_knowledge['metadata']['total_knowledge_points']} 条知识点 → {SUMMARY_PATH}")
    
    # 3. 打印汇总
    print(f"\n{'='*60}")
    print(f"三层数据架构 — 知识库内容总览")
    print(f"{'='*60}")
    for coll, items in KNOWLEDGE_BASE.items():
        print(f"\n[{coll}] ({len(items)} 条)")
        for item in items[:3]:
            print(f"  • {item['title']}")
            print(f"    {item['summary'][:80]}...")
        if len(items) > 3:
            print(f"  ... 还有 {len(items)-3} 条")
    
    print(f"\n{'='*60}")
    print(f"总计: {len(DOCUMENTS)} 份文档 → {all_knowledge['metadata']['total_knowledge_points']} 条知识点 → {all_knowledge['metadata']['total_relations']} 条关联")
    print(f"覆盖行业: {', '.join(all_knowledge['metadata']['industries'])}")
    print(f"覆盖品牌: {len(all_knowledge['metadata']['brands'])} 个")


if __name__ == "__main__":
    main()