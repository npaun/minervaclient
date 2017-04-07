# transcript.py: Handler for transcript-related commands.
# This file is from Minervac, a command-line client for Minerva
# <http://npaun.ca/projects/minervac>
# (C) Copyright 2016-2017 Nicholas Paun

import requests
from minerva_common import *
import transcript_parse

def get_transcript(terms = None,report = 'transcript_default',show = ['summary','credit','grades']):
    minerva_login()
    minerva_records_menu()
    r = minerva_get("bzsktran.P_Display_Form?user_type=S&tran_type=V")
    transcript_parse.transcript_report(r.text,terms,report,show)
