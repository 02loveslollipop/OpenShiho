# ovpn/

Drop your HackTheBox OpenVPN profiles here **before** running `./build.sh`.
They will be copied into the image at `/home/shiho/` during the build.

This directory is gitignored — your VPN credentials are never committed.

Convention used by the `htb-connect` helper:
- `release.ovpn` — Release Arena (`htb-connect -r`)
- `machines2.ovpn` — Machines network (`htb-connect -m`)

A redacted template is in `example.ovpn.template` for reference.
