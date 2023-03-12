#!/bin/sh

export PYTHONPATH="${PYTHONPATH}:`pwd`"

python base/main_player.py 1 g > "player-1-log.txt" 2> "player-1-error.txt" &
sleep 1
i=2
while [ $i -le 11 ] ; do
    python base/main_player.py $i > "player-$i-log.txt" 2> "player-$i-error.txt" &
    sleep 0.2

  i=`expr $i + 1`
done

sleep 2
python coach_main.py > "coach-log.txt" 2> "coach-error.txt"
