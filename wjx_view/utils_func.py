from typing import List,Tuple
import re

def iter_mo(txt:str,reg_obj:re.Pattern) -> List[Tuple[int,int]]:
    """

    :param txt: question txt str
    :param reg_obj: regex obj matching pattern
    :return: List[Tuple(mo.start, mo.end)]
    """
    res = reg_obj.finditer(txt)
    entries_mo = [mo for mo in res]
    entires_starts = [mo.span()[0] for mo in entries_mo]
    entries_ends   = [mo.span()[1] for mo in entries_mo]
    return list(zip(entires_starts,entries_ends))

def get_tuples_of_neighbouring_indices(list_obj):
        length = len(list_obj)
        starts = list_obj[:length]
        ends = list_obj[1:]
        ends.append(None)
        return list(zip(starts,ends))

def get_content_around_indics_tuples(start_indics_list:List[int],end_indics_list:List[int]) -> List[Tuple[int,int]]:
    content_start_indics = [0] + end_indics_list[:-1]
    content_end_indics   = start_indics_list
    return list(zip(content_start_indics,content_end_indics))