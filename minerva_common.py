import credentials_local
import requests

cookie_data = {}
referer = ""
s = requests.Session()

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
	minerva_post("twbkwbis.P_ValLogin",{'sid': credentials_local.id, 'PIN': credentials_local.pin})
	r = minerva_get("twbkwbis.P_GenMenu?name=bmenu.P_MainMnu")
	minerva_get('twbkwbis.P_GenMenu?name=bmenu.P_RegMnu&param_name=SRCH_MODE&param_val=NON_NT')


class MinervaState:
        register,wait,closed,possible,unknown,wait_places_remaining,full,full_places_remaining,only_waitlist_known = range(9)
class MinervaError:
	reg_ok,reg_fail,reg_wait,course_none,course_not_found,user_error,net_error,require_unsatisfiable = range(8)


def get_term_code(term):
	part_codes = {'FALL': '09', 'FALL-SUP': '10', 'WINTER': '01', 'WINTER-SUP': '02', 'SUMMER': '05', 'SUMMER-SUP': '06'}
	if term.isdigit(): # Term code
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
		status_codes = {'Registered': 'R','Web Registered': 'R','(Add(ed) to Waitlist)': 'W', 'Web Drop': 'DROP'}
	else:
		status_codes = {'Registered': 'R','Web Registered': 'RW','(Add(ed) to Waitlist)': 'LW', 'Web Drop': 'DW'}

	return status_codes[status]

def get_type_abbrev(type):
	types = {'Lecture': 'Lec','Tutorial': 'Tut','Conference': 'Conf','Seminar': 'Sem'}
	if type in types:
		return types[type]
	else:
		return type

# Doesn't really do much. Just tries a few tricks to shorten the names of buildings
def get_bldg_abbrev(location):
	subs = {'Building': '','Biology': 'Bio.','Chemistry': 'Chem.','Physics': 'Phys.', 'Engineering': 'Eng.'}
	for sub in subs:
		location = location.replace(sub,subs[sub])

	return location
