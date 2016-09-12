from bs4 import BeautifulSoup
from minerva_common import *
import sys

def parse_record(cells):
    fields = ['status','course','section','title','credits','unknown','grade','remarks','unknown2','credits_earned','class_avg']
    record = {}
  
    for field,cell in zip(fields,cells):
        record[field] =  cell.text.strip()


    return record

def parse_transcript(text):
        text = text.replace("&nbsp;"," ").replace("<br>","\n")
	html = BeautifulSoup(text,'html.parser')
        transcript = {}
	term = None
        tables = html.body.find_all('table',{'class': 'dataentrytable'})
        tbl_personal = tables[0]
        tbl_transcript = tables[1]

        for row in tbl_transcript.tbody.find_all('tr',recursive=False):
            cells = row.find_all('td',recursive=False)
            if len(cells) == 1:
                if cells[0].table:
                    print "GPA"
                else:
                    if not cells[0].span:
                        continue

                    heading  = cells[0].span.b
                    text = cells[0].span.text

                    if heading:
                        try:
                            term = get_term_code(heading.text.replace(" ",""))
                        except KeyError:
                            term = heading.text

                        transcript[term] = {'grades': [],'summary': {}}
                        curr = transcript[term]
                    elif text.startswith('Standing'): #This is your term standing
                        nil,standing_text = text.split(":")
                        curr['summary']['standing'] = standing_text.strip()
                    elif "\n" in text: #This is the degree block
                        degree,year_status,program = text.split("\n",2)
                        info_block = {}
                        info_block['degree'] = get_degree_abbrev(degree)
                        year_status = year_status.split(" ")
                        info_block['year'] = year_status[-1]
                        info_block['status'] = year_status[0]
                        info_block['programs'] = program.replace("\n",", ")
                        info_block['_program'] = info_block['degree'] + " " + get_program_abbrev(program)

                        print info_block
                        curr['info'] = info_block
            else:
                if term:
                    curr['grades'].append(parse_record(cells))


        transcript_report(transcript)

def transcript_report(trans):
    print trans.keys()
    term = trans['201509']

    print term['summary']['standing']

    for entry in term['grades']:
        print entry['course'], '\t' ,entry['credits'],entry['grade']


f = open('/home/np//minervaslammer/unofficial.html').read()

parse_transcript(f)

