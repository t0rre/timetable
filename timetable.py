import requests
import datetime
#Todo
#implement school selector
#implement command line arguments
#config:
defaultDomain = "halmstad.skola24.se"
defaultId = "ÅÅMMDD-XXXX"

#headers for the api
headers = {"X-Scope": "8a22163c-8662-4535-9050-bc5e1923df48", "Content-Type":"application/json"}
def defInput(string, default):
    inp = input(string+" ["+default+"]: ")
    if(inp == ""):
        inp = default
    return inp
domain = defInput("Enter domain", defaultDomain)
studentId = defInput("Enter your id", defaultId)
data={"signature":studentId}
#get encoded signature from id
response = requests.post("https://web.skola24.se/api/encrypt/signature", headers=headers, json=data)
signature = response.json()["data"]["signature"]
#get render key
response = requests.post("https://web.skola24.se/api/get/timetable/render/key", headers=headers, data="null")
renderKey = response.json()["data"]["key"]
#request body for timetable
data={
   "renderKey":renderKey,
   "host":domain,
   "unitGuid":"OWM1YWRhYTEtYTNmYi1mNzYzLWI5NDItZjkzZjE3M2VhNjA4",
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
   "week":datetime.datetime.today().isocalendar()[1],#current week
   "year":datetime.datetime.today().year,
   "privateFreeTextMode":"false",
   "privateSelectionMode":"null",
   "customerKey":""
}
#the api uses 1-7 for daynumber, python uses 0-6
date = datetime.datetime.today().weekday()+1

#on weekend
if(datetime.datetime.today().weekday()>4):
    #get the timetable for next week instead
    data["week"]=datetime.datetime.today().isocalendar()[1]+1
    print("[INFO]\tCurrently weekend. Getting timetable for next week.")
    #reset date to first date of week
    date = 1

#get the timetalbe
response = requests.post("https://web.skola24.se/api/render/timetable", headers=headers, json=data)
week = response.json()["data"]["lessonInfo"]
#create empty object for lessons
today = {"list": []}
for x in week:
    #add only lessons for current day to object
    if x["dayOfWeekNumber"] == date:
        today["list"].append(x)
#format lesson object nicer 
today = today["list"]
#function to return starttime for comparison
def startTime(elem):
    return (datetime.datetime.strptime(elem["timeStart"], '%H:%M:%S')-datetime.datetime(1970,1,1)).total_seconds()
#sort lessons in order of start time
today = sorted(today, key=startTime)
#print each lesson
for lesson in today:
    print("------")
    for text in lesson["texts"]:
        print(text)
    print(lesson["timeStart"]+" - "+lesson["timeEnd"])
print("------")