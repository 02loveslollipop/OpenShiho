# Architecture

shiho-runtime is separated by what ships versus what only supports the repo.

`container/` is self-contained and is exactly what a release zip contains:
`Containerfile`, `build.sh`, `run.sh`, `config/`, `scripts/`, `ovpn/`,
`quadlet/`, and the in-container knowledge base (`AGENTS.md`,
`LEARNINGS.md`). Nothing in `container/` depends on paths outside itself, so
it can be copied out of the repo and still build and run.

The repo root holds only documentation and CI (`README.md`, `docs/`,
`.github/workflows/`). See [ADR 0001](../adr/0001-container-directory-split.md)
for why the split exists.

`build.sh` stages `container/`'s contents into a temporary directory before
invoking `docker build` / `podman build`, so the Containerfile's `COPY`
instructions only ever see what's actually needed for the image, plus
whatever OpenVPN profiles the user dropped into `container/ovpn/`.

`run.sh` auto-detects the container runtime, builds the image if it's
missing, and applies the runtime-specific flags systemd-as-PID-1 needs
(see [Troubleshooting](../user/troubleshooting.md)).

The in-container persistent knowledge base (`~/scripts/`, `~/AGENTS.md`,
`~/LEARNINGS.md`) follows its own conventions, documented in full inside
`container/AGENTS.md`.
