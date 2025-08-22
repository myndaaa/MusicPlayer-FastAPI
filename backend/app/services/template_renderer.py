from pathlib import Path


class TemplateRenderer:
    """file-based template renderer using Python format placeholders."""

    def render(self, template_path: str, context: dict) -> str:
        template_file = Path(template_path)
        content = template_file.read_text(encoding="utf-8")
        return content.format(**context)


