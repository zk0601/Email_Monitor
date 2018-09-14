#coding:utf-8
import yaml
import smtplib
import os
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr, parseaddr

Yaml_File = os.path.join(os.path.dirname(__file__), "options.yaml")
log_file = os.path.join(os.path.dirname(__file__), "log")


class Post_email(object):
    def __init__(self):
        with open(Yaml_File, 'rb') as f:
            smtp_setting = yaml.load(f)['smtp_setting']
        self.smtp_server = smtp_setting['smtp_server'][0]
        self.sender = smtp_setting['sender'][0]
        self.sender_passwd = smtp_setting['sender_passwd'][0]
        self.receivers = ",".join(smtp_setting['receivers'])

    def send_email(self, text, header):
        try:
            msg = MIMEText(text, 'plain', 'utf-8')
            msg['From'] = self._format_addr('监控邮件<%s>' % self.sender)
            msg['To'] = self.receivers
            msg['Subject'] = Header(header, 'utf-8').encode()
            server = smtplib.SMTP_SSL(self.smtp_server, 465)
            server.set_debuglevel(1)
            server.login(self.sender, self.sender_passwd)
            server.sendmail(self.sender, self.receivers.split(','), msg.as_string())
        except Exception as e:
            with open(log_file, 'a') as f:
                f.write(str(e))

    def _format_addr(self, s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), addr))
