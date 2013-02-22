(Application) Confbridge
========================

Confbridge is Asterisk's new conferencing subsystem, providing far greater functionality than
Meetme, with better performance and structural design. While technically a part of Asterisk's core,
it's specialised enough that pystrix treats it as a module.

Members
-------

All of the following objects should be accessed as part of the `ami.app_confbridge_events`
namespace, regardless of the modules in which they are defined.

Events
++++++

.. autoclass:: ami.app_confbridge_events.ConfbridgeEnd
    :show-inheritance:
    :members:
    
.. autoclass:: ami.app_confbridge_events.ConfbridgeJoin
    :show-inheritance:
    :members:

.. autoclass:: ami.app_confbridge_events.ConfbridgeLeave
    :show-inheritance:
    :members:
    
.. autoclass:: ami.app_confbridge_events.ConfbridgeList
    :show-inheritance:
    :members:
    
.. autoclass:: ami.app_confbridge_events.ConfbridgeListComplete
    :show-inheritance:
    :members:
    
.. autoclass:: ami.app_confbridge_events.ConfbridgeListRooms
    :show-inheritance:
    :members:
    
.. autoclass:: ami.app_confbridge_events.ConfbridgeListRoomsComplete
    :show-inheritance:
    :members:
    
.. autoclass:: ami.app_confbridge_events.ConfbridgeStart
    :show-inheritance:
    :members:
    
.. autoclass:: ami.app_confbridge_events.ConfbridgeTalking
    :show-inheritance:
    :members:
    
Aggregate Events
++++++++++++++++

.. autoclass:: ami.app_confbridge_events.ConfbridgeList_Aggregate
    :show-inheritance:
    :members:
    
.. autoclass:: ami.app_confbridge_events.ConfbridgeListRooms_Aggregate
    :show-inheritance:
    :members:
    
