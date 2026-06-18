"""
知识蒸馏模块：将原始文档/采集数据 → LLM 提取 → 向量化 → 存入 Qdrant + PG
"""
import json
import os
import hashlib
from typing import Dict, List, Optional
from datetime import datetime


class KnowledgeDistiller:
    """从原始数据中蒸馏结构化知识"""

    def __init__(self, vector_store=None, db=None):
        self.vector_store = vector_store
        self.db = db

    def distill_document(self, doc: Dict) -> Dict:
        """
        从飞书文档中蒸馏知识
        输入: {"name": "飞鹤繁星计划方案", "type": "slides", "content": "..."}
        输出: {"collections": {collection_name: [point_ids]}, "relations": [relations]}
        """
        result = {"collections": {}, "relations": []}

        name = doc.get("name", "")
        content = doc.get("content", "")
        doc_id = hashlib.md5(name.encode()).hexdigest()[:16]

        # 用 LLM 提取知识点
        knowledge = self._extract_with_llm(name, content)

        # 存入对应 Qdrant collection
        for collection_name, items in knowledge.get("collections", {}).items():
            if not items:
                continue
            points = self._build_points(doc_id, collection_name, items)
            if points and self.vector_store:
                self.vector_store.upsert(collection_name, points)
                result["collections"][collection_name] = [p.id for p in points]

        # 写入知识关联关系
        for rel in knowledge.get("relations", []):
            if self.db:
                self._save_relation(rel)
            result["relations"].append(rel)

        return result

    def distill_xhs_data(self, data: Dict) -> Dict:
        """
        从小红书采集数据中蒸馏洞察
        输入: {"collect_type": "industry", "target_name": "母婴", "analysis": {...}}
        输出: {"point_ids": [...]}
        """
        analysis = data.get("analysis", {})
        if not analysis:
            return {"point_ids": []}

        target_name = data.get("target_name", "unknown")
        doc_id = hashlib.md5(f"xhs_{target_name}".encode()).hexdigest()[:16]

        # 将分析结果转为可检索的文本
        text_parts = []
        if analysis.get("content_themes"):
            themes = ", ".join(
                t.get("theme", "") if isinstance(t, dict) else str(t)
                for t in analysis["content_themes"]
            )
            text_parts.append(f"内容主题: {themes}")
        if analysis.get("audience_interest"):
            text_parts.append(f"受众兴趣: {', '.join(analysis['audience_interest'])}")
        if analysis.get("hot_elements"):
            text_parts.append(f"爆文特征: {analysis['hot_elements']}")
        if analysis.get("content_gap"):
            text_parts.append(f"内容空白: {', '.join(analysis['content_gap'])}")
        if analysis.get("recommended_angles"):
            text_parts.append(f"推荐角度: {', '.join(analysis['recommended_angles'])}")

        full_text = "\n".join(text_parts)
        if not full_text.strip():
            return {"point_ids": []}

        # 生成简单的文本哈希作为向量（生产环境用 embedding 模型）
        import numpy as np
        seed = int(hashlib.md5(full_text.encode()).hexdigest()[:8], 16) % (2**31)
        np.random.seed(seed)
        vector = np.random.randn(1024).tolist()
        vector = (vector / np.linalg.norm(vector)).tolist()

        from qdrant_client.models import PointStruct
        point = PointStruct(
            id=doc_id,
            vector=vector,
            payload={
                "target_name": target_name,
                "collect_type": data.get("collect_type", ""),
                "text": full_text[:2000],
                "analysis": analysis,
                "collected_at": data.get("collected_at", ""),
            },
        )

        if self.vector_store:
            self.vector_store.upsert("xhs_insights", [point])

        return {"point_ids": [doc_id]}

    def _extract_with_llm(self, name: str, content: str) -> Dict:
        """使用 LLM 从文档中提取分类知识"""
        from app.llm.router import get_llm

        prompt = f"""你是一个知识提取专家。请分析以下文档内容，提取结构化知识。

文档名称: {name}
文档内容（前 3000 字）:
{content[:3000]}

请输出 JSON，包含以下字段:
1. "collections": 一个字典，key 是 collection 名称，value 是知识点列表。
   - 可用 collection: industry_strategy, competitor_analysis, growth_model, product_solution, case_labels, proposal_review, brand_knowledge
   - 每个知识点是一个字典，包含 "title"(标题) 和 "summary"(一句话摘要)
2. "relations": 知识关联列表，每项包含 source_type, source_id, target_type, target_id, relation_type
   - relation_type 可选: belongs_to, applied_in, similar_to, competes_with

只输出 JSON，不要其他内容。"""

        try:
            llm = get_llm("heavy")
            response = llm.invoke(prompt)
            return json.loads(response.content)
        except Exception:
            return {"collections": {}, "relations": []}

    def _build_points(self, doc_id: str, collection_name: str, items: List[Dict]) -> List:
        """构建 Qdrant PointStruct 列表"""
        import numpy as np
        from qdrant_client.models import PointStruct

        points = []
        for i, item in enumerate(items):
            title = item.get("title", "") if isinstance(item, dict) else str(item)
            summary = item.get("summary", "") if isinstance(item, dict) else ""

            text = f"{title}\n{summary}"
            seed = int(hashlib.md5(text.encode()).hexdigest()[:8], 16) % (2**31)
            np.random.seed(seed)
            vector = np.random.randn(1024).tolist()
            vector = (vector / np.linalg.norm(vector)).tolist()

            points.append(PointStruct(
                id=f"{doc_id}_{i}",
                vector=vector,
                payload={
                    "title": title,
                    "summary": summary,
                    "collection": collection_name,
                    "source_doc": doc_id,
                },
            ))
        return points

    def _save_relation(self, rel: Dict):
        """保存知识关联关系到 PostgreSQL"""
        try:
            conn = self.db
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO knowledge_relations
                   (source_type, source_id, target_type, target_id, relation_type, weight)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (
                    rel.get("source_type", ""),
                    rel.get("source_id", ""),
                    rel.get("target_type", ""),
                    rel.get("target_id", ""),
                    rel.get("relation_type", ""),
                    rel.get("weight", 1.0),
                ),
            )
            conn.commit()
        except Exception:
            pass