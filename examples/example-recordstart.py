#!/usr/bin/env python
import plivohelper
import sys


try:
    calluuid = sys.argv[1]
    fileformat = sys.argv[2]
    filepath = sys.argv[3]
except IndexError:
    print "Need CallUUID, FileFormat, FilePath args"
    sys.exit(1)
try:
    filename = sys.argv[4]
except IndexError:
    filename = ''
try:
    timelimit = sys.argv[5]
except IndexError:
    timelimit = ''

# URL of the Plivo REST Service
REST_API_URL = 'http://127.0.0.1:8088'
API_VERSION = 'v0.1'

# Sid and AuthToken
SID = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
AUTH_TOKEN = 'YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY'

# Create a REST object
plivo = plivohelper.REST(REST_API_URL, SID, AUTH_TOKEN, API_VERSION)

call_params = {'CallUUID':calluuid, 'FileFormat':fileformat, 'FilePath':filepath, 'FileName':filename, 'TimeLimit':timelimit}

try:
    print plivo.record_start(call_params)
except Exception, e:
    print e
