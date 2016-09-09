import requests
from minerva_common import *
import sched_parse

def schedule(term,report = 'default'):
	minerva_login()
	minerva_get('bwskfshd.P_CrseSchdDetl')
	r = minerva_post('bwskfshd.P_CrseSchdDetl',{'term_in': term})
	sched_parse.course_details_report(r.text,report)

schedule('201609')
