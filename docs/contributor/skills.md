# Skills

`container/skills/` is a `git subtree` of
[OpenCROW](https://github.com/02loveslollipop/OpenCROW)'s `skills/`
directory, scoped to toolboxes and I/O connectors only. See
[ADR 0002](../adr/0002-skills-via-subtree.md) for why.

## What's in scope

- `opencrow-*-toolbox` — the toolbox skills.
- `minecraft-async`, `netcat-async`, `reverse-shell-async`, `ssh-async` — the
  async I/O connectors.
- `_shared` — the Python runtime helper toolbox scripts import; not a skill
  itself, but required by ones that are kept.

Everything else OpenCROW ships under `skills/` (currently just `sagemath`,
an OpenCROW "Runner") is pruned after every pull.

## Updating

OpenCROW doesn't publish a ready-made subtree branch by default, so the
split has to be (re)created there first, then pulled here.

**In a checkout of OpenCROW**, on the branch OpenShiho tracks
(`release`):

```sh
git checkout release && git pull
git branch -D skills-subtree/release 2>/dev/null
git subtree split --prefix=skills -b skills-subtree/release release
git push origin skills-subtree/release --force
```

**In OpenShiho**:

```sh
git subtree pull --prefix=container/skills \
    https://github.com/02loveslollipop/OpenCROW.git skills-subtree/release --squash
```

Then re-check `container/skills` for anything outside the toolbox/connector
scope (diff against the list above) and remove it, e.g.:

```sh
git rm -r container/skills/sagemath   # if OpenCROW reintroduced it
git commit -m "Prune non-toolbox/non-connector skills from the OpenCROW subtree"
```

Run `make smoke` before pushing.
