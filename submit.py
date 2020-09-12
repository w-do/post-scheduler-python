import praw
import time
import json
from datetime import datetime


def getJson(filePath):
    with open(filePath) as f:
        return json.load(f)

def getPost(subreddit, query):
    result = None
    for submission in subreddit.search(query, sort='new', time_filter='hour', limit=1):
        result = submission
    return result

def waitUntil(thisTime):
    seconds = (datetime.fromisoformat(thisTime) - datetime.now()).total_seconds()
    if (seconds > 0):
        print(f'waiting {seconds} seconds until {thisTime}')
        time.sleep(seconds)
    else:
        print('not a future time')

auth = getJson('auth.json')
clientId = auth['clientId']
clientSecret = auth['clientSecret']
user = auth['user']
pw = auth['pw']

config = getJson('config.json')
sub = config['sub']
# TODO: VALIDATE TITLE
title = config['title']
imgPath = f"images/{config['imageName']}"
comment = config['comment']
scheduledTime = config['scheduledTime']

reddit = praw.Reddit(
    client_id=clientId,
    client_secret=clientSecret,
    user_agent=f'mac:test:1.0.0 (by /u/{user})',
    username=user,
    password=pw)
reddit.validate_on_submit = True
subreddit = reddit.subreddit(sub)

waitUntil(scheduledTime)

title += f' {datetime.now()}'

try:
    submission = subreddit.submit_image(
        title,
        imgPath,
        resubmit=True,
        send_replies=False,
        nsfw=True,
        spoiler=False,
        timeout=20,
        without_websockets=False,
        discussion_type=None)
    print(f'posted {title}, replying')
    submission.reply(f'{datetime.now()} {comment}')
except praw.exceptions.WebSocketException:
    print(f'posted {title}, got websocket error')
    time.sleep(90)

    counter = 1
    submission = None
    interval = 15

    while (submission == None and interval * counter < 300):
        print('z' * counter)
        time.sleep(interval)
        # NO DOUBLE QUOTES IN TITLE
        submission = getPost(subreddit, f'title:"{title}" AND author:{user}')
        counter += 1
    
    if (submission != None):
        print('replying')
        submission.reply(f'{datetime.now()} {comment}')
    else:
        print('timed out :(')
