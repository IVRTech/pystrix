Events
======

The AMI generates events in response to changes in its environment (unsolicited) or as a response to
certain request actions. All known events are described in this section. Their usage is consistently
a matter of registering a callback handler for an event with
:meth:`ami.Manager.register_callback` and then waiting for the event to occur.

.. toctree::

    core.rst
    dahdi.rst
    zaptel.rst
    app_confbridge.rst
    app_meetme.rst
    

