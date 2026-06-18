"""
将销售支持知识库及其嵌入文档的内容映射到三层数据架构
来源: https://ycnm3444stv0.feishu.cn/docx/NeqkdQj7loHgTmx8fEHcnWlDncq
包含嵌入文档: 弘摩资质合集、内容罗盘使用手册、内容罗盘演示空间操作文档
"""
import json
import hashlib
import os
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("/data/raw/feishu")
OUTPUT_DIR = Path("/workspace/Database")

# ── 加载现有数据 ──
with open(DATA_DIR / "document_index.json") as f:
    doc_index = json.load(f)

with open(DATA_DIR / "knowledge_summary.json") as f:
    kb = json.load(f)

# ──────────────────────────────────────────────
# L1: 新增原始文档
# ──────────────────────────────────────────────
print("=" * 60)
print("L1 原始数据层 — 新增文档")
print("=" * 60)

new_docs = [
    {
        "doc_name": "销售支持知识库",
        "doc_type": "docx",
        "source_folder": "根目录",
        "feishu_token": "NeqkdQj7loHgTmx8fEHcnWlDncq",
        "feishu_url": "https://ycnm3444stv0.feishu.cn/docx/NeqkdQj7loHgTmx8fEHcnWlDncq",
        "industry": "通用",
        "brand": "",
        "is_template": False,
        "is_case": False,
        "content": "销售支持知识库 - 对外资料索引 + 商务流程，含6大产品线介绍、标准报价、合同、最佳实践案例、LOGO素材",
    },
    {
        "doc_name": "弘摩资质合集",
        "doc_type": "docx",
        "source_folder": "销售支持/嵌入文档",
        "feishu_token": "PdZQdUJe4op61nxSb7ZcKDovnef",
        "feishu_url": "https://ycnm3444stv0.feishu.cn/wiki/Ywi1wj0EkiBGuLko1tucJ6UTnGb",
        "industry": "通用",
        "brand": "弘摩科技",
        "is_template": False,
        "is_case": False,
        "content": "弘摩科技资质文档合集，含公司介绍、商标注册、软件著作权、ISO认证等资质材料",
    },
    {
        "doc_name": "【内容罗盘】使用手册v2",
        "doc_type": "docx",
        "source_folder": "销售支持/嵌入文档",
        "feishu_token": "UhVkd8lFRokGO6xyEatcV8AGn6g",
        "feishu_url": "https://ycnm3444stv0.feishu.cn/wiki/EiULwWeEoiTaf8kgWAucEzCbnkf",
        "industry": "通用",
        "brand": "",
        "is_template": True,
        "is_case": False,
        "content": "内容罗盘产品完整操作手册，涵盖设备管理、账号管理、养号任务、笔记发布、互动任务、评论任务、校验任务、评论截图工具、数据统计等模块的详细操作说明",
    },
    {
        "doc_name": "内容罗盘演示空间操作文档（销售侧）",
        "doc_type": "docx",
        "source_folder": "销售支持/嵌入文档",
        "feishu_token": "Zv3cdKQ7XoVksFx8eXQcP413nfh",
        "feishu_url": "https://ycnm3444stv0.feishu.cn/docx/Zv3cdKQ7XoVksFx8eXQcP413nfh",
        "industry": "通用",
        "brand": "",
        "is_template": True,
        "is_case": False,
        "content": "内容罗盘销售演示流程：演示空间说明(后台地址/手机设备/账号)、6步演示流程(设备管理→账号管理→养号→笔记发布→互动→数据统计)、试用申请流程、常见问题",
    },
]

# 更新 document_index
for doc in new_docs:
    doc["doc_hash"] = doc["feishu_token"]
    # 避免重复
    if not any(d.get("doc_hash") == doc["doc_hash"] for d in doc_index):
        doc_index.append(doc)
        print(f"  + L1 新增文档: {doc['doc_name']}")

# 保存
with open(DATA_DIR / "document_index.json", "w") as f:
    json.dump(doc_index, f, ensure_ascii=False, indent=2)

# ──────────────────────────────────────────────
# L2: 更新知识层
# ──────────────────────────────────────────────
print("\n" + "=" * 60)
print("L2 知识层 — 新增知识点")
print("=" * 60)

# 新增产品方案知识
new_product_knowledge = []

# 内容罗盘详细功能
new_product_knowledge.append({
    "title": "内容罗盘产品功能全景",
    "summary": "内容罗盘是一站式小红书KOS运营SaaS平台，涵盖设备管理、账号管理、养号、笔记发布、互动、评论、校验、数据统计等完整功能模块，支持手机端自动化执行",
    "source": "销售支持知识库/内容罗盘使用手册",
    "key_points": [
        "设备管理：手机设备在线状态监控、启用/禁用、分组管理",
        "账号管理：KOS账号集中录入、绑定设备、批量导入",
        "养号任务：自动模拟真实用户行为，养号提升账号权重",
        "笔记发布：一次配置多账号同时发布，自动返回发布链接",
        "互动任务：自动评论、点赞、收藏、关注，批量执行",
        "评论任务：自评+第三方评论，定时发布，支持结果导出",
        "校验任务：验证评论外显状态，自动截图留存",
        "评论截图工具：PC端工具，利用第三方账号校验评论外显",
        "数据统计：全流程可追溯、可量化，支持Excel/CSV导出",
    ],
    "tags": ["内容罗盘", "SaaS", "KOS运营", "自动化", "产品功能"],
})

# AiHub生图
new_product_knowledge.append({
    "title": "AiHub生图产品能力",
    "summary": "AiHub提供AI换装生图能力，支持服装/场景变换，有独立操作方法和生图账号体系",
    "source": "销售支持知识库",
    "key_points": [
        "AI换装功能：支持服装/场景变换",
        "独立生图账号体系",
        "有Demo演示能力",
        "标准合同WIP",
    ],
    "tags": ["AiHub", "AI生图", "换装", "产品"],
})

