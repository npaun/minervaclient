# pub_search.py: Search for available places in requested courses (via the Display Dynamic Schedule interface)
# This file is from Minervac, a command-line client for Minerva
# <http://npaun.ca/projects/minervac>
# (C) Copyright 2016-2017 Nicholas Paun

import requests,urllib,StringIO,csv,sys
from minerva_common import *

def build_request(term,codes):
	req = [
	('sel_crse',''),
	('sel_title',''),
	('begin_hh','0'),
	('begin_mi','0'),
	('begin_ap','a'),
	('end_hh','0'),
	('end_mi','0'),
	('end_ap','a'),
	('sel_dunt_code',''),
	('sel_dunt_unit',''),
	('sel_from_cred',''),
	('sel_to_cred',''),
	('sel_coll',''),
	('call_value_in','UNSECURED'),
	('display_mode_in','LIST'),
	('search_mode_in',''),
	('term_in',term),
	('sel_subj','dummy'),
	('sel_day','dummy'),
	('sel_ptrm','dummy'),
	('sel_ptrm','%'),
	('sel_camp','dummy'),
	('sel_schd','dummy'),
	('sel_schd','%'),
	('sel_sess','dummy'),
	('sel_instr','dummy'),
	('sel_instr','%'),
	('sel_attr','dummy'),
	('sel_attr','%'),
	('crn','dummy'),
	('rsts','dummy'),
	('sel_levl','dummy'),
	('sel_levl','%'),
	('sel_insm','dummy'),
	]

	for code in codes:
		req.append(('sel_subj',code.split("-")[0]))
	
	return urllib.urlencode(req)

def search(term,course_codes):
	request = build_request(term,course_codes)
	sys.stderr.write("> bwckgens.csv\n")
	result = requests.post("https://horizon.mcgill.ca/rm-PBAN1/bwckgens.csv",request)
	return parse_results(result.text)


def parse_results(text):
	stream = StringIO.StringIO(text.encode("ascii","ignore"))
	field_names = ['crn','subject','course','section','type','credits','title','days','time','cap','wl_cap','wl_act','wl_rem','instructor','date','location','status']
	file = csv.DictReader(stream,field_names)

	records = {}
	first = True
	for row in file:
		if row['subject'] is None or row['subject'] == 'Subject':
			continue

		if row['cap'] == '':
			continue

		if row['wl_rem'] == '':
			row['wl_rem'] = -1000

		row['_code'] = "-".join([row['subject'],row['course'],row['section']])
		row['select'] = MinervaState.only_waitlist_known

		row['reg'] = {}
		row['reg']['cap'] = int(row['cap'])
		
		row['wait'] = {}
		row['wait']['cap'] = int(row['wl_cap'])
		row['wait']['act'] = int(row['wl_act'])
		row['wait']['rem'] = int(row['wl_rem'])

		if row['wait']['rem'] > 0:
			row['_state'] = MinervaState.wait
		else:
			row['_state'] = MinervaState.unknown

		records[row['_code']] = row

	
	return records
