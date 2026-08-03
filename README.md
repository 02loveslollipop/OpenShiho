# shiho-runtime

A reproducible Debian 12 + KDE Plasma + TigerVNC + SSH container for CTF /
HackTheBox work. Built from a `Containerfile` that works with both **podman**
and **docker**, configured for a systemd PID 1 so `htb-connect`, VNC, and SSH
all run as services. Ships with a security-tool stack (gdb, radare2, pwntools,
angr, and more) and a persistent, queryable knowledge base under `~/scripts/`.

The image is ~6 GB, so the repo ships the build definition rather than the
image itself.

## Quick start

```sh
curl -fsSL https://github.com/02loveslollipop/shiho-runtime/releases/latest/download/shiho-runtime-latest.zip -o shiho-runtime.zip
unzip shiho-runtime.zip
cd shiho-runtime
./run.sh
```

`run.sh` auto-detects podman or docker and builds the image on first run if
it isn't present locally yet. See [Quick start](docs/user/quick-start.md) for
the source-checkout flow and connection details.

## Repository layout

- `container/` — everything needed to build and run the image: `Containerfile`,
  `build.sh`, `run.sh`, `config/`, `scripts/`, `ovpn/`, `quadlet/`, plus the
  in-container knowledge base (`AGENTS.md`, `LEARNINGS.md`). Self-contained —
  see [ADR 0001](docs/adr/0001-container-directory-split.md).
- `docs/` — user, contributor, and ADR documentation.
- `.github/workflows/` — build check (docker + podman) and release packaging.

## Development

```sh
make build     # build the image
make run       # run it (builds first if needed)
make smoke     # validate shell/python syntax and workflow YAML
```

See [documentation index](docs/README.md) for installation details, build
arguments, troubleshooting, architecture, and the release process.

## License

Apache License 2.0 — see [LICENSE](LICENSE).
