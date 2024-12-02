#!/bin/bash

# export PYTHONPATH="${PYTHONPATH}:`pwd`"

python_env=.venv/bin/activate
source $python_env

# Set the options, all the options are passed as environment variables
options=$@

echo "Options: $options"

# Function to handle termination
cleanup() {
  echo "Terminating all start_agent.py processes..."
  for pid in "${pids[@]}"; do
    kill $pid
  done
  exit 0
}

# Trap SIGTERM and SIGINT signals
trap cleanup SIGTERM SIGINT

run_command="python3 main.py"

# list of pids
pids=()

# Example of running the command and storing the PID
# Run the command
$run_command $options --goalie &
pids+=($!)

sleep 1

i=2
while [ $i -le 11 ] ; do
  $run_command $options --player &
  pids+=($!)

  sleep 0.2

  i=`expr $i + 1`
done

sleep 2
$run_command $options --coach &
pids+=($!)

# Wait for all pids
wait "${pids[@]}"