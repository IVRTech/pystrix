(Application) Confbridge
========================

Confbridge is Asterisk's new conferencing subsystem, providing far greater functionality than
Meetme, with better performance and structural design. While technically a part of Asterisk's core,
it's specialised enough that pystrix treats it as a module.

Members
-------

All of the following objects should be accessed as part of the `ami.app_confbirdge` namespace,
regardless of the modules in which they are defined.

Classes
+++++++

.. autoclass:: ami.app_confbridge.ConfbridgeKick
    :members: __init__

.. autoclass:: ami.app_confbridge.ConfbridgeList
    :members: __init__

.. autoclass:: ami.app_confbridge.ConfbridgeListRooms
    :members: __init__

.. autoclass:: ami.app_confbridge.ConfbridgeLock
    :members: __init__

.. autoclass:: ami.app_confbridge.ConfbridgeUnlock
    :members: __init__

.. autoclass:: ami.app_confbridge.ConfbridgeMoHOn
    :members: __init__

.. autoclass:: ami.app_confbridge.ConfbridgeMoHOff
    :members: __init__

.. autoclass:: ami.app_confbridge.ConfbridgeMute
    :members: __init__

.. autoclass:: ami.app_confbridge.ConfbridgeUnmute
    :members: __init__

.. autoclass:: ami.app_confbridge.ConfbridgePlayFile
    :members: __init__
    
.. autoclass:: ami.app_confbridge.ConfbridgeStartRecord
    :members: __init__

.. autoclass:: ami.app_confbridge.ConfbridgeStopRecord
    :members: __init__

.. autoclass:: ami.app_confbridge.ConfbridgeSetSingleVideoSrc
    :members: __init__

