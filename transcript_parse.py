from bs4 import BeautifulSoup
from minerva_common import *
import sys
import re
import config
import sched_parse

def parse_record(cells):
    fields = ['status','course','section','title','credits','unknown','grade','remarks','unknown2','credits_earned','class_avg']
    record = {}
  
    for field,cell in zip(fields,cells):
        record[field] =  cell.text.strip()

    record['_grade_desc'] = get_grade_explanation(record['grade'])

    return record

def parse_init_block(text,heading):
    prev_degree = heading.text.split("\n")[-1]
    info = {'year': '-', 'degree': prev_degree, '_program': prev_degree}
    
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
                    curr['info'].update(parse_gpa_block(cells[0].table,transcript['000000']['info']))
                else:
                    if not cells[0].span:
                        continue

                    text = cells[0].span.text

                    if cells[0].span.b:
                        heading = cells[0].span
                        term = get_term_code(heading.b.text.replace(" ",""))
                        transcript[term] = {'grades': [],'info': {}}
                        curr = transcript[term]
                        curr['info']['term'] = heading.b.text.strip()

                    elif text.startswith('Standing'): #This is your term standing
                        nil,standing_text = text.split(":")
                        curr['info']['standing'] = standing_text.strip()

                    elif "\n" in text: #This is the degree block
                        if term == '000000': #The "Previous education" block behaves differently
                            curr['info'].update(parse_init_block(text,heading))
                        else:
                            curr['info'].update(parse_info_block(text))
            else:
                if term:
                    curr['grades'].append(parse_record(cells))


        return transcript

def load_transcript_format(report):
        if report not in config.reports:
                print "Error! Report not found"
                sys.exit(MinervaError.user_error)


        report = config.reports[report]
        fmt_1 = (report['columns'][0],report['format'][0])
        fmt_2 = (report['columns'][1],report['format'][1])
        fmt_3 = (report['columns'][2],report['format'][2])

        return (fmt_1,fmt_2,fmt_3)

def transcript_report(trans,terms = None,report = 'transcript_default',show_info = True,show_gpa = True,show_grades = True,show_header = False):
        if not show_header:
                del trans['000000']

        if terms is not None:
                iter = (term for term in terms)
        else:
                iter = (term for term in sorted(trans.keys()))


        for term in iter:
                termv = trans[term]
                (info_fmt,gpa_fmt,grades_fmt) = load_transcript_format(report)
                        
                if show_info:    
                        sys.stdout.write(sched_parse.apply_format(termv['info'],info_fmt))
                
                if show_gpa and 'tgpa' in termv['info']:
                        sys.stdout.write(sched_parse.apply_format(termv['info'],gpa_fmt))


                if show_grades and termv['grades']:
                        sort = config.reports[report]['sort']
                        grades = sched_parse.multi_keysort(termv['grades'],sort)
                        print ""
                        for grade in grades:
                                sys.stdout.write(sched_parse.apply_format(grade,grades_fmt))


f = open('/home/np//minervaslammer/unofficial.html').read()
transcript_report(parse_transcript(f),report = 'transcript_default',show_header=True)


