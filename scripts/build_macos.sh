#!/bin/bash

# This script builds a standalone macOS application bundle of Timesheet
# Generator using Nuitka.
# The PROGRAM variable MUST match the name of the entry Python script
# (without the .py extension). This will be the name of the executable.

PROGRAM="main"
ASSETS_PATH="assets"
ICON_PATH="assets/icons/app-icon.icns"

nuitka --standalone \
       --enable-plugin=pyside6 \
       --static-libpython=no \
       --macos-create-app-bundle \
       --include-data-dir=$ASSETS_PATH=assets \
       --macos-app-icon=$ICON_PATH \
       $PROGRAM.py
