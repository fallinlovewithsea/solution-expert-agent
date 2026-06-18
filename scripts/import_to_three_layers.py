"""
三层数据架构导入脚本
将飞书文件夹内容按三层架构组织：
  L1: 原始数据层 — raw_documents (JSON + SQL)
  L2: 知识层 — knowledge_relations (JSON + SQL) + Qdrant 向量数据
  L3: 记忆层 — user_preferences + session_memory (JSON + SQL)

生成 SQL 脚本可直接导入 PostgreSQL，JSON 文件可直接导入 Qdrant。
"""
import json
import hashlib
import os
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("/data/raw/feishu")
OUTPUT_DIR = Path("/workspace/data/three_layers")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── 加载知识库 ──
with open(DATA_DIR / "knowledge_summary.json") as f:
    kb = json.load(f)

with open(DATA_DIR / "document_index.json") as f:
    doc_index = json.load(f)

# ──────────────────────────────────────────────
# L1: 原始数据层
# ──────────────────────────────────────────────
print("=" * 60)
print("L1 原始数据层 — 构建中...")
print("=" * 60)

l1_documents = []
for doc in doc_index:
    doc_hash = doc["doc_hash"]
    # 生成文档内容摘要（基于文件名和元数据推断）
    content_parts = []
    content_parts.append(f"# {doc['name']}")
    content_parts.append(f"类型: {doc['type']}")
    content_parts.append(f"位置: {doc['folder']}")
    content_parts.append(f"行业: {doc['industry']}")
    content_parts.append(f"模板: {'是' if doc['is_template'] else '否'}")
    content_parts.append(f"案例: {'是' if doc['is_case'] else '否'}")
    if doc.get("brand"):
        content_parts.append(f"品牌: {doc['brand']}")
    content_parts.append(f"飞书文档ID: {doc_hash}")
    content_parts.append(f"导入时间: {datetime.now().isoformat()}")

    l1_doc = {
        "doc_name": doc["name"],
        "doc_type": doc["type"],
        "source_folder": doc["folder"],
        "feishu_token": doc_hash,
        "feishu_url": f"https://ycnm3444stv0.feishu.cn/drive/folder/EmcZfzpSul8rCcdhXvhcKpgWn7g",
        "content": "\n".join(content_parts),
        "collected_at": datetime.now().isoformat(),
        "industries": [doc["industry"]],
        "brands": [doc["brand"]] if doc.get("brand") else [],
        "is_template": doc["is_template"],
        "is_case": doc["is_case"],
    }
    l1_documents.append(l1_doc)

# 保存 L1 JSON
l1_path = OUTPUT_DIR / "l1_raw_documents.json"
l1_path.write_text(json.dumps(l1_documents, ensure_ascii=False, indent=2))
print(f"  L1 文档条目: {len(l1_documents)} 条 → {l1_path}")

# 生成 L1 SQL
l1_sql_lines = ["-- L1: 原始数据层 — raw_documents", "BEGIN;", ""]
for doc in l1_documents:
    name = doc["doc_name"].replace("'", "''")
    content = doc["content"].replace("'", "''")
    l1_sql_lines.append(
        f"INSERT INTO raw_documents (doc_name, doc_type, source_folder, feishu_token, feishu_url, content, collected_at) "
        f"VALUES ('{name}', '{doc['doc_type']}', '{doc['source_folder']}', '{doc['feishu_token']}', "
        f"'{doc['feishu_url']}', '{content[:500]}', NOW());"
    )
l1_sql_lines.append("")
l1_sql_lines.append("COMMIT;")

l1_sql_path = OUTPUT_DIR / "l1_raw_documents.sql"
l1_sql_path.write_text("\n".join(l1_sql_lines))
print(f"  L1 SQL 脚本: {l1_sql_path}")

# ──────────────────────────────────────────────
# L2: 知识层
# ──────────────────────────────────────────────
print("\n" + "=" * 60)
print("L2 知识层 — 构建中...")
print("=" * 60)

l2_knowledge = []
point_id = 0
for coll_name, items in kb["collections"].items():
    for item in items:
        point_id += 1
        source_id = hashlib.md5(item["title"].encode()).hexdigest()[:12]
        kp = {
            "id": point_id,
            "collection": coll_name,
            "source_id": source_id,
            "title": item["title"],
            "summary": item["summary"],
            "source": item.get("source", ""),
            "key_points": item.get("key_points", []),
            "tags": item.get("tags", []),
            "created_at": datetime.now().isoformat(),
        }
        l2_knowledge.append(kp)

