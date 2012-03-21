Core
====

By default, Asterisk exposes a number of ways to interact with a channel, all of which are described
below.

Members
-------

All of the following objects should be accessed as part of the `agi.core` namespace, regardless of
the modules in which they are defined.

Constants
+++++++++

.. data:: CHANNEL_DOWN_AVAILABLE

    Channel is down and available
    
.. data:: CHANNEL_DOWN_RESERVED
    
    Channel is down and reserved

.. data:: CHANNEL_OFFHOOK

    Channel is off-hook
    
.. data:: CHANNEL_DIALED

    A destination address has been specified

.. data:: CHANNEL_ALERTING

    The channel is locally ringing
    
.. data:: CHANNEL_REMOTE_ALERTING

    The channel is remotely ringing

.. data:: CHANNEL_UP

    The channel is connected
    
.. data:: CHANNEL_BUSY

    The channel is in a busy, non-conductive state

.. data:: FORMAT_SLN
    :noindex:

    Selects the `sln` audio format
    
.. data:: FORMAT_G723
    :noindex:

    Selects the `g723` audio format
    
.. data:: FORMAT_G729
    :noindex:

    Selects the `g729` audio format
    
.. data:: FORMAT_GSM
    :noindex:

    Selects the `gsm` audio format
    
.. data:: FORMAT_ALAW
    :noindex:

    Selects the `alaw` audio format
    
.. data:: FORMAT_ULAW
    :noindex:

    Selects the `ulaw` audio format
    
.. data:: FORMAT_VOX
    :noindex:

    Selects the `vox` audio format
    
.. data:: FORMAT_WAV
    :noindex:

    Selects the `wav` audio format

.. data:: LOG_DEBUG

    The Asterisk logging level equivalent to 'debug'
    
.. data:: LOG_INFO

    The Asterisk logging level equivalent to 'info'
    
.. data:: LOG_WARN

    The Asterisk logging level equivalent to 'warn'
    
.. data:: LOG_ERROR

    The Asterisk logging level equivalent to 'error'
    
.. data:: LOG_CRITICAL

    The Asterisk logging level equivalent to 'critical'
    
.. data:: TDD_ON

    Sets TDD to on
    
.. data:: TDD_OFF

    Sets TDD to off

.. data:: TDD_MATE

    Sets TDD to mate

Classes
+++++++

.. autoclass:: agi.core.Answer

.. autoclass:: agi.core.ChannelStatus

.. autoclass:: agi.core.ControlStreamFile

.. autoclass:: agi.core.DatabaseDel

.. autoclass:: agi.core.DatabaseDeltree

.. autoclass:: agi.core.DatabaseGet

.. autoclass:: agi.core.DatabasePut

.. autoclass:: agi.core.Exec

.. autoclass:: agi.core.GetData

.. autoclass:: agi.core.GetFullVariable

.. autoclass:: agi.core.GetOption

.. autoclass:: agi.core.GetVariable

.. autoclass:: agi.core.Hangup

.. autoclass:: agi.core.Noop

.. autoclass:: agi.core.ReceiveChar

.. autoclass:: agi.core.ReceiveText

.. autoclass:: agi.core.RecordFile

.. autoclass:: agi.core.SayAlpha

.. autoclass:: agi.core.SayDate

.. autoclass:: agi.core.SayDatetime

.. autoclass:: agi.core.SayDigits

.. autoclass:: agi.core.SayNumber

.. autoclass:: agi.core.SayPhonetic

.. autoclass:: agi.core.SayTime

.. autoclass:: agi.core.SendImage

.. autoclass:: agi.core.SendText

.. autoclass:: agi.core.SetAutohangup

.. autoclass:: agi.core.SetCallerid

.. autoclass:: agi.core.SetContext

.. autoclass:: agi.core.SetExtension

.. autoclass:: agi.core.SetMusic

.. autoclass:: agi.core.SetPriority

.. autoclass:: agi.core.SetVariable

.. autoclass:: agi.core.StreamFile

.. autoclass:: agi.core.TDDMode

.. autoclass:: agi.core.Verbose

.. autoclass:: agi.core.WaitForDigit

Exceptions
++++++++++

.. autoexception:: agi.core.AGIDBError
    :show-inheritance:
    
