import sched_parse,sched_ics,,config
from datetime import datetime as dt
from minerva_common import *

def find_exam_times(date,time):
    start = dt.strptime('%Y-%m-%d%H:%M:%S',date + time)
    end = start + datetime.timedelta(hours=+3) # (voiceover) "All exams are three hours in duration."

    dt_start = start.strftime('%Y%m%dT%H%M%S')
    dt_end = end.strftime('%Y%m%dT%H%M%S')

    return (dt_start,dt_end)


def export_ics_sched(sched,report = 'cal'):
	fmt = sched_ics.prepare_cal_report(report)

	cal = u"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Minervaclient//NONSGML minervac.icebergsys.net//EN"""

	for entry in sched:
                dt_start,dt_end = find_exam_times(entry['date'],entry['time'])
                if 'date_2' in entry:
                    print "Two day exams are not currently handled."

		location = entry['_building'] + ' ' + entry['room']
	
		summary = sched_ics.ics_escape(sched_parse.apply_format(entry,fmt[0]))
		description = sched_ics.ics_escape(sched_parse.apply_format(entry,fmt[1]))
		uid = 'FINAL-' + entry['_code'] + "@minervac.icebergsys.net"
		created = dt.utcnow().strftime("%Y%m%dT%H%M%SZ")

		cal += u"""
BEGIN:VEVENT
UID:{uid}
SUMMARY:{summary}
DTSTAMP;VALUE=DATE-TIME:{dt_stamp}
DTSTART;TZID=America/Montreal;VALUE=DATE-TIME:{dt_start}
DTEND;TZID=America/Montreal;VALUE=DATE-TIME:{dt_end}
DESCRIPTION:{description}
LOCATION:{location}
END:VEVENT""".format(uid=uid,summary=summary,description=description,location=location,dt_start=dt_start,dt_end=dt_end,dt_stamp=created)

	cal += u"""
END:VCALENDAR"""

	return cal 
