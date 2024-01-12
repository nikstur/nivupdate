{
  description = "Update Niv dependencies via GitLab Pull Requests with a single command";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

    flake-utils.url = "github:numtide/flake-utils";

    flake-compat = {
      url = "github:edolstra/flake-compat";
      flake = false;
    };

    flake-parts = {
      url = "github:hercules-ci/flake-parts";
      inputs.nixpkgs-lib.follows = "nixpkgs";
    };

    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs = {
        nixpkgs.follows = "nixpkgs";
        flake-utils.follows = "flake-utils";
      };
    };

    pre-commit-hooks-nix = {
      url = "github:cachix/pre-commit-hooks.nix";
      inputs = {
        nixpkgs.follows = "nixpkgs";
        flake-utils.follows = "flake-utils";
        flake-compat.follows = "flake-compat";
      };
    };
  };

  outputs = inputs@{ self, flake-parts, ... }: flake-parts.lib.mkFlake { inherit inputs; } (_: {

    imports = [
      inputs.pre-commit-hooks-nix.flakeModule
    ];

    systems = [
      "x86_64-linux"
      "aarch64-linux"

      "x86_64-darwin"
      "aarch64-darwin"
    ];

    perSystem = { config, system, ... }:
      let
        pkgs = import inputs.nixpkgs { inherit system; };

        inherit (inputs.poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryApplication;

        nivupdate = pkgs.callPackage ./build.nix { inherit mkPoetryApplication; };
      in
      {
        packages = {
          inherit nivupdate;
          default = nivupdate;
        };

        pre-commit = {
          check.enable = true;

          settings = {
            hooks = {
              nixpkgs-fmt.enable = true;
              statix.enable = true;
              typos.enable = true;

              ruff.enable = true;
              black.enable = true;
              isort.enable = true;
            };

            excludes = [ "sources.nix" ];
            settings.statix.ignore = [ "sources.nix" ];
          };

        };

        devShells.default = pkgs.mkShell {
          shellHook = ''
            ${config.pre-commit.installationScript}
          '';

          inputsFrom = [ nivupdate ];
          packages = [ pkgs.poetry ];
        };
      };
  });
}
