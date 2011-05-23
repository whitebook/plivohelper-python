# -*- coding: utf-8 -*-

__VERSION__ = "0.1"

import urllib, urllib2, base64, hmac
from hashlib import sha1
from xml.dom.minidom import Document

try:
    from google.appengine.api import urlfetch
    APPENGINE = True
except ImportError:
    APPENGINE = False
try:
    import json
except ImportError:
    import simplejson as json


class PlivoException(Exception): pass

# Plivo REST Helpers
# ===========================================================================

class HTTPErrorProcessor(urllib2.HTTPErrorProcessor):
    def https_response(self, request, response):
        code, msg, hdrs = response.code, response.msg, response.info()
        if code >= 300:
            response = self.parent.error(
                'http', request, response, code, msg, hdrs)
        return response

class HTTPErrorAppEngine(Exception): pass

class PlivoUrlRequest(urllib2.Request):
    def get_method(self):
        if getattr(self, 'http_method', None):
            return self.http_method
        return urllib2.Request.get_method(self)

class REST(object):
    """Plivo helper class for making
    REST requests to the Plivo API.  This helper library works both in
    standalone python applications using the urllib/urlib2 libraries and
    inside Google App Engine applications using urlfetch.
    """
    def __init__(self, url, auth_id='', auth_token='', api_version='v0.1'):
        """initialize a object

        url: Rest API Url
        auth_id: Plivo SID/ID
        auth_token: Plivo token

        returns a Plivo object
        """
        self.url = url
        self.auth_id = auth_id
        self.auth_token = auth_token
        self.opener = None
        self.api_version = api_version

    def _build_get_uri(self, uri, params):
        if params:
            if uri.find('?') > 0:
                if uri[-1] != '&':
                    uri += '&'
                uri = uri + urllib.urlencode(params)
            else:
                uri = uri + '?' + urllib.urlencode(params)
        return uri

    def _urllib2_fetch(self, uri, params, method=None):
        # install error processor to handle HTTP 201 response correctly
        if self.opener == None:
            self.opener = urllib2.build_opener(HTTPErrorProcessor)
            urllib2.install_opener(self.opener)

        if method and method == 'GET':
            uri = self._build_get_uri(uri, params)
            req = PlivoUrlRequest(uri)
        else:
            req = PlivoUrlRequest(uri, urllib.urlencode(params))
            if method and (method == 'DELETE' or method == 'PUT'):
                req.http_method = method

        authstring = base64.encodestring('%s:%s' % (self.auth_id, self.auth_token))
        authstring = authstring.replace('\n', '')
        req.add_header("Authorization", "Basic %s" % authstring)

        response = urllib2.urlopen(req)
        return response.read()

    def _appengine_fetch(self, uri, params, method):
        if method == 'GET':
            uri = self._build_get_uri(uri, params)

        try:
            httpmethod = getattr(urlfetch, method)
        except AttributeError:
            raise NotImplementedError(
                "Google App Engine does not support method '%s'" % method)

        authstring = base64.encodestring('%s:%s' % (self.auth_id, self.auth_token))
        authstring = authstring.replace('\n', '')
        r = urlfetch.fetch(url=uri, payload=urllib.urlencode(params),
            method=httpmethod,
            headers={'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': 'Basic %s' % authstring})
        if r.status_code >= 300:
            raise HTTPErrorAppEngine("HTTP %s: %s" % \
                (r.status_code, r.content))
        return r.content

    def request(self, path, method=None, data={}):
        """sends a request and gets a response from the Plivo REST API

        path: the URL (relative to the endpoint URL, after the /v1
        method: the HTTP method to use, defaults to POST
        data: for POST or PUT, a dict of data to send

        returns Plivo response in XML or raises an exception on error
        """
        if not path:
            raise ValueError('Invalid path parameter')
        if method and method not in ['GET', 'POST', 'DELETE', 'PUT']:
            raise NotImplementedError(
                'HTTP %s method not implemented' % method)

        if path[0] == '/':
            uri = self.url + path
        else:
            uri = self.url + '/' + path

        if APPENGINE:
            return json.loads(self._appengine_fetch(uri, data, method))
        return json.loads(self._urllib2_fetch(uri, data, method))

    def call(self, call_params):
        """REST Call Helper
        """
        path = '/' + self.api_version + '/Call/'
        method = 'POST'
        return self.request(path, method, call_params)

    def bulk_call(self, call_params):
        """REST BulkCalls Helper
        """
        path = '/' + self.api_version + '/BulkCall/'
        method = 'POST'
        return self.request(path, method, call_params)

    def transfer_call(self, call_params):
        """REST Transfer Live Call Helper
        """
        path = '/' + self.api_version + '/TransferCall/'
        method = 'POST'
        return self.request(path, method, call_params)

    def hangup_call(self, call_params):
        """REST Hangup Live Call Helper
        """
        path = '/' + self.api_version + '/HangupCall/'
        method = 'POST'
        return self.request(path, method, call_params)

    def hangup_all_calls(self):
        """REST Hangup All Live Calls Helper
        """
        path = '/' + self.api_version + '/HangupAllCalls/'
        method = 'POST'
        return self.request(path, method)

    def schedule_hangup(self, call_params):
        """REST Schedule Hangup Helper
        """
        path = '/' + self.api_version + '/ScheduleHangup/'
        method = 'POST'
        return self.request(path, method, call_params)

    def cancel_scheduled_hangup(self, call_params):
        """REST Cancel a Scheduled Hangup Helper
        """
        path = '/' + self.api_version + '/CancelScheduledHangup/'
        method = 'POST'
        return self.request(path, method, call_params)


