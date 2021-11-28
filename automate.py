import requests
import json
import inquirer
import time
import re
import pprint
import datetime
import csv

questions = [
    inquirer.List(
        'module',
        message="What are you booking in",
        choices=[
            'MTPR',
            'KBLC',
            'KBLC2',
            'KSLC',
            'KSLC2',
            'KMLC'
        ],
    ),
    inquirer.List(
        'location',
        message="Choose location",
        choices=[
            'BKK',
            'UPC',
        ],
    ),
    inquirer.Text('repeat',
                  message="Repeat times",
                  validate=lambda _, x: re.match('\d', x) and len(x) < 5),
    inquirer.Text('interval',
                  message="Repeat interval (second)",
                  validate=lambda _, x: re.match('\d', x) and len(x) < 5),
]
answers = inquirer.prompt(questions)

with open('./setting.json') as setting_raw:
    setting = json.load(setting_raw)

with open('./data.json') as entry_point_raw:
    entry_point = json.load(entry_point_raw)

printer = pprint.PrettyPrinter(indent=4, compact=True, width=40)

printer.pprint('============= profile =============')
printer.pprint(setting)
printer.pprint('=========== summit data ===========')
printer.pprint(answers)
printer.pprint('===================================')

moduleData = entry_point[answers['module']]
locationList = ['BKK (กทม. และปริมณฑล)', 'UPC (ต่างจังหวัด)']

location = locationList[0] if answers['location'] == 'BKK' else locationList[1]


def submit(url, submission):
    response = requests.post(f'{url}/formResponse', submission)
    return [response.status_code, response.text]


def formveiw(url):
    response = requests.get(f'{url}/viewform')
    return response.text


def is_close_form(text):
    return text.find(
        'freebirdFormviewerViewResponseConfirmContentContainer') != -1


def write_log(status, reason):
    log = open("log.csv", "a", encoding='utf-8')
    writer = csv.writer(log)
    writer.writerow([datetime.datetime.now(), submission, status, reason])


submission = {
    moduleData['carNo']: setting['carNo'],
    moduleData['location']: location,
    moduleData['company']: setting['company'],
    moduleData['driverName']: setting['driverName'],
    moduleData['driverPhone']: setting['driverPhone'],
    "pageHistory": moduleData['pageHistory']
}

repeatTime = int(answers['repeat'])

for current in range(repeatTime):
    text = formveiw(moduleData['url'])
    is_close_time = is_close_form(text)
    if is_close_time:
        balance = repeatTime - (current + 1)
        print(f'From still close. will be try {balance} times')
        time.sleep(int(answers['interval']))

        if not balance:
            print('End process with not success. Please try later')
            write_log('fail', 'form close')
            break

        continue

    resCode, data = submit(moduleData['url'], submission)
    if resCode != 200:
        write_log('fail', 'form error')
        print('Already submit. Please try later')
        break

    write_log('success', 'submitted')
    print('Summit form success')
    print('End process with success')
    break