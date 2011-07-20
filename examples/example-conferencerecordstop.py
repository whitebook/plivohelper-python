#!/usr/bin/env python
import plivohelper
import sys


try:
    room = sys.argv[1]
    recordfile = sys.argv[2]
except IndexError:
    print "Need ConferenceName, RecordFile args"
    sys.exit(1)
try:
    filename = sys.argv[4]
except IndexError:
    filename = ''

# URL of the Plivo REST Service
REST_API_URL = 'http://127.0.0.1:8088'
API_VERSION = 'v0.1'

# Sid and AuthToken
SID = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
AUTH_TOKEN = 'YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY'

# Create a REST object
plivo = plivohelper.REST(REST_API_URL, SID, AUTH_TOKEN, API_VERSION)

call_params = {'ConferenceName':room, 'RecordFile':recordfile}

try:
    print plivo.conference_record_stop(call_params)
except Exception, e:
    print e
