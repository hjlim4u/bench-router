# Scenario "session": which core a call reaches (Q1, Q2). Three cores: default, shepherdr, other.
for s in default shepherdr other; do
  cap "core_json_before_$s" cat ~/.local/state/herdr-core/$s/core.json   # passive: no core is started
  cap "status_$s" env HC_SESSION=$s hc server status --json             # active: starts the core when absent
  cap "core_json_after_$s" cat ~/.local/state/herdr-core/$s/core.json
done
sock() { echo ~/.local/state/herdr-core/$1/$1.sock; }
# hc itself: HC_SOCKET vs HC_SESSION vs HC_TERMINAL_SOCKET
cap hc_session_default_socket_other env HC_SESSION=default HC_SOCKET=$(sock other) hc server status --json
cap hc_session_other_socket_default env HC_SESSION=other HC_SOCKET=$(sock default) hc server status --json
cap hc_terminal_socket_other_only env HC_TERMINAL_SOCKET=$(sock other) hc server status --json
cap hc_socket_missing env HC_SOCKET=/tmp/nope.sock hc ls --json

# herdr-task under each environment the router might hand it: add + start, then where the terminal landed
i=0
variant() {
  name=$1; shift; i=$((i+1))
  add_task "add_$name" "br-v$i" "$@"
  k=$(key_of "add_$name")
  [ -n "$k" ] || k="repo#$i"
  cap "start_$name" env "$@" herdr-task start "$k" --folder ~/repo --space demo --json
  for s in default shepherdr other; do
    cap "ls_${name}_in_$s" env HC_SESSION=$s hc ls --label "herdr.task=$k" --json
  done
}
variant unset
variant session_default HC_SESSION=default
variant session_shepherdr HC_SESSION=shepherdr
variant session_other HC_SESSION=other
variant session_other_named HC_SESSION=other SHEPHERDR_SESSION=other
variant socket_default HC_SOCKET=$(sock default)
variant socket_shepherdr HC_SOCKET=$(sock shepherdr)
variant socket_other HC_SOCKET=$(sock other)
variant session_default_socket_shepherdr HC_SESSION=default HC_SOCKET=$(sock shepherdr)
variant foreign_terminal HC_TERMINAL_SOCKET=$(sock other) HC_TERMINAL_ID=t1
cat ~/agent-env-*.txt > "$O/agent_env.txt" 2>/dev/null
finish
