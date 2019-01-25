import smtplib
import logging

def send_email(body):
    """send email alert"""
    logging.info('Sending email')
    recipient = 'erpost@joinallofus.net'
    subject = 'Daily Risk Posture for Google Cloud'

    # gmail sign-in
    gmail_sender = 'gcp.notifications@gmail.com'
    gmail_passwd = 'wrznocyvwbilyder'
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
