# sched_timetable.py: Generate a HTML timetable from course schedule structures
# This file is from Minervac, a command-line client for Minerva
# <http://npaun.ca/projects/minervac>
# (C) Copyright 2016-2017 Nicholas Paun

import config,sched_parse
from datetime import datetime as dt
from minerva_common import *

def timetable_report(text,report = 'timetable_default'):
	sched = sched_parse.parse_schedule(text,separate_wait = False)
	timetable_html(timetable_struct(sched,report))
	

def timetable_struct(sched,report = 'timetable_default'):
	(fmt,sched) = sched_parse.prepare_report(report,sched)
	timetable = {}
	i = 1

	for entry in sched:
		if '_time' not in entry:
			continue

		t_start = entry['_time']['start']
		if t_start not in timetable:
			timetable[t_start] = {}

		if entry['days'] not in timetable[t_start]:
			timetable[t_start][entry['days']] = {}
		
		entry['_action_desc'] = entry['_action_desc'].replace('\033[1;32m','<strong>').replace('\033[0m','</strong>') #FIXME: This is really ugly.
		summary = sched_parse.apply_format(entry,fmt)

		wait = 'wait_pos' in entry and entry['wait_pos'] is not None
		timetable[t_start][entry['days']][i] = ((entry['_time'],summary,wait))
		i += 1
	
	return timetable

def timeslot_format(timeslot):
	if timeslot[-2:] == "35":
		return timeslot[:-3] + "h30"
	elif timeslot[-2:] == "05":
		return timeslot[:-3]

def calc_rowspan(time):
	t_start = dt.strptime(time['start'],config.date_fmt['short_time'])
	t_end = dt.strptime(time['end'],config.date_fmt['short_time'])
	delta = t_end - t_start
	minutes = delta.total_seconds() / 60
	
	return int(minutes / 25)

def make_day_header(days):
	header = """
	<thead class='sched-header'>
		<tr>
			<th></th>
	"""

	for day in days:
		header += "<th>" + get_real_weekday(day) + "</th>\n"

	header += "</tr>\n</thead>\n"
	return header

def timetable_cell(day,course_num,entry):
	_time,summary,wait = entry
	rowspan = calc_rowspan(_time)
	colspan(day,rowspan)

	if wait:
		summary = "<div class='waiting' title='Waitlisted'>" + summary + "</div>"
	else:
		summary = "<div class='registered' title='Registered'>" + summary + "</div>"

	return "\t<td class='sched-entry sched-entry-{n}' rowspan='{rowspan}'>{entry}</td>".format(entry=summary,rowspan=rowspan,n=course_num)


def timetable_process_timeslot(day,entries):
	for day_code in entries:
		if day in day_code:
			course_num,entry = entries[day_code].items()[0]
			return timetable_cell(day,course_num,entry)
	
	return False

def colspan(col,set = None):
	if set is None:
		if col not in colspan.spans:
			colspan.spans[col] = 0
		
		return colspan.spans[col] == 0
	elif set == '-':
		if colspan.spans[col] > 0:
			colspan.spans[col] -= 1
	else:
		colspan.spans[col] = set

		
def make_style_header():
	header = "<style>\n"
	header += open('sched_timetable.css').read()
	header +=  "</style>\n"

	return header

def timetable_html(timetable):
	colspan.spans = {}
	course_times = ['08h05','08h35','09h05','09h35','10h05','10h35','11h05','11h35','12h05','12h35','13h05','13h35','14h05','14h35','15h05','15h35','16h05','16h35','17h05','17h35']

	days = get_minerva_weekdays(config.show_weekend)
	
	print """
	<!DOCTYPE html>
	<html>
		<head>
			<title>Minervac Class Schedule</title>
			<meta charset="UTF-8" />
			<meta name="generator" content="minervac" />
			{style}
		</head>
		<body>
			<h1 class="sched-title">Class Schedule</h1>
			<table class='sched-table'>
				{days}

	""".format(style=make_style_header(),days=make_day_header(days))
	
	for time in course_times:
		print """
		<tr class='sched-row'>
			<th class='sched-timeslot'>{time}</th>
		""".format(time=timeslot_format(time))
			
		for day in days:
			if time in timetable:
				cell = timetable_process_timeslot(day,timetable[time])
				if cell: print cell
			
			if colspan(day):
				print "\t<td class='sched-blank'>&nbsp;</td>"
	

			colspan(day,'-')

		print """
		</tr>
		"""

	print """
	</table>
	</body>
	</html>
	"""
