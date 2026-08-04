# Contributing to OpenShiho

Keep `container/` self-contained — see
[ADR 0001](docs/adr/0001-container-directory-split.md). Anything a running
container needs at build or run time belongs under `container/`, not the
repo root.

If you're changing the in-container persistent script/learning conventions
(`~/scripts/`, `~/scripts/learnings/`), follow the schema and immutability
rules already defined in `container/AGENTS.md` — don't edit a versioned
script in place; add a new version instead.

`container/skills/` is a `git subtree` of OpenCROW, not hand-edited directly
— see [Skills](docs/contributor/skills.md) for how to pull upstream updates.

Run `make smoke` before submitting a change. It checks shell syntax, Python
syntax, and workflow YAML. `.github/workflows/build.yml` additionally builds
the container end-to-end with both docker and podman on every push and pull
request.

Update the relevant page under `docs/` when behavior, layout, or build args
change — see the [documentation index](docs/README.md).
