# Scenario "stop": the router's stop path on a running worker (stop_run), how long the end state stays
# observable, resume, and the queue-cancel path (reopen on a to-do task).
add_task add br-1
K=$(key_of add)
cap start herdr-task start "$K" --folder ~/repo --space demo --json
T=$(jq -r .terminal "$O/start.out"); W=$(jq -r .worktree "$O/start.out")
wait_commit "$W"; sleep 1
cap show_before herdr-task show "$K" --folder ~/repo --json
# 3.2 only has `herdr-task stop` (the person's Stop: an Esc-like pause, not termination); 3.1 answers with usage
cap task_stop herdr-task stop "$K" --folder ~/repo --json
cap show_after_task_stop herdr-task show "$K" --folder ~/repo --json
cap get_after_task_stop env HC_SESSION=$S hc get "$T" --json
# stop_run: kill the live terminals show lists (raw output)
cap kill env HC_SESSION=$S hc kill "$T" --json
start=$(date +%s)
for at in 0 5 30 120 300; do
  while [ $(( $(date +%s) - start )) -lt $at ]; do sleep 1; done
  cap "get_t${at}" env HC_SESSION=$S hc get "$T" --json
  cap "ls_all_t${at}" env HC_SESSION=$S hc ls --all --label "herdr.task=$K" --json
  cap "ls_live_t${at}" env HC_SESSION=$S hc ls --label "herdr.task=$K" --json
  cap "show_t${at}" herdr-task show "$K" --folder ~/repo --json
done
cap kill_again env HC_SESSION=$S hc kill "$T" --json
cap server_restart env HC_SESSION=$S hc server restart --json
cap get_after_restart env HC_SESSION=$S hc get "$T" --json
cap ls_all_after_restart env HC_SESSION=$S hc ls --all --json
cap resume herdr-task resume "$K" --folder ~/repo --space demo --json
cap show_after_resume herdr-task show "$K" --folder ~/repo --json
cap rm env HC_SESSION=$S hc rm "$T" --json
cap get_after_rm env HC_SESSION=$S hc get "$T" --json
# queue cancel: a task that was never started
add_task add_todo br-2
cap reopen_todo herdr-task reopen "$(key_of add_todo)" --folder ~/repo --json
finish
