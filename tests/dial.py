from flask import Flask, request, render_template
import plivohelper
import os

response_server = Flask("ResponseServer")
response_server.debug = True



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
    #               'CallUUID': unique id of call, 'reason': reason of hangup
    print "We got a hangup notification"
    return "OK"

@response_server.route('/dialed/', methods=['GET', 'POST'])
def dialed():
    if request.method == 'POST':
        print request.form.items()
    else:
        print request.args.items()
    r = plivohelper.Response()
    r.addSpeak("Dial done")
    print "RESTXML Response => %s" % r
    return render_template('response_template.xml', response=r)

@response_server.route('/dialmusic/', methods=['GET', 'POST'])
def dialmusic():
    r = plivohelper.Response()
    r.addSpeak("Calling now", loop=1)
    r.addPlay("http://127.0.0.1:5000/static/duck.mp3", loop=1)
    r.addPlay("http://127.0.0.1:5000/static/duck.mp3", loop=1)
    print "RESTXML Response => %s" % r
    return render_template('response_template.xml', response=r)

@response_server.route('/confirm/', methods=['GET', 'POST'])
def confirm():
    r = plivohelper.Response()
    r.addSpeak("Confirm by pressing 9", loop=1)
    r.addPlay("http://127.0.0.1:5000/static/duck.mp3", loop=1)
    r.addPlay("http://127.0.0.1:5000/static/duck.mp3", loop=1)
    print "RESTXML Response => %s" % r
    return render_template('response_template.xml', response=r)

@response_server.route('/answered/', methods=['GET', 'POST'])
def answered():
    # Post params- 'CallUUID': unique id of call, 'Direction': direction of call,
    #               'To': Number which was called, 'From': calling number,
    #               If Direction is outbound then 2 additional params:
    #               'ALegUUID': Unique Id for first leg,
    #               'ALegRequestUUID': request id given at the time of api call

    if request.method == 'POST':
        try:
            print "CallUUID: %s" % request.form['CallUUID']
        except:
            pass
    else:
        try:
            print "CallUUID: %s" % request.args['CallUUID']
        except:
            pass
    r = plivohelper.Response()
    r.addSpeak("Dial Test")
    d = r.addDial(action="http://127.0.0.1:5000/dialed/",
                  hangupOnStar=True, timeLimit=60,
                  dialMusic="http://127.0.0.1:5000/dialmusic/",
                  confirmSound="http://127.0.0.1:5000/confirm/",
                  confirmKey="9")
    d.addNumber("4871", gateways="sofia/gateway/pstn/", gatewayTimeouts="30")
    d.addNumber("1749", gateways="sofia/gateway/pstn", gatewayTimeouts="30")
    print "RESTXML Response => %s" % r
    return render_template('response_template.xml', response=r)



if __name__ == '__main__':
    if not os.path.isfile("templates/response_template.xml"):
        print "Error : Can't find the XML template : templates/response_template.xml"
    else:
        response_server.run(host='127.0.0.1', port=5000)
