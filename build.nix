{ lib
, poetry2nix
, niv
, git
, openssh # needed for git ssh dependencies
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
