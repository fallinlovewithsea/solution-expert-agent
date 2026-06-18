from skills.base import BaseSkill, SkillInput, SkillOutput
from pydantic import Field
from typing import List, Dict, Optional


class ContentGenInput(SkillInput):
    full_proposal: dict = Field(description="S5 方案设计输出")
    matched_cases: List[Dict] = Field(default_factory=list, description="S6 案例匹配结果")
    brand_assets: Dict = Field(default_factory=dict, description="品牌资产信息")


class ContentGenOutput(SkillOutput):
    slides: List[Dict] = Field(default_factory=list)
    slide_count: int = 0


class S7ContentGeneration(BaseSkill):
    name = "s7_content_gen"
    description = "内容生成：根据方案设计生成 Slide 内容"

    SLIDE_STRUCTURE = [
        {"section": "封面", "title_key": "cover_title", "layout_type": "cover"},
        {"section": "公司介绍", "title_key": "company_title", "layout_type": "two_column"},
        {"section": "行业洞察", "title_key": "industry_title", "layout_type": "chart_focus"},
        {"section": "客户诊断", "title_key": "diagnosis_title", "layout_type": "bullet_cards"},
        {"section": "竞品对标", "title_key": "competitor_title", "layout_type": "comparison_table"},
        {"section": "解决方案", "title_key": "solution_title", "layout_type": "icon_grid"},
        {"section": "工具赋能与预算", "title_key": "tools_title", "layout_type": "grid_cards"},
        {"section": "案例展示", "title_key": "case_title", "layout_type": "case_card"},
        {"section": "实施路径", "title_key": "timeline_title", "layout_type": "timeline"},
        {"section": "团队介绍", "title_key": "team_title", "layout_type": "two_column"},
    ]

    def execute(self, input_data: ContentGenInput) -> ContentGenOutput:
        slides = []
        proposal = input_data.full_proposal

        for i, slide_def in enumerate(self.SLIDE_STRUCTURE):
            section = slide_def["section"]
            layout = slide_def["layout_type"]

            content = self._generate_slide_content(
                section=section,
                proposal=proposal,
                matched_cases=input_data.matched_cases,
                brand_assets=input_data.brand_assets,
                slide_index=i + 1,
            )

            title = self._extract_title(section, proposal, input_data.brand_assets)

            slides.append({
                "index": i + 1,
                "title": title,
                "section": section,
                "layout_type": layout,
                "content": content,
            })

        return ContentGenOutput(slides=slides, slide_count=len(slides))

    def _generate_slide_content(
        self,
        section: str,
        proposal: dict,
        matched_cases: list,
        brand_assets: dict,
        slide_index: int,
    ) -> str:
        """为每一页 Slide 生成内容，优先使用方案数据，不足时调用 LLM"""
        brand_name = brand_assets.get("brand_name", "")
        industry = brand_assets.get("industry", "")
        pain_points = brand_assets.get("pain_points", [])
        competitors = brand_assets.get("competitors", [])

        # 从提案中提取相关内容
        op_strategy = proposal.get("operation_strategy", {}) or {}
        tool_empower = proposal.get("tool_empowerment", {}) or {}
        impl_path = proposal.get("implementation_path", []) or []

        # 按 section 匹配内容
        section_content = {
            "封面": self._build_cover(brand_name, industry),
            "公司介绍": self._build_company_intro(industry),
            "行业洞察": self._build_industry_slide(industry, op_strategy),
            "客户诊断": self._build_diagnosis_slide(brand_name, pain_points, op_strategy),
            "竞品对标": self._build_competitor_slide(brand_name, competitors, op_strategy),
            "解决方案": self._build_solution_slide(brand_name, op_strategy),
            "工具赋能与预算": self._build_tools_slide(brand_name, tool_empower),
            "案例展示": self._build_case_slide(matched_cases),
            "实施路径": self._build_timeline_slide(brand_name, impl_path),
            "团队介绍": self._build_team_slide(brand_name),
        }

        content = section_content.get(section, "")

        # 如果提案数据不足以生成内容，调用 LLM 补充
        if not content or len(content) < 50:
            content = self._llm_fill_slide(
                section=section,
                brand_name=brand_name,
                industry=industry,
                project_name=brand_assets.get("project_name", ""),
                budget_range=brand_assets.get("budget_range", ""),
                pain_points=pain_points,
                competitors=competitors,
                proposal=proposal,
                matched_cases=matched_cases,
            )

        return content

    def _build_cover(self, brand_name: str, industry: str) -> str:
        """构建封面内容"""
        return f"""<h1>{brand_name} 小红书KOS增长全案方案</h1>
<p>行业：{industry}</p>
<p>易美传播 · 繁星计划</p>
<p>日期：{self._today()}</p>"""

    def _build_company_intro(self, industry: str) -> str:
        """构建公司介绍"""
        return f"""<h2>关于易美传播</h2>
<ul>
<li>专注小红书KOS矩阵营销，服务{industry}等多个行业头部品牌</li>
<li>自主研发AI Service内容生成引擎，日产文案1000+篇、图片2000+张</li>
<li>管理400+品牌KOS账号，累计发布笔记超10万篇</li>
<li>基于火山引擎数据湖的Agent DataLake解决方案</li>
</ul>"""

    def _build_industry_slide(self, industry: str, op_strategy: dict) -> str:
        """构建行业洞察页"""
        insight = op_strategy.get("industry_insight", "")
        if insight:
            return f"<h2>{industry}行业小红书KOS营销趋势</h2>{insight}"
        return f"""<h2>{industry}行业小红书KOS营销趋势</h2>
<p>基于对{industry}行业小红书内容生态的深度分析，该行业在小红书平台的营销呈现以下核心趋势：</p>
<ul>
<li>KOS矩阵规模化运营成为头部品牌标配</li>
<li>AIGC内容生产效率成为竞争关键变量</li>
<li>搜索占位与评论区营销成为新的转化战场</li>
</ul>"""

    def _build_diagnosis_slide(self, brand_name: str, pain_points: list, op_strategy: dict) -> str:
        """构建客户诊断页"""
        diag = op_strategy.get("client_diagnosis", "")
        if diag:
            return f"<h2>{brand_name} 小红书营销现状诊断</h2>{diag}"
        items = "".join(f"<li>{p}</li>" for p in pain_points[:5]) if pain_points else "<li>需要进一步诊断</li>"
        return f"<h2>{brand_name} 小红书营销现状诊断</h2><ul>{items}</ul>"

    def _build_competitor_slide(self, brand_name: str, competitors: list, op_strategy: dict) -> str:
        """构建竞品对标页"""
        bench = op_strategy.get("competitor_benchmark", "")
        if bench:
            return f"<h2>竞品对标分析</h2>{bench}"
        comp_rows = ""
        for c in competitors[:5]:
            comp_rows += f"<tr><td>{c}</td><td>待分析</td><td>待分析</td><td>待分析</td></tr>"
        return f"""<h2>{brand_name} vs 竞品 小红书表现对比</h2>
<table><tr><th>品牌</th><th>KOS账号数</th><th>月均笔记</th><th>互动率</th></tr>{comp_rows}</table>"""

    def _build_solution_slide(self, brand_name: str, op_strategy: dict) -> str:
        """构建解决方案页"""
        growth = op_strategy.get("growth_strategy", "")
        platform = op_strategy.get("platform_strategy", "")
        execution = op_strategy.get("execution_plan", "")
        parts = []
        if growth:
            parts.append(f"<h3>增长策略</h3>{growth}")
        if platform:
            parts.append(f"<h3>平台策略</h3>{platform}")
        if execution:
            parts.append(f"<h3>执行方案</h3>{execution}")
        if parts:
            return f"<h2>{brand_name} KOS矩阵增长方案</h2>" + "".join(parts)
        return f"""<h2>{brand_name} KOS矩阵增长方案</h2>
<h3>增长策略</h3>
<ul>
<li>AIGC内容量产：日产1000+文案、2000+图片，保障KOS矩阵内容供给</li>
<li>KOS代发代管：400+账号矩阵化管理，统一内容质量与发布节奏</li>
<li>搜索占位：关键词前置，一篇内容服务一个主关键词</li>
<li>评论区营销：将评论区作为核心转化场</li>
</ul>
<h3>执行方案</h3>
<ul>
<li>账号矩阵搭建：A/B/C分层分发，优账号优先承载核心关键词</li>
<li>内容生产：AI Agent批量生成，多重审核保障质量</li>
<li>数据复盘：霸屏率、互动率、转化率三指标驱动优化</li>
</ul>"""

    def _build_tools_slide(self, brand_name: str, tool_empower: dict) -> str:
        """构建工具赋能与预算页"""
        product = tool_empower.get("product_capability", "")
        budget = tool_empower.get("budget_planning", "")
        parts = []
        if product:
            parts.append(f"<h3>产品能力匹配</h3>{product}")
        if budget:
            parts.append(f"<h3>预算规划</h3>{budget}")
        if parts:
            return f"<h2>工具赋能与预算规划</h2>" + "".join(parts)
        return f"""<h2>工具赋能与预算规划</h2>
<h3>产品能力匹配</h3>
<ul>
<li>AI Service：AIGC内容生成、智能润色、智能改图</li>
<li>内容罗盘：内容趋势分析、竞品监控、内容ROI评估</li>
<li>Agent DataLake：数据湖+向量检索+LangGraph编排</li>
</ul>
<h3>预算规划</h3>
<ul>
<li>内容生产：AIGC批量生成，单篇成本可控</li>
<li>账号管理：400+账号矩阵化管理</li>
<li>数据看板：实时监控霸屏率与转化效果</li>
</ul>"""

    def _build_case_slide(self, matched_cases: list) -> str:
        """构建案例展示页"""
        if matched_cases:
            case_items = ""
            for c in matched_cases[:3]:
                case_items += f"""<div class="case-card">
<h3>{c.get('case_name', c.get('name', '案例'))}</h3>
<p>行业：{c.get('industry', '')} | 相关性：{c.get('relevance_score', '')}</p>
<p>{c.get('match_reason', c.get('summary', ''))}</p>
</div>"""
            return f"<h2>成功案例</h2><div class=\"case-grid\">{case_items}</div>"
        return """<h2>成功案例</h2>
<p>已为飞鹤、英氏、金领冠、a2、林氏家居、老庙、领克、极氪等17+品牌提供KOS矩阵营销服务。</p>"""

    def _build_timeline_slide(self, brand_name: str, impl_path: list) -> str:
        """构建实施路径页"""
        if impl_path:
            timeline_items = ""
            for p in impl_path[:4]:
                timeline_items += f"""<div class="timeline-item">
<h3>{p.get('phase', '')}</h3>
<p>时间：{p.get('timeline', '')}</p>
<p>交付：{p.get('deliverables', '')}</p>
</div>"""
            return f"<h2>{brand_name} 项目实施路径</h2><div class=\"timeline\">{timeline_items}</div>"
        return f"""<h2>{brand_name} 项目实施路径</h2>
<ul>
<li>Phase 1：需求诊断与策略对齐（第1-2周）</li>
<li>Phase 2：内容生产与账号搭建（第3-4周）</li>
<li>Phase 3：上线运营与数据监控（第5-8周）</li>
<li>Phase 4：数据复盘与策略优化（第9-12周）</li>
</ul>"""

    def _build_team_slide(self, brand_name: str) -> str:
        """构建团队介绍页"""
        return f"""<h2>{brand_name} 项目服务团队</h2>
<ul>
<li>策略顾问：负责行业洞察、增长策略制定</li>
<li>内容运营：负责AIGC内容生产与质量审核</li>
<li>账户管理：负责400+账号矩阵化管理</li>
<li>数据分析：负责数据看板与复盘报告</li>
<li>客户成功：负责客户沟通与需求响应</li>
</ul>"""

    def _llm_fill_slide(
        self, section: str, brand_name: str, industry: str, project_name: str,
        budget_range: str, pain_points: list, competitors: list,
        proposal: dict, matched_cases: list,
    ) -> str:
        """LLM 补充生成 Slide 内容"""
        try:
            from app.llm import get_llm
            llm = get_llm(task_type="light")
            prompt = f"""为以下提案的 '{section}' 页面生成内容。用 HTML 格式返回，使用 h2/h3/p/ul/li/table 标签。

品牌：{brand_name}
行业：{industry}
痛点：{pain_points[:3] if pain_points else '未知'}
竞品：{competitors[:3] if competitors else '未知'}
预算：{budget_range or '未指定'}
方案摘要：{str(proposal)[:500]}
案例：{str(matched_cases)[:300]}

要求：精炼、结构化、可落地。只返回 HTML 内容。"""
            resp = llm.invoke(prompt)
            content = resp.content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("```", 1)[0]
            return content
        except Exception:
            return f"<h2>{section}</h2><p>内容待补充</p>"

    def _extract_title(self, section: str, proposal: dict, brand_assets: dict) -> str:
        """提取页面标题"""
        brand = brand_assets.get("brand_name", "")
        titles = {
            "封面": f"{brand} 小红书KOS增长全案",
            "公司介绍": "关于易美传播",
            "行业洞察": f"{brand_assets.get('industry', '')}行业小红书KOS营销趋势",
            "客户诊断": f"{brand} 小红书营销现状诊断",
            "竞品对标": f"{brand} vs 竞品 小红书表现对比",
            "解决方案": f"{brand} KOS矩阵增长方案",
            "工具赋能与预算": "工具赋能与预算规划",
            "案例展示": "成功案例展示",
            "实施路径": f"{brand} 项目实施路径",
            "团队介绍": f"{brand} 项目服务团队",
        }
        return titles.get(section, section)

    @staticmethod
    def _get_layout(section: str) -> str:
        layouts = {
            "封面": "cover", "公司介绍": "two_column",
            "行业洞察": "chart_focus", "客户诊断": "bullet_cards",
            "竞品对标": "comparison_table", "解决方案": "icon_grid",
            "工具赋能与预算": "grid_cards", "案例展示": "case_card",
            "实施路径": "timeline", "团队介绍": "two_column",
        }
        return layouts.get(section, "default")

    @staticmethod
    def _today() -> str:
        from datetime import datetime
        return datetime.now().strftime("%Y年%m月%d日")