import requests
from minerva_common import *
import sched_parse,sched_timetable,sched_ics

def course_details(term,report = 'default',visual = False,calendar = False,conflicts_only = False,no_conflicts = False):
	minerva_login()
	mineva_reg_menu()
	minerva_get('bwskfshd.P_CrseSchdDetl')
	r = minerva_post('bwskfshd.P_CrseSchdDetl',{'term_in': term})

	if visual:
		sched_timetable.timetable_report(r.text,report)
	elif calendar:
		sched_ics.export_schedule(r.text,report)
	elif conflicts_only:
		sched_parse.conflict_report(r.text,report)
	else:
		sched_parse.course_details_report(r.text,report)
		if not no_conflicts:
			sched_parse.conflict_report(r.text,'conflicts')


