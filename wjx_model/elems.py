"""
文件附件内容处理工具
从AnswerParser获取数据user_id和serial_num两个数据
从datafile的文件名获取问卷id <- 这一项功能意义不大，不过已经在Session里用session_id做了
本文件中包含AttachmentParser和AttachmentEntry两个部分。
- attachment parser 负责针对一个session，找到对应文件夹中所有的附件文档
- 每一个附件文档用一个attachment entry表示
"""

import os
import re
from typing import Union
from urllib.parse import urlparse


class AttachmentFileEntry:
    img_ext_list = ['.jpg','.jpeg','.bmp','.png','.gif']
    doc_ext_list = ['.doc','.docx','.ppt','.pptx','.txt','.pdf','.xls','.xlsx']
    archive_ext_list = ['.zip','.rar']
    # 虽然我讨厌regex（因为过几个月根本看不明白），这里还是做个验证
    # 问卷星导出的附件文件至少应该包括2个下划线作为分界
    ReAttachmentFileName = re.compile(r'.*_.*_')
    ReSerialNum = re.compile(r'序号(\d+)')
    def __init__(self,file_path):
        assert os.path.exists(file_path)
        self.file_path = file_path
        self._filename, self._file_ext = os.path.splitext(os.path.split(self.file_path)[-1])
        mo = self.ReAttachmentFileName.match(self._filename)
        if mo:
            self._filename_components_list = self._filename.split('_')
        else:
            raise Exception(f'{file_path}指向文件不符合附件命名规则')

    @property
    def serial_num(self):
        raw_txt = self._filename_components_list[0]
        mo = self.ReSerialNum.match(raw_txt)
        if mo:
            return mo.group(1)
        else:
            raise Exception(f'{raw_txt} 不符合序号格式')

    @property
    def user_id(self):
        return self._filename_components_list[1]

    @property
    def question_title(self):
        return self._filename_components_list[2]

    @property
    def attachment_type(self):
        if self._file_ext in self.img_ext_list:
            return 'image'
        elif self._file_ext in self.doc_ext_list:
            return 'document'
        elif self._file_ext in self.archive_ext_list:
            return 'archive'
        elif self._file_ext=="":
            return 'folder'
        else:
            # 对于预计类型以外的文件，还是留这个报错的口子
            # 照理来说通过在问卷星里加入格式限制可以规避特殊类型文件
            raise Exception(f'{self._file_ext} in {self._filename} is not a predefined type for attachment')


class AnswerField:
    ReIsURL = re.compile(r'https://alifile.sojump.cn/.*')
    ReSerialNum = re.compile('^\d+[\.,、]')
    def __init__(self,q_title:str,content:Union[str,int,float]):
        self.content = content
        self.question_title = self.remove_question_serial_num(q_title)
        self.attachment = None
        self.attachment_type = None
        url_parsed = self.parse_url()
        if url_parsed:
            self.is_file_upload = True
        else:
            self.is_file_upload = False

    def __str__(self):
        if isinstance(self.content,(int,float)):
            return f"{self.content}"
        elif isinstance(self.content,str):
            return self.content
        else:
            raise ValueError(f"{self.question_title} 的值类型为：{type(self.content)}")

    def remove_question_serial_num(self,txt):
        mo = self.ReSerialNum.match(txt)
        if mo:
            _,serial_num_ends_at = mo.span()
            return txt[serial_num_ends_at:]
        else:
            return txt

    def update_url_to_file_attachment(self,attachment:AttachmentFileEntry):
        self.attachment = attachment
        self.attachment_type = attachment.attachment_type

    def parse_url(self):
        if isinstance(self.content,(int,float)):
            return None
        mo = self.ReIsURL.match(self.content)
        if mo:
            parse_content = urlparse(self.content)
            return parse_content.path
        else:
            return None

    @property
    def abbrev_question_title(self):
        return self.question_title[:15]

    @property
    def answer_field_type(self):
        if not self.is_file_upload:
            return 'text'
        elif self.attachment_type:
            return self.attachment_type
        else:
            # 如果数据文件比较新，附件比较旧，可能新提交的人的文件在附件这里没有文件，这块就会报错
            raise ValueError('answer_field_type should be called after update_url_file_attachment is called')
