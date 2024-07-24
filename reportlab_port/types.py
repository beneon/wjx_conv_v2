from typing import TypeVar, List, TypedDict
from dataclasses import dataclass
from wjx_model.elems import AnswerField
from wjx_view.sub_question_entry import ReportContentElement


class ContentParagraph:
    def __init__(self,answer_field:AnswerField):
        self._answer_field = answer_field

    @property
    def question_title(self):
        return self._answer_field.question_title

    @property
    def paragraph_type(self):
        if self._answer_field.is_file_upload:
            return self._answer_field.attachment_type
        else:
            return 'text'


ReportContent = TypeVar('ReportContent',str,List[List[ReportContentElement]])


@dataclass
class ReportData:
    curriculum_title: str
    exp_title: str
    exp_type: str
    exp_num: int
    student_name: str
    student_id: str
    student_class: str
    report_content: ReportContent
