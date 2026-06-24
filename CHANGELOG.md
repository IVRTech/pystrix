# Changelog

All notable changes to pystrix are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project aims
to follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `AGENTS.md` with an architecture overview and contributor guidance.
- `CLAUDE.md` pointing to `AGENTS.md`.
- A Contributing section and AGI, FastAGI, and AMI quick-start examples in the README.
- `.readthedocs.yaml` and `doc/requirements.txt` for reproducible documentation builds.
- This changelog.

### Changed
- Converted `README.rst` to `README.md` and corrected the version and install URL.
- Stated the license as the GNU LGPLv3 or later across the README and `setup.py`. pystrix is not dual-licensed. Both `COPYING` and `COPYING.LESSER` ship because the LGPL extends the GPL.
- Declared Python 3.9+ in `setup.py` through `python_requires` and trove classifiers, and dropped Python 2 and the end-of-life 3.x entries. The classifiers stop at 3.12, because `pystrix/agi/fastagi.py` imports the `cgi` module that Python 3.13 removed (tracked in #36).
- Narrowed the "any platform" claim. The FastAGI server runs on Linux and macOS only, because it reads `SOMAXCONN` with `sysctl`.
- Removed the `AUTHORS` file. Provenance now lives in the README, and the contributor list comes from git history and the GitHub contributors page.
- Modernized `doc/conf.py` (`exclude_patterns`, Read the Docs theme with a fallback, raw-string regex).

### Fixed
- `build-release.py` no longer fails on the missing `pystrix.spec`. The RPM packaging path was removed, and the release tarball now ships `README.md` and `CHANGELOG.md` so a build from the sdist can read the long description.
- Corrected the `_Response.time` description in the AMI docs and fixed several typos.
- Stopped tracking `doc/_build/` output and macOS `._` metadata files, and fixed the `.gitignore` rule that let them in.

## [1.2.0]

### Added
- FastAGI server sizes its listen backlog from the system `SOMAXCONN`, raising the number of concurrent calls it can accept.

### Changed
- FastAGI server enables `allow_reuse_address` on the socket.

---

Releases before 1.2.0 are recorded in the git commit history.

[Unreleased]: https://github.com/IVRTech/pystrix/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/IVRTech/pystrix/releases/tag/v1.2.0
