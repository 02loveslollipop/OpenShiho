#!/usr/bin/env bash
set -euo pipefail

# shiho-runtime build helper. Stages the build context so OpenVPN profiles placed in
# ./ovpn/ (gitignored) are injected into the image without being committed.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

RUNTIME="${RUNTIME:-}"      # auto-detect if unset: podman, else docker
TAG="${TAG:-shiho-runtime:latest}"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

VNC_PASSWORD="${VNC_PASSWORD:-vm@2026}"
USER_PASSWORD="${USER_PASSWORD:-1234}"

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

# Stage everything the Containerfile needs.
cp -r Containerfile AGENTS.md LEARNINGS.md config scripts skills "$STAGE/"

# Inject OpenVPN profiles if the user dropped any into ./ovpn/
mkdir -p "$STAGE/ovpn"
if compgen -G 'ovpn/*.ovpn' >/dev/null; then
    echo "==> Including OpenVPN profile(s):"
    cp -v ovpn/*.ovpn "$STAGE/ovpn/" | sed 's/^/    /'
else
    echo "==> No OpenVPN profiles in ./ovpn/ (optional; build proceeds without them)"
fi

echo "==> Building image $TAG ..."
"$RUNTIME" build \
    --build-arg VNC_PASSWORD="$VNC_PASSWORD" \
    --build-arg USER_PASSWORD="$USER_PASSWORD" \
    -t "$TAG" \
    -f "$STAGE/Containerfile" \
    "$STAGE"

echo "==> Done: $TAG"
