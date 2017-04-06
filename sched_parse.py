from bs4 import BeautifulSoup
from datetime import datetime as dt
from minerva_common import *
import config
import sys,urllib,re

def parse_schedule(text,separate_wait = True):
	html = BeautifulSoup(text,'html5lib')
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
			entry[field] = cell.text.strip().replace("\n","; ")
			if entry[field] == '':
				entry[field] = '{0}'

                entry['instructor'] = entry['instructor'].replace(', ','')            
                entry['_instructor_sn'] = entry['instructor'].split('; ')[0].split(' ')[-1]

		if entry['credits'][-4:] == '.000': #Strip decimals when irrelevant
			entry['credits'] = entry['credits'][:-4]


		entry['_status_desc'],entry['_status_date'] = entry['status'].split(" on ")
		entry['_status_desc'] = get_status_code(entry['_status_desc'],short=True)
		
		entry['_status_date'] = dt.strptime(entry['_status_date'],'%b %d, %Y').strftime(config.date_fmt['short_date'])

		if 'wait_notify_expires' in entry and entry['wait_notify_expires'] is not None:
			entry['wait_notify_expires'] = dt.strptime(entry['wait_notify_expires'],minerva_date['full']).strftime(config.date_fmt['short_datetime'])
			entry['_action_desc'] = "[\033[1;32mReg by " + entry['wait_notify_expires'] + "\033[0m]"
		elif 'wait_pos' in entry:
			entry['_action_desc'] = "[#" + entry['wait_pos'] + " on waitlist]"
		else:
			entry['_action_desc'] = ''

                if entry['_status_desc'] == 'W':
                    entry['_action_desc'] = '[Withdrawn from this course]'


		sched_table = sched.findAll('td')
		fields = ['time_range','days','location','date_range','type','instructors']

		for field,cell in zip(fields,sched_table):
			entry[field] = cell.text.strip()


		entry['_day_idx'] = day_index(entry['days'])		
		entry['type'] = get_type_abbrev(entry['type'])

		loc_bits =  entry['location'].rsplit(" ",1)

		if len(loc_bits) == 2:
			entry['_building'],entry['_room'] = loc_bits
		else:
			entry['_building'] = loc_bits[0]
			entry['_room'] = ''

		entry['_building'] = entry['_building'].strip()
		entry['_link_gmaps'] = "http://maps.google.com/?" + urllib.urlencode([('saddr','My Location'),('daddr',entry['_building'] + ", Montreal")])
		entry['_building'] = get_bldg_abbrev(entry['_building']).strip()

		
		t_bits = entry['time_range'].split(" - ")
		if len(t_bits) == 2:	
			t_start,t_end = entry['time_range'].split(" - ")
			t_start = dt.strptime(t_start,minerva_date['time']).strftime(config.date_fmt['short_time'])
			t_end = dt.strptime(t_end,minerva_date['time']).strftime(config.date_fmt['short_time'])
			t_range = '-'.join([t_start,t_end])
			entry['_time'] = {}
			entry['_time']['start'] = t_start
			entry['_time']['end'] = t_end
			entry['time_range'] = t_range
		else:
			entry['time_range'] = t_bits[0]

		d_start,d_end = entry['date_range'].split(" - ")
		d_start = dt.strptime(d_start,minerva_date['date']).strftime(config.date_fmt['full_date'])
		d_end = dt.strptime(d_end,minerva_date['date']).strftime(config.date_fmt['full_date'])
		d_range = ' / '.join([d_start,d_end]) #ISO made me do it
		entry['_date'] = {'start': d_start,'end': d_end}
		entry['date_range'] = d_range

		
		if ('wait_pos' in entry and 'wait_pos' is not None and separate_wait) or entry['_status_desc'] == 'W':
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
	(fmt,sched) = prepare_report(report,sched,sort = False)

	instances = []
	weekdays = get_minerva_weekdays()
	for entry in sched:
		for day in entry['days']:
			weekday = weekdays.index(day)
			key = str(weekday) + dt.strptime(entry['_time']['start'],config.date_fmt['short_time']).strftime('%H%M')
			end = str(weekday) + dt.strptime(entry['_time']['end'],config.date_fmt['short_time']).strftime('%H%M')
			instances.append((key,end,entry))

	instances = sorted(instances)
	conflict_pairs = []
	
	i = -1
	for curr in instances[:-1]:
		i += 1
		(c_start,c_end,c_entry) = curr
		(n_start,n_end,n_entry) = instances[i+1]
		pair = c_entry['_code'] + "," + n_entry['_code']

		if c_start[0] != n_start[0]: #We've run out of courses for the day
			continue
		elif pair in conflict_pairs: #We already know what happens
			continue
		elif (c_start < n_end) and (c_end > n_start): #Formal definition of a time conflict
			conflict_pairs.append(pair)
			print_conflict(fmt,c_entry,n_entry)

	
def print_conflict(fmt,curr,next):	
		intersect = "".join(list(set(curr['days']).intersection(set(next['days']))))
		print "* Conflict: \033[1;31m%s %s-%s\033[0m" % (intersect,next['_time']['start'], curr['_time']['end'])
		sys.stdout.write(apply_format(curr,fmt))
		sys.stdout.write(apply_format(next,fmt))


def prepare_report(report,sched,sort = True):
	if report not in config.reports:
		print "Error! Report not found"
		sys.exit(MinervaError.user_error)
	
	report = config.reports[report]
	if sort:
		sorted = multi_keysort(sched,report['sort'])
	else:
		sorted = sched
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

	def nat(s, _nsre=re.compile('([0-9]+)')):
            def value(text):
                if text.isdigit():
                    return int(text)
                elif type(text) == str:
                    return text.lower()
                else:
                    return text

            if type(s) == str:
                return [value(text) for text in re.split(_nsre, s)]
            else:
                return [s]

	def comparer(left, right):
		for fn, mult in comparers:
			lval = nat(fn(left))
			rval = nat(fn(right))
			result = cmp(lval, rval)
			if result:
			    return mult * result
		else:
			return 0


	return sorted(items, cmp=comparer)

def day_index(days):
	m_weekdays = get_minerva_weekdays()
	index = ""
	for day in days:
		index += str(m_weekdays.index(day) + 1)


	return days
	return index.ljust(7,'0')

def course_details_report(text,report = 'default'):
	reg,wait = parse_schedule(text)
	if reg:
		print ""
		print "* Registered:"
		print_sched_report(reg,report)
	
	if wait:
		print ""
                print "* Waitlist / Withdrawn / Other:"
		print_sched_report(wait,report)

def conflict_report(text,report = 'conflicts'):
	sched = parse_schedule(text,separate_wait = False)
	find_conflicts(sched,report)



