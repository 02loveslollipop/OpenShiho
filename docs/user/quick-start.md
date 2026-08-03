# Quick start

## From a release (recommended)

Download the latest zip from the [Releases page](../../../../releases),
unzip it, and run:

```sh
unzip shiho-runtime-*.zip
cd shiho-runtime
./run.sh
```

`run.sh` auto-detects podman or docker, builds the image if it isn't present
locally yet, then starts the container. No separate build step is required.

## From a source checkout

```sh
git clone git@github.com:02loveslollipop/shiho-runtime.git
cd shiho-runtime/container
./run.sh
```

## Connect

```text
VNC:  vncviewer localhost:5901       (password: vm@2026, or your --build-arg)
SSH:  ssh shiho@localhost -p 2222    (password: 1234, or your --build-arg)
```

See [Installation](installation.md) for build arguments, OpenVPN profile
injection, manual run commands, and the systemd/Quadlet unit.
