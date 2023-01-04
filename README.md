# NivUpdate

Update Niv dependencies via GitLab Merge Requests using a single command.

## Getting Started

You can run `nivupdate` locally:

```sh
nix run github.com:nikstur/nivupdate
```

or from the GitLab CI:

```yml
nivupdate:
  script:
    - |
      nix run --refresh github.com:nikstur/nivupdate -- \
        --mr \
	--url "$CI_PROJECT_URL" \
	--user "NivUpdate Bot"
```

To make sure you're running the newest version of `nivupdate` with `nix run`,
you can add the `--refresh` flag to the nix command to force it to download the
newest version.

You can also pass a custom SSH command to nivupdate (and thus to Git) so that
you can access your repository with a e.g. a custom SSH key and without strict
host key checking. This makes it easy to use nivupdate in CI even when HTTP(S)
access to your repository is disabled.

```sh
nix run github.com:nikstur/nivupdate -- \
  --ssh-cmd "ssh -o StrictHostKeyChecking=no -i $SSH_PRIVATE_KEY"
```

## Pinning NivUpdate

The recommended ways to pin nivupdate are via Niv itself or with Flakes. 

### Niv 

```sh
niv init
niv add nikstur/nivupdate
```

See `examples/niv` for an example that pulls in nivupdate via Niv and also
defines a wrapper script to adjust nivupdate to the project's need.
