from wjx_model import SessionData
from wjx_model.iters import AnswerEntry
from wjx_view.template_parser import TemplateParser, AfterView
import os

class DataTemplateIntegrator:
    def __init__(self,session_data:SessionData):
        self.session_data = session_data
        self.wd = session_data.wd
        self.template = self._load_template()
        self.after_views_list = [AfterView(self.template,ans_entry) for ans_entry in self.session_data]

    def __len__(self):
        return len(self.after_views_list)

    def __getitem__(self, item) -> AfterView:
        if 0<=item<self.__len__():
            return self.after_views_list[item]
        else:
            raise IndexError()

    def _load_template(self) -> TemplateParser:
        question_template_path = os.path.join(self.wd, 'question.md')
        assert os.path.exists(question_template_path), f'question.md not found in {self.wd}'
        with open(question_template_path, 'r', encoding='utf8') as _q_file:
            q_template_lines = _q_file.readlines()
        return TemplateParser(q_template_lines, self.session_data.exp_entry)

