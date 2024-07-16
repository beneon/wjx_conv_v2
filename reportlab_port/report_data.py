from wjx_model.data_file_parser import AnswerEntry
from wjx_view import TemplateParser
from wjx_model.type_dict_coll import ReportData

class ReportDataGen:
    def __init__(self,answer_entry:AnswerEntry, template:TemplateParser):
        self.answer_entry = answer_entry
        self.template = template
