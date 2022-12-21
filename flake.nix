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
    utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        poetry2nix' = pkgs.callPackage poetry2nix { };
        pathInputs = with pkgs; [
          openssh # needed for git ssh dependencies
          niv
          git
        ];
        commonArgs = {
          projectDir = ./.;
          # Wheels need to be preferred otherwise pytest cannot be used
          preferWheels = true;
        };
        nivupdate = poetry2nix'.mkPoetryApplication commonArgs // { };
        nivupdateEnv = poetry2nix'.mkPoetryEnv commonArgs // {
          editablePackageSources = {
            nivupdate = ./.;
          };
        };

        wrappedNivupdate = pkgs.runCommand "nivupdate"
          {
            nativeBuildInputs = [ pkgs.makeWrapper ];
          } ''
          mkdir -p $out/bin
          makeWrapper ${nivupdate}/bin/nivupdate $out/bin/nivupdate \
            --set PATH ${pkgs.lib.makeBinPath pathInputs} \
        '';

        nivupdateGitlab = pkgs.writeShellApplication {
          name = "nivupdate";

          runtimeInputs = [
            pkgs.openssh
            wrappedNivupdate
          ];

          text = ''
            eval $(ssh-agent -s)
            echo "$SSH_PRIVATE_KEY" | tr -d '\r' | ssh-add -
            mkdir -p ~/.ssh
            chmod 700 ~/.ssh
            nivupdate $@
          '';
        };
      in
      {
        packages = {
          default = wrappedNivupdate;
          gitlab = nivupdateGitlab;
        };

        apps = {
          default = utils.lib.mkApp { drv = wrappedNivupdate; };
          gitlab = utils.lib.mkApp { drv = nivupdateGitlab; };
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
              statix.ignore = [ "sources.nix" "patches" ];
            };
          };
        };

        devShells.default = with pkgs; mkShell {
          inputsFrom = [ nivupdateEnv.env ];
          packages = pathInputs ++ [
            poetry
          ];
          inherit (self.checks.${system}.pre-commit) shellHook;
        };
      });
}
