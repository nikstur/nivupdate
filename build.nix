{ lib
, poetry2nix
, niv
, git
, openssh # needed for git ssh dependencies
  # nix is needed for nix-prefetch-url called by niv
  # See https://github.com/nmattia/niv/issues/222
, nix
, runCommand
, makeWrapper
}:
let
  nivupdate = poetry2nix.mkPoetryApplication {
    projectDir = ./.;
    # Wheels need to be preferred otherwise pytest cannot be used
    preferWheels = true;
  };

  pathInputs = [
    openssh
    niv
    git
    nix
  ];
in
runCommand "nivupdate"
{
  nativeBuildInputs = [ makeWrapper ];
} ''
  mkdir -p $out/bin
  makeWrapper ${nivupdate}/bin/nivupdate $out/bin/nivupdate \
    --set PATH ${lib.makeBinPath pathInputs} \
''
