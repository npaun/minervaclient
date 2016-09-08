
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
