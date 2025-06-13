{
  description = "Minimal python dev env";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/release-24.11";
  };

  outputs = { nixpkgs, ... }: 
  let
    systems = [ "aarch64-darwin" "x86_64-linux" ];
    makeShell =
      system: let 
        pkgs = import nixpkgs { inherit system; };
      in {
        name = "${system}";
        value = {
          default = pkgs.mkShell {
            packages = with pkgs; [
              pyright
            ];
          };
        };
      };
  in
  {
    devShells = builtins.listToAttrs (map makeShell systems);
  };
}
