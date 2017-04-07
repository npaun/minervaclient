# sched_ics.py: Export course schedule to vCalendar format
# This file is from Minervac, a command-line client for Minerva
# <http://npaun.ca/projects/minervac>
# (C) Copyright 2016-2017 Nicholas Paun

import sched_parse,config
from datetime import datetime as dt
from minerva_common import *



def next_weekday(d, weekday):
	days_ahead = weekday - d.weekday()
	if days_ahead < 0: # Target day already happened this week
		days_ahead += 7

	return d + datetime.timedelta(days_ahead)

def labor_day_swap(d_start,days):
	if d_start.month == 9 and 'M' not in days and 'F' in days:
		#1. Fall term
		#2. Would not have come up anyway as a Monday
		#3. Is a real Friday
		first_day = d_start + datetime.timedelta(days=7)
		return first_day
	else:
		return False

def find_first_day(days,d_start,t_start,t_end):
	minerva_days = get_minerva_weekdays()
	d_start = dt.strptime(d_start + " " + t_start,config.date_fmt['full_date'] + " " + config.date_fmt['short_time'])
	dt_end = dt.strptime(t_end,config.date_fmt['short_time'])

	best_weekday = dt(9999,1,1)
	ics_days = []


	for day in days:
		idx = minerva_days.index(day)
		cand_weekday = next_weekday(d_start,idx)
		if cand_weekday < best_weekday:
			best_weekday = cand_weekday
		
		ics_days.append(get_ics_weekday(day))

	possible_first_day = labor_day_swap(d_start,days)
	if possible_first_day: best_weekday = possible_first_day		

	dt_end = dt_end.replace(best_weekday.year,best_weekday.month,best_weekday.day)

	dt_start = best_weekday.strftime(iso_date['full'])
	dt_end = dt_end.strftime(iso_date['full'])
	ics_days = ",".join(ics_days)

	return (ics_days,dt_start,dt_end)	

def find_last_day(d_end):
	d_end = dt.strptime(d_end,config.date_fmt['full_date'])
	d_end += datetime.timedelta(days=1)
	return d_end.strftime(iso_date['full'])

def prepare_cal_report(report):	
	if report not in config.reports:
		print "Error! Report not found"
		sys.exit(MinervaError.user_error)
	
	report = config.reports[report]
	return [(report['columns'][0],report['format'][0]),(report['columns'][1],report['format'][1])]

def ics_escape(text):
	return text.replace("\033[1;32m","*") \
	.replace("\033[0m","*") \
	.replace(",","\,") \
	.replace(";","\;")
		

def export_ics_sched(sched,report = 'cal'):
	fmt = prepare_cal_report(report)

	cal = u"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Minervaclient//NONSGML minervac.icebergsys.net//EN"""

	for entry in sched:
		(days,dt_start,dt_end) = find_first_day(entry['days'],entry['_date']['start'],entry['_time']['start'],entry['_time']['end'])
		date_end = find_last_day(entry['_date']['end'])

		location = entry['_building'] + ' ' + entry['_room']
	
		summary = ics_escape(sched_parse.apply_format(entry,fmt[0]))
		description = ics_escape(sched_parse.apply_format(entry,fmt[1]))
		uid = entry['_code'] + "@minervac.icebergsys.net"
		created = dt.utcnow().strftime(iso_date['full']) + "Z"

		cal += u"""
BEGIN:VEVENT
UID:{uid}
SUMMARY:{summary}
DTSTAMP;VALUE=DATE-TIME:{dt_stamp}
DTSTART;TZID=America/Montreal;VALUE=DATE-TIME:{dt_start}
DTEND;TZID=America/Montreal;VALUE=DATE-TIME:{dt_end}
DESCRIPTION:{description}
LOCATION:{location}
RRULE:FREQ=WEEKLY;UNTIL={date_end};BYDAY={days}
END:VEVENT""".format(uid=uid,summary=summary,description=description,location=location,dt_start=dt_start,dt_end=dt_end,days=days,date_end=date_end,dt_stamp=created)

	cal += u"""
END:VCALENDAR"""

	return cal

def export_schedule(text,report = 'cal'):
	sched = sched_parse.parse_schedule(text,separate_wait = False)
	print export_ics_sched(sched,report).encode("utf8").replace("\n","\r\n")

