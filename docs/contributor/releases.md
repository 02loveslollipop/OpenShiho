# Releases

## Cutting a release

```sh
git tag v1.0.0
git push origin v1.0.0
```

Pushing a tag matching `v*.*.*` triggers
`.github/workflows/release.yml`, which:

1. Copies `container/` plus the root `README.md` into an `openshiho/`
   staging directory.
2. Zips it as `openshiho-<tag>.zip`.
3. Publishes it to the repository's GitHub Release for that tag, with
   auto-generated release notes.

See [ADR 0001](../adr/0001-container-directory-split.md) for why the zip's
contents are exactly `container/`.

## Before tagging

Run `make smoke` locally. `.github/workflows/build.yml` also builds the
container with both docker and podman on every push and pull request to
`main` — check that it's green before cutting a release tag.

## Versioning

The repository tag (`vX.Y.Z`) versions the *release packaging*, independent
from the tool versions pinned as `Containerfile` build args
(`OPENCODE_VERSION`, `FASTFETCH_VERSION`, `R2_VERSION`). Bump those
separately when you want a newer tool inside the image.
