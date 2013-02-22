(Application) Meetme
====================

Meetme is Asterisk's long-standing, now-being-phased-out conferencing subsystem. While technically a
part of Asterisk's core, it's specialised enough that pystrix treats it as a module.

Members
-------

All of the following objects should be accessed as part of the `ami.app_meetme_events` namespace,
regardless of the modules in which they are defined.

Events
++++++

.. autoclass:: ami.app_meetme_events.MeetmeJoin
    :show-inheritance:
    :members:

.. autoclass:: ami.app_meetme_events.MeetmeList
    :show-inheritance:
    :members:

.. autoclass:: ami.app_meetme_events.MeetmeListRooms
    :show-inheritance:
    :members:

.. autoclass:: ami.app_meetme_events.MeetmeMute
    :show-inheritance:
    :members:    

Aggregate Events
++++++++++++++++

.. autoclass:: ami.app_meetme_events.MeetmeList_Aggregate
    :show-inheritance:
    :members:
    
.. autoclass:: ami.app_meetme_events.MeetmeListRooms_Aggregate
    :show-inheritance:
    :members:
    
