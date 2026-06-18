from app.skills.base import BaseSkill, SkillInput, SkillOutput, SkillRegistry


class MockInput(SkillInput):
    text: str


class MockOutput(SkillOutput):
    result: str = ""


class MockSkill(BaseSkill):
    name = "mock"
    description = "A mock skill for testing"

    def execute(self, input_data: MockInput) -> MockOutput:
        return MockOutput(result=input_data.text.upper())


def test_skill_execution():
    skill = MockSkill()
    result = skill.run(MockInput(text="hello"))
    assert result.success is True
    assert result.result == "HELLO"
    assert result.elapsed_ms > 0


def test_skill_registry():
    SkillRegistry.clear()
    skill = MockSkill()
    SkillRegistry.register(skill)
    found = SkillRegistry.get("mock")
    assert found is not None
    assert found.name == "mock"
    skills = SkillRegistry.list_all()
    assert "mock" in skills
    assert skills["mock"]["description"] == "A mock skill for testing"


def test_skill_error_handling():
    class FailingSkill(BaseSkill):
        name = "failing"
        description = "always fails"

        def execute(self, input_data):
            raise ValueError("test error")

    skill = FailingSkill()
    result = skill.run(MockInput(text="test"))
    assert result.success is False
    assert "test error" in result.error
    assert result.elapsed_ms > 0