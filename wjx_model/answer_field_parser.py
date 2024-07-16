
import re
from typing import Union
from urllib.parse import urlparse
from wjx_model.attachment_parser import AttachmentFileEntry


class AnswerField:
    ReIsURL = re.compile(r'https://alifile.sojump.cn/.*')
    def __init__(self,q_title:str,content:Union[str,int,float]):
        self.content = content
        self.attachment = None
        self.attachment_type = None
        self.question_title = q_title
        url_parsed = self.parse_url()
        if url_parsed:
            self.is_file_upload = True
        else:
            self.is_file_upload = False

    def __str__(self):
        return self.question_title

    def update_url_to_file_attachment(self,attachment:AttachmentFileEntry):
        self.attachment = attachment
        self.attachment_type = attachment.attachment_type
        pass

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


