#!/bin/sh

export PYTHONPATH="${PYTHONPATH}:`pwd`"

#./base/main_player.py g &

i=1
while [ $i -le 11 ] ; do
    ./base/main_player.py &
    sleep 0.01

  i=`expr $i + 1`
done
