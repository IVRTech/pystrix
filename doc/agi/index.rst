Asterisk Gateway Interface (AGI)
================================

The AGI interface consists of a number of action classes that are sent to Asterisk to effect actions
on active channels. Two different means of getting access to a channel are defined: AGI and FastAGI,
with the difference between them being that every AGI instance runs as a child process of Asterisk
(full Python interpreter and everything), while FastAGI runs over a TCP/IP socket, allowing for
faster startup times and lower overhead, with the cost of a little more development investment.

pystrix exposes the same feature-set and interaction model for both AGI and FastAGI, allowing any
of the actions defined in the following sections to be instantiated and passed (any number of times)
to :meth:`agi.AGI.execute`.

.. toctree::
    :maxdepth: 3
    
    core.rst

Members
-------

All of the following objects should be accessed as part of the `agi` namespace, regardless of the
modules in which they are defined.

Classes
+++++++

.. autoclass:: agi.AGI
    :members:
    :inherited-members:
    
.. autoclass:: agi.FastAGIServer
    :members:
    
    .. attribute:: timeout

        The number of seconds to wait for a request when using
        :meth:`handle_request`. Has no effect on
        :meth:`serve_forever`.

    .. method:: handle_request()

        Handles at most one request in a separate thread or times out and returns control silently.
        
    .. method:: serve_forever()

        Continues to serve requests as they are received, handling each in a new thread, until
        :meth:`shutdown` is called.
        
    .. method:: shutdown()
    
        Interrupts :meth:`serve_forever` gracefully.
        
Exceptions
++++++++++

.. autoexception:: agi.AGIException
    :show-inheritance:
    
    .. attribute:: items
    
        A dictionary containing any key-value items received from Asterisk to explain the exception.

.. autoexception:: agi.AGIError
    :show-inheritance:
    
.. autoexception:: agi.AGIUnknownError
    :show-inheritance:
    
.. autoexception:: agi.AGIAppError
    :show-inheritance:
    
.. autoexception:: agi.AGIHangup
    :show-inheritance:
    
.. autoexception:: agi.AGISIGPIPEHangup
    :show-inheritance:
    
.. autoexception:: agi.AGISIGHUPHangup
    :show-inheritance:
    
.. autoexception:: agi.AGIResultHangup
    :show-inheritance:
    
.. autoexception:: agi.AGIDeadChannelError
    :show-inheritance:
    
.. autoexception:: agi.AGIUsageError
    :show-inheritance:
    
.. autoexception:: agi.AGIInvalidCommandError
    :show-inheritance:
    
