#!/bin/sh

python3 compile.py build_ext --inplace
python3 clean.py c-files