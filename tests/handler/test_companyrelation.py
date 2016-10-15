# coding=utf-8

import requests, json

url = 'http://localhost:8000/mobile/company/follow'

url_visit = 'http://localhost:8000/mobile/company/visitreq'

header = {'content-type': 'application/json'}


def post_fun(url, data):
    headers = {'content-type': 'application/json'}
    re = requests.post(url, data=json.dumps(data), headers=headers)

    return re


data = {'company_id': 111, 'user_id': 444, 'status': 1,
        '_xsrf':'EAB1D2AB05EEF04D35BA5FDF789DD6A3'}

# re = post_fun(url_visit, data)
#


get_url = 'http://localhost:8000/mobile/company/111'

re = requests.get(get_url)

print(json.loads(re.text))
