# this Nix script is utilized to initialize the environment including required dependencies

let
  # Enable overlays (refer to the package being modified via `super` and to packages it uses via `cls`)
  # See https://gist.github.com/mayhewluke/e2f67c65c2e135f16a8e
  # NixOS v19.03: Spark v2.2.1 using Scala v2.11.8, OpenJDK 64-Bit v1.8.0_212
  # NixOS v19.09: Spark v2.4.3 using Scala v2.11.12, OpenJDK 64-Bit v1.8.0_212
  sparkOverlay = cls: super: {
    spark = (super.spark.override {
      version = "2.4.3";
    }).overrideAttrs(oldAttrs: rec {
      src = super.fetchzip {
        sha256 = "1dvvr1q3dz961bl7qigxngrp4ssrbll3g1s6nkra6gyr83pis96c";
        url = "mirror://apache/spark/${oldAttrs.name}/${oldAttrs.name}-bin-without-hadoop.tgz";
      };
    });
  };
  # NixOS v19.03: Hadoop v2.7.7
  hadoopOverlay = cls: super: {
    hadoop = super.hadoop_3_1;
  };
  overlays = [
    #sparkOverlay	# no need in NixOS v19.09
    hadoopOverlay
  ];

in
  # Running against custom version of nixpkgs or pkgs would be as simple as running `nix-shell --arg nixpkgs /absolute/path/to/nixpkgs`
  # See https://garbas.si/2015/reproducible-development-environments.html
  { nixpkgs ? import <nixpkgs>, pkgs ? nixpkgs { inherit overlays; } }:

let
  # Python from Spark
  sparkPython = builtins.head (builtins.filter (pkg: builtins.hasAttr "pname" pkg && pkg.pname == "python") pkgs.spark.buildInputs);
  env = sparkPython.withPackages(ps: with ps; [ virtualenv pip ]);

in pkgs.stdenv.mkDerivation {

  name = "spark-python-env";
  inherit env;

  buildInputs = [ pkgs.hadoop pkgs.spark env pkgs.jdk pkgs.gradle pkgs.maven ];

  shellHook = ''
    # disable custom Java options imported from the system environment
    unset _JAVA_OPTIONS
    # unset SOURCE_DATE_EPOCH to prevent "ZIP does not support timestamps before 1980" when using pythonPackages.wheel, see https://github.com/NixOS/nixpkgs/blob/master/doc/languages-frameworks/python.section.md#python-setuppy-bdist_wheel-cannot-create-whl
    unset SOURCE_DATE_EPOCH
    # set the environment
    source ./environment.sh
    # versions
    echo "*** HADOOP VERSION ***"
    hadoop version
    echo "*** SPARK VERSION ***"
    spark-submit --version
    echo "*** PYTHON VERSION ***"
    python --version
    echo "***"
  '';

  # MAY BE REQUIRED to set system-wide: Fixes for applications with static paths to core utilities
  # config.system.activationScripts.binls = {
  #   text = ''
  #     # Create the /bin/ls symlink; otherwise some unpatched things won't work.
  #     # E.g., Hive or PySpark, check by $ echo 'spark.sql("show databases").show()' | ( cd /tmp && nix-shell --packages spark --command spark-shell )
  #     mkdir -m 0755 -p /bin
  #     ln -sfn "${pkgs.coreutils}/bin/ls" /bin/.ls.tmp
  #     mv /bin/.ls.tmp /bin/ls # atomically replace /bin/ls
  #   '';
  #   deps = [];
  # };

}
