from wjx_model import Session
from wjx_view.template_parser import TemplateParser
import os

class DataTemplateIntegrator:
    def __init__(self,entry_path:str,session:Session):
        self.wd = entry_path
        self.session = session

    def _load_template(self):
        question_template_path = os.path.join(self.wd, 'question.md')
        assert os.path.exists(question_template_path), f'question.md not found in {self.wd}'
        with open(question_template_path, 'r', encoding='utf8') as _q_file:
            q_template_lines = _q_file.readlines()
        return TemplateParser(q_template_lines)