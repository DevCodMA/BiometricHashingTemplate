from random import randint
from twilio.rest import Client

def generate(phone):
    # set Twilio account SID, auth token, and phone number
    account_sid = 'YOUR ACCOUNT SID'
    auth_token = 'YOUR AUTH TOKEN'
    twilio_number = 'TWILIO NUMBER'

    # generate random 6-digit OTP
    otp = randint(100000, 999999)

    # create Twilio client
    client = Client(account_sid, auth_token)

    # send SMS message containing OTP
    message = client.messages.create(
        body=f'Your OTP is {otp}',
        from_=twilio_number,
        to="+91"+phone
    )
    return otp