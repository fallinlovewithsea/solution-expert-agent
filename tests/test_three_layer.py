"""三层数据架构专项测试"""
import pytest
from unittest.mock import patch, MagicMock


class TestRawDataLayer:
    """L1: 原始数据层测试"""

    def test_raw_document_model(self):
        from app.db.models import RawDocument
        doc = RawDocument(
            doc_name="飞鹤繁星计划方案",
            doc_type="slides",
            source_folder="飞鹤",
            feishu_token="tok123",
            feishu_url="https://feishu.cn/slides/tok123",
            content="测试内容",
        )
        assert doc.doc_name == "飞鹤繁星计划方案"
        assert doc.doc_type == "slides"
        assert doc.content == "测试内容"

    def test_raw_xhs_data_model(self):
        from app.db.models import RawXhsData
        data = RawXhsData(
            collect_type="industry",
            target_name="母婴",
            keywords=["宝宝奶粉"],
            notes=[{"title": "测试笔记", "likes": 100}],
            comments=[],
            analysis={"content_themes": [{"theme": "测评", "ratio": 0.5}]},
        )
        assert data.collect_type == "industry"
        assert len(data.notes) == 1
        assert data.notes[0]["likes"] == 100


class TestKnowledgeLayer:
    """L2: 知识层测试"""

    def test_knowledge_relation_model(self):
        from app.db.models import KnowledgeRelation
        rel = KnowledgeRelation(
            source_type="case_labels",
            source_id="feihe_2024",
            target_type="industry_strategy",
            target_id="muying_kos",
            relation_type="belongs_to",
            weight=0.9,
        )
        assert rel.relation_type == "belongs_to"
        assert rel.weight == 0.9

    def test_distiller_xhs(self):
        from app.knowledge.distiller import KnowledgeDistiller
        distiller = KnowledgeDistiller()
        result = distiller.distill_xhs_data({
            "collect_type": "industry",
            "target_name": "母婴",
            "analysis": {
                "content_themes": [{"theme": "产品测评", "ratio": 0.35}],
                "audience_interest": ["产品成分与安全性"],
                "hot_elements": "封面采用对比图",
                "content_gap": ["专业深度测评内容不足"],
                "recommended_angles": ["打造成分党专业测评人设"],
            },
        })
        assert "point_ids" in result
        assert len(result["point_ids"]) == 1

    def test_distiller_empty(self):
        from app.knowledge.distiller import KnowledgeDistiller
        distiller = KnowledgeDistiller()
        result = distiller.distill_xhs_data({
            "collect_type": "industry",
            "target_name": "empty",
            "analysis": {},
        })
        assert result["point_ids"] == []


class TestMemoryLayer:
    """L3: 记忆层测试"""

    def test_user_preference_model(self):
        from app.db.models import UserPreference
        pref = UserPreference(
            user_id="user_001",
            preferred_industries=["母婴", "大健康"],
            budget_range="50-200万",
            output_formats=["slides", "pptx"],
            search_history=["飞鹤", "KOS矩阵"],
            interaction_count=5,
        )
        assert pref.user_id == "user_001"
        assert len(pref.preferred_industries) == 2
        assert pref.interaction_count == 5

    def test_session_memory_model(self):
        from app.db.models import SessionMemory
        session = SessionMemory(
            session_id="sess_001",
            user_id="user_001",
            client_name="飞鹤",
            industry="母婴",
            stage="proposal",
            bid_result="进行中",
            context={"requirement": "KOS矩阵搭建"},
        )
        assert session.client_name == "飞鹤"
        assert session.stage == "proposal"
        assert session.context["requirement"] == "KOS矩阵搭建"

    def test_memory_store_init(self):
        from app.db.memory import MemoryStore
        store = MemoryStore()
        # 不依赖 Redis 的方法应正常工作
        assert store is not None
        assert hasattr(store, 'get_user_preferences')
        assert hasattr(store, 'save_session')


class TestVectorStoreExtended:
    """向量存储扩展测试"""

    def test_collections_include_new(self):
        from app.vector_store.client import VectorStore
        assert "brand_knowledge" in VectorStore.COLLECTIONS
        assert "xhs_insights" in VectorStore.COLLECTIONS
        assert len(VectorStore.COLLECTIONS) == 8


class TestLoaderIntegration:
    """Loader 集成测试"""

    def test_loader_has_distill_methods(self):
        from app.material_libraries.loader import MaterialLibraryLoader
        loader = MaterialLibraryLoader()
        assert hasattr(loader, '_save_raw_document')
        assert hasattr(loader, '_trigger_distill')


class TestS3Integration:
    """S3 集成测试"""

    @patch("skills.s3_industry_insight.XHSCollector")
    def test_s3_has_save_method(self, mock_collector_class):
        """验证 S3 有 _save_raw_xhs_data 方法"""
        mock_collector = MagicMock()
        mock_collector_class.return_value = mock_collector
        mock_collector.search_industry.return_value = {
            "keywords": ["宝宝奶粉"],
            "notes": [],
            "comments": [],
            "analysis": {},
            "collected_at": "2026-06-18",
        }
        mock_collector.search_competitor.return_value = {
            "brand": "伊利",
            "notes": [],
            "comments": [],
            "analysis": {},
            "collected_at": "2026-06-18",
        }
        mock_collector.search_client.return_value = {
            "account": "飞鹤",
            "notes": [],
            "comments": [],
            "analysis": {},
            "collected_at": "2026-06-18",
        }

        from skills.s3_industry_insight import S3IndustryInsight
        skill = S3IndustryInsight()
        assert hasattr(skill, '_save_raw_xhs_data')

    @patch("skills.s3_industry_insight.XHSCollector")
    def test_s3_execute_does_not_crash(self, mock_collector_class):
        """验证 S3 执行不抛异常（DB 不可用时静默跳过）"""
        mock_collector = MagicMock()
        mock_collector_class.return_value = mock_collector
        mock_collector.search_industry.return_value = {
            "keywords": ["宝宝奶粉"],
            "notes": [],
            "comments": [],
            "analysis": {},
            "collected_at": "2026-06-18",
        }
        mock_collector.search_competitor.return_value = {
            "brand": "伊利",
            "notes": [],
            "comments": [],
            "analysis": {},
            "collected_at": "2026-06-18",
        }
        mock_collector.search_client.return_value = {
            "account": "飞鹤",
            "notes": [],
            "comments": [],
            "analysis": {},
            "collected_at": "2026-06-18",
        }

        from skills.s3_industry_insight import S3IndustryInsight, IndustryInsightInput
        skill = S3IndustryInsight()
        result = skill.run(IndustryInsightInput(
            industry="母婴",
            competitors=["伊利"],
            client_name="飞鹤",
        ))
        assert result.success is True
        assert result.industry_analysis["note_count"] == 0


class TestArchiveLifecycle:
    """归档生命周期边界测试"""

    def test_archive_rejects_missing_project_result(self):
        from app.tools.archive import ProposalArchiveTool

        result = ProposalArchiveTool().archive(
            proposal_spec={"title": "测试方案"},
            brief={"client_name": "飞鹤", "industry": "母婴"},
            review_comments="",
            bid_result="",
            user_id="test_user",
            session_id="sess_test_001",
        )

        assert result.success is False
        assert "禁止归档" in result.error


class TestAgentState:
    """AgentState 测试"""

    def test_agent_state_has_memory_fields(self):
        from app.agent import AgentState
        fields = list(AgentState.__annotations__.keys())
        assert "user_id" in fields
        assert "session_id" in fields
        assert "brief" in fields
        assert "decision_map" in fields
        assert "proposal_spec" in fields
        assert "review_status" in fields
