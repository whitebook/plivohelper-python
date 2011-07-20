#!/usr/bin/env python
import plivohelper
import sys

try:
    member_filter = sys.argv[1]
except IndexError:
    member_filter = ""
try:
    uuid_filter = sys.argv[2]
except IndexError:
    uuid_filter = ""
try:
    only_mute = sys.argv[3]
except IndexError:
    only_mute = 'false'
try:
    only_deaf = sys.argv[4]
except IndexError:
    only_deaf = 'false'

# URL of the Plivo REST Service
REST_API_URL = 'http://127.0.0.1:8088'
API_VERSION = 'v0.1'

# Sid and AuthToken
SID = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
AUTH_TOKEN = 'YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY'

# Create a REST object
plivo = plivohelper.REST(REST_API_URL, SID, AUTH_TOKEN, API_VERSION)

call_params = {'MemberFilter':member_filter, 
               'CallUUIDFilter':uuid_filter, 'MutedFilter':only_mute, 'DeafFilter':only_deaf}


try:
    print plivo.conference_list(call_params)
except Exception, e:
    print e
