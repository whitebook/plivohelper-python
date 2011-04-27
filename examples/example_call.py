#!/usr/bin/env python
import plivohelper


#URL of the Rest Telefonie service
REST_API_URL = 'http://127.0.0.1:8088'

# Sid and AuthToken
SID = 'ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
AUTH_TOKEN = 'YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY'

#Define Channel Variable - http://wiki.freeswitch.org/wiki/Channel_Variables
originate_dial_string = "bridge_early_media=true,hangup_after_bridge=true"

# Create a REST object
plivo = plivohelper.REST(REST_API_URL, SID, AUTH_TOKEN)

# Initiate a new outbound call to user/1000 using a HTTP POST
call_params = {
    'From': '919191919191', # Caller Id
    'To' : '1000', # User Number to Call
    'Gateways' : "user/", # Gateway string to try dialing our separated by comma. First in list will be tried first
    'GatewayCodecs' : "'PCMA,PCMU'", # Codec string as needed by FS for each gateway separated by comma
    'GatewayTimeouts' : "60",      # Seconds to timeout in string for each gateway separated by comma
    'GatewayRetries' : "1", # Retry String for Gateways separated by comma, on how many times each gateway should be retried
    'OriginateDialString' : originate_dial_string,
    'AnswerUrl' : "http://127.0.0.1:5000/answered/",
    'HangUpUrl' : "http://127.0.0.1:5000/hangup/",
    'RingUrl' : "http://127.0.0.1:5000/ringing/"
}

#Perform the Call on the Rest API
try:
    print plivo.call(call_params)
except Exception, e:
    print e
