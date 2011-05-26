
Plivo Python Helper Library
---------------------------

Description
~~~~~~~~~~~

The Plivo Python helper simplifies the process of making REST calls and generating RESTXML.

See `Plivo Documentation <http://www.plivo.org/docs/>`_ for more information.


Installation
~~~~~~~~~~~~~

**Run:**
    $ sudo pip install plivohelper


Manual Installation
~~~~~~~~~~~~~~~~~~~~

**Download the source and run:**
    $ sudo python setup.py install


Usage
~~~~~
To use the Plivo helper library, just 'import plivohelper' in the your current python file.
As shown in example-call.py, you will need to specify the ACCOUNT_ID and ACCOUNT_TOKEN, before you can make REST requests.

Before you run the examples, you should have Plivo Running along with FreeSWITCH Running and a user 1000 logged in.

See `Plivo Documentation <http://www.plivo.org/docs/>`_ for more information.


Files
~~~~~

**plivohelper.py:** include this library in your code

**examples/example-call.py:** example usage of REST Call

**examples/example-bulkcalls.py:** example usage of REST Bulk Calls

**examples/example-transfercall.py:** example usage of REST Transfer Live Call

**examples/example-hangupcall.py:** example usage of REST Hangup Live Call

**examples/example-xml.py:** example usage of the RESTXML generator

**examples/example-utils.py:** example usage of utilities

**examples/example-responseserver.py:** example usage of live RESTXML (`Requires Flask <http://flask.pocoo.org/>`_)


Credits
-------

Plivo Python Helper Library is derived from `Twilio Python Helper <https://github.com/twilio/twilio-python>`_


License
-------

The Plivo Python Helper Library  is distributed under the MIT License
