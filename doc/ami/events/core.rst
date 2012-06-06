Core
====

Asterisk provides a rich assortment of information-carrying events by default, the standard set of
which are described here.

Members
-------

All of the following objects should be accessed as part of the `ami.core_events` namespace,
regardless of the modules in which they are defined.

Classes
+++++++

.. autoclass:: ami.core_events.AGIExec
    :members:

.. autoclass:: ami.core_events.ChannelUpdate
    :members:

.. autoclass:: ami.core_events.CoreShowChannel
    :members:
    
.. autoclass:: ami.core_events.CoreShowChannelsComplete
    :members:

.. autoclass:: ami.core_events.DBGetResponse
    :members:

.. autoclass:: ami.core_events.DTMF
    :members:
    
.. autoclass:: ami.core_events.FullyBooted
    :members:

.. autoclass:: ami.core_events.Hangup
    :members:

.. autoclass:: ami.core_events.HangupRequest
    :members:

.. autoclass:: ami.core_events.MonitorStart
    :members:
    
.. autoclass:: ami.core_events.MonitorStop
    :members:

.. autoclass:: ami.core_events.NewAccountCode
    :members:

.. autoclass:: ami.core_events.Newchannel
    :members:
    
.. autoclass:: ami.core_events.Newexten
    :members:
    
.. autoclass:: ami.core_events.Newstate
    :members:

.. autoclass:: ami.core_events.OriginateResponse
    :members:
    
.. autoclass:: ami.core_events.ParkedCall
    :members:

.. autoclass:: ami.core_events.ParkedCallsComplete
    :members:

.. autoclass:: ami.core_events.PeerEntry
    :members:

.. autoclass:: ami.core_events.PeerlistComplete
    :members:

.. autoclass:: ami.core_events.QueueEntry
    :members:

.. autoclass:: ami.core_events.QueueMember
    :members:

.. autoclass:: ami.core_events.QueueMemberAdded
    :members:

.. autoclass:: ami.core_events.QueueMemberPaused
    :members:

.. autoclass:: ami.core_events.QueueMemberRemoved
    :members:

.. autoclass:: ami.core_events.QueueParams
    :members:

.. autoclass:: ami.core_events.QueueStatusComplete
    :members:

.. autoclass:: ami.core_events.Reload
    :members:

.. autoclass:: ami.core_events.RTCPReceived
    :members:

.. autoclass:: ami.core_events.RTCPSent
    :members:

.. autoclass:: ami.core_events.Shutdown
    :members:

.. autoclass:: ami.core_events.SoftHangupRequest
    :members:

.. autoclass:: ami.core_events.Status
    :members:

.. autoclass:: ami.core_events.StatusComplete
    :members:

.. autoclass:: ami.core_events.UserEvent
    :members:

.. autoclass:: ami.core_events.VarSet
    :members:

