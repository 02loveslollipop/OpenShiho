# Troubleshooting

Known host-level pitfalls when building or running the container. Learnings
specific to working *inside* the container (agent/session behavior) live in
`container/LEARNINGS.md` instead.

## Rootless podman can't create a TUN device

Rootless podman cannot attach `/dev/net/tun` on the host network. Use a
bridge network with published ports (this is what `run.sh` and the sample
Quadlet already do) instead of `--network host`.

## SELinux blocks `/dev/net/tun`

With SELinux in `Enforcing` mode, container access to `/dev/net/tun` is
denied unless the container's security label is disabled. The sample Quadlet
in `container/quadlet/` sets `SecurityLabelDisable=true` for this reason.

## `/dev/net/tun` needs both a device and capabilities

Passing `--device /dev/net/tun` alone is not enough for OpenVPN to bring up a
tunnel; the container also needs `NET_ADMIN` and `NET_RAW`. `run.sh` and the
Quadlet unit both add all three.

## systemd as PID 1 under docker vs. podman

Podman runs `/sbin/init` as systemd PID 1 without extra flags. Docker needs
`--tmpfs /tmp --tmpfs /run -v /sys/fs/cgroup:/sys/fs/cgroup:rw` for systemd
to start cleanly. `run.sh` branches on the detected runtime to apply the
right set of flags automatically — see `container/run.sh` if you're
reproducing this manually.