# 一键组图
new_product_knowledge.append({
    "title": "一键组图产品能力",
    "summary": "一键组图提供快速图片合成接口，支持批量图片组合生成",
    "source": "销售支持知识库",
    "key_points": [
        "API接口形式提供",
        "支持批量图片组合",
        "快速生成能力",
    ],
    "tags": ["一键组图", "图片合成", "API", "产品"],
})

# 商务流程知识
new_business_knowledge = []

new_business_knowledge.append({
    "title": "标准商务流程",
    "summary": "销售支持知识库定义了完整的商务流程：演示→试用申请→报价→合同→交付，涵盖KOS/AIGC/内容罗盘/AiHub四条产品线",
    "source": "销售支持知识库",
    "key_points": [
        "演示流程：内容罗盘6步演示(设备管理→账号管理→养号→笔记发布→互动→数据统计)，每模块2-3分钟",
        "演示空间：https://content-compass.cn，固定3台手机+3个演示账号",
        "试用申请：客户自行提供小红书账号，填写项目与人员申请表，1-2天部署",
        "报价体系：标准报价模板(Wiki) + 市场用刊例(PPTX)",
        "合同体系：KOS合同(弘摩/易美双版本)、AIGC合同(弘摩/易美双版本)、内容罗盘合同(WIP)、AiHub合同(WIP)",
        "双品牌主体：弘摩科技(技术侧) 和 易美传播(营销侧)，外发前需确认版本",
        "技术对接人：王美齐",
    ],
    "tags": ["商务流程", "演示", "试用", "报价", "合同", "双品牌"],
})

new_business_knowledge.append({
    "title": "最佳实践案例库",
    "summary": "销售对外展示的最佳实践案例涵盖One page合集(快克/伊利/领秀军事展)、飞鹤、林氏家居、Hellosunny、松达等5大案例",
    "source": "销售支持知识库",
    "key_points": [
        "One page合集：含快克(大健康)、伊利、领秀军事展(线下碰一碰)案例",
        "飞鹤奶粉：弘摩版本，初次沟通不建议直接发",
        "林氏家居：弘摩版本，家居行业KOS矩阵标杆",
        "Hellosunny：易美版本，母婴行业案例",
        "松达(莱萃诺)：大健康行业案例",
        "所有案例版本日期20260324，外发前确认当前状态",
    ],
    "tags": ["最佳实践", "案例", "飞鹤", "林氏家居", "松达", "快克", "伊利"],
})

# 更新知识库
for item in new_product_knowledge:
    kb["collections"]["product_solution"].append(item)
    print(f"  + L2 product_solution: {item['title']}")

for item in new_business_knowledge:
    # 新增商务流程集合
    if "business_process" not in kb["collections"]:
        kb["collections"]["business_process"] = []
    kb["collections"]["business_process"].append(item)
    print(f"  + L2 business_process: {item['title']}")

# 新增关联关系
new_relations = [
    {"source_type": "product_solution", "source_id": "内容罗盘", "target_type": "business_process", "target_id": "标准商务流程", "relation_type": "supported_by", "weight": 0.9},
    {"source_type": "product_solution", "source_id": "内容罗盘", "target_type": "doc", "target_id": "内容罗盘使用手册", "relation_type": "documented_in", "weight": 1.0},
    {"source_type": "product_solution", "source_id": "内容罗盘", "target_type": "doc", "target_id": "内容罗盘演示空间操作文档", "relation_type": "demo_guide", "weight": 1.0},
    {"source_type": "business_process", "source_id": "标准商务流程", "target_type": "doc", "target_id": "弘摩资质合集", "relation_type": "documents", "weight": 0.8},
    {"source_type": "business_process", "source_id": "最佳实践案例库", "target_type": "case_labels", "target_id": "飞鹤", "relation_type": "exemplifies", "weight": 0.9},
    {"source_type": "business_process", "source_id": "最佳实践案例库", "target_type": "case_labels", "target_id": "林氏家居", "relation_type": "exemplifies", "weight": 0.9},
    {"source_type": "product_solution", "source_id": "AiHub生图", "target_type": "product_solution", "target_id": "AI Service解决方案", "relation_type": "complements", "weight": 0.7},
    {"source_type": "product_solution", "source_id": "一键组图", "target_type": "product_solution", "target_id": "AI Service解决方案", "relation_type": "complements", "weight": 0.6},
]

for rel in new_relations:
    if rel not in kb["relations"]:
        kb["relations"].append(rel)
        print(f"  + L2 relation: {rel['source_id']} → {rel['target_id']}")

# 保存知识库
with open(DATA_DIR / "knowledge_summary.json", "w") as f:
    json.dump(kb, f, ensure_ascii=False, indent=2)

# ──────────────────────────────────────────────
# 汇总统计
# ──────────────────────────────────────────────
print("\n" + "=" * 60)
print("三层数据更新完成")
print("=" * 60)

l1_count = len(doc_index)
l2_collections = {k: len(v) for k, v in kb["collections"].items()}
l2_total = sum(l2_collections.values())
l2_rel = len(kb["relations"])

print(f"L1 原始文档: {l1_count} 份 (新增 {len(new_docs)} 份)")
print(f"L2 知识点: {l2_total} 条 (新增 {len(new_product_knowledge) + len(new_business_knowledge)} 条)")
print(f"L2 关联关系: {l2_rel} 条 (新增 {len(new_relations)} 条)")
print(f"\nL2 集合分布:")
for name, count in l2_collections.items():
    print(f"  {name}: {count} 条")