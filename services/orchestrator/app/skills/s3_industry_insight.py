from app.skills.base import BaseSkill, SkillInput, SkillOutput
from pydantic import Field
from typing import List, Dict, Optional
from app.skills.xhs_collector import XHSCollector


class IndustryInsightInput(SkillInput):
    industry: str = Field(description="目标行业")
    category: str = Field(default="", description="细分品类")
    competitors: List[str] = Field(default_factory=list, description="竞品品牌名列表")
    client_name: str = Field(default="", description="客户品牌名")
    client_brand: str = Field(default="", description="客户品牌名（别名）")


class IndustryInsightOutput(SkillOutput):
    industry_analysis: Dict = Field(default_factory=dict)
    competitor_analysis: List[Dict] = Field(default_factory=list)
    client_diagnosis: Dict = Field(default_factory=dict)
    growth_analysis: Dict = Field(default_factory=dict)
    # 汇总摘要
    summary: str = Field(default="")


class S3IndustryInsight(BaseSkill):
    name = "s3_industry_insight"
    description = "行业洞察：采集小红书数据 + LLM 深度分析行业/竞品/客户"

    INDUSTRY_KEYWORDS = {
        "母婴": ["宝宝奶粉怎么选", "敏宝口粮", "奶粉测评", "育儿好物", "母婴种草"],
        "大健康": ["养生好物", "健康管理", "保健品推荐", "营养补充"],
        "家居家装": ["装修灵感", "家居好物", "家具推荐", "软装搭配"],
        "汽车": ["买车攻略", "新车评测", "新能源车", "汽车保养"],
        "酒类": ["白酒推荐", "好酒分享", "品酒笔记", "送礼酒"],
        "食品": ["美食推荐", "零食测评", "健康食品", "饮品推荐"],
    }

    def execute(self, input_data: IndustryInsightInput) -> IndustryInsightOutput:
        collector = XHSCollector()

        keywords = self.INDUSTRY_KEYWORDS.get(
            input_data.industry,
            [input_data.industry + "推荐", input_data.industry + "测评"],
        )

        # ── 行业数据采集 ──
        industry_data = collector.search_industry(keywords)

        # ── 竞品数据采集 ──
        competitor_data = []
        for comp in input_data.competitors:
            comp_data = collector.search_competitor(comp)
            competitor_data.append(self._analyze_competitor(comp_data))

        # ── 客户数据采集 ──
        client_name = input_data.client_name or input_data.client_brand
        client_data = collector.search_client(client_name) if client_name else {}
        diagnosis = self._analyze_client(client_data, client_name)

        # ── 增长分析 ──
        growth = self._analyze_growth(input_data.industry, industry_data, competitor_data)

        # ── 行业分析 ──
        industry_analysis = self._analyze_industry(industry_data)

        # ── 生成摘要 ──
        summary = self._build_summary(
            industry_analysis, competitor_data, diagnosis, growth
        )

        # ── 保存原始采集数据到 L1 ──
        self._save_raw_xhs_data("industry", input_data.industry, keywords, industry_data)
        for comp in input_data.competitors:
            comp_raw = collector.search_competitor(comp)
            self._save_raw_xhs_data("competitor", comp, [comp], comp_raw)
        if client_name:
            self._save_raw_xhs_data("client", client_name, [client_name], client_data)

        return IndustryInsightOutput(
            industry_analysis=industry_analysis,
            competitor_analysis=competitor_data,
            client_diagnosis=diagnosis,
            growth_analysis=growth,
            summary=summary,
        )

    # ── 行业分析 ──

    def _analyze_industry(self, data: Dict) -> Dict:
        """使用采集器返回的 LLM 分析结果"""
        analysis = data.get("analysis", {})
        notes = data.get("notes", [])
        total_likes = sum(n.get("likes", 0) for n in notes)
        total_comments = sum(n.get("comments", 0) for n in notes)
        total_collects = sum(n.get("collects", 0) for n in notes)

        return {
            # 基础统计
            "trend_keywords": data.get("keywords", []),
            "note_count": len(notes),
            "total_interactions": total_likes + total_comments + total_collects,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "total_collects": total_collects,
            "avg_likes": total_likes // max(len(notes), 1),
            "volume_trend": (
                f"共采集 {len(notes)} 篇笔记，总互动量 "
                f"{total_likes + total_comments + total_collects}"
            ),
            # LLM 深度分析
            "content_themes": analysis.get("content_themes", []),
            "audience_interest": analysis.get("audience_interest", []),
            "hot_elements": analysis.get("hot_elements", ""),
            "sentiment_overview": analysis.get("sentiment_overview", ""),
            "content_gap": analysis.get("content_gap", []),
            "recommended_angles": analysis.get("recommended_angles", []),
            # 元数据
            "collected_at": data.get("collected_at", ""),
        }

    # ── 竞品分析 ──

    def _analyze_competitor(self, data: Dict) -> Dict:
        """使用采集器返回的 LLM 分析 + 评论数据"""
        analysis = data.get("analysis", {})
        notes = data.get("notes", [])
        comments = data.get("comments", [])
        brand = data.get("brand", "")

        total_likes = sum(n.get("likes", 0) for n in notes)
        note_count = len(notes)
        avg_likes = total_likes // max(note_count, 1)

        return {
            "name": brand,
            "note_count": note_count,
            "monthly_notes": note_count,
            "avg_interaction": avg_likes,
            "total_likes": total_likes,
            # LLM 分析
            "content_strategy": {
                "themes": analysis.get("content_themes", []),
                "kos_estimated_scale": analysis.get("kos_estimated_scale", 0),
                "publishing_frequency": analysis.get(
                    "publishing_frequency", f"月均 {note_count} 篇"
                ),
                "engagement_rate": analysis.get("engagement_rate", "N/A"),
            },
            "strength": analysis.get("strength", "待分析"),
            "weakness": analysis.get("weakness", "待分析"),
            # 评论分析
            "comment_count": len(comments),
            "comment_sentiment": self._sentiment_from_comments(comments),
            # 元数据
            "collected_at": data.get("collected_at", ""),
        }

    # ── 客户诊断 ──

    def _analyze_client(self, data: Dict, client_name: str) -> Dict:
        """使用采集器返回的 LLM 分析 + 评论舆情"""
        analysis = data.get("analysis", {})
        notes = data.get("notes", [])
        comments = data.get("comments", [])

        note_count = len(notes)
        total_likes = sum(n.get("likes", 0) for n in notes)
        avg_likes = total_likes // max(note_count, 1)

        if not analysis:
            return {
                "account_health_score": 0,
                "content_quality_score": 0,
                "sentiment_ratio": {"positive": 0, "neutral": 0, "negative": 0},
                "key_issues": ["暂无数据"],
                "improvement_areas": ["请先采集客户小红书数据"],
                "note_count": 0,
                "avg_likes": 0,
                "total_likes": 0,
                "comment_count": 0,
            }

        # 从 analysis 提取情感数据
        sentiment = analysis.get("sentiment", {})
        sentiment_ratio = {
            "positive": sentiment.get("positive", 0.65),
            "neutral": sentiment.get("neutral", 0.25),
            "negative": sentiment.get("negative", 0.10),
        }

        return {
            "account_health_score": analysis.get("account_health_score", 0),
            "content_quality_score": analysis.get("content_quality_score", 0),
            "sentiment_ratio": sentiment_ratio,
            "key_issues": analysis.get("key_issues", []),
            "improvement_areas": analysis.get("improvement_areas", []),
            # 基础统计
            "note_count": note_count,
            "avg_likes": avg_likes,
            "total_likes": total_likes,
            "comment_count": len(comments),
            "comment_sentiment": self._sentiment_from_comments(comments),
            # 元数据
            "collected_at": data.get("collected_at", ""),
        }

    # ── 增长分析 ──

    def _analyze_growth(
        self, industry: str, industry_data: Dict, competitor_data: List[Dict]
    ) -> Dict:
        """基于行业数据 + 竞品数据生成增长策略建议"""
        analysis = industry_data.get("analysis", {})
        content_gap = analysis.get("content_gap", [])
        recommended_angles = analysis.get("recommended_angles", [])

        # 竞品策略汇总
        competitor_strategies = []
        for comp in competitor_data:
            cs = comp.get("content_strategy", {})
            if isinstance(cs, dict):
                competitor_strategies.append({
                    "name": comp.get("name", ""),
                    "strength": comp.get("strength", ""),
                    "weakness": comp.get("weakness", ""),
                    "kos_scale": cs.get("kos_estimated_scale", 0),
                })

        return {
            "platform_strategy": f"小红书{industry}行业增长策略",
            "growth_model": "KOS矩阵 + 内容种草 + AI赋能",
            "content_gap_opportunities": content_gap,
            "recommended_angles": recommended_angles,
            "competitor_benchmark": competitor_strategies,
            "key_success_factors": [
                "高频稳定的内容输出",
                "KOS 矩阵账号联动",
                "数据驱动的选题优化",
                "评论区深度互动运营",
            ],
        }

    # ── 辅助方法 ──

    def _sentiment_from_comments(self, comments: List[Dict]) -> Dict:
        """基于评论关键词做简易情感分析"""
        if not comments:
            return {"positive": 0, "neutral": 0, "negative": 0}

        positive_words = ["好", "棒", "喜欢", "推荐", "赞", "不错", "好用", "收藏", "学到了"]
        negative_words = ["差", "垃圾", "坑", "后悔", "难用", "不行", "踩雷", "避雷", "智商税"]

        pos = neg = neu = 0
        for c in comments:
            text = c.get("content", "")
            if any(w in text for w in positive_words):
                pos += 1
            elif any(w in text for w in negative_words):
                neg += 1
            else:
                neu += 1

        total = max(pos + neg + neu, 1)
        return {
            "positive": round(pos / total, 2),
            "neutral": round(neu / total, 2),
            "negative": round(neg / total, 2),
        }

    def _build_summary(
        self,
        industry: Dict,
        competitors: List[Dict],
        diagnosis: Dict,
        growth: Dict,
    ) -> str:
        """生成行业洞察一句话摘要"""
        note_count = industry.get("note_count", 0)
        themes = industry.get("content_themes", [])
        theme_str = ""
        if isinstance(themes, list) and themes:
            if isinstance(themes[0], dict):
                theme_str = "、".join(t.get("theme", "") for t in themes[:3])
            else:
                theme_str = "、".join(str(t) for t in themes[:3])

        competitor_count = len(competitors)
        health = diagnosis.get("account_health_score", "N/A")

        return (
            f"{industry.get('trend_keywords', [''])[0]}行业共采集 {note_count} 篇笔记，"
            f"主要内容主题为 {theme_str or '待分析'}；"
            f"分析了 {competitor_count} 个竞品，"
            f"客户账号健康度 {health} 分。"
        )

    def _save_raw_xhs_data(self, collect_type: str, target_name: str,
                           keywords: List[str], data: Dict):
        """保存原始采集数据到 L1 raw_xhs_data 表"""
        if not data:
            return
        try:
            from app.db.database import get_db
            import json as j
            with get_db() as db:
                cursor = db.cursor()
                cursor.execute(
                    """INSERT INTO raw_xhs_data
                       (collect_type, target_name, keywords, notes, comments, analysis)
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (
                        collect_type,
                        target_name,
                        j.dumps(keywords),
                        j.dumps(data.get("notes", [])),
                        j.dumps(data.get("comments", [])),
                        j.dumps(data.get("analysis", {})),
                    ),
                )
        except Exception:
            pass