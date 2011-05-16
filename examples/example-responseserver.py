from flask import Flask, request, render_template
import plivohelper
import os

response_server = Flask("ResponseServer")
response_server.debug = True

"""
This is a simple example which demonstrate how easy you can build a light HTTP
server using Flask which will return formatted XML to command the Plivo Server

By default the HTTP Server will be listening on http://127.0.0.1:5000

The following URLs are implemented:
    * /
    * /ringing/
    * /answered/
    * /redirect/answered/
    * /getdigits/

"""

# Helper function to create IVR and return rest XML

def create_ivr_example():
    """Create a simple IVR which pause and play an audio"""
    r = plivohelper.Response()
    #r.addScheduleHangup(time=10)
    #r.addSpeak("$1000.200", loop=5, type='CURRENCY', method= 'PRONOUNCED')
    r.addSpeak("Welcome to Freeswitch", loop=2, voice='pico', engine='tts_commandline')
    r.addPlay("http://demo.twilio.com/hellomonkey/monkex.mp3", loop=1)
    r.addPlay("http://demo.twilio.com/hellomonkey/monkey.mp3", loop=1)
    r.addRedirect(url='http://127.0.0.1:5000/redirect/answered/')
    r.addHangup()
    return r

def create_transfer_rest_xml():
    r = plivohelper.Response()
    r.addWait(length=2)
    r.addSpeak("This is a transferred call in between", loop=2)
    r.addHangup()
    return r


def create_ivr_example_redirect():
    """Create an IVR which will gather DTMF when calling an extra URL and play few audio files"""
    r = plivohelper.Response()
    g = r.addGetDigits(numDigits=5, timeout=25, playBeep='true', action='http://127.0.0.1:5000/getdigits/')
    g.addPlay("/usr/local/freeswitch/sounds/en/us/callie/ivr/8000/venky.wav", loop=1)
    g.addWait(length=1)
    g.addSpeak("Hi this is venky", loop=1, voice='slt')
    g.addSpeak("Hi this is command line tts pico", loop=1, voice='pico', engine='tts_commandline')
    g.addSpeak("$1000.200", loop=2, type='CURRENCY', method= 'PRONOUNCED')
    g.addWait(length=2)
    g.addPlay("/usr/local/freeswitch/sounds/en/us/callie/ivr/8000/ivr-hello.wav", loop=2)
    r.addPlay("/usr/local/freeswitch/sounds/en/us/callie/ivr/8000/ivr-hello.wav", loop=2)
    r.addRecord(prefix="user_")
    r.addHangup()
    return r


def create_ivr_get_digits():
    """ Create an IVR which on which we are gathering DTMF, see call in create_ivr_example_redirect"""
    r = plivohelper.Response()
    r.addSpeak("Hi there. Can you hear me?", loop=2)
    r.addHangup()
    return r

def create_ivr_say_thank_123():
    """ Create an IVR"""
    r = plivohelper.Response()
    r.addSpeak("Hello and Welcome to our demo of Plivo", loop=2)
    r.addWait(length=3)
    r.addHangup()
    return r

# URLs Implementation

@response_server.errorhandler(404)
def page_not_found(error):
    """This implemente an error page when page aren't found"""
    print "404 page not found"
    return 'This URL does not exist', 404


@response_server.route('/')
def home():
    """Implement root url / """
    return "This is an example of an http server returning RESTXML!"


@response_server.route('/ringing/', methods=['GET', 'POST'])
def call_ringing():
    """Implement ringing URL"""
    # Post params- 'to': ringing number, 'request_uuid': request id given at the time of api call
    print "We got a ringing notification"
    return "OK"


@response_server.route('/hangup/', methods=['GET', 'POST'])
def call_hangup():
    """Implement the hangup URL"""
    # Post params- 'request_uuid': request id given at the time of api call,
    #               'call_uuid': unique id of call, 'reason': reason of hangup
    #request_uuid, call_uuid, reason
    if request.form:
        print "request_uuid = " + request.form['request_uuid']
        print "call_uuid = " + request.form['call_uuid']
        print "reason = " + request.form['reason']
    return "OK"


@response_server.route('/answered/', methods=['GET', 'POST'])
def rest_xml_response():
    # Post params- 'call_uuid': unique id of call, 'direction': direction of call,
    #               'called_no': Number which was called, 'from_no': calling number,
    #               If direction is outbound then 2 additional params:
    #               'aleg_uuid': Unique Id for first leg,
    #               'aleg_request_uuid': request id given at the time of api call
    print request.form['call_uuid']
    signature = request.headers['X-Plivo-Signature']
    utils = plivohelper.Utils('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
                                'YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY')
    if utils.validateRequest(request.base_url, request.form, signature):
        response = create_ivr_example()
    else:
        response = ""
    return render_template('response_template.xml', response=response)


@response_server.route('/redirect/answered/', methods=['GET', 'POST'])
def rest_redirect_xml_response():
    # Post params- Same params as rest_xml_response()
    response = create_ivr_example_redirect()
    return render_template('response_template.xml', response=response)



@response_server.route('/transfered/', methods=['GET', 'POST'])
def rest_transfer_xml_response():
     # Post params- Same params as rest_xml_response()
    response = create_transfer_rest_xml()
    return render_template('response_template.xml', response=response)


@response_server.route('/getdigits/', methods=['GET', 'POST'])
def get_digits():
    # Post params- Same params as rest_xml_response() with additional
    # 'Digit' = input digts from user
    print "DTMF = " + request.form['Digits']
    if request.form['Digits']=='123':
        response = create_ivr_get_digits()
    else:
        response = create_ivr_get_digits()
    return render_template('response_template.xml', response=response)



if __name__ == '__main__':
    if not os.path.isfile("templates/response_template.xml"):
        print "Error : Can't find the XML template : templates/response_template.xml"
    else:
        response_server.run(host='127.0.0.1', port=5000)
