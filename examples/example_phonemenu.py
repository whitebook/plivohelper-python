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
    r.add_say("Main Menu")
    r.add_redirect(url='http://127.0.0.1:5000/main2/')
    return r

def create_mainmenu2():
    """Create the menu"""
    r = plivohelper.Response()
    r.add_say("Main Menu 2")
    return r


def create_phonemenu(destination=None):
    """Create the menu"""
    r = plivohelper.Response()
    print ">>>> def create_phonemenu"
    
    if destination=='hours':
        r.add_say("Initech is open Monday through Friday, 9am to 5pm")
        r.add_say("Saturday, 10am to 3pm and closed on Sundays")
        
    elif destination=='location':
        g = r.add_gather(playBeep='true', action='http://127.0.0.1:5000/phonemenu/location')
        g.add_say("For directions from the East Bay, press 1")
        g.add_say("For directions from San Jose, press 2")
        
    elif destination=='east-bay':
        r.add_say("Take BART towards San Francisco / Milbrae. Get off on Powell Street. Walk a block down 4th street")
        
    elif destination=='san-jose':
        r.add_say("Take Cal Train to the Milbrae BART station. Take any Bart train to Powell Street")
        
    elif destination=='duck':
        r.add_play("http://localhost/~areski/duck.mp3", loop=5)
        
    elif destination=='receptionist':
        r.add_say("Please wait while we connect you")
        #<Dial>NNNNNNNNNN</Dial>
        
    else:
        #default menu
        g = r.add_gather(numDigits=1, timeout=5, playBeep='true', action='http://127.0.0.1:5000/phonemenu/default')
        #the follow example Fail
        #g = r.add_gather(playBeep='true', action='http://127.0.0.1:5000/phonemenu/?node=default')
        g.add_say("Hello and welcome to the Initech Phone Menu")
        g.add_say("For business hours, press 1")
        g.add_say("For directions, press 2")
        g.add_say("To hear a duck quack, press 3")
        g.add_say("To speak to a receptionist, press 0")
        
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
def rest_xml_response():
    # Post params- 'call_uuid': unique id of call, 'direction': direction of call,
    #               'called_no': Number which was called, 'from_no': calling number,
    #               If direction is outbound then 2 additional params:
    #               'aleg_uuid': Unique Id for first leg,
    #               'aleg_request_uuid': request id given at the time of api call
    
    if request.form:
        print request.form['call_uuid']
    response = create_mainmenu2()
    print response
    #response = create_phonemenu()
    return render_template('response_template.xml', response=response)

@response_server.route('/phonemenu/', methods=['GET', 'POST'])
@response_server.route('/phonemenu/<node>', methods=['GET', 'POST'])
def gather_digits_phonemenu(node='default'):
    # Post params- Same params as rest_xml_response() with additional
    # 'Digit' = input digts from user
    destination = None
    print "HERE"
    print node
    if node=='location':
        destination='location'
    if request:
        print dir(request.form)
        if request.form and request.form['Digits']:
            dtmf = request.form['Digits']
            print "DTMF"
            print dtmf
            
            if node=='default' and DTMF==1:
                destination = 'hours'
            if node=='default' and DTMF==2:
                destination = 'location'
            if node=='default' and DTMF==3:
                destination = 'duck'
            if node=='default' and DTMF==0:
                destination = 'receptionist'
            if node=='location' and DTMF==1:
                destination = 'east-bay'
            if node=='location' and DTMF==2:
                destination = 'san-jose'
            
    #response = create_phonemenu(destination)
    response = create_mainmenu2()
    print response
    return render_template('response_template.xml', response=response)


if __name__ == '__main__':
    if not os.path.isfile("templates/response_template.xml"):
        print "Error : Can't find the XML template : templates/response_template.xml"
    else:
        response_server.run(host='127.0.0.1', port=5000)
