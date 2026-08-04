# Installation

All commands below are run from `container/` unless noted otherwise.

## Build

```sh
cd container
./build.sh                    # auto-detects podman, else docker
TAG=mytag RUNTIME=docker ./build.sh
VNC_PASSWORD=secret ./build.sh
```

The image is tagged `openshiho:latest` by default. `build.sh` stages
`Containerfile`, `AGENTS.md`, `LEARNINGS.md`, `config/`, and `scripts/` into a
temporary build context so the Containerfile only ever sees what it needs.

### Build arguments

| ARG                 | Default   | Description                    |
|---------------------|-----------|---------------------------------|
| `VNC_PASSWORD`       | `vm@2026` | TigerVNC password               |
| `USER_PASSWORD`      | `1234`    | `shiho` SSH/login password      |
| `OPENCODE_VERSION`   | `1.18.11` | opencode release version        |
| `FASTFETCH_VERSION`  | `2.66.0`  | fastfetch release version       |
| `R2_VERSION`         | `6.1.8`   | radare2 release version          |

### Optional: include your OpenVPN profiles

Put your real HTB profiles in `container/ovpn/` before building:

```sh
cp /path/to/release.ovpn   container/ovpn/release.ovpn
cp /path/to/machines2.ovpn container/ovpn/machines2.ovpn
cd container && ./build.sh
```

`container/ovpn/` is gitignored, so credentials never enter the repo. See
`container/ovpn/README.md` for the naming convention the `htb-connect` helper
expects.

## Run

```sh
cd container
./run.sh                      # podman or docker; builds first if the image is missing
RUNTIME=docker ./run.sh
```

### Manual run (podman)

```sh
podman rm -f openshiho 2>/dev/null
podman run -d --name openshiho --hostname openshiho \
    -p 5901:5901 -p 2222:2222 \
    --device /dev/net/tun --cap-add NET_ADMIN --cap-add NET_RAW \
    --memory 2g openshiho:latest /sbin/init
```

### Manual run (docker)

```sh
docker rm -f openshiho 2>/dev/null
docker run -d --name openshiho --hostname openshiho \
    -p 5901:5901 -p 2222:2222 \
    --device /dev/net/tun --cap-add NET_ADMIN --cap-add NET_RAW \
    --memory 2g \
    --tmpfs /tmp --tmpfs /run \
    -v /sys/fs/cgroup:/sys/fs/cgroup:rw \
    openshiho:latest /sbin/init
```

## systemd / Quadlet (podman)

For a fully-managed setup (auto-start, stable hostname), a sample Quadlet
unit is in `container/quadlet/`:

```sh
mkdir -p ~/.config/containers/systemd
cp container/quadlet/openshiho.container ~/.config/containers/systemd/
systemctl --user daemon-reload
systemctl --user enable --now openshiho.service
```

If you use Quadlet with SELinux enforcing, see
[Troubleshooting](troubleshooting.md) for the `/dev/net/tun` caveats it
already accounts for (`SecurityLabelDisable=true`, explicit
`AddCapability=NET_ADMIN NET_RAW`).
