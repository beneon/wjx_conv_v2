from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Spacer
from reportlab.platypus.frames import Frame
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm, inch, cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT,TA_CENTER,TA_RIGHT,TA_JUSTIFY

paragraphs = [
    'Multiple columns turned out to be easier than I expected. Instead of using the SimpleDocTemplate as in the previous examples, we need to use BaseDocTemplate and create our own frames using Platypus. Platypus will flow the text into each frame as necessary.',
    'I completely re-wrote the makePDF method on the PDF class of my Snakelets blog. First thing, of course, is to import the appropriate libraries.',
    'I’ve added a content-disposition header. Instead of attachment, as you normally put into content-disposition, I’ve specified that the file should be displayed normally (which on some browsers will still be as an attachment if they don’t have the capability to inline-view PDF files). But by giving it a filename, if they do save the PDF they should get that as the default filename for the file.',
]

doc = SimpleDocTemplate('test.pdf')
cav = canvas.Canvas('test.pdf',A4)
story = [Spacer(1,20*mm)]
styles = getSampleStyleSheet()
style = styles['Normal']
for p_text in paragraphs:
    p = Paragraph(p_text,style)
    story.append(p)
    story.append(Spacer(1,2*mm))

f1 = Frame(0,12*cm,20*cm,5*cm,showBoundary=1,)
f2 = Frame(0,0,width=20*cm,height=10*cm,showBoundary=1)

