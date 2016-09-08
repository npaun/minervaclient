#!/usr/bin/env python

import requests
import urllib
import sys
#from bs4 import BeautifulSoup

execfile('minerva_parse.py')
execfile('minerva_local_logic.py')
execfile('config.local')

s = requests.Session()
cookie_data = {}
referer = ""



def minerva_get(func):
	print "? " + func
	global referer
	url = "https://horizon.mcgill.ca/pban1/" + func
	r = s.get(url,cookies = cookie_data, headers={'Referer': referer})
	referer = url
	return r

def minerva_post(func,req):
	print "> " + func
	global referer
	url = "https://horizon.mcgill.ca/pban1/" + func
	r = s.post(url,data = req,cookies = cookie_data,headers = {'Referer': referer})
	referer = url
	return r
	


def minerva_login():
	minerva_get("twbkwbis.P_WWWLogin")
	minerva_post("twbkwbis.P_ValLogin",{'sid': id, 'PIN': pin})
	r = minerva_get("twbkwbis.P_GenMenu?name=bmenu.P_MainMnu")
	minerva_get('twbkwbis.P_GenMenu?name=bmenu.P_RegMnu&param_name=SRCH_MODE&param_val=NON_NT')

def make_course_request(term,subjects):
	request = [
			('rsts','dummy'),
			('crn','dummy'), 	# This is the CRN
			('term_in', term), 		# Term of search 
			('sel_day','dummy'),
			('sel_schd','dummy'),
			('sel_insm','dummy'),
			('sel_camp','dummy'),
			('sel_levl','dummy'),
			('sel_sess','dummy'),
			('sel_instr','dummy'),
			('sel_ptrm','dummy'),
			('sel_attr','dummy'),
			('sel_subj','dummy')]

	for subj in subjects: request.append(('sel_subj',subj))
	request.extend([
			('sel_crse',''),	# Course code
			('sel_title',''),
			('sel_schd','%'),
			('sel_from_cred',''),
			('sel_to_cred',''),
			('sel_levl','%'),
			('sel_ptrm','%'),
			('sel_instr','%'),
			('sel_attr','%'),
			('begin_hh','0'),
			('begin_mi','0'),
			('begin_ap','a'),
			('end_hh','0'),
			('end_mi','0'),
			('end_ap','a'),
			('SUB_BTN','Get Course Sections'),
			('path','1')
		])	#This is seriously what Minerva shoves into a search form 

	return urllib.urlencode(request)

def dummy_course_request(term):
	return "rsts=dummy&crn=dummy&term_in=" + term + "&sel_subj=dummy&sel_day=dummy&sel_schd=dummy&sel_insm=dummy&sel_camp=dummy&sel_levl=dummy&sel_sess=dummy&sel_instr=dummy&sel_ptrm=dummy&sel_attr=dummy&sel_crse=&sel_title=&sel_from_cred=&sel_to_cred=&sel_ptrm=%25&begin_hh=0&begin_mi=0&end_hh=0&end_mi=0&begin_ap=x&end_ap=y&path=1&SUB_BTN=Advanced+Search" # Copied and pasted

def minerva_search_courses(term,course_codes):
	subjects = []
	for code in course_codes:
		subjects.append(code.split("-")[0])

	minerva_get("bwskfcls.p_sel_crse_search")
	minerva_post("bwskfcls.bwckgens.p_proc_term_date",{'p_calling_proc': 'P_CrseSearch','search_mode_in': 'NON_NT', 'p_term': term})
	minerva_post("bwskfcls.P_GetCrse",dummy_course_request(term))
	
	
	r = minerva_post("bwskfcls.P_GetCrse_Advanced",make_course_request(term,subjects))
	return course_search(r.text)

def minerva_get_registered(term):
	minerva_get("bwskfreg.P_AltPin")
	r = minerva_post("bwskfreg.P_AltPin",{'term_in': term})
	return r.text

def minerva_reg_courses(text,crns):
	request = quick_add_insert(text,crns)
	r = minerva_post('bwckcoms.P_Regs',request)
	result = quick_add_status(r.text)
	if result == MinervaError.reg_wait:
		wait_request = quick_add_wait(r.text)
		r = minerva_post('bwckcoms.P_Regs',wait_request)
		result = quick_add_status(r.text)
	elif result == MinervaError.reg_fail:
		sys.exit(MinervaError.reg_fail)

def minerva_check_courses(courses,codes,require_all = False,require_reg = False):
	crns = []

	for code in codes:
		valid_state = False

		if code not in courses:
			print "* Course %s cannot be found. Failure." % code
			sys.exit(MinervaError.course_not_found)

		course = courses[code]
		sys.stdout.write("[" + code + "] ")

		if course['select'] == MinervaState.possible:
			sys.stdout.write("* Minerva permits registration ")
			if course['_state'] == MinervaState.register:
				sys.stdout.write("in course.\n")
				valid_state = True
			elif course['_state'] == MinervaState.wait:
				sys.stdout.write("on waitlist.\n")
				valid_state = True
				print "\t\t You will be in position " + str(course['wait']['act'] + 1) + "."
			elif course['_state'] == MinervaState.wait_places_remaining:
				sys.stdout.write("on waitlist, and places remain in the course.\n")
				valid_state = True
				print "\t\t You will be in position " + str(course['wait']['act'] + 1) + "."
			elif course['_state'] == MinervaState.full:
				sys.stdout.write("but waitlist is reported full.\n")
			elif course['_state'] == MinervaState.full_places_remaining:
				sys.stdout.write("but waitlist is reported full (places remain in the class).\n")
			else:
				sys.stdout.write("but the current state is unexpected.\n")

			if not require_reg or (require_reg and valid_state):
				crns.append(course['crn'])
		else:
			print "* Minerva prohibits registration."
			print "\t\t The status on Minerva is " + course['status'] 


	if require_all and len(courses) != len(crns):
		print "* Some courses cannot be registered. The require all constraint is unsatisfiable."
		sys.exit(MinervaError.require_unsatisfiable)
	elif len(crns) == 0:
		print "* No courses can be registered. Failure."
		sys.exit(MinervaError.course_none)

	return crns

# Attempts to register for a course by CRN without checking for room
# Example: minerva_fast_register('201609',['814'])
def minerva_fast_register(term,crns):
	minerva_login()
	courses = minerva_get_registered(term)
	minerva_reg_courses(courses,crns)

# Attempts to register for a course by course code, first checking for room in the course
# Example: minerva_check_register('201609',['COMP-206-001','MATH-240-001'])
def minerva_check_register(term,course_codes,require_all = False,require_reg = False):
	minerva_login()
	courses = minerva_search_courses(term,course_codes)
	crns = minerva_check_courses(courses,course_codes,require_all,require_reg)
	current = minerva_get_registered(term)
	minerva_reg_courses(current,crns)


#vi: ft=python
