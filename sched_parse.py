from bs4 import BeautifulSoup
from datetime import datetime as dt
from minerva_common import *
import config
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
			if entry[field] == '':
				entry[field] = None


		if entry['credits'][-4:] == '.000': #Strip decimals when irrelevant
			entry['credits'] = entry['credits'][:-4]

		

		entry['_status_desc'],entry['_status_date'] = entry['status'].split(" on ")
		entry['_status_desc'] = get_status_code(entry['_status_desc'],short=True)
		
		entry['_status_date'] = dt.strptime(entry['_status_date'],'%b %d, %Y').strftime(config.date_fmt['short_date'])

		if 'wait_notify_expires' in entry and entry['wait_notify_expires'] is not None:
			entry['wait_notify_expires'] = dt.strptime(entry['wait_notify_expires'],'%b %d, %Y %I:%M %p').strftime(config.date_fmt['short_datetime'])
			entry['_action_desc'] = "[\033[1;32mReg by " + entry['wait_notify_expires'] + "\033[0m]"
		elif 'wait_pos' in entry:
			entry['_action_desc'] = "[#" + entry['wait_pos'] + " on waitlist]"
		else:
			entry['_action_desc'] = ''


		sched_table = sched.findAll('td')
		fields = ['time_range','days','location','date_range','type','instructors']

		for field,cell in zip(fields,sched_table):
			entry[field] = cell.text.strip()

		entry['type'] = get_type_abbrev(entry['type'])
		entry['location'] = get_bldg_abbrev(entry['location'])

		entry['_building'],entry['_room'] = entry['location'].rsplit(" ",1)
		entry['_building'] = entry['_building'].strip()

		t_start,t_end = entry['time_range'].split(" - ")
		t_start = dt.strptime(t_start,'%I:%M %p').strftime(config.date_fmt['short_time'])
		t_end = dt.strptime(t_end,'%I:%M %p').strftime(config.date_fmt['short_time'])
		t_range = '-'.join([t_start,t_end])
		entry['_time'] = {}
		entry['_time']['start'] = t_start
		entry['_time']['end'] = t_end
		entry['time_range'] = t_range

		d_start,d_end = entry['date_range'].split(" - ")
		d_start = dt.strptime(d_start,'%b %d, %Y').strftime(config.date_fmt['full_date'])
		d_end = dt.strptime(d_end,'%b %d, %Y').strftime(config.date_fmt['full_date'])
		d_range = ' / '.join([d_start,d_end]) #ISO made me do it
		entry['_date'] = {'start': d_start,'end': d_end}
		entry['date_range'] = d_range

		
		if 'wait_pos' in entry and 'wait_pos' is not None and separate_wait:
			wait_entries.append(entry)
		else:
			entries.append(entry)

	if separate_wait:
		return (entries,wait_entries)
	else:
		return entries

def print_sched(sched,columns):

	for entry in sched:
		for col in columns:
			if col in entry:
				sys.stdout.write(entry[col] + "\t")
			else:
				sys.stdout.write(col)

		print ""


def print_sched_report(sched,report = 'default'):
	(fmt,sched) = prepare_report(report,sched)

	for entry in sched: sys.stdout.write(apply_format(entry,fmt))

def find_conflicts(sched,report = 'conflicts'):
	(fmt,sched) = prepare_report(report,sched)

	for i, curr in enumerate(sched[:-1]):
		next = sched[i+1]

		if not set(curr['days']).intersection(set(next['days'])): #This isn't quite right
			continue 
	
		next_start = dt.strptime(next['_time']['start'],config.date_fmt['short_time'])
		curr_end = dt.strptime(curr['_time']['end'],config.date_fmt['short_time'])
		diff = int((next_start - curr_end).total_seconds() / 60)
			
		if diff <= 0:
			print "* Conflict for %d mins" % -diff
			sys.stdout.write(apply_format(curr,fmt))
			sys.stdout.write(apply_format(next,fmt))
def prepare_report(report,sched):
	if report not in config.reports:
		print "Error! Report not found"
		sys.exit(MinervaError.user_error)
	
	report = config.reports[report]
	sorted = multi_keysort(sched,report['sort'])
	return ((report['columns'],report['format']),sorted)

def apply_format(entry,fmt):
	columns, fmt_string = fmt
	vals = []
	for col in columns:
		vals.append(entry[col])
				

	return fmt_string % tuple(vals)


# Copypasta from this Stackoverflow answer. http://stackoverflow.com/a/1144405. Python apparently sucks.
def multi_keysort(items, columns):
	if columns is None:
		return items

	from operator import itemgetter
	comparers = [((itemgetter(col[1:].strip()), -1) if col.startswith('-') else
			      (itemgetter(col.strip()), 1)) for col in columns]
	def comparer(left, right):
		for fn, mult in comparers:
			result = cmp(fn(left), fn(right))
			if result:
			    return mult * result
		else:
			return 0
	return sorted(items, cmp=comparer)

def course_details_report(text,report = 'default'):
	reg,wait = parse_schedule(text)
	if reg:
		print ""
		print "* Registered courses:"
		print_sched_report(reg,report)
	
	if wait:
		print ""
		print "* Waitlist:"
		print_sched_report(wait,report)

def conflict_report(text,report = 'conflicts'):
	sched = parse_schedule(text,separate_wait = False)
	find_conflicts(sched,report)


# vi: ft=python
