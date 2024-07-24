from typing import Union, List
from dataclasses import dataclass
from wjx_model.elems import AnswerField


@dataclass
class ReportContentElement:
    main_text:str
    answer: Union[AnswerField,None]
    choices: Union[List[Union[str,int,float]],None]

    def _get_chosen_txt(self,data_input:Union[str,int,float]):
        if isinstance(data_input,int):
            assert self.choices is not None, f'index:{data_input} is given but self.choices is None'
            if 1<=data_input<=len(self.choices):
                # 问卷星的序号是从1开始计数的
                return self.choices[data_input-1]
            else:
                raise IndexError(f'data_input:{data_input} is out of choices index range')
        elif isinstance(data_input,(str,float)):
            return data_input
        else:
            raise Exception(f'data input {data_input} is not str or int')

    @property
    def _rc_element_type(self):
        if self.answer is None:
            return 'paragraph description'
        else:
            return self.answer.answer_field_type

    @property
    def content(self):
        if self._rc_element_type== 'paragraph description':
            return ""
        elif self.choices is None and self._rc_element_type== 'text':
            return self.answer.content
        elif self.choices and self._rc_element_type== 'text':
            return self._get_chosen_txt(self.answer.content)
        elif self._rc_element_type in ['image','document','archive']:
            return self.answer.attachment.file_path
        else:
            raise ValueError(f"{self._rc_element_type} 类型未定义")

    @property
    def content_type(self):
        if self._rc_element_type== 'image':
            return "image"
        elif self._rc_element_type=='archive' or self._rc_element_type=='document':
            return "link"
        elif self._rc_element_type== "paragraph description" or self._rc_element_type== "text":
            return "text"
        else:
            raise ValueError(f"{self._rc_element_type} 类型未定义")






class QuestionSimpleEntry:
    def __init__(self,question_main_txt:str,question_answer:AnswerField=None

                  ,question_choices:List[str]=None):
        self.main_text = question_main_txt.strip(" \n")
        self.answer = question_answer
        self.choices = question_choices
        self.join_with_sep = " "

    def get_report_content_element(self):
        assert self.answer is not None, f"answer data is not filled for {self.main_text}"
        return ReportContentElement(self.main_text,self.answer,self.choices)

    def generate_txt(self, data_input: Union[str, int,float]):
        if isinstance(data_input,(int,float)):
            data_input = str(data_input)
        return self.main_text + self.join_with_sep + data_input


class ParagraphDescEntry(QuestionSimpleEntry):
    def __init__(self,question_main_txt:str):
        super().__init__(question_main_txt)

    def generate_txt(self):
        return self.main_text

    def get_report_content_element(self):
        return ReportContentElement(self.main_text,None,None)



class FillerQuestionEntry(QuestionSimpleEntry):
    def __init__(self,question_main_txt:str,question_answer:Union[str,int]=None):
        super().__init__(question_main_txt,question_answer,None)




class FileUploadQuestionEntry(QuestionSimpleEntry):
    def __init__(self,question_main_txt:str):
        super().__init__(question_main_txt,None)


class SingleChoiceQuestionEntry(QuestionSimpleEntry):
    def __init__(self,question_main_txt:str,question_answer:Union[str,int]=None,question_choices:List[str]=None):
        super().__init__(question_main_txt,question_answer,question_choices)

    # def generate_txt(self,data_input:Union[str,int]):
    #     if isinstance(data_input,int):
    #         assert self.choices is not None, f'index:{data_input} is given but self.choices is None'
    #         if 1<=data_input<=len(self.choices):
    #             # 问卷星的序号是从1开始计数的
    #             return self.main_text+self.join_with_sep+self.choices[data_input-1]
    #         else:
    #             raise IndexError(f'data_input:{data_input} is out of choices index range')
    #     elif isinstance(data_input,(str,float)):
    #         return self.main_text+self.join_with_sep+data_input
    #     else:
    #         raise Exception(f'data input {data_input} is not str or int')
