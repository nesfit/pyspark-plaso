# -*- coding: utf-8 -*-


class CustomPipPackageDir:
    """
    Python packages install class (not in a shell) to be executable by PySpark workers by
    pyspark-driver:
      sparkContext.addPyFile("custom_pip_package_dir.py")
    pyspark-worker:
      from custom_pip_package_dir import CustomPipPackageDir
      cppd = CustomPipPackageDir()
      cppd.install("future")
    """

    def __init__(self, package_dir=None):
        # type: (str) -> None
        """
        Initializes the Python package install class.
        :param package_dir: a directory where to load packages from on the installation
        """
        self.package_dir = package_dir
        self.make_package_dir()
        self.register_package_dir()

    def make_package_dir(self):
        # type: () -> None
        """
        Create a custom module storage.
        """
        if self.package_dir is not None:
            import os
            try:
                os.makedirs(self.package_dir)
            except OSError as e:
                import errno
                if e.errno != errno.EEXIST:
                    raise

    def register_package_dir(self):
        """
        Register the package directory as a custom module storage.
        """
        if self.package_dir is not None:
            import sys
            if self.package_dir not in sys.path:
                sys.path.insert(1, self.package_dir)

    def pip_install(self, packages):
        # type: (list) -> str
        """
        Install the packages by external call of pip.
        :param packages: a list of packages to install
        :return: the output buffer of the pip
        """
        import subprocess
        import sys
        args = [sys.executable,
                "-W", "ignore",
                "-m", "pip",
                "install",
                "--no-cache-dir"]
        try:
            return subprocess.check_output(args +
                                           (["--target=%s" % self.package_dir] if self.package_dir is not None else [
                                               "--user", "--install-option=--prefix="]) +
                                           packages, stderr=subprocess.STDOUT, universal_newlines=True)
        except subprocess.CalledProcessError as e:
            return e.output

    @staticmethod
    def check_installed_package(package):
        # type: (str) -> bool
        """
        Check if the package is available.
        :param package: the package to check
        :return: True if the package is available, False otherwise
        """
        import pkgutil
        package_name = package.replace('python-', '').replace('py-', '')
        return pkgutil.find_loader(package_name)

    def install(self, packages):
        # type: (list) -> str
        """
        Install the packages by external call of pip if they are not already installed.
        :param packages: a list of packages to install
        :return: the output buffer of the pip
        """
        # make an array of the packages while skipping empty lines
        packages_list = filter(lambda x: x, packages.splitlines()) if isinstance(packages, str) else packages
        # skip already installed packages (without python- and py- prefixes)
        missing_packages = filter(lambda x: not self.check_installed_package(x), packages_list)
        # call pip
        return self.pip_install(missing_packages) if missing_packages else None
