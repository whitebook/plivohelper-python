#!/usr/bin/env python
import plivohelper
import sys


try:
    call_uuid = sys.argv[1]
except IndexError:
    print "need CallUUID argument"
    sys.exit(1)


# URL of the Plivo REST Service
REST_API_URL = 'http://127.0.0.1:8088'
API_VERSION = 'v0.1'

# Sid and AuthToken
SID = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
AUTH_TOKEN = 'YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY'

# Create a REST object
plivo = plivohelper.REST(REST_API_URL, SID, AUTH_TOKEN, API_VERSION)

# Hangup a call using a HTTP POST
hangup_call_params = {
    'CallUUID' : call_uuid, # CallUUID for Hangup
}

# Perform a hangup on a Call
try:
    print plivo.hangup_call(hangup_call_params)
except Exception, e:
    print e
