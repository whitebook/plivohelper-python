#!/usr/bin/env python
import plivohelper


REST_API_URL = 'http://127.0.0.1:5000'

# Sid and AuthToken
SID = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
AUTH_TOKEN = 'YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY'

plivo = plivohelper.REST(REST_API_URL, SID, AUTH_TOKEN)

path = '/'
method = 'GET'
print plivo.request(path, method, {})
