# Prelude for every scenario: runs INSIDE a throwaway shepherdr-env container only (see capture.sh).
# stdout carries only the final tar of /tmp/out; everything else goes to stderr.
set -u
exec 3>&1 1>&2
O=/tmp/out; mkdir -p "$O"
TAG=$(git -C ~/shepherdr describe --tags 2>/dev/null)
case "$TAG" in v3.1.*) S=default ;; *) S=shepherdr ;; esac  # the core session herdr-task itself uses (see shepherdr-spike.md)
RID=00000000-0000-4000-8000-000000000001

# cap NAME CMD...: raw stdout/stderr/exit code of one command, plus an index line
cap() {
  n=$1; shift
  "$@" >"$O/$n.out" 2>"$O/$n.err"; rc=$?
  echo "$rc" >"$O/$n.rc"
  printf '%s\t%s\t%s\n' "$n" "$rc" "$(printf '%q ' "$@")" >>"$O/index.tsv"
  echo "[$n] rc=$rc" >&2
  return 0
}
finish() { tar -C "$O" -cf - . >&3; }

# Synthetic agent: answers Shepherdr's `claude auth status` probe, then commits one file and idles.
mkdir -p ~/.local/bin
cat > ~/.local/bin/claude <<'EOF'
#!/bin/sh
case "${1:-}" in auth|--version|-v) echo '{"loggedIn": true}'; exit 0 ;; esac
env | grep -E '^(HC_|HERDR|SHEPHERDR)' | sort > "$HOME/agent-env-$(basename "$PWD").txt"
echo hello > agent.txt && git add agent.txt && git commit -qm "agent: write agent.txt"
echo "synthetic agent idle"
exec sleep 3600
EOF
chmod +x ~/.local/bin/claude
cp ~/.local/bin/claude ~/.local/bin/codex

mkdir -p ~/repo && cd ~/repo && git init -q && echo a > a && git add a && git commit -qm init
printf 'Write agent.txt and commit it.\n' > /tmp/input.txt

# add_task NAME TITLE [ENV...]: the router's exact add argv (herdr.py execute) with branch br/<TITLE minus "br-">
add_task() {
  n=$1 t=$2; shift 2
  cap "$n" env "$@" herdr-task add "$t" --prompt-file /tmp/input.txt --folder ~/repo --base main --branch "br/${t#br-}" \
    --agent claude --model default --worktree --set review=off --set "merge=ask me first" --set proof=off --json
}
key_of() { jq -r '.key // empty' "$O/$1.out" 2>/dev/null; }
# wait_commit WORKTREE: until the synthetic agent's commit is there (max 30s)
wait_commit() { for _ in $(seq 60); do git -C "$1" log -1 --format=%s 2>/dev/null | grep -q '^agent:' && return 0; sleep 0.5; done; return 1; }
