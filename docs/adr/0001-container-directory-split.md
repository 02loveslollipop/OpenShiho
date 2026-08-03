# ADR 0001: Container assets live under `container/`

Status: accepted.

All build/run assets (`Containerfile`, `build.sh`, `run.sh`, `config/`,
`scripts/`, `ovpn/`, `quadlet/`, plus the in-container `AGENTS.md` and
`LEARNINGS.md`) live under `container/` instead of the repo root.

The release workflow (`.github/workflows/release.yml`) packages `container/`
verbatim into the release zip. Keeping it self-contained means the release
artifact is exactly the directory a contributor already builds and tests
from — there is no separate packaging step that could drift from what's in
version control, and the repo root stays free to hold documentation and CI
without those files leaking into what end users download.

This avoids coupling the shipped artifact's shape to the whole repository
layout, and keeps `docs/` and `.github/` additions from ever needing to be
excluded from a release zip.
