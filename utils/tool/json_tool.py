# # coding=utf-8
#
# import json
# import decimal
# import datetime
#
# class JSONEncoder(json.JSONEncoder):
#
#     def default(self, o):
#         if isinstance(o, decimal.Decimal):
#             return float(o)
#         if isinstance(o, datetime.datetime):
#             return str(o)
#         return super(JSONEncoder, self).default(self, o)
