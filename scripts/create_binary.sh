#!/bin/bash


# show error if binary directory already exists

if [ -d "binary" ]; then
  echo "binary directory already exists. Please remove it before running this script."
  exit 1
fi

# create binary directory

mkdir binary

# create binary

nuitka --standalone --onefile --output-dir=binary ../main_player.py
nuitka --standalone --onefile --output-dir=binary ../main_coach.py

# remove build directory

rm -rf binary/main_player.build
rm -rf binary/main_player.dist
rm -rf binary/main_player.onefile-build

rm -rf binary/main_coach.build
rm -rf binary/main_coach.dist
rm -rf binary/main_coach.onefile-build

# # copy start to binary directory

cp start binary/start
cp startAll binary/startAll