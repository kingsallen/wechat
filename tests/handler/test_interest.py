# coding=utf-8

import requests, json


headers = {'content-type': 'application/json'}


def post_fun(url, data):
    headers = {'content-type': 'application/json'}
    re = requests.post(url, data=json.dumps(data), headers=headers)

    return re


data = {'company_id': 111, 'user_id': 444, 'status': 1,
        '_xsrf':'EAB1D2AB05EEF04D35BA5FDF789DD6A3'}

# re = post_fun(url_visit, data)
#

url = 'http://localhost:8000/m/interest'
m = {'name': '马超', 'company': '仟寻招聘', 'position': 'Python开发'}

# re = requests.get(url)

re = post_fun(url, m)

print(json.loads(re.text))

# send {'message': '短信发送异常!', 'data': '{}', 'status': 80001} <class 'dict'>
