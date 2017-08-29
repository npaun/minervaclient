# minerva_common.py: Common functions and definitions for working with Minerva
# This file is from Minervac, a command-line client for Minerva
# <http://npaun.ca/projects/minervac>
# (C) Copyright 2016-2017 Nicholas Paun

import config,credentials_local
import requests,sys
import datetime
from datetime import datetime as dt

cookie_data = {}
referer = ""
s = requests.Session()

def minerva_get(func):
	if verbose:
		sys.stderr.write("? " + func + "\n")

	global referer
	url = "https://horizon.mcgill.ca/pban1/" + func
	r = s.get(url,cookies = cookie_data, headers={'Referer': referer})
	referer = url
	return r

def minerva_post(func,req):
	if verbose:
		sys.stderr.write("> " + func + "\n")

	global referer
	url = "https://horizon.mcgill.ca/pban1/" + func
	r = s.post(url,data = req,cookies = cookie_data,headers = {'Referer': referer})
	referer = url
	return r

def minerva_login():
	minerva_get("twbkwbis.P_WWWLogin")
	minerva_post("twbkwbis.P_ValLogin",{'sid': credentials_local.id, 'PIN': credentials_local.pin})
	minerva_get("twbkwbis.P_GenMenu?name=bmenu.P_MainMnu")

def minerva_reg_menu():
	minerva_get("twbkwbis.P_GenMenu?name=bmenu.P_StuMainMnu")
	minerva_get('twbkwbis.P_GenMenu?name=bmenu.P_RegMnu&param_name=SRCH_MODE&param_val=NON_NT')

def minerva_records_menu():
	minerva_get("twbkwbis.P_GenMenu?name=bmenu.P_StuMainMnu")
	minerva_get("twbkwbis.P_GenMenu?name=bmenu.P_AdminMnu")

class MinervaState:
        register,wait,closed,possible,unknown,wait_places_remaining,full,full_places_remaining,only_waitlist_known = range(9)
class MinervaError:
	reg_ok,reg_fail,reg_wait,course_none,course_not_found,user_error,net_error,require_unsatisfiable = range(8)


def get_term_code(term):
	part_codes = {'FALL': '09', 'FALL-SUP': '10', 'WINTER': '01', 'WINTER-SUP': '02', 'SUMMER': '05', 'SUMMER-SUP': '06'}
	if term == "PREVIOUSEDUCATION":
		return '000000' # Sort first
	elif term.isdigit(): # Term code
		return term
	elif term[0].isdigit(): #Year first
		year = term[0:4]
		if term[4] == '-':
			part = term[5:]
		else:
			part = term[4:]
		part = part_codes[part.upper()]

	else:
		year = term[-4:]
		if term[-5] == '-':
			part = term[:-5]
		else:
			part = term[:-4]
		
		part = part_codes[part.upper()]

	return year + part

def get_status_code(status,short = False):
	if short:
            status_codes = {'Registered': 'R','Web Registered': 'R','(Add(ed) to Waitlist)': 'WL', 'Web Drop': 'DROP','Web Withdrawn Course': 'W'}
	else:
            status_codes = {'Registered': 'R','Web Registered': 'RW','(Add(ed) to Waitlist)': 'LW', 'Web Drop': 'DW', 'Web Withdrawn Course': 'WW'}

	return status_codes[status] if status in status_codes else status

def get_type_abbrev(type):
	types = {'Lecture': 'Lec','Tutorial': 'Tut','Conference': 'Conf','Seminar': 'Sem','Laboratory': 'Lab','Student Services Prep Activity': 'StudSrvcs'}
	if type in types:
		return types[type]
	else:
		return type

# Doesn't really do much. Just tries a few tricks to shorten the names of buildings
def get_bldg_abbrev(location):
        subs = {
                'Building': '', 'Hall': '', 'Pavilion': '','House': '','Centre': '', 'Complex': '',
                'Library': 'Lib.', 'Laboratory': 'Lab.',
                'Biology': 'Bio.', 'Chemistry': 'Chem.',' Physics': 'Phys.', 'Engineering': 'Eng.', 'Anatomy': 'Anat.', 'Dentistry': 'Dent.', 'Medical': 'Med.', 'Life Sciences': 'Life Sc.'
        }

	for sub in subs:
		location = location.replace(sub,subs[sub])

	return location

def get_minerva_weekdays(weekend = False):
	if weekend:
		return ['M','T','W','R','F','S','U']
	else:
		return ['M','T','W','R','F']

def get_real_weekday(minerva_day):
	return get_real_weekday.map[minerva_day]
get_real_weekday.map = {'M': 'Monday','T':'Tuesday','W': 'Wednesday','R': 'Thursday','F': 'Friday','S': 'Saturday','U': 'Sunday'}

def get_ics_weekday(minerva_day):
	return {'M': 'MO','T': 'TU','W': 'WE','R': 'TH','F': 'FR','S': 'SA', 'U': 'SU'}[minerva_day]

def minervac_sanitize(text):
	return text.encode('ascii','ignore')

