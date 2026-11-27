#!/bin/bash
# Host helper for the Shepherdr 3.1 -> 3.2 switch (docs/shepherdr-switch.md). Run it on the host being switched.
#   check   read-only: what still blocks the switch (exit 1 if anything does)
#   backup  quiesced archive of what the 3.2 installer changes (stops shepherdr.service; run after `check` passes)
#   smoke   after the switch: one headless bench-router run through Shepherdr in a throwaway repo, then cleanup
# Env: B (backup dir, default ~/.local/backups/shepherdr), SHEPHERDR_SRC (default: the installed record's source,
#      else ~/shepherdr), TARGET (default v3.2.19), SMOKE_MODEL / SMOKE_EFFORT (default claude-haiku-5-5 / low; must
#      be a profile in profiles.toml), BENCH_ROUTER_SPACE (default bench-router).
# It reads the default folders (~/.config, ~/.local/share, ~/.local/state, ~/.herdr): `backup` refuses when
# XDG_*_HOME, HERDR_APP_HOME or SHEPHERDR_HOME point elsewhere.
set -u
B=${B:-$HOME/.local/backups/shepherdr}
TARGET=${TARGET:-v3.2.19}
DATA=${XDG_DATA_HOME:-$HOME/.local/share}/shepherdr
STATE=${XDG_STATE_HOME:-$HOME/.local/state}

src() {
  [ -n "${SHEPHERDR_SRC:-}" ] && { echo "$SHEPHERDR_SRC"; return; }
  python3 - "$DATA" <<'E'
import json, os, sys
for p in (f"{sys.argv[1]}/installed.json", os.path.expanduser("~/.config/herdr-app/data/shepherdr/installed.json")):
    try:
        s = json.load(open(p)).get("source")
    except (OSError, ValueError):
        continue
    if s and os.path.isdir(s):
        print(s); break
else:
    print(os.path.expanduser("~/shepherdr"))
E
}

check() {
  python3 - "$DATA" "$(src)" "$TARGET" "${BENCH_ROUTER_COORDINATION_DIR:-$STATE/bench-router/coordination}" <<'E'
import glob, json, os, shutil, subprocess, sys
data, src, target, coordination = sys.argv[1:]
home = os.path.expanduser("~")
block, notes = [], []
def load(p):
    try: return json.load(open(p))
    except (OSError, ValueError): return None
def git(cwd, *a):
    p = subprocess.run(["git", "-C", cwd, *a], capture_output=True, text=True)
    return p.stdout.strip() if p.returncode == 0 else None
ver = next((d.get("version") for d in map(load, (f"{data}/installed.json", f"{home}/.config/herdr-app/data/shepherdr/installed.json")) if d), None)
print("installed:", ver or "no install record found")
legacy = f"{home}/.herdr/tasks"
try: layout = open(f"{data}/LAYOUT").read().strip()
except OSError: layout = "1"
print("data layout:", layout, "(data in ~/.herdr; the 3.2 install moves it and leaves links there)" if layout == "1"
      else "(Shepherdr's own folders; ~/.herdr holds links)")
print(f"source {src}:", f"has {target}" if git(src, "tag", "-l", target) else f"no {target} tag (git -C {src} fetch --tags)")
print("hc:", shutil.which("hc") or "MISSING", "| bun:", shutil.which("bun") or "missing (the 3.2 service and web app need it)")
if not shutil.which("hc"): block.append("hc (herdr-core 0.1.17 or newer) is not on the PATH")
# processes by cwd, to tell a live agent from a card nobody works on
cwds = {}
for p in glob.glob("/proc/[0-9]*/cwd"):
    try: cwds.setdefault(os.readlink(p), []).append(p.split("/")[2])
    except OSError: pass
seen = set()
for folder in (f"{data}/tasks", legacy):
    if os.path.realpath(folder) in seen: continue
    seen.add(os.path.realpath(folder))
    for path in sorted(glob.glob(f"{folder}/*.json")):
        d = load(path)
        if not isinstance(d, dict):
            block.append(f"unreadable task list {path}"); continue
        for t in d.get("tasks") or []:
            name, wt = f"{d.get('prefix') or 'TASK'}-{t.get('id')} in {d.get('folder')}", t.get("worktree")
            real = os.path.realpath(wt) if wt else None
            if t.get("state") == "running" and not t.get("archived"):
                live = sorted({pid for c, pids in cwds.items() if real and (c == real or c.startswith(real + "/")) for pid in pids})
                block.append(f"running card {name}: " + (f"live processes {','.join(live[:5])}" if live else
                             "no worktree recorded: check its agent by hand" if not wt else
                             "worktree is gone (stale: settle it)" if not os.path.isdir(real) else "no live process (stale: settle it)"))
            elif t.get("state") == "done" and real and os.path.isdir(real):
                dirty = git(real, "status", "--porcelain")
                if dirty:
                    notes.append(f"done card {name} has {len(dirty.splitlines())} uncommitted paths in {wt}")
for f in glob.glob(f"{coordination}/*.json"):
    d = load(f) or {}
    if d.get("active") is True:
        ref = d.get("reference") or {}
        block.append(f"active admission: run {ref.get('run_id')} ({d.get('status')}) cwd {ref.get('cwd')}")
for pid in subprocess.run(["pgrep", "-u", str(os.getuid()), "-x", "herdr-app"], capture_output=True, text=True).stdout.split():
    try: st = open(f"/proc/{pid}/stat").read().rsplit(")", 1)[1].split()[0]
    except OSError: continue
    if st != "Z":
        notes.append(f"Herdr app pid {pid} is open (state {st}" + (": stopped, send CONT before TERM" if st == "T" else "") + "): close it before `backup`")
for n in notes: print("note:", n)
print("BLOCKERS:" if block else "no blockers on this machine (the installer also checks linked machines: read its --dry-run)")
for b in block: print("  -", b)
sys.exit(1 if block else 0)
E
}

