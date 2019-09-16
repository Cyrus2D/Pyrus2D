#!/bin/sh

python3 clean.py
python3 compile.py build_ext --inplace

cp start.sh binary/
cp base/main_player.py  binary/base/
cp base/formation_dt/ binary/base/ -r
rm binary/base/main_player.cpython-36m-x86_64-linux-gnu.so


python3 clean.py c-files