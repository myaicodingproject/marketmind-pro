from jinja2 import Environment, FileSystemLoader
from typing import List
from enhanced_models import ReportSection, EnhancedReport


class TemplateService:
    def __init__(self):
        self.jinja_env = Environment(loader=FileSystemLoader('app/templates'))
    
    def render_section(self, section: ReportSection, format: str) -> str:
        template = self.jinja_env.get_template(f'section_{format}.html')
        return template.render(section=section)
    
    def render_report(self, report: EnhancedReport, format: str) -> str:
        template = self.jinja_env.get_template(f'report_{format}.html')
        return template.render(report=report)
    
    def get_css_files(self, format: str) -> List[str]:
        css_files = ['typography.css', 'colors.css', 'tables.css', 'sections.css', 'markdown.css']
        if format == 'pdf':
            css_files.append('print.css')
        return css_files