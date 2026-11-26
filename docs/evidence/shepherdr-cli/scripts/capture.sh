#!/bin/sh
# Host driver: run each scenario in its own throwaway shepherdr-env container and unpack its captures.
# Nothing is mounted; the container prints a tar of /tmp/out.
# Usage: capture.sh [TAG...] (default both); SCENARIOS="stop" capture.sh to run a subset.
#   docs/evidence/shepherdr-cli/<TAG>/<scenario>/{NAME.out,NAME.err,NAME.rc,index.tsv,agent_env.txt}
set -eu
here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$here/../../../.." && pwd)
for tag in ${*:-v3.1.26 v3.2.19}; do
  for sc in ${SCENARIOS:-contract stop session kill_only}; do
    out="$here/../$tag/$sc"; rm -rf "$out"; mkdir -p "$out"
    cat "$here/lib.sh" "$here/$sc.sh" | "$root/eval/shepherdr-env/run.sh" shell "$tag" bash -s 2>"$out/run.log" \
      | tar -x -C "$out"
    echo "$tag/$sc: $(wc -l < "$out/index.tsv") commands"
  done
done
