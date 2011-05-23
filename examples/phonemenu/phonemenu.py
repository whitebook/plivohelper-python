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
    * /ringing/
    * /answered/
    * /hangup/
    * /phonemenu/
"""


web = {}
web['default'] = ('receptionist','hours', 'location', 'duck')
web['location'] = ('receptionist','east-bay', 'san-jose', 'marin')



@response_server.errorhandler(404)
def page_not_found(error):
    """error page"""
    print "404 page not found"
    return 'This URL does not exist', 404

@response_server.route('/ringing/', methods=['GET', 'POST'])
def ringing():
    """ringing URL"""
    # Post params- 'to': ringing number, 'request_uuid': request id given at the time of api call
    print "We got a ringing notification"
    return "OK"

@response_server.route('/hangup/', methods=['GET', 'POST'])
def hangup():
    """hangup URL"""
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
    # Default destination
    destination = 'default'
    # Get destination from url query string: 
    # 'node' : destination
    # 'Digits' : input digits from user
    if request.method == 'POST':
        node = request.args.get('node', None)
        dtmf = request.form.get('Digits', -1)
    else:
        node = request.args.get('node', None)
        dtmf = request.args.get('Digits', -1)
    if not node:
        node = 'default'
    try:
        digits = int(dtmf)
    except ValueError:
        digits = -1

    if digits >= 0:
        try:
            destination = web[node][digits]
        except (KeyError, IndexError):
            destination = 'default'

    print "Destination %s" % str(destination)
    print "Digits %s" % str(digits)

    r = plivohelper.Response()

    if destination == 'hours':
        r.addSpeak("Initech is open Monday through Friday, 9am to 5pm")
        r.addSpeak("Saturday, 10am to 3pm and closed on Sundays")
    elif destination == 'location':
        g = r.addGetDigits(numDigits=1, 
                   action='http://127.0.0.1:5000/phonemenu/?node=location')
        g.addSpeak("For directions from the East Bay, press 1")
        g.addSpeak("For directions from San Jose, press 2")
    elif destination == 'east-bay':
        r.addSpeak("Take BART towards San Francisco / Milbrae. Get off on Powell Street. Walk a block down 4th street")
    elif destination == 'san-jose':
        r.addSpeak("Take Cal Train to the Milbrae BART station. Take any Bart train to Powell Street")
    elif destination == 'duck':
        r.addPlay("http://127.0.0.1:5000/static/duck.mp3")
    elif destination == 'receptionist':
        r.addSpeak("Please wait while we connect you")
        r.addDial("NNNNNNNNNN")
    else:
        # default menu
        g = r.addGetDigits(numDigits=1, 
                           action='http://127.0.0.1:5000/phonemenu/?node=default')
        g.addSpeak("Hello and welcome to the Initech Phone Menu")
        g.addSpeak("For business hours, press 1")
        g.addSpeak("For directions, press 2")
        g.addSpeak("To hear a duck quack, press 3")
        g.addSpeak("To speak to a receptionist, press 0")

    print "RESTXML Response => %s" % r
    return render_template('response_template.xml', response=r)



if __name__ == '__main__':
    if not os.path.isfile("templates/response_template.xml"):
        print "Error : Can't find the XML template : templates/response_template.xml"
    else:
        response_server.run(host='127.0.0.1', port=5000)

