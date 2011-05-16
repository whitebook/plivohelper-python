#!/usr/bin/env python

"""
The RESTXML Python Response Library makes it easy to write RESTXML without having
to touch XML. Error checking is built in to help preventing invalid markup.

USAGE:
To create RESTXML, you will make RESTXML Grammar.
Convenience methods are provided to simplify RESTXML creation.

SUPPORTED GRAMMAR:
    Response
    Speak
    Play
    Dial
    GetDigits
    Hangup
    Redirect
    Record
    Wait
    Number
    Conference
    PreAnswer
    RecordSession
    ScheduleHangup
"""

import plivohelper

# ===========================================================================
# Using Speak, Dial, and Play
r = plivohelper.Response()
r.append(plivohelper.Speak("Hello World", loop=10))
r.append(plivohelper.Dial("4155551212", timeLimit=45))
r.append(plivohelper.Play("http://www.mp3.com"))
print r
print "\n\n"

""" outputs:
<Response>
    <Speak loop="10">Hello World</Speak>
    <Dial timeLimit="45">4155551212</Dial>
    <Play>http://www.mp3.com</Play>
</Response>
"""

# The same XML can be created above using the convenience methods
r = plivohelper.Response()
r.addSpeak("Hello World", loop=10)
r.addDial("4155551212", timeLimit=45)
r.addScheduleHangup(time=10)
r.addPlay("http://www.mp3.com")
print r
print "\n\n"

# ===========================================================================
# Using Gather, Redirect
r = plivohelper.Response()
g = r.addGetDigits(numDigits=25, timeout=25, playBeep='true')
g.addPlay("/usr/local/freeswitch/sounds/en/us/callie/ivr/8000/ivr-hello.wav", loop=2)
r.addWait(length=5)
r.addPlay("/usr/local/freeswitch/sounds/en/us/callie/ivr/8000/ivr-hello.wav", loop=2)
r.addRecord()
r.addHangup()
print r
print "\n\n"

""" outputs:
<Response>
    <GetDigits numdigits="1">
        <Play loop="2">/usr/local/freeswitch/sounds/en/us/callie/ivr/8000/ivr-hello.wav</Play>
    </GetDigits>
    <Pause length="5"/>
    <Play loop="2">/usr/local/freeswitch/sounds/en/us/callie/ivr/8000/ivr-hello.wav</Play>
    <Record/>
    <Hangup/>
</Response>
"""

# ===========================================================================
# Adding a Speak Grammar Element multiple times
r = plivohelper.Response()
s = plivohelper.Speak("Press 1")
r.append(s)
r.append(s)
print r
print "\n\n"

""" outputs:
<Response>
    <Speak>Press 1</Speak>
    <Speak>Press 1</Speak>
</Response>
"""

# ===========================================================================
# You may want to add an attribute to a Grammar Element that the library doesn't support.
# To set arbitrary attribute / value pairs, just include the new attribute
# as a named parameter
r = plivohelper.Response()
r.append(plivohelper.Redirect(crazy="delicious"))
print r
print "\n\n"

""" outputs:
<Response>
    <Redirect crazy="delicious"/>
</Response>
"""
