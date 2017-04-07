from bs4 import BeautifulSoup as bs
import requests
from datetime import datetime as dt
from subprocess import check_call, call
import sys

if len(sys.argv) > 1:
    cmd = sys.argv[1]
else:
    cmd = "true"

def main():
    print "\033[1;36mgrabLRS:\033[0m Copy link location; paste LRS URL; press enter; stuff happens."
    while True:
        print "\n"
        url = raw_input('\033[1m<URL>\033[1;32m ')
        dest,video = get_source(requests.get(url).text)
        fetch(video,dest)


def fetch(video,dest):
    try: 
        check_call(["curl",video,"-o",dest])
        call([cmd,dest])
    except:
        print "Not today"


def process(data):
    data = requests.get(data).text.split("\n")
    video_url = data[6]
    return video_url

def get_source(text): 
    html = bs(text,'html5lib')
    srcs = html.find_all('source')
    course = html.find('span', {'id': 'TabContainer1_TabPanel1_LabelCourse'}).text
    date = html.find('span', {'id': 'TabContainer1_TabPanel1_LabelRecordingDate'}).text
    date = dt.strptime(date,'%m/%d/%Y %H:%M:%S %p').strftime('%m-%d')
    course = "-".join(course.split("-")[:-1])
    fname = "-".join([course,date]) + ".mp4"

    print "\033[0m\n\033[1mDownloading...\033[1;36m " + fname + "\033[0m"


    if not srcs:
        return

    data_url = srcs[0]['src']
    return fname,process(data_url)

main()
