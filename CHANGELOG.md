# Changelog

All notable changes to pystrix are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project aims
to follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- `Manager.monitor_connection` no longer crashes its monitoring thread when the connection drops. Pinging a downed connection raised `ManagerSocketError` (broken socket) or `ManagerError` (the liveness check inside `send_action` failing when the connection dropped just after the loop's own check) inside the thread, which dumped a traceback to stderr and killed the monitor. The monitor now catches both and stops cleanly, logging the reason at debug level when a logger is set. The method also returns the monitoring thread so callers can join it (#3).
- `Manager.send_action` no longer raises a raw `AttributeError` when a concurrent `disconnect()` clears the connection between the liveness check and the send. It now drops the just-registered request and raises `ManagerSocketError` instead (#3).
- The FastAGI server no longer prints an unhandled traceback to stderr when a client disconnects during the AGI environment handshake. A caller hanging up, Asterisk aborting the leg, or a bare TCP probe raised `AGISIGPIPEHangup` from the handler and printed a full traceback for a routine event. The handler now ends the request quietly. Errors raised by the script handler itself still propagate (#49).
- The FastAGI server sizes its listen backlog without shelling out to `sysctl`. It now requests the maximum backlog and lets the kernel cap it to the live system `somaxconn`, which still tracks a tuned-up limit automatically. This also lifts the platform restriction added in 1.3.0: the server previously raised `NotImplementedError` on any host that was neither Linux nor macOS, and now runs everywhere (#32).

## [1.3.0] - 2026-06-24

### Added
- `AGENTS.md` with an architecture overview and contributor guidance.
- `CLAUDE.md` pointing to `AGENTS.md`.
- A Contributing section and AGI, FastAGI, and AMI quick-start examples in the README.
- `.readthedocs.yaml` and `doc/requirements.txt` for reproducible documentation builds.
- A GitHub Actions CI workflow that runs the test suite with coverage across Python 3.9 through 3.13, plus a documentation build check.
- A `pytest` unit-test suite covering AMI message parsing and request building, AGI response parsing, and action and helper formatting, with `pytest` and `pytest-cov` in a `test` extra (`pip install -e '.[test]'`).
- Coverage measurement through `pytest-cov`, reported in the CI logs. No coverage data leaves CI.
- A CI status badge in the README.
- A curated `ruff` configuration, a `.pre-commit-config.yaml`, and a CI lint job.
- This changelog.

### Changed
- Converted `README.rst` to `README.md` and corrected the version and install URL.
- Stated the license as the GNU LGPLv3 or later across the README and packaging metadata. pystrix is not dual-licensed. Both `COPYING` and `COPYING.LESSER` ship because the LGPL extends the GPL.
- Declared Python 3.9+ through `python_requires` and trove classifiers (3.9 through 3.13), and dropped Python 2 and the end-of-life 3.x entries.
- Narrowed the "any platform" claim. The FastAGI server runs on Linux and macOS only, because it reads `SOMAXCONN` with `sysctl`.
- Removed the `AUTHORS` file. Provenance now lives in the README, and the contributor list comes from git history and the GitHub contributors page.
- Modernized `doc/conf.py` (`exclude_patterns`, Read the Docs theme with a fallback, raw-string regex).
- Formatted the whole codebase with `ruff format` (line length 88) and enabled import sorting (ruff's `I` rule). Both are now enforced in pre-commit and CI. A `.git-blame-ignore-revs` file lets `git blame` skip the reformat commit.
- Migrated packaging from `setup.py` to `pyproject.toml` (PEP 621) with a PEP 639 SPDX license expression (`LGPL-3.0-or-later`). Moved the ruff config into `[tool.ruff]`, and removed `setup.py`, `build-release.py`, and `ruff.toml`. Build with `python -m build`; the version is read dynamically from `pystrix.VERSION`.

### Removed
- The Python 2 compatibility shims: the `queue` and `socketserver` import fallbacks, the `basestring` branch in `generic_transforms`, and the explicit `(object)` base classes. The codebase is now Python 3 only. Dropping Python 2 is released as a pragmatic minor bump rather than a major one, since Python 2 support was already nominal and end-of-life.

### Fixed
- Narrowed the bare `except` around `line.decode()` in `_AGI._read_line` to an `isinstance(line, bytes)` check. A real `UnicodeDecodeError` on malformed socket bytes now surfaces instead of being swallowed and leaving raw bytes in the line (#50).
- Applied safe lint fixes surfaced by ruff: `not x is`/`not x in` rewritten to `x is not`/`x not in`, removed unused imports, and turned two invalid escape sequences (`\d`, `\*`) into raw strings. Intentional re-exports are marked with targeted ignores.
- `_Request.build_request` now honors its documented ActionID precedence: an explicit argument wins, then a value already set on the request, then a generated one. Previously a pre-set ActionID was dropped when no argument was passed, and it overrode an explicit argument. The resolved ActionID is also coerced to a string so a pre-set non-string value matches Asterisk's responses (#43).
- Replaced the removed `cgi.urlparse.parse_qs` in `pystrix/agi/fastagi.py` with `urllib.parse.parse_qs`. This fixes FastAGI query-string parsing on all Python 3 and restores Python 3.13 support (#36).
- Corrected the `_Response.time` description in the AMI docs and fixed several typos.
- Stopped tracking `doc/_build/` output and macOS `._` metadata files, and fixed the `.gitignore` rule that let them in.

## [1.2.0]

### Added
- FastAGI server sizes its listen backlog from the system `SOMAXCONN`, raising the number of concurrent calls it can accept.

### Changed
- FastAGI server enables `allow_reuse_address` on the socket.

---

Releases before 1.2.0 are recorded in the git commit history.

[Unreleased]: https://github.com/IVRTech/pystrix/compare/v1.3.0...HEAD
[1.3.0]: https://github.com/IVRTech/pystrix/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/IVRTech/pystrix/releases/tag/v1.2.0
