#!/usr/bin/env python

import plivohelper

# ===========================================================================
# Using Say, Dial, and Play
r = plivohelper.Response()
r.append(plivohelper.Say("Hello World", voice=plivohelper.Say.WOMAN, language=plivohelper.Say.ENGLISH, loop=10))
#r.append(plivohelper.Conference("myroom"))
r.append(plivohelper.Dial("4155551212", time_limit=45))
r.append(plivohelper.Play("http://www.mp3.com"))
print r

""" outputs:
<Response>
    <Say voice="man" language="fr" loop="10">Hello World</Say>
    <Dial timeLimit="45">4155551212</Dial>
    <Play>http://www.mp3.com</Play>
</Response>
"""

# The same XML can be created above using the convenience methods
r = plivohelper.Response()
r.add_say("Hello World", voice=plivohelper.Say.WOMAN, language=plivohelper.Say.ENGLISH, loop=10)
r.add_dial("4155551212", time_limit=45)
r.add_schedulehangup(time=10)
r.add_play("http://www.mp3.com")
print r


# ===========================================================================
# Using Gather, Redirect
r = plivohelper.Response()
g = r.add_gather(num_digits=25, timeout=25, play_beep='true')
g.add_play("/usr/local/freeswitch/sounds/en/us/callie/ivr/8000/ivr-hello.wav", loop=2)
r.add_pause(length=5)
r.add_play("/usr/local/freeswitch/sounds/en/us/callie/ivr/8000/ivr-hello.wav", loop=2)
r.add_record()
r.add_hangup()
print r

""" outputs:
<Response>
    <Gather numdigits="1">
        <Play loop="2">/usr/local/freeswitch/sounds/en/us/callie/ivr/8000/ivr-hello.wav</Play>
    </Gather>
    <Pause length="5"/>
    <Play loop="2">/usr/local/freeswitch/sounds/en/us/callie/ivr/8000/ivr-hello.wav</Play>
    <Record/>
    <Hangup/>
</Response>
"""

# ===========================================================================
# Adding a Say verb multiple times
r = plivohelper.Response()
s = plivohelper.Say("Press 1")
r.append(s)
r.append(s)
print r

""" outputs:
<Response>
    <Say>Press 1</Say>
    <Say>Press 1</Say>
</Response>
"""

# ===========================================================================
# You may want to add an attribute to a verb that the library doesn't support.
# To set arbitrary attribute / value pairs, just include the new attribute
# as a named parameter
r = plivohelper.Response()
r.append(plivohelper.Redirect(crazy="delicious"))
print r

""" outputs:
<Response>
    <Redirect crazy="delicious"/>
</Response>
"""
