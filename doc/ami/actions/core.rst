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

Actions
+++++++

.. autoclass:: ami.core.AbsoluteTimeout
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.AGI
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.Bridge
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.Challenge
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.ChangeMonitor
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.Command
    :show-inheritance:
    :members: __init__
    
.. autoclass:: ami.core.CoreShowChannels
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.CreateConfig
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.DBDel
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.DBDelTree
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.DBGet
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.DBPut
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.Events
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.ExtensionState
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.GetConfig
    :show-inheritance:
    :members: __init__
    
    .. method:: get_lines()
        
        Provides a generator that yields every line in order.

.. autoclass:: ami.core.Getvar
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.Hangup
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.ListCommands
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.ListCategories
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.LocalOptimizeAway
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.Login
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.Logoff
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.ModuleLoad
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.Monitor
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.MuteAudio
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.Originate_Application
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.Originate_Context
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.Park
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.ParkedCalls
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.PauseMonitor
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.Ping
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.PlayDTMF
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.QueueAdd
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.QueueLog
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.QueuePause
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.QueuePenalty
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.QueueReload
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.QueueRemove
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.QueueStatus
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.Redirect
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.Reload
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.SendText
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.SetCDRUserField
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.Setvar
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.SIPnotify
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.SIPpeers
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.SIPqualify
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.SIPshowpeer
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.SIPshowregistry
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.Status
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.StopMonitor
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.UnpauseMonitor
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.UpdateConfig
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.UserEvent
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.core.VoicemailUsersList
    :show-inheritance:
    :members: __init__

Exceptions
++++++++++

.. autoexception:: ami.core.ManagerAuthError
    :show-inheritance:
    
