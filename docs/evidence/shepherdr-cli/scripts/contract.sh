# Scenario "contract": every herdr-task/hc call the router makes on a successful run, in order.
# Run: capture.sh (prepends lib.sh). Core session $S is the one herdr-task uses for this tag.
cap task_version herdr-task --version
cap hc_version hc --version
cap where herdr-task where --json
add_task add_router_title "br-$RID"                 # the router's literal title (39 chars)
add_task add br-1                                    # short title, used for the rest of the scenario
cap add_plain herdr-task add plain-title --prompt x --folder ~/repo   # without --json
cap list herdr-task list --json
K=$(key_of add)
cap start herdr-task start "$K" --folder ~/repo --space demo --json
T=$(jq -r .terminal "$O/start.out"); W=$(jq -r .worktree "$O/start.out")
wait_commit "$W"; sleep 1
cap show herdr-task show "$K" --folder ~/repo --json
# the router's own hc calls run with HC_SESSION=<receipt's core_session>, "default" from a plain shell
for s in default shepherdr; do
  cap "ls_label_$s" env HC_SESSION=$s hc ls --label "herdr.task=$K" --json
  cap "get_$s" env HC_SESSION=$s hc get "$T" --json
done
cap run_bg env HC_SESSION=$S hc run --bg --rm --json --no-parent --label "bench-router.watch=$RID" -- env X=1 sleep 600
cap ls_watch env HC_SESSION=$S hc ls --label "bench-router.watch=$RID" --json
cap send env HC_SESSION=$S hc send "$T" "message from the router" --json
cap ready herdr-task ready "$K" --folder ~/repo --summary "Results validated by bench-router" --json
cap show_after_ready herdr-task show "$K" --folder ~/repo --json
cap ls_label_after_ready env HC_SESSION=$S hc ls --label "herdr.task=$K" --json
# release(): kill every terminal carrying the task label
cap kill env HC_SESSION=$S hc kill "$T" --json
cap get_after_kill env HC_SESSION=$S hc get "$T" --json
cap ls_all_after_kill env HC_SESSION=$S hc ls --all --json
cap show_after_kill herdr-task show "$K" --folder ~/repo --json
cat ~/agent-env-*.txt > "$O/agent_env.txt" 2>/dev/null
finish
