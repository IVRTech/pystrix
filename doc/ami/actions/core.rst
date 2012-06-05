Core
====

Asterisk provides a rich collection of features by default, the standard set of which are described
here.

Members
-------

All of the following objects should be accessed as part of the `ami.core` namespace, regardless of
the modules in which they are defined.

Constants
+++++++++

.. data:: AUTHTYPE_MD5

    Uses MD5 authentication when logging into AMI
    
.. data:: EVENTMASK_ALL

    Turns on all events with the :class:`ami.core.Events` action

.. data:: EVENTMASK_NONE

    Turns off all events with the :class:`ami.core.Events` action
    
.. data:: EVENTMASK_CALL

    Turns on call events with the :class:`ami.core.Events` action
    
.. data:: EVENTMASK_LOG

    Turns on log events with the :class:`ami.core.Events` action
    
.. data:: EVENTMASK_SYSTEM

    Turns on system events with the :class:`ami.core.Events` action

.. data:: FORMAT_SLN

    Selects the `sln` audio format
    
.. data:: FORMAT_G723

    Selects the `g723` audio format
    
.. data:: FORMAT_G729

    Selects the `g729` audio format
    
.. data:: FORMAT_GSM

    Selects the `gsm` audio format
    
.. data:: FORMAT_ALAW

    Selects the `alaw` audio format
    
.. data:: FORMAT_ULAW

    Selects the `ulaw` audio format
    
.. data:: FORMAT_VOX

    Selects the `vox` audio format
    
.. data:: FORMAT_WAV

    Selects the `wav` audio format
    
.. data:: ORIGINATE_RESULT_REJECT

    Remote extension rejected (hung up) without answering
    
.. data:: ORIGINATE_RESULT_RING_LOCAL

    Local extension rang, but didn't answer
    
.. data:: ORIGINATE_RESULT_RING_REMOTE

    Remote extension rang, but didn't answer
    
.. data:: ORIGINATE_RESULT_ANSWERED

    Remote extension answered
    
.. data:: ORIGINATE_RESULT_BUSY

    Remote extension was busy
    
.. data:: ORIGINATE_RESULT_CONGESTION

    Remote extension was unreachable
    
.. data:: ORIGINATE_RESULT_INCOMPLETE

    Remote extension could not be identified

Classes
+++++++

.. autoclass:: ami.core.AbsoluteTimeout
    :members: __init__

.. autoclass:: ami.core.AGI
    :members: __init__

.. autoclass:: ami.core.Bridge
    :members: __init__

.. autoclass:: ami.core.Challenge
    :members: __init__

.. autoclass:: ami.core.ChangeMonitor
    :members: __init__

.. autoclass:: ami.core.Command
    :members: __init__
    
.. autoclass:: ami.core.CoreShowChannels
    :members: __init__

.. autoclass:: ami.core.CreateConfig
    :members: __init__

.. autoclass:: ami.core.DBDel
    :members: __init__

.. autoclass:: ami.core.DBDelTree
    :members: __init__

.. autoclass:: ami.core.DBGet
    :members: __init__

.. autoclass:: ami.core.DBPut
    :members: __init__

.. autoclass:: ami.core.Events
    :members: __init__

.. autoclass:: ami.core.ExtensionState
    :members: __init__

.. autoclass:: ami.core.GetConfig
    :members: __init__
    
    .. method:: get_lines()
        
        Provides a generator that yields every line in order.

.. autoclass:: ami.core.Getvar
    :members: __init__

.. autoclass:: ami.core.Hangup
    :members: __init__

.. autoclass:: ami.core.ListCommands
    :members: __init__

.. autoclass:: ami.core.ListCategories
    :members: __init__

.. autoclass:: ami.core.LocalOptimizeAway
    :members: __init__

.. autoclass:: ami.core.Login
    :members: __init__

.. autoclass:: ami.core.Logoff
    :members: __init__

.. autoclass:: ami.core.ModuleLoad
    :members: __init__

.. autoclass:: ami.core.Monitor
    :members: __init__

.. autoclass:: ami.core.MuteAudio
    :members: __init__

.. autoclass:: ami.core.Originate_Application
    :members: __init__

.. autoclass:: ami.core.Originate_Context
    :members: __init__

.. autoclass:: ami.core.Park
    :members: __init__

.. autoclass:: ami.core.ParkedCalls
    :members: __init__

.. autoclass:: ami.core.PauseMonitor
    :members: __init__

.. autoclass:: ami.core.Ping
    :members: __init__

.. autoclass:: ami.core.PlayDTMF
    :members: __init__

.. autoclass:: ami.core.QueueAdd
    :members: __init__

.. autoclass:: ami.core.QueueLog
    :members: __init__

.. autoclass:: ami.core.QueuePause
    :members: __init__

.. autoclass:: ami.core.QueuePenalty
    :members: __init__

.. autoclass:: ami.core.QueueReload
    :members: __init__

.. autoclass:: ami.core.QueueRemove
    :members: __init__

.. autoclass:: ami.core.QueueStatus
    :members: __init__

.. autoclass:: ami.core.Redirect
    :members: __init__

.. autoclass:: ami.core.Reload
    :members: __init__

.. autoclass:: ami.core.SendText
    :members: __init__

.. autoclass:: ami.core.SetCDRUserField
    :members: __init__

.. autoclass:: ami.core.Setvar
    :members: __init__

.. autoclass:: ami.core.SIPnotify
    :members: __init__

.. autoclass:: ami.core.SIPpeers
    :members: __init__

.. autoclass:: ami.core.SIPqualify
    :members: __init__

.. autoclass:: ami.core.SIPshowpeer
    :members: __init__

.. autoclass:: ami.core.SIPshowregistry
    :members: __init__

.. autoclass:: ami.core.Status
    :members: __init__

.. autoclass:: ami.core.StopMonitor
    :members: __init__

.. autoclass:: ami.core.UnpauseMonitor
    :members: __init__

.. autoclass:: ami.core.UpdateConfig
    :members: __init__

.. autoclass:: ami.core.UserEvent
    :members: __init__

.. autoclass:: ami.core.VoicemailUsersList
    :members: __init__

Exceptions
++++++++++

.. autoexception:: ami.core.ManagerAuthError
    :show-inheritance:
    
