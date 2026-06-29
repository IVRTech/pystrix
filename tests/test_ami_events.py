"""
Tests for the AMI event-registration API and the built-in event registry.

Covers:
- register_event_class / unregister_event_class public API
- registry-build quality (no junk, aggregates preserved)
- new built-in classes (DialBegin, DialEnd, Bridge*)
"""

import inspect

import pytest

import pystrix.ami.ami as ami
import pystrix.ami.core_events as core_events
from pystrix.ami.ami import (
    _EVENT_REGISTRY,
    _EVENT_REGISTRY_REV,
    _Aggregate,
    _Event,
    register_event_class,
    unregister_event_class,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class _MyEvent(_Event):
    """A custom event class for testing."""


class _MyEventAlt(_Event):
    """A second custom event class for testing an explicit name override."""


class _NotAnEvent:
    """A class that is not a subclass of _Event."""


def _cleanup(*classes_or_names):
    """Remove test registrations so tests don't bleed into each other."""
    for c in classes_or_names:
        unregister_event_class(c)


# ---------------------------------------------------------------------------
# register_event_class
# ---------------------------------------------------------------------------


class TestRegisterEventClass:
    def teardown_method(self):
        _cleanup(_MyEvent, _MyEventAlt, "CustomWireName", "AltName")

    def test_registers_by_class_name_by_default(self):
        register_event_class(_MyEvent)
        assert _EVENT_REGISTRY.get("_MyEvent") is _MyEvent
        assert _EVENT_REGISTRY_REV.get(_MyEvent) == "_MyEvent"

    def test_explicit_name_overrides_class_name(self):
        register_event_class(_MyEvent, name="CustomWireName")
        assert _EVENT_REGISTRY.get("CustomWireName") is _MyEvent
        assert _EVENT_REGISTRY_REV.get(_MyEvent) == "CustomWireName"
        assert "_MyEvent" not in _EVENT_REGISTRY

    def test_non_event_subclass_raises_value_error(self):
        with pytest.raises(ValueError):
            register_event_class(_NotAnEvent)

    def test_non_class_raises_value_error(self):
        with pytest.raises(ValueError):
            register_event_class("not_a_class")

    def test_overwrite_replaces_previous_registration(self):
        register_event_class(_MyEvent)
        register_event_class(_MyEventAlt, name="_MyEvent")
        assert _EVENT_REGISTRY.get("_MyEvent") is _MyEventAlt
        assert _EVENT_REGISTRY_REV.get(_MyEventAlt) == "_MyEvent"
        assert _MyEvent not in _EVENT_REGISTRY_REV

    def test_re_register_same_class_under_new_name_evicts_old_forward_entry(self):
        register_event_class(_MyEvent)
        register_event_class(_MyEvent, name="AltName")
        assert "_MyEvent" not in _EVENT_REGISTRY
        assert _EVENT_REGISTRY.get("AltName") is _MyEvent
        assert _EVENT_REGISTRY_REV.get(_MyEvent) == "AltName"

    def test_overwrite_different_class_evicts_old_reverse_entry(self):
        register_event_class(_MyEvent, name="SharedName")
        register_event_class(_MyEventAlt, name="SharedName")
        assert _EVENT_REGISTRY.get("SharedName") is _MyEventAlt
        assert _MyEvent not in _EVENT_REGISTRY_REV

    def _make_partial_manager(self):
        """Return a Manager with only the attributes needed by _compile_callback_definition."""
        import threading

        manager = ami.Manager.__new__(ami.Manager)
        manager._event_callbacks = []
        manager._event_callbacks_lock = threading.Lock()
        manager._connection_lock = threading.Lock()
        return manager

    def test_registered_class_resolves_via_compile_callback_definition(self):
        register_event_class(_MyEvent)
        manager = self._make_partial_manager()

        # _compile_callback_definition should resolve to a REFERENCE callback now
        from pystrix.ami.ami import _CALLBACK_TYPE_REFERENCE

        result = manager._compile_callback_definition(_MyEvent, lambda e, m: None)
        assert result[0] == _CALLBACK_TYPE_REFERENCE
        assert result[1] == "_MyEvent"

    def test_unregistered_class_still_raises_in_callback(self):
        # Without registration, passing a custom class should raise ValueError
        manager = self._make_partial_manager()
        with pytest.raises(ValueError):
            manager._compile_callback_definition(_MyEvent, lambda e, m: None)


# ---------------------------------------------------------------------------
# unregister_event_class
# ---------------------------------------------------------------------------


class TestUnregisterEventClass:
    def setup_method(self):
        register_event_class(_MyEvent)

    def teardown_method(self):
        _cleanup(_MyEvent)

    def test_unregister_by_class_object(self):
        result = unregister_event_class(_MyEvent)
        assert result is True
        assert "_MyEvent" not in _EVENT_REGISTRY
        assert _MyEvent not in _EVENT_REGISTRY_REV

    def test_unregister_by_string_name(self):
        result = unregister_event_class("_MyEvent")
        assert result is True
        assert "_MyEvent" not in _EVENT_REGISTRY
        assert _MyEvent not in _EVENT_REGISTRY_REV

    def test_unregister_unknown_returns_false(self):
        assert unregister_event_class("DoesNotExist") is False
        assert unregister_event_class(_MyEventAlt) is False

    def test_unregister_is_symmetric(self):
        unregister_event_class(_MyEvent)
        # Re-registration should work cleanly
        register_event_class(_MyEvent)
        assert _EVENT_REGISTRY.get("_MyEvent") is _MyEvent


# ---------------------------------------------------------------------------
# Registry build quality
# ---------------------------------------------------------------------------


class TestRegistryContents:
    def test_no_module_imports_in_registry(self):
        """re and generic_transforms must not appear."""
        assert "re" not in _EVENT_REGISTRY
        assert "generic_transforms" not in _EVENT_REGISTRY

    def test_all_values_are_classes(self):
        for name, obj in _EVENT_REGISTRY.items():
            assert inspect.isclass(obj), f"{name!r} maps to non-class {obj!r}"

    def test_all_event_classes_are_message_template_subclasses(self):
        from pystrix.ami.ami import _MessageTemplate

        for name, obj in _EVENT_REGISTRY.items():
            assert issubclass(obj, _MessageTemplate), (
                f"{name!r} ({obj!r}) is not a _MessageTemplate subclass"
            )

    def test_aggregates_are_preserved(self):
        """_Aggregate subclasses must stay in the registry for synchronous actions."""
        agg_names = [n for n, c in _EVENT_REGISTRY.items() if issubclass(c, _Aggregate)]
        assert len(agg_names) >= 10, f"Expected at least 10 aggregates, got {agg_names}"

    def test_forward_and_reverse_maps_are_consistent(self):
        for name, cls in _EVENT_REGISTRY.items():
            rev = _EVENT_REGISTRY_REV.get(cls)
            # A class may be keyed under multiple names (forward only); reverse
            # stores the canonical name, which is the last one written.
            # We just check it round-trips through the reverse direction.
            assert rev is not None, f"No reverse entry for {name!r} -> {cls!r}"
            assert _EVENT_REGISTRY.get(rev) is cls, (
                f"Reverse map for {cls!r} points to {rev!r} but forward map disagrees"
            )

    def test_known_builtin_events_present(self):
        for name in ("Hangup", "FullyBooted", "Newexten", "AGIExec", "Shutdown"):
            assert name in _EVENT_REGISTRY, f"Expected built-in event {name!r} missing"


# ---------------------------------------------------------------------------
# New built-in event classes
# ---------------------------------------------------------------------------


class TestNewBuiltinEvents:
    @pytest.mark.parametrize(
        "name",
        [
            "BridgeCreate",
            "BridgeDestroy",
            "BridgeEnter",
            "BridgeLeave",
            "DialBegin",
            "DialEnd",
            "Hold",
            "MusicOnHoldStart",
            "MusicOnHoldStop",
            "NewCallerid",
            "NewConnectedLine",
            "Unhold",
        ],
    )
    def test_event_class_exists_in_core_events(self, name):
        assert hasattr(core_events, name), f"core_events.{name} not found"
        cls = getattr(core_events, name)
        assert inspect.isclass(cls)
        assert issubclass(cls, _Event)

    @pytest.mark.parametrize(
        "name",
        [
            "BridgeCreate",
            "BridgeDestroy",
            "BridgeEnter",
            "BridgeLeave",
            "DialBegin",
            "DialEnd",
            "Hold",
            "MusicOnHoldStart",
            "MusicOnHoldStop",
            "NewCallerid",
            "NewConnectedLine",
            "Unhold",
        ],
    )
    def test_event_class_is_in_registry(self, name):
        assert name in _EVENT_REGISTRY, f"{name!r} not found in _EVENT_REGISTRY"
        assert _EVENT_REGISTRY[name] is getattr(core_events, name)

    def test_newexten_present_not_newexten_alias(self):
        """Wire name is Newexten (Asterisk 13 manager_channels.c:616); NewExten is not added."""
        assert "Newexten" in _EVENT_REGISTRY
        assert "NewExten" not in _EVENT_REGISTRY

    @pytest.mark.parametrize(
        "name", ["BridgeCreate", "BridgeDestroy", "BridgeEnter", "BridgeLeave"]
    )
    def test_bridgenumchannels_coerced_to_int(self, name):
        cls = getattr(core_events, name)
        event = cls([f"Event: {name}\r\n", "BridgeNumChannels: 2\r\n"])
        headers, _ = event.process()
        assert headers["BridgeNumChannels"] == 2
        assert isinstance(headers["BridgeNumChannels"], int)

    def test_bridgenumchannels_non_numeric_becomes_none(self):
        event = core_events.BridgeEnter(
            ["Event: BridgeEnter\r\n", "BridgeNumChannels: abc\r\n"]
        )
        headers, _ = event.process()
        assert headers["BridgeNumChannels"] is None

    def test_bridgenumchannels_missing_becomes_none(self):
        event = core_events.BridgeCreate(["Event: BridgeCreate\r\n"])
        headers, _ = event.process()
        assert "BridgeNumChannels" in headers
        assert headers["BridgeNumChannels"] is None
