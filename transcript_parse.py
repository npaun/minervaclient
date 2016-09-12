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
        text = text.replace("&nbsp;"," ")
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

                    heading  = cells[0].span.b
                    if heading:
                        try:
                            term = get_term_code(heading.text.replace(" ",""))
                        except KeyError:
                            term = heading.text

                        transcript[term] = {'grades': [],'summary': {}}
                    elif cells[0].span.text.startswith('Standing'):
                        nil,standing_text = cells[0].span.text.split(":")
                        transcript[term]['summary']['standing'] = standing_text.strip()
            else:
                if term:
                    transcript[term]['grades'].append(parse_record(cells))


        transcript_report(transcript)

def transcript_report(trans):
    term = trans['201509']

    print term['summary']['standing']

    for entry in term['grades']:
        print entry['course'], '\t' ,entry['credits'],entry['grade']


f = open('/home/np//minervaslammer/unofficial.html').read()

parse_transcript(f)

