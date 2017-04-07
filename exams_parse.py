# exams_parse.py: Parse transcript to find courses, look up your exam time from the dataset
# This file is from Minervac, a command-line client for Minerva
# <http://npaun.ca/projects/minervac>
# (C) Copyright 2016-2017 Nicholas Paun

import requests,sys
from minerva_common import *
import sched_parse,transcript_parse
import config
from datetime import datetime as dt

def get_courses(term):
    minerva_login()
    minerva_records_menu()
    r = minerva_get("bzsktran.P_Display_Form?user_type=S&tran_type=V")
    trans = transcript_parse.parse_transcript(r.text)

    sn = dequebecify(trans['000000']['info']['_sn'].upper()) # The surname is used to find which exam room the student is assigned to
    courses = []

    for course in trans[term]['grades']: # You can only write exams for one term at a time (At least I hope so for the sake of everyone's sanity)
        if course['grade'] == '': #Don't show exams for stuff you've already been assigned a grade
            courses.append(course['_code'])

    return sn,courses

def get_exam_sched(term):
    repo = config.data_source[0]
    url = repo + "exams-" + term + ".json"

    if is_verbose():
        print "D", url

    r = requests.get(url)
    if r.status_code == 404:
        print """
* \033[1;31mExam schedule not found for requested term.\033[0m
    If the university has published a final exam schedule, contact <\x6e\151chol\141s.p\141u\x6e@\x6d\141\151l.\x6dcg\151ll.c\141>
    to prod the developer and get him to generate the dataset.
        """
        sys.exit(1)
    elif r.status_code != 200:
        print "\033[1;31mFailed to load the exam schedule for requested term.\033[0m"
        sys.exit(1)

    return r.json()

def rewrite_record(record):
    date_1 = dt.strptime(record['date'],iso_date['date'])
    record['date'] = date_1.strftime(config.date_fmt['exam_date'])

    time = dt.strptime(record['time'], iso_date['time']).time()
    record['time'] = time.strftime(config.date_fmt['exam_time'])


    if 'date_2' in record and date_2 != '':
        date_2 = dt.strptime(record['date_2'],iso_date['date'])

        if date_1.month == date_2.month:
            date_2_fmt = date_2.strftime(config.date_fmt['exam_date_continued'])
        else:
            date_2_fmt = date_2.strftime(config.date_fmt['exam_date'])

        record['_datetime'] = [dt.combine(date_1,time),dt.combine(date_2,time)]
        record['date'] += "/" + date_2_fmt
    else:
        record['_datetime'] = [dt.combine(date_1,time)]


    record['_building'] = get_bldg_abbrev(get_bldg_name(record['building']))

    record['_desc'] = record['_note_th'] + " " + record['_note_id']

    return record



def search_exams(sched,(sn,courses)):
    entries = []
    notfound = []
    for course in courses:
        if course not in sched:
            notfound.append({'_code': course, '_reason': 'No final exam found for this course.'})
       	    continue

	entry = sched[course]
	found = False

	for loc in entry['loc']:
 		cmp_f = loc['from']
		sn_f = sn.ljust(len(cmp_f),'A')
	
		if sn_f >= cmp_f:
			cmp_t = loc['to']
			sn_t = sn.ljust(len(cmp_t),'A')
			if sn_t <= cmp_t:
				entry.update(loc) # Flatten for easy report formatting
				found = True
				break

	if found:
		entries.append(rewrite_record(entry))
	else:
		notfound.append({'_code': course, '_reason': "No exam location found for your surname. You're totally sure you're in the course right?"})

	
    return (entries,notfound)

def find_exams(term,return_notfound = True):
    sched = get_exam_sched(term)
    keys =  get_courses(term)
    res =  search_exams(sched,keys)
    if return_notfound:
        return res
    else:
        found,notfound = res
        return found

def final_exam_schedule(term, report = 'exams_default'):
    exams,notfound = find_exams(term,return_notfound = True)

    if exams:
        sched_parse.print_sched_report(exams,report)

    if notfound:
        print ""
        print "* No records for: "
        print ""

        sched_parse.print_sched_report(notfound,'exams_notfound')
