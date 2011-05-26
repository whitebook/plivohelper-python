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

@response_server.route('/menu/', methods=['GET', 'POST'])
def menu():
    if request.method == 'POST':
        print request.form.items()
        digits = request.form.get('Digits', '')
        try:
            print "CallUUID: %s" % request.form['CallUUID']
        except:
            pass
    else:
        print request.args.items()
        digits = request.args.get('Digits', '')
        try:
            print "CallUUID: %s" % request.args['CallUUID']
        except:
            pass
    r = plivohelper.Response()
    if digits:
        speak_digits = ", ".join([ d for d in digits ])
        r.addSpeak("Get Digits. Digits pressed %s" % speak_digits)
    else:
        r.addSpeak("Get Digits. No digits pressed")
    r.addSpeak("Get Digits Ended")
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
    d = r.addGetDigits(action="http://127.0.0.1:5000/menu/", 
                       timeout=10, retries=2, finishOnKey='#',
                       numDigits=2, playBeep=True, 
                       validDigits="01234")
    d.addSpeak("Get Digits. Press 0, 1, 2, 3 or 4")
    print "RESTXML Response => %s" % r
    return render_template('response_template.xml', response=r)



if __name__ == '__main__':
    if not os.path.isfile("templates/response_template.xml"):
        print "Error : Can't find the XML template : templates/response_template.xml"
    else:
        response_server.run(host='127.0.0.1', port=5000)
