# this Nix script is utilized to initialize the environment including required dependencies

let

  name = "pyspark-plaso-deployment";

  # Enable overlays (refer to the package being modified via `super` and to packages it uses via `cls`)
  # See https://gist.github.com/mayhewluke/e2f67c65c2e135f16a8e
  # NixOS v19.03: Spark v2.2.1 using Scala v2.11.8, OpenJDK 64-Bit v1.8.0_212
  # NixOS v19.09: Spark v2.4.3 using Scala v2.11.12, OpenJDK 64-Bit v1.8.0_212
  # NixOS v20.03: Spark v2.4.4 using Scala v???; but Mesos is broken, see https://github.com/NixOS/nixpkgs/issues/78557
  sparkOverlay = cls: super: {
    spark = (super.spark.override {
      RSupport = false;
      mesosSupport = false;
    });
  };
  overlays = [
    sparkOverlay	# no need in NixOS v20.03 for broken Mesos
  ];

in
  # Running against custom version of nixpkgs or pkgs would be as simple as running `nix-shell --arg nixpkgs /absolute/path/to/nixpkgs`
  # See https://garbas.si/2015/reproducible-development-environments.html
  { nixpkgs ? import <nixpkgs>, pkgs ? nixpkgs { inherit overlays; } }:

let
  # Python from Spark
  sparkPython = builtins.head (builtins.filter (pkg: builtins.hasAttr "pname" pkg && pkg.pname == "python") pkgs.spark.buildInputs);
  env = sparkPython.withPackages(ps: with ps; [ virtualenv pip ]);

in pkgs.stdenv.mkDerivation rec {

  inherit name env;

  buildInputs = with pkgs; [
    env
    # build the application
    jdk gradle maven
    # build Docker image
    docker docker-compose
    # control API and fetch deps
    curl p7zip
  ];

  shellHook = ''
    # disable custom Java options imported from the system environment
    unset _JAVA_OPTIONS
    # unset SOURCE_DATE_EPOCH to prevent "ZIP does not support timestamps before 1980" when using pythonPackages.wheel, see https://github.com/NixOS/nixpkgs/blob/master/doc/languages-frameworks/python.section.md#python-setuppy-bdist_wheel-cannot-create-whl
    unset SOURCE_DATE_EPOCH
    # to prevent UnicodeEncodeError: 'ascii' codec can't encode character u'...
    export PYTHONIOENCODING=utf8
    # versions
    echo "# SOFTWARE:" ${builtins.concatStringsSep ", " (map (x: x.name) buildInputs)}
  '';

}
