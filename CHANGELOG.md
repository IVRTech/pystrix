# Changelog

All notable changes to pystrix are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project aims
to follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `AGENTS.md` with an architecture overview and contributor guidance.
- `CLAUDE.md` pointing to `AGENTS.md`.
- `Contributing` section in the README.
- `.readthedocs.yaml` and `doc/requirements.txt` for reproducible documentation builds.
- This changelog.

### Changed
- Converted `README.rst` to `README.md` and corrected the version, install URL, and license wording.
- Declared Python 3.9+ support in `setup.py` (`python_requires` and trove classifiers); dropped Python 2 and end-of-life 3.x classifiers.
- Rewrote `AUTHORS` as the single source of truth for credits.
- Modernized `doc/conf.py` (`exclude_patterns`, Read the Docs theme with a fallback, raw-string regex).

### Fixed
- `build-release.py` no longer fails on the missing `pystrix.spec`; the RPM packaging path was removed.
- Corrected the `_Response.time` description in the AMI docs and fixed several typos.
- Stopped tracking `doc/_build/` output and macOS `._` metadata files; fixed the `.gitignore` rule that let them in.

## [1.2.0]

### Added
- FastAGI server sizes its listen backlog from the system `SOMAXCONN`, raising the number of concurrent calls it can accept.

### Changed
- FastAGI server enables `allow_reuse_address` on the socket.

---

Releases before 1.2.0 are recorded in the git commit history.

[Unreleased]: https://github.com/IVRTech/pystrix/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/IVRTech/pystrix/releases/tag/v1.2.0
