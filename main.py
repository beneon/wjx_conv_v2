
import yaml
import os

from wjx_model import Curriculum, Session
from wjx_view import DataTemplateIntegrator, AfterView
from reportlab_port import ExpReport


with open('config.yaml','r',encoding='utf8') as _hdlr:
    config = yaml.safe_load(_hdlr)
wd = config['wd']
spss_exp_curr = Curriculum(wd)

for exp_session in spss_exp_curr:
    session_data = exp_session.generate_session_data()
    if session_data.exp_entry['exp_num']<6:
        continue
    dti = DataTemplateIntegrator(session_data)
    for after_view in dti:
        rp_data = after_view.generate_report_data()
        pdf_path = os.path.join(session_data.wd,f"{rp_data.student_class}_{rp_data.student_id}_{rp_data.student_name}.pdf")
        exp_report = ExpReport(pdf_path,rp_data)
        exp_report.go()
