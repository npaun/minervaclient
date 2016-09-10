from bs4 import BeautifulSoup
from datetime import datetime
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
		
		entry['_status_date'] = datetime.strptime(entry['_status_date'],'%b %d, %Y').strftime(config.date_fmt['short_date'])

		if 'wait_notify_expires' in entry and entry['wait_notify_expires'] is not None:
			entry['wait_notify_expires'] = datetime.strptime(entry['wait_notify_expires'],'%b %d, %Y %I:%M %p').strftime(config.date_fmt['short_datetime'])
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
		t_start = datetime.strptime(t_start,'%I:%M %p').strftime(config.date_fmt['short_time'])
		t_end = datetime.strptime(t_end,'%I:%M %p').strftime(config.date_fmt['short_time'])
		t_range = '-'.join([t_start,t_end])
		entry['_time'] = {}
		entry['_time']['start'] = t_start
		entry['_time']['end'] = t_end
		entry['time_range'] = t_range

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
	if report not in config.reports:
		print "Error! Report not found"
		sys.exit(MinervaError.user_error)
	

	columns = config.reports[report]['columns']
	fmt_string = config.reports[report]['format']
	sort = config.reports[report]['sort']

	sched = multi_keysort(sched,sort)
	for entry in sched:
			vals = []
			for col in columns:
				vals.append(entry[col])
				

			print fmt_string % tuple(vals)

def timetable_struct(sched,report = 'timetable_default'):
	columns = config.reports[report]['columns']
	fmt_string = config.reports[report]['format']
	sort = config.reports[report]['sort']

	sched = multi_keysort(sched,sort)
	course_times = ['8','8:30','9','9:30','10','10:30','11','11:30','12','12:30','13','13:30','14','14:30','15','15:30','16','16:30','17','17:30']
	timetable = {}

	i = 1
	for entry in sched:
		t_start = entry['_time']['start']
		if t_start not in timetable:
			timetable[t_start] = {}

		if entry['days'] not in timetable[t_start]:
			timetable[t_start][entry['days']] = {}

		vals = []
		for col in columns:
			vals.append(entry[col])

		summary = fmt_string % tuple(vals)
		if 'wait_pos' in entry and entry['wait_pos'] is not None:
			wait = True
		else:
			wait = False

		timetable[t_start][entry['days']][i] = ((entry['_time'],summary,wait))
		i += 1
	
	return timetable

def timeslot_format(timeslot):
	if timeslot[-2:] == "35":
		return "*"
	elif timeslot[-2:] == "05":
		return timeslot[:-3]

def calc_rowspan(time):
	t_start = datetime.strptime(time['start'],config.date_fmt['short_time'])
	t_end = datetime.strptime(time['end'],config.date_fmt['short_time'])
	delta = t_end - t_start
	minutes = delta.total_seconds() / 60
	
	return int(minutes / 25)

def timetable_html(timetable,num_courses,report = 'timetable_default'):
	course_times = ['08h05','08h35','09h05','09h35','10h05','10h35','11h05','11h35','12h05','12h35','13h05','13h35','14h05','14h35','15h05','15h35','16h05','16h35','17h05','17h35']
	days = ['M','T','W','R','F','S','U']
	day_names = {'M': 'Monday','T': 'Tuesday','W': 'Wednesday','R': 'Thursday','F': 'Friday','S': 'Saturday','U': 'Sunday'}

	print """
	<link rel="stylesheet" href="sched.css"/>
	<table class='sched-table'>
		<thead class='sched-header'>
			<tr>
				<th>*</th>
				<th>Monday</th>
				<th>Tuesday</th>
				<th>Wednesday</th>
				<th>Thursday</th>
				<th>Friday</th>
				<th>Saturday</th>
				<th>Sunday</th>
			</tr>
		</thead>
	"""

	spans = {}
	
	for time in course_times:
		print """
		<tr class='sched-row'>
			<th class='sched-timeslot'>{time}</th>
		""".format(time=timeslot_format(time))
	
			
		col = 0
		for day in days:
			if col in spans:
				pass
				#print spans[col]

			if time in timetable:
				for day_code in timetable[time]:
					if day in day_code:
						course_num,entry = timetable[time][day_code].items()[0]
						_time,summary,wait = entry
						rowspan = calc_rowspan(_time)
						spans[col] = rowspan - 0

						if wait:
							summary = "<div class='waiting'>" + summary + "</div>"
						else:
							summary = "<div class='registered'>" + summary + "</div>"

						#print str(col) + " Spans " + str(spans[col])
						print "\t<td class='sched-entry sched-entry-{n}' rowspan='{rowspan}'>{entry}</td>".format(entry=summary,rowspan=rowspan,n=course_num)
					elif col not in spans or spans[col] == 0:
						print "\t<td class='sched-blank'><br><br><br></td>"

					
			elif col not in spans or spans[col] == 0:
				print "\t<td class='sched-blank'><br><br><br></td>"
	
			if col in spans and spans[col] > 0:
				spans[col] -= 1
			else:
				spans[col] = 0

			col += 1

		print """
		</tr>
		"""

	print "</table>"			
			

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


def timetable_report(text,report = 'timetable_default'):
	sched = parse_schedule(text,separate_wait = False)
	timetable_html(timetable_struct(sched,report),len(sched),report)
	

f = open('/home/np/minervaslammer/crsedetail.html').read()
timetable_report(f)
# vi: ft=python
