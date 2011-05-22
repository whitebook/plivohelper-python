from flask import Flask, request, render_template, url_for
import plivohelper
import os

response_server = Flask("ResponseServer")
response_server.debug = True

"""
This is a simple example which demonstrate how easy you can build a light HTTP
server using Flask which will return formatted XML to command the Plivo Server

By default the HTTP Server will be listening on http://127.0.0.1:5000

The following URLs are implemented:
    * /ringing/
    * /answered/
    * /hangup/
    * /phonemenu/

"""

#url_for('static', filename='duck.mp3')


@response_server.errorhandler(404)
def page_not_found(error):
    """This implemente an error page when page aren't found"""
    print "404 page not found"
    return 'This URL does not exist', 404

@response_server.route('/ringing/', methods=['GET', 'POST'])
def ringing():
    """Implement ringing URL"""
    # Post params- 'to': ringing number, 'request_uuid': request id given at the time of api call
    print "We got a ringing notification"
    return "OK"

@response_server.route('/hangup/', methods=['GET', 'POST'])
def hangup():
    """Implement the hangup URL"""
    # Post params- 'request_uuid': request id given at the time of api call,
    #               'call_uuid': unique id of call, 'reason': reason of hangup
    print "We got a hangup notification"
    return "OK"

@response_server.route('/answered/', methods=['GET', 'POST'])
def answered():
    # Post params- 'call_uuid': unique id of call, 'direction': direction of call,
    #               'called_no': Number which was called, 'from_no': calling number,
    #               If direction is outbound then 2 additional params:
    #               'aleg_uuid': Unique Id for first leg,
    #               'aleg_request_uuid': request id given at the time of api call

    if request.method == 'POST':
        try:
            print "CallUUID: %s" % request.form['call_uuid']
        except:
            pass
    else:
        try:
            print "CallUUID: %s" % request.args['call_uuid']
        except:
            pass
    return phonemenu()


@response_server.route('/phonemenu/', methods=['GET', 'POST'])
def phonemenu():
    # default destination
    destination = 'default'
    # Get destination from url query string: 
    # 'node' : destination
    # 'Digits' : input digits from user
    if request.method == 'POST':
        destination = request.args.get('node', destination)
        dtmf = request.form.get('Digits', None)
    else:
        destination = request.args.get('node', destination)
        dtmf = request.args.get('Digits', None)

    if dtmf:
        print "Received DTMF %s" % str(dtmf)
        if destination == 'default':
            if dtmf == '1':
                destination = 'hours'
            elif dtmf == '2':
                destination = 'location'
            elif dtmf == '3':
                destination = 'duck'
            elif dtmf == '0':
                destination = 'receptionist'
        elif destination == 'location':
            if dtmf == '1':
                destination = 'east-bay'
            elif dtmf == '2':
                destination = 'san-jose'

    print "Destination %s" % str(destination)

    restxml = plivohelper.Response()

    if destination == 'hours':
        restxml.addSpeak("Initech is open Monday through Friday, 9am to 5pm")
        restxml.addSpeak("Saturday, 10am to 3pm and closed on Sundays")
    elif destination == 'location':
        g = restxml.addGetDigits(numDigits=1, playBeep='true', 
                           action='http://127.0.0.1:5000/phonemenu/?node=location')
        g.addSpeak("For directions from the East Bay, press 1")
        g.addSpeak("For directions from San Jose, press 2")
    elif destination == 'east-bay':
        restxml.addSpeak("Take BART towards San Francisco / Milbrae. Get off on Powell Street. Walk a block down 4th street")
    elif destination == 'san-jose':
        restxml.addSpeak("Take Cal Train to the Milbrae BART station. Take any Bart train to Powell Street")
    elif destination == 'duck':
        restxml.addPlay("http://127.0.0.1:5000/static/duck.mp3")
    elif destination == 'receptionist':
        restxml.addSpeak("Please wait while we connect you")
        restxml.addDial("NNNNNNNNNN")
    else:
        # default menu
        g = restxml.addGetDigits(numDigits=1, playBeep='true', 
                           action='http://127.0.0.1:5000/phonemenu/?node=default', 
                           method="GET")
        g.addSpeak("Hello and welcome to the Initech Phone Menu")
        g.addSpeak("For business hours, press 1")
        g.addSpeak("For directions, press 2")
        g.addSpeak("To hear a duck quack, press 3")
        g.addSpeak("To speak to a receptionist, press 0")

    print "RESTXML Response => %s" % restxml
    return render_template('response_template.xml', response=restxml)



if __name__ == '__main__':
    if not os.path.isfile("templates/response_template.xml"):
        print "Error : Can't find the XML template : templates/response_template.xml"
    else:
        response_server.run(host='127.0.0.1', port=5000)

