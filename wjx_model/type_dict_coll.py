from typing import TypedDict, List


class ExpEntry(TypedDict):
    curriculum_title:str
    exp_title:str
    exp_type:str
    exp_num:int


class CourseConfigYaml(TypedDict):
    student_data: str
    curriculum_title:str
    entries: List[ExpEntry]


