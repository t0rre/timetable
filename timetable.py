#!/bin/python3
import requests
import datetime
import calendar
from isoweek import Week
import argparse
import json
#Todo
#implement school selector
#implement command line arguments
#config:
defaultDomain = "halmstad.skola24.se"
defaultId = "ÅÅMMDD-XXXX"
defaultUnit = ""                            #default school (not implemented, it's here for the syntax)


parser = argparse.ArgumentParser(description='A timetable-script for skola25\'s "schemavisare"')
parser.add_argument('-i', '--id', help='The student-id, often a "personnummer".')
parser.add_argument('-D', '--domain', help="The municipality's skola24-domain, eg halmstad.skola24.se")
parser.add_argument('-g', '--unit-guid', help="School-id, can be acquired through the -G flag")
parser.add_argument('-G', '--guid-selector', action='store_true', help="Prints all the available units in the domain")
parser.add_argument('-w', '--week', help="week number, default is current week", type=int, default=datetime.datetime.today().isocalendar()[1])
parser.add_argument('-y', '--year', help="year, default is current year", type=int, default=datetime.datetime.today().year)
parser.add_argument('-d', '--day', help="day, 1-7 default is the current day", type=int, default=datetime.datetime.today().weekday()+1)
parser.add_argument('--hide-finished', help='Hide the lessons that are already finished for the day', action='store_true')
args = parser.parse_args()
#print(args) ##debug

#headers for the api
headers = {"X-Scope": "8a22163c-8662-4535-9050-bc5e1923df48", "Content-Type":"application/json"}
#function for input, and with a default value
def defInput(string, default):
    inp = input(string+" ["+default+"]: ")
    if(inp == ""):
        inp = default
    return inp
def skola24ErrorCheck(r):
    if(r.status_code != requests.codes.ok):
        print("[ERROR]\tGot response "+str(r.status_code)+" from "+r.url)
        exit()
    if (r.json()["error"] != None):
        print("[ERROR]\tGot the following error from "+r.url+" : "+ json.dumps(r.json()["error"]))
        exit()
    if(r.json()["validation"]):
        print("[ERROR]\tGot error from "+r.url+", error: "+json.dumps(r.json()["validation"]))
        exit()
    if(r.json()["exception"] != None):
        print("[ERROR]\tGot exception from "+r.url+", error: "+json.dumps(r.json()["exception"]))
        exit()

#prompt for student id if domain argument isn't supplied, otherwise use the supplied argument
if(args.domain == None):
    domain = defInput("Enter domain", defaultDomain)
else:
    domain = args.domain
    
if(args.guid_selector):
    #get unit guids from domain §
    data = {"getTimetableViewerUnitsRequest":{"hostName":domain}}
    print("[INFO]\tGetting units for "+domain)
    response = requests.post("https://web.skola24.se/api/services/skola24/get/timetable/viewer/units", headers=headers, json=data)
    skola24ErrorCheck(response)
    if(response.json()["data"]["validationErrors"]):
        print("[ERROR]\tGot error from "+response.url+", error: "+json.dumps(response.json()["data"]["validationErrors"]))
        exit()
    if(response.json()["data"]["errors"] != None):
        print("[ERROR]\tGot error from "+response.url+", error: "+json.dumps(response.json()["data"]["errors"]))
        exit()
    units = response.json()["data"]["getTimetableViewerUnitsResponse"]["units"]
    print(units)
    for unit in units:
        print("Name: "+unit["unitId"]+" GUID: "+unit["unitGuid"])
else:
    #normal run
    if (args.unit_guid == None):
        guid = defInput("Enter your unitGuid", defaultUnit)
    else:
        guid = args.unit_guid
    if (args.id == None):
        studentId = defInput("Enter your id", defaultId)
    else:
        studentId = args.id
    data={"signature":studentId}
    #get encoded signature from id
    print("[INFO]\tGetting encoded student id")
    response = requests.post("https://web.skola24.se/api/encrypt/signature", headers=headers, json=data)
    skola24ErrorCheck(response)
    signature = response.json()["data"]["signature"]
    #get render key
    print("[INFO]\tGetting renderkey")
    response = requests.post("https://web.skola24.se/api/get/timetable/render/key", headers=headers, data="null")
    skola24ErrorCheck(response)
    renderKey = response.json()["data"]["key"]
    #request body for timetable
    data={
    "renderKey":renderKey,
    "host":domain,
    "unitGuid":guid,
    "startDate":"null",
    "endDate":"null",
    "scheduleDay":0,
    "blackAndWhite":"false",
    "width":1223,
    "height":550,
    "selectionType":4,
    "selection":signature,
    "showHeader":"false",
    "periodText":"",
    "week":args.week,#current week
    "year":args.year,
    "privateFreeTextMode":"false",
    "privateSelectionMode":"null",
    "customerKey":""
    }
    #the api uses 1-7 for daynumber, python uses 0-6
    if(args.day > 7):
        print("[WARNING]\tDay is larger than 7, capping at 7.")
        date = 7
    else:
        date = args.day

    #on weekend
    """ if(date>5):
        #get the timetable for next week instead
        data["week"]=data["week"]+1
        print("[WARNING]\tCurrently weekend. Getting timetable for next week.")
        #reset date to first date of week
        date = 1
        #if on weekend in the last week of year
        if(data["week"]==Week.last_week_of_year(data["year"])):
            data["year"]=data["year"]+1
            data["week"]=1 """

    #get the timetable
    print("[INFO]\tGetting timetable")
    response = requests.post("https://web.skola24.se/api/render/timetable", headers=headers, json=data)
    skola24ErrorCheck(response)
    week = response.json()["data"]["lessonInfo"]
    #create empty object for lessons
    while True:
        today = {"list": []}
        for x in week:
            #add only lessons for current day to object
            if x["dayOfWeekNumber"] == date:
                today["list"].append(x)
        #format lesson object nicer 
        today = today["list"]
        if(not today):
            if(date == 7):
                print("[INFO]\tDay was empty, trying first day of next week")
                date = 1
                data["week"]=data["week"]+1
                if(data["week"]==Week.last_week_of_year(data["year"])):
                    print("[INFO]\tLast week of year, trying next year.")
                    data["year"]=data["year"]+1
                    data["week"]=1
            else:
                print("[INFO]\tDay was empty, trying next day")
                date+=1
        else:
            break
    #function to return starttime for comparison
    def startTime(elem):
        return (datetime.datetime.combine(datetime.datetime.today(), datetime.datetime.strptime(elem["timeStart"], '%H:%M:%S').time())-datetime.datetime(1970,1,1)).total_seconds()
    def endTime(elem):
        return (datetime.datetime.combine(datetime.datetime.today(), datetime.datetime.strptime(elem["timeEnd"], '%H:%M:%S').time())-datetime.datetime(1970,1,1)).total_seconds()
    def printLesson(elem):
        for text in elem["texts"]:
            print(text)
        print(elem["timeStart"]+" - "+elem["timeEnd"])
    #sort lessons in order of start time
    today = sorted(today, key=startTime)
    #print each lesson
    print("Returning timetable for "+calendar.day_name[date-1]+", week "+str(data["week"])+".")
    for lesson in today:
        if (args.hide_finished):
            if(endTime(lesson)>(datetime.datetime.today()-datetime.datetime(1970,1,1)).total_seconds()):
                print("------")
                printLesson(lesson)
        else:
            print("------")
            printLesson(lesson)
    print("------")
