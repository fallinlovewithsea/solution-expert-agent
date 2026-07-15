from pydantic import BaseModel, Field


class ExportResult(BaseModel):
    success: bool = False
    outputs: dict = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)


class ProposalExporter:
    """Render an approved proposal into requested formats."""

    SUPPORTED_FORMATS = {"slides", "docx", "pptx"}

    def export(self, proposal_spec: dict, brief: dict, output_formats: list[str]) -> ExportResult:
        requested = list(dict.fromkeys(output_formats or ["pptx"]))
        invalid = [item for item in requested if item not in self.SUPPORTED_FORMATS]
        if invalid:
            return ExportResult(errors=[f"不支持的输出格式：{', '.join(invalid)}"])

        try:
            from skills.s8_format_output import S8FormatOutput, FormatOutputInput

            result = S8FormatOutput().run(FormatOutputInput(
                slides=proposal_spec.get("slides", []),
                brand_assets=brief.get("brand_assets", {}) or {},
                output_formats=requested,
                brand_name=brief.get("client_name", "品牌"),
                proposal_title=proposal_spec.get("title", "小红书营销解决方案"),
            ))
        except Exception as exc:
            return ExportResult(errors=[f"输出工具执行失败：{exc}"])

        outputs = {
            "slides_url": getattr(result, "slides_url", None) or "",
            "docx_url": getattr(result, "docx_url", None) or "",
            "pptx_path": getattr(result, "pptx_path", None) or "",
        }
        errors = []
        for key, value in outputs.items():
            if "placeholder" in value:
                outputs[key] = ""
                errors.append(f"{key} 未生成：外部输出服务不可用")

        generated = any(outputs.values())
        if not generated and not errors:
            errors.append("未生成任何输出文件")
        return ExportResult(success=generated, outputs=outputs, errors=errors)