# RESTXML Response Helpers
# ===========================================================================

class Grammar(object):
    """Plivo basic grammar object.
    """
    def __init__(self, **kwargs):
        self.name = self.__class__.__name__
        self.body = None
        self.nestables = None
        self.grammar = []
        self.attrs = {}
        for k, v in kwargs.items():
            if k == "sender":
                k = "from"
            if v is True or v is False:
                v = Grammar.bool2txt(v)
            if v is not None:
                self.attrs[k] = unicode(v)

    @staticmethod
    def bool2txt(var):
        if var is True:
            return 'true'
        elif var is False:
            return 'false'
        return None

    def __repr__(self):
        """
        String representation of a grammar
        """
        doc = Document()
        return self._xml(doc).toxml()

    def _xml(self, root):
        """
        Return an XML element representing this grammar
        """
        grammar = root.createElement(self.name)

        # Add attributes
        keys = self.attrs.keys()
        keys.sort()
        for a in keys:
            grammar.setAttribute(a, self.attrs[a])

        if self.body:
            text = root.createTextNode(self.body)
            grammar.appendChild(text)

        for c in self.grammar:
            grammar.appendChild(c._xml(root))

        return grammar

    @staticmethod
    def check_post_get_method(method=None):
        if not method in ('GET', 'POST'):
            raise PlivoException("Invalid method parameter, must be 'GET' or 'POST'")

    def append(self, grammar):
        if not self.nestables:
            raise PlivoException("%s is not nestable" % self.name)
        if not grammar.name in self.nestables:
            raise PlivoException("%s is not nestable inside %s" % \
                            (grammar.name, self.name))
        self.grammar.append(grammar)
        return grammar

    def asUrl(self):
        return urllib.quote(str(self))

    def addSpeak(self, text, **kwargs):
        return self.append(Speak(text, **kwargs))

    def addPlay(self, url, **kwargs):
        return self.append(Play(url, **kwargs))

    def addWait(self, **kwargs):
        return self.append(Wait(**kwargs))

    def addRedirect(self, url=None, **kwargs):
        return self.append(Redirect(url, **kwargs))

    def addHangup(self, **kwargs):
        return self.append(Hangup(**kwargs))

    def addReject(self, **kwargs):
        return self.append(Reject(**kwargs))

    def addGetDigits(self, **kwargs):
        return self.append(GetDigits(**kwargs))

    def addNumber(self, number, **kwargs):
        return self.append(Number(number, **kwargs))

    def addDial(self, number=None, **kwargs):
        return self.append(Dial(number, **kwargs))

    def addRecord(self, **kwargs):
        return self.append(Record(**kwargs))

    def addConference(self, name, **kwargs):
        return self.append(Conference(name, **kwargs))

    def addSms(self, msg, **kwargs):
        return self.append(Sms(msg, **kwargs))

    def addRecordSession(self, **kwargs):
        return self.append(RecordSession(**kwargs))

    def addPreAnswer(self, **kwargs):
        return self.append(PreAnswer(**kwargs))

    def addScheduleHangup(self, **kwargs):
        return self.append(ScheduleHangup(**kwargs))

