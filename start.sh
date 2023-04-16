#!/bin/sh

export PYTHONPATH="${PYTHONPATH}:`pwd`"

python base/main_player.py -g ${1+"$@"}&
sleep 1
i=2
while [ $i -le 11 ] ; do
    python base/main_player.py ${1+"$@"}&
    sleep 0.2

  i=`expr $i + 1`
done

sleep 2
python base/main_coach.py ${1+"$@"}
