#!/usr/bin/env python

import plivohelper

# Sid and AuthToken
ACCOUNT_SID = 'ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
ACCOUNT_TOKEN = 'YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY'

# Create a Utils object
utils = plivohelper.Utils(ACCOUNT_SID, ACCOUNT_TOKEN)

# ===========================================================================
# 1. Validate the request from server

# the URL and POST parameters would normally be provided by the web framework
url = "http://UUUUUUUUUUUUUUUUUU"
post_vars = {}

# the request from Server also includes the HTTP header: X-REST-Signature
# containing the expected signature
signature = "SSSSSSSSSSSSSSSSSSSSSSSSSSSS"

print "The request from Server to %s with the POST parameters %s " % (url, post_vars)

if utils.validate_request(url, post_vars, signature):
    print "was confirmed to have come from Server."
else:
    print "was NOT VALID.  It might have been spoofed!"
