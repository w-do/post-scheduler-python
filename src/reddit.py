import praw
import prawcore
import time
import util
from datetime import datetime


def getPost(subreddit, query):
    result = None
    for submission in subreddit.search(query, sort='new', time_filter='hour', limit=1):
        result = submission
    return result

def getSubreddit(subredditName):
    auth = util.getJson('src/config.json')

    reddit = praw.Reddit(
        client_id=auth['clientId'],
        client_secret=auth['clientSecret'],
        user_agent=auth['userAgent'],
        username=auth['user'],
        password=auth['pw'])
    reddit.validate_on_submit = True
    return reddit.subreddit(subredditName)

def postImage(subredditName, title, imgPath, comment):
    subreddit = getSubreddit(subredditName)

    try:
        submission = subreddit.submit_image(
            title,
            imgPath,
            resubmit=True,
            send_replies=False,
            nsfw=False,
            spoiler=False,
            timeout=20,
            without_websockets=False,
            discussion_type=None)
        submission.reply(comment)
        return f'Submitted post with comment at {datetime.now()}'
    except praw.exceptions.WebSocketException:
        posted = datetime.now()
        time.sleep(60)

        counter = 0
        interval = 15
        author = util.getJson('src/config.json')['user']

        # poll for our submitted post
        while interval * counter < 300: # retry for up to 5 minutes
            submission = getPost(subreddit, f'title:"{title}" AND author:{author}')
            if submission != None:
                break
            time.sleep(interval)
            counter += 1
        
        if submission != None:
            submission.reply(comment)
            return f'Submitted post at {posted}, submitted comment at {datetime.now()}'
        else:
            return f'Error submitting post or comment. {datetime.now()}'
