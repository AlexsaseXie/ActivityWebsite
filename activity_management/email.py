import smtplib
from email.mime.text import MIMEText

mail_host = 'smtp.163.com'
mail_user = 'thss15_anyz'
mail_pass = '123SoLoMoN456'
sender = 'thss15_anyz@163.com'

#receivers:收件人(list),title:邮件标题,content:邮件内容
def send_emails(receivers, title, content):
    message = MIMEText(content, 'plain', 'utf-8')
    message['Subject'] = title
    message['From'] = sender
    message['To'] = ",".join(receivers)
    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(mail_host,25)
        smtpObj.login(mail_user,mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        smtpObj.quit()
        return True
    except smtplib.SMTPException as e:
        return False