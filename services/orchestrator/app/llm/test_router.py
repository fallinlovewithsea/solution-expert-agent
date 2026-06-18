import os
from unittest.mock import patch


def test_get_light_llm():
    from app.llm.router import get_llm
    llm = get_llm("light")
    assert llm is not None


def test_get_heavy_llm_fallback():
    from app.llm.router import get_llm
    with patch.dict(os.environ, {"CLOUD_LLM_PROVIDER": "ollama"}, clear=False):
        llm = get_llm("heavy")
        assert llm is not None