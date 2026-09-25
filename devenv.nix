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
    echo "explainervid-skill dev shell"
    echo "Native deps: cairo, pango, ffmpeg, latex, dvisvgm"
    echo "Use: ./scripts/scaffold_project.sh my_explainer /tmp/my_explainer_video"
  '';
}
