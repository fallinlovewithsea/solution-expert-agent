from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel
import time


class SkillInput(BaseModel):
    """所有 Skill 的输入基类"""
    pass


class SkillOutput(BaseModel):
    """所有 Skill 的输出基类"""
    success: bool = True
    error: Optional[str] = None
    elapsed_ms: float = 0.0


class BaseSkill(ABC):
    """Skill 基类，定义统一接口"""

    name: str = "base"
    description: str = ""
    version: str = "1.0.0"

    @abstractmethod
    def execute(self, input_data: SkillInput) -> SkillOutput:
        """执行 Skill 核心逻辑"""
        pass

    def run(self, input_data: SkillInput) -> SkillOutput:
        """带计时和异常处理的执行入口"""
        start = time.time()
        try:
            result = self.execute(input_data)
            result.elapsed_ms = (time.time() - start) * 1000
            return result
        except Exception as e:
            return self._error_output(e, start)

    def _error_output(self, error: Exception, start: float) -> SkillOutput:
        return SkillOutput(
            success=False,
            error=str(error),
            elapsed_ms=(time.time() - start) * 1000,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
        }


class SkillRegistry:
    """Skill 注册中心"""

    _skills: Dict[str, BaseSkill] = {}

    @classmethod
    def register(cls, skill: BaseSkill):
        cls._skills[skill.name] = skill

    @classmethod
    def get(cls, name: str) -> Optional[BaseSkill]:
        return cls._skills.get(name)

    @classmethod
    def list_all(cls) -> Dict[str, Dict]:
        return {name: s.to_dict() for name, s in cls._skills.items()}

    @classmethod
    def clear(cls):
        cls._skills.clear()