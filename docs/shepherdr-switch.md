# Shepherdr 3.1 → 3.2 switch: handoff

This is the short path for switching a host from Shepherdr 3.1.x to 3.2.19 with bench-router in use. It is
written for an operator, or an agent the operator explicitly asked to do the switch. It takes about 30 minutes,
most of it spent settling running cards.

The reference material is in [shepherdr-rollback.md](shepherdr-rollback.md):
- what the installer changes, in the section 2 locations table;
- the replica rehearsal (section 4);
- the rollback (section 6);
- the known gaps (section 7).

This handoff only repeats what you need to run the switch.

## Files

| File | Use |
|---|---|
| `eval/shepherdr_switch.sh` | `check` lists what blocks the switch (read-only). `backup` writes the quiesced archive. `smoke` runs one bench-router task through Shepherdr after the switch. |
| `docs/shepherdr-rollback.md` | Locations, rehearsal, rollback, known gaps. |
| `eval/shepherdr-env/`, `eval/shepherdr_rehearsal.sh` | Docker images and the replica rehearsal of install plus rollback (optional, section 4 of the runbook). |

## Before you start

- **Host:** Linux or WSL2. You need `hc` (herdr-core) 0.1.17 or newer on the PATH. You also need `bun`, because
  without it the 3.2 service and web app are not installed.
- **Shepherdr source:** Shepherdr 3.1.x is installed from a git clone. The script reads its path from the
  install record and falls back to `~/shepherdr` (`SHEPHERDR_SRC` overrides it). `check` prints the path; the
  commands below call it `SRC`.
- **Default folders:** the script reads `~/.config`, `~/.local/share`, `~/.local/state` and `~/.herdr`. If
  `XDG_*_HOME`, `HERDR_APP_HOME` or `SHEPHERDR_HOME` point elsewhere, `backup` refuses and you archive by hand
  (runbook section 3).
- **Data layout:** `check` prints it. On a plain 3.1 host it is 1: the board data is in `~/.herdr`, and the 3.2
  install moves it into Shepherdr's own folders and leaves links behind. The first host was already on layout 2.
  Both cases are covered.
- **A Shepherdr space for bench-router:** `smoke` uses `BENCH_ROUTER_SPACE`, or `bench-router` when it is unset.
- **bench-router:** install it from `main` at or after the port merge (PR #22), with
  `uv tool install --force <checkout>`. Do this first. The port works with both 3.1 and 3.2, so you can update it
  while 3.1 is still running.
- **Stop new submissions:** no new `bench-router route` or `parallel` runs, and no new board tasks, until the
  smoke test passes.

## Steps

1. **Check.** Run `eval/shepherdr_switch.sh check` and settle every blocker it lists:

   | Blocker | What to do |
   |---|---|
   | running card with live processes | Let it finish. If bench-router started it, `bench-router collect --run-id RUN --cwd CWD`. |
   | running card with no live process (stale) | Nothing will ever finish it, and 3.2 refuses to switch while it is `running`. Copy `~/.local/share/shepherdr/tasks` aside, then run `herdr-task done ID --folder REPO` (`herdr-task reopen` undoes it). |
   | active admission | Run `bench-router collect --run-id RUN --cwd CWD`. If it stays active and the worker is gone: run `bench-router coordination status` for the key, then `bench-router coordination release --key KEY --confirmed-stopped --note "..."`. |
   | running card with no worktree recorded | The script cannot tell whether an agent still works on it. Look at the board, then wait or settle it. |
   | no `hc` | Install herdr-core first. |

   `check` only sees this machine. The installer also refuses while a linked machine has working tasks or
   cannot be reached; the dry run in step 5 shows that.

   Worktrees are not in the archive. `check` prints a `note:` for each finished card whose worktree holds
   uncommitted changes: commit, save or remove those before the switch.
2. **Close the Herdr app.** `backup` refuses while it runs. If `check` reports it in state `T` (stopped), it
   ignores TERM until it gets `kill -CONT PID`.
3. **Back up.** Run `eval/shepherdr_switch.sh backup`.
   - It stops `shepherdr.service` and writes `~/.local/backups/shepherdr/shepherdr-3.1.tar`, mode 0600, with a
     `.sha256` beside it.
   - It also saves the clone's HEAD and the `~/.local/bin` listing.
   - The archive holds secrets (`keys.json`, `vault.json`, the service token). Keep it on this host.
4. **Rehearse (optional, needs Docker).** This installs 3.2.19 over a copy of your archive in a throwaway
   container, rolls it back and compares. Do it on a host whose board you cannot afford to lose.
   ```sh
   eval/shepherdr-env/run.sh build v3.2.19     # once; copies this host's herdr-core into the image
   docker run --rm -i -u root --entrypoint bash \
     -e REPLICA_USER="$USER" -e REPLICA_UID="$(id -u)" -e REPLICA_HOME="$HOME" \
     -v ~/.local/backups/shepherdr/shepherdr-3.1.tar:/backup.tar:ro \
     -v "$PWD/eval/shepherdr_rehearsal.sh:/rehearsal.sh:ro" shepherdr-env:v3.2.19 /rehearsal.sh
   ```
   The last line must be `REHEARSAL PASS`: the same number of cards list before the install and after the
   rollback, and `herdr-task` points at the 3.1 payload again. The image has no bun, so the service and the web
   app are not exercised.
5. **Install.**
   ```sh
   git -C SRC fetch --tags && git -C SRC checkout v3.2.19
   shepherdr update --source SRC --dry-run   # must not print a "still working" line
   shepherdr update --source SRC --yes
   ```
   - The 3.1 `shepherdr update` hands over to the 3.2.19 installer in the checkout. It does not pull.
   - Never pass `--force`: it switches while cards are still working.
6. **Verify.**
   - `shepherdr doctor` exits 0 and ends with `✓ whole`.
   - `grep HC_SESSION ~/.config/systemd/user/shepherdr.service` shows `HC_SESSION=shepherdr`.
   - `systemctl --user is-active shepherdr` prints `active`.
   - `shepherdr where` shows layout 2.
   - `shepherdr web status` answers.
7. **Smoke test.** Run `eval/shepherdr_switch.sh smoke`.
   - It runs one headless task (default `claude-haiku-5-5` at `low`; set `SMOKE_MODEL`/`SMOKE_EFFORT` to a profile
     in your `profiles.toml`) in a throwaway repo.
   - It checks five things: the result was collected, Ready was handed off, the terminals were released, the
     admission was released, and the receipt is bound to session `shepherdr` with a core id.
   - On a pass it removes the card, the worktree and the repo. On a failure it keeps them and prints where they
     are.
8. **Hand back.**
   - Reopen the Herdr app. Shepherdr now lives in the web app, and its old views in the app show a notice.
   - Accept Codex's one-time prompt to trust its new hook.
   - Resume submissions.
   - Keep the archive until the new install has run for a while.

If any of steps 5 to 7 fails, roll back with section 6 of the runbook. Use the archive from step 3
(`shepherdr-3.1.tar`) wherever the runbook says `shepherdr-3.1.26.tar`. Do not restore `~/.herdr` from the
archive unless you also restore the board data: after the install it holds links to the moved data, and 3.1
reads the current cards through them.

## What these files were checked on

| Environment | `check` | `backup` | Rehearsal (install, rollback) | Real install | `smoke` |
|---|---|---|---|---|---|
| First host: WSL2, uid 1000, `/home/<user>`, layout 2, 100 cards | yes | by hand, same paths | pass | yes | pass |
| Docker replica of another host: uid 1500, home `/srv/op`, fresh 3.1.26, layout 1, 3 cards | yes (stale card found) | yes | pass | no (no bun) | no |

Not checked anywhere: a host with linked machines, a 3.1 web-only install, and non-default `XDG_*_HOME`.

## What surprised us on the first host (2026-11-27)

- **Stale running cards:** 11 of 12 `running` cards had no agent process; some were left over from 2026-11-18.
  The 3.2 check counts the card state, not processes, so these block the switch until settled.
- **Stopped app:** the Herdr app had been stopped (`T`) for hours. TERM only took effect after CONT.
- **Linked worktrees:** a run started from a linked git worktree became `delivery_uncertain`, because
  herdr-task files such cards under the main checkout. This is fixed in the merged port (`b4f6664`). Older runs
  of this kind collect once bench-router is updated.
- **Runs from before the port:** receipts written before the port have no `core_id`. They collect, but the router
  never stops or releases them. End their terminals by hand.
- **What the installer did on that host:**
  - It took 30 mods, 8 artifact mods, the layout and 74 other files out of `~/.config/herdr-app`.
  - It converted 8 artifacts to pages, which cannot be undone.
  - It carried `shepherdr.secrets` and `herdr-app` over from the `default` core session.
  - Its own backup of what it replaced went to `~/.local/share/shepherdr/.shepherdr-backup/<timestamp>/`.

## Switch record

| Date | Host | From → to | Blockers settled | Doctor | Smoke |
|---|---|---|---|---|---|
| 2026-11-27 | WSL2, hc 0.1.20 | 3.1.26 (`7d183cf7`) → 3.2.19 (`d2ed8301`) | 11 stale running cards marked done, 1 live card settled, Herdr app closed | ✓ whole | pass (run `6c407dde`) |
