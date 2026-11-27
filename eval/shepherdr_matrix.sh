#!/bin/sh
# T9: the real bench-router CLI (--runner herdr) against Shepherdr 3.1.26 and 3.2.19 with hc 0.1.20.
# Usage: sh eval/shepherdr_matrix.sh [TAG...]     (default: v3.1.26 v3.2.19; T9c runs when both are given)
# Everything runs inside throwaway shepherdr-env containers (eval/shepherdr-env/run.sh). Only this checkout is
# mounted (read-only, /src) plus one named volume for T9c (/carry), removed on exit. The agent is a synthetic
# stub; codexbar is a synthetic stub; no model or paid decision call is made.
# Output: docs/evidence/shepherdr-matrix/<tag>/<scenario>/ (CLI outputs, receipt, observed.json, calls.jsonl),
#         docs/evidence/shepherdr-matrix/summary.tsv (one row per tag and path).
set -eu
root=$(cd "$(dirname "$0")/.." && pwd)
self="$root/eval/shepherdr_matrix.sh"
ev="$root/docs/evidence/shepherdr-matrix"
tags=${*:-v3.1.26 v3.2.19}
vol="bench-router-t9c-$$"
inner() { printf 'PHASE=%s\n' "$1"; sed -n '/^#### IN-CONTAINER ####$/,$p' "$self"; }
# run TAG PHASE DIR [VOLUME]: one phase in a fresh container; it prints a tar of its evidence
run() {
  rm -rf "$3"; mkdir -p "$3"
  inner "$2" | SRC="$root" VOL="${4:-}" sh "$root/eval/shepherdr-env/run.sh" shell "$1" bash -s 2>"$3/run.log" \
    | tar -x -C "$3"
}
mkdir -p "$ev"
for tag in $tags; do
  run "$tag" matrix "$ev/$tag"
  echo "$tag: $(grep -c PASS "$ev/$tag/summary.tsv" || true) pass, $(grep -c FAIL "$ev/$tag/summary.tsv" || true) fail"
done
case " $tags " in *" v3.1.26 "*) case " $tags " in *" v3.2.19 "*)
  trap 'docker volume rm -f "$vol" >/dev/null' EXIT
  docker volume create "$vol" >/dev/null
  docker run --rm -u root -v "$vol:/carry" shepherdr-env:v3.1.26 chown tester /carry
  run v3.1.26 t9c-make "$ev/t9c/make-v3.1.26" "$vol"
  run v3.2.19 t9c-check "$ev/t9c/check-v3.2.19" "$vol"
  echo "t9c: $(grep -c PASS "$ev/t9c/check-v3.2.19/summary.tsv" || true) pass, $(grep -c FAIL "$ev/t9c/check-v3.2.19/summary.tsv" || true) fail" ;;
esac ;; esac
{ printf 'tag\thc\tcore_session\tcore_id\trun_id\tpath\texpected\tobserved\tresult\tevidence\n'
  cat "$ev"/v*/summary.tsv "$ev"/t9c/make-*/summary.tsv "$ev"/t9c/check-*/summary.tsv 2>/dev/null || true; } > "$ev/summary.tsv"
exit 0

#### IN-CONTAINER ####
# Runs only inside a throwaway shepherdr-env container. stdout carries only the final tar of /tmp/out.
set -u
exec 3>&1 1>&2
O=/tmp/out; mkdir -p "$O"; : > "$O/summary.tsv"
TAG=$(git -C ~/shepherdr describe --tags)
case "$TAG" in v3.1.*) S=default ;; *) S=shepherdr ;; esac  # the core session herdr-task uses (shepherdr-spike.md)
REAL_TASK=$(command -v herdr-task); REAL_HC=/usr/local/bin/herdr-core
export TAG S REAL_TASK REAL_HC HCV="$(hc --version)"
mkdir -p ~/br && tar --exclude=./.git --exclude=./.bench-router -C /src -cf - . | tar -C ~/br -xf -
export PYTHONPATH=~/br

# Call log: shims ahead of herdr-task and hc; by = router (bench_router.cli), observer (bench_router.lifecycle)
# or other (herdr-task's own hc calls).
mkdir -p /tmp/shim
for pair in "herdr-task:$REAL_TASK" "hc:$REAL_HC"; do
  n=${pair%%:*} real=${pair#*:}
  cat > /tmp/shim/$n <<EOF
#!/bin/sh
who=\$(tr '\0' ' ' < /proc/\$PPID/cmdline 2>/dev/null | cut -c1-300)
case "\$who" in *bench_router.lifecycle*) by=observer ;; *bench_router.cli*) by=router ;; *) by=other ;; esac
"$real" "\$@"; rc=\$?
python3 -c 'import json,sys,time; print(json.dumps({"t":round(time.time(),3),"by":sys.argv[1],"exe":sys.argv[2],"rc":int(sys.argv[3]),"argv":sys.argv[4:]}))' "\$by" "$n" "\$rc" "\$@" >> /tmp/calls.jsonl
exit \$rc
EOF
  chmod +x /tmp/shim/$n
done
export PATH=/tmp/shim:$PATH
: > /tmp/calls.jsonl

# Synthetic agent (claude) and CodexBar. The agent reports idle/working to hc with OSC 7501 (hc's status source).
mkdir -p ~/.local/bin ~/.config/bench-router
cat > ~/.local/bin/claude <<'STUB'
#!/usr/bin/env python3
"""Synthetic claude: reads the bench-router contract from its argv (Shepherdr passes the prompt; headless: -p),
writes result.md/result.json, commits agent.txt, reports its status with OSC 7501, then idles reading stdin.
MODE=complete (default) | tell (results only after a message) | hang (never) | slow (after 25 s)."""
import hashlib, json, os, re, subprocess, sys, time
args = sys.argv[1:]
if args[:1] in (["auth"], ["--version"], ["-v"]):
    print('{"loggedIn": true}'); sys.exit(0)
text = "\n".join(args)
os.makedirs(os.path.expanduser("~/stub-log"), exist_ok=True)
with open(os.path.expanduser(f"~/stub-log/{os.getpid()}.json"), "w") as f:
    json.dump({"cwd": os.getcwd(), "argv_tail": [a[-400:] for a in args[-2:]],
               "env": {k: v for k, v in os.environ.items() if k.startswith(("HC_", "HERDR", "SHEPHERDR"))}}, f)
headless = "-p" in args
def field(label):
    m = re.search(re.escape(label) + r"[^:\n]*:\s*(\S+)", text)
    return m.group(1) if m else None
def osc(state):
    if not headless:
        sys.stdout.write(f"\033]7501;state={state}\007"); sys.stdout.flush()
run_id, nonce, fp, rd = field("실행 식별자"), field("검증 토큰"), field("프로필 지문"), field("결과 디렉터리")
m = re.search(r"MODE=(\w+)", text); mode = m.group(1) if m else "complete"
def deliver(note):
    if not run_id:
        return
    d = os.path.join(os.getcwd(), rd); os.makedirs(d, exist_ok=True)
    if os.path.exists(os.path.join(d, "result.json")):
        return
    md = f"# synthetic result\nrun {run_id}, mode {mode}: {note}\n".encode()
    open(os.path.join(d, "result.md"), "wb").write(md)
    open("agent.txt", "a").write(f"{run_id} {note}\n")
    subprocess.run(["git", "add", "agent.txt"]); subprocess.run(["git", "commit", "-qm", f"agent: {note}"])
    json.dump({"schema_version": "1.0", "run_id": run_id, "nonce": nonce, "profile_fingerprint": fp, "status": "success",
               "result_file": "result.md", "result_sha256": hashlib.sha256(md).hexdigest(), "checks": []},
              open(os.path.join(d, "result.json"), "w"))
    print(f"DONE {run_id} {rd}/result.json", flush=True)
osc("working")
if mode == "slow":
    time.sleep(25)
if mode in ("complete", "slow"):
    deliver("completed first turn")
if headless:
    sys.exit(0)
while mode == "hang":
    time.sleep(3600)
osc("idle"); print("synthetic agent idle", flush=True)
for line in sys.stdin:  # hc send pastes the text and presses enter
    osc("working")
    open(os.path.expanduser("~/told.log"), "a").write(json.dumps({"cwd": os.getcwd(), "run_id": run_id, "line": line.strip()}) + "\n")
    deliver("completed after tell")
    osc("idle")
while True:
    time.sleep(3600)
STUB
cat > ~/.local/bin/codexbar <<'EOF'
#!/bin/sh
# synthetic CodexBar 0.84: fresh, unexhausted quota for the requested provider (no network)
python3 -c 'import json,sys,datetime; print(json.dumps([{"provider": sys.argv[1], "source": "oauth", "usage": {"updatedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(), "primary": {"usedPercent": 10, "windowMinutes": 300}}}]))' "$3"
EOF
chmod +x ~/.local/bin/claude ~/.local/bin/codexbar
cat > ~/.config/bench-router/profiles.toml <<'EOF'
schema_version = "1.0"
[[profile]]
id = "claude-opus-medium"
enabled = true
kind = "claude"
executable = "claude"
args = ["--model", "claude-opus-5-5", "--effort", "medium"]
model_id = "claude-opus-5-5"
harness_id = "claude-code"
reasoning_effort = "medium"
config_revision = "2026-11-26"
cost_tier = "high"
inference_local = false
context_tokens = 1000000
capabilities = ["filesystem_write"]
EOF

br() { python3 -m bench_router.cli --runner herdr --herdr-space demo "$@"; }
hcs() { env -u HC_SOCKET HC_SESSION="$S" "$REAL_HC" "$@"; }
# cap SC NAME CMD...: stdout/stderr/exit code of one command under $O/SC
cap() {
  sc=$1 n=$2; shift 2; mkdir -p "$O/$sc"
  "$@" >"$O/$sc/$n.out" 2>"$O/$sc/$n.err"; rc=$?
  echo "$rc" >"$O/$sc/$n.rc"; echo "[$sc/$n] rc=$rc" >&2
  return 0
}
mkrepo() { mkdir -p ~/w/$1 && cd ~/w/$1 && git init -q && echo a > a && git add a && git commit -qm init && cd ~; }
# task FILE ID MODE EXECUTION CWD
task() {
  python3 - "$@" <<'EOF'
import json, sys
f, tid, mode, ex, cwd = sys.argv[1:6]
json.dump({"schema_version": "1.0", "task_id": tid, "round": 1, "summary": f"switch matrix {tid}",
           "prompt": f"Synthetic switch-matrix task. MODE={mode}", "cwd": cwd, "execution": ex,
           "constraints": {"timeout_ms": 300000},
           "profile_filter": {"include": {"model": ["claude-opus-5-5"], "effort": ["medium"]}}}, open(f, "w"))
EOF
}
# sel SC TASK OUT: offline assessment (synthetic codexbar preflight) -> select -> the selection object
sel() {
  cap "$1" evaluate br evaluate --preflight --format 3 --task "$2" --host claude
  cap "$1" select br select --assessment "$O/$1/evaluate.out" --profile claude-opus-medium --policy-id switch-matrix \
    --policy-version 1 --reason "sole profile fixed by the task's profile_filter"
  python3 -c 'import json,sys; json.dump(json.load(open(sys.argv[1]))["selection"], open(sys.argv[2], "w"))' "$O/$1/select.out" "$3"
}
rid() { python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("run_id") or "")' "$O/$1"; }
now() { python3 -c 'import time; print(round(time.time(), 3))'; }
# wait_status CWD RID STATUS SECONDS: read the receipt file only (no CLI call)
wait_status() {
  for _ in $(seq $(($4 * 2))); do
    python3 -c 'import json,sys; sys.exit(json.load(open(sys.argv[1]))["status"] != sys.argv[2])' \
      "$1/.bench-router/runs/$2/receipt.json" "$3" 2>/dev/null && return 0
    sleep 0.5
  done; return 1
}
# wait_idle CWD RID: until the run's agent terminal reports idle (hc get, outside the router)
wait_idle() {
  for _ in $(seq 60); do
    t=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("terminal_id") or "")' "$1/.bench-router/runs/$2/receipt.json" 2>/dev/null)
    [ -n "$t" ] && hcs get "$t" --json 2>/dev/null | grep -q '"status":{"state":"idle"' && return 0
    sleep 0.5
  done; return 1
}

cat > /tmp/check.py <<'EOF'
"""check.py SC RID EXPECT [EXTRA-JSON]: observe one run separately (result copy, terminal end state, admission)
and append a summary row. Reads files, hc get/ls and herdr-task show directly (not through the call-log shim)."""
import glob, hashlib, json, os, subprocess, sys
sc, rid, expect = sys.argv[1:4]
extra = json.loads(sys.argv[4]) if len(sys.argv) > 4 else {}
O, HOME, S = "/tmp/out", os.path.expanduser("~"), os.environ["S"]
d = f"{O}/{sc}"; os.makedirs(d, exist_ok=True)
env = {k: v for k, v in os.environ.items() if k not in ("HC_SOCKET", "HC_TERMINAL_SOCKET", "HC_TERMINAL_ID")}
env["HC_SESSION"] = S
def hc(*a):
    p = subprocess.run([os.environ["REAL_HC"], *a, "--json"], capture_output=True, text=True, env=env)
    try:
        return json.loads(p.stdout or p.stderr)
    except ValueError:
        return {"raw": (p.stdout + p.stderr)[:300], "rc": p.returncode}
paths = [p for p in glob.glob(f"{HOME}/w/**/runs/{rid}/receipt.json", recursive=True, include_hidden=True)] if rid else []
o = {"scenario": sc, "run_id": rid, "expect": expect}
rc = json.load(open(paths[0])) if paths else {}
if paths:
    open(f"{d}/receipt.json", "wb").write(open(paths[0], "rb").read())
o["status"] = rc.get("status")
o["core"] = rc.get("project_binding") or {}
rd = rc.get("run_dir", "")
try:
    man = json.load(open(f"{rd}/result.json"))
    md = open(f"{rd}/result.md", "rb").read()
    o["result_copied"] = (man.get("nonce") == rc.get("nonce") and man.get("run_id") == rid
                          and hashlib.sha256(md).hexdigest() == man.get("result_sha256"))
except (OSError, ValueError):
    o["result_copied"] = False
key = rc.get("thread_id")
ls = hc("ls", "--all", "--label", f"herdr.task={key}") if key else {}
o["terminals"] = {}
for t in ls.get("terminals") or []:
    g = hc("get", t["address"])
    o["terminals"][t["address"]] = {k: g.get(k) for k in ("state", "reason", "exit_code", "signal", "status")}
if rc.get("terminal_id") and rc["terminal_id"] not in o["terminals"]:
    g = hc("get", rc["terminal_id"])
    o["terminals"][rc["terminal_id"]] = {k: g.get(k) for k in ("state", "reason", "exit_code", "signal", "status", "labels")} if "state" in g else g
w = hc("ls", "--all", "--label", f"bench-router.watch={rid}")
o["observer_terminals"] = [{k: t.get(k) for k in ("address", "state")} for t in w.get("terminals") or []]
if key:
    p = subprocess.run([os.environ["REAL_TASK"], "show", key, "--folder", rc.get("repo_cwd", rc.get("cwd")), "--json"],
                       capture_output=True, text=True, env={k: v for k, v in os.environ.items() if not k.startswith("HC_")})
    try:
        b = json.loads(p.stdout)
        o["board"] = {k: b.get(k) for k in ("state", "status", "needs", "why", "live")}
    except ValueError:
        o["board"] = {"raw": (p.stdout + p.stderr)[:300]}
co = json.loads(subprocess.run([sys.executable, "-m", "bench_router.cli", "coordination", "status"],
                               capture_output=True, text=True).stdout or "{}")
recs = [x for x in co.get("records", []) if (x.get("reference") or {}).get("run_id") == rid]
o["admission_active"] = recs[0]["active"] if recs else None
o["ready"], o["release"], o["process_exited"] = rc.get("ready"), rc.get("release"), rc.get("process_exited")
t0, t1 = extra.get("t0", 0), extra.get("t1", 1e12)
calls = [json.loads(x) for x in open("/tmp/calls.jsonl")]
addrs = set(o["terminals"]) | {t["address"] for t in o["observer_terminals"]} | {rc.get("terminal_id")} - {None}
if extra.get("t0"):  # a time window: every call, whoever made it
    mine = [c for c in calls if t0 <= c["t"] <= t1]
else:  # the router's and observer's calls naming this run, its task key or one of its terminals
    mine = [c for c in calls if c["by"] != "other" and any(rid in a or (key and key in a) or a in addrs for a in c["argv"])]
json.dump(mine, open(f"{d}/calls.json", "w"), indent=1)
ops = {}
for c in mine:
    k = f"{c['by']}:{c['exe']} {c['argv'][0] if c['argv'] else ''}"
    ops[k] = ops.get(k, 0) + 1
o["calls"] = ops
terms = [t for t in o["terminals"].values() if isinstance(t, dict)]
finished = bool(terms) and all(t.get("state") == "finished" for t in terms)
told = [json.loads(x) for x in open(f"{HOME}/told.log")] if os.path.exists(f"{HOME}/told.log") else []
checks = {}
if expect == "completed":
    checks = {"status completed": o["status"] == "completed", "result copied beside receipt": o["result_copied"],
              "ready handoff": (o["ready"] or {}).get("state") == "ready" and (o.get("board") or {}).get("state") == "ready",
              "release recorded": bool(o["release"]), "terminal finished (hc get)": finished,
              "admission released": o["admission_active"] is False}
elif expect == "stopped":
    checks = {"status execution_failed": o["status"] == "execution_failed", "process_exited": o["process_exited"] is True,
              "terminal finished (hc get)": finished, "admission released": o["admission_active"] is False,
              "no result claimed": not o["result_copied"]}
elif expect == "resumed":
    live = [t for t in terms if t.get("state") == "live"]
    checks = {"status completed": o["status"] == "completed", "result copied beside receipt": o["result_copied"],
              "resumed terminal live, task-labelled (not auto-released)": len(live) == 1,
              "admission released": o["admission_active"] is False}
elif expect == "unchanged":
    raw = open(paths[0], "rb").read() if paths else b""
    checks = {"receipt bytes unchanged": hashlib.sha256(raw).hexdigest() == extra.get("sha"),
              "status completed": o["status"] == "completed", "result readable": o["result_copied"],
              "0 start/send/kill/ready/resume calls": not any(c["argv"][:1] in (["start"], ["send"], ["kill"], ["ready"], ["resume"]) for c in mine)}
elif expect == "held":
    checks = {"status delivery_uncertain": o["status"] == "delivery_uncertain", "admission held": o["admission_active"] is True,
              "0 start/send/kill/ready/resume calls": not any(c["argv"][:1] in (["start"], ["send"], ["kill"], ["ready"], ["resume"]) for c in mine)}
if "told" in extra:
    checks["message reached the agent"] = any(extra["told"] in x["line"] for x in told)
if "out" in extra:  # SC/NAME.out must report this status
    try:
        got = json.load(open(f"{d}/{extra['out'][0]}.out")).get("status")
    except (OSError, ValueError):
        got = None
    checks[f"{extra['out'][0]} -> {extra['out'][1]}"] = got == extra["out"][1]
if "observer" in extra:
    checks["ready sent by the core observer"] = any(c["by"] == "observer" and c["argv"][:1] == ["ready"] for c in mine)
o["checks"] = checks
ok = bool(checks) and all(checks.values())
json.dump(o, open(f"{d}/observed.json", "w"), indent=1, ensure_ascii=False)
short = lambda t: f"{t.get('state')}/{t.get('reason')}" if isinstance(t, dict) else str(t)
observed = (f"status={o['status']}; result_copied={o['result_copied']}; terminals="
            + ",".join(f"{a}:{short(t)}" for a, t in o["terminals"].items())
            + f"; admission_active={o['admission_active']}; ready={(o['ready'] or {}).get('state')}; release={'yes' if o['release'] else 'no'}"
            + "".join(f"; FAILED {k}" for k, v in checks.items() if not v))
expected = {"completed": "completed; result copied; Ready; released; terminals finished; admission released",
            "stopped": "execution_failed; process exited; terminals finished; admission released",
            "resumed": "resumed terminal live and labelled; completed record kept; admission released",
            "unchanged": "completed receipt bytes unchanged; result readable; no control calls",
            "held": "delivery_uncertain; admission held; 0 start/send/kill/ready calls"}[expect]
if "told" in extra:
    expected += "; message delivered"
with open(f"{O}/summary.tsv", "a") as f:
    f.write("\t".join([os.environ["TAG"], os.environ["HCV"], o["core"].get("session", S), str(o["core"].get("core_id")),
                       rid or "-", sc, expected, observed, "PASS" if ok else "FAIL",
                       f"shepherdr-matrix/{os.environ.get('EVDIR', os.environ['TAG'])}/{sc}/observed.json"]) + "\n")
