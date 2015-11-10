from raven import Client
import sendgrid
import os

client = Client(os.environ['SENTRY_DSN'])

sg_user = os.environ['SG_USER']
sg_pass = os.environ['SG_PASS']

sg = sendgrid.SendGridClient(sg_user, sg_pass)

TEST_URL = 'http://localhost:5000/'
PRODUCTION_URL = 'http://isitsteaknight.com/'

def sendConfirmationEmail(user):
    message = sendgrid.Mail()
    message.add_to(user['email'])
    message.set_subject('IsItSteakNight Email Confirmation')
    message.set_html('Hi! <br><br> Please click the following link to confirm your email, ' + PRODUCTION_URL + 'ConfirmSubscriber?token=' + str(user['key']))
    message.set_from('IsItSteakNight')
    status, msg = sg.send(message)
    print('email sent: ', status, msg)

    if(status is not 200):
        client.context.merge({
            'user': user,
            'status': status,
            'msg': msg
        })
        client.captureMessage('Send confirmation email failed.')
        client.captureException()
        client.context.clear()

    return (status, msg)