backup() {
  for v in XDG_CONFIG_HOME:.config XDG_DATA_HOME:.local/share XDG_STATE_HOME:.local/state; do
    n=${v%%:*}; [ -z "${!n:-}" ] || [ "${!n}" = "$HOME/${v#*:}" ] || { echo "$n is not the default: archive those folders by hand"; exit 1; }
  done
  [ -z "${HERDR_APP_HOME:-}${SHEPHERDR_HOME:-}" ] || { echo "HERDR_APP_HOME/SHEPHERDR_HOME is set: archive those folders by hand"; exit 1; }
  check >/dev/null || { echo "check reports blockers; run '$0 check'"; exit 1; }
  pgrep -u "$(id -u)" -x herdr-app >/dev/null && { echo "close the Herdr app first ('$0 check' shows its pid)"; exit 1; }
  systemctl --user stop shepherdr.service 2>/dev/null
  mkdir -p -m 700 "$B"
  [ -e "$B/shepherdr-3.1.tar" ] && mv "$B/shepherdr-3.1.tar" "$B/shepherdr-3.1.$(date +%Y%m%d-%H%M%S).tar"
  git -C "$(src)" rev-parse HEAD > "$B/shepherdr-clone-HEAD.txt"
  ls -l ~/.local/bin > "$B/bin-links.txt"
  u=${HOME#/}
  paths=()
  for p in .config/herdr-app .config/shepherdr .config/systemd/user/shepherdr.service \
           .config/systemd/user/default.target.wants/shepherdr.service .claude/settings.json .codex/hooks.json \
           .local/share/shepherdr .local/state/shepherdr .herdr .local/bin/herdr-task .local/bin/shepherdr \
           .local/bin/herdr-secret .local/bin/herdr-browser .local/bin/herdr-artifact; do
    { [ -e "$HOME/$p" ] || [ -L "$HOME/$p" ]; } && paths+=("$u/$p")
  done
  (cd / && tar --create --preserve-permissions --xattrs --acls --numeric-owner \
     --exclude="$u/.herdr/worktrees" --exclude="$u/.local/share/shepherdr/worktrees" \
     -f "$B/shepherdr-3.1.tar" "${paths[@]}") || { echo "tar failed"; exit 1; }
  (cd "$B" && sha256sum shepherdr-3.1.tar > shepherdr-3.1.tar.sha256 && chmod 600 shepherdr-3.1.tar* shepherdr-clone-HEAD.txt bin-links.txt)
  echo "archive $B/shepherdr-3.1.tar: $(tar -tf "$B/shepherdr-3.1.tar" | wc -l) entries (it holds secrets: keep it on this host)"
  echo "shepherdr.service is stopped: the 3.2 install starts it; to stay on 3.1, systemctl --user start shepherdr.service"
}

smoke() {
  local R T profile ok card wt
  local space=${BENCH_ROUTER_SPACE:-${BENCH_ROUTER_HERDR_SESSION:-bench-router}}
  R=$(mktemp -d) T=$(mktemp -d)
  # the identity is repo-local so the agent's commit works on a host without a global git identity
  git -C "$R" init -q -b main && git -C "$R" config user.name smoke && git -C "$R" config user.email smoke@example.invalid \
    && echo smoke > "$R/README.md" && git -C "$R" add . && git -C "$R" commit -qm init || { echo "cannot create $R"; exit 1; }
  python3 - "$R" "$T" "${SMOKE_MODEL:-claude-haiku-5-5}" "${SMOKE_EFFORT:-low}" <<'E'
import json, sys, uuid
repo, tmp, model, effort = sys.argv[1:]
json.dump({"schema_version": "1.0", "task_id": uuid.uuid4().hex, "round": 1, "summary": "Shepherdr switch smoke test",
           "execution": "headless", "cwd": repo,
           "prompt": "Create SMOKE.md containing the line 'shepherdr smoke ok', commit it as 'smoke: add SMOKE.md', and finish.",
           "profile_filter": {"include": {"model": [model], "effort": [effort]}}}, open(f"{tmp}/task.json", "w"))
E
  bench-router --runner herdr --herdr-space "$space" evaluate --preflight --format 3 --task "$T/task.json" --host claude > "$T/eval.json" 2> "$T/eval.err"
  profile=$(python3 - "$T/eval.json" <<'E'
import json, sys
d = json.load(open(sys.argv[1])); rec = d.get("recommendation") or {}
assert d.get("status") == "ok" and rec.get("status") == "selected", (d.get("status"), rec)
print(rec["profile"], rec["policy"]["id"], rec["policy"]["version"])
E
  ) || { echo "evaluate did not select one profile (is SMOKE_MODEL/SMOKE_EFFORT in profiles.toml, with quota?): see $T/eval.json, $T/eval.err"; exit 1; }
  set -- $profile
  bench-router select --assessment "$T/eval.json" --profile "$1" --policy-id "$2" --policy-version "$3" \
    --reason "switch smoke test" | python3 -c "import json,sys;json.dump(json.load(sys.stdin)['selection'],open(sys.argv[1],'w'))" "$T/sel.json"
  bench-router --runner herdr --herdr-space "$space" route --task "$T/task.json" --selection "$T/sel.json" --wait-ms 180000 > "$T/route.json" 2> "$T/route.err"
  python3 - "$T/route.json" "${BENCH_ROUTER_COORDINATION_DIR:-$STATE/bench-router/coordination}" <<'E'
import glob, json, os, sys
try: d = json.load(open(sys.argv[1]))
except ValueError: sys.exit("route printed no JSON: see " + sys.argv[1][:-4] + "err")
adm = [json.load(open(f)) for f in glob.glob(f"{sys.argv[2]}/*.json")]
adm = [a for a in adm if (a.get("reference") or {}).get("run_id") == d.get("run_id")]
b = json.load(open(d["receipt_path"])).get("project_binding", {}) if d.get("receipt_path") else {}
checks = {"result collected": (d.get("status"), d.get("task_outcome")) == ("completed", "success"),
          "Ready handed off": (d.get("ready") or {}).get("state") == "ready",
          "terminals released": bool((d.get("release") or {}).get("terminals")),
          "admission released": bool(adm) and adm[0].get("active") is False,
          "bound to the 3.2 session and a core id": bool(b.get("core_id")) and b.get("session") == (os.environ.get("SHEPHERDR_SESSION") or "shepherdr")}
for k, v in checks.items(): print(("PASS " if v else "FAIL ") + k)
print("run", d.get("run_id"), "card", d.get("thread_id"), "status", d.get("status"), "session", b.get("session"))
open(sys.argv[1] + ".card", "w").write(f"{d.get('thread_id') or ''}\t{d.get('worktree') or ''}")
sys.exit(0 if all(checks.values()) else 1)
E
  ok=$?
  if [ "$ok" = 0 ]; then
    IFS=$'\t' read -r card wt < "$T/route.json.card"
    [ -n "$card" ] && herdr-task rm "${card##*#}" --folder "$R" >/dev/null
    [ -n "$wt" ] && git -C "$R" worktree remove --force "$wt" && rmdir "$(dirname "$wt")" 2>/dev/null
    # herdr-task rm leaves the repo's empty card store behind
    python3 - "$R" "$DATA/tasks" "$HOME/.herdr/tasks" <<'E'
import glob, json, os, sys
for p in {os.path.realpath(p) for folder in sys.argv[2:] for p in glob.glob(f"{folder}/*.json")}:
    d = json.load(open(p))
    if d.get("folder") == sys.argv[1] and not d.get("tasks"): os.remove(p)
E
    rm -rf "$R" "$T"
    echo "smoke passed; card, worktree and throwaway repo removed"
  else
    echo "smoke FAILED: kept $R (repo, receipts) and $T (route.json, route.err)."
    echo "If the run only timed out: bench-router collect --run-id RUN --cwd $R --wait-ms 120000"
    exit 1
  fi
}

case "${1:-}" in
  check) check ;;
  backup) backup ;;
  smoke) smoke ;;
  *) sed -n '2,10p' "$0"; exit 2 ;;
esac
