from raven import Client
import sendgrid
import os
import time

client = Client(os.environ['SENTRY_DSN'])

sg_user = os.environ['SG_USER']
sg_pass = os.environ['SG_PASS']

sg = sendgrid.SendGridClient(sg_user, sg_pass)

TEST_URL = 'http://localhost:5000/'
PRODUCTION_URL = 'http://isitsteaknight.com/'

def tellEricSomeoneSignedUp(email):
    message = senggrid.Mail()
    message.add_to('eric.song@rutgers.edu')
    message.set_subject('Someone signed up for IsItSteakNight: ' + email)
    message.set_html(email + ' signed up. wooo')
    message.set_from('IsItSteakNight')
    status, msg = sg.send(message)

def sendConfirmationEmail(email, query, key):
    user = {
        'email': email,
        'query': query,
        'key': key
    }
    message = sendgrid.Mail()
    message.add_to(user['email'])
    message.set_subject('IsItSteakNight Email Confirmation')
    message.set_html('Hi! <br><br> Please click the following link to confirm your email, ' + PRODUCTION_URL + 'ConfirmSubscriber?token=' + str(user['key']))
    message.set_from('IsItSteakNight')
    status, msg = sg.send(message)

    if(status is not 200):
        client.user_context({
            'user': user,
            'status': status,
            'msg': msg
        })
        client.captureMessage('Send confirmation email failed')
        client.context.clear()
        time.sleep(1) #bad...
        return (status, msg)
    else:
        return (status, msg)
