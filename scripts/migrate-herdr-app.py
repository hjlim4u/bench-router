#!/usr/bin/env python3
"""Migrate the installed Ovis/Shepherdr; default is a read-only plan."""
import argparse
import json
import os
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path


def remove_unused_bindings(text):
    return ''.join(block for block in re.split(r'(?=^\[)', text, flags=re.M)
                   if not re.search(r'^command\s*=\s*"(?:annotate\.|zenbu-labs\.terminal-browser\.)', block, re.M))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    home = Path.home()
    config = home / '.config/herdr'
    registry = json.loads((config / 'plugins.json').read_text())
    def entries(value):
        if isinstance(value, dict):
            if 'plugin_id' in value:
                yield value
            for child in value.values():
                yield from entries(child)
        elif isinstance(value, list):
            for child in value:
                yield from entries(child)
    plugins = {p['plugin_id']: p for p in entries(registry)}
    ovis = Path(plugins['devswha.ovis']['source']['managed_path'])
    installed = json.loads((home / '.local/share/shepherdr/installed.json').read_text())
    source = Path(installed['source'])
    if not (source / 'install.sh').is_file() or not (ovis / 'scripts/plugin.ts').is_file():
        raise SystemExit('Installed source missing; no changes made.')
    install = ['shepherdr', 'install', '--source', str(source), '--keys', 'keep', '--no-hooks', '--yes']
    if not args.apply:
        print('Remove Annotate/terminal-browser plugin registrations and their keybindings.')
        print('Keep reviewr and Plugin Manager out of the app migration.')
        print('Set Ovis to herdr-core; keep its existing authentication, port and state.')
        print('Install Shepherdr desktop layout with existing keys and agent hooks preserved.')
        subprocess.run([*install, '--no-build', '--dry-run'], check=True, stdout=subprocess.DEVNULL)
        print('Shepherdr dry run: OK. Run with --apply from an unrestricted user terminal.')
        return
    backup = home / '.local/state/herdr-app-migration' / datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    for path in [config / 'config.toml', config / 'plugins.json',
                 config / 'plugins/config/devswha.ovis/.env',
                 *[home / '.config/herdr-app' / name for name in ('keys.json', 'settings.json', 'shared.json')]]:
        if path.exists():
            target = backup / path.relative_to(home)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
    subprocess.run(install, check=True)
    for plugin_id in ('annotate', 'zenbu-labs.terminal-browser'):
        if plugin_id in plugins:
            subprocess.run(['herdr', 'plugin', 'uninstall', plugin_id], check=True)
    path = config / 'config.toml'
    path.write_text(remove_unused_bindings(path.read_text()))
    env_file = config / 'plugins/config/devswha.ovis/.env'
    env_file.parent.mkdir(parents=True, exist_ok=True)
    text = env_file.read_text() if env_file.exists() else ''
    text = re.sub(r'^(?:export\s+)?(?:OVIS_RUNTIME|OVIS_HC_BIN|HC_SESSION)=.*\n?', '', text, flags=re.M)
    env_file.write_text(text.rstrip() + '\nOVIS_RUNTIME=herdr-core\nHC_SESSION=default\n')
    env_file.chmod(0o600)
    env = {**os.environ, 'HERDR_PLUGIN_ROOT': str(ovis),
           'HERDR_PLUGIN_CONFIG_DIR': str(env_file.parent),
           'HERDR_PLUGIN_STATE_DIR': str(home / '.local/state/herdr/plugins/devswha.ovis')}
    for action in ('stop', 'start', 'status'):
        subprocess.run(['sh', 'scripts/with-bun.sh', 'scripts/plugin.ts', action], cwd=ovis, env=env, check=True)
    subprocess.run(['shepherdr', 'doctor'], check=True)
    print(f'Migration applied. Backup: {backup}')
    print('In Herdr app, Ctrl+Shift+L selects the Shepherdr layout.')


if __name__ == '__main__':
    main()
