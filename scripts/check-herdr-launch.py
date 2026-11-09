import json, os, subprocess, tempfile, tomllib
from pathlib import Path
root=Path.cwd()
config=tomllib.loads((root/'examples/herdr-tui.toml').read_text())
assert all(k['type']=='pane' and 'hc attach' in k['command'] for k in config['keys']['command'])
with tempfile.TemporaryDirectory() as tmp:
    fake=Path(tmp)/'herdr'
    fake.write_text('#!/usr/bin/env python3\nimport json,os,sys\nprint(json.dumps({"argv":sys.argv[1:],"env":dict(os.environ)}))\n')
    fake.chmod(0o755)
    env={**os.environ,'PATH':tmp+':'+os.environ['PATH'],'HC_SESSION':'wrong','HERDR_SOCKET_PATH':'wrong','XDG_CONFIG_HOME':'/tmp/original-config','XDG_STATE_HOME':'/tmp/original-state'}
    result=json.loads(subprocess.check_output(['sh','scripts/herdr.sh','tui','--help'],env=env,text=True))
    e=result['env']
    assert result['argv']==['--session','app-companion','--help']
    assert e['XDG_CONFIG_HOME']==str(root/'.bench-router/tui/config')
    assert 'HC_SESSION' not in e and 'HERDR_SOCKET_PATH' not in e
    e['BENCH_ROUTER_LOGIN_SHELL']='/bin/sh'
    restored=subprocess.check_output(['sh','scripts/herdr-shell.sh','-c','printf "%s:%s" "$XDG_CONFIG_HOME" "$XDG_STATE_HOME"'],env=e,text=True)
    assert restored=='/tmp/original-config:/tmp/original-state'
print('Herdr launch isolation and shell restoration: OK')
