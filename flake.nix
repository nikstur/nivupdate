{
  description = "Update Niv dependencies via GitLab Pull Requests with a single command";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    utils.url = "github:numtide/flake-utils";
    poetry2nix.url = "github:nix-community/poetry2nix";
    poetry2nix.inputs.nixpkgs.follows = "nixpkgs";
    pre-commit-hooks.url = "github:cachix/pre-commit-hooks.nix";
    pre-commit-hooks.inputs.nixpkgs.follows = "nixpkgs";
    flake-compat = { url = "github:edolstra/flake-compat"; flake = false; };
  };

  outputs = { self, nixpkgs, utils, poetry2nix, pre-commit-hooks, ... }:
    {
      overlays.default = final: prev: {
        nivupdate = final.callPackage ./build.nix {
          poetry2nix = final.callPackage poetry2nix { };
        };
      };
    } // utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        poetry2nix' = pkgs.callPackage poetry2nix { };

        nivupdateEnv = poetry2nix'.mkPoetryEnv {
          projectDir = ./.;
          # Wheels need to be preferred otherwise pytest cannot be used
          preferWheels = true;
          editablePackageSources = {
            nivupdate = ./.;
          };
        };

        nivupdate = pkgs.callPackage ./build.nix {
          poetry2nix = poetry2nix';
        };

      in
      {
        packages = {
          default = nivupdate;
        };

        apps = {
          default = utils.lib.mkApp { drv = nivupdate; };
        };

        checks = {
          pre-commit = pre-commit-hooks.lib.${system}.run {
            src = ./.;
            hooks = {
              nixpkgs-fmt.enable = true;
              statix.enable = true;
              black.enable = true;
              isort.enable = true;
              flake8.enable = true;
            };
            excludes = [ "sources.nix" ];
            settings = {
              statix.ignore = [ "sources.nix" ];
            };
          };
        };

        devShells.default = with pkgs; mkShell {
          inputsFrom = [ nivupdateEnv.env ];
          packages = [
            poetry
            openssh
            niv
            git
          ];
          inherit (self.checks.${system}.pre-commit) shellHook;
        };
      });
}
