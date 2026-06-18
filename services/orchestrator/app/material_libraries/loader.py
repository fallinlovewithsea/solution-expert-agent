import json
import os
from pathlib import Path
from typing import List, Dict


class MaterialLibraryLoader:
    """从飞书文件夹拉取文档，初始化 8 大物料库"""

    DATA_DIR = Path("/data/material-libraries")

    def __init__(self):
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)

    def load_all_from_feishu(self, folder_token: str):
        """从飞书文件夹拉取全部文档并构建物料库"""
        docs = self._fetch_all_docs(folder_token)
        for doc in docs:
            self._classify_and_store(doc)
        return len(docs)

    def _fetch_all_docs(self, folder_token: str) -> List[Dict]:
        """递归拉取飞书文件夹中所有文档内容"""
        import subprocess
        import json as j

        result = subprocess.run(
            [
                "lark-cli", "drive", "files", "list",
                "--params", j.dumps({"folder_token": folder_token, "page_size": 200}),
                "--format", "json", "--as", "user",
            ],
            capture_output=True, text=True,
        )
        data = j.loads(result.stdout)
        docs = []

        for f in data.get("data", {}).get("files", []):
            if f["type"] == "folder":
                docs.extend(self._fetch_all_docs(f["token"]))
            elif f["type"] == "docx":
                content = self._fetch_docx(f["token"])
                docs.append({
                    "name": f["name"],
                    "type": "docx",
                    "token": f["token"],
                    "content": content,
                    "url": f["url"],
                })
            elif f["type"] == "slides":
                content = self._fetch_slides(f["token"])
                docs.append({
                    "name": f["name"],
                    "type": "slides",
                    "token": f["token"],
                    "content": content,
                    "url": f["url"],
                })
        return docs

    def _fetch_docx(self, token: str) -> str:
        import subprocess
        import json as j
        result = subprocess.run(
            ["lark-cli", "docs", "+fetch", "--api-version", "v2",
             "--doc", token, "--doc-format", "markdown", "--as", "user"],
            capture_output=True, text=True,
        )
        data = j.loads(result.stdout)
        return data.get("data", {}).get("document", {}).get("content", "")

    def _fetch_slides(self, token: str) -> str:
        import subprocess
        import json as j
        import re
        result = subprocess.run(
            ["lark-cli", "slides", "xml_presentations", "get",
             "--as", "user", "--params", j.dumps({"xml_presentation_id": token}),
             "--format", "json"],
            capture_output=True, text=True,
        )
        data = j.loads(result.stdout)
        content = data.get("data", {}).get("xml_presentation", {}).get("content", "")
        texts = re.findall(r"<p[^>]*>(.*?)</p>", content)
        return " ".join(re.sub(r"<[^>]+>", "", t) for t in texts if t.strip())

    def _classify_and_store(self, doc: Dict):
        """根据文档内容分类存入对应物料库"""
        content = doc["content"]
        name = doc["name"]

        if any(kw in name for kw in ["通案", "行业", "策略"]):
            self._save_to_json("industry_strategy", name, content)
        elif any(kw in name for kw in ["案例", "case"]):
            self._save_to_json("case_labels", name, content)
        elif any(kw in name for kw in ["产品", "能力", "解决方案"]):
            self._save_to_json("product_solution", name, content)
        elif any(kw in name for kw in ["竞品", "对标"]):
            self._save_to_json("competitor_analysis", name, content)
        elif any(kw in name for kw in ["增长", "模型"]):
            self._save_to_json("growth_model", name, content)
        elif any(kw in name for kw in ["复盘", "review"]):
            self._save_to_json("proposal_review", name, content)

        # L1: 保存原始文档
        self._save_raw_document(doc)

        # L2: 触发知识蒸馏
        self._trigger_distill(doc)

    def _save_to_json(self, library: str, name: str, content: str):
        import json as j
        lib_dir = self.DATA_DIR / library
        lib_dir.mkdir(parents=True, exist_ok=True)
        filepath = lib_dir / f"{name}.json"
        filepath.write_text(j.dumps({"name": name, "content": content}, ensure_ascii=False))

    def _save_raw_document(self, doc: Dict):
        """保存原始文档到 L1 raw_documents 表"""
        try:
            from app.db.database import get_db
            with get_db() as db:
                cursor = db.cursor()
                cursor.execute(
                    """INSERT INTO raw_documents
                       (doc_name, doc_type, source_folder, feishu_token, feishu_url, content)
                       VALUES (%s, %s, %s, %s, %s, %s)
                       ON CONFLICT DO NOTHING""",
                    (
                        doc.get("name", ""),
                        doc.get("type", ""),
                        doc.get("source_folder", ""),
                        doc.get("token", ""),
                        doc.get("url", ""),
                        doc.get("content", ""),
                    ),
                )
        except Exception:
            pass

    def _trigger_distill(self, doc: Dict):
        """触发知识蒸馏流程"""
        try:
            from app.knowledge.distiller import KnowledgeDistiller
            from app.vector_store.client import VectorStore
            from app.db.database import get_db

            with get_db() as db:
                distiller = KnowledgeDistiller(
                    vector_store=VectorStore(),
                    db=db,
                )
                distiller.distill_document(doc)
        except Exception:
            pass