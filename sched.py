import requests
from minerva_common import *
import sched_parse

def course_details(term,report = 'default',visual = False):
	minerva_login()
	minerva_get('bwskfshd.P_CrseSchdDetl')
	r = minerva_post('bwskfshd.P_CrseSchdDetl',{'term_in': term})
	if not visual:
		sched_parse.course_details_report(r.text,report)
	else:
		sched_parse.timetable_report(r.text,report)
