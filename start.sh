#!/bin/sh

# export PYTHONPATH="${PYTHONPATH}:`pwd`"

#./base/main_player.py g &

i=1
while [ $i -le 11 ] ; do
    python main.py > "player-$i-log.txt" 2> "player-$i-error.txt" &
    sleep 0.01

  i=`expr $i + 1`
done

sleep 5
python coach_main.py > "coach-log.txt" 2> "coach-error.txt"
