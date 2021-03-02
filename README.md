# timetable
An commandline python script for getting timetable from skola24.se (Work In Progress)

Idea from [@aj0er](https://github.com/aj0er)'s [Schema-website](https://te19adjo.kgwebb.se/schema/).
Help also provided by [@aj0er](https://github.com/aj0er).

## Requirements
* Python 3
* Python Packages
  * `isoweek`
  * `requests`

## Install
* Download the python script
* (Optional) Change defaults and parameters in the `config` section of the script.
* Run it with `python3` (python not tested)
  
  `python3 timetable.py`

## Command-line arguments
```
usage: timetable.py [-h] [-i ID] [-D DOMAIN] [-g UNIT_GUID] [-G] [-w WEEK] [-y YEAR] [-d DAY] [--hide-finished]

optional arguments:
  -h, --help            show this help message and exit
  -i ID, --id ID        The student-id, often a "personnummer".
  -D DOMAIN, --domain DOMAIN
                        The municipality's skola24-domain, eg halmstad.skola24.se
  -g UNIT_GUID, --unit-guid UNIT_GUID
                        School-id, can be acquired through the -G flag
  -G, --guid-selector   Prints all the available units in the domain
  -w WEEK, --week WEEK  week number, default is current week
  -y YEAR, --year YEAR  year, default is current year
  -d DAY, --day DAY     day 1-7, default is the current day
  --hide-finished       Hide the lessons that are already finished for the day
```
