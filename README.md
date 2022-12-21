# NivUpdate

Update Niv dependencies via GitLab Merge Requests using a single command

## Getting Started

You can run `nivupdate locally`:

```sh
nix run github.com:nikstur/nivupdate
```

or from the GitLab CI:

```yml
nivupdate:
  script:
    - nix run --refresh github.com:nikstur/nivupdate#gitlab
```

To make sure you're running the newest version of `nivupdate` with `nix run`,
you can add the `--refresh` flag to the nix command to force it to download the
newest version.
