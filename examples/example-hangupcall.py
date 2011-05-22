#!/usr/bin/env python
import plivohelper


# URL of the Plivo REST Service
REST_API_URL = 'http://127.0.0.1:8088'

# Sid and AuthToken
SID = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
AUTH_TOKEN = 'YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY'

# Create a REST object
plivo = plivohelper.REST(REST_API_URL, SID, AUTH_TOKEN)

# Hangup a call using a HTTP POST
hangup_call_params = {
    'CallUUID' : 'edaa59e1-79e0-41de-b016-f7a7570f6e9c', # Request UUID to hangup call
}

# Perform a hangup on a Call
try:
    print plivo.hangup_call(hangup_call_params)
except Exception, e:
    print e
