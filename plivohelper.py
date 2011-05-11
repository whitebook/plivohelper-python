# -*- coding: utf-8 -*-

__VERSION__ = "0.10"


import urllib, urllib2, base64, hmac
from hashlib import sha1
from xml.sax.saxutils import escape, quoteattr
from xml.dom.minidom import Document


class RESTException(Exception):
    pass


# REST Helpers
# ===========================================================================

class HTTPErrorProcessor(urllib2.HTTPErrorProcessor):
    def https_response(self, request, response):
        code, msg, hdrs = response.code, response.msg, response.info()
        if code >= 300:
            response = self.parent.error(
                'http', request, response, code, msg, hdrs)
        return response


class RESTUrlRequest(urllib2.Request):
    def get_method(self):
        if getattr(self, 'http_method', None):
            return self.http_method
        return urllib2.Request.get_method(self)


class REST:
    """
    Provides helper functions for making REST requests to the REST API.
    """
    def __init__(self, url, id, token):
        """
        initialize an account object
        url: Rest API Url
        id: SID/ID
        token: Account token
        """
        self.url = url
        self.id = id
        self.token = token
        self.opener = None

    def _build_get_uri(self, uri, params):
        if params and len(params) > 0:
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
            req = RESTUrlRequest(uri)
        else:
            req = RESTUrlRequest(uri, urllib.urlencode(params))
            if method and (method == 'DELETE' or method == 'PUT'):
                req.http_method = method

        authstring = base64.encodestring('%s:%s' % (self.id, self.token))
        authstring = authstring.replace('\n', '')
        req.add_header("Authorization", "Basic %s" % authstring)

        response = urllib2.urlopen(req)
        return response.read()

    def request(self, path, method=None, vars={}):
        """sends a request and gets a response from the REST API

        path: the URL (relative to the endpoint URL, after the /v1
        url: the HTTP method to use, defaults to POST
        vars: for POST or PUT, a dict of data to send

        returns response in XML or raises an exception on error
        """
        if not path or len(path) < 1:
            raise ValueError('Invalid path parameter')
        if method and method not in ['GET', 'POST', 'DELETE', 'PUT']:
            raise NotImplementedError(
                'HTTP %s method not implemented' % method)

        if path[0] == '/':
            uri = self.url + path
        else:
            uri = self.url + '/' + path

        return self._urllib2_fetch(uri, vars, method)

    def call(self, call_params):
        """Call Helper
        """
        path = '/v0.1/Calls/'
        method = 'POST'
        return self.request(path, method, call_params)

    def bulk_call(self, call_params):
        """Bulk Call Helper
        """
        path = '/v0.1/BulkCalls/'
        method = 'POST'
        return self.request(path, method, call_params)

    def modify_call(self, call_params):
        """Modify Call Helper
        """
        path = '/v0.1/ModifyCall/'
        method = 'POST'
        return self.request(path, method, call_params)

    def hangup_all_calls(self):
        """Hangup All Calls Helper
        """
        path = '/v0.1/HangupAll/'
        method = 'GET'
        return self.request(path, method)


# RESTXML Response Helpers
# ===========================================================================


