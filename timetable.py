import requests
import datetime
import json
import time
headers = {"X-Scope": "8a22163c-8662-4535-9050-bc5e1923df48", "Content-Type":"application/json"}
def defInput(string, default):
    inp = input(string+" ["+default+"]: ")
    if(inp == ""):
        inp = default
    return inp
domain = defInput("Enter domain", "halmstad.skola24.se")
studentId = input("Enter your id: ")
data={"signature":studentId}
response = requests.post("https://web.skola24.se/api/encrypt/signature", headers=headers, json=data)
signature = response.json()["data"]["signature"]
response = requests.post("https://web.skola24.se/api/get/timetable/render/key", headers=headers, data="null")
renderKey = response.json()["data"]["key"]
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
   "year":2021,
   "privateFreeTextMode":"false",
   "privateSelectionMode":"null",
   "customerKey":""
}
date = datetime.datetime.today().weekday()+1
#on weekend
if(datetime.datetime.today().weekday()>4):
    #get the timetable for next week instead
    data["week"]=datetime.datetime.today().isocalendar()[1]+1
    print("[INFO]\tCurrently weekend. Getting timetable for next week.")
    date = 1

response = requests.post("https://web.skola24.se/api/render/timetable", headers=headers, json=data)
week = response.json()["data"]["lessonInfo"]
today = {"list": []}
for x in week:
    if x["dayOfWeekNumber"] == date:
        today["list"].append(x) 
today = today["list"]
def startTime(elem):
    return (datetime.datetime.strptime(elem["timeStart"], '%H:%M:%S')-datetime.datetime(1970,1,1)).total_seconds()
today = sorted(today, key=startTime)
for lesson in today:
    print("------")
    for text in lesson["texts"]:
        print(text)
    print(lesson["timeStart"]+" - "+lesson["timeEnd"])
print("------")