(Application) Confbridge
========================

Confbridge is Asterisk's new conferencing subsystem, providing far greater functionality than
Meetme, with better performance and structural design. While technically a part of Asterisk's core,
it's specialised enough that pystrix treats it as a module.

Members
-------

All of the following objects should be accessed as part of the `ami.app_confbirdge` namespace,
regardless of the modules in which they are defined.

Actions
+++++++

.. autoclass:: ami.app_confbridge.ConfbridgeKick
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.app_confbridge.ConfbridgeList
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.app_confbridge.ConfbridgeListRooms
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.app_confbridge.ConfbridgeLock
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.app_confbridge.ConfbridgeUnlock
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.app_confbridge.ConfbridgeMoHOn
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.app_confbridge.ConfbridgeMoHOff
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.app_confbridge.ConfbridgeMute
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.app_confbridge.ConfbridgeUnmute
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.app_confbridge.ConfbridgePlayFile
    :show-inheritance:
    :members: __init__
    
.. autoclass:: ami.app_confbridge.ConfbridgeStartRecord
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.app_confbridge.ConfbridgeStopRecord
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.app_confbridge.ConfbridgeSetSingleVideoSrc
    :show-inheritance:
    :members: __init__

