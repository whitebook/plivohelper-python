#!/usr/bin/env python

import resthelper

# ===========================================================================
# Using Say, Dial, and Play
r = resthelper.Response()
r.append(resthelper.Say("Hello World", voice=resthelper.Say.WOMAN, language=resthelper.Say.ENGLISH, loop=10))
r.append(resthelper.Dial("4155551212", time_limit=45))
r.append(resthelper.Play("http://www.mp3.com"))
print r

""" outputs:
<Response>
    <Say voice="man" language="fr" loop="10">Hello World</Say>
    <Dial timeLimit="45">4155551212</Dial>
    <Play>http://www.mp3.com</Play>
</Response>
"""

# The same XML can be created above using the convenience methods
r = resthelper.Response()
r.add_say("Hello World", voice=resthelper.Say.WOMAN, language=resthelper.Say.ENGLISH, loop=10)
r.add_dial("4155551212", time_limit=45)
r.add_play("http://www.mp3.com")
print r


# ===========================================================================
# Using Gather, Redirect
r = resthelper.Response()
g = r.append(resthelper.Gather(num_digits=1))
g.append(resthelper.Say("Press 1"))
r.append(resthelper.Redirect())
print r

""" outputs:
<Response>
    <Gather numDigits="1">
        <Say>Press 1</Say>
    </Gather>
    <Redirect/>
</Response>
"""

# ===========================================================================
# Adding a Say verb multiple times
r = resthelper.Response()
s = resthelper.Say("Press 1")
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
r = resthelper.Response()
r.append(resthelper.Redirect(crazy="delicious"))
print r

""" outputs:
<Response>
    <Redirect crazy="delicious"/>
</Response>
"""
