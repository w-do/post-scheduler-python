import PySimpleGUI as sg
import time
import threading
from datetime import datetime, timedelta
import util
import reddit

# parse date/time values into an ISO 8601 string
def parseDatetime(v):
    hour = v['-hour-'] % 12
    if v['-period-'] == 'PM':
        hour += 12
    return f'{v["-date-"]} {util.pad(hour)}:{v["-minute-"]}:00'

def postImageThread(window, v):
    util.waitUntil(parseDatetime(v))
    result = reddit.postImage(v['-subredditName-'], v['-title-'], v['-imagePath-'], v['-comment-'])
    setStatus(window, result)

# wait until scheduled time and post image in a separate thread so the gui doesn't lock up
def postImage(values):
    threading.Thread(target=postImageThread, args=(window,values,), daemon=True).start()

def validate(v):
    if not util.isValid(parseDatetime(v)):
        return 'ERROR: Invalid date or time'
    if util.isNullOrWhitespace(v['-subredditName-']):
        return 'ERROR: No subreddit chosen'
    if util.isNullOrWhitespace(v['-imagePath-']):
        return 'ERROR: No image selected'
    if util.isNullOrWhitespace(v['-title-']):
        return 'ERROR: Missing title'
    if len(v['-title-']) > 300:
        return 'ERROR: Title exceeds max length (300 characters)'
    if '"' in v['-title-']: # not a reddit restriction, but it messes up our search
        return 'ERROR: Title cannot contain double quotes'
    if util.isNullOrWhitespace(v['-comment-']):
        return 'ERROR: Missing comment'
    return f'Post scheduled for {parseDatetime(v)}'

def setStatus(window, status):
    # status = f'{status} ({datetime.now()})'
    window['-status-'].update(status)
    print(status)

sg.theme('DarkGreen2')

subredditValues = util.getJson('src/config.json')['subreddits']
dateValues = list(map(util.daysFromNow, range(7)))
hourValues = list(range(1, 13))
minuteValues = list(map(util.pad, range(60)))
periodValues = ['AM', 'PM']

layout = [
    [sg.Text('Subreddit:', size=(10, 1)),
        sg.InputCombo(subredditValues, size=(50, 1), key='-subredditName-')],
    [sg.Text('Image:', size=(10, 1)),
        sg.Input(disabled=True, size=(43, 1)),
        sg.FileBrowse(key='-imagePath-')],
    [sg.Text('Title:', size=(10, 1)),
        sg.InputText(key='-title-', size=(52, 1))],
    [sg.Text('Comment:', size=(10, 1)),
        sg.Multiline(size=(50, 3), key='-comment-')],
    [sg.Text('Date:', size=(10, 1)),
        sg.Spin(dateValues, initial_value=str(util.daysFromNow(1)), key='-date-', size=(28, 1))],
    [sg.Text('Time:', size=(10, 1)),
        sg.InputCombo(hourValues, default_value=8, key='-hour-', size=(4, 1)),
        sg.Text(':'),
        sg.InputCombo(minuteValues, default_value='00', key='-minute-', size=(4, 1)),
        sg.Text(' '),
        sg.InputCombo(periodValues, default_value='AM', key='-period-', size=(4, 1))],
    [sg.Text('Status:', size=(10, 1)),
        sg.InputText(default_text='', key='-status-', disabled=True, size=(52, 1))],
    [sg.Button('Schedule'), sg.Quit()]
]

window = sg.Window('Post scheduler', layout, default_element_size=(60, 1))

while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Quit'):
        break
    if event == 'Schedule':
        status = validate(values)
        setStatus(window, status)

        if not status.startswith('ERROR'):
            postImage(values)

window.close()
