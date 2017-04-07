# exams.py: Handler for requests for final exam schedules
# This file is from Minervac, a command-line client for Minerva
# <http://npaun.ca/projects/minervac>
# (C) Copyright 2016-2017 Nicholas Paun

import requests
from minerva_common import *
import exams_parse,exams_ics



def final_exams(term,report = 'exams_default',calendar = False):
	if calendar:
		exams_ics.export_schedule(term,report)
	else:
		exams_parse.final_exam_schedule(term,report)


