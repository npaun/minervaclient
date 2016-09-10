#### Formatting
date_fmt = {'short_date': '%-m/%-d', 'short_datetime': '%-m/%-d %-H:%-M','short_time': '%Hh%M'}


#### Reports
reports = {'long': {},'default': {},'short': {}}

reports['long']['columns'] = ['subject','course','credits','section','type','crn','days','time_range','_building','_room','instructor','_action_desc']
reports['long']['format'] = "%s %s (%s)\t%s (%s)\t% 5s\t\t% 3s %s\t\t%-16.16s %s\t\t%-16s\t%s"
reports['long']['sort'] = ['days','time_range','_code']

reports['default']['columns'] = ['subject','course','credits','section','type','crn','days','time_range','_action_desc']
reports['default']['format'] = "%s %s (%s)\t%s (%s)\t% 5s\t\t% 3s %s\t%s"
reports['default']['sort'] = ['days','time_range','_code']

reports['short']['columns'] = ['subject','course','credits','section','crn','_action_desc']
reports['short']['format'] = "%s %s (%s)\t%s\t% 5s\t%s"
reports['short']['sort'] = ['_code']
