import requests
from minerva_common import *
import sched_parse,sched_timetable

def course_details(term,report = 'default',visual = False):
	minerva_login()
	minerva_get('bwskfshd.P_CrseSchdDetl')
	r = minerva_post('bwskfshd.P_CrseSchdDetl',{'term_in': term})
	if not visual:
		sched_parse.course_details_report(r.text,report)
	else:
		sched_timetable.timetable_report(r.text,report)
