Asterisk Management Interface (AMI)
===================================

The AMI interface consists primarily of a number of action classes that are sent to Asterisk to
ellicit responses. Additionally, a number of event classes are defined to provide convenience
processing on the various messages Asterisk generates.

All of these concepts are bound together by a Manager class, which provides facilities for sending
actions and serving callback handlers when events are received.

.. toctree::

    core.rst
    dahdi.rst
    zaptel.rst
