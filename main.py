
import yaml
import os

from wjx_model import Curriculum, Session
from reportlab_port import ExpReport


with open('config.yaml','r',encoding='utf8') as _hdlr:
    config = yaml.safe_load(_hdlr)
wd = config['wd']
spss_exp_curr = Curriculum(wd)
spss_exp_05 = spss_exp_curr[4]

t_parser = spss_exp_05.template_parser
t_list = [t_parser[i] for i in range(len(t_parser))]

answer_parser = spss_exp_05.answers
a00 = answer_parser[0]

with open(os.path.join('dataset_tmp','report.yaml'),'r',encoding='utf8') as _hdlr:
    report_data = yaml.safe_load(_hdlr)

exp_report = ExpReport('tmp.pdf',report_data)
exp_report.go()