# 保存 L2 JSON
l2_path = OUTPUT_DIR / "l2_knowledge_points.json"
l2_path.write_text(json.dumps(l2_knowledge, ensure_ascii=False, indent=2))
print(f"  L2 知识点: {len(l2_knowledge)} 条 → {l2_path}")

# 保存 L2 关联关系
l2_rel_path = OUTPUT_DIR / "l2_knowledge_relations.json"
l2_rel_path.write_text(json.dumps(kb["relations"], ensure_ascii=False, indent=2))
print(f"  L2 关联关系: {len(kb['relations'])} 条 → {l2_rel_path}")

# 生成 L2 SQL — knowledge_relations
l2_sql_lines = ["-- L2: 知识层 — knowledge_relations", "BEGIN;", ""]
for rel in kb["relations"]:
    l2_sql_lines.append(
        f"INSERT INTO knowledge_relations (source_type, source_id, target_type, target_id, relation_type, weight) "
        f"VALUES ('{rel['source_type']}', '{rel['source_id']}', '{rel['target_type']}', "
        f"'{rel['target_id']}', '{rel['relation_type']}', {rel['weight']});"
    )
l2_sql_lines.append("")
l2_sql_lines.append("COMMIT;")

l2_sql_path = OUTPUT_DIR / "l2_knowledge_relations.sql"
l2_sql_path.write_text("\n".join(l2_sql_lines))
print(f"  L2 SQL 脚本: {l2_sql_path}")

# 生成 L2 Qdrant 导入数据
qdrant_data = []
for kp in l2_knowledge:
    qdrant_data.append({
        "id": kp["id"],
        "vector": [0.0] * 1024,  # 占位向量，实际使用时需通过 embedding 模型生成
        "payload": {
            "title": kp["title"],
            "summary": kp["summary"],
            "source": kp["source"],
            "key_points": kp["key_points"],
            "tags": kp["tags"],
            "collection": kp["collection"],
        },
    })

qdrant_path = OUTPUT_DIR / "l2_qdrant_import.json"
qdrant_path.write_text(json.dumps(qdrant_data, ensure_ascii=False, indent=2))
print(f"  L2 Qdrant 导入数据: {len(qdrant_data)} 条 → {qdrant_path}")

# ──────────────────────────────────────────────
# L3: 记忆层
# ──────────────────────────────────────────────
print("\n" + "=" * 60)
print("L3 记忆层 — 构建中...")
print("=" * 60)

# 用户偏好
user_pref = {
    "user_id": "default_user",
    "preferred_industries": ["母婴", "大健康", "家居家装", "汽车"],
    "preferred_templates": ["繁星计划", "KOS矩阵全链路管理通案", "AI Service解决方案"],
    "budget_range": "50-200万",
    "output_formats": ["slides", "docx", "html"],
    "search_history": [],
    "interaction_count": 0,
    "last_active_at": datetime.now().isoformat(),
    "created_at": datetime.now().isoformat(),
    "updated_at": datetime.now().isoformat(),
}

l3_user_path = OUTPUT_DIR / "l3_user_preferences.json"
l3_user_path.write_text(json.dumps(user_pref, ensure_ascii=False, indent=2))
print(f"  L3 用户偏好: 1 条 → {l3_user_path}")

# 会话记忆（示例）
session_memories = [
    {
        "session_id": "session_example_001",
        "user_id": "default_user",
        "client_name": "飞鹤",
        "industry": "母婴",
        "stage": "方案生成",
        "key_notes": "客户关注KOS矩阵规模化和搜索占位，已使用繁星计划模板",
        "context": {
            "last_template": "繁星计划升级方案",
            "last_industry": "母婴",
            "last_brand": "飞鹤",
            "last_output": "slides",
        },
        "created_at": datetime.now().isoformat(),
    },
    {
        "session_id": "session_example_002",
        "user_id": "default_user",
        "client_name": "林氏家居",
        "industry": "家居家装",
        "stage": "需求诊断",
        "key_notes": "客户需要KOS代发代管，关注内容质量和矩阵规模",
        "context": {
            "last_template": "KOS矩阵全链路管理通案",
            "last_industry": "家居家装",
            "last_brand": "林氏家居",
            "last_output": "slides",
        },
        "created_at": datetime.now().isoformat(),
    },
]

