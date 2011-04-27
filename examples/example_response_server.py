from flask import Flask, request, render_template

import plivohelper

response_server = Flask("ResponseServer")
response_server.debug = True


@response_server.errorhandler(404)
def page_not_found(error):
    return 'This URL does not exist', 404


def create_rest_xml():
    r = plivohelper.Response()
    r.add_pause(length=3)
    r.add_play("/usr/local/freeswitch/sounds/en/us/callie/ivr/8000/ivr-hello.wav", loop=1)
    r.add_redirect(url='http://127.0.0.1:5000/redirect/answered/')
    r.add_hangup()
    return r


def create_redirect_rest_xml():
    r = plivohelper.Response()
    g = r.add_gather(numDigits=25, timeout=25, playBeep='true', action='http://127.0.0.1:5000/gather/dtmf/')
    g.add_play("/usr/local/freeswitch/sounds/en/us/callie/ivr/8000/ivr-generic_greeting.wav", loop=1)
    g.add_play("/usr/local/freeswitch/sounds/en/us/callie/ivr/8000/ivr-hello.wav", loop=1)
    r.add_pause(length=5)
    r.add_play("/usr/local/freeswitch/sounds/en/us/callie/ivr/8000/ivr-hello.wav", loop=2)
    r.add_record()
    r.add_hangup()
    return r


def create_gather_digits():
    r = plivohelper.Response()
    r.add_pause(length=5)
    r.add_play("/usr/local/freeswitch/sounds/en/us/callie/ivr/8000/ivr-dude_you_suck.wav", loop=1)
    r.add_hangup()
    return r


@response_server.route('/')
def home():
    return "This is an example of a server return RESTXML!"


@response_server.route('/ringing/', methods=['GET', 'POST'])
def call_ringing():
    # Post params- 'to': ringing number, 'request_uuid': request id given at the time of api call
    return "OK"


@response_server.route('/hangup/', methods=['GET', 'POST'])
def call_hangup():
    # Post params- 'request_uuid': request id given at the time of api call,
    #               'call_uuid': unique id of call, 'reason': reason of hangup
    return "OK"


@response_server.route('/answered/', methods=['GET', 'POST'])
def rest_xml_response():
    # Post params- 'call_uuid': unique id of call, 'direction': direction of call,
    #               'called_no': Number which was called, 'from_no': calling number,
    #               If direction is outbound then 2 additional params:
    #               'aleg_uuid': Unique Id for first leg,
    #               'aleg_request_uuid': request id given at the time of api call

    response = create_rest_xml()
    return render_template('response_template.xml', response=response)


@response_server.route('/redirect/answered/', methods=['GET', 'POST'])
def rest_redirect_xml_response():
    # Post params- Same params as rest_xml_response()
    response = create_redirect_rest_xml()
    return render_template('response_template.xml', response=response)


@response_server.route('/gather/dtmf/', methods=['GET', 'POST'])
def gather_digits():
    # Post params- Same params as rest_xml_response() with additional
    # 'Digit' = input digts from user
    response = create_gather_digits()
    return render_template('response_template.xml', response=response)



if __name__ == '__main__':
    response_server.run()
