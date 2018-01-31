# Copyright 2014 The Moore Collective, LLC, All Rights Reserved
import smtplib
import pyzmail

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

_SENDER="noreply@spriggle.net"

def send_email(sender_sn, receiver_email, html_content="", text_content=""):
    subject=sender_sn + " sent you a message"

    print 'sending email to ', receiver_email

    msg=MIMEMultipart('alternative')
    msg['Subject']=subject
    msg['From']='Spriggle <' +_SENDER +'>'
    msg['To']=receiver_email

    msg.attach(MIMEText(text_content, 'plain'))
    msg.attach(MIMEText(html_content, 'html'))

    try:
        print 'trying local smtp'
        smtpconn=smtplib.SMTP('localhost')
        smtpconn.sendmail(_SENDER, receiver_email, msg.as_string())
        smtpconn.quit()
        #print 'successfully sent email from smtp:localhost'
    except Exception:
        try:
            print 'trying remote smtp'
            sender=(sender_sn, 'tschiavo68@gmail.com')
            recipients=[msg['To']]
            prefered_encoding='iso-8859-1'
            text_encoding='iso-8859-1'
        
            #todo:tony:add external settings to avoid them being in src ctrl 
            smtp_host='smtp.gmail.com'
            smtp_port=587
            smtp_mode='tls'
            smtp_login='tschiavo68@gmail.com'
            smtp_password=None 
         
            payload, mail_from, rcpt_to, msg_id=pyzmail.compose_mail(\
                    sender, \
                    recipients, \
                    subject, \
                    prefered_encoding, \
                    (text_content, text_encoding), \
                    html=None, \
                    attachments=None)
        
            #print 'text content', text_content
            #print 'html content', html_content 
            #print 'payload', payload
         
            ret=pyzmail.send_mail(payload, mail_from, rcpt_to, smtp_host, \
                    smtp_port=smtp_port, smtp_mode=smtp_mode, \
                    smtp_login=smtp_login, smtp_password=smtp_password)
    
            if isinstance(ret, dict):
                if ret:
                    print 'failed recipients:', ', '.join(ret.keys())
                else:
                    print 'successfully sent email from smtp:remotehost'
            else:
                print 'error:', ret

        except Exception:
            print "error sending email to " + receiver_email