class Verb:
    """
    Basic verb object.
    """
    def __init__(self, **kwargs):
        self.name = self.__class__.__name__
        self.body = None
        self.nestables = None

        self.verbs = []
        self.attrs = {}
        for k, v in kwargs.items():
            if k == "sender":
                k = "from"
            if v != None:
                self.attrs[k] = unicode(v)

    def __repr__(self):
        """
        String representation of an verb
        """
        doc = Document()
        return self._xml(doc).toxml()

    def _xml(self, root):
        """
        Return an XML element representing this verb
        """
        verb = root.createElement(self.name)

        # Add attributes
        keys = self.attrs.keys()
        keys.sort()
        for a in keys:
            verb.setAttribute(a, self.attrs[a])

        if self.body:
            text = root.createTextNode(self.body)
            verb.appendChild(text)

        for c in self.verbs:
            verb.appendChild(c._xml(root))

        return verb


    def append(self, verb):
        if not self.nestables:
            raise RESTException("%s is not nestable" % self.name)
        if verb.name not in self.nestables:
            raise RESTException("%s is not nestable inside %s" % \
                (verb.name, self.name))
        self.verbs.append(verb)
        return verb

    def as_url(self):
        return urllib.quote(str(self))

    def add_say(self, text, **kwargs):
        return self.append(Say(text, **kwargs))

    def add_play(self, url, **kwargs):
        return self.append(Play(url, **kwargs))

    def add_pause(self, **kwargs):
        return self.append(Pause(**kwargs))

    def add_redirect(self, url=None, **kwargs):
        return self.append(Redirect(url, **kwargs))

    def add_hangup(self, **kwargs):
        return self.append(Hangup(**kwargs))

    def add_reject(self, **kwargs):
        return self.append(Reject(**kwargs))

    def add_gather(self, **kwargs):
        return self.append(Gather(**kwargs))

    def add_number(self, number, **kwargs):
        return self.append(Number(number, **kwargs))

    def add_dial(self, number=None, **kwargs):
        return self.append(Dial(number, **kwargs))

    def add_record(self, **kwargs):
        return self.append(Record(**kwargs))

    def add_conference(self, name, **kwargs):
        return self.append(Conference(name, **kwargs))

    def add_recordsession(self, **kwargs):
        return self.append(RecordSession(**kwargs))


class Response(Verb):
    """
    REST response object.
    """
    def __init__(self, version=None, **kwargs):
        Verb.__init__(self, version=version, **kwargs)
        self.nestables = ['Say', 'Play', 'Gather', 'Record', 'Dial',
            'Redirect', 'Pause', 'Hangup', 'Reject', 'Sms']


class Say(Verb):
    """
    Say text

    text: text to say
    voice: MAN or WOMAN
    language: language to use
    loop: number of times to say this text
    """
    MAN = 'man'
    WOMAN = 'woman'

    ENGLISH = 'en'
    SPANISH = 'es'
    FRENCH = 'fr'
    GERMAN = 'de'

    def __init__(self, text, voice=None, language=None, loop=None, **kwargs):
        Verb.__init__(self, voice=voice, language=language, loop=loop,
            **kwargs)
        self.body = text
        if voice and (voice != self.MAN and voice != self.WOMAN):
            raise RESTException( \
                "Invalid Say voice parameter, must be 'man' or 'woman'")
        if language and (language != self.ENGLISH and language != self.SPANISH
            and language != self.FRENCH and language != self.GERMAN):
            raise RESTException( \
                "Invalid Say language parameter, must be " + \
                "'en', 'es', 'fr', or 'de'")


class Play(Verb):
    """
    Play audio file at a URL

    url: url of audio file, MIME type on file must be set correctly
    loop: number of time to say this text
    """
    def __init__(self, url, loop=None, **kwargs):
        Verb.__init__(self, loop=loop, **kwargs)
        self.body = url


class Pause(Verb):
    """
    Pause the call

    length: length of pause in seconds
    """
    def __init__(self, length=None, **kwargs):
        Verb.__init__(self, length=length, **kwargs)


class Redirect(Verb):
    """
    Redirect call flow to another URL

    url: redirect url
    """
    GET = 'GET'
    POST = 'POST'

    def __init__(self, url=None, method=None, **kwargs):
        Verb.__init__(self, method=method, **kwargs)
        if method and (method != self.GET and method != self.POST):
            raise RESTException("Invalid method parameter, must be 'GET' or 'POST'")
        self.body = url


class Hangup(Verb):
    """
    Hangup the call
    """
    def __init__(self, **kwargs):
        Verb.__init__(self)


class RecordSession(Verb):
    """
    Record the call session
    """
    def __init__(self, **kwargs):
        Verb.__init__(self)


class Gather(Verb):
    """
    Gather digits from the caller's keypad

    action: URL to which the digits entered will be sent
    method: submit to 'action' url using GET or POST
    num_digits: how many digits to gather before returning
    timeout: wait for this many seconds before returning
    finish_on_key: key that triggers the end of caller input
    """
    GET = 'GET'
    POST = 'POST'

    def __init__(self, action=None, method=None, num_digits=None, timeout=None,
        finish_on_key=None, **kwargs):

        Verb.__init__(self, action=action, method=method,
            num_digits=num_digits, timeout=timeout, finish_on_key=finish_on_key,
            **kwargs)
        if method and (method != self.GET and method != self.POST):
            raise RESTException("Invalid method parameter, must be 'GET' or 'POST'")
        self.nestables = ['Say', 'Play']


