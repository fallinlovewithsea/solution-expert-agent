import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict, Optional


class VectorStore:
    """封装 Qdrant 向量数据库，管理 8 大物料库的向量索引"""

    COLLECTIONS = {
        "industry_strategy": 1024,
        "competitor_analysis": 1024,
        "growth_model": 1024,
        "product_solution": 1024,
        "case_labels": 1024,
        "proposal_review": 1024,
        "brand_knowledge": 1024,
        "xhs_insights": 1024,
        "behavioral_economics": 1024,   # 新增：行为经济学与心理学
    }

    def __init__(self):
        self.client = QdrantClient(
            host=os.getenv("QDRANT_HOST", "qdrant"),
            port=int(os.getenv("QDRANT_PORT", "6333")),
        )
        self._init_collections()

    def _init_collections(self):
        existing = {c.name for c in self.client.get_collections().collections}
        for name, dim in self.COLLECTIONS.items():
            if name not in existing:
                self.client.create_collection(
                    collection_name=name,
                    vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
                )

    def upsert(self, collection: str, points: List[PointStruct]):
        self.client.upsert(collection_name=collection, points=points)

    def search(
        self,
        collection: str,
        query_vector: List[float],
        limit: int = 5,
        score_threshold: float = 0.7,
    ) -> List[Dict]:
        results = self.client.search(
            collection_name=collection,
            query_vector=query_vector,
            limit=limit,
            score_threshold=score_threshold,
        )
        return [
            {"id": r.id, "score": r.score, "payload": r.payload}
            for r in results
        ]

    def delete_collection(self, name: str):
        self.client.delete_collection(collection_name=name)