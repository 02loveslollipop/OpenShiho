# LEARNINGS

Lessons learned while working in the shiho-runtime container.

Format: `YYYY-MM-DD | topic | lesson`

Structured, machine-queryable learnings also live under `scripts/learnings/`
as one YAML file per learning (see AGENTS.md section 10 for the schema).

2026-08-03 | infra | Rootless podman cannot create a TUN device on the host network; use a bridge network with published ports (5901/2222).
2026-08-03 | infra | SELinux (Enforcing) blocks container access to /dev/net/tun; requires `SecurityLabelDisable=true` in the Quadlet.
2026-08-03 | infra | /dev/net/tun needs both `AddDevice=/dev/net/tun` and `AddCapability=NET_ADMIN NET_RAW`.
2026-08-03 | infra | htb-connect: openvpn runs as root (sudo), so `kill -0` as a normal user reports EPERM; check `/proc/$pid` existence instead.
2026-08-03 | infra | openvpn `--writepid` writes the pid after the daemon forks; poll for the pid file before reporting success.
2026-08-03 | infra | Bind-mounted persistent dirs (scripts/, LEARNINGS, AGENTS) need 777/666 so both container-root and container-UID-1000 can write.
