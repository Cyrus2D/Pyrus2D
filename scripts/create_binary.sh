#!/bin/bash


# show error if binary directory already exists

if [ -d "binary" ]; then
  echo "binary directory already exists. Please remove it before running this script."
  exit 1
fi

# create binary directory

mkdir binary

# create binary

nuitka --standalone --onefile --output-dir=binary ../main.py

# remove build directory

rm -rf binary/main.build
rm -rf binary/main.dist
rm -rf binary/main.onefile-build

# # copy start to binary directory

cp start binary/start
cp startAll binary/startAll

# make base/formation_dt

mkdir binary/base
cp -r ../base/formation_dt binary/base/formation_dt