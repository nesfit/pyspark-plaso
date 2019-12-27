#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the PE file parser."""

from __future__ import unicode_literals

import plaso.tarzan.mediator.print_mediator
from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import resolver as path_spec_resolver
from plaso.parsers import pe
from plaso.parsers import sqlite
from plaso.parsers import winreg
from plaso.tarzan.file import file


def run_PE(mediator):
    f = file.LocalFileObject()
    f.open("test_data/test_pe.exe")

    parser = pe.PEParser()
    parser.Parse(mediator, f);  # file object parser

    f.close()


def run_SQLite(mediator):
    pathSpec = path_spec_factory.Factory.NewPathSpec(definitions.TYPE_INDICATOR_OS, location="test_data/History")
    file_entry = path_spec_resolver.Resolver.OpenFileEntry(pathSpec)

    mediator.SetFileEntry(file_entry);

    parser = sqlite.SQLiteParser()
    parser.Parse(mediator);


def run_WinReg(mediator):
    f = file.LocalFileObject()
    f.open("test_data/NTUSER.DAT")

    parser = winreg.WinRegistryParser()
    parser.Parse(mediator, f)  # file object parser

    f.close()


# ====================================


m = plaso.tarzan.mediator.print_mediator.PrintMediator()
# run_PE(m)
# run_SQLite(m)
run_WinReg(m)
