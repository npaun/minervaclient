#!/usr/bin/env python

from bs4 import BeautifulSoup
import urllib
import sys
import codecs

class MinervaState:
	register,wait,closed,possible,unknown,wait_places_remaining,full,full_places_remaining = range(8)
class MinervaError:
	reg_ok,reg_fail,reg_wait,course_none,course_not_found,user_error,net_error,require_unsatisfiable = range(8)

def quick_add_insert(text,crns):
	html = BeautifulSoup(text,'html.parser')
	forms = html.body.find_all('form')
	reg = forms[1]
	inputs = reg.find_all(['input','select'])
	request = []


	for input in inputs:
		
		if not input.has_attr('name'): 
			if input.has_attr('id'):
				print "This is an actual problem"
			else: 
				continue

		
		if input.has_attr('value'): #This should always fail for a select.
			val = input['value']
		else:
			val = ''

		if val == 'Class Search':  #We want to register and not search,
			continue

		if crns and input['name'] == 'CRN_IN' and val == '':  # Shove our CRN in the first blank field
			val = crns.pop(0)

		request.append((input['name'], val))
	
	
	return urllib.urlencode(request)

def quick_add_status(text):
	html = BeautifulSoup(text,'html.parser')
	errtable = html.body.find('table',{'summary':'This layout table is used to present Registration Errors.'})
	if errtable is not None:
			error = errtable.findAll('td',{'class': "dddefault"})[0].a.text
			if error.startswith("Open"):
				print "* Must enter the waitlist section."
				return MinervaError.reg_wait
			else:	
				print "\033[1m* Failed to register: \033[0m " + str(error)
				return MinervaError.reg_fail
	

	print "\033[1m* Registration probably suceeded.\033[0m"
	return MinervaError.reg_ok

def quick_add_wait(text):
	html = BeautifulSoup(text,'html.parser')
	forms = html.body.find_all('form')
	reg = forms[1]
	inputs = reg.find_all(['input','select'])
	request = []


	for input in inputs:
		
		if not input.has_attr('name'): 
			if input.has_attr('id'):
				print "This is an actual problem"
			else: 
				continue

		
		if input.has_attr('value'): #This should always fail for a select.
			val = input['value']
		else:
			val = ''


		if input.has_attr('id') and input['id'].startswith('waitaction'):
			val = 'LW'

		request.append((input['name'], val))
	
	print request	
	return urllib.urlencode(request)

def parse_entry(cells):

	if cells is None:
		return None

	if len(cells) < 20:
		return None

	record = {}
	if cells[0].abbr is not None and cells[0].abbr.text == "C":
		record['select'] = MinervaState.closed
	else:
		record['select'] = MinervaState.possible

	keys = ['crn','subject','course','section','type','credits','title','days','time']
	for cell,key in zip(cells[1:9],keys):
		cell = cell.text.encode('ascii','ignore')  # Because this stuff is used elsewhere in the program
		if cell == ' ': cell = None
		record[key] = cell

	record['reg'] = {}
	reg_keys = ['cap','act','rem']
	for cell,key in zip(cells[10:13],reg_keys):
		cell = cell.text
		if not cell.isdigit(): cell = -1000
		record['reg'][key] = int(cell)

	record['wait'] = {}
	wait_keys = ['cap','act','rem']	
	for cell,key in zip(cells[13:16],wait_keys):
		cell = cell.text
		if not cell.isdigit(): cell = -1000
		record['wait'][key] = int(cell)
		
	
	keys = ['instructor','date','location','status']
	for cell,key in zip(cells[16:],keys):
		cell = cell.text
		if cell == ' ': cell = None
		record[key] = cell
	
	return record

def determine_state(record):
	if record['select'] == MinervaState.closed:
		record['_state'] = record['select']
	elif record['reg']['rem'] > 0:
		if record['wait']['act'] < 0:
			record['_state'] = MinervaState.register
		elif record['wait']['rem'] > 0:
			record['_state'] = MinervaState.wait_places_remaining
		else:
			record['_state'] = MinervaState.full_places_remaining
	elif record['wait']['rem'] > 0:
			record['_state'] = MinervaState.wait
	elif record['wait']['rem'] <= 0:
			record['_state'] = MinervaState.full
	else:
			record['_state'] = MinervaState.unknown

def course_search(text):
	text = text.replace('&nbsp;',' ') # This is really dumb, but I don't want know how Python handles Unicode
	html = BeautifulSoup(text,'html.parser')
	table = html.body.find('table',{'summary':'This layout table is used to present the sections found'})
	tr = table.findAll('tr')[2:]
	records = {}
	for row in tr:
		cells = row.findAll('td')
		record = parse_entry(cells)

		if record is None:
			continue
		elif record['subject'] is None: #This is notes, or additional days. I don't care about it right now
			continue
			
		record['_code'] = record['subject'] + "-" + record['course'] + "-" + record['section']

		determine_state(record)

		records[record['_code']] = record
	
	return records