class Response(Grammar):
    """Plivo response object.

    version: Plivo API version 0.1
    """
    def __init__(self, version=None, **kwargs):
        Grammar.__init__(self, version=version, **kwargs)
        self.nestables = ['Speak', 'Play', 'GetDigits', 'Record', 'Dial',
            'Redirect', 'Wait', 'Hangup', 'Reject', 'Sms', 'RecordSession',
            'PreAnswer', 'ScheduleHangup', 'Conference']

class Speak(Grammar):
    """Speak text

    text: text to say
    voice: voice to be used based on TTS engine
    language: language to use
    loop: number of times to say this text
    """
    ENGLISH = 'en'
    SPANISH = 'es'
    FRENCH = 'fr'
    GERMAN = 'de'

    def __init__(self, text, voice=None, language='en', loop=1, **kwargs):
        Grammar.__init__(self, voice=voice, language=language, loop=loop, **kwargs)
        self.body = text
        if not language in (self.ENGLISH, self.SPANISH,
                            self.FRENCH, self.GERMAN):
            raise PlivoException( \
                "Invalid Say language parameter, must be " + \
                "'en', 'es', 'fr', or 'de'")

class Play(Grammar):
    """Play audio file at a URL

    url: url of audio file, MIME type on file must be set correctly
    loop: number of time to say this text
    """
    def __init__(self, url, loop=1, **kwargs):
        Grammar.__init__(self, loop=loop, **kwargs)
        self.body = url

class Wait(Grammar):
    """Wait for some time to further process the call

    length: length of wait time in seconds
    """
    def __init__(self, length, transferEnabled=False):
        Grammar.__init__(self, length=length, transferEnabled=transferEnabled)

class Redirect(Grammar):
    """Redirect call flow to another URL

    url: redirect url
    """
    def __init__(self, url=None, method="POST", **kwargs):
        Grammar.__init__(self, method=method, **kwargs)
        Grammar.check_post_get_method(method)
        self.body = url

class Hangup(Grammar):
    """Hangup the call
    """
    def __init__(self, **kwargs):
        Grammar.__init__(self)

class GetDigits(Grammar):
    """Get digits from the caller's keypad

    action: URL to which the digits entered will be sent
    method: submit to 'action' url using GET or POST
    numDigits: how many digits to gather before returning
    timeout: wait for this many seconds before returning
    finishOnKey: key that triggers the end of caller input
    """
    def __init__(self, action=None, method='POST',
                 numDigits=1, timeout=5,
                 finishOnKey=None, **kwargs):

        Grammar.__init__(self, action=action, method=method,
                         numDigits=numDigits, timeout=timeout,
                         finishOnKey=finishOnKey, **kwargs)
        Grammar.check_post_get_method(method)
        self.nestables = ['Speak', 'Play', 'Wait']

class Number(Grammar):
    """Specify phone number in a nested Dial element.

    number: phone number to dial
    sendDigits: key to press after connecting to the number
    """
    def __init__(self, number, sendDigits=None, **kwargs):
        Grammar.__init__(self, sendDigits=sendDigits, **kwargs)
        self.body = number

