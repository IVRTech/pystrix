(Application) Confbridge
========================

Confbridge is Asterisk's new conferencing subsystem, providing far greater functionality than
Meetme, with better performance and structural design. While technically a part of Asterisk's core,
it's specialised enough that pystrix treats it as a module.

Members
-------

All of the following objects should be accessed as part of the `ami.app_confbridge_events`
namespace, regardless of the modules in which they are defined.

Classes
+++++++

.. autoclass:: ami.app_confbridge_events.ConfbridgeEnd
    :members:
    
.. autoclass:: ami.app_confbridge_events.ConfbridgeJoin
    :members:

.. autoclass:: ami.app_confbridge_events.ConfbridgeLeave
    :members:
    
.. autoclass:: ami.app_confbridge_events.ConfbridgeList
    :members:
    
.. autoclass:: ami.app_confbridge_events.ConfbridgeListComplete
    :members:
    
.. autoclass:: ami.app_confbridge_events.ConfbridgeListRooms
    :members:
    
.. autoclass:: ami.app_confbridge_events.ConfbridgeListRoomsComplete
    :members:
    
.. autoclass:: ami.app_confbridge_events.ConfbridgeStart
    :members:
    
.. autoclass:: ami.app_confbridge_events.ConfbridgeTalking
    :members:
    
