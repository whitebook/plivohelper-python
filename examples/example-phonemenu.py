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
    * /phonemenu/

"""


# Helper function to create IVR and return rest XML

def create_mainmenu():
    """Create the menu"""
    r = plivohelper.Response()
    r.addSpeak("Main Menu")
    r.addRedirect(url='http://127.0.0.1:5000/main2/')
    return r

def create_mainmenu2():
    """Create the menu"""
    r = plivohelper.Response()
    r.addSpeak("Main Menu 2")
    return r


def create_phonemenu(destination=None):
    """Create the menu"""
    print destination
    r = plivohelper.Response()
    print ">>>> def create_phonemenu"

    if destination == 'hours':
        r.addSpeak("Initech is open Monday through Friday, 9am to 5pm")
        r.addSpeak("Saturday, 10am to 3pm and closed on Sundays")

    elif destination == 'location':
        g = r.addGetDigits(playBeep='true', action='http://127.0.0.1:5000/phonemenu/location')
        g.addSpeak("For directions from the East Bay, press 1")
        g.addSpeak("For directions from San Jose, press 2")

    elif destination == 'east-bay':
        r.addSpeak("Take BART towards San Francisco / Milbrae. Get off on Powell Street. Walk a block down 4th street")

    elif destination == 'san-jose':
        r.addSpeak("Take Cal Train to the Milbrae BART station. Take any Bart train to Powell Street")

    elif destination == 'duck':
        r.addPlay("http://localhost/~areski/duck.mp3", loop=5)

    elif destination == 'receptionist':
        r.addSpeak("Please wait while we connect you")
        #<Dial>NNNNNNNNNN</Dial>

    else:
        #default menu
        #g = r.addGetDigits(numDigits=1, timeout=5, playBeep='true', action='http://127.0.0.1:5000/phonemenu/default')
        #the follow example Fail
        g = r.addGetDigits(playBeep='true', action='http://127.0.0.1:5000/phonemenu/?node=hours', method="GET")
        g.addSpeak("Hello and welcome to the Initech Phone Menu")
        g.addSpeak("For business hours, press 1")
        g.addSpeak("For directions, press 2")
        g.addSpeak("To hear a duck quack, press 3")
        g.addSpeak("To speak to a receptionist, press 0")

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

    if request.form:
        print request.form['call_uuid']
    response = create_mainmenu()
    print response
    #response = create_phonemenu()
    return render_template('response_template.xml', response=response)

@response_server.route('/main2/', methods=['GET', 'POST'])
def rest_xml_response_main2():
    # Post params- 'call_uuid': unique id of call, 'direction': direction of call,
    #               'called_no': Number which was called, 'from_no': calling number,
    #               If direction is outbound then 2 additional params:
    #               'aleg_uuid': Unique Id for first leg,
    #               'aleg_request_uuid': request id given at the time of api call

    if request.form:
        print request.form['call_uuid']
    #response = create_mainmenu2()
    response = create_phonemenu()
    print response
    return render_template('response_template.xml', response=response)

@response_server.route('/phonemenu/', methods=['GET', 'POST'])
@response_server.route('/phonemenu/<node>', methods=['GET', 'POST'])
def gather_digits_phonemenu(node='default'):
    # Post params- Same params as rest_xml_response() with additional
    # 'Digit' = input digts from user
    destination = None
    print "HERE"

    # get node from url : if found overwrite current node set
    node = request.args.get('node', node)

    print node

    if node == 'location':
        destination = 'location'
    if request:
        print dir(request.form.items())
        if request.form and request.form['Digits']:
            dtmf = request.form['Digits']
            print "DTMF"
            print dtmf

            if node == 'default' and dtmf == '1':
                destination = 'hours'
            if node == 'default' and dtmf == '2':
                destination = 'location'
            if node == 'default' and dtmf == '3':
                destination = 'duck'
            if node == 'default' and dtmf == '0':
                destination = 'receptionist'
            if node == 'location' and dtmf == '1':
                destination = 'east-bay'
            if node == 'location' and dtmf == '2':
                destination = 'san-jose'
    if node == 'hours':
        destination = 'hours'

    response = create_phonemenu(destination)
    #response = create_mainmenu2()
    print response
    return render_template('response_template.xml', response=response)


if __name__ == '__main__':
    if not os.path.isfile("templates/response_template.xml"):
        print "Error : Can't find the XML template : templates/response_template.xml"
    else:
        response_server.run(host='127.0.0.1', port=5000)
