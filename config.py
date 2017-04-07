# config.py: Minervac default configuration file
# This file is from Minervac, a command-line client for Minerva
# <http://npaun.ca/projects/minervac>
# (C) Copyright 2016-2017 Nicholas Paun

#### Datasets
data_source = ['http://cs.mcgill.ca/~npaun/mnvc-data/'] # Where should common datasets be downloaded from? There is only one option for now.


#### Formatting
date_fmt = {
        'short_date': '%-m/%-d', # Short date
        'short_datetime': '%-m/%-d %-H:%-M', # Short date and time
        'short_time': '%Hh%M', # Quebec style time format
        'full_date': '%Y-%m-%d', # ISO date format
        'exam_date': '%a, %b %e', # Provides day of the week, abbreviated month and day
        'exam_date_continued': '(%a) %-d', # When two day exams are scheduled
        'exam_time': '%-l:%M %p' # Starting time for exams
        }
show_weekend = False # When generating timetables, should the weekend be shown? (Do you have weekend courses?)

#### Reports

reports = {
            ### long, short, default: For standard course schedule reports, containing various amounts of detail.
            'long': {
                        'columns': ['subject','course','credits','section','type','crn','days','time_range','_building','_room','_instructor_sn','_action_desc'],
                        'format': "%s %s (%s)\t%s (%s)\t% 5s\t\t% 3s %s\t\t%-16.16s %s\t\t%-16.24s\t%s\n",
                        'sort': ['_day_idx','time_range','_code']
            },

            'default': {
                        'columns': ['subject','course','credits','section','type','crn','days','time_range','_action_desc'],
                        'format': "%s %s (%s)\t%s (%s)\t% 5s\t\t% 3s %s\t%s\n",
                        'sort': ['_day_idx','time_range','_code']
            },

            'short': {
                        'columns': ['subject','course','credits','section','crn','_action_desc'],
                        'format': "%s %s (%s)\t%s\t% 5s\t%s\n",
                        'sort': ['_code']
            },

            ### conflicts: For displaying course conflicts to the user.
            'conflicts': {
                            'columns': ['_code','type','crn','days','time_range','_building','_room','_action_desc'],
                            'format': "\t%s (%s)\t% 5s\t\t% 3s \033[1;31m%s\033[0m\t\t%-16.16s %s %s\n",
                            'sort':  None # A different algorithm is used to find conflicts
            },

            ### timetable_default: Formats information for each course's timetable cell (in HTML)
            'timetable_default': {
                                    'columns': ['subject','course','section','type','_link_gmaps','_building','_room','time_range','_action_desc'],
                                    'format': """
<p class='sched-course'>%s %s&ndash;%s (%s)</p>
<p class='sched-location'><a href='%s' title='Get directions to this building'>%s %s</a></p>
<p class='sched-time'>%s</p>
<p class='sched-action-desc'>%s</p>
                                    """,
                                    'sort':  ['days','time_range','_code']
            },

            ### cal_default: The first element stores the entry title and the second its description
            'cal_default': {
                            'columns': [
                                        ['subject','course','type','_action_desc'],
                                        ['_code','instructor','crn','_action_desc']
                            ],
                            'format': [
                                        "%s %s (%s) %s",
                                        "%s\\nInstructor: %s\\nCRN: %s\\n%s"
                            ],
                            'sort': None #Let the calendar program deal with this
            },

            ### transcript_{long,default,short}: Standard reports for the unofficial transcript
            ### Elements: [0] Program information, [1] Term results [2] Course grades
            'transcript_long': {
                                'columns': [
                                            ['term','status','year','_program'],
                                            ['term_att','term_earned','cumm_att','cumm_earned','tgpa','term_incl','cgpa','transfer_credits','standing'],
                                            ['status','remarks','_code','credits_earned','credits','grade','class_avg','_grade_desc']
                                ],
                                'format': [
                                            "\n\033[1m%s:\033[0m [%s]\nU%s %s\n",
                                            "%s/%s credits earned (%s/%s total)\tGPA: %s [%s cr.] (%s overall)\nTransfer credits: %s\t\t\tStanding: %s\n",
                                            "%s %s\t%s\t% 1s | % 1s\t\t%- 2s . %- 2s\t\t%s\n"
                                ],
                                'sort': ['_code']
            },

            'transcript_default': {
                                    'columns': [
                                                ['term','year','_program'],
                                                ['term_earned','cumm_earned','transfer_credits','tgpa','cgpa'],
                                                ['subject','course','credits_earned','credits','grade','class_avg','remarks','_grade_desc']
                                    ],
                                    'format': [
                                                "\n\033[1m%s:\033[0m\nU%s %s\n",
                                                "%s credits (%s total) [%s xfer]\tGPA: %s (%s overall)\n",
                                                "%s %s\t% 1s | % 1s\t\t%- 2s . %- 2s\t\t%s %s\n"
                                    ],
                                    'sort': ['_code']
            },

            'transcript_short': {
                                    'columns': [
                                                ['term','year'],
                                                ['term_earned','cumm_earned','tgpa','cgpa'],
                                                ['subject','course','credits_earned','grade','_grade_desc']
                                    ],
                                    'format': [
                                                "\n\033[1m%s\033[0m (U%s)\n",
                                                "Credits: %s (%s)\tGPA: %s/%s\n",
                                                "%s %s\t%s\t%- 2s\t\t%s\n"
                                    ],
                                    'sort': ['_code']
            },

            ### exams_default: A default format for final exam schedules
            'exams_default': {
                                'columns': ['subject','course','section','date','time','_building','room','rows','_desc'],
                                'format': "%s %s (%s)\t\t%s\t@ %- 5s\t\t%-16.16s %-10s\t%-6s\t%s\n",
                                'sort': ['_datetime','_code']
            },

            ### exams_notfound: Used to display courses without final exams, just so you won't forget about them
            'exams_notfound': {
                                'columns': ['_code','_reason'],
                                'format': "%s:\t%s\n",
                                'sort': ['_code']
            },


            ### cal_exams: Used to generate calendar entries for final exam schedules
            'cal_exams': {
                            'columns': [
                                        ['subject','course'],
                                        ['_code','_building','room','rows','_desc','date','time']
                            ],
                            'format': [
                                        '%s %s (FINAL)',
                                        '%s\\nBuilding: %s / Room: %s / Rows: %s\\n%s\\nDate: %s / Time: %s'
                            ],
                            'sort': None # Let the calendar program deal with this.
            }
}



