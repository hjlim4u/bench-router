"""Offline check: removing plugin bindings must retain unrelated settings."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location('migration', Path(__file__).with_name('migrate-herdr-app.py'))
migration = importlib.util.module_from_spec(spec)
spec.loader.exec_module(migration)
text = '''onboarding = false
[[keys.command]]
key = "prefix+a"
command = "annotate.capture"
[[keys.command]]
key = "prefix+r"
command = "persiyanov.reviewr.toggle"
[[keys.command]]
key = "prefix+b"
command = "zenbu-labs.terminal-browser.open-split"
[experimental]
kitty_graphics = true
'''
result = migration.remove_unused_bindings(text)
assert 'annotate.capture' not in result and 'terminal-browser' not in result
assert 'persiyanov.reviewr.toggle' in result
assert '[experimental]\nkitty_graphics = true' in result
assert migration.remove_unused_bindings(result) == result
print('Migration binding removal and idempotence: OK')
