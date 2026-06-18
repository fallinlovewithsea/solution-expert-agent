from app.skills.base import BaseSkill, SkillInput, SkillOutput
from pydantic import Field
from typing import List, Optional, Dict
from app.skills.xhs_collector import XHSCollector


class IndustryInsightInput(SkillInput):
    industry: str = Field(description="行业")
    category: str = Field(default="", description="子品类")
    competitors: List[str] = Field(default_factory=list, description="竞品列表")
    client_name: str = Field(default="", description="客户名称")
    client_brand: str = Field(default="", description="客户品牌")


class IndustryInsightOutput(SkillOutput):
    industry_analysis: Dict = Field(default_factory=dict)
    competitor_analysis: List[Dict] = Field(default_factory=list)
    client_diagnosis: Dict = Field(default_factory=dict)
    growth_analysis: Dict = Field(default_factory=dict)
    summary: str = ""


class S3IndustryInsight(BaseSkill):
    name = "s3_industry_insight"
    description = "行业洞察：采集小红书行业数据 + 竞品分析 + 客户诊断 + 增长分析"

    INDUSTRY_KEYWORDS = {
        "母婴": ["母婴", "奶粉", "宝宝", "育儿", "辅食", "婴幼儿"],
        "大健康": ["健康", "养生", "保健品", "营养", "大健康", "调理"],
        "家居家装": ["家居", "装修", "家装", "软装", "家具", "全屋定制"],
        "汽车": ["汽车", "新能源", "电动车", "新车", "试驾", "买车"],
        "酒类": ["酒", "白酒", "红酒", "品酒", "送礼", "茅台"],
        "食品": ["食品", "零食", "饮料", "乳制品", "牛奶", "酸奶"],
        "珠宝": ["珠宝", "黄金", "钻石", "首饰", "戒指", "项链"],
        "设计": ["设计", "UI", "品牌设计", "平面设计", "包装设计"],
        "技术": ["技术", "SaaS", "云计算", "AI", "数据", "数字化转型"],
    }

    def execute(self, input_data: IndustryInsightInput) -> IndustryInsightOutput:
        collector = XHSCollector()
        keywords = self.INDUSTRY_KEYWORDS.get(
            input_data.industry,
            [input_data.industry] if input_data.industry else ["营销"],
        )

        # 1. 行业数据采集
        industry_data = collector.search_industry(keywords, limit=20)

        # 2. 竞品数据采集（一次采集，避免重复）
        competitor_data = {}
        for comp in input_data.competitors:
            if comp:
                competitor_data[comp] = collector.search_competitor(comp, limit=10)

        # 3. 客户数据采集
        client_data = None
        if input_data.client_name:
            client_data = collector.search_client(input_data.client_name, limit=10)

        # 4. 数据分析
        industry_analysis = self._analyze_industry(industry_data)
        competitor_analysis = self._analyze_competitors(competitor_data, input_data.competitors)
        client_diagnosis = self._analyze_client(client_data, input_data.client_name)
        growth_analysis = self._analyze_growth(industry_analysis, competitor_analysis)

        # 5. 生成摘要
        summary = self._build_summary(
            input_data.industry, industry_analysis, competitor_analysis, client_diagnosis
        )

        # 6. 写入 L1 原始数据层（一次批量写入，避免重复采集）
        self._save_raw_xhs_data(
            input_data, industry_data, competitor_data, client_data,
            industry_analysis, competitor_analysis, client_diagnosis,
        )

        return IndustryInsightOutput(
            industry_analysis=industry_analysis,
            competitor_analysis=competitor_analysis,
            client_diagnosis=client_diagnosis,
            growth_analysis=growth_analysis,
            summary=summary,
        )

    # ── 分析逻辑 ──────────────────────────────────────────────

    def _analyze_industry(self, data: dict) -> dict:
        analysis = data.get("analysis", {})
        return {
            "overview": analysis.get("content_themes", ""),
            "hot_topics": analysis.get("user_interests", ""),
            "viral_features": analysis.get("viral_features", ""),
            "content_gaps": analysis.get("content_gaps", ""),
            "entry_angles": analysis.get("entry_angles", ""),
            "sentiment": analysis.get("sentiment", ""),
            "note_count": len(data.get("notes", [])),
        }

    def _analyze_competitors(
        self, competitor_data: dict, competitors: list
    ) -> list:
        results = []
        for comp in competitors:
            if comp not in competitor_data:
                continue
            data = competitor_data[comp]
            analysis = data.get("analysis", {})
            results.append({
                "brand": comp,
                "note_count": len(data.get("notes", [])),
                "content_themes": analysis.get("content_themes", ""),
                "sentiment": analysis.get("sentiment", ""),
                "strengths": analysis.get("strengths", []),
                "weaknesses": analysis.get("weaknesses", []),
                "comment_count": len(data.get("comments", [])),
            })
        return results

    def _analyze_client(self, client_data: dict, client_name: str) -> dict:
        if not client_data:
            return {"brand": client_name, "status": "未采集到数据", "note_count": 0}
        analysis = client_data.get("analysis", {})
        return {
            "brand": client_name,
            "note_count": len(client_data.get("notes", [])),
            "content_themes": analysis.get("content_themes", ""),
            "sentiment": analysis.get("sentiment", ""),
            "performance": analysis.get("performance", ""),
            "gaps": analysis.get("gaps", []),
        }

    def _analyze_growth(self, industry: dict, competitors: list) -> dict:
        return {
            "market_size": f"{industry.get('note_count', 0)} 篇行业笔记",
            "competitor_count": len(competitors),
            "growth_drivers": [
                "AIGC内容生产效率提升",
                "KOS矩阵规模化运营",
                "搜索占位策略优化",
                "评论区营销转化",
            ],
            "key_opportunities": [
                "关键词前置+单篇单一关键词策略",
                "AB测试驱动内容优化",
                "A/B/C分层账号分发",
            ],
        }

    def _build_summary(
        self, industry: str, industry_analysis: dict,
        competitor_analysis: list, client_diagnosis: dict,
    ) -> str:
        parts = [f"{industry}行业小红书KOS营销分析："]
        parts.append(f"采集行业笔记 {industry_analysis.get('note_count', 0)} 篇")
        parts.append(f"分析竞品 {len(competitor_analysis)} 个")
        if client_diagnosis.get("status") != "未采集到数据":
            parts.append(f"客户笔记 {client_diagnosis.get('note_count', 0)} 篇")
        return "，".join(parts)

    # ── L1 数据写入 ───────────────────────────────────────────

    def _save_raw_xhs_data(
        self, input_data: IndustryInsightInput,
        industry_data: dict, competitor_data: dict, client_data: dict,
        industry_analysis: dict, competitor_analysis: list, client_diagnosis: dict,
    ):
        """将原始数据写入 L1 raw_xhs_data 表"""
        try:
            from app.db.db import get_db
            db = get_db()
            import json

            # 行业数据
            db.execute(
                "INSERT INTO raw_xhs_data (collect_type, target_name, keywords, notes, comments, analysis, collected_at) "
                "VALUES (?, ?, ?, ?, ?, ?, NOW())",
                (
                    "industry",
                    input_data.industry,
                    json.dumps(self.INDUSTRY_KEYWORDS.get(input_data.industry, []), ensure_ascii=False),
                    json.dumps(industry_data.get("notes", []), ensure_ascii=False),
                    "[]",
                    json.dumps(industry_analysis, ensure_ascii=False),
                ),
            )

            # 竞品数据（已在 execute 中采集，此处直接使用）
            for comp_name, comp_data in competitor_data.items():
                db.execute(
                    "INSERT INTO raw_xhs_data (collect_type, target_name, keywords, notes, comments, analysis, collected_at) "
                    "VALUES (?, ?, ?, ?, ?, ?, NOW())",
                    (
                        "competitor",
                        comp_name,
                        json.dumps([comp_name], ensure_ascii=False),
                        json.dumps(comp_data.get("notes", []), ensure_ascii=False),
                        json.dumps(comp_data.get("comments", []), ensure_ascii=False),
                        json.dumps(comp_data.get("analysis", {}), ensure_ascii=False),
                    ),
                )

            # 客户数据
            if client_data:
                db.execute(
                    "INSERT INTO raw_xhs_data (collect_type, target_name, keywords, notes, comments, analysis, collected_at) "
                    "VALUES (?, ?, ?, ?, ?, ?, NOW())",
                    (
                        "client",
                        input_data.client_name,
                        json.dumps([input_data.client_name], ensure_ascii=False),
                        json.dumps(client_data.get("notes", []), ensure_ascii=False),
                        json.dumps(client_data.get("comments", []), ensure_ascii=False),
                        json.dumps(client_data.get("analysis", {}), ensure_ascii=False),
                    ),
                )

            db.commit()
        except Exception as e:
            print(f"[S3] L1 数据写入失败: {e}")

    @staticmethod
    def _sentiment_from_comments(comments: list) -> str:
        pos = 0
        neg = 0
        pos_words = ["好", "不错", "推荐", "喜欢", "赞", "棒", "优秀", "靠谱"]
        neg_words = ["差", "不好", "失望", "坑", "后悔", "踩雷", "垃圾"]
        for c in comments:
            text = c.get("content", "")
            if any(w in text for w in pos_words):
                pos += 1
            if any(w in text for w in neg_words):
                neg += 1
        if pos > neg:
            return "正面为主"
        if neg > pos:
            return "负面为主"
        return "中性"