import time
import random
import logging
import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import httpx

logger = logging.getLogger(__name__)


class XHSCollector:
    """小红书公开数据采集器 — 增强版

    支持：
    - 指数退避重试 + 速率限制
    - 开发模式（模拟数据，无需真实网络）
    - 笔记详情 + 评论采集
    - LLM 驱动的深度内容分析
    - Cookie/Session 持久化
    """

    SEARCH_API = "https://edith.xiaohongshu.com/api/sns/web/v1/search/notes"
    NOTE_API = "https://edith.xiaohongshu.com/api/sns/web/v1/feed"
    COMMENT_API = "https://edith.xiaohongshu.com/api/sns/web/v2/comment/page"

    MAX_RETRIES = 3
    BASE_DELAY = 2.0  # 基础重试间隔（秒）
    RATE_LIMIT_INTERVAL = 1.5  # 请求间隔（秒）
    DEV_MODE = os.getenv("XHS_DEV_MODE", "false").lower() == "true"

    def __init__(self):
        self._last_request_time = 0.0
        self.client = httpx.Client(
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/125.0.0.0 Safari/537.36"
                ),
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Origin": "https://www.xiaohongshu.com",
                "Referer": "https://www.xiaohongshu.com/",
            },
            timeout=30.0,
            follow_redirects=True,
        )

    # ── 公开入口 ──────────────────────────────────────────────

    def search_industry(self, keywords: List[str], limit: int = 50) -> Dict:
        """按行业关键词采集笔记 + LLM 分析"""
        if self.DEV_MODE:
            return self._dev_industry_data(keywords)

        results = {
            "keywords": keywords,
            "notes": [],
            "analysis": {},
            "collected_at": datetime.now().isoformat(),
        }
        for kw in keywords:
            notes = self._search_notes(kw, max(limit // len(keywords), 5))
            results["notes"].extend(notes)

        # 去重
        results["notes"] = self._deduplicate(results["notes"])

        # LLM 深度分析
        if results["notes"]:
            results["analysis"] = self._analyze_with_llm(
                "行业", results["keywords"], results["notes"]
            )

        return results

    def search_competitor(self, brand_name: str, limit: int = 30) -> Dict:
        """按品牌名采集竞品笔记 + 评论"""
        if self.DEV_MODE:
            return self._dev_competitor_data(brand_name)

        notes = self._search_notes(brand_name, limit)
        comment_data = self._collect_comments(notes[:5])

        analysis = {}
        if notes:
            analysis = self._analyze_with_llm(
                "竞品", [brand_name], notes
            )

        return {
            "brand": brand_name,
            "notes": notes,
            "comments": comment_data,
            "analysis": analysis,
            "collected_at": datetime.now().isoformat(),
        }

    def search_client(self, account_name: str, limit: int = 30) -> Dict:
        """采集客户账号笔记 + 评论舆情"""
        if self.DEV_MODE:
            return self._dev_client_data(account_name)

        notes = self._search_notes(account_name, limit)
        comment_data = self._collect_comments(notes[:5])

        analysis = {}
        if notes:
            analysis = self._analyze_with_llm(
                "客户", [account_name], notes
            )

        return {
            "account": account_name,
            "notes": notes,
            "comments": comment_data,
            "analysis": analysis,
            "collected_at": datetime.now().isoformat(),
        }

    # ── 核心采集 ──────────────────────────────────────────────

    def _search_notes(self, keyword: str, limit: int) -> List[Dict]:
        """搜索笔记，带重试和速率限制"""
        notes = []
        page = 1

        while len(notes) < limit and page <= 3:
            batch = self._fetch_page(keyword, page, min(limit - len(notes), 20))
            if not batch:
                break
            notes.extend(batch)
            page += 1

        return notes[:limit]

    def _fetch_page(self, keyword: str, page: int, page_size: int) -> List[Dict]:
        """请求单页笔记（带重试）"""
        for attempt in range(self.MAX_RETRIES):
            try:
                self._rate_limit()
                response = self.client.get(
                    self.SEARCH_API,
                    params={
                        "keyword": keyword,
                        "page": page,
                        "page_size": page_size,
                        "sort": "general",
                        "search_id": self._gen_search_id(),
                    },
                )

                if response.status_code == 200:
                    return self._parse_notes(response.json())
                elif response.status_code == 429:
                    wait = self.BASE_DELAY * (2 ** attempt)
                    logger.warning(f"[XHS] 速率限制，等待 {wait}s 后重试")
                    time.sleep(wait)
                elif response.status_code == 471:
                    logger.warning("[XHS] 触发反爬，降级到开发模式")
                    return []
                else:
                    logger.warning(f"[XHS] HTTP {response.status_code} for '{keyword}'")
                    if attempt < self.MAX_RETRIES - 1:
                        time.sleep(self.BASE_DELAY * (2 ** attempt))

            except httpx.TimeoutException:
                logger.warning(f"[XHS] 请求超时 (attempt {attempt+1})")
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.BASE_DELAY * (2 ** attempt))
            except Exception as e:
                logger.error(f"[XHS] 采集异常: {e}")
                break

        return []

    def _parse_notes(self, data: dict) -> List[Dict]:
        """解析笔记数据"""
        items = data.get("data", {}).get("items", [])
        parsed = []
        for item in items:
            note_card = item.get("note_card", {}) or {}
            interact = note_card.get("interact_info", {}) or {}
            user = note_card.get("user", {}) or {}
            cover = note_card.get("cover", {})

            parsed.append({
                "note_id": item.get("id", ""),
                "title": note_card.get("display_title", ""),
                "desc": (note_card.get("desc", "") or "")[:500],
                "type": note_card.get("type", "normal"),
                "likes": interact.get("liked_count", 0) or 0,
                "comments": interact.get("comment_count", 0) or 0,
                "collects": interact.get("collected_count", 0) or 0,
                "shares": interact.get("share_count", 0) or 0,
                "author": user.get("nickname", ""),
                "author_id": user.get("user_id", ""),
                "author_image": user.get("avatar", ""),
                "cover_url": cover.get("url_default", "") or cover.get("url", ""),
                "tags": [
                    t.get("name", "")
                    for t in (note_card.get("tag_list", []) or [])
                ],
                "time": note_card.get("time", 0),
                "url": f"https://www.xiaohongshu.com/explore/{item.get('id', '')}",
            })
        return parsed

    def _collect_comments(self, notes: List[Dict]) -> List[Dict]:
        """采集笔记评论（用于舆情分析）"""
        if not notes:
            return []

        comments = []
        for note in notes[:3]:
            note_id = note.get("note_id", "")
            if not note_id:
                continue
            try:
                self._rate_limit()
                response = self.client.get(
                    self.COMMENT_API,
                    params={
                        "note_id": note_id,
                        "cursor": "",
                        "top_comment_id": "",
                        "image_formats": "jpg,webp",
                    },
                )
                if response.status_code == 200:
                    data = response.json()
                    for c in data.get("data", {}).get("comments", [])[:10]:
                        comments.append({
                            "note_id": note_id,
                            "comment_id": c.get("id", ""),
                            "content": c.get("content", ""),
                            "likes": c.get("like_count", 0),
                            "author": c.get("user_info", {}).get("nickname", ""),
                            "time": c.get("create_time", 0),
                        })
            except Exception:
                continue

        return comments

    def _analyze_with_llm(
        self, target_type: str, keywords: List[str], notes: List[Dict]
    ) -> Dict:
        """使用 LLM 对采集数据进行深度分析"""
        try:
            from app.llm import get_llm

            # 构建分析样本
            sample = notes[:10]
            titles = [n.get("title", "") for n in sample]
            total_likes = sum(n.get("likes", 0) for n in notes)
            authors = list(set(n.get("author", "") for n in notes))

            prompt = f"""你是小红书数据分析专家。请分析以下 {target_type} 数据：

关键词：{keywords}
采集笔记数：{len(notes)}
总互动量：{total_likes}
热门标题：{titles}

请返回 JSON：
- content_themes: 内容主题分布（3-5个主题及占比）
- audience_interest: 用户兴趣点（3-5条）
- hot_elements: 爆文特征（封面/标题/内容模式）
- sentiment_overview: 整体舆情倾向（正面/负面/中性）
- content_gap: 内容空白机会点（3-5条）
- recommended_angles: 建议切入角度（3-5条）

只返回 JSON。"""

            llm = get_llm("heavy")
            response = llm.invoke(prompt)
            content = response.content

            # 提取 JSON
            import json as j
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            return j.loads(content)

        except Exception as e:
            logger.warning(f"[XHS] LLM 分析失败，使用基础统计: {e}")
            return self._basic_analysis(notes)

    def _basic_analysis(self, notes: List[Dict]) -> Dict:
        """基础统计分析（LLM 不可用时的降级方案）"""
        note_count = len(notes)
        if note_count == 0:
            return {"note_count": 0, "message": "无数据"}

        total_likes = sum(n.get("likes", 0) for n in notes)
        total_comments = sum(n.get("comments", 0) for n in notes)
        avg_likes = total_likes // note_count if note_count else 0

        return {
            "note_count": note_count,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "avg_likes": avg_likes,
            "top_authors": self._top_authors(notes, 5),
            "top_notes": self._top_notes(notes, 3),
            "content_themes": ["基于笔记标题统计"],
            "audience_interest": ["数据量不足，建议启用 LLM 分析"],
            "hot_elements": "待 LLM 分析",
            "sentiment_overview": "待 LLM 分析",
            "content_gap": ["待 LLM 分析"],
            "recommended_angles": ["待 LLM 分析"],
        }

    def _top_authors(self, notes: List[Dict], n: int) -> List[Dict]:
        author_map = {}
        for note in notes:
            author = note.get("author", "unknown")
            if author not in author_map:
                author_map[author] = {"name": author, "note_count": 0, "total_likes": 0}
            author_map[author]["note_count"] += 1
            author_map[author]["total_likes"] += note.get("likes", 0)
        return sorted(author_map.values(), key=lambda x: x["total_likes"], reverse=True)[:n]

    def _top_notes(self, notes: List[Dict], n: int) -> List[Dict]:
        return sorted(notes, key=lambda x: x.get("likes", 0), reverse=True)[:n]

    def _deduplicate(self, notes: List[Dict]) -> List[Dict]:
        seen = set()
        unique = []
        for n in notes:
            nid = n.get("note_id", "")
            if nid and nid not in seen:
                seen.add(nid)
                unique.append(n)
        return unique

    # ── 工具方法 ──────────────────────────────────────────────

    def _rate_limit(self):
        """速率限制：确保请求间隔不小于 RATE_LIMIT_INTERVAL"""
        now = time.time()
        elapsed = now - self._last_request_time
        if elapsed < self.RATE_LIMIT_INTERVAL:
            jitter = random.uniform(0, 0.5)
            time.sleep(self.RATE_LIMIT_INTERVAL - elapsed + jitter)
        self._last_request_time = time.time()

    def _gen_search_id(self) -> str:
        return f"{int(time.time() * 1000)}{random.randint(1000, 9999)}"

    # ── 开发模式模拟数据 ──────────────────────────────────────

    def _dev_industry_data(self, keywords: List[str]) -> Dict:
        return {
            "keywords": keywords,
            "notes": self._dev_notes(keywords[0], 25),
            "analysis": {
                "note_count": 25,
                "total_likes": 12500,
                "total_comments": 3200,
                "avg_likes": 500,
                "content_themes": [
                    {"theme": "产品测评", "ratio": 0.35},
                    {"theme": "使用教程", "ratio": 0.25},
                    {"theme": "种草推荐", "ratio": 0.20},
                    {"theme": "行业资讯", "ratio": 0.12},
                    {"theme": "互动话题", "ratio": 0.08},
                ],
                "audience_interest": [
                    "产品成分与安全性",
                    "性价比对比",
                    "使用效果真实反馈",
                    "品牌口碑与信任度",
                ],
                "hot_elements": "封面采用对比图+大字标题，内容以'真实体验+数据支撑'为主",
                "sentiment_overview": "正面 65% / 中性 25% / 负面 10%",
                "content_gap": [
                    "专业深度测评内容不足",
                    "KOS 矩阵账号密度低",
                    "用户互动回评率低",
                ],
                "recommended_angles": [
                    "打造'成分党'专业测评人设",
                    "高频互动问答提升信任",
                    "季节性内容策划抢占流量",
                ],
            },
            "collected_at": datetime.now().isoformat(),
        }

    def _dev_competitor_data(self, brand_name: str) -> Dict:
        note_count = random.randint(20, 60)
        return {
            "brand": brand_name,
            "notes": self._dev_notes(brand_name, note_count),
            "comments": self._dev_comments(brand_name, 15),
            "analysis": {
                "note_count": note_count,
                "total_likes": note_count * random.randint(200, 600),
                "content_themes": [
                    {"theme": "达人种草", "ratio": 0.40},
                    {"theme": "官方发布", "ratio": 0.30},
                    {"theme": "用户UGC", "ratio": 0.20},
                    {"theme": "活动推广", "ratio": 0.10},
                ],
                "kos_estimated_scale": random.randint(30, 150),
                "publishing_frequency": f"月均 {random.randint(30, 100)} 篇",
                "engagement_rate": f"{random.uniform(1.5, 5.0):.1f}%",
                "strength": "内容矩阵稳定，达人资源丰富",
                "weakness": "内容同质化明显，互动深度不足",
            },
            "collected_at": datetime.now().isoformat(),
        }

    def _dev_client_data(self, account_name: str) -> Dict:
        note_count = random.randint(8, 30)
        health = random.randint(40, 75)
        return {
            "account": account_name,
            "notes": self._dev_notes(account_name, note_count),
            "comments": self._dev_comments(account_name, 10),
            "analysis": {
                "note_count": note_count,
                "account_health_score": health,
                "content_quality_score": health - random.randint(5, 15),
                "sentiment": {
                    "positive": random.uniform(0.50, 0.75),
                    "neutral": random.uniform(0.15, 0.30),
                    "negative": random.uniform(0.05, 0.20),
                },
                "key_issues": [
                    "内容更新频率不稳定",
                    "缺乏统一视觉风格",
                    "评论区互动率低",
                ],
                "improvement_areas": [
                    "建立内容日历，稳定更新节奏",
                    "统一品牌视觉规范",
                    "建立评论区回复 SOP",
                ],
            },
            "collected_at": datetime.now().isoformat(),
        }

    def _dev_notes(self, keyword: str, count: int) -> List[Dict]:
        notes = []
        templates = [
            "【深度测评】{kw}到底值不值得买？看完这篇就懂了",
            "{kw}使用一个月后，我来说说真实感受",
            "别再踩坑了！{kw}避雷指南",
            "年度好物推荐 | {kw}必须拥有姓名",
            "新手必看 | {kw}入门指南",
            "对比了5款{kw}，这款性价比最高",
            "大家都在问的{kw}，今天统一回答",
            "被问爆了的{kw}，终于整理好了",
        ]
        for i in range(count):
            tpl = random.choice(templates)
            notes.append({
                "note_id": f"dev_{keyword}_{i}",
                "title": tpl.format(kw=keyword),
                "desc": f"这是关于{keyword}的第{i+1}篇笔记，详细介绍了产品特点和使用心得。",
                "type": random.choice(["normal", "video"]),
                "likes": random.randint(50, 2000),
                "comments": random.randint(5, 200),
                "collects": random.randint(10, 500),
                "shares": random.randint(1, 100),
                "author": random.choice(["达人A", "博主B", "用户C", "KOL_D", "素人E"]),
                "author_id": f"dev_author_{random.randint(1, 999)}",
                "author_image": "",
                "cover_url": "",
                "tags": [keyword, random.choice(["好物推荐", "测评", "种草", "干货"])],
                "time": int((datetime.now() - timedelta(days=random.randint(1, 90))).timestamp() * 1000),
                "url": f"https://www.xiaohongshu.com/explore/dev_{i}",
            })
        return notes

    def _dev_comments(self, keyword: str, count: int) -> List[Dict]:
        templates = [
            "这个真的很好用！",
            "已收藏，谢谢分享",
            "请问适合新手吗？",
            "和XX品牌比起来怎么样？",
            "价格有点贵，有没有平替？",
            "用了一段时间，效果确实不错",
            "求链接！",
            "踩过坑，早看到这篇就好了",
        ]
        return [
            {
                "note_id": f"dev_note_{i//3}",
                "comment_id": f"dev_cmt_{i}",
                "content": random.choice(templates),
                "likes": random.randint(0, 50),
                "author": random.choice(["用户001", "小红薯", "路人甲"]),
                "time": int(time.time() * 1000),
            }
            for i in range(count)
        ]