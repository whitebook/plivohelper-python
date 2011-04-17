#!/usr/bin/env python

import resthelpers

# ===========================================================================
# Using Say, Dial, and Play
r = resthelpers.Response()
r.append(resthelpers.Say("Hello World", voice=resthelpers.Say.WOMAN, language=resthelpers.Say.ENGLISH, loop=10))
r.append(resthelpers.Dial("4155551212", time_limit=45))
r.append(resthelpers.Play("http://www.mp3.com"))
print r

""" outputs:
<Response>
    <Say voice="man" language="fr" loop="10">Hello World</Say>
    <Dial timeLimit="45">4155551212</Dial>
    <Play>http://www.mp3.com</Play>
</Response>
"""

# The same XML can be created above using the convenience methods
r = resthelpers.Response()
r.add_say("Hello World", voice=resthelpers.Say.WOMAN, language=resthelpers.Say.ENGLISH, loop=10)
r.add_dial("4155551212", time_limit=45)
r.add_play("http://www.mp3.com")
print r


# ===========================================================================
# Using Gather, Redirect
r = resthelpers.Response()
g = r.append(resthelpers.Gather(num_digits=1))
g.append(resthelpers.Say("Press 1"))
r.append(resthelpers.Redirect())
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
r = resthelpers.Response()
s = resthelpers.Say("Press 1")
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
r = resthelpers.Response()
r.append(resthelpers.Redirect(crazy="delicious"))
print r

""" outputs:
<Response>
    <Redirect crazy="delicious"/>
</Response>
"""
