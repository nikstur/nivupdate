{
  description = "Update Niv dependencies via GitLab Pull Requests with a single command";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    utils.url = "github:numtide/flake-utils";
    poetry2nix.url = "github:nix-community/poetry2nix";
    poetry2nix.inputs.nixpkgs.follows = "nixpkgs";
    pre-commit-hooks.url = "github:cachix/pre-commit-hooks.nix";
    pre-commit-hooks.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, utils, poetry2nix, pre-commit-hooks }:
    utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        poetry2nix' = pkgs.callPackage poetry2nix { };
        # Wheels need to be preferred otherwise pytest cannot be used
        nivupdate = poetry2nix'.mkPoetryApplication {
          projectDir = ./.;
          preferWheels = true;
        };
        nivupdateEnv = poetry2nix'.mkPoetryEnv {
          projectDir = ./.;
          preferWheels = true;
        };
      in
      {
        packages.default = nivupdate;

        checks = {
          pre-commit = pre-commit-hooks.lib.${system}.run {
            src = ./.;
            hooks = {
              nixpkgs-fmt.enable = true;
              statix.enable = true;
            };
          };
        };

        # devShells.default = nivupdateEnv.env;

        devShells.default = with pkgs; mkShell {
          inputsFrom = [ nivupdateEnv ];
          packages = [ poetry ];
          inherit (self.checks.${system}.pre-commit) shellHook;
        };
      });
}