class Number(Verb):
    """
    Specify phone number in a nested Dial element.

    number: phone number to dial
    send_digits: key to press after connecting to the number
    """
    def __init__(self, number, send_digits=None, **kwargs):
        Verb.__init__(self, send_digits=send_digits, **kwargs)
        self.body = number


class Conference(Verb):
    """
    Specify conference in a nested Dial element.

    name: friendly name of conference
    muted: keep this participant muted (bool)
    beep: play a beep when this participant enters/leaves (bool)
    start_conference_on_enter: start conf when this participants joins (bool)
    end_conference_on_exit: end conf when this participants leaves (bool)
    wait_url: TwiML url that executes before conference starts
    wait_method: HTTP method for wait_url GET/POST
    """
    GET = 'GET'
    POST = 'POST'

    def __init__(self, name, muted=None, beep=None,
        start_conference_on_enter=None, end_conference_on_exit=None, wait_url=None,
        wait_method=None, **kwargs):
        Verb.__init__(self, muted=muted, beep=beep,
            start_conference_on_enter=start_conference_on_enter,
            end_conference_on_exit=end_conference_on_exit, wait_url=wait_url,
            wait_method=wait_method, **kwargs)
        if wait_method and (wait_method != self.GET and wait_method != self.POST):
            raise RESTException("Invalid wait_method parameter, must be GET or POST")
        self.body = name


class Dial(Verb):
    """
    Dial another phone number and connect it to this call

    action: submit the result of the dial to this URL
    method: submit to 'action' url using GET or POST
    """
    GET = 'GET'
    POST = 'POST'

    def __init__(self, number=None, action=None, method=None, **kwargs):
        Verb.__init__(self, action=action, method=method, **kwargs)
        self.nestables = ['Number', 'Conference']
        if number and len(number.split(',')) > 1:
            for n in number.split(','):
                self.append(Number(n.strip()))
        else:
            self.body = number
        if method and (method != self.GET and method != self.POST):
            raise RESTException("Invalid method parameter, must be GET or POST")


class Record(Verb):
    """
    Record audio from caller

    action: submit the result of the dial to this URL
    method: submit to 'action' url using GET or POST
    max_length: maximum number of seconds to record
    timeout: seconds of silence before considering the recording complete
    """
    GET = 'GET'
    POST = 'POST'

    def __init__(self, action=None, method=None, max_length=None,
                 timeout=None, **kwargs):
        Verb.__init__(self, action=action, method=method, max_length=max_length,
            timeout=timeout, **kwargs)
        if method and (method != self.GET and method != self.POST):
            raise RESTException("Invalid method parameter, must be GET or POST")


class Reject(Verb):
    """
    Reject an incoming call

    reason: message to play when rejecting a call
    """
    REJECTED = 'rejected'
    BUSY = 'busy'

    def __init__(self, reason=None, **kwargs):
        Verb.__init__(self, reason=reason, **kwargs)
        if reason and (reason != self.REJECTED and reason != self.BUSY):
            raise RESTException("Invalid reason parameter, must be BUSY or REJECTED")


# Utility function and Request Validation
# ===========================================================================

class Utils:
    def __init__(self, id, token):
        """initialize an utility object

        id: Account ID
        token: Auth token

        returns a util object
        """
        self.id = id
        self.token = token

    def validate_request(self, uri, post_var, expected_signature):
        """validate a request from server

        uri: the full URI that RESTServer requested on your server
        post_var: post vars that RESTServer sent with the request
        expected_signature: signature in HTTP X-REST-Signature header

        returns true if the request passes validation, false if not
        """

        # append the POST variables sorted by key to the uri
        s = uri
        if len(post_var) > 0:
            for k, v in sorted(post_var.items()):
                s += k + v

        # compute signature and compare signatures
        digest = hmac.new(self.token, s, sha1).digest()
        encoded_str = base64.encodestring(digest).strip()
        return ( encoded_str == expected_signature)
