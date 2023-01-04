let
  sources = import ./nix/sources.nix { };
  nivupdate = import sources.nivupdate;
  pkgs = import sources.nixpkgs {
    overlays = [ nivupdate.overlays.default ];
  };

  # You can define your own wrapper script to make some nivupdate actions even
  # simpler.
  updateWithMR = pkgs.writeShellApplication {
    name = "update-with-mr";
    runtimeInputs = [ pkgs.nivupdate ];
    text = ''
      nivupdate --mr --url "https://gitlab.example.com/mygroup/myproject" 
    '';
  };
in
pkgs.mkShell
{
  packages = [ pkgs.nivupdate updateWithMR ];
}
