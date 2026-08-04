# ADR 0002: `container/skills` is a git subtree of OpenCROW, scoped to toolboxes and connectors

Status: accepted.

`container/skills/` is populated from
[OpenCROW](https://github.com/02loveslollipop/OpenCROW)'s `skills/`
directory via `git subtree`, not a symlink or a submodule.

A symlink only resolves on a machine that also has open-crow checked out at
a known path; it would leave a dangling link in the Containerfile build
context (COPY cannot follow it) and in downloaded release zips. A submodule
would leave `container/skills` empty on a plain `git clone` unless every
consumer (including CI and the release workflow) remembers
`--recurse-submodules`, which conflicts with [ADR 0001](0001-container-directory-split.md)'s
requirement that `container/` be self-contained. A subtree merges real,
committed files, so every checkout and every release zip already has them.

`git subtree` only imports a whole source repository at a destination
prefix — it has no notion of "only this subdirectory of the source". To
bring in just OpenCROW's `skills/` tree, OpenCROW carries a maintained
branch, `skills-subtree/release`, produced by
`git subtree split --prefix=skills`, containing only that subdirectory's
history with paths already rebased to the top level. That branch is what
OpenShiho's subtree points at.

Only skills classified as a toolbox (`opencrow-*-toolbox`) or an I/O
connector (`minecraft-async`, `netcat-async`, `reverse-shell-async`,
`ssh-async`) are kept, plus
`_shared` (the Python runtime helper several toolbox scripts import).
Anything else OpenCROW ships under `skills/` — currently just `sagemath`,
classified as a "Runner" rather than a toolbox or connector — is removed
from `container/skills` after each subtree pull. Constellation is a
separate OpenCROW service, not something that ever appears under
`skills/`, so no constellation-specific pruning has been needed so far;
if a skill referencing Constellation is ever added upstream, it gets
removed the same way.

See [Skills](../contributor/skills.md) for the update procedure.
