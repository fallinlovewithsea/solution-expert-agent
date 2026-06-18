"""
记忆层 (L3)：用户偏好 + 客户操作历史 + Redis 缓存
"""
import json
import os
import redis
from typing import Optional, Dict, List
from datetime import datetime


class MemoryStore:
    """记忆层统一入口"""

    def __init__(self):
        self.redis = redis.Redis(
            host=os.getenv("REDIS_HOST", "redis"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            db=2,  # 使用独立 db 避免冲突
            decode_responses=True,
        )

    # ── 用户偏好 ──

    def get_user_preferences(self, user_id: str) -> Dict:
        """获取用户偏好（优先 Redis 缓存）"""
        cached = self.redis.get(f"user_pref:{user_id}")
        if cached:
            return json.loads(cached)

        prefs = self._load_user_prefs_from_db(user_id)
        if prefs:
            self.redis.setex(f"user_pref:{user_id}", 3600, json.dumps(prefs, ensure_ascii=False))
        return prefs or {}

    def update_user_preferences(self, user_id: str, updates: Dict):
        """更新用户偏好（PG + Redis 双写）"""
        self._upsert_user_prefs_db(user_id, updates)
        # 刷新缓存
        prefs = self._load_user_prefs_from_db(user_id)
        if prefs:
            self.redis.setex(f"user_pref:{user_id}", 3600, json.dumps(prefs, ensure_ascii=False))

    def record_search(self, user_id: str, keyword: str):
        """记录搜索关键词"""
        prefs = self.get_user_preferences(user_id) or {}
        history = prefs.get("search_history", [])
        history.insert(0, keyword)
        history = history[:20]  # 保留最近 20 条
        self.update_user_preferences(user_id, {"search_history": history})

    def record_industry(self, user_id: str, industry: str):
        """记录行业偏好"""
        prefs = self.get_user_preferences(user_id) or {}
        industries = prefs.get("preferred_industries", [])
        if industry not in industries:
            industries.append(industry)
        self.update_user_preferences(user_id, {"preferred_industries": industries})

    def record_output_format(self, user_id: str, format_type: str):
        """记录输出格式偏好"""
        prefs = self.get_user_preferences(user_id) or {}
        formats = prefs.get("output_formats", [])
        if format_type not in formats:
            formats.append(format_type)
        self.update_user_preferences(user_id, {"output_formats": formats})

    def _load_user_prefs_from_db(self, user_id: str) -> Optional[Dict]:
        """从 PG 加载用户偏好"""
        try:
            from app.db.database import get_db
            with get_db() as db:
                cursor = db.cursor()
                cursor.execute(
                    "SELECT * FROM user_preferences WHERE user_id = %s",
                    (user_id,),
                )
                row = cursor.fetchone()
                if row:
                    return dict(row)
        except Exception:
            pass
        return None

    def _upsert_user_prefs_db(self, user_id: str, updates: Dict):
        """UPSERT 用户偏好到 PG"""
        try:
            from app.db.database import get_db
            with get_db() as db:
                cursor = db.cursor()
                cursor.execute(
                    """INSERT INTO user_preferences (user_id, preferred_industries, preferred_templates,
                       budget_range, output_formats, search_history, interaction_count, last_active_at)
                       VALUES (%s, %s, %s, %s, %s, %s, 1, NOW())
                       ON CONFLICT (user_id) DO UPDATE SET
                       preferred_industries = COALESCE(%s, user_preferences.preferred_industries),
                       preferred_templates = COALESCE(%s, user_preferences.preferred_templates),
                       budget_range = COALESCE(%s, user_preferences.budget_range),
                       output_formats = COALESCE(%s, user_preferences.output_formats),
                       search_history = COALESCE(%s, user_preferences.search_history),
                       interaction_count = user_preferences.interaction_count + 1,
                       last_active_at = NOW(),
                       updated_at = NOW()""",
                    (
                        user_id,
                        json.dumps(updates.get("preferred_industries", [])),
                        json.dumps(updates.get("preferred_templates", [])),
                        updates.get("budget_range", ""),
                        json.dumps(updates.get("output_formats", [])),
                        json.dumps(updates.get("search_history", [])),
                        # ON CONFLICT DO UPDATE values
                        json.dumps(updates.get("preferred_industries")),
                        json.dumps(updates.get("preferred_templates")),
                        updates.get("budget_range"),
                        json.dumps(updates.get("output_formats")),
                        json.dumps(updates.get("search_history")),
                    ),
                )
        except Exception:
            pass

    # ── 会话记忆 ──

    def save_session(self, session_id: str, user_id: str, client_name: str,
                     industry: str = "", stage: str = "", context: Dict = None):
        """保存会话到 PG + Redis"""
        ctx = context or {}
        record = {
            "session_id": session_id,
            "user_id": user_id,
            "client_name": client_name,
            "industry": industry,
            "stage": stage,
            "context": ctx,
        }
        # Redis 短期缓存（24h）
        self.redis.setex(f"session:{session_id}", 86400, json.dumps(record, ensure_ascii=False))
        # 客户端缓存（30min）
        self.redis.setex(f"client:{client_name}", 1800, json.dumps(record, ensure_ascii=False))
        # PG 持久化
        self._save_session_db(record)

    def get_session(self, session_id: str) -> Optional[Dict]:
        """获取会话（优先 Redis）"""
        cached = self.redis.get(f"session:{session_id}")
        if cached:
            return json.loads(cached)
        return self._load_session_db(session_id)

    def get_client_history(self, client_name: str) -> Optional[Dict]:
        """获取客户历史（优先 Redis）"""
        cached = self.redis.get(f"client:{client_name}")
        if cached:
            return json.loads(cached)
        return self._load_client_history_db(client_name)

    def update_session_result(self, session_id: str, bid_result: str = "",
                              review_feedback: str = ""):
        """更新会话结果（中标/丢单/审核反馈）"""
        try:
            from app.db.database import get_db
            with get_db() as db:
                cursor = db.cursor()
                cursor.execute(
                    """UPDATE session_memory SET
                       bid_result = %s, review_feedback = %s, updated_at = NOW()
                       WHERE session_id = %s""",
                    (bid_result, review_feedback, session_id),
                )
        except Exception:
            pass

    def _save_session_db(self, record: Dict):
        """保存会话到 PG"""
        try:
            from app.db.database import get_db
            with get_db() as db:
                cursor = db.cursor()
                cursor.execute(
                    """INSERT INTO session_memory
                       (session_id, user_id, client_name, industry, stage, context)
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (
                        record["session_id"],
                        record["user_id"],
                        record["client_name"],
                        record.get("industry", ""),
                        record.get("stage", ""),
                        json.dumps(record.get("context", {})),
                    ),
                )
        except Exception:
            pass

    def _load_session_db(self, session_id: str) -> Optional[Dict]:
        """从 PG 加载会话"""
        try:
            from app.db.database import get_db
            with get_db() as db:
                cursor = db.cursor()
                cursor.execute(
                    "SELECT * FROM session_memory WHERE session_id = %s ORDER BY created_at DESC LIMIT 1",
                    (session_id,),
                )
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception:
            return None

    def _load_client_history_db(self, client_name: str) -> Optional[Dict]:
        """从 PG 加载客户最近历史"""
        try:
            from app.db.database import get_db
            with get_db() as db:
                cursor = db.cursor()
                cursor.execute(
                    "SELECT * FROM session_memory WHERE client_name = %s ORDER BY created_at DESC LIMIT 1",
                    (client_name,),
                )
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception:
            return None