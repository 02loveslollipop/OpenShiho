# OpenShiho

An agentic HackTheBox runtime. OpenShiho packages
[opencode](https://opencode.ai) as the operating agent inside a reproducible
Debian 12 + KDE Plasma + TigerVNC + SSH container, and ships it prepackaged
with [OpenCROW](https://github.com/02loveslollipop/OpenCROW)'s toolbox and
I/O connector skills — so the agent can pick the right tool for a challenge
(pwn, crypto, reversing, network, web, forensics, osint, stego) and drive
long-running interactive sessions (Minecraft, netcat, SSH) without you
wiring any of that up by hand.

The container itself works with both **podman** and **docker**, runs
systemd as PID 1 so services (VNC, SSH, `htb-connect`) start on boot, and
carries a persistent, queryable knowledge base under `~/scripts/` so what
the agent learns on one challenge is searchable on the next.

The image is ~6 GB, so the repo ships the build definition rather than the
image itself.

## What you get

- **opencode**, prepackaged with OpenCROW's `opencrow-*-toolbox` skills
  (pwn, crypto, reversing, network, web, forensics, osint, stego, utility)
  and its async I/O connectors (`minecraft-async`, `netcat-async`,
  `ssh-async`) — see [Skills](docs/contributor/skills.md).
- The underlying tool stack those skills drive: gdb/gdb-multiarch,
  radare2, pwntools, angr, capstone, unicorn, z3-solver, ropper, ROPgadget,
  checksec, and more.
- **KDE Plasma 5** desktop over TigerVNC on port **5901**, plus **SSH** on
  port **2222**, for when you want to drive the box directly.
- **/dev/net/tun + NET_ADMIN/NET_RAW** so OpenVPN (`htb-connect`) works.
- A **persistent knowledge base** in `~/`: `AGENTS.md`, `LEARNINGS.md`,
  `~/scripts/` with queryable script and learning archives that survive
  across challenge sessions.

## Quick start

```sh
curl -fsSL https://github.com/02loveslollipop/OpenShiho/releases/latest/download/openshiho-latest.zip -o openshiho.zip
unzip openshiho.zip
cd openshiho
./run.sh
```

`run.sh` auto-detects podman or docker and builds the image on first run if
it isn't present locally yet. See [Quick start](docs/user/quick-start.md) for
the source-checkout flow and connection details.

## Repository layout

- `container/` — everything needed to build and run the image:
  `Containerfile`, `build.sh`, `run.sh`, `config/`, `scripts/`, `skills/`,
  `ovpn/`, `quadlet/`, plus the in-container knowledge base (`AGENTS.md`,
  `LEARNINGS.md`). Self-contained — see
  [ADR 0001](docs/adr/0001-container-directory-split.md).
  - `skills/` is a `git subtree` of OpenCROW's toolbox and connector skills
    — see [ADR 0002](docs/adr/0002-skills-via-subtree.md).
- `docs/` — user, contributor, and ADR documentation.
- `.github/workflows/` — build check (docker + podman) and release packaging.

## Development

```sh
make build     # build the image
make run       # run it (builds first if needed)
make smoke     # validate shell/python syntax and workflow YAML
```

See [documentation index](docs/README.md) for installation details, build
arguments, troubleshooting, architecture, skill updates, and the release
process.

## License

Apache License 2.0 — see [LICENSE](LICENSE).
