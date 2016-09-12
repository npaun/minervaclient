from bs4 import BeautifulSoup
from minerva_common import *
import sys

def parse_record(cells):
    fields = ['status','course','section','title','credits','unknown','grade','remarks','unknown2','credits_earned','class_avg']
    record = {}
  
    for field,cell in zip(fields,cells):
        record[field] =  cell.text.strip()

    record['_grade_desc'] = get_grade_explanation(record['grade'])

    return record

def parse_info_block(text): #This is the explanation of the degree and year
        degree,year_status,program = text.split("\n",2)

        info_block = {}
        info_block['degree'] = get_degree_abbrev(degree)
        year_status = year_status.split(" ")
        info_block['year'] = year_status[-1]
        info_block['status'] = year_status[0]
        info_block['programs'] = program.replace("\n",", ")
        info_block['_program'] = get_program_abbrev(program)

        return info_block
   

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
                        curr['info'] = parse_info_block(text)
            else:
                if term:
                    curr['grades'].append(parse_record(cells))


        transcript_report(transcript)

def transcript_report(trans):
    for term in sorted(trans.keys()):

        info = trans[term]['info']
        print '\033[1m', term, '\033[0m', '(' + info['status'] + ')'
        print "U%s %s %s" % (info['year'], info['degree'], info['_program'])

        for entry in trans[term]['grades']:
            print "% 3s\t%s %s\t\t% 1s | %s\t\t%- 2s | %- 2s\t\t%s" % (entry['status'],entry['course'],entry['section'],entry['credits_earned'],entry['credits'],entry['grade'],entry['class_avg'],entry['_grade_desc'])

        print ""

f = open('/home/np//minervaslammer/unofficial.html').read()

parse_transcript(f)

