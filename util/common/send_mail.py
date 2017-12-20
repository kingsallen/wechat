import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.mime.application import MIMEApplication
from setting import settings


# 添加给附件重命名, 格式为{'123.pdf':'test.pdf'} 将123.pdf按照发送名为test.pdf发送
def send_mail(to, subject, text, server="", attachments=[], from_name="", from_mail=""):
    # attachments=[{'filename':'****.***', 'fileurl':'....'},{}]
    receiver = to
    msg = MIMEMultipart()
    body = MIMEText(text, 'html', 'utf-8')
    msg.attach(body)
    if from_name and from_mail:
        msg['From'] = "%s <%s>" % (Header(from_name, "utf-8"), from_mail)
    else:
        msg['From'] = settings['mail_sender']
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
    smtp.connect(settings['mail_smtpserver'])
    smtp.login(settings['mail_username'], settings['mail_password'])
    try:
        smtp.sendmail(msg['From'], receiver, msg.as_string())
    except Exception as e:
        smtp.quit()
        raise e
    finally:
        smtp.quit()

