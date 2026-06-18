import os
from celery import Celery

celery_app = Celery(
    "solution_expert",
    broker=os.getenv("CELERY_BROKER", "redis://redis:6379/0"),
    backend=os.getenv("CELERY_BACKEND", "redis://redis:6379/1"),
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
)


@celery_app.task(name="collect_xhs_data")
def collect_xhs_data(industry: str, competitors: list, client_name: str):
    """定时采集小红书数据"""
    from skills.s3_industry_insight import S3IndustryInsight, IndustryInsightInput
    skill = S3IndustryInsight()
    result = skill.run(IndustryInsightInput(
        industry=industry,
        competitors=competitors,
        client_name=client_name,
    ))
    return result.model_dump()


@celery_app.task(name="archive_proposal")
def archive_proposal(proposal_data: dict):
    """归档提案数据到物料库"""
    from skills.s9_archive import S9Archive, ArchiveInput
    skill = S9Archive()
    result = skill.run(ArchiveInput(
        final_proposal=proposal_data,
        bid_result=proposal_data.get("bid_result", ""),
    ))
    return result.model_dump()


@celery_app.task(name="distill_knowledge")
def distill_knowledge(doc_id: int = None):
    """对指定文档或全部文档进行知识蒸馏"""
    from app.db.database import get_db
    from app.knowledge.distiller import KnowledgeDistiller
    from app.vector_store.client import VectorStore

    with get_db() as db:
        cursor = db.cursor()
        if doc_id:
            cursor.execute("SELECT * FROM raw_documents WHERE id = %s", (doc_id,))
        else:
            cursor.execute("SELECT * FROM raw_documents WHERE id NOT IN (SELECT DISTINCT CAST(source_id AS INTEGER) FROM knowledge_relations WHERE source_type = 'raw_document') ORDER BY id LIMIT 50")

        rows = cursor.fetchall()
        distiller = KnowledgeDistiller(vector_store=VectorStore(), db=db)
        count = 0
        for row in rows:
            doc = dict(row)
            distiller.distill_document({
                "name": doc.get("doc_name", ""),
                "type": doc.get("doc_type", ""),
                "content": doc.get("content", ""),
                "source_folder": doc.get("source_folder", ""),
                "token": doc.get("feishu_token", ""),
                "url": doc.get("feishu_url", ""),
            })
            count += 1
        return {"distilled": count}


@celery_app.task(name="distill_xhs")
def distill_xhs_data(xhs_id: int = None):
    """对小红书采集数据进行知识蒸馏"""
    from app.db.database import get_db
    from app.knowledge.distiller import KnowledgeDistiller
    from app.vector_store.client import VectorStore

    with get_db() as db:
        cursor = db.cursor()
        if xhs_id:
            cursor.execute("SELECT * FROM raw_xhs_data WHERE id = %s", (xhs_id,))
        else:
            cursor.execute("SELECT * FROM raw_xhs_data WHERE id NOT IN (SELECT DISTINCT CAST(source_id AS INTEGER) FROM knowledge_relations WHERE source_type = 'xhs_data') ORDER BY id LIMIT 50")

        rows = cursor.fetchall()
        distiller = KnowledgeDistiller(vector_store=VectorStore())
        count = 0
        for row in rows:
            distiller.distill_xhs_data(dict(row))
            count += 1
        return {"distilled": count}