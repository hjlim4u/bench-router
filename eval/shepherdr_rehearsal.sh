#!/bin/bash
# Replica rehearsal of docs/shepherdr-rollback.md section 4: restore the 3.1 archive, check it, install the image's
# Shepherdr (3.2.19) over it, roll back with section 6, check again. Runs as root inside a throwaway container; only
# the archive (read-only) comes from the host. Build the image once (eval/shepherdr-env/run.sh build v3.2.19), then,
# from the repository root:
#   docker run --rm -i -u root --entrypoint bash \
#     -e REPLICA_USER="$USER" -e REPLICA_UID="$(id -u)" -e REPLICA_HOME="$HOME" \
#     -v ~/.local/backups/shepherdr/shepherdr-3.1.tar:/backup.tar:ro \
#     -v "$PWD/eval/shepherdr_rehearsal.sh:/rehearsal.sh:ro" shepherdr-env:v3.2.19 /rehearsal.sh
# The replica user gets the host's uid and home path: the archive keeps numeric owners and absolute ~/.herdr links.
# The last line is "REHEARSAL PASS" or "REHEARSAL FAIL". Running cards make the install refuse; the replica then
# forces it, which is never done on the host.
set -u
U=${REPLICA_USER:?set REPLICA_USER to the host user name}; H=${REPLICA_HOME:-/home/$U}; ID=${REPLICA_UID:-1000}
R=${H#/}; SRC=/home/tester/shepherdr; TV=$(git -c safe.directory="$SRC" -C "$SRC" describe --tags | sed 's/^v//')
[ -n "$TV" ] || { echo "REHEARSAL FAIL: cannot read the image's Shepherdr version"; exit 1; }
step() { printf '\n##### %s\n' "$*"; }
as() { su - "$U" -c "export PATH=$H/.local/bin:/usr/local/bin:/usr/bin:/bin; $*"; }

step "A. restore archive into $H (uid $ID)"
{ getent passwd "$ID" | cut -d: -f1; getent passwd "$U" | cut -d: -f1; } | sort -u | grep -vx tester | xargs -r -n1 userdel -r 2>/dev/null
useradd -u "$ID" -M -d "$H" -s /bin/bash "$U" && mkdir -p "$H" && chown "$ID:$ID" "$H" || { echo "REHEARSAL FAIL: cannot create user $U (uid $ID)"; exit 1; }
tar -xpf /backup.tar --numeric-owner -C / && echo "extract rc=0"
chown "$ID:$ID" "$H" "$H"/.config "$H"/.local "$H"/.local/share "$H"/.local/state "$H"/.local/bin "$H"/.claude "$H"/.codex "$H"/.config/systemd "$H"/.config/systemd/user 2>/dev/null; true
as 'git config --global user.email r@example.invalid; git config --global user.name r'
# shortcut: the cards' repositories are not in the archive; empty repos at the same paths let list/show open them
as 'python3 - <<E
import json,glob,os,subprocess
for p in glob.glob(os.path.expanduser("~/.herdr/tasks/*.json")):
    f=json.load(open(p)).get("folder")
    if f and not os.path.isdir(f):
        os.makedirs(f); subprocess.run(["git","init","-q",f]); subprocess.run(["git","-C",f,"commit","-q","--allow-empty","-m","replica"])
        print("stub repo", f.replace(os.path.expanduser("~"),"~").split("/")[-1][:3]+"…")
E'

check() {
  step "$1: payload, session settings, layout"
  as 'readlink ~/.local/bin/herdr-task ~/.local/bin/shepherdr'
  as 'echo "HC_SESSION lines in unit: $(grep -c HC_SESSION ~/.config/systemd/user/shepherdr.service)"'
  as 'echo "LAYOUT=$(cat ~/.local/share/shepherdr/LAYOUT 2>/dev/null || echo "none, layout 1")"; ls -L ~/.herdr >/dev/null && echo "~/.herdr resolves"'
  as 'python3 - <<E
import json,glob,os
n=0; f=0
for p in glob.glob(os.path.expanduser("~/.herdr/tasks/*.json")):
    d=json.load(open(p)); f+=1; n+=len(d.get("tasks",[]))
print("on-disk cards", n, "files", f)
E'
  step "$1: existing tasks open (herdr-task)"
  as 'herdr-task list --all --archived --json > /tmp/arch.json; echo "list --all --archived rc=$?"'
  as 'herdr-task list --all --json > /tmp/list.json; echo "list --all rc=$?"; python3 - <<E
import json,collections
active=[(g["folder"],t) for g in json.load(open("/tmp/list.json")) for t in g["tasks"]]
arch=[(g["folder"],t) for g in json.load(open("/tmp/arch.json")) for t in g["tasks"]]
print("listed: active", len(active), "archived", len(arch), "total", len(active)+len(arch),
      "folders", len({f for f,_ in active+arch}))
open("/tmp/count","w").write(str(len(active)+len(arch)))
print("states", dict(collections.Counter(t.get("state") for _,t in active+arch)))
by={}
for f,t in active+arch: by.setdefault(t.get("state"), (f,t))
for s in ("done","running"):
    if s in by:
        f,t=by[s]; open("/tmp/show_"+s,"w").write(str(t.get("key"))+chr(9)+f)
E'
  as 'python3 - <<E
import json,os,subprocess
for s in ("done","running"):
    if not os.path.exists("/tmp/show_"+s): print("show", s, "no card"); continue
    k,f=open("/tmp/show_"+s).read().split(chr(9))
    p=subprocess.run(["herdr-task","show",k,"--folder",f,"--json"],capture_output=True,text=True)
    try: d=json.loads(p.stdout); info={x:d.get(x) for x in ("state","status","needs")}
    except Exception: info=(p.stderr or p.stdout)[-200:]
    print("show", s, "rc=%d" % p.returncode, info)
E'
  as 'hc server status --json 2>&1 | python3 -c "import json,sys;d=json.load(sys.stdin);print(\"core status\",json.dumps(d)[:300])" 2>&1'
  as 'hc server stop >/dev/null 2>&1; true'
  cp /tmp/count "/tmp/count_$2" 2>/dev/null; rm -f /tmp/count /tmp/show_done /tmp/show_running
}

check "B. baseline (3.1 restored)" before

step "C. forward path: install $TV over the restored 3.1"
rm -rf "$H/shepherdr"; cp -a "$SRC" "$H/shepherdr" && chown -R "$ID:$ID" "$H/shepherdr"
as 'cd ~/shepherdr && git describe --tags && ./install.sh --no-build --yes > /tmp/install1.log 2>&1; echo "install (no --force) rc=$?"; tail -25 /tmp/install1.log'
if ! as 'test -f ~/.local/share/shepherdr/installed.json && grep -q "\"version\": \"'"$TV"'\"" ~/.local/share/shepherdr/installed.json'; then
  step "C2. replica only: retry with --force (never on the host)"
  as 'cd ~/shepherdr && ./install.sh --no-build --yes --force > /tmp/install2.log 2>&1; echo "install --force rc=$?"; tail -25 /tmp/install2.log'
fi
as 'shepherdr doctor > /tmp/doctor.log 2>&1; echo "doctor rc=$?"; tail -30 /tmp/doctor.log'
as 'shepherdr where 2>&1 | head -40'
as 'cat ~/.local/state/shepherdr/migrate.json; echo; grep -n "HC_SESSION\|SHEPHERDR_SESSION" ~/.config/systemd/user/shepherdr.service; ls ~/.local/share/shepherdr/.shepherdr-backup 2>&1; readlink ~/.local/bin/herdr-task; ls ~/.config/herdr-app/mods 2>&1 | head; test -e ~/.config/herdr-app/data/shepherdr/installed.json && echo "3.1 record present" || echo "3.1 record removed"'
as 'herdr-task list --all --json > /tmp/l32.json; echo "3.2 list rc=$?"; python3 -c "import json;d=json.load(open(\"/tmp/l32.json\"));print(\"3.2 listed\",sum(len(g[\"tasks\"]) for g in d))"'
as 'python3 - <<E
import json,glob,os,collections
c=collections.Counter()
for p in glob.glob(os.path.expanduser("~/.herdr/tasks/*.json")):
    d=json.load(open(p)); c.update(k for k in d if k!="tasks")
    for t in d.get("tasks",[]): c.update("task."+k for k in t)
print(sorted(c.items()))
E' > /tmp/fields_after.txt
as 'grep -c . ~/.claude/settings.json; grep -o "shepherdr/hooks[^\"]*\|herdr-app/mods/chat[^\"]*" ~/.claude/settings.json | sort | uniq -c'

step "D. rollback (section 6)"
as 'cd / && tar -cpf /tmp/shepherdr-failed.tar --exclude='"$R"'/.herdr/worktrees --exclude='"$R"'/.local/share/shepherdr/worktrees '"$R"'/.config/herdr-app '"$R"'/.config/shepherdr '"$R"'/.local/share/shepherdr '"$R"'/.local/state/shepherdr '"$R"'/.herdr 2>/dev/null; echo "failed-state archive rc=$?"'
as 'shepherdr uninstall > /tmp/uninstall.log 2>&1; echo "uninstall rc=$?"; tail -20 /tmp/uninstall.log'
# ~/.herdr is not restored: after the install it holds links to the moved data, which 3.1 reads through
tar -xpf /backup.tar --numeric-owner -C / --exclude="$R/.herdr" \
  --exclude="$R/.local/share/shepherdr/tasks" --exclude="$R/.local/share/shepherdr/artifacts" \
  --exclude="$R/.local/share/shepherdr/secrets" && echo "restore (payload+config; board data and ~/.herdr kept) rc=0"

check "E. after rollback (3.1 payload, post-switch board data)" after

step "E2. 3.2-written fields still in the kept board data"
as 'python3 - <<E
import json,glob,os,collections
c=collections.Counter()
for p in glob.glob(os.path.expanduser("~/.herdr/tasks/*.json")):
    d=json.load(open(p)); c.update(k for k in d if k!="tasks")
    for t in d.get("tasks",[]): c.update("task."+k for k in t)
print(sorted(c.items()))
E' > /tmp/fields_rollback.txt
mkdir -p /tmp/orig && tar -xf /backup.tar -C /tmp/orig --wildcards "$R/.local/share/shepherdr/tasks/*.json" "$R/.herdr/tasks/*.json" 2>/dev/null; chmod -R a+rX /tmp/orig
as 'python3 - <<E
import json,glob,collections
c=collections.Counter()
for p in glob.glob("/tmp/orig/'"$R"'/.local/share/shepherdr/tasks/*.json")+glob.glob("/tmp/orig/'"$R"'/.herdr/tasks/*.json"):
    d=json.load(open(p)); c.update(k for k in d if k!="tasks")
    for t in d.get("tasks",[]): c.update("task."+k for k in t)
print(sorted(c.items()))
E' > /tmp/fields_before.txt
python3 - <<'E'
import ast
b=dict(ast.literal_eval(open("/tmp/fields_before.txt").read()))
a=dict(ast.literal_eval(open("/tmp/fields_rollback.txt").read()))
print("fields added by 3.2:", {k:a[k] for k in a if k not in b})
print("fields removed:", [k for k in b if k not in a])
print("count changes:", {k:(b[k],a[k]) for k in b if k in a and a[k]!=b[k]})
E
step "F. hooks after rollback"
for f in .claude/settings.json .codex/hooks.json .config/systemd/user/shepherdr.service .config/herdr-app/keys.json; do tar -tf /backup.tar "$R/$f" >/dev/null 2>&1 || { echo "not in archive: $f"; continue; }
  tar -xOf /backup.tar "$R/$f" | cmp -s - "$H/$f" && echo "same as archive: $f" || { echo "DIFFERS: $f"; differs=1; }; done
b=$(cat /tmp/count_before 2>/dev/null); a=$(cat /tmp/count_after 2>/dev/null)
link=$(readlink "$H/.local/bin/herdr-task")
echo "cards listed before: ${b:-none}, after rollback: ${a:-none}; herdr-task -> $link"
case "$link" in *"/.config/herdr-app/"*) ;; *) differs=1 ;; esac
[ -n "$b" ] && [ "$b" = "$a" ] && [ -z "${differs:-}" ] && echo "REHEARSAL PASS" || { echo "REHEARSAL FAIL"; exit 1; }
