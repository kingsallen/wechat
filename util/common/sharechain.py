# # coding=utf-8
#
# import datetime
# import torndb
# import mtp.setting as options
# from mtp.util.common.datetool import curr_now
#
#
# # 获取 position_id 列表，不区分 sys_wechat 是否开启被动求职者
# SQL_GET_POSITIONS = """
# SELECT distinct(position_id)
# FROM candidate_position_share_record
# WHERE create_time BETWEEN %s AND %s
# """
#
# # 获取从职位发布开始所有转发浏览记录，不区分 sys_wechat 是否开启被动求职者
# SQL_GET_RECOMS = """
# SELECT r.create_time,
#        r.wechat_id,
#        r.recom_id,
#        r.position_id,
#        r.presentee_id
# FROM candidate_position_share_record r
# INNER JOIN job_position p ON r.position_id = p.id
# WHERE r.presentee_id != 0
#   AND r.create_time BETWEEN %s AND %s
#   AND r.position_id = %s
#   AND r.recom_id != r.presentee_id
# ORDER BY r.create_time
# """
#
# SQL_CHECK_RECOM_HISTROY = """
# SELECT depth,
#        recom_id_2,
#        recom_id,
#        click_time
# FROM recom_record
# WHERE position_id = %s
#   AND presentee_id = %s
#   AND click_time < %s
# ORDER BY id DESC
# LIMIT 1
# """
#
# # 写入 stats.recom_record，
# # 新增字段 last_recom_id 保存转发链倒数第二个节点的用户微信 ID，
# # 为了方便重新计算每个转发链
# SQL_SAVE_RECORD = """
# INSERT INTO recom_record
# (position_id,presentee_id,click_time,depth,recom_id_2,recom_id,last_recom_id)
# VALUES (%s,
#         %s,
#         %s,
#         %s,
#         %s,
#         %s,
#         %s)
# """
#
# # 判断 sys_wechat 是否开启被动求职者， 是则写入 recom_record，
# # 兼容挖掘被动求职者功能
# SQL_INSERT_RECORD = """
# INSERT INTO candidate_recom_record
# (position_id,presentee_id,click_time,depth,recom_id_2,recom_id)
# SELECT r.position_id,
#        r.presentee_id,
#        r.click_time,
#        r.depth,
#        r.recom_id_2,
#        r.recom_id
# FROM recom_record r
# INNER JOIN job_position p ON r.position_id = p.id
# JOIN hr_wx_wechat w ON w.company_id = p.company_id
# INNER JOIN user_wx_user u ON u.id = r.presentee_id
# WHERE w.passive_seeker=0
#   AND r.depth != 0
#   AND r.click_time BETWEEN %s AND %s
#   AND u.nickname != "(未知)"
# GROUP BY recom_id,
#          presentee_id,
#          position_id
# ORDER BY click_time
# """
#
# SQL_INSERT_RECORD_REAL_TIME = """
# INSERT INTO candidate_recom_record
# (position_id,presentee_id,click_time,depth,recom_id_2,recom_id) VALUES
# (%s, %s, %s, %s, %s, %s)
# """
#
# SQL_SELECT_RECORD_REAL_TIME = """
# SELECT r.position_id,
#        r.presentee_id,
#        r.click_time,
#        r.depth,
#        r.recom_id_2,
#        r.recom_id
# FROM recom_record r
# INNER JOIN job_position p ON r.position_id = p.id
# JOIN hr_wx_wechat w ON w.company_id = p.company_id
# INNER JOIN user_wx_user u ON u.id = r.presentee_id
# WHERE w.passive_seeker=0
#   AND r.depth != 0
#   AND p.id = %s
#   AND r.presentee_id = %s
#   AND u.nickname != "(未知)"
# ORDER BY r.id DESC
# LIMIT 1
# """
#
# # 判断微信 ID 是否为认证员工
# SQL_CHECK_EMPLOYEE = """
# SELECT DISTINCT(e.id) FROM user_employee e
# LEFT JOIN job_position p ON p.company_id = e.company_id
# WHERE
#   e.activation = 0
#   AND e.disable = 0
#   AND p.id = %s
#   AND e.wxuser_id = %s
# """
#
# SQL_CHECK_EMPLOYEE_IS_HR = """
# SELECT ha.id FROM user_hr_account ha
# INNER JOIN job_position jp ON jp.company_id = ha.company_id
# WHERE jp.id = %s AND ha.wxuser_id = %s
# """
#
# # 判断待处理数据是否为 stats.recom_record 中已经存在的重复数据
# SQL_CHECK_RECOM = """
# SELECT position_id, presentee_id, depth, recom_id, recom_id2, last_recom_id
# FROM recom_record
# WHERE position_id = %s
#   AND presentee_id = %s
#   AND click_time < %s
# LIMIT 1
# """
#
# SQL_CHECK_RECOM_RECORD = """
# SELECT id
# FROM recom_record
# WHERE position_id = %s
#   AND presentee_id = %s
#   AND click_time = %s
# LIMIT 1
# """
#
# SQL_CHECK_HR_CANDIDATE_REMARK = """
# SELECT r.hraccount_id
# FROM candidate_remark r
# WHERE r.status = 2
#   AND r.hraccount_id IN ( SELECT e.id FROM user_employee e
#     JOIN job_position p ON p.company_id = e.company_id
#     WHERE p.id = %s )
#   AND r.wxuser_id = %s
# """
#
# SQL_UPDATE_REMARK_STATUS = """
# UPDATE candidate_remark SET status = 0
# WHERE hraccount_id = %s
#   AND wxuser_id = %s
# """
#
# SQL_GET_JOB_APPLICATIONS = """
# SELECT j.position_id, j.recommender_id recommender_wxuser_id,
# w.id applyer_wxuser_id, j.submit_time
# FROM job_application j
# JOIN user_wx_user w on w.wechat_id = j.wechat_id
#   AND w.sysuser_id = j.applier_id
# WHERE j.recommender_id != 0
#   AND j.submit_time BETWEEN %s AND %s
# """
#
# SQL_UPDATE_JOB_APPLICATION = """
#     UPDATE job_application
#     SET recommender_id = %s
#     WHERE position_id = %s
#       AND submit_time = %s
# """
#
# SQL_GET_LATEST_RECOM_RECORD = """
# SELECT position_id, presentee_id, depth, recom_id, click_time
# FROM recom_record
# WHERE position_id = %s
#   AND presentee_id = %s
#   AND click_time <= '%s'
# ORDER BY click_time DESC
# LIMIT 1
# """
#
# SQL_GET_LATEST_SHARE_RECORD = """
# SELECT create_time,
#        wechat_id,
#        recom_id,
#        position_id,
#        presentee_id
# FROM candidate_position_share_record
# WHERE presentee_id = %s
#   AND position_id = %s
#   AND recom_id != presentee_id
# ORDER BY create_time DESC
# LIMIT 1
# """
#
# db = torndb.Connection(
#     host=options.mysql_host,
#     database=options.mysql_database,
#     user=options.mysql_user,
#     password=options.mysql_password,
#     time_zone='+8:00',
#     max_idle_time=180,
#     charset='utf8'
# )
#
# #执行间隔为 15 分钟
# to_time = datetime.datetime.now()
# from_time = to_time - datetime.timedelta(minutes=15)
#
#
# def get_positions():
#     positions = db.query(
#         SQL_GET_POSITIONS,
#         from_time,
#         to_time
#     )
#     return positions
#
#
# def get_recoms(pid):
#     recoms = db.query(
#         SQL_GET_RECOMS,
#         from_time,
#         to_time,
#         pid
#     )
#     return recoms
#
#
# def get_latest_share_record(presentee_id, pid):
#     recoms = db.query(
#         SQL_GET_LATEST_SHARE_RECORD,
#         presentee_id,
#         pid
#     )
#     return recoms if len(recoms) == 1 else None
#
#
# def is_valid_sys_employee(position_id, wxuser_id):
#     count = len(db.query(SQL_CHECK_EMPLOYEE, position_id, wxuser_id))
#     return count != 0
#
#
# def employee_is_hr(position_id, wxuser_id):
#     count = len(db.query(SQL_CHECK_EMPLOYEE_IS_HR, position_id, wxuser_id))
#     return count != 0
#
#
# def get_recom_history_record(position_id, presentee_id, click_time):
#     history = db.query(
#         SQL_CHECK_RECOM_HISTROY,
#         position_id,
#         presentee_id,
#         click_time)
#
#     return history[0] if history else None
#
#
# def no_existed_record(recom):
#     records = db.query(
#         SQL_CHECK_RECOM_RECORD,
#         recom["position_id"],
#         recom["presentee_id"],
#         recom['create_time'])
#
#     return len(records) == 0
#
# def hr_remark_ignored_record(recom):
#     hr_employee_id = db.query(SQL_CHECK_HR_CANDIDATE_REMARK, recom['position_id'], recom['presentee_id'])
#     return hr_employee_id[0] if hr_employee_id else None
#
#
# def save_recom(list):
#     """ 处理转发轨迹
#     将浏览者置为关系最近的员工的初被动求职者
#     如果链路中不存在员工，则将浏览者置为第一个转发人的被动求职者
#
#     Args:
#         list: 转发记录
#     """
#
#     for recom in list:
#         # 如果看的人是员工，记录为 level 0， recom_id 为自己，
#         #   recom_id_2 为空， last_recom_id 为空
#         if is_valid_sys_employee(recom['position_id'], recom['presentee_id']) \
#                 and no_existed_record(recom):
#             print ("position_id:%s,recom_id:%s,presentee_id:%s" %
#                    (recom.position_id, recom.presentee_id,
#                     recom.presentee_id))
#             db.execute(
#                 SQL_SAVE_RECORD,
#                 recom['position_id'],
#                 recom['presentee_id'],
#                 recom['create_time'],
#                 0,
#                 0,
#                 recom['presentee_id'],
#                 0
#             )
#
#         # 如果看的人不是员工，
#         else:
#             # 如果数据已经记录，则不会重复记录
#             if no_existed_record(recom):
#                 last_node = get_recom_history_record(recom['position_id'],
#                                                      recom['recom_id'],
#                                                      recom['create_time'])
#
#                 # 如果存在上游数据（last_node）， 转发链长度 + 1
#                 if last_node:
#                     print ("position_id:%s,recom_id:%s,presentee_id:%s" %
#                            (recom.position_id, last_node.recom_id,
#                             recom.presentee_id))
#                     db.execute(
#                         SQL_SAVE_RECORD,
#                         recom['position_id'],
#                         recom['presentee_id'],
#                         recom['create_time'],
#                         last_node['depth'] + 1,
#                         recom['recom_id'] if last_node[
#                             'depth'] == 1 else last_node['recom_id_2'],
#                         last_node['recom_id'],
#                         recom['recom_id']
#                     )
#                 # 如果不存在上游数据，记录为 level 1， recom_id_2 为空，
#                 #   last_recom_id 为 recom_id
#                 else:
#                     print ("position_id:%s,recom_id:%s,presentee_id:%s" %
#                            (recom.position_id, recom.recom_id,
#                             recom.presentee_id))
#                     db.execute(
#                         SQL_SAVE_RECORD,
#                         recom['position_id'],
#                         recom['presentee_id'],
#                         recom['create_time'],
#                         1,  # level = 1
#                         0,  # no recom_id_2
#                         recom['recom_id'],
#                         recom['recom_id']
#                     )
#
#                 # 查询 hr_candidate_remark, 如果对应数据被忽略，则设为新数据
#                 remark_record = hr_remark_ignored_record(recom)
#                 if remark_record:
#                     print ("renew candidate_remark: hraccount_id:%s,wxuser_id:%s" %
#                            (remark_record['hraccount_id'], recom['presentee_id']))
#                     db.execute(
#                         SQL_UPDATE_REMARK_STATUS,
#                         remark_record['hraccount_id'],
#                         recom['presentee_id']
#                     )
#
#
# def get_job_applications():
#     job_applications = db.query(
#         SQL_GET_JOB_APPLICATIONS,
#         from_time,
#         to_time
#     )
#     return job_applications
#
#
# def update_application_record(job_application, recom_id):
#     """
#     将 job_application 条目的 recommender_id 修复成正确的 recom_id
#     """
#
#     db.execute(SQL_UPDATE_JOB_APPLICATION, recom_id, job_application["position_id"],
#                job_application["submit_time"])
#
#
# def refresh_share_chain(wxuser_id=None, position_id=None):
#     """
#     对给定的 wxuser_id 和 position_id 做链路原数据的入库操作
#     :param handler: 调用的此方法的 handler 可以将 self 传入用于打印 debug log
#     :param wxuser_id: 查看 JD 页的用户 wxsuer_id
#     :param position_id: 被查看的职位 id
#     :return: 如果创建链路愿数据成功,返回 True; 否则返回 False
#     """
#
#     assert wxuser_id and position_id
#
#     # 找到这个 wxuser_id 最后访问该职位的点击记录
#     share_record = get_latest_share_record(wxuser_id, position_id)
#
#     if share_record:
#         # 找到 share_record 后创建 stats.recom_record
#         save_recom(share_record)
#
#         rec = db.get(SQL_SELECT_RECORD_REAL_TIME, position_id, wxuser_id)
#         if rec:
#             db.execute(
#                 SQL_INSERT_RECORD_REAL_TIME, rec.position_id, rec.presentee_id,
#                 rec.click_time, rec.depth, rec.recom_id_2, rec.recom_id)
#         return True
#     else:
#         return False
#
# TODO
def get_referral_employee_wxuser_id(wxuser_id=None, position_id=None):
    pass
#     """
#     返回 wxuser_id 申请职位时,是否经过了员工内推.
#     如果经过了员工内推,返回内推员工 user_wx_user id
#     :param handler: 调用的此方法的 handler 可以将 self 传入用于打印 debug log
#     :param wxuser_id: 申请人 user_wx_user id
#     :param position_id: 被申请职位 id
#     :return: 如果有内推员工,返回内推员工 user_wx_user id; 如果没有内推员工或参数不全
#     ,返回 0.
#     返回的内推员工 wxuser id 以这次申请点击时候的链路为准.
#     如果这个用户看了其他包含员工转发的链路, 但是没有从这条链路申请职位,
#         是不能正常获取到员工 wxuser id 的.
#     """
#     assert wxuser_id and position_id
#
#     if is_valid_sys_employee(position_id, wxuser_id):
#         return 0
#
#     fixed_now = curr_now()
#
#     # 获取这条申请的 recom_record 条目
#     sql = SQL_GET_LATEST_RECOM_RECORD % (position_id, wxuser_id, fixed_now)
#     # _handler_debug_log(handler, sql)
#     recom_record = db.query(sql)
#
#     # 如果是直接点入申请职位的, 不存在内推员工
#     if len(recom_record) == 0:
#         return 0
#
#     # 获取 recom_record 中的 recom_id
#     recom_id = recom_record[0]["recom_id"]
#     click_time = recom_record[0]["click_time"]
#
#     # 查找 “最初推荐人” 的 recom_record 的记录，如果这条记录的 depth 是 0，那么这条记录就是内推
#     recom_record_of_recom = db.query(SQL_GET_LATEST_RECOM_RECORD % (
#         position_id, recom_id, click_time))
#
#     # 如果查不到最初联系人, 说明这条链路没有被截断过
#     # 并且 recom_id 这个人是自己点 JD 也访问的
#     if len(recom_record_of_recom) == 0:
#         # 如果直接访问的人是认证员工,返回认证员工的 id
#         if(is_valid_sys_employee(position_id, recom_id) or
#            employee_is_hr(position_id, recom_id)):
#             return recom_id
#         else:
#             return 0
#
#     # 如果可以查到最初联系人, 说明这个链路被截断过
#     # 那么在被截断的时候, 当时的 presentee_id 就是内推员工 id
#     if recom_record_of_recom[0]["depth"] == 0 and recom_id != wxuser_id:
#         return recom_id
#     else:
#         return 0
#
#
# TODO
def is_1degree_of_employee(position_id, wxuser_id):
    pass
#     """
#     返回是否是员工一度
#     仅限于新版红包调用
#     :param position_id:
#     :param wxuser_id:
#     :return: bool
#     """
#     fixed_now = curr_now()
#     sql = SQL_GET_LATEST_RECOM_RECORD % (position_id, wxuser_id, fixed_now)
#     recom_record = db.query(sql)
#
#     if len(recom_record) == 0 or recom_record[0]['depth'] != 1:
#         return False
#
#     recom_id = recom_record[0]["recom_id"]
#     click_time = recom_record[0]["click_time"]
#
#     recom_record_of_recom = db.query(SQL_GET_LATEST_RECOM_RECORD % (
#         position_id, recom_id, click_time))
#
#     if (len(recom_record_of_recom) != 0 and
#             recom_record_of_recom[0].depth == 0):
#         return True
#
#     if (len(recom_record_of_recom) == 0 and is_valid_sys_employee(
#             position_id, recom_id)):
#         return True
#
#     return False
