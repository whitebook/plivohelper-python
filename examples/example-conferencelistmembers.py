#!/usr/bin/env python
import plivohelper
import sys


try:
    room = sys.argv[1]
except IndexError:
    print "Need ConferenceName argument"
    sys.exit(1)

try:
    member_filter = sys.argv[2]
except IndexError:
    member_filter = ""
try:
    uuid_filter = sys.argv[3]
except IndexError:
    uuid_filter = ""

# URL of the Plivo REST Service
REST_API_URL = 'http://127.0.0.1:8088'
API_VERSION = 'v0.1'

# Sid and AuthToken
SID = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
AUTH_TOKEN = 'YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY'

# Create a REST object
plivo = plivohelper.REST(REST_API_URL, SID, AUTH_TOKEN, API_VERSION)

call_params = {'ConferenceName':room, 'Members':member_filter, 'CallUUIDs':uuid_filter}

try:
    print plivo.conference_list_members(call_params)
except Exception, e:
    print e
