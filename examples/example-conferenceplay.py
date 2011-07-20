#!/usr/bin/env python
import plivohelper
import sys


try:
    room = sys.argv[1]
    memberid = sys.argv[2]
    soundfile = sys.argv[3]
except IndexError:
    print "Need ConferenceName, MemberID, FilePath args"
    sys.exit(1)

# URL of the Plivo REST Service
REST_API_URL = 'http://127.0.0.1:8088'
API_VERSION = 'v0.1'

# Sid and AuthToken
SID = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
AUTH_TOKEN = 'YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY'

# Create a REST object
plivo = plivohelper.REST(REST_API_URL, SID, AUTH_TOKEN, API_VERSION)

call_params = {'ConferenceName':room, 'MemberID':memberid, 'FilePath':soundfile}

try:
    print plivo.conference_play(call_params)
except Exception, e:
    print e