def get_degree_abbrev(degree):
	subs = {
		'Bachelor of Science': 'BSc',
		'Master of Science': 'MSc',
		'Master of Science, Applied': 'MScA',
		'Bachelor of Arts': 'BA',
		'Master of Arts': 'MA',
		'Bachelor of Arts and Science': 'BAsc',
		'Bachelor of Engineering': 'BEng',
		'Bachelor of Software Engineering': 'BSE',
		'Master of Engineering': 'MEng',
		'Bachelor of Commerce': 'BCom',
		'Licentiate in Music': 'LMus',
		'Bachelor of Music': 'BMus',
		'Master of Music': 'MMus',
		'Bachelor of Education': 'BEd',
		'Master of Education': 'MEd',
		'Bachelor of Theology': 'BTh',
		'Master of Sacred Theology': 'STM',
		'Master of Architecture': 'MArch',
		'Bachelor of Civil Law': 'BCL',
		'Bachelor of Laws': 'LLB',
		'Master of Laws': 'LLM',
		'Bachelor of Social Work': 'BSW',
		'Master of Social Work': 'MSW',
		'Master of Urban Planning': 'MUP',
		'Master of Business Administration': 'MBA',
		'Master of Management': 'MM',
		'Bachelor of Nursing (Integrated)': 'BNI',
		'Doctor of Philosophy': 'PhD',
		'Doctor of Music': 'DMus'
	} #Most of these degrees probably won't work with minervac, but this list may be slightly useful
	for sub in subs:
		degree = degree.replace(sub,subs[sub])
	
	return degree

def get_program_abbrev(program):
	program = program.replace('Major Concentration','Major').replace('Minor Concentration','Minor') #Who cares?
	majors = []
	minors = []
	other = []

	for line in program.split("\n"):
		if line.startswith("Major"):
			majors.append(line.split("Major ")[1])
                elif line.startswith("Honours"):
                        majors.append(line)
		elif line.startswith("Minor"):
			minors.append(line.split("Minor ")[1])
		else:
			other.append(line)

	
	program = ", ".join(majors)
	if minors:
		program += "; Minor " + ", ".join(minors)
	if other:
		program += " [" + ", ".join(other) + "]"

	return program

def get_grade_explanation(grade,normal_grades = False):
	explanation = {
		'HH': 'To be continued',
		'IP': 'In progress',
		'J': 'Absent',
		'K': 'Incomplete',
		'KE': 'Further extension granted',
		'K*': 'Further extension granted',
		'KF': 'Incomplete - Failed',
		'KK': 'Completion requirement waived',
		'L': 'Deferred',
		'LE': 'Deferred - extension granted',
		'L*': 'Deferred - extension granted',
		'NA': 'Grade not yet available',
		'&&': 'Grade not yet available',
		'NE': 'No evaluation',
		'NR': 'No grade reported by the instructor (recorded by the Registrar)',
		'P': 'Pass',
		'Q': 'Course continues in following term',
		'R': 'Course credit',
		'W': 'Permitted to withdraw',
		'WF': 'Withdraw - failing',
		'WL': 'Faculty permission to withdraw from a deferred examination',
		'W--': 'No grade: student withdrew from the University',
		'--': 'No grade: student withdrew from the University',
		'CO': 'Complete [Academic Integrity Tutorial]',
		'IC': 'Incomplete [Academic Integrity Tutorial]'
	}

	normal_explanation = {
		'A': '85 - 100',
		'A-': '80 - 84',
		'B+': '75 - 79',
		'B': '70 - 74',
		'B-': '65 - 69',
		'C+': '60 - 64',
		'C': '55 - 59',
		'D': '50 - 54',
		'F': '0 - 49',
		'S': 'Satisfactory',
		'U': 'Unsatisfactory'
	}

	if normal_grades:
		explanation.extend(normal_explanation)

	if grade in explanation:
		return explanation[grade]
	else:
		return ''

def lg_to_gpa(letter_grade):
	return {'A': '4.0','A-': '3.7','B+': '3.3', 'B': '3.0', 'B-': '2.7', 'C+': '2.3', 'C': '2.0','D': '1.0','F': '0'}[letter_grade]

verbose = False
def set_loglevel(set_verbose):
	global verbose
	verbose = set_verbose

def is_verbose():
    global verbose
    return verbose

def dequebecify(input):
    # From <http://stackoverflow.com/questions/517923>
    # This function only transliterates French diacritics.
    # If you need to separate Quebec from Canada, try:
    # roc,qc = canada.sovereignty_referendum('quebec')

    import unicodedata
    return ''.join(c for c in unicodedata.normalize('NFD', input)
            if unicodedata.category(c) != 'Mn')

def fetch_buildings_table():
    repo = config.data_source[0]
    url = repo + "buildings.json"

    if is_verbose():
        print "D", url

    print "Downloading buildings database....."

    r  = requests.get(url)
    if r.status_code != 200:
        print "\033[1;31mFailed to download buildings table."
        sys.exit(1)

    f = open('buildings.json','w')
    f.write(r.text.encode('UTF-8'))
    f.close()


def get_bldg_name(code):
    import json
    try:
        f = open('buildings.json')
    except Exception:
        fetch_buildings_table()
        return get_bldg_name(code)

    buildings = json.loads(f.read())

    if code in buildings:
        return buildings[code]['name']
    else:
        return code #If we don't know, just stick with what we have


iso_date  = {
        'date': '%Y-%m-%d',
        'time': '%H:%M',
        'full': '%Y%m%dT%H%M%S'
}

minerva_date = {
        'date': '%b %d, %Y',
        'time': '%I:%M %p',
        'full': '%b %d, %Y %I:%M %p'
}
