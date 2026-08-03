#!/usr/bin/env bash
set -euo pipefail

# shiho-runtime run helper. Starts the container with VNC (5901), SSH (2222),
# /dev/net/tun passthrough, and NET_ADMIN/NET_RAW capabilities so OpenVPN works.
# Builds the image first if it doesn't exist yet, so a fresh checkout (or a
# downloaded release archive) can be started with just ./run.sh.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

RUNTIME="${RUNTIME:-}"
TAG="${TAG:-shiho-runtime:latest}"
NAME="${NAME:-shiho-runtime}"

detect_runtime() {
    if [ -n "$RUNTIME" ]; then
        return 0
    fi
    if command -v podman >/dev/null 2>&1; then
        RUNTIME=podman
    elif command -v docker >/dev/null 2>&1; then
        RUNTIME=docker
    else
        echo "error: neither podman nor docker found" >&2
        exit 1
    fi
}

detect_runtime
echo "==> Using runtime: $RUNTIME"

if ! "$RUNTIME" image inspect "$TAG" >/dev/null 2>&1; then
    echo "==> Image $TAG not found locally; building it first..."
    RUNTIME="$RUNTIME" TAG="$TAG" ./build.sh
fi

COMMON=(
    --name "$NAME"
    --hostname shiho-runtime
    -p 5901:5901
    -p 2222:2222
    --device /dev/net/tun
    --cap-add NET_ADMIN
    --cap-add NET_RAW
    --memory 2g
)

if [ "$RUNTIME" = "podman" ]; then
    # Podman runs /sbin/init as systemd PID 1; no extra flags needed for systemd.
    "$RUNTIME" rm -f "$NAME" >/dev/null 2>&1 || true
    "$RUNTIME" run -d "${COMMON[@]}" "$TAG" /sbin/init
else
    # Docker needs cgroup + tmpfs setup for systemd in a container.
    "$RUNTIME" rm -f "$NAME" >/dev/null 2>&1 || true
    "$RUNTIME" run -d \
        "${COMMON[@]}" \
        --tmpfs /tmp --tmpfs /run \
        -v /sys/fs/cgroup:/sys/fs/cgroup:rw \
        "$TAG" /sbin/init
fi

echo "==> Started $NAME"
echo "    VNC:  localhost:5901 (password: \$VNC_PASSWORD build arg)"
echo "    SSH:  ssh shiho@localhost -p 2222"
