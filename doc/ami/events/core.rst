asterisk "asyncagi"Core
====

Asterisk provides a rich assortment of information-carrying events by default, the standard set of
which are described here.

Members
-------

All of the following objects should be accessed as part of the `ami.core_events` namespace,
regardless of the modules in which they are defined.

Events
++++++

.. autoclass:: ami.core_events.AGIExec
    :show-inheritance:
    :members:

.. autoclass:: ami.core_events.AsyncAGI
    :show-inheritance:
    :members:

.. autoclass:: ami.core_events.ChannelUpdate
    :show-inheritance:
    :members:

.. autoclass:: ami.core_events.CoreShowChannel
    :show-inheritance:
    :members:
    
.. autoclass:: ami.core_events.CoreShowChannelsComplete
    :show-inheritance:
    :members:

.. autoclass:: ami.core_events.DBGetResponse
    :show-inheritance:
    :members:

.. autoclass:: ami.core_events.DTMF
    :show-inheritance:
    :members:
    
.. autoclass:: ami.core_events.FullyBooted
    :show-inheritance:
    :members:

.. autoclass:: ami.core_events.Hangup
    :show-inheritance:
    :members:

.. autoclass:: ami.core_events.HangupRequest
    :show-inheritance:
    :members:

.. autoclass:: ami.core_events.MonitorStart
    :show-inheritance:
    :members:
    
.. autoclass:: ami.core_events.MonitorStop
    :show-inheritance:
    :members:

.. autoclass:: ami.core_events.NewAccountCode
    :show-inheritance:
    :members:

.. autoclass:: ami.core_events.Newchannel
    :show-inheritance:
    :members:
    
.. autoclass:: ami.core_events.Newexten
    :show-inheritance:
    :members:
    
.. autoclass:: ami.core_events.Newstate
    :show-inheritance:
    :members:

.. autoclass:: ami.core_events.OriginateResponse
    :show-inheritance:
    :members:
    
.. autoclass:: ami.core_events.ParkedCall
    :show-inheritance:
    :members:

.. autoclass:: ami.core_events.ParkedCallsComplete
    :show-inheritance:
    :members:

.. autoclass:: ami.core_events.PeerEntry
    :show-inheritance:
    :members:

.. autoclass:: ami.core_events.PeerlistComplete
    :show-inheritance:
    :members:

.. autoclass:: ami.core_events.QueueEntry
    :show-inheritance:
    :members:

.. autoclass:: ami.core_events.QueueMember
    :show-inheritance:
    :members:

.. autoclass:: ami.core_events.QueueMemberAdded
    :show-inheritance:
    :members:

.. autoclass:: ami.core_events.QueueMemberPaused
    :show-inheritance:
    :members:

.. autoclass:: ami.core_events.QueueMemberRemoved
    :show-inheritance:
    :members:

.. autoclass:: ami.core_events.QueueParams
    :show-inheritance:
    :members:

.. autoclass:: ami.core_events.QueueStatusComplete
    :show-inheritance:
    :members:

.. autoclass:: ami.core_events.RegistryEntry
    :show-inheritance:
    :members:
    
.. autoclass:: ami.core_events.RegistratonsComplete
    :show-inheritance:
    :members:

.. autoclass:: ami.core_events.Reload
    :show-inheritance:
    :members:

.. autoclass:: ami.core_events.RTCPReceived
    :show-inheritance:
    :members:

.. autoclass:: ami.core_events.RTCPSent
    :show-inheritance:
    :members:

.. autoclass:: ami.core_events.Shutdown
    :show-inheritance:
    :members:

.. autoclass:: ami.core_events.SoftHangupRequest
    :show-inheritance:
    :members:

.. autoclass:: ami.core_events.Status
    :show-inheritance:
    :members:

.. autoclass:: ami.core_events.StatusComplete
    :show-inheritance:
    :members:

.. autoclass:: ami.core_events.UserEvent
    :show-inheritance:
    :members:

.. autoclass:: ami.core_events.VarSet
    :show-inheritance:
    :members:

.. autoclass:: ami.core_events.VoicemailUserEntry
    :show-inheritance:
    :members:

.. autoclass:: ami.core_events.VoicemailUserEntryComplete
    :show-inheritance:
    :members:

Aggregate Events
++++++++++++++++

.. autoclass:: ami.core_events.CoreShowChannels_Aggregate
    :show-inheritance:
    :members:
    
.. autoclass:: ami.core_events.ParkedCalls_Aggregate
    :show-inheritance:
    :members:
    
.. autoclass:: ami.core_events.QueueStatus_Aggregate
    :show-inheritance:
    :members:
    
.. autoclass:: ami.core_events.SIPpeers_Aggregate
    :show-inheritance:
    :members:
    
.. autoclass:: ami.core_events.SIPshowregistry_Aggregate
    :show-inheritance:
    :members:
    
.. autoclass:: ami.core_events.Status_Aggregate
    :show-inheritance:
    :members:
    
.. autoclass:: ami.core_events.VoicemailUsersList_Aggregate
    :show-inheritance:
    :members:
    