print(f"[{sc}] {'PASS' if ok else 'FAIL'} {observed}", file=sys.stderr)
EOF

finish() {
  cp /tmp/calls.jsonl "$O/calls.jsonl"; cat ~/stub-log/*.json > "$O/stub-log.jsonl" 2>/dev/null
  cp ~/told.log "$O/told.log" 2>/dev/null
  br coordination status > "$O/coordination.json" 2>&1
  hcs ls --all --json > "$O/hc_ls_all.json" 2>&1
  tar -C "$O" -cf - . >&3
}

matrix() {
  # route, interactive: completes in its first turn
  mkrepo ri; task /tmp/ri.json sm-ri complete interactive ~/w/ri; sel route-interactive /tmp/ri.json /tmp/ri.sel
  cap route-interactive route br route --task /tmp/ri.json --selection /tmp/ri.sel --wait-ms 90000
  RI=$(rid route-interactive/route.out)
  python3 /tmp/check.py route-interactive "$RI" completed '{"out":["route","completed"]}'
  # route, headless one-shot CLI
  mkrepo rh; task /tmp/rh.json sm-rh complete headless ~/w/rh; sel route-headless /tmp/rh.json /tmp/rh.sel
  cap route-headless route br route --task /tmp/rh.json --selection /tmp/rh.sel --wait-ms 90000
  python3 /tmp/check.py route-headless "$(rid route-headless/route.out)" completed '{"out":["route","completed"]}'
  # the core observer alone: route returns at once and nobody collects; the observer must collect, Ready, release
  mkrepo ob; task /tmp/ob.json sm-ob slow interactive ~/w/ob; sel observer /tmp/ob.json /tmp/ob.sel
  cap observer route br route --task /tmp/ob.json --selection /tmp/ob.sel --wait-ms 0
  OB=$(rid observer/route.out); wait_status ~/w/ob "$OB" completed 120; sleep 3
  python3 /tmp/check.py observer "$OB" completed '{"observer":1}'
  # tell: the agent writes its result only after the router's message
  mkrepo te; task /tmp/te.json sm-te tell interactive ~/w/te; sel tell /tmp/te.json /tmp/te.sel
  cap tell route br route --task /tmp/te.json --selection /tmp/te.sel --wait-ms 0
  TE=$(rid tell/route.out); wait_idle ~/w/te "$TE"
  cap tell tell br tell --cwd ~/w/te --run-id "$TE" --message "matrix-tell-$TAG"
  cap tell collect br collect --cwd ~/w/te --run-id "$TE" --wait-ms 60000
  python3 /tmp/check.py tell "$TE" completed "{\"told\":\"matrix-tell-$TAG\",\"out\":[\"tell\",\"sent\"]}"
  # stop a working agent, then collect
  mkrepo st; task /tmp/st.json sm-st hang interactive ~/w/st; sel stop /tmp/st.json /tmp/st.sel
  cap stop route br route --task /tmp/st.json --selection /tmp/st.sel --wait-ms 0
  ST=$(rid stop/route.out); sleep 3
  cap stop stop br stop --cwd ~/w/st --run-id "$ST"
  cap stop collect br collect --cwd ~/w/st --run-id "$ST" --wait-ms 30000
  python3 /tmp/check.py stop "$ST" stopped '{"out":["stop","stop_sent"]}'
  # resume the completed interactive run, then tell the resumed agent
  cap resume resume br resume --cwd ~/w/ri --run-id "$RI"
  sleep 5
  cap resume tell br tell --cwd ~/w/ri --run-id "$RI" --message "matrix-resume-tell-$TAG"
  sleep 2
  python3 /tmp/check.py resume "$RI" resumed "{\"told\":\"matrix-resume-tell-$TAG\",\"out\":[\"tell\",\"sent\"]}"
  # parallel: one interactive and one headless member (group schema 2.0 with explicit selections)
  mkrepo par
  task /tmp/pi.json sm-par-i complete interactive ~/w/par; sel parallel /tmp/pi.json /tmp/pi.sel
  mv "$O/parallel/evaluate.out" "$O/parallel/evaluate-i.out"; mv "$O/parallel/select.out" "$O/parallel/select-i.out"
  task /tmp/ph.json sm-par-h complete headless ~/w/par; sel parallel /tmp/ph.json /tmp/ph.sel
  python3 - <<'PY'
import json, os
tasks = []
for t, s in (("/tmp/pi.json", "/tmp/pi.sel"), ("/tmp/ph.json", "/tmp/ph.sel")):
    task = json.load(open(t)); task.pop("cwd")
    tasks.append({"task": task, "selections": [json.load(open(s))]})
json.dump({"schema_version": "2.0", "group_id": "switch-matrix", "cwd": os.path.expanduser("~/w/par"), "tasks": tasks},
          open("/tmp/group.json", "w"))
PY
  cp /tmp/group.json "$O/parallel/group.json"
  cap parallel parallel br parallel --group /tmp/group.json --wait-ms 90000
  for m in $(python3 -c 'import json,sys
for m in json.load(open(sys.argv[1])).get("members", []): print(str(m.get("label")) + "=" + str((m.get("rounds") or [{}])[-1].get("run_id")))' "$O/parallel/parallel.out"); do
    python3 /tmp/check.py "parallel-${m%%=*}" "${m#*=}" completed
  done
  # collect after a core restart while the agent is still working
  mkrepo rs; task /tmp/rs.json sm-rs slow interactive ~/w/rs; sel restart /tmp/rs.json /tmp/rs.sel
  cap restart route br route --task /tmp/rs.json --selection /tmp/rs.sel --wait-ms 0
  RS=$(rid restart/route.out); sleep 2
  cap restart server_restart hcs server restart
  cap restart collect br collect --cwd ~/w/rs --run-id "$RS" --wait-ms 90000
  python3 /tmp/check.py restart "$RS" completed '{"out":["collect","completed"]}'
}

# T9c, part 1 (3.1.26): a completed and an unfinished receipt, carried in /carry
t9c_make() {
  export EVDIR=t9c/make-v3.1.26
  mkrepo c; task /tmp/c.json sm-c complete interactive ~/w/c; sel t9c-completed /tmp/c.json /tmp/c.sel
  cap t9c-completed route br route --task /tmp/c.json --selection /tmp/c.sel --wait-ms 90000
  C=$(rid t9c-completed/route.out); python3 /tmp/check.py t9c-completed "$C" completed
  mkrepo u; task /tmp/u.json sm-u hang interactive ~/w/u; sel t9c-unfinished /tmp/u.json /tmp/u.sel
  cap t9c-unfinished route br route --task /tmp/u.json --selection /tmp/u.sel --wait-ms 0
  U=$(rid t9c-unfinished/route.out); sleep 5
  cp ~/w/u/.bench-router/runs/$U/receipt.json "$O/t9c-unfinished/receipt.json"
  printf '%s %s\n' "$C" "$U" > /carry/runs
  tar -C ~ -cf /carry/home.tar w .local/state/bench-router
  ( cd ~ && sha256sum w/c/.bench-router/runs/$C/receipt.json w/u/.bench-router/runs/$U/receipt.json ) > /carry/sha256
  cp /carry/runs /carry/sha256 "$O/"
}

# T9c, part 2 (3.2.19): another terminal holds t1 first, then collect both carried runs
t9c_check() {
  export EVDIR=t9c/check-v3.2.19
  for s in shepherdr default; do
    cap t9c-occupy "t1_$s" env -u HC_SOCKET HC_SESSION=$s "$REAL_HC" run --bg --json --name "squatter-$s" -- sleep 3600
  done
  tar -C ~ -xf /carry/home.tar
  read C U < /carry/runs; cp /carry/runs /carry/sha256 "$O/"
  t0=$(now)
  cap t9c-completed collect br collect --cwd ~/w/c --run-id "$C" --wait-ms 10000
  t1=$(now)
  python3 /tmp/check.py t9c-completed "$C" unchanged "{\"t0\":$t0,\"t1\":$t1,\"sha\":\"$(grep "/runs/$C/" /carry/sha256 | cut -d' ' -f1)\"}"
  t0=$(now)
  cap t9c-unfinished collect br collect --cwd ~/w/u --run-id "$U" --wait-ms 10000
  t1=$(now)
  python3 /tmp/check.py t9c-unfinished "$U" held "{\"t0\":$t0,\"t1\":$t1}"
}

case "$PHASE" in
  matrix) matrix ;;
  t9c-make) t9c_make ;;
  t9c-check) t9c_check ;;
esac
finish
