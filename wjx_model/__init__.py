import yaml
import pandas as pd
import os
from typing import List
from wjx_model.iters import StudentInfoIter,AnswerEntryIter, StudentInfo, AnswerEntry, AttachmentParser
from wjx_model.type_dict_coll import CourseConfigYaml, ExpEntry


"""
curriculum 是一整门课程的管理类，下设多个Session类，每个session对应一次问卷星问卷。

"""


class Curriculum:
    curriculum_config_filename = 'config.yaml'
    def __init__(self,wd:str):
        self.wd = wd
        assert os.path.exists(wd), f'working dir:{wd} do not exist'
        self.config_of_course: CourseConfigYaml = self._load_config_data()
        df_student_data = pd.read_excel(
            os.path.join(self.wd,self.config_of_course['student_data'])
        )
        self.student_data = StudentInfoIter(df_student_data)

    def __len__(self):
        return len(self.config_of_course['entries'])

    def __getitem__(self, item):
        if 0<=item<self.__len__():
            entry_dict: ExpEntry = self.config_of_course['entries'][item]
            entry_dict['curriculum_title'] = self.config_of_course['curriculum_title']
            session_wd = os.path.join(self.wd,f"exp{entry_dict['exp_num']:02d}")
            assert os.path.exists(session_wd), f'session wd:{session_wd} do not exist'
            return Session(session_wd,self.student_data,entry_dict)
        else:
            raise IndexError(f'id:{item} is out of bound')

    def _load_config_data(self):
        with open(os.path.join(self.wd,self.curriculum_config_filename),'r',encoding='utf8') as _hdlr:
            return yaml.safe_load(_hdlr)


class Session:
    def __init__(self,entry_path:str,student_data:StudentInfoIter,entry_dict:ExpEntry):
        self.wd = entry_path
        self.exp_entry = entry_dict
        self.student_data = student_data
        self.answers, self.session_id = self._load_answers()
        self.attachment_folder = self._get_attachment_folder(self.session_id)
        if self.attachment_folder:
            self.attachment_parser = AttachmentParser(os.path.join(self.wd, self.attachment_folder))
            self._update_answers_file_upload_fields()

    def generate_session_data(self):
        return SessionData(self.student_data,self.answers,self.wd,self.exp_entry)

    def _update_answers_file_upload_fields(self):
        """
        遍历一个问卷文件中的所有答案
        :return:
        """
        for answer_entry in self.answers:
            self._update_answer_fu_fields(answer_entry)

    def _update_answer_fu_fields(self,answer_entry:AnswerEntry):
        """
        遍历related attachments（序列号与当前答案序列号相同），从answer entry中找到与之对应的answer field，call its `update_url_to_file_attachment` 方法

        :param answer_entry:
        :return:
        """
        related_attachments = self.attachment_parser.get_attachments_via_serial_num(answer_entry.serial_num)
        for attachment in related_attachments:
            related_answer_field_index_list = [e for e in answer_entry if e.abbrev_question_title==attachment.question_title]
            if len(related_answer_field_index_list)==1:
                related_answer_field_index_list[0].update_url_to_file_attachment(attachment)
            elif len(related_answer_field_index_list)==0:
                raise Exception(f'found no answer field with q_title:{attachment.question_title}, candidate answer_fields:{" ".join([e.abbrev_question_title for e in answer_entry])}')
            else:
                raise Exception(f'found multiple answer fields with q_title{attachment.question_title}')

    def _get_attachment_folder(self,session_id):
        wd_content_list = os.listdir(self.wd)
        attachment_folder = [f for f in wd_content_list if os.path.splitext(f)[-1]=="" and session_id in f]
        if len(attachment_folder)==0:
            return None
        elif len(attachment_folder)==1:
            return attachment_folder[0]
        else:
            raise Exception('multiple attachemnt folder found')

    def _load_answers(self):
        xls_file_list = [f for f in os.listdir(self.wd) if os.path.splitext(f)[-1]=='.xlsx']
        assert len(xls_file_list)==1, f'when loading answers, {len(xls_file_list)} xlsx files were found'
        filename_splits = xls_file_list[0].split('_')
        session_id = filename_splits[0]
        df_answer_data = pd.read_excel(os.path.join(self.wd,xls_file_list[0]))
        return AnswerEntryIter(df_answer_data), session_id


class SessionData:
    def __init__(self, student_info:StudentInfoIter, answer_entries:AnswerEntryIter,wd:str, exp_entry:ExpEntry):
        """
        1. 将student data和问卷数据交叉比对，获得每一个学生的基本信息
        2. 将session按照AnswerEntry以及下属的AnswerField组织起来。（iterable）
        """
        self.student_info = student_info
        self.answer_entries = answer_entries
        self.exp_entry = exp_entry
        assert os.path.exists(wd)
        self.wd = wd
        self.update_answer_entries_with_student_info()
        pass

    def __len__(self):
        return len(self.answer_entries)

    def __getitem__(self, item):
        if 0<=item<self.__len__():
            return self.answer_entries[item]
        else:
            raise IndexError

    def update_answer_entries_with_student_info(self):
        """
        looper
        :return:
        """
        for ae in self:
            self._update_ae_with_student_info(ae)


    def _update_ae_with_student_info(self,e:AnswerEntry):
        i = self.student_info.find_index_of_item_with_attr_val(
            'student_name',
            getattr(e,'student_name')
        )
        if i is not None:
            setattr(e,'student_class_name',self.student_info[i].student_class_name)
        else:
            raise Exception(f'find no match for {e.serial_num}:{e.student_name} in exp{self.exp_entry["exp_num"]:02d} {self.exp_entry["exp_title"]}')
        #
        # i = self.student_info.find_index_of_item_with_attr_val('student_id',getattr(e,'student_id'))
        # if i:
        #     setattr(e, 'student_class_name', self.student_info[i].student_class_name)
        # else:
        #     raise ValueError(f'对于{e.student_name}:{e.student_id}，没有在学生信息中找到对应数据(可能是因为名字重名或学号输入错误)')