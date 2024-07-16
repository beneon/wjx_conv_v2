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

from wjx_model.answer_field_parser import AnswerField


class AttachmentParser:
    def __init__(self,attachment_path):
        self.wd = attachment_path
        assert os.path.exists(self.wd), f'{attachment_path} do not exists'
        self._file_list = os.listdir(self.wd)

    def __len__(self):
        return len(self._file_list)

    def __getitem__(self, item):
        if 0<=item<self.__len__():
            return AttachmentFileEntry(os.path.join(self.wd,self._file_list[item]))
        else:
            raise IndexError

    def _filter_attachment_entries(self,filter_str:AnswerField,match_attr_name:str):
        return [self.__getitem__(i) for i in range(len(self)) if getattr(self.__getitem__(i),match_attr_name)==filter_str]

    def get_attachments_via_serial_num(self,serial_num:AnswerField):
        if isinstance(serial_num.content,(int,float)):
            serial_num_str = str(serial_num.content)
        return self._filter_attachment_entries(serial_num_str,'serial_num')

    def get_attachments_via_user_id(self,user_id:str):
        return self._filter_attachment_entries(user_id.content,'user_id')


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
