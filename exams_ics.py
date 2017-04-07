# exams_ics.py: Export final exam schedule to vCalendar format
# This file is from Minervac, a command-line client for Minerva
# <http://npaun.ca/projects/minervac>
# (C) Copyright 2016-2017 Nicholas Paun

import sched_parse,sched_ics,exams_parse,config
from datetime import datetime as dt
from minerva_common import *

def find_exam_times(start):
    end = start + datetime.timedelta(hours = +3) # (voiceover) "All exams are three hours in duration."

    dt_start = start.strftime(iso_date['full'])
    dt_end = end.strftime(iso_date['full'])

    return (dt_start,dt_end)

def gen_ics_event(entry,datetime,fmt,tag):
    dt_start,dt_end = find_exam_times(datetime)
    location = entry['_building'] + ' ' + entry['room']
	
    summary = sched_ics.ics_escape(sched_parse.apply_format(entry,fmt[0]))
    description = sched_ics.ics_escape(sched_parse.apply_format(entry,fmt[1]))
    uid = entry['_code'] + '-' + tag + "@minervac.icebergsys.net"
    created = dt.utcnow().strftime(iso_date['full']) + "Z"

    cal = u"""
BEGIN:VEVENT
UID:{uid}
SUMMARY:{summary}
DTSTAMP;VALUE=DATE-TIME:{dt_stamp}
DTSTART;TZID=America/Montreal;VALUE=DATE-TIME:{dt_start}
DTEND;TZID=America/Montreal;VALUE=DATE-TIME:{dt_end}
DESCRIPTION:{description}
LOCATION:{location}
END:VEVENT""".format(uid=uid,summary=summary,description=description,location=location,dt_start=dt_start,dt_end=dt_end,dt_stamp=created)

    return cal



def export_ics_sched(sched,report = 'cal_exams'):
	fmt = sched_ics.prepare_cal_report(report)

	cal = u"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Minervaclient//NONSGML minervac.icebergsys.net//EN"""

	for entry in sched:
                cal += gen_ics_event(entry,entry['_datetime'][0],fmt,'final')
                if 'date_2' in entry:
                    cal += gen_ics_event(entry,entry['_datetime'][1],fmt,'final-day-2')

	cal += u"""
END:VCALENDAR"""

	return cal

def export_schedule(term,report = 'cal_exams'):
    exams = exams_parse.find_exams(term,return_notfound=False)
    print export_ics_sched(exams,report).encode("utf8").replace("\n","\r\n")
