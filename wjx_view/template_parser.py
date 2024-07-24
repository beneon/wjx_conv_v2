import re
from typing import List, Tuple, TypeVar
from wjx_model.iters import AnswerEntry
from wjx_model.type_dict_coll import ExpEntry
from reportlab_port import ReportData
from wjx_view.parser_coll import FillerQuestion, FileUploadQuestion, SingleChoiceQuestion, ParagraphDesc
from wjx_view.sub_question_entry import ReportContentElement
from wjx_view.utils_func import get_tuples_of_neighbouring_indices


AKQ = TypeVar('AKQ',FillerQuestion,FileUploadQuestion,SingleChoiceQuestion,ParagraphDesc)


class TemplateParser:
    ReQuestionStart = re.compile('^>\s')
    ReQuestionTypeInd = re.compile(r'\[([^\d#]*)\]')
    # 默认不现实模板中的答案（答案一行用//开头）
    NOANSWERDISP = True
    def __init__(self,template_lines:List[str],exp_entry:ExpEntry):
        self.template_lines = template_lines
        self.exp_entry = exp_entry
        if self.NOANSWERDISP:
            self.template_lines = [l for l in self.template_lines if l[:2]!="//"]
        # 首先将模板内容分而治之
        self._q_title_line_indics = self._get_question_title_line_indics()
        self._q_title_s_e_indics_tuples = get_tuples_of_neighbouring_indices(self._q_title_line_indics)
        self.q_txt_list = [self._combine_lines_for_1_question(*tp) for tp in self._q_title_s_e_indics_tuples]
        # 这里除了每个问题生成一个QuestionParser，还记录了每个问题里内含的子问题数量，这对于多项填空很重要
        self._question_parsers, self._question_sub_entries_num_list = self._get_question_entries_and_num()

    def __len__(self):
        return len(self.q_txt_list)

    def _gen_q_parser(self,item):
        if 0<=item<self.__len__():
            q_txt = self.q_txt_list[item]
            q_type_ind = self._question_type_extract(q_txt)
            if q_type_ind=='填空题':
                return FillerQuestion(q_txt)
            if q_type_ind=='矩阵文本题':
                return FillerQuestion(q_txt)
            elif q_type_ind=='单选题':
                return SingleChoiceQuestion(q_txt)
            elif q_type_ind=='上传文件题':
                return FileUploadQuestion(q_txt)
            elif q_type_ind=='段落说明':
                return ParagraphDesc(q_txt)
            else:
                raise Exception(f'q_type_ind:{q_type_ind} is not prepared')
        else:
            raise IndexError('item idx out of range')

    def __getitem__(self, item:int)->AKQ:
        """

        :param item:
        :return: tuple of q parser and int(问题包含多少子问题)
        """
        if 0<=item<self.__len__():
            return self._question_parsers[item]
        else:
            raise IndexError('item idx out of range')

    def generate_list_of_rc_list(self) -> List[List[ReportContentElement]]:
        return [
            akq.generate_report_content_list() for akq in self
        ]

    def _get_question_entries_and_num(self) -> Tuple[List[AKQ],List[int]]:
        question_parsers = [self._gen_q_parser(i) for i in range(self.__len__())]
        entries_num_list = [len(e) for e in question_parsers]
        return question_parsers, entries_num_list

    def _question_type_extract(self,txt:str):
        # txt = txt.replace('\n',' ')
        mo = self.ReQuestionTypeInd.search(txt)
        if mo:
            q_type_ind = mo.group(1)
        else:
            # A big if
            q_type_ind = '段落说明'
        return q_type_ind


    def _get_question_title_line_indics(self):
        list_index_of_line_of_question_title = list()
        for index, line in enumerate(self.template_lines):

            mo = self.ReQuestionStart.match(line)
            if mo:
                list_index_of_line_of_question_title.append(index)
        return list_index_of_line_of_question_title

    def _combine_lines_for_1_question(self, index_start, index_next_start):
        lines = self.template_lines[index_start:index_next_start]
        txt = ''.join(lines)
        # remove the leading ">\s"
        txt = txt[2:]
        return txt


class AfterView:
    def __init__(self,template_parser:TemplateParser,answer_entry:AnswerEntry):
        """
        这个class负责将一个answer entry转换成经template parser处理过以后的数据形式
        这个类承上启下，要负责输出reportlab能够使用的数据
        :param template_parser:
        :param answer_entry:
        """
        self.template_parser = template_parser
        self.answer_entry = answer_entry
        self._batch_send_answer_data_input_list()
        self.list_of_rc_list = self.template_parser.generate_list_of_rc_list()

    def generate_report_data(self) -> ReportData:
        return ReportData(
            curriculum_title=self.template_parser.exp_entry['curriculum_title'],
            exp_title=self.template_parser.exp_entry['exp_title'],
            exp_type=self.template_parser.exp_entry['exp_type'],
            exp_num=self.template_parser.exp_entry['exp_num'],
            student_name = self.answer_entry.student_name,
            student_id=self.answer_entry.student_id,
            student_class=self.answer_entry.student_class_name,
            report_content=self.list_of_rc_list
        )

    def _batch_send_answer_data_input_list(self):
        return [
            self._send_answer_data_input_list(item,self.answer_entry)
            for item in range(len(self.template_parser))
        ]

    def _send_answer_data_input_list(self,item,ans_entry:AnswerEntry):
        assert 0<=item<len(self.template_parser)
        start_id, end_id = self._get_q_answer_id_start_end(item)
        # answers_data_input_items_list = list(range(start_id,end_id))
        answers_data_input_list = [
            ans_entry.get_ans_field_via_question_id(i)
            for i in range(start_id,end_id)
        ]
        t_parser:AKQ = self.template_parser._question_parsers[item]
        if isinstance(t_parser,ParagraphDesc):
            t_parser.update_question_parser()
        elif isinstance(t_parser,(FillerQuestion,FileUploadQuestion,SingleChoiceQuestion)):
            # 对于文件上传问题，需要和AnswerParser做更多的交流，这里可以通过
            # answers_data_input_items_list
            t_parser.update_question_parser(answers_data_input_list)
        else:
            raise ValueError(f'instance of question is {type(t_parser)}, not part of AKQ')

    def _get_q_answer_id_start_end(self,item):
        if item>0:
            start = sum(self.template_parser._question_sub_entries_num_list[:item])

        else:
            start = 0
        end = start + self.template_parser._question_sub_entries_num_list[item]
        return start, end