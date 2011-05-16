#!/usr/bin/env python
import plivohelper


#URL of the Plivo
REST_API_URL = 'http://127.0.0.1:8088'

# Sid and AuthToken
SID = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
AUTH_TOKEN = 'YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY'

# Create a REST object
plivo = plivohelper.REST(REST_API_URL, SID, AUTH_TOKEN)

# Hangup a call using a HTTP POST
transfer_call_params = {
    'URL' : "http://127.0.0.1:5000/transfered/",
    'CallUUID' : 'edaa59e1-79e0-41de-b016-f7a7570f6e9c', # Request UUID to hangup call
}

#Perform a Transfer on Live Call
try:
    print plivo.transfer_call(transfer_call_params)
except Exception, e:
    print e
