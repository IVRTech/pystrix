# pystrix

[![CI](https://github.com/IVRTech/pystrix/actions/workflows/ci.yml/badge.svg)](https://github.com/IVRTech/pystrix/actions/workflows/ci.yml)

**pystrix** is a versatile [Asterisk](https://www.asterisk.org/) interface package for AMI and (Fast)AGI needs. [Ivrnet, inc.](https://www.ivrnet.com/) published it as open source under the LGPLv3, and contributions from all users are welcome.

## Overview

pystrix runs on Python 3.9+. It targets Asterisk 1.10+ and provides a rich, easy-to-extend set of bindings for three Asterisk integration protocols:

- **AMI** (Asterisk Manager Interface) — a persistent TCP connection for controlling and monitoring the whole server. Originate calls, hang them up, read channel status, and react to live events.
- **AGI** (Asterisk Gateway Interface) — per-call scripting over stdin and stdout. Drive the dialplan of a single call: play audio, collect digits, set variables.
- **FastAGI** — the same call scripting as AGI, served from a long-running threaded TCP server instead of a process spawned per call.

The package is a toolkit, not a framework. You can drop it into a larger project without adopting an async framework such as Twisted.

This repository is version **1.2.0**. The canonical version lives in `pystrix/__init__.py`. New releases follow `<major>.<minor>.<patch>`, with a patch release cut for each bug fix.

## Installation

From PyPI:

```bash
pip install pystrix
```

From GitHub:

```bash
pip install git+https://github.com/IVRTech/pystrix.git#egg=pystrix
```

## Quick start

### AGI — script a single call

```python
#!/usr/bin/env python
import pystrix

if __name__ == '__main__':
    agi = pystrix.agi.AGI()

    agi.execute(pystrix.agi.core.Answer())  # Answer the call

    # Play a file; DTMF '1' or '2' interrupts playback
    response = agi.execute(
        pystrix.agi.core.StreamFile('demo-thanks', escape_digits=('1', '2'))
    )
    if response:  # Playback was interrupted
        (dtmf_character, offset) = response

    agi.execute(pystrix.agi.core.Hangup())  # Hang up
```

### FastAGI — serve many calls from one process

```python
import re
import pystrix

server = pystrix.agi.FastAGIServer()

def demo_handler(agi, args, kwargs, match, path):
    agi.execute(pystrix.agi.core.Answer())
    agi.execute(pystrix.agi.core.StreamFile('demo-thanks'))
    agi.execute(pystrix.agi.core.Hangup())

server.register_script_handler(re.compile('demo'), demo_handler)
server.register_script_handler(None, demo_handler)  # default handler
server.serve_forever()
```

The FastAGI server sizes its listen backlog from the system `SOMAXCONN` value, so it absorbs large bursts of simultaneous calls. It reads that value with `sysctl`, so the server currently runs on Linux and macOS only. AMI and AGI have no such restriction.

### AMI — control and monitor the server

```python
import pystrix

manager = pystrix.ami.Manager()
manager.connect('localhost')

# Authenticate with an MD5 challenge to avoid sending the password in plain text
challenge = manager.send_action(pystrix.ami.core.Challenge())
manager.send_action(pystrix.ami.core.Login(
    'username', 'password', challenge=challenge.result['Challenge'],
))

# React to events as Asterisk emits them
def on_hangup(event, manager):
    print('Channel hung up:', event.get('Channel'))

manager.register_callback(pystrix.ami.core_events.Hangup, on_hangup)
```

Full, commented examples for all three protocols live in `doc/examples/`.

## Documentation

Online documentation is available at <http://pystrix.readthedocs.io/>.

Inline documentation is complete and written in [reStructuredText](https://docutils.sourceforge.io/rst.html), so the source stays readable.

For an architecture overview and contributor guidance, see [AGENTS.md](AGENTS.md).

## Contributing

pystrix has no third-party runtime dependencies, so setup is short.

```bash
git clone https://github.com/IVRTech/pystrix.git
cd pystrix
python3 -m venv .venv && source .venv/bin/activate
pip install -e '.[test]'
```

The editable install (`-e`) means your local edits take effect without reinstalling.

A few things to know before you send a change:

- **Run the tests** with `pytest`. CI runs them across Python 3.9 through 3.13 on every pull request. There is no live-Asterisk integration test, so socket-level behavior is still worth checking against a real server (AMI on port 5038, FastAGI on port 4573).
- **Lint with ruff.** `ruff check .` must pass, and CI enforces it. Install the hooks to lint on each commit: `pip install pre-commit && pre-commit install`. Formatting is not enforced yet.
- **Target Python 3.9+.** The codebase is Python 3 only; the old Python 2 compatibility shims have been removed, so don't reintroduce them.
- **Build the docs** when you touch them: `pip install -r doc/requirements.txt`, then `cd doc && make html`.
- **Version bumps** go in `pystrix/__init__.py`. `setup.py` reads `VERSION` from there.
- **Keep docstrings complete** and written in reStructuredText. The reference docs are generated from them.

## License

pystrix is licensed under the GNU Lesser General Public License v3 or later (`COPYING.LESSER`). The LGPL extends the GNU General Public License v3 (`COPYING`), so both license texts ship with the project.

## Credits

[Neil Tallim](http://uguu.ca/) created pystrix, and [Ivrnet, inc.](https://www.ivrnet.com/) funded its initial development. For the full list of contributors, see the [contributors page](https://github.com/IVRTech/pystrix/graphs/contributors) or the commit history.
