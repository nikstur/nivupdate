{ lib
, mkPoetryApplication
, makeBinaryWrapper
, niv
, git
  # openssh is needed for git ssh dependencies
, openssh
  # nix is needed for nix-prefetch-url called by niv
  # See https://github.com/nmattia/niv/issues/222
, nix
}:
let
  pathInputs = [
    openssh
    niv
    git
    nix
  ];
in
mkPoetryApplication {

  projectDir = ./.;

  preferWheels = true;

  nativeBuildInputs = [ makeBinaryWrapper ];

  postFixup = ''
    wrapProgram $out/bin/nivupdate --set PATH ${ lib.makeBinPath pathInputs }
  '';

}
