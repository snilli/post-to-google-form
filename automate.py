import requests
import json
import inquirer
import time
import re

questions = [
    inquirer.List(
        'module',
        message="What are you booking in",
        choices=[
            'MTPR',
            'KBLC',
            'KBLC2',
            'KSLC',
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

with open('./data.json') as json_file:
    data = json.load(json_file)

moduleData = data[answers['module']]
locationList = ['BKK (กทม. และปริมณฑล)', 'UPC (ต่างจังหวัด)']
carNo = '2ฒข783'
company = 'พงศ์ธาริน'
driverName = 'มณฑล ธีระราษฎร์'
driverPhone = '0929046313'
location = locationList[0] if answers['location'] == 'BKK' else locationList[1]


def submit(url, submission):
    response = requests.post(url, submission)
    return response.status_code


submission = {
    moduleData['carNo']: carNo,
    moduleData['location']: location,
    moduleData['company']: company,
    moduleData['driverName']: driverName,
    moduleData['driverPhone']: driverPhone
}

repeatTime = int(answers['repeat'])

for current in range(repeatTime):
    resCode = submit(moduleData['url'], submission)
    if resCode == 200:
        print('Summit form success')
        print('End process with success')
        break

    balance = repeatTime - (current + 1)
    print(f'Summit form not success. will be try {balance} times')
    time.sleep(int(answers['interval']))
    if not balance:
        print('End process with not success. Please try later')
