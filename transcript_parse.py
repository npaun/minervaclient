from bs4 import BeautifulSoup
from minerva_common import *
import sys
import re

print "Can't see this" #

def parse_record(cells):
    fields = ['status','course','section','title','credits','unknown','grade','remarks','unknown2','credits_earned','class_avg']
    record = {}
  
    for field,cell in zip(fields,cells):
        record[field] =  cell.text.strip()

    record['_grade_desc'] = get_grade_explanation(record['grade'])

    return record

def parse_init_block(text,heading):
    prev_degree = heading.text.split("\n")[-1]
    info = {'year': '', 'degree': prev_degree, '_program': ''}
    
    for line in text.split("\n"):
        if line.startswith("Credits Required"):
            info['program_group'],info['program_credits'] = re.match("Credits Required for (.*?) *- *(.*?) credits",line).groups()
        elif line.endswith("Scholarship"):
            info['scholarship'] = line.rsplit(" ",1)[0]

    return info

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

def parse_gpa_block(table,init):
    cells = table.find_all('tr')[1:]
    gpa = {}
    term_fields = ['nil','tgpa','transfer_credits','nil','term_att','term_earned','term_incl','term_points']
    cumm_fields = ['nil','cgpa','nil','total_credits','nil','cumm_att','cumm_earned','cumm_incl','cumm_points']
    credit_fields = ['transfer_credits','total_credits','term_att','term_earned','term_incl','cumm_att','cumm_earned','cumm_incl']
    
    for cell,field in zip(cells[0].find_all('td'),term_fields):
        gpa[field] = cell.text.strip()


    for cell,field in zip(cells[1].find_all('td'),cumm_fields):
        gpa[field] = cell.text.strip()


    for field in gpa:
        if field in credit_fields:
            gpa[field] = gpa[field].replace('.00','')

    gpa['_mcgill_credits'] = int(gpa['total_credits']) - int(gpa['transfer_credits']) 
    gpa['_term_fail'] = int(gpa['term_att']) - int(gpa['term_earned'])
    gpa['_cumm_fail'] = int(gpa['term_att']) - int(gpa['term_earned'])
    gpa['_credits_remaining'] = int(init['program_credits']) - int(gpa['cumm_earned'])
    gpa['_credits_percent'] = int(round((float(gpa['cumm_earned']) / float(init['program_credits']) * 100),0))


    return gpa

def parse_transcript(text):
        text = text.replace("&nbsp;"," ").replace("<br>","\n")
	html = BeautifulSoup(text,'html.parser')
        transcript = {}
	term = None
        tables = html.body.find_all('table',{'class': 'dataentrytable'})
        tbl_personal = tables[0]
        tbl_transcript = tables[1]
        trans_rows = tbl_transcript.tbody.find_all('tr',recursive=False)

        for row in trans_rows:
            cells = row.find_all('td',recursive=False)
            if len(cells) == 1:
                if cells[0].table:
                    curr['gpa'] = parse_gpa_block(cells[0].table,transcript['000000']['info'])
                else:
                    if not cells[0].span:
                        continue

                    text = cells[0].span.text

                    if cells[0].span.b:
                        heading = cells[0].span
                        try:
                            term = get_term_code(heading.b.text.replace(" ",""))
                        except KeyError:
                            term = heading.b.text
                        transcript[term] = {'grades': [],'summary': {}}
                        curr = transcript[term]
                    elif text.startswith('Standing'): #This is your term standing
                        nil,standing_text = text.split(":")
                        curr['summary']['standing'] = standing_text.strip()
                    elif "\n" in text: #This is the degree block
                        if term == '000000':
                            curr['info'] = parse_init_block(text,heading)
                        else:
                            curr['info'] = parse_info_block(text)
            else:
                if term:
                    curr['grades'].append(parse_record(cells))


        transcript_report(transcript)

def transcript_report(trans):
    for term in sorted(trans.keys()):

        info = trans[term]['info']
        print "%s\nU%s %s %s" % (term,info['year'], info['degree'], info['_program'])
        
        if 'gpa' in trans[term]:
            gpa = trans[term]['gpa']
            print u'\t\t\tCredits: +%s, \u03a3%s, %s%%;\tGPA: %s, \u03a3%s' % (gpa['term_earned'],gpa['cumm_earned'],gpa['_credits_percent'],gpa['tgpa'],gpa['cgpa'])

        for entry in trans[term]['grades']:
            print "% 3s\t%s %s\t\t% 1s | %s\t\t%- 2s | %- 2s\t\t%s" % (entry['status'],entry['course'],entry['section'],entry['credits_earned'],entry['credits'],entry['grade'],entry['class_avg'],entry['_grade_desc'])

        print ""

f = open('/home/np//minervaslammer/unofficial.html').read()

parse_transcript(f)

