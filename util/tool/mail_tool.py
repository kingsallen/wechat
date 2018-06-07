# coding=utf-8

# @Time    : 3/22/17 17:36
# @Author  : panda (panyuxin@moseeker.com)
# @File    : mail_tool.py
# @DES     :

import re
import os
import smtplib
import traceback

from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication


from setting import settings

from util.tool.pdf_tool import generate_html_template_resume
from util.common import ObjectDict


def send_mail_notice_hr(position, employee, conf, profile, email, template_other, dict_conf, workyears, html_to_pdf=''):
    # todo(niuzhenya)因为有循环导入的问题，在函数内部导入logger模块，重构需要对这几个模块进行解耦
    from globals import logger

    def parse_profile_for_email(profile):
        """
        处理 profile 数据, email模板中不需要未填写的数据
        :param profile:
        :return:
        """
        profile_copy = profile
        if profile_copy.get("basic").get("gender") == 0:
            profile_copy["basic"]["gender_name"] = ""

        return profile_copy

    def get_edu_for_application(profile):
        """
        获取最新教育经历用以申请
        """
        educations = profile.get("educations", [])

        if educations:
            return (sorted(educations, key=lambda x: x.get("start_date", ""),
                           reverse=True)[0])
        return ObjectDict()

    def get_valid_filename(s):
        """
        copy it from Django/utils/text.py
        """
        s = s.strip()
        return re.sub(r'(?u)[^-\w.]', ' ', s)

    def get_hrdownload_filename(position_name, resume, subfix=".pdf"):
        '''
        HR下载查看的文件名
        :param position_name:
        :param resume:
        :return:
        '''
        education = get_edu_for_application(resume)  # check education 为空
        degree = dict_conf.degree.get(str(education.get("degree", "0")))
        degree_text = "_{}".format(degree) if degree else ""
        if resume.get("workexps"):
            workyears_text = "_{}年工作经验".format(workyears) if workyears > 0 else "_少于1年工作经验"
        else:
            workyears_text = ""
        file_name = "{position}_{applier_name}{degree}{workyears}_{mobile}{subfix}".format(
            position=position_name,
            applier_name=resume.get('basic', {}).get('name', ''),
            degree=degree_text,
            workyears=workyears_text,
            mobile=resume.get('basic', {}).get('mobile', ''),
            subfix=subfix)
        file_name = get_valid_filename(file_name)
        return file_name.encode('utf-8')

    def get_profile_attachment(profile):
        """
        获取Profile中的attachment
        :param profile:
        :return:
        """
        if not profile:
            return None, None
        attachment = profile.get('attachments')[0] if profile.get('attachments') else None
        if not attachment:
            return None, None
        return attachment.get('name'), attachment.get('path')


    try:
        logger.debug("[send_mail_notice_hr]send email to hr_email:{0} start".format(email))

        profile_email = parse_profile_for_email(profile)
        resume_html = generate_html_template_resume(employee, conf, profile_email, template_other, position, dict_conf)

        attachments = []
        part = ObjectDict()
        part.filename = html_to_pdf
        part.fileurl = settings.resume_path
        part.sendname = get_hrdownload_filename(position.title, profile_email)

        logger.debug("[send_mail_notice_hr]part:{}".format(part))

        attachments.append(part)
        attach_name, attach_path = get_profile_attachment(profile)
        if attach_name and attach_path:
            email_attach = ObjectDict()
            email_attach.filename = attach_path
            email_attach.fileurl = settings.emailresume_path
            email_attach.sendname = attach_name
            attachments.append(email_attach)

        logger.debug("[send_mail_notice_hr]attachments:{}".format(attachments))

        if position.jobnumber:
            title = "{}:{}-职位申请通知".format(position.jobnumber, position.title)
        else:
            title = "{}-职位申请通知".format(position.title)

        logger.debug("[send_mail_notice_hr]to:{}".format(email.replace("；", ";").split(";")))
        logger.debug("[send_mail_notice_hr]title:{}".format(title))
        send_mail(email.replace("；", ";").split(";"),
                           title,
                           resume_html,
                           attachments=attachments)
        logger.debug("[send_mail_notice_hr]send email to hr end[send_mail_notice_hr] hr_email: {0}, position: {1}, "
                       .format(email, position.id))
    except Exception as e:
        logger.error(traceback.format_exc())
        raise


def send_mail(to, subject, text, attachments=[], from_name="", from_mail=""):
    """
    通过仟寻服务器，发送邮件
    :param to:
    :param subject:
    :param text:
    :param server:
    :param attachments:
    :param from_name:
    :param from_mail:
    :return:
    """
    receiver = to
    msg = MIMEMultipart()
    body = MIMEText(text, 'html', 'utf-8')
    msg.attach(body)
    if from_name and from_mail:
        msg['From'] = "%s <%s>" % (Header(from_name, "utf-8"), from_mail)
    else:
        msg['From'] = settings.cv_mail_sender

    msg['Subject'] = Header(subject, 'utf-8')

    def encode_attachment_filename(file_name):
        if isinstance(file_name, str):
            return Header(file_name, "utf-8").encode()
        elif isinstance(file_name, bytes):
            return encode_attachment_filename(file_name.decode("utf-8"))
        else:
            return encode_attachment_filename("附件")

    for attach in attachments:
        url = os.path.join(attach.get('fileurl'), attach.get('filename'))
        part = MIMEApplication(open(url, "rb").read())
        part.add_header('Content-Disposition', 'attachment',
                        filename=encode_attachment_filename(attach.sendname) or encode_attachment_filename(
                            attach.filename))
        msg.attach(part)

    smtp = smtplib.SMTP()
    smtp.connect(settings.cv_mail_smtpserver)
    smtp.login(settings.cv_mail_username, settings.cv_mail_password)
    try:
        smtp.sendmail(msg['From'], receiver, msg.as_string())
    except Exception as e:
        smtp.quit()
        raise e
    finally:
        smtp.quit()


if __name__ == "__main__":

    send_mail("pyx0622@gmail.com", "测试邮件", "hello")

