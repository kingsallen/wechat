# coding=utf-8

# @Time    : 3/22/17 17:36
# @Author  : panda (panyuxin@moseeker.com)
# @File    : mail_tool.py
# @DES     :

import os
import smtplib

from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from setting import settings


def send_mail_notice_hr(self, position, employee, conf, sysuserid, profile, email, template_other, html_to_pdf=''):
    try:
        self.LOG.debug("send email to hr_email:{0} start".format(email))
        # 处理自定义字段
        profile_email = parse_profile_for_email(profile)

        resume_html = resumeDao.generate_html_template_resume(
                self, employee, conf, sysuserid, profile_email, template_other, position, const)

        attachments = []
        part = mdict()
        part.filename = html_to_pdf
        part.fileurl = self.settings['resume_path']
        part.sendname = get_hrdownload_filename(position.title, profile_email)

        attachments.append(part)
        # 以下是给HR发送Email附件申请 已经将rename attacment 进行了合并 @智华
        attach_name, attach_path = get_profile_attachment(profile)
        if attach_name and attach_path:
            email_attach = mdict()
            email_attach.filename = attach_path
            email_attach.fileurl = self.settings['emailresume_path']
            email_attach.sendname = attach_name
            attachments.append(email_attach)

        title = position.jobnumber+":"+position.title + "-职位申请通知" if position.jobnumber else position.title + "-职位申请通知"

        self.LOG.debug("[SH]to:{}".format(email.replace("；", ";").split(";")))
        self.LOG.debug("[SH]title:{}".format(title))
        send_mail(email.replace("；", ";").split(";"),
                           title,
                           resume_html,
                           attachments=attachments)
        self.LOG.debug("send email to hr end[send_mail_notice_hr] hr_email: {0}, position: {1}, sysuserid: {2}, "
                       .format(email, position.id, sysuserid))
    except Exception as e:
        print (e)
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
            return encode_attachment_filename(u"附件")

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
