Asterisk Management Interface (AMI)
===================================

The AMI interface consists primarily of a number of action classes that are sent to Asterisk to
ellicit responses. Additionally, a number of event classes are defined to provide convenience
processing on the various messages Asterisk generates.

.. toctree::
    :maxdepth: 2
    
    actions/index.rst
    events/index.rst
    
All of these concepts are bound together by the :class:`ami.Manager` class, which provides
facilities for sending actions and serving callback handlers when events are received.

Members
-------

All of the following objects should be accessed as part of the `ami` namespace, regardless of the
modules in which they are defined.

Constants
+++++++++

Aside, perhaps, from the "GENERIC" values, to be matched against :attr:`ami.ami._Message.name` responses,
these constants are largely unnecessary outside of internal module usage, but they're exposed for
convenience's sake.

.. data:: RESPONSE_GENERIC

    A header-value provided as a surrogate for unidentifiable responses
    
.. data:: EVENT_GENERIC

    A header-value provided as a surrogate for unidentifiable unsolicited events

.. data:: KEY_ACTION

    The header key used to identify an action being requested of Asterisk
    
.. data:: KEY_ACTIONID

    The header key used to hold the ActionID of a request, for matching with responses
    
.. data:: KEY_EVENT

    The header key used to hold the event-name of a response
    
.. data:: KEY_RESPONSE

    The header key used to hold the event-name of a request

Classes
+++++++

.. autoclass:: ami.Manager
    :members:
    
Internal classes
~~~~~~~~~~~~~~~~

The following classes are not meant to be worked with directly, but are important for other parts of
the system, with members that are worth knowing about.

.. autoclass:: ami.ami._Message
    :members:
    
    .. attribute:: data
    
        A series of lines containing the message's payload from Asterisk
        
    .. attribute:: headers
    
        A reference to a dictionary containing all headers associated with this message. Simply
        treating the message itself as a dictionary for headers is preferred, however; the two
        methods are equivalent.
        
    .. attribute:: raw
    
        The raw response from Asterisk as a series of lines, provided for applications that need
        access to the original data.
    
.. autoclass:: ami.ami._Request
    
    .. attribute:: timeout
    
        The number of seconds to wait before considering this request timed out, defaulting to `5`;
        may be a float.
        
        Indefinite waiting is not supported, but arbitrarily large values may be provided.
        
        A request that has timed out may still be serviced by Asterisk, with the notification being
        treated as an orphaned event.
        
        Changing the timeout value of the request object has no effect on any previously-sent
        instances of the request object, since the value is copied at dispatch-time.
        
Exceptions
++++++++++

.. autoexception:: ami.Error
    :show-inheritance:

.. autoexception:: ami.ManagerError
    :show-inheritance:

.. autoexception:: ami.ManagerSocketError
    :show-inheritance:

