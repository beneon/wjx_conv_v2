import re
from typing import TypeVar
from wjx_view.sub_question_entry import QuestionSimpleEntry, ParagraphDescEntry, FillerQuestionEntry, \
    FileUploadQuestionEntry, SingleChoiceQuestionEntry, ReportContentElement
from wjx_view.utils_func import iter_mo, get_content_around_indics_tuples
from wjx_model.elems import AnswerField
from typing import List,Union

QE = TypeVar('QE',QuestionSimpleEntry,ParagraphDescEntry,FillerQuestionEntry,FileUploadQuestionEntry,SingleChoiceQuestionEntry)


class QuestionTxtParserBase:
    ReSerialNum = re.compile('^\d+[\.,、]')
    ReFillerHolder = re.compile('__+')
    def __init__(self,question_txt):
        self.txt = self.remove_question_serial_num(question_txt)
        self.q_e_list = self._get_q_e_list()


    def __len__(self):
        return 1

    def _get_q_e_list(self) -> List[QE]:
        return [self._get_q_s_entry(i) for i in range(self.__len__())]

    def _get_q_s_entry(self,item) -> QE:
        return QuestionSimpleEntry(self.txt)

    def __getitem__(self, item) -> QE:
        if 0<=item<len(self):
            return self.q_e_list[item]
        else:
            raise IndexError()

    def generate_report_content_list(self) -> List[ReportContentElement]:
        return [e.get_report_content_element() for e in self]

    def update_question_parser(self,answers_fields_list:List[AnswerField]):
        assert len(answers_fields_list)==self.__len__(), f'答案answer entry数量{len(answers_fields_list)}需要和子问题数量{len(self)}一致'
        for i,q_e in enumerate(self):
            q_e.answer = answers_fields_list[i]

    def remove_question_serial_num(self,txt):
        mo = self.ReSerialNum.match(txt)
        if mo:
            _,serial_num_ends_at = mo.span()
            return txt[serial_num_ends_at:]
        else:
            return txt

    # def generate_question_txt(self,data_input_list:List[Union[int,str]]=None):
    #     """
    #     DEPRECATE
    #     :param data_input_list: List of data input entries for each sub question
    #     :return: str of merged question entries
    #     """
    #     if data_input_list is None:
    #         q_txt_list = [
    #             self.__getitem__(i).generate_txt("")
    #             for i in range(self.__len__())
    #         ]
    #     else:
    #         q_txt_list = [
    #             self.__getitem__(i).generate_txt(data_input_list[i])
    #             for i in range(self.__len__())
    #         ]
    #     raise DeprecationWarning('this function is deprecated')
    #     return " ".join(q_txt_list)


class FillerQuestion(QuestionTxtParserBase):
    def __init__(self,question_txt:str):
        self.txt = self.remove_question_serial_num(question_txt)
        self._q_entry_indics_list = self._get_filler_list()
        self.q_e_list = self._get_q_e_list()

    def __len__(self):
        return len(self._q_entry_indics_list)

    def _get_q_s_entry(self,item) -> FillerQuestionEntry:
        if 0<=item<self.__len__():
            txt_start_index, txt_end_index = self._q_entry_indics_list[item]
            q_entry_main_txt = self.txt[txt_start_index:txt_end_index]
            return FillerQuestionEntry(q_entry_main_txt)
        else:
            raise IndexError(f'{item} out of bound')

    def _get_filler_list(self):
        """
        根据填空符__找到符号左边文字的函数。
        :return:
        """
        if self.ReFillerHolder.search(self.txt):
            mo_pos_list = iter_mo(self.txt,self.ReFillerHolder)
            pos_starts, pos_ends = list(zip(*mo_pos_list))
            pos_starts = list(pos_starts)
            pos_ends = list(pos_ends)
            question_entry_indics_list = get_content_around_indics_tuples(pos_starts,pos_ends)
            return question_entry_indics_list
        else:
            raise Exception(f'filler holder regex match none: {self.txt}')


class SingleChoiceQuestion(QuestionTxtParserBase):
    def __init__(self,question_txt:str):
        self.reChoice = re.compile(r'[○\-]\s+(.*)')
        super().__init__(question_txt)

    def _get_q_e_list(self) -> List[SingleChoiceQuestionEntry]:
        return [self._get_q_s_entry(0)]

    def _get_q_s_entry(self,item) -> SingleChoiceQuestionEntry:
        main_txt, choice_content_list = self._get_main_txt_and_choice_list()
        return SingleChoiceQuestionEntry(main_txt, question_choices=choice_content_list)

    def __getitem__(self, item) -> SingleChoiceQuestionEntry:
        if 0<=item<self.__len__():
            return self.q_e_list[item]
        else:
            raise IndexError()

    def _get_main_txt_and_choice_list(self):
        mo_choice_list = iter_mo(self.txt,self.reChoice)
        main_txt_ends_index = mo_choice_list[0][0]
        choice_content_list = [self._get_choice_content(*indics_tuple) for indics_tuple in mo_choice_list]
        return self.txt[:main_txt_ends_index], choice_content_list

    def _get_choice_content(self,start_ind,end_ind):
        return self.txt[start_ind:end_ind]

class FileUploadQuestion(QuestionTxtParserBase):
    def __init__(self,question_txt:str):
        super().__init__(question_txt)

    def _get_q_e_list(self):
        return [FileUploadQuestionEntry(self.txt)]

    def __getitem__(self, item):
        if 0<=item<len(self):
            return self.q_e_list[item]
        else:
            raise IndexError()


class ParagraphDesc(QuestionTxtParserBase):
    def __init__(self,question_txt:str):
        super().__init__(question_txt)

    def __len__(self):
        return 0

    def _get_q_e_list(self):
        return [ParagraphDescEntry(self.txt)]

    def __getitem__(self, item):
        if item==0:
            return self.q_e_list[item]
        else:
            raise IndexError()

    def update_question_parser(self,answers_fields_list=None):
        assert answers_fields_list is None, '段落说明不应该有答案数据'
        pass

    # def generate_question_txt(self):
    #     """
    #     DEPRECATE
    #     :return:
    #     """
    #     raise DeprecationWarning('this function is deprecated')
    #     return self.__getitem__(0).generate_txt()

