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
        courses.append(course['_code'])

    return sn,courses

def get_exam_sched(term):
    repo = config.data_source[0]
    url = repo + "exams-" + term + ".json"
    
    if minvera_common.is_verbose():
        print "D?", url
        
    r = requests.get(url)
    if r.status_code == 404:
        print """
* \033[1;31mExam schedule not found for requested term.\033[0m 
    If the university has published a final exam schedule, contact <\x6eicholas.pau\x6e@\x6dail.\x6dcgill.ca> 
    to prod the developer and get him to generate the dataset.
        """
        sys.exit(1)
    elif r.status_code != 200:
        print "\033[1;31mFailed to load the exam schedule for requested term.\033[0m"
        sys.exit(1)

    return r.json()

def rewrite_record(record):
    date_1 = dt.strptime(record['date'],'%Y-%m-%d')
    record['_date_fmt'] = date_1.strftime(config.date_fmt['exam_date'])

    if 'date_2' in record and date_2 != '':
        date_2 = dt.strptime(record['date_2'],'%Y-%m-%d')

        if date_1.month == date_2.month:
            date_2_fmt = date_2.strftime(config.date_fmt['exam_date_continued'])
        else:
            date_2_fmt = date_2.strftime(config.date_fmt['exam_date'])

        record['_date_fmt'] += "/" + date_2_fmt

    
    record['_time_fmt'] = dt.strptime(record['time'], '%H:%M').strftime(config.date_fmt['exam_time'])

    record['_desc'] = record['_note_th'] + " " + record['_note_id']

    return record



def find_exams(sched,(sn,courses)):
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

def final_exam_schedule(term = None, report = 'exams_default'):
    sched = get_exam_sched(term)
    keys =  get_courses(term)
    exams,notfound = find_exams(sched,keys)

    if exams:
        sched_parse.print_sched_report(exams,report)

    if notfound:
        print ""
        print "* No records for: "
        print ""

        sched_parse.print_sched_report(notfound,'exams_notfound')
