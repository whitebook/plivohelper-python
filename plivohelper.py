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

class Element(object):
    """Plivo basic element object.
    """
    def __init__(self, **kwargs):
        self.name = self.__class__.__name__
        self.body = None
        self.nestables = None
        self.elements = []
        self.attrs = {}
        for k, v in kwargs.items():
            if k == "sender":
                k = "from"
            if v is True or v is False:
                v = Element.bool2txt(v)
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
        String representation of a element
        """
        doc = Document()
        return self._xml(doc).toxml()

    def _xml(self, root):
        """
        Return an XML element representing this element
        """
        element = root.createElement(self.name)

        # Add attributes
        keys = self.attrs.keys()
        keys.sort()
        for a in keys:
            element.setAttribute(a, self.attrs[a])

        if self.body:
            text = root.createTextNode(self.body)
            element.appendChild(text)

        for c in self.elements:
            element.appendChild(c._xml(root))

        return element

    @staticmethod
    def check_post_get_method(method=None):
        if not method in ('GET', 'POST'):
            raise PlivoException("Invalid method parameter, must be 'GET' or 'POST'")

    def append(self, element):
        if not self.nestables:
            raise PlivoException("%s is not nestable" % self.name)
        if not element.name in self.nestables:
            raise PlivoException("%s is not nestable inside %s" % \
                            (element.name, self.name))
        self.elements.append(element)
        return element

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

    def addPreAnswer(self, **kwargs):
        return self.append(PreAnswer(**kwargs))


class Response(Element):
    """Plivo response object.

    version: Plivo API version 0.1
    """
    def __init__(self, version=None, **kwargs):
        Element.__init__(self, version=version, **kwargs)
        self.nestables = ['Speak', 'Play', 'GetDigits', 'Record', 'Dial',
            'Redirect', 'Wait', 'Hangup', 'PreAnswer', 'Conference']

class Speak(Element):
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
        Element.__init__(self, voice=voice, language=language, loop=loop, **kwargs)
        self.body = text
        if not language in (self.ENGLISH, self.SPANISH,
                            self.FRENCH, self.GERMAN):
            raise PlivoException( \
                "Invalid Say language parameter, must be " + \
                "'en', 'es', 'fr', or 'de'")

class Play(Element):
    """Play audio file at a URL

    url: url of audio file, MIME type on file must be set correctly
    loop: number of time to say this text
    """
    def __init__(self, url, loop=1, **kwargs):
        Element.__init__(self, loop=loop, **kwargs)
        self.body = url

class Wait(Element):
    """Wait for some time to further process the call

    length: length of wait time in seconds
    """
    def __init__(self, length, transferEnabled=False):
        Element.__init__(self, length=length, transferEnabled=transferEnabled)

class Redirect(Element):
    """Redirect call flow to another URL

    url: redirect url
    """
    def __init__(self, url=None, method="POST", **kwargs):
        Element.__init__(self, method=method, **kwargs)
        Element.check_post_get_method(method)
        self.body = url

class Hangup(Element):
    """Hangup the call
    """
    VALID_REASONS = ('rejected', 'busy')

    def __init__(self, reason=None, schedule=0, **kwargs):
        Element.__init__(self, reason=reason, schedule=schedule, **kwargs)
        if not reason in self.VALID_REASONS:
            reason = ''
        schedule = int(schedule)
        if schedule < 0:
            schedule = 0

class GetDigits(Element):
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

        Element.__init__(self, action=action, method=method,
                         numDigits=numDigits, timeout=timeout,
                         finishOnKey=finishOnKey, **kwargs)
        Element.check_post_get_method(method)
        self.nestables = ['Speak', 'Play', 'Wait']

class Number(Element):
    """Specify phone number in a nested Dial element.

    number: phone number to dial
    sendDigits: key to press after connecting to the number
    """
    def __init__(self, number, sendDigits=None, **kwargs):
        Element.__init__(self, sendDigits=sendDigits, **kwargs)
        self.body = number

class Conference(Element):
    """Enter a conference room.

    name: room name

    waitSound: sound to play while alone in conference 
          Can be a list of sound files separated by comma.
          (default no sound)
    muted: enter conference muted 
          (default false)
    startConferenceOnEnter: the conference start when this member joins 
          (default true)
    endConferenceOnExit: close conference after this member leaves 
          (default false)
    maxMembers: max members in conference 
          (0 for max : 200)
    enterSound: sound to play when a member enters
          if empty, disabled
          if 'beep:1', play one beep
          if 'beep:2', play two beeps
          (default disabled)
    exitSound: sound to play when a member exits
          if empty, disabled
          if 'beep:1', play one beep
          if 'beep:2', play two beeps
          (default disabled)
    timeLimit: max time in seconds before closing conference 
          (default 0, no timeLimit)
    hangupOnStar: exit conference when member press '*' 
          (default false)
    """
    def __init__(self, name,
                 muted=False, waitSound='',
                 startConferenceOnEnter=True, endConferenceOnExit=False,
                 maxMembers=0, enterSound='', exitSound='',
                 timeLimit=0, hangupOnStar=False, **kwargs):
        Element.__init__(self, muted=muted, waitSound=waitSound,
                         startConferenceOnEnter=startConferenceOnEnter, 
                         endConferenceOnExit=endConferenceOnExit,
                         maxMembers=maxMembers, enterSound=enterSound,
                         exitSound=exitSound, timeLimit=timeLimit,
                         hangupOnStar=hangupOnStar, **kwargs)
        self.body = name

class Dial(Element):
    """Dial another phone number and connect it to this call

    action: submit the result of the dial to this URL
    method: submit to 'action' url using GET or POST
    """
    def __init__(self, number=None, action=None, method='POST', **kwargs):
        Element.__init__(self, action=action, method=method, **kwargs)
        self.nestables = ['Number']
        Element.check_post_get_method(method)
        if number:
            numbers = number.split(',')
            if numbers:
                for n in numbers:
                    self.append(Number(n.strip()))
            else:
                self.body = number

class Record(Element):
    """Record audio from caller

    maxLength: maximum number of seconds to record (default 60)
    timeout: seconds of silence before considering the recording complete (default 500)
    playBeep: play a beep before recording (true/false, default true)
    format: file format (default mp3)
    filePath: complete file path to save the file to
    finishOnKey: Stop recording on this key
    prefix: prefix appended to record file
    bothLegs: record both legs (true/false, default false)
              no beep will be played
    """
    def __init__(self, maxLength=None, timeout=None, 
                 playBeep=True, format=None,
                 filePath=None, finishOnKey=None, prefix=None,
                 bothLegs=False, **kwargs):
        Element.__init__(self, maxLength=maxLength,
                         timeout=timeout, playBeep=playBeep,
                         format=format, filePath=filePath,
                         finishOnKey=finishOnKey, prefix=prefix,
                         bothLegs=bothLegs, **kwargs)

class PreAnswer(Element):
    """Answer the call in Early Media Mode and execute nested element
    """
    def __init__(self, time=None, **kwargs):
        Element.__init__(self, time=time, **kwargs)
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
