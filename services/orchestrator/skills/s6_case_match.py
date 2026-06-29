from skills.base import BaseSkill, SkillInput, SkillOutput
from pydantic import Field
from typing import List, Optional, Dict


class CaseMatchInput(SkillInput):
    industry: str = Field(description="行业")
    customer_type: str = Field(default="", description="客户类型 / 子品类")
    pain_points: List[str] = Field(default_factory=list, description="客户痛点")
    solution_modules: List[str] = Field(default_factory=list, description="方案模块")


class CaseMatchOutput(SkillOutput):
    matched_cases: List[Dict] = Field(default_factory=list)
    recommendation: str = ""


class S6CaseMatch(BaseSkill):
    name = "s6_case_match"
    description = "案例匹配：基于行业、痛点、方案模块多维度匹配相似案例，新增焦虑释放验证和制度同构维度"

    def execute(self, input_data: CaseMatchInput) -> CaseMatchOutput:
        # 从知识库中获取案例列表
        cases = self._load_case_library()
        if not cases:
            return CaseMatchOutput(
                matched_cases=[],
                recommendation="案例库为空，建议先从知识库导入案例"
            )

        # 多维打分（含焦虑释放验证维度）
        scored = []
        for case in cases:
            score = self._calculate_score(
                case, input_data.industry, input_data.customer_type,
                input_data.pain_points, input_data.solution_modules
            )
            if score > 0:
                case["relevance_score"] = round(score, 2)
                scored.append(case)

        # 按分数降序，取前 5
        scored.sort(key=lambda x: x["relevance_score"], reverse=True)
        top5 = scored[:5]

        # 生成推荐语
        rec = self._build_recommendation(top5, input_data)

        return CaseMatchOutput(matched_cases=top5, recommendation=rec)

    def _load_case_library(self) -> List[Dict]:
        """从知识库加载案例"""
        try:
            from app.vector_store.client import VectorStoreClient
            client = VectorStoreClient()
            results = client.search("case_labels", "KOS矩阵 营销 案例", limit=20)
            if results:
                return [r.payload for r in results if r.payload]
        except Exception:
            pass

        # 降级：使用内置案例库
        return [
            {"case_name": "飞鹤繁星计划", "industry": "母婴", "customer_type": "婴幼儿奶粉",
             "pain_points": ["KOS矩阵规模化", "内容质量", "搜索占位", "转化闭环"],
             "solution_modules": ["KOS代发代管", "AIGC内容生成", "搜索占位", "评论区营销"],
             "key_metrics": "5版本迭代，KOS矩阵行业规模第一",
             "source": "飞鹤/飞鹤_繁星计划升级方案"},
            {"case_name": "a2至初KOS项目", "industry": "母婴", "customer_type": "婴幼儿奶粉",
             "pain_points": ["搜索占位效果", "内容质量", "数据复盘"],
             "solution_modules": ["KOS代发代管", "AIGC内容生成", "搜索占位", "数据看板"],
             "key_metrics": "15天完成15,000篇笔记，霸屏率提升至70%",
             "source": "a2/a2_小红书KOS项目复盘"},
            {"case_name": "英氏KOS矩阵", "industry": "母婴", "customer_type": "婴幼儿辅食",
             "pain_points": ["内容效率", "账号管理", "转化率"],
             "solution_modules": ["KOS代发代管", "内容罗盘", "全链路转化"],
             "key_metrics": "全链路管理能力行业领先",
             "source": "根目录/英氏_KOS矩阵全链路管理通案"},
            {"case_name": "金领冠内容营销", "industry": "母婴", "customer_type": "婴幼儿奶粉",
             "pain_points": ["内容差异化", "竞品追赶", "增长放缓"],
             "solution_modules": ["AIGC内容生成", "KOS矩阵", "竞品分析"],
             "key_metrics": "增长迅速，专利配方背书",
             "source": "根目录/金领冠_繁星计划升级方案"},
            {"case_name": "林氏家居KOS矩阵", "industry": "家居家装", "customer_type": "家居零售",
             "pain_points": ["场景化内容", "KOS代发代管", "内容质量"],
             "solution_modules": ["KOS代发代管", "场景化内容", "AIGC内容生成"],
             "key_metrics": "场景展示效果比单品好3倍",
             "source": "根目录/林氏家居_KOS矩阵全链路管理通案"},
            {"case_name": "老庙黄金小红书", "industry": "珠宝", "customer_type": "黄金珠宝",
             "pain_points": ["品牌年轻化", "内容创新", "社交传播"],
             "solution_modules": ["KOS矩阵", "内容创新", "小红书种草"],
             "key_metrics": "品牌文化故事背书策略",
             "source": "根目录/老庙_小红书种草方案"},
            {"case_name": "蒙牛内容营销", "industry": "食品", "customer_type": "乳制品",
             "pain_points": ["内容批量生产", "矩阵管理", "数据归因"],
             "solution_modules": ["AIGC内容生成", "KOS矩阵", "数据归因"],
             "key_metrics": "大健康品类内容合规经验",
             "source": "根目录/蒙牛_KOS矩阵全链路管理通案"},
            {"case_name": "利星行汽车新媒体", "industry": "汽车", "customer_type": "汽车经销商",
             "pain_points": ["新车评测", "新媒体转型", "线索转化"],
             "solution_modules": ["KOS矩阵", "新车评测", "微信+小红书双平台"],
             "key_metrics": "微信+小红书双平台策略",
             "source": "汽车类/利星行_新媒体运营方案"},
            {"case_name": "领克汽车KOS", "industry": "汽车", "customer_type": "新能源汽车",
             "pain_points": ["品牌声量", "KOS矩阵", "口碑建设"],
             "solution_modules": ["KOS矩阵", "新车评测", "用户口碑"],
             "key_metrics": "新能源赛道快速布局",
             "source": "汽车类/领克_新媒体运营方案"},
            {"case_name": "极氪内容营销", "industry": "汽车", "customer_type": "新能源汽车",
             "pain_points": ["品牌认知", "内容创新", "用户互动"],
             "solution_modules": ["KOS矩阵", "AIGC内容生成", "用户互动"],
             "key_metrics": "高端新能源品牌小红书策略",
             "source": "汽车类/极氪_新媒体运营方案"},
        ]

    def _calculate_score(
        self, case: Dict, industry: str, customer_type: str,
        pain_points: List[str], solution_modules: List[str],
    ) -> float:
        """多维度打分：行业(35%) + 客户类型(15%) + 痛点(20%) + 方案模块(20%) + 焦虑释放验证(10%)"""
        score = 0.0

        # 行业匹配 (35%)
        if case.get("industry", "") == industry:
            score += 0.35
        elif industry in case.get("industry", ""):
            score += 0.15

        # 客户类型匹配 (15%)
        if customer_type and case.get("customer_type", "") == customer_type:
            score += 0.15
        elif customer_type and customer_type in case.get("customer_type", ""):
            score += 0.08

        # 痛点匹配 (20%)
        case_pains = case.get("pain_points", [])
        if pain_points and case_pains:
            matched = len(set(pain_points) & set(case_pains))
            total = max(len(pain_points), 1)
            score += 0.2 * (matched / total)

        # 方案模块匹配 (20%)
        case_modules = case.get("solution_modules", [])
        if solution_modules and case_modules:
            matched = len(set(solution_modules) & set(case_modules))
            total = max(len(solution_modules), 1)
            score += 0.2 * (matched / total)

        # 焦虑释放验证 (10%)：案例是否有可量化的"释放"效果（ROI/效率提升/成本降低等）
        key_metrics = case.get("key_metrics", "")
        if key_metrics:
            release_indicators = ["ROI", "提升", "降低", "增长", "节约", "增效"]
            match_count = sum(1 for ind in release_indicators if ind in key_metrics)
            score += 0.1 * (match_count / len(release_indicators))

        return score

    def _build_recommendation(self, cases: List[Dict], input_data: CaseMatchInput) -> str:
        if not cases:
            return "未找到匹配案例，建议扩展搜索范围"
        high = [c for c in cases if c["relevance_score"] >= 0.5]
        if high:
            names = "、".join(c["case_name"] for c in high[:3])
            # 社会证明效应：多案例共同行动形成"行业共识"信号
            social_proof = ""
            if len(high) >= 3:
                industries = set(c.get("industry", "") for c in high)
                if len(industries) >= 2:
                    social_proof = f"跨{len(industries)}个行业的案例共同验证了同类方案，这已形成行业共识——不只一家在这样做。"
            base = f"推荐参考 {names} 等 {len(high)} 个高相关案例"
            if social_proof:
                return f"{base}。{social_proof}"
            return f"{base}，方案设计时可重点借鉴"
        return f"匹配到 {len(cases)} 个案例，建议结合行业特征调整参考侧重点"