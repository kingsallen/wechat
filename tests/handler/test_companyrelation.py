# coding=utf-8

import requests, json

url = 'http://localhost:8000/mobile/company/follow'
header = {'content-type': 'application/json'}


def post_fun(url, data):
    headers = {'content-type': 'application/json'}
    re = requests.post(url, data=json.dumps(data), headers=headers)

    return re


data = {'company_id': 111, 'user_id': 222, '_xsrf':'EAB1D2AB05EEF04D35BA5FDF789DD6A3'}
# data = {}

re = post_fun(url, data)

print json.loads(re.text)