class Sms(Grammar):
    """ Send a Sms Message to a phone number

    to: whom to send message to, defaults based on the direction of the call
    sender: whom to send message from.
    action: url to request after the message is queued
    method: submit to 'action' url using GET or POST
    statusCallback: url to hit when the message is actually sent
    """
    def __init__(self, msg, to=None, sender=None, method=None,
                 action=None, statusCallback=None, **kwargs):
        Grammar.__init__(self, action=action, method=method, to=to,
                         sender=sender, statusCallback=statusCallback,
                         **kwargs)
        Grammar.check_post_get_method(method)
        self.body = msg

class Conference(Grammar):
    """Enter a conference room.

    name: room name
    waitAloneSound: sound to play while alone in conference
    muted: enter conference muted
    moderator: enter as moderator
    closeOnExit: close conference after this user leaves
    maxMembers: max members in conference (0 for no limit)
    """
    def __init__(self, name,
                 muted=False, waitAloneSound=None,
                 moderator=False, closeOnExit=False,
                 maxMembers=0, **kwargs):
        Grammar.__init__(self, muted=False, waitAloneSound=None,
                         moderator=False, closeOnExit=False,
                         maxMembers=0, **kwargs)
        self.body = name

class Dial(Grammar):
    """Dial another phone number and connect it to this call

    action: submit the result of the dial to this URL
    method: submit to 'action' url using GET or POST
    """
    def __init__(self, number=None, action=None, method='POST', **kwargs):
        Grammar.__init__(self, action=action, method=method, **kwargs)
        self.nestables = ['Number']
        Grammar.check_post_get_method(method)
        numbers = number.split(',')
        if numbers:
            for n in numbers:
                self.append(Number(n.strip()))
        else:
            self.body = number

class Record(Grammar):
    """Record audio from caller

    action: submit the result of the dial to this URL
    method: submit to 'action' url using GET or POST
    maxLength: maximum number of seconds to record
    timeout: seconds of silence before considering the recording complete
    """
    def __init__(self, action=None, method=None, maxLength=None,
                 timeout=None, **kwargs):
        Grammar.__init__(self, action=action, method=method,
                         maxLength=maxLength, timeout=timeout, **kwargs)
        Grammar.check_post_get_method(method)

class Reject(Grammar):
    """Reject an incoming call

    reason: message to play when rejecting a call
    """
    REJECTED = 'rejected'
    BUSY = 'busy'

    def __init__(self, reason=None, **kwargs):
        Grammar.__init__(self, reason=reason, **kwargs)
        if not reason in (self.REJECTED, self.BUSY):
            raise PlivoException( \
                "Invalid reason parameter, must be BUSY or REJECTED")

class RecordSession(Grammar):
    """Record the call session
    """
    def __init__(self, prefix=None, **kwargs):
        Grammar.__init__(self, prefix=None, **kwargs)

class ScheduleHangup(Grammar):
    """Schedule Hangup of call after a certain time
    """
    def __init__(self, time=None, **kwargs):
        Grammar.__init__(self, time=time, **kwargs)

class PreAnswer(Grammar):
    """Answer the call in Early Media Mode and execute nested grammar
    """
    def __init__(self, time=None, **kwargs):
        Grammar.__init__(self, time=time, **kwargs)
        self.nestables = ['Play', 'Speak', 'GetDigits', 'Wait']


# Plivo Utility function and Request Validation
# ===========================================================================

class Utils(object):
    def __init__(self, auth_id='', auth_token=''):
        """initialize a plivo utility object

        auth_id: Plivo account SID/ID
        auth_token: Plivo account token

        returns a Plivo util object
        """
        self.auth_id = auth_id
        self.auth_token = auth_token

    def validateRequest(self, uri, postVars, expectedSignature):
        """validate a request from plivo

        uri: the full URI that Plivo requested on your server
        postVars: post vars that Plivo sent with the request
        expectedSignature: signature in HTTP X-Plivo-Signature header

        returns true if the request passes validation, false if not
        """

        # append the POST variables sorted by key to the uri
        s = uri
        for k, v in sorted(postVars.items()):
            s += k + v

        # compute signature and compare signatures
        return (base64.encodestring(hmac.new(self.auth_token, s, sha1).digest()).\
            strip() == expectedSignature)
