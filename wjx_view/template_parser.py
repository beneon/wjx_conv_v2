import re
from typing import List
from wjx_model.data_file_parser import AnswerEntry
from wjx_view.parser_coll import FillerQuestion, FileUploadQuestion, SingleChoiceQuestion, ParagraphDesc

from wjx_view.utils_func import get_tuples_of_neighbouring_indices

class TemplateParser:
    ReQuestionStart = re.compile('^>\s')
    ReQuestionTypeInd = re.compile(r'\[(.*)\]')
    NOANSWERDISP = True
    def __init__(self,template_lines:List[str]):
        self.template_lines = template_lines
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

    def __getitem__(self, item):
        if 0<=item<self.__len__():
            q_txt = self.q_txt_list[item]
            q_type_ind = self._question_type_extract(q_txt)
            if q_type_ind=='填空题':
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

    def generate_template_output(self):
        # 负责call _batch_send_answer_data_input_list让每个qparser运行generate question txt，整合结果
        pass

    def _get_question_entries_and_num(self):
        question_parsers = [self.__getitem__(i) for i in range(self.__len__())]
        entries_num_list = [len(e) for e in question_parsers]
        return question_parsers, entries_num_list

    def _batch_send_answer_data_input_list(self, ans_entry:AnswerEntry):
        return [
            self._send_answer_data_input_list(item,ans_entry)
            for item in range(self.__len__())
        ]

    def _send_answer_data_input_list(self,item,ans_entry:AnswerEntry):
        start_id, end_id = self._get_q_answer_id_start_end(item)
        # answers_data_input_items_list = list(range(start_id,end_id))
        answers_data_input_list = [
            ans_entry.get_entry_value_via_question_id(i)
            for i in range(start_id,end_id)
        ]
        t_parser = self.__getitem__(item)
        if isinstance(t_parser,ParagraphDesc):
            return t_parser.generate_question_txt()
        if isinstance(t_parser,FileUploadQuestion):
            # 对于文件上传问题，需要和AnswerParser做更多的交流，这里可以通过
            # answers_data_input_items_list
            pass
        else:
            return t_parser.generate_question_txt(answers_data_input_list)

    def _get_q_answer_id_start_end(self,item):
        if item>0:
            start = sum(self._question_sub_entries_num_list[:item])

        else:
            start = 0
        end = start + self._question_sub_entries_num_list[item]
        return start, end

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