from bs4 import BeautifulSoup
from datetime import datetime
from minerva_common import *
import config_local
import sys

def parse_schedule(text,separate_wait = True):
	html = BeautifulSoup(text,'html.parser')
	tbls_course = html.body.find_all('table',{'summary': 'This layout table is used to present the schedule course detail'})
	tbls_sched = html.body.find_all('table',{'summary': 'This table lists the scheduled meeting times and assigned instructors for this class..'})

	entries = []
	wait_entries = []
	for course,sched in zip(tbls_course,tbls_sched):
		entry = {}

		title,course_name,section = course.caption.text.split(" - ")
		entry['title'] = title[:-1] # No period
		entry['subject'],entry['course'] = course_name.split(" ")
		entry['section'] = section
		entry['_code'] = "-".join([entry['subject'],entry['course'],entry['section']])
		
		course_table = course.findAll('td')
		if len(course_table) == 8:
			fields = ['term','crn','status','instructor','grade_mode','credits','level','campus']
		elif len(course_table) == 10:
			fields = ['term','crn','status','wait_pos','wait_notify_expires','instructor','grade_mode','credits','level','campus']
		for field,cell in zip(fields,course_table):
			entry[field] = cell.text.strip()


		if entry['credits'][-4:] == '.000': #Strip decimals when irrelevant
			entry['credits'] = entry['credits'][:-4]

		

		entry['_status_desc'],entry['_status_date'] = entry['status'].split(" on ")
		entry['_status_desc'] = get_status_code(entry['_status_desc'],short=True)
		
		entry['_status_date'] = datetime.strptime(entry['_status_date'],'%b %d, %Y').strftime(config_local.date_fmt['short_date'])

		if 'wait_notify_expires' in entry and entry['wait_notify_expires'] != '':
			entry['wait_notify_expires'] = datetime.strptime(entry['wait_notify_expires'],'%b %d, %Y %I:%M %p').strftime(config_local.date_fmt['short_datetime'])
			entry['_action_desc'] = "[\033[1;32mReg by " + entry['wait_notify_expires'] + "\033[0m]"
		elif 'wait_pos' in entry:
			entry['_action_desc'] = "[#" + entry['wait_pos'] + " on waitlist]"
		else:
			entry['_action_desc'] = '\t\t\t'


		sched_table = sched.findAll('td')
		fields = ['time_range','days','location','date_range','type','instructors']

		for field,cell in zip(fields,sched_table):
			entry[field] = cell.text.strip()

		entry['type'] = get_type_abbrev(entry['type'])
		entry['location'] = get_bldg_abbrev(entry['location'])

		entry['_building'],entry['_room'] = entry['location'].rsplit(" ",1)
		entry['_building'] = entry['_building'].strip()

		t_start,t_end = entry['time_range'].split(" - ")
		t_start = datetime.strptime(t_start,'%I:%M %p').strftime(config_local.date_fmt['short_time'])
		t_end = datetime.strptime(t_end,'%I:%M %p').strftime(config_local.date_fmt['short_time'])
		t_range = '-'.join([t_start,t_end])
		entry['_time'] = {}
		entry['_time']['start'] = t_start
		entry['_time']['end'] = t_end
		entry['time_range'] = t_range

		if 'wait_pos' in entry and 'wait_pos' != '' and separate_wait:
			wait_entries.append(entry)
		else:
			entries.append(entry)

	return (entries,wait_entries)

def print_sched(sched,columns):

	for entry in sched:
		for col in columns:
			if col in entry:
				sys.stdout.write(entry[col] + "\t")
			else:
				sys.stdout.write(col)

		print ""


def print_sched_report(sched,report = 'default'):
	if report not in config_local.reports:
		print "Error! Report not found"
		sys.exit(MinervaError.user_error)
	

	columns = config_local.reports[report]['columns']
	fmt_string = config_local.reports[report]['format']
	for entry in sched:
			vals = []
			for col in columns:
				vals.append(entry[col])
				

			print fmt_string % tuple(vals)

def course_details_report(text,report = 'default'):
	wait,reg = parse_schedule(text)
	if reg:
		print ""
		print "* Registered courses:"
		print_sched_report(reg,report)
	
	if wait:
		print ""
		print "* Waitlist:"
		print_sched_report(wait,report)

