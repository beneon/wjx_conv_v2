import os.path
from typing import List,TypeVar
from wjx_view.sub_question_entry import ReportContentElement
from reportlab.platypus import Paragraph, Image
from PIL import Image as P_Image
import pathlib

P = TypeVar('P',Paragraph,Image)

class RCElementProc:
    def __init__(self,report_content:ReportContentElement,styles:dict):
        self._report_content = report_content
        self.styles = styles
        self.content_type = report_content.content_type
        self.main_text = report_content.main_text
        self.content = report_content.content

    def get_flowables(self) -> List[P]:
        if self.content_type=='image':
            return self._get_image_flowable()
        elif self.content_type=='text':
            return self._get_text_flowable()
        elif self.content_type=='link':
            return self._get_link_flowable()
        else:
            raise ValueError('only prepared for text or image')

    def _get_text_flowable(self):
        if self.main_text[-1]=='\n':
            main_text_paragraph = Paragraph(self.main_text,self.styles['maintext_left'])
            content_text_paragraph = [
                Paragraph(s,self.styles['content_left']) for
                s in self.content.split('\n')
            ]
            return main_text_paragraph+content_text_paragraph
        else:
            return [Paragraph(f"{self.main_text}:<u>{self.content}</u>",self.styles['content_left'])]

    def _get_image_flowable(self):
        image_path = os.path.abspath(self.content)
        assert os.path.exists(image_path)
        image_platypus = Image(image_path)
        ori_width = image_platypus.imageWidth
        ori_height = image_platypus.imageHeight
        ratio_w = 400/ori_width
        ratio_h = 300/ori_height
        ratio = min(ratio_w,ratio_h)
        return [
            Paragraph(self.main_text,self.styles['maintext_left']),
            Image(image_path,round(ori_width*ratio),round(ori_height*ratio))
        ]

    def _get_link_flowable(self):
        link_path = os.path.abspath(self.content)
        link_path = pathlib.Path(link_path).as_uri()
        return [
            Paragraph(self.main_text,self.styles['maintext_left']),
            Paragraph(f"<a href='{link_path}'>文件链接</a>",self.styles['content_left'])
        ]

class QuestionProc:
    def __init__(self,rce_list:List[ReportContentElement],styles:dict):
        self.rce_list = rce_list
        self.styles = styles
        self.rce_converter_list = [e for e in self]

    def get_combined_flowables(self):
        rst_list = []
        for rce_conv_flowables in self.rce_converter_list:
            rst_list=rst_list+rce_conv_flowables
        return rst_list

    def __len__(self):
        return len(self.rce_list)

    def __getitem__(self,item) -> List[P]:
        if 0<=item<self.__len__():
            rce:ReportContentElement = self.rce_list[item]
            rce_proc = RCElementProc(rce,self.styles)
            return rce_proc.get_flowables()
        else:
            raise IndexError()