Events
======

The AMI generates events in response to changes in its environment (unsolicited) or as a response to
certain request actions. All known events are described in this section. Their usage is consistently
a matter of registering a callback handler for an event with
:meth:`ami.Manager.register_callback` and then waiting for the event to occur.

.. toctree::

    core_events.rst
    dahdi_events.rst
    zaptel_events.rst
    app_confbridge_events.rst
    app_meetme_events.rst
    

