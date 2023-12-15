#!/bin/sh

export PYTHONPATH="${PYTHONPATH}:`pwd`"
# take argument -n into num_players, with default value 11
num_players=11
while getopts n: option
do
case "${option}"
in
n) num_players=${OPTARG};;
esac
done
python base/main_player.py -g ${1+"$@"}&
sleep 1
i=2
while [ $i -le $num_players ] ; do
    python base/main_player.py ${1+"$@"}&
    sleep 0.2

  i=`expr $i + 1`
done

sleep 2
python base/main_coach.py ${1+"$@"}
