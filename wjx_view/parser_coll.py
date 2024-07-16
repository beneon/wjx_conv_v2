import re
from wjx_view.utils_func import iter_mo, get_content_around_indics_tuples
from typing import List,Union

class QuestionSimpleEntry:
    def __init__(self,question_main_txt:str,question_answer:Union[str,int]=None,question_choices:List[str]=None):
        self.main_text = question_main_txt.strip(" \n")
        self.answer = question_answer
        self.choices = question_choices
        self.join_with_sep = " "

    def generate_txt(self, data_input: Union[str, int,float]):
        if isinstance(data_input,(int,float)):
            data_input = str(data_input)
        return self.main_text + self.join_with_sep + data_input


class ParagraphDescEntry(QuestionSimpleEntry):
    def __init__(self,question_main_txt:str):
        super().__init__(question_main_txt)

    def generate_txt(self):
        return self.main_text

class FillerQuestionEntry(QuestionSimpleEntry):
    def __init__(self,question_main_txt:str,question_answer:Union[str,int]=None):
        super().__init__(question_main_txt,question_answer,None)


class FileUploadQuestionEntry(QuestionSimpleEntry):
    def __init__(self,question_main_txt:str):
        super().__init__(question_main_txt,None)


class SingleChoiceQuestionEntry(QuestionSimpleEntry):
    def __init__(self,question_main_txt:str,question_answer:Union[str,int]=None,question_choices:List[str]=None):
        super().__init__(question_main_txt,question_answer,question_choices)

    def generate_txt(self,data_input:Union[str,int]):
        if isinstance(data_input,int):
            assert self.choices is not None, f'index:{data_input} is given but self.choices is None'
            if 1<=data_input<=len(self.choices):
                # 问卷星的序号是从1开始计数的
                return self.main_text+self.join_with_sep+self.choices[data_input-1]
            else:
                raise IndexError(f'data_input:{data_input} is out of choices index range')
        elif isinstance(data_input,(str,float)):
            return self.main_text+self.join_with_sep+data_input
        else:
            raise Exception(f'data input {data_input} is not str or int')


class QuestionTxtParserBase:
    ReSerialNum = re.compile('^\d+[\.,、]')
    ReFillerHolder = re.compile('__+')
    def __init__(self,question_txt):
        self.txt = self.remove_question_serial_num(question_txt)

    def __len__(self):
        return 1

    def __getitem__(self, item)->QuestionSimpleEntry:
        return QuestionSimpleEntry(self.txt)

    def generate_question_txt(self,data_input_list:List[Union[int,str]]=None):
        """

        :param data_input_list: List of data input entries for each sub question
        :return: str of merged question entries
        """
        if data_input_list is None:
            q_txt_list = [
                self.__getitem__(i).generate_txt("")
                for i in range(self.__len__())
            ]
        else:
            q_txt_list = [
                self.__getitem__(i).generate_txt(data_input_list[i])
                for i in range(self.__len__())
            ]
        return " ".join(q_txt_list)
    def remove_question_serial_num(self,txt):
        mo = self.ReSerialNum.match(txt)
        if mo:
            _,serial_num_ends_at = mo.span()
            return txt[serial_num_ends_at:].strip(" \n")
        else:
            return txt.strip(" \n")


class FillerQuestion(QuestionTxtParserBase):
    def __init__(self,question_txt:str):
        super().__init__(question_txt)
        self._q_entry_indics_list = self._get_filler_list()

    def __len__(self):
        return len(self._q_entry_indics_list)

    def __getitem__(self, item):
        if 0<=item<self.__len__():
            txt_start_index, txt_end_index = self._q_entry_indics_list[item]
            q_entry_main_txt = self.txt[txt_start_index:txt_end_index]
            return FillerQuestionEntry(q_entry_main_txt)
        else:
            raise IndexError(f'{item} out of bound')

    def _get_filler_list(self):
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
        super().__init__(question_txt)
        self.reChoice = re.compile(r'[○\-]\s+(.*)')

    def __getitem__(self, item):
        assert item==0, '单选题每题应该只有一个问题'
        main_txt, choice_content_list = self._get_main_txt_and_choice_list()
        return SingleChoiceQuestionEntry(main_txt,question_choices=choice_content_list)

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

    def __getitem__(self, item):
        return FileUploadQuestionEntry(self.txt)


class ParagraphDesc(QuestionTxtParserBase):
    def __init__(self,question_txt:str):
        super().__init__(question_txt)

    def __len__(self):
        return 0

    def __getitem__(self, item):
        return ParagraphDescEntry(self.txt)

    def generate_question_txt(self):
        return self.__getitem__(0).generate_txt()

