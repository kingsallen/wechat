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

url = 'http://localhost:8000/api/mobile/cellphone'
m = {'mobile': '18855101775', 'code': 9948}

# re = requests.get(url, params={'mobile': '18855101775'})

re = post_fun(url, m)

print json.loads(re.text)
