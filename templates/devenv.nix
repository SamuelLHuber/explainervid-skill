{ pkgs, ... }:

{
  packages = [
    pkgs.uv
    pkgs.pkg-config
    pkgs.cairo
    pkgs.pango
    pkgs.ffmpeg
    (pkgs.texlive.combine {
      inherit (pkgs.texlive) scheme-medium standalone preview;
    })
  ];

  env.PIP_DISABLE_PIP_VERSION_CHECK = "1";
  env.PIP_NO_PYTHON_VERSION_WARNING = "1";

  enterShell = ''
    echo "explainer video dev shell"
    echo "Use ./devenv.sh 'python build.py check' or ./devenv.sh 'python build.py render --quality low'"
  '';
}
