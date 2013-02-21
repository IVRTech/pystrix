(Application) Meetme
====================

Meetme is Asterisk's long-standing, now-being-phased-out conferencing subsystem. While technically a
part of Asterisk's core, it's specialised enough that pystrix treats it as a module.

Members
-------

All of the following objects should be accessed as part of the `ami.app_meetme` namespace,
regardless of the modules in which they are defined.

Actions
+++++++

.. autoclass:: ami.app_meetme.MeetmeList
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.app_meetme.MeetmeMute
    :show-inheritance:
    :members: __init__

.. autoclass:: ami.app_meetme.MeetmeUnmute
    :show-inheritance:
    :members: __init__

