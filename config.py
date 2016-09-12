#### Formatting
date_fmt = {'short_date': '%-m/%-d', 'short_datetime': '%-m/%-d %-H:%-M','short_time': '%Hh%M','full_date': '%Y-%m-%d'}
show_weekend = False

#### Reports
reports = {'long': {},'default': {},'short': {},'conflicts': {},'timetable_default': {},'cal_default': {}}

reports['long']['columns'] = ['subject','course','credits','section','type','crn','days','time_range','_building','_room','instructor','_action_desc']
reports['long']['format'] = "%s %s (%s)\t%s (%s)\t% 5s\t\t% 3s %s\t\t%-16.16s %s\t\t%-16.24s\t%s\n"
reports['long']['sort'] = ['_day_idx','time_range','_code']

reports['default']['columns'] = ['subject','course','credits','section','type','crn','days','time_range','_action_desc']
reports['default']['format'] = "%s %s (%s)\t%s (%s)\t% 5s\t\t% 3s %s\t%s\n"
reports['default']['sort'] = ['_code']

reports['short']['columns'] = ['subject','course','credits','section','crn','_action_desc']
reports['short']['format'] = "%s %s (%s)\t%s\t% 5s\t%s\n"
reports['short']['sort'] = ['_code']

reports['conflicts']['columns'] = ['_code','crn','days','time_range','_building','_room','_action_desc']
reports['conflicts']['format'] = "\t%s\t% 5s\t\t% 3s \033[1;31m%s\033[0m\t\t%-16.16s %s %s\n"
reports['conflicts']['sort'] = None # A different algorithm is used to find conflicts

reports['timetable_default']['columns'] = ['subject','course','section','type','_link_gmaps','_building','_room','time_range','_action_desc']
reports['timetable_default']['format'] = """
<p class='sched-course'>%s %s&ndash;%s (%s)</p>
<p class='sched-location'><a href='%s' title='Get directions to this building'>%s %s</a></p>
<p class='sched-time'>%s</p>
<p class='sched-action-desc'>%s</p>
"""
reports['timetable_default']['sort'] = ['days','time_range','_code']

reports['cal_default']['columns'] = [['subject','course','type','_action_desc'],['_code','instructor','crn','_action_desc']]
reports['cal_default']['format'] = ["%s %s (%s) %s","%s\\nInstructor: %s\\nCRN: %s\\n%s"]
reports['cal_default']['sort'] = None #Let the calendar program deal with this

# vi: ft=python
