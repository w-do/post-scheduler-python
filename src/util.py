import time
import json
from datetime import datetime, timedelta


# get x days from now as ISO 8601 date string
def daysFromNow(x):
    return str(datetime.now().date() + timedelta(days=x))

def getJson(filePath):
    with open(filePath) as f:
        return json.load(f)

# get the number of seconds between now and a given ISO 8601 datetime
def getSecondsUntil(isoTime):
    return (datetime.fromisoformat(isoTime) - datetime.now()).total_seconds()

def isNullOrWhitespace(s):
    return s == None or str.strip(s) == ''

def isValid(iso):
    try:
        datetime.fromisoformat(iso)
        return True
    except:
        return False

def pad(x):
    return '0' + str(x) if x < 10 else str(x)

# sleep until a given ISO 8601 datetime
# probably overengineered - not sure how much of a concern drift is
def waitUntil(thisTime):
    seconds = getSecondsUntil(thisTime)
    if seconds > 0:
        while seconds > .1:
            if seconds > 3600:
                time.sleep(seconds / 2)
            else:
                time.sleep(1800 if seconds > 1800 else seconds)

            seconds = getSecondsUntil(thisTime)
