import smtplib
import logging
import credentials

def send_email(body):
    """send email alert"""
    logging.info('Sending email')
    recipient = credentials.get_recipient_email()
    subject = 'Security Alert for Google Cloud Service Accounts'

    # gmail sign-in
    gmail_sender = credentials.get_sender_email()
    gmail_passwd = credentials.get_password()
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_sender, gmail_passwd)
    except smtplib.SMTPAuthenticationError:
        logging.error('Bad credentials.  Exiting...')
        exit(1)
    except Exception as err:
        logging.error('Gmail failure: {0}'.format(err))
        exit(1)

    body = '\r\n'.join(['To: %s' % recipient,
                        'From: %s' % gmail_sender,
                        'Subject: %s' % subject,
                        '', body])

    try:
        server.sendmail(gmail_sender, [recipient], body)
        logging.info('Email sent!')
    except Exception as err:
        logging.error('Sending mail failure: {0}'.format(err))

    server.quit()


if __name__ == '__main__':
    send_email('This is a test')
