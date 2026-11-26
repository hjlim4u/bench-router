# Scenario "kill_only": the board's view after the router kills a running worker (no `herdr-task stop` first),
# and the card after a start the guard refused.
add_task add br-1
K=$(key_of add)
cap start herdr-task start "$K" --folder ~/repo --space demo --json
T=$(jq -r .terminal "$O/start.out"); W=$(jq -r .worktree "$O/start.out")
wait_commit "$W"; sleep 1
cap kill env HC_SESSION=$S hc kill "$T" --json
start=$(date +%s)
for at in 0 2 5 15; do
  while [ $(( $(date +%s) - start )) -lt $at ]; do sleep 1; done
  cap "show_t${at}" herdr-task show "$K" --folder ~/repo --json
done
add_task add_refused br-2
cap start_refused env HC_SESSION=other herdr-task start "$(key_of add_refused)" --folder ~/repo --space demo --json
cap show_refused herdr-task show "$(key_of add_refused)" --folder ~/repo --json
cap git_branches git -C ~/repo branch --list
finish
