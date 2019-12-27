# -*- coding: utf-8 -*-

# import all extractors to register them in a manager
import pe
import sqlite
# TODO: modify _DEFINITION_FILES_PATH in plaso/parsers/winreg_plugins/dtfabric_plugin.py to use a really absolute path
# (currently, the path is "./site-packages.zip/plaso/parsers/winreg_plugins" not
# "/tmp/spark-9ab37c0a-fc38-451b-ab67-130e16d4ff7d/userFiles-1fb1db76-f20c-434e-9eb5-0e97d8dee7a4/site-packages.zip/..."
#import winreg
