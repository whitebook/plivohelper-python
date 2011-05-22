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
    * /transfered/

"""


# Helper function to create IVR and return rest XML

def create_mainmenu():
    """Create the menu"""
    print ">>> Create main menu"
    r = plivohelper.Response()
    r.addSpeak("Welcome to Plivo demo, you are in main menu")
    r.addRedirect(url='http://127.0.0.1:5000/phonemenu/')
    return r

def create_phonemenu(destination=None):
    """Create the menu"""
    r = plivohelper.Response()
    print ">>> Creating phonemenu ..."
    print "Destination is %s" % str(destination)

    if destination == 'hours':
        r.addSpeak("Initech is open Monday through Friday, 9am to 5pm")
        r.addSpeak("Saturday, 10am to 3pm and closed on Sundays")
        r.addRedirect(url='http://127.0.0.1:5000/phonemenu/')
    elif destination == 'location':
        g = r.addGetDigits(numDigits=1, playBeep='true', action='http://127.0.0.1:5000/phonemenu/location')
        g.addSpeak("For directions from the East Bay, press 1")
        g.addSpeak("For directions from San Jose, press 2")
        r.addRedirect(url='http://127.0.0.1:5000/phonemenu/')
    elif destination == 'east-bay':
        r.addSpeak("Take BART towards San Francisco / Milbrae. Get off on Powell Street. Walk a block down 4th street")
        r.addRedirect(url='http://127.0.0.1:5000/phonemenu/exit')
    elif destination == 'san-jose':
        r.addSpeak("Take Cal Train to the Milbrae BART station. Take any Bart train to Powell Street")
        r.addRedirect(url='http://127.0.0.1:5000/phonemenu/exit')
    elif destination == 'duck':
        r.addSpeak("Duck typing is so good in python", loop=1)
        r.addRedirect(url='http://127.0.0.1:5000/phonemenu/exit')
    elif destination == 'receptionist':
        r.addSpeak("Please wait while we connect you")
        r.addRedirect(url='http://127.0.0.1:5000/phonemenu/')
    elif destination == 'exit':
        r.addSpeak("Goodbye ! Thank you for testing Plivo")
        r.addHangup()
    else:
        #default menu
        g = r.addGetDigits(numDigits=1, playBeep='true', action='http://127.0.0.1:5000/phonemenu/', method="GET")
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
    print "We got a hangup notification"
    return "OK"

@response_server.route('/answered/', methods=['GET', 'POST'])
def rest_xml_response():
    # Post params- 'call_uuid': unique id of call, 'direction': direction of call,
    #               'called_no': Number which was called, 'from_no': calling number,
    #               If direction is outbound then 2 additional params:
    #               'aleg_uuid': Unique Id for first leg,
    #               'aleg_request_uuid': request id given at the time of api call

    if request.form:
        print "CallUUID: %s" % request.form['call_uuid']
    response = create_mainmenu()
    print response
    return render_template('response_template.xml', response=response)

@response_server.route('/phonemenu/', methods=['GET', 'POST'])
@response_server.route('/phonemenu/<destination>', methods=['GET', 'POST'])
def gather_digits_phonemenu(destination='default'):
    # Post params- Same params as rest_xml_response() with additional
    # 'Digit' = input digts from user

    # Get destination from url query string:
    # if found overwrite current destination set

    if request.method == 'POST':
        destination = request.args.get('destination', destination)
        print "Found Destination %s" % str(destination)
        print "Received params : %s" % str(request.form.items())
        dtmf = request.form.get('Digits', None)
    else:
        destination = request.args.get('destination', destination)
        print "Found Destination %s" % str(destination)
        print "Received params : %s" % str(request.args)
        dtmf = request.args.get('Digits', None)

    if dtmf:
        print "Received DTMF %s" % str(dtmf)
        if destination == 'default' and dtmf == '1':
            destination = 'hours'
        elif destination == 'default' and dtmf == '2':
            destination = 'location'
        elif destination == 'default' and dtmf == '3':
            destination = 'duck'
        elif destination == 'default' and dtmf == '0':
            destination = 'receptionist'
        elif destination == 'location' and dtmf == '1':
            destination = 'east-bay'
        elif destination == 'location' and dtmf == '2':
            destination = 'san-jose'
        else:
            destination = 'default'

    print "New Destination is %s" % str(destination)

    response = create_phonemenu(destination)
    print "RESTXML Response => %s" % response
    return render_template('response_template.xml', response=response)

@response_server.route('/transfered/', methods=['GET', 'POST'])
def rest_xml_transfer():
    """Implement the transfer URL"""
    # Post params- 'request_uuid': request id given at the time of api call,
    #               'call_uuid': unique id of call, 'reason': reason of hangup
    print "We got a transfer notification"
    r = plivohelper.Response()
    r.addSpeak("Transfering call now !")
    r.addRedirect(url='http://127.0.0.1:5000/phonemenu/exit')
    print r
    return render_template('response_template.xml', response=r)



if __name__ == '__main__':
    if not os.path.isfile("templates/response_template.xml"):
        print "Error : Can't find the XML template : templates/response_template.xml"
    else:
        response_server.run(host='127.0.0.1', port=5000)
