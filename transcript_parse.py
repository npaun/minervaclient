# transcript_parse.py: Parse unofficial transcripts into an internal representation
# This file is from Minervac, a command-line client for Minerva
# <http://npaun.ca/projects/minervac>
# (C) Copyright 2016-2017 Nicholas Paun

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

    if record['course'] == '':
        return None

    record['subject'],record['course'] = record['course'].split(" ")
    record['_code'] = '-'.join([record['subject'],record['course'],record['section']])

    record['_grade_desc'] = get_grade_explanation(record['grade'])

    return record

def parse_init_block(text,heading):
    prev_degree = heading.text.split("\n")[-1]
    info = {'year': '-', 'degree': prev_degree, '_program': prev_degree,'status': 'General information'}

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

    if len(cells) != 2:
        return {}


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

def parse_transfer(text):
        source,num = re.match("From: (.*)? *- *(.*?) credits",text).groups()
        return {'xfer_source': source, 'xfer_credits': num}

def parse_transfer_credits(table,info):
        fields = ['subject','course','unknown1','unknown2']
        records = []
        source = info['xfer_source']

        for row in table.find_all('tr'):
                record = {'credits_earned': '-','credits': '-','grade': '-','class_avg': '-','_grade_desc': 'Credits/Exemptions: ' + source,'status': '', 'remarks': '','section':'N/A'}
                for cell,field in zip(row.find_all('td'),fields):
                        record[field] = cell.text.strip()

                record['_code'] = '-'.join([record['subject'],record['course']])
                records.append(record)

        return records

def parse_student_block(table):
    info = {}
    label_field = {'Student Name': 'name','Student Name with Preferred First Name': 'name', 'McGill ID': 'sid', 'Permanent Code': 'permcode', 'Advisor(s)': 'advisor'}
    # ^ For students with preferred first names, their name field is displayed differently. For our purposes, we will just treat the preferred name as the name.

    for row in table.find_all('tr'):
        cells = row.find_all('td')
        key_label = cells[0].text.strip()[:-1] # Strip off the colon
        if key_label in label_field: # If we actually want to record this information.
            key = label_field[key_label]

        value = cells[1].text.strip()

        info[key] = value

    info['_sn'],info['_givenName'] = info['name'].split(', ')

    return info

def parse_transcript(text):
        text = text.replace("&nbsp;"," ").replace("<BR>","\n")

	html = BeautifulSoup(text,'html5lib')
        transcript = {}
	term = None
        tables = html.body.find_all('table',{'class': 'dataentrytable'})
        try:
            tbl_transcript = tables[1]
        except IndexError:
            print("Transcript not available. Probably not registered.")
            sys.exit(MinervaError.user_error)
            
        tbl_student = tables[0]
        student_info = parse_student_block(tbl_student) # Just in case someone wants their name, or Permanent code, etc.

        trans_rows = tbl_transcript.tbody.find_all('tr',recursive=False)
        for row in trans_rows:
            cells = row.find_all('td',recursive=False)
            if len(cells) == 1:
                if cells[0].table:
                    first_cell = cells[0].table.tr.td.text
                    if first_cell.startswith(' '):
                        transcript[term]['info'].update(parse_gpa_block(cells[0].table,transcript['000000']['info']))
                    else:
                        curr['grades'].extend(parse_transfer_credits(cells[0].table,curr['info']))
                else:
                    if not cells[0].span:
                        continue

                    text = cells[0].span.text.strip()

                    if cells[0].span.b:
                        heading = cells[0].span
                        term = get_term_code(heading.b.text.replace(" ",""))
                        transcript[term] = {'grades': [],'info': {}}
                        curr = transcript[term]
                        curr['info']['term'] = heading.b.text.strip()

                    elif text == '':
                       continue
                    elif text.startswith('Standing'): #This is your term standing
                        nil,standing_text = text.split(":")
                        curr['info']['standing'] = standing_text.strip()
                    elif text.startswith('From:'): #This is advanced standing stuff
                        curr['info'].update(parse_transfer(text))
                    elif term == '000000':
                        curr['info'].update(parse_init_block(text,heading))
                    elif "\n" in text: #This is the degree block
                        curr['info'].update(parse_info_block(text))
            else:
                if term:
                    record = parse_record(cells)
                    if record is not None:
                        curr['grades'].append(parse_record(cells))


        transcript['000000']['info'].update(student_info)

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

def print_transcript(trans,terms = None,report = 'transcript_default',show = ['summary','credit','grades']):
        if 'header' not in show:
                del trans['000000']

        if terms is not None:
                iter = (term for term in terms)
        else:
                iter = (term for term in sorted(trans.keys()))

        for term in iter:
                termv = trans[term]
                (info_fmt,gpa_fmt,grades_fmt) = load_transcript_format(report)

                if 'summary' in show:
                        sys.stdout.write(sched_parse.apply_format(termv['info'],info_fmt))

                if 'credit' in show and 'tgpa' in termv['info']:
                        sys.stdout.write(sched_parse.apply_format(termv['info'],gpa_fmt))


                if 'grades' in show and termv['grades']:
                        sort = config.reports[report]['sort']
                        grades = sched_parse.multi_keysort(termv['grades'],sort)
                        print ""
                        for grade in grades:
                                sys.stdout.write(sched_parse.apply_format(grade,grades_fmt))

def transcript_report(text,terms = None,report = 'transcript_default',show = ['summary','credit','grades']):
        trans = parse_transcript(text)
        print_transcript(trans,terms,report,show)
