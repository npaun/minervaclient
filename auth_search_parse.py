# auth_search_parse.py: Parse course search results to determine CRNs and availability (via the Minerva interface)
# This file is from Minervac, a command-line client for Minerva
# <http://npaun.ca/projects/minervac>
# (C) Copyright 2016-2017 Nicholas Paun

from minerva_common import *
from bs4 import BeautifulSoup

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
		if record['wait']['act'] <= 0:
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

def search_parse(text):
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


