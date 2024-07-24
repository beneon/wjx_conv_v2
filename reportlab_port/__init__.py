from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Spacer
from reportlab.platypus.frames import Frame
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm, inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT,TA_CENTER,TA_RIGHT,TA_JUSTIFY

from reportlab_port.types import ReportData
from reportlab_port.content_proc import QuestionProc,RCElementProc

from typing import List, TypeVar

StoryContent = TypeVar('StoryContent',Spacer,Paragraph)

pdfmetrics.registerFont(TTFont('SimSun', 'simsun.ttc'))
pdfmetrics.registerFont(TTFont('SimHei', 'simhei.ttf'))

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(fontName='SimSun', name='header_song',alignment=TA_RIGHT, fontSize=10))
styles.add(ParagraphStyle(fontName='SimHei',name='header_hei',fontSize=12,alignment=TA_LEFT))
styles.add(ParagraphStyle(fontName='SimHei',name='hei_center',fontSize=12,alignment=TA_CENTER))
styles.add(ParagraphStyle(fontName='SimSun',name='content_left',fontSize=12,alignment=TA_LEFT,firstLineIndent=2))
styles.add(ParagraphStyle(fontName='SimHei',name='maintext_left',fontSize=12,alignment=TA_LEFT,firstLineIndent=2))


class ExpReport:
    def __init__(self,pdf_filepath:str, report_data: ReportData):
        self.doc = SimpleDocTemplate(pdf_filepath,pagesize=A4)
        self.report_data = report_data
        self.story: List[StoryContent] = []
        self.styles = styles
        self._update_story_list()

    def go(self):
        self.doc.build(self.story,onFirstPage=self.pageDraw,onLaterPages=self.pageDraw)

    def pageDraw(self,canv:canvas.Canvas,doc) -> None:
        canv.saveState()
        self._create_header(canv,doc)
        self._create_footer(canv,doc)
        canv.rect(doc.leftMargin,doc.bottomMargin,doc.width,doc.height)
        canv.restoreState()

    def _update_story_list(self):
        if isinstance(self.report_data.report_content,str):
            paragraph_txts = self.report_data.report_content.split('\n')
            for p_txt in paragraph_txts:
                self.story.append(Paragraph(p_txt,self.styles['content_left']))
        elif isinstance(self.report_data.report_content,list):
            question_proc_list = [QuestionProc(rce_list,self.styles) for rce_list in self.report_data.report_content]
            rst_list = []
            for question_proc_flowable in question_proc_list:
                rst_list = rst_list+question_proc_flowable.get_combined_flowables()
            for f in rst_list:
                self.story.append(f)


    def _create_header(self, canv:canvas.Canvas, doc)->None:
        left_header = Paragraph(f"{self.report_data.curriculum_title}实验报告", styles['header_hei'])
        w,h = left_header.wrap(doc.width,doc.topMargin)
        left_header.drawOn(canv, doc.leftMargin, doc.height + doc.bottomMargin + doc.topMargin*2/3 - h)

        right_header = Paragraph(f"姓名：{self.report_data.student_name} 学号：{self.report_data.student_id}班级：{self.report_data.student_class}<br/>", styles['header_song'])
        wr,hr = right_header.wrap(doc.width,doc.topMargin-h)
        right_header.drawOn(canv, doc.leftMargin, doc.height + doc.bottomMargin + doc.topMargin*2/3 - h - hr)

    def _create_footer(self,canv:canvas.Canvas, doc) -> None:
        footer = Paragraph('佛山科学技术学院医学院',styles['header_song'])
        w, h = footer.wrap(doc.width, doc.bottomMargin)
        footer.drawOn(canv, doc.leftMargin, doc.bottomMargin*2/3 - h)




