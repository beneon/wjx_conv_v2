import pandas as pd
from collections import OrderedDict
from wjx_model.answer_field_parser import AnswerField

class DataFileIter:
    def __init__(self,df:pd.DataFrame,EntryClass):
        self.df = df
        self.EntryClass=EntryClass

    def __len__(self):
        return self.df.shape[0]

    def __getitem__(self, item:int):
        if item<self.__len__():
            row_ele: pd.Series = self.df.iloc[item, :]
            row_ele_dict = OrderedDict(row_ele.to_dict())
            return self.EntryClass(row_ele_dict)
        else:
            raise IndexError

    def find_index_of_item_with_attr_val(self,attr_name,attr_val):
        candidate_list = [i for i,e in enumerate(self) if getattr(e,attr_name)==attr_val]
        if len(candidate_list)==1:
            return candidate_list[0]
        elif len(candidate_list)==0:
            return None
        else:
            raise ValueError(f'{attr_name}属性值{attr_val}在查找列表中有多个匹配')


    def iter_to_list(self):
        # 注意，getitem每次获取一个entry的时候，会**重新**init这个东西，这个bug还真是够隐蔽的。
        return [e for e in self]



class EntryBase:
    def __init__(self, row_ele_dict:dict):
        self.row_ele_dict = row_ele_dict
        self.alias_dict = {}
        self.alias_reverse_dict = {}

    def update_alias_dict(self, alias_list, internal_name:str):
        alias_list_filtered = [a for a in alias_list if a in self.row_ele_dict.keys()]
        assert len(alias_list_filtered)==1, f'对于{internal_name}相关结果筛选以后的别名有重复或者无对应别名：{alias_list_filtered}'
        for alias in alias_list_filtered:
            self.alias_dict[alias]=internal_name
            self.alias_reverse_dict[internal_name]=alias

    def get_attr_via_alias(self,alias:str):
        assert alias in self.row_ele_dict.keys(), f'alias:{alias} is not included in row ele dict'
        assert alias in self.alias_dict.keys()
        internal_name = self.alias_dict[alias]
        return getattr(self,internal_name)

    def set_attr_via_internal_name(self,internal_name:str):
        alias = self.alias_reverse_dict[internal_name]
        assert alias in self.row_ele_dict.keys(), f'alias:{alias} is not included in row ele dict'

        val = self.row_ele_dict[alias]
        setattr(self,internal_name,val)




class StudentInfo(EntryBase):
    def __init__(self,row_ele_dict:dict):
        super().__init__(row_ele_dict)
        self.update_alias_dict(
            ['姓名','名字','请输入姓名'],
            'student_name'
        )
        self.update_alias_dict(
            ['学号','学号/工号','工号','请输入学号'],
            'student_id'
        )
        self.update_alias_dict(
            ['班级'],
            'student_class_name'
        )
        self.set_attr_via_internal_name('student_name')
        self.set_attr_via_internal_name('student_id')
        self.set_attr_via_internal_name('student_class_name')


class AnswerEntry(EntryBase):
    def __init__(self,row_ele_dict:dict):
        row_ele_dict = {k: AnswerField(k, v) for k, v in row_ele_dict.items()}
        super().__init__(row_ele_dict)
        self.update_alias_dict(
            ['基本信息：—姓名：','1、姓名','姓名'],
            'student_name'
        )
        self.update_alias_dict(
            ['学号','2、学号','1、学号:'],
            'student_id'
        )
        self.set_attr_via_internal_name('student_name')
        self.set_attr_via_internal_name('student_id')
        self.questions_titles = self._questions_title_list()

    @property
    def serial_num(self):
        if '序号' in self.row_ele_dict.keys():
            return self.row_ele_dict['序号']
        else:
            raise Exception('row ele dict不包含 序号 一项')

    @property
    def user_id(self):
        if '用户ID' in self.row_ele_dict.keys():
            return self.row_ele_dict['用户ID']
        else:
            raise Exception('row ele dict 不包含 用户ID 一项')

    def get_entry_value_via_question_id(self,item):
        """
        注：questions titles 只包含作答的内容。
        :param item: 一列所在的顺序id
        :return: 对应的答案值
        """
        question_title = self.questions_titles[item]
        return self.row_ele_dict[question_title]

    def __len__(self):
        return len(self.questions_titles)

    def __getitem__(self, item):
        """
        注：questions titles 只包含作答的内容。
        :param item: 一列所在的顺序id
        :return: 对应的答案值
        """
        if 0 <= item < self.__len__():
            question_title = self.questions_titles[item]
            return self.row_ele_dict[question_title]
        else:
            raise IndexError

    def _questions_title_list(self):
        keys_list = list(self.row_ele_dict.keys())
        # 这里定义问卷内容起始部分依赖当前问卷数据情况，如果来自ip或者总分不是前缀最后一项的话会出问题
        if '总分' in keys_list:
            index_str = '总分'
        elif '来自IP' in keys_list:
            index_str = '来自IP'
        else:
            raise Exception('问卷中不包含关键项：**来自IP**或**总分**')
        _q_starts_at = keys_list.index(index_str)+1
        return keys_list[_q_starts_at:]
