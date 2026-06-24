# AGENTS.md

Guidance for AI agents working in the pystrix repository. Read this before making changes.

## What pystrix is

pystrix is a pure-Python client library for the Asterisk telephony server. It is a toolkit, not a framework, with no third-party runtime dependencies. It targets Python 3.9+ and Asterisk 1.10+.

It covers three Asterisk protocols:

- **AMI** (Asterisk Manager Interface): a persistent TCP socket on port 5038. You send actions and receive both request-responses and unsolicited server events on the same stream. Event-driven and concurrent.
- **AGI** (Asterisk Gateway Interface): per-call scripting over stdin and stdout. Blocking and synchronous.
- **FastAGI**: AGI served from a long-running threaded TCP server on port 4573.

The core split to keep in mind: AGI is one blocking call per script; AMI is one socket multiplexing many concurrent request-responses and events, which is why the AMI code is built on threads and queues.

## Repository layout

```
pystrix/
├── __init__.py             VERSION lives here (currently 1.2.0)
├── ami/
│   ├── ami.py              Manager class + threading/socket core (the heart of AMI)
│   ├── core.py             ~60 Action classes (Login, Originate, Hangup, Ping, ...)
│   ├── core_events.py      ~50 Event classes + Aggregate classes
│   ├── dahdi.py            DAHDI hardware actions
│   ├── dahdi_events.py     DAHDI events
│   ├── app_confbridge.py   ConfBridge app actions
│   ├── app_confbridge_events.py
│   ├── app_meetme.py       MeetMe app actions
│   ├── app_meetme_events.py
│   └── generic_transforms.py   type coercion + py2/3 bytes<->str helpers
└── agi/
    ├── agi_core.py         _AGI base: command framing, response parsing, exceptions
    ├── agi.py              AGI class (stdin/stdout + SIGHUP handling)
    ├── fastagi.py          FastAGIServer (threaded TCP) + FastAGI handler
    └── core.py             ~45 Action classes (Answer, StreamFile, SayNumber, ...)

doc/                        Sphinx/reStructuredText docs + runnable examples in doc/examples/
setup.py                    Packaging; reads README.md for long_description
build-release.py            Release helper
```

## Architecture notes

### AMI flow (`pystrix/ami/ami.py`)

`Manager` is the entry point. On `connect()` it starts two daemon threads:

1. `_MessageReader` (`ami.py:956`) reads framed messages off the socket and sorts each one. A message with an `Event:` header goes to the event queue. A message with an `ActionID` is a response to a request you sent, stored by ID. Anything else is an orphaned response.
2. `_event_dispatcher` (`ami.py:170`) pulls from those queues and fires registered callbacks.

Three patterns build on the request/response basics:

- **ActionID matching**: every request gets a host-qualified random ID (`_get_host_action_id`, `ami.py:315`) so responses pair with requests even across multiple AMI connections.
- **Synchronous requests**: some actions trigger a burst of events ending in a "complete" event. A synchronous `_Request` declares its unique, list, and finaliser event classes. `send_action` blocks until all finalisers arrive (`_add_outstanding_request`, `ami.py:578`).
- **Aggregates**: the async equivalent. `_Aggregate` classes in `core_events.py` gather a multi-event reply into one synthesized object with count validation.

### The class-mutation trick

Each raw message parses into a generic `_Message`. The reader then looks up the event name in `_EVENT_REGISTRY` and rebinds the object's `__class__` in place to the specific event subclass (`ami.py:1031`). This turns a socket string into a typed object whose `process()` method knows how to coerce its own fields, with no re-parsing. The registry is built in `pystrix/ami/__init__.py:55-63` by reflecting over the `*_events` modules at import time.

### AGI flow (`pystrix/agi/agi_core.py`)

`_AGI` is protocol-agnostic. It reads Asterisk's environment variables on startup, then `execute()` sends a command line and parses the numeric reply: 200 is success, 510 invalid command, 511 dead channel, 520 usage error. Hangups raise `AGIResultHangup` or `AGISIGHUPHangup`.

`AGI` (`agi.py`) wires I/O to stdin/stdout and traps SIGHUP. `FastAGIServer` (`fastagi.py`) is a `ThreadingMixIn` TCP server that matches each request path against registered regexes to pick a handler.

### FastAGI scaling

This fork's main feature is FastAGI throughput. `_ThreadedTCPServer` (`fastagi.py:52`) sizes `request_queue_size` from the system `SOMAXCONN` (read via `sysctl` on Linux and Darwin) instead of the small Python default, and sets `allow_reuse_address`. The listen backlog directly bounds how many simultaneous calls the server can accept under a surge.

## Conventions for extending the library

- **Add an AMI action**: subclass `_Request` in the matching `ami/` module. Override `process_response()` for custom result handling.
- **Add an AMI event**: subclass `_Event` in a `*_events` module. The registry auto-discovers it at import, so no manual registration is needed. Match the class name to Asterisk's event name.
- **Add an AGI command**: subclass `_Action` in `agi/core.py`. Override `process_response()` to parse the reply.
- The `app_*` and `dahdi` modules are this same pattern applied to Asterisk add-on modules. Follow their structure for new modules.

## Python version and Python 3 boundaries

The project targets Python 3.9+ and the source is Python 3 only. The earlier Python 2 compatibility shims were removed (#47), so don't reintroduce patterns like `basestring` checks or `import Queue` fallbacks.

Two bytes/string details at the I/O boundary are not Python 2 baggage and must stay:

- Explicit bytes/string conversion via `string_to_bytes` and `bytes_to_string`.
- The AMI socket opens in binary mode (`makefile(mode="rb")` in `ami.py`) on purpose. Text mode silently drops carriage returns and breaks Asterisk's CRLF message framing. Do not change this.

## Working in this repo

- There is no test suite and no linter config. Verify changes against the runnable examples in `doc/examples/` and, where possible, a live Asterisk server.
- `VERSION` in `pystrix/__init__.py` is the single source of truth. `setup.py` imports it. Bump it for releases.
- `setup.py` reads `README.md`. Keep that filename in sync if the README is ever renamed again.
- Docs are Sphinx reStructuredText under `doc/`. Update the relevant `.rst` when adding public actions or events.
- Keep inline docstrings complete and in reStructuredText. The project relies on them for its documentation.
