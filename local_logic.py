
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