l3_session_path = OUTPUT_DIR / "l3_session_memory.json"
l3_session_path.write_text(json.dumps(session_memories, ensure_ascii=False, indent=2))
print(f"  L3 会话记忆: {len(session_memories)} 条 → {l3_session_path}")

# 生成 L3 SQL
l3_sql_lines = ["-- L3: 记忆层", "BEGIN;", ""]
l3_sql_lines.append("-- user_preferences")
l3_sql_lines.append(
    f"INSERT INTO user_preferences (user_id, preferred_industries, preferred_templates, budget_range, output_formats) "
    f"VALUES ('default_user', '[\"母婴\",\"大健康\",\"家居家装\",\"汽车\"]', "
    f"'[\"繁星计划\",\"KOS矩阵全链路管理通案\",\"AI Service解决方案\"]', '50-200万', '[\"slides\",\"docx\",\"html\"]');"
)
l3_sql_lines.append("")
l3_sql_lines.append("-- session_memory")
for sm in session_memories:
    l3_sql_lines.append(
        f"INSERT INTO session_memory (session_id, user_id, client_name, industry, stage, key_notes, context) "
        f"VALUES ('{sm['session_id']}', '{sm['user_id']}', '{sm['client_name']}', "
        f"'{sm['industry']}', '{sm['stage']}', '{sm['key_notes']}', "
        f"'{json.dumps(sm['context'], ensure_ascii=False)}');"
    )
l3_sql_lines.append("")
l3_sql_lines.append("COMMIT;")

l3_sql_path = OUTPUT_DIR / "l3_memory.sql"
l3_sql_path.write_text("\n".join(l3_sql_lines))
print(f"  L3 SQL 脚本: {l3_sql_path}")

# ──────────────────────────────────────────────
# 汇总报告
# ──────────────────────────────────────────────
print("\n" + "=" * 60)
print("三层数据架构 — 导入完成")
print("=" * 60)

summary = {
    "L1_原始数据层": {
        "文档总数": len(l1_documents),
        "按类型": {
            "slides": sum(1 for d in l1_documents if d["doc_type"] == "slides"),
            "docx": sum(1 for d in l1_documents if d["doc_type"] == "docx"),
            "file": sum(1 for d in l1_documents if d["doc_type"] == "file"),
            "shortcut": sum(1 for d in l1_documents if d["doc_type"] == "shortcut"),
        },
        "按文件夹": {},
        "按行业": {},
        "案例数": sum(1 for d in l1_documents if d["is_case"]),
        "模板数": sum(1 for d in l1_documents if d["is_template"]),
    },
    "L2_知识层": {
        "知识点总数": len(l2_knowledge),
        "关联关系数": len(kb["relations"]),
        "按集合": {},
    },
    "L3_记忆层": {
        "用户偏好": 1,
        "会话记忆": len(session_memories),
    },
}

for d in l1_documents:
    folder = d["source_folder"]
    summary["L1_原始数据层"]["按文件夹"][folder] = summary["L1_原始数据层"]["按文件夹"].get(folder, 0) + 1
    for ind in d["industries"]:
        summary["L1_原始数据层"]["按行业"][ind] = summary["L1_原始数据层"]["按行业"].get(ind, 0) + 1

for kp in l2_knowledge:
    coll = kp["collection"]
    summary["L2_知识层"]["按集合"][coll] = summary["L2_知识层"]["按集合"].get(coll, 0) + 1

summary_path = OUTPUT_DIR / "three_layer_summary.json"
summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2))
print(f"\n汇总报告: {summary_path}")

# 打印
print(f"\n{'指标':<20} {'数量':>10}")
print("-" * 32)
print(f"{'L1 原始文档':<20} {len(l1_documents):>10}")
print(f"{'L2 知识点':<20} {len(l2_knowledge):>10}")
print(f"{'L2 关联关系':<20} {len(kb['relations']):>10}")
print(f"{'L3 用户偏好':<20} {1:>10}")
print(f"{'L3 会话记忆':<20} {len(session_memories):>10}")
print("-" * 32)
print(f"{'总计':<20} {len(l1_documents) + len(l2_knowledge) + len(kb['relations']) + 1 + len(session_memories):>10}")

print(f"\n所有数据文件已生成到: {OUTPUT_DIR}")
for f in sorted(OUTPUT_DIR.iterdir()):
    print(f"  {f.name}")