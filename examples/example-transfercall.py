#!/usr/bin/env python
import plivohelper
import sys


# URL of the Plivo
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

# Transfer a call using a HTTP POST
transfer_call_params = {
    'URL' : "http://127.0.0.1:5000/transfered/",
    'CallUUID' : call_uuid, # CallUUID to transfer
}

# Perform a Transfer on Live Call
try:
    print plivo.transfer_call(transfer_call_params)
except Exception, e:
    print e
