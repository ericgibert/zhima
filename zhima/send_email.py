"""
    Wrapper to send email
"""
# Import smtplib for the actual sending function
import smtplib

# Here are the email package modules we'll need
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(subject, from_, to_,
               message_txt="",
               message_HTML="",
               images=[],
               server="", port=465,
               login="",
               passwd="",
               debug=0):
    """
        allow some default values to reduce overhead
    :return:
    """
    COMMASPACE = ', '
    # Create the container (outer) email message.
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = from_ # the sender's email address
    msg['To'] = COMMASPACE.join(to_) # the list of all recipients' email addresses
    if message_txt:
        msg.attach(MIMEText(message_txt, 'plain'))
    elif message_HTML:
        msg.attach(MIMEText(message_HTML, 'html', _charset='utf-8'))

    # Assume we know that the image files are all in PNG format
    for file in images:
        # Open the files in binary mode.  Let the MIMEImage class automatically
        # guess the specific image type.
        with open(file, 'rb') as fp:
            img = MIMEImage(fp.read())
            img.add_header('Content-Disposition', 'attachment')
        msg.attach(img)

    if debug >= 3:
        print(msg['From'])
        print(msg['To'])
        print(message_txt)
        print(message_HTML)
        print(server)
        
    # Send the email via our own SMTP server.
    s = smtplib.SMTP_SSL(server, port)
    if debug >= 3:
        print(s)
    is_logged = s.login(login, passwd)
    if debug >= 3:
        print(is_logged)

    #is_sent = s.send_message(msg)
    is_sent = s.sendmail(msg['From'], msg['To'], msg.as_string())
    if debug >= 3:
        print(is_sent)
    s.quit()


if __name__ == "__main__":
    from model_db import Database
    db = Database()

    send_email("test email",
               from_=db.mailbox["username"],
               to_ = ["ericgibert@yahoo.fr",],
               message_HTML = """
               From the <b>__main__</b> part of send_email.py module
               <p>網站有中、英文版本，也有繁、簡體版</p>
               """,
               images=[r"/home/pi/zhima/Private/night_batch.log"],
               server=db.mailbox["server"], port=db.mailbox["port"],
               login=db.mailbox["username"], passwd=db.mailbox["password"],
               debug=3)
