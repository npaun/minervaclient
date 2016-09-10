import requests
from minerva_common import *
import sched_parse,sched_timetable

def course_details(term,report = 'default',visual = False,conflicts_only = False,no_conflicts = False):
	minerva_login()
	minerva_get('bwskfshd.P_CrseSchdDetl')
	r = minerva_post('bwskfshd.P_CrseSchdDetl',{'term_in': term})
	if visual:
		sched_timetable.timetable_report(r.text,report)
	elif conflicts_only:
		sched_parse.conflict_report(r.text,report)
	else:
		sched_parse.course_details_report(r.text,report)
		if not no_conflicts:
			sched_parse.conflict_report(r.text,'conflicts')

