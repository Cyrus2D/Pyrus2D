#!/bin/sh

i=1
while [ $i -le 11 ] ; do
    ./base/main_player.py &

  i=`expr $i + 1`
done