from dotenv import load_dotenv
import os
import requests

# Load environment variables from .env file
load_dotenv()

def sendEmail(receiverEmail, title, body):
	# a dictionary with email data
    emailData = {
        'from' : os.getenv('SENDER_EMAIL'),
        'to': receiverEmail,
        'subject': title,
        'text': body
    }

    response = requests.post(
  		os.getenv('MAILGUN_EMAIL_API_ENDPOINT'),
  		auth=("api", os.getenv('MAILGUN_EMAIL_API_KEY')),
  		data=emailData)
    
    if response.status_code == 200:
        print('Successfully sent email')
    else:
        print("Some error occurred while sending email")


receiverEmail = input('Enter the email of receiver: ')
title = input('Enter the title of email: ')
body = input('Enter the body of the email: ')

sendEmail(receiverEmail, title, body)