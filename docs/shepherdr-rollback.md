# Shepherdr 3.1.26 → 3.2.19 backup, rehearsal and rollback

This is the operator runbook for plan step 5 (work unit T10). A person runs every command in it. Agents
only prepared it, from a read-only survey of the host on 2026-11-27 and from the 3.1.26 and 3.2.19 sources.
No Shepherdr, `herdr-task` or `hc` command was run on the host. Paths use `~` for the operator's home.

Gate G3 (approval to switch) needs a passed rehearsal (section 4). The switch itself (T11, section 5)
covers one repository at a time.

## 1. Baseline: what is installed now

- **Shepherdr 3.1.26.** It is installed from the clone `~/shepherdr`, at commit `7d183cf7`
  (`git describe`: `v3.1.26-2-g7d183cf7`). Both install records say `3.1.26`:
  `~/.config/herdr-app/data/shepherdr/installed.json` and `~/.local/share/shepherdr/installed.json`.
- **The data has already moved to the 3.2 layout.** `~/.local/state/shepherdr/migrate.json` records the move:
  `settings`, `tasks`, `artifacts`, `vault`, `service`, `browser` and `cli-check` are all `moved`, at
  2026-11-26 15:05 KST. `~/.local/share/shepherdr/LAYOUT` is `2`. Each `~/.herdr/<kind>` is now an absolute
  symlink into the XDG folders, so 3.1.26 (which has no layout code) still reads `~/.herdr/tasks` and works.
  - The journal does not say which program made this move. Treat the layout-2 state, with its links, as
    the baseline you restore to. Do not run `shepherdr migrate --rollback` to reach it.
- **`~/.herdr/worktrees` was not moved.** It is a real directory of about 3.6 GB after the cleanup below. The new
  `~/.local/share/shepherdr/worktrees` is empty.
- **Two core sessions exist under `~/.local/state/herdr-core/`.**
  - `default` is live. It is shared with the Herdr app and has a holder socket under
    `/run/user/1000/herdr-core/`.
  - `shepherdr` is a stale directory from 2026-11-26, with no process.
- **Running processes:**
  - the `shepherdr.service` user unit (bun, `Restart=always`);
  - `herdr-core serve` and `herdr-core hold` for `default`;
  - the Herdr app GUI;
  - the 3.1 `herdr-task scheduler`.
- **Board.** There are 98 cards in 12 folder files. At survey time 11 cards were `running`.
- **bench-router.** No admission record was active and no receipt was unsettled. No current receipt has a
  `core_id`: they were written before the port.
- **Binaries outside the clone.** The 3.2.19 installer does not install or replace
  `~/.local/bin/herdr-core` or `~/.local/share/herdr-app/herdr-app`. `bin/shepherdr` only checks that
  `hc` 0.1.17 or newer is on the PATH and that the Herdr app exists. So the switch leaves both binaries alone.
  Update them separately, if at all.

## 2. Locations

The Kind column says what each location holds: binary, config, board data, secret store, core runtime,
journal, backup, worktree, receipt or admission. Mode is noted only where it matters.

The **Switch** column says whether the 3.2.19 installer (`bin/shepherdr install`, `layout.migrate`) changes the
location, and therefore whether section 3 backs it up.
- **yes**: the installer changes or removes it, and it is backed up.
- **no**: the installer leaves it alone, and it is not backed up.
- **record**: only its listing is saved.

| Location | Kind | Switch | Notes |
|---|---|---|---|
| `~/.local/bin/{herdr-task,shepherdr,herdr-secret,herdr-browser,herdr-artifact}` | symlinks | yes | They point into `~/.config/herdr-app/{bin,mods/*/bin}` (3.1). 3.2 repoints them into `~/.local/share/shepherdr` and records what it replaced; `uninstall` puts those back. |
| `~/.local/bin/herdr-core`, `hc → herdr-core` | binary | no | The installer only checks that `hc` is 0.1.17 or newer. |
| `~/.local/share/herdr-app/`, `~/.local/share/herdr-app-ime/`, `~/.local/bin/herdr-app` | Herdr app GUI and IME wrapper | no | 3.2 only checks that the app exists. |
| `~/shepherdr` | source clone | record | It is the 3.1 install source; the rollback reinstalls from commit `7d183cf7`. It has tags only up to v3.1.x. |
| `~/.config/herdr-app/` | 3.1 payload and config | **yes** | 3.2 removes the 3.1 mods, layout, `lib/`, `core/`, `bin/`, Shepherdr's keys in `keys.json` (0600, secret) and the 3.1 install record. It adds `mods/open-shepherdr`. `data/` (mod data and 3.1 board backups) is not removed, but it is part of the same tree. |
| `~/.config/herdr-app/.shepherdr-backup/20261109-165305/` | 3.1 install backup | (inside the above) | Holds what the 3.1 install replaced. **Its `keys.json` is 0644 and should be 0600.** |
| `~/.local/state/herdr-app-migration/20261109-*/` | config snapshot | no | The configs from before the 3.1 install. |
| `~/.config/shepherdr/` | config | **yes** | 3.2 settings migrations rewrite it (moving per-space task settings and old instructions). |
| `~/.config/herdr-core/templates/` | role templates | no | 3.2 never overwrites a changed template; it writes `<file>.new` beside it. |
| `~/.config/herdr/` (including its plugins, such as ovis via `~/.config/herdr-web-ui → ~/.config/ovis`) | Herdr config | no | The installer does not touch `~/.config/herdr`. |
| `~/.config/systemd/user/shepherdr.service` | unit (0600) | **yes** | 3.2 rewrites it with `HC_SESSION=shepherdr`. |
| `~/.claude/settings.json`, `~/.codex/hooks.json` | agent hooks | **yes** | 3.2 removes the 3.1 `…/herdr-app/mods/chat/` hooks and adds its own (skipped with `--no-hooks`). |
| `~/.local/share/shepherdr/` | payload **and** data | **yes** | The payload (`service/`, `bin/`, `core/`, `mods/`, `web/`, `installed.json`) is replaced whole. Next to it are `tasks/` (3.2 adds fields such as `project_id`), `artifacts/` (converted one-way to pages), `secrets/` (0700, `vault.json` 0600) and `LAYOUT`. |
| `~/.local/state/shepherdr/` | service state, move journal | **yes** | `service/` (`token` and `service.json`, 0600, plus the socket), `migrate.json`, `sync-hold`. |
| `~/.herdr/` (except `worktrees/`) | legacy links | **yes** | The compatibility links, `cli-check.json` and `sync-hold`. 3.2 heals the links. |
| `~/.herdr/worktrees/` | task worktrees (about 3.6 GB) | no | Worktrees never move. Branches stay in their repositories. |
| `~/.local/state/herdr-core/<session>/` (0700) | core runtime | no | The installer copies shared documents from `default` into `shepherdr` and moves idle agents there. It only reads `default`, and terminals cannot be restored as processes anyway. |
| `<repo>/.bench-router/`, `~/.local/state/bench-router/coordination/`, `~/.config/bench-router/` | receipts, admission, profiles | no | Shepherdr does not touch them. |

## 3. Backup (before the switch, and before the rehearsal)

1. **Quiesce.**
   - Stop new submissions: no `bench-router route` or `parallel`, and no new board tasks.
   - Wait until no card is `running` or `working`, or stop each card deliberately. 3.2 refuses to switch while
     tasks are working, unless forced. Never force it.
   - Confirm that bench-router has no active admission:
     `grep -l '"active": true' ~/.local/state/bench-router/coordination/*.json` must print nothing.
2. **Record what the switch does not back up.**
   ```sh
   git -C ~/shepherdr rev-parse HEAD
   ls -l ~/.local/bin > ~/shepherdr-switch-bin-links.txt
   ```
   Do not run `hc` to read the core id: `~/.local/state/herdr-core/default/core.json` already holds it.
3. **Stop the writers so the copy is consistent.**
   - Run `systemctl --user stop shepherdr.service`.
   - Close the Herdr app, which stops the 3.1 scheduler and the chat tabs.
   - The `default` core can keep running: nothing it owns is in the archive.
4. **Archive only what the installer changes** (the **yes** rows in section 2). Keep permissions, and keep
   the absolute paths, because the `~/.herdr` links are absolute. `B` is a 0700 folder that no sync tool
   watches; `/var/backups` needs root.
   ```sh
   B=~/.local/backups/shepherdr && mkdir -p -m 700 "$B"
   cd / && tar --create --preserve-permissions --xattrs --acls --numeric-owner \
     --exclude="home/$USER/.herdr/worktrees" -f "$B/shepherdr-3.1.26.tar" \
     home/$USER/.config/herdr-app home/$USER/.config/shepherdr \
     home/$USER/.config/systemd/user/shepherdr.service \
     home/$USER/.config/systemd/user/default.target.wants/shepherdr.service \
     home/$USER/.claude/settings.json home/$USER/.codex/hooks.json \
     home/$USER/.local/share/shepherdr home/$USER/.local/state/shepherdr home/$USER/.herdr \
     home/$USER/.local/bin/herdr-task home/$USER/.local/bin/shepherdr home/$USER/.local/bin/herdr-secret \
     home/$USER/.local/bin/herdr-browser home/$USER/.local/bin/herdr-artifact
   chmod 600 "$B/shepherdr-3.1.26.tar"
   sha256sum "$B/shepherdr-3.1.26.tar" > "$B/shepherdr-3.1.26.tar.sha256"
   ```
   - The archive contains secrets: `vault.json`, `keys.json` and the service `token`. Keep it on this machine
     and out of any synced folder.
   - `~/.herdr/worktrees` is left out because the switch never moves it. Before the switch, remove the
     worktrees of finished cards (see "Worktree cleanup" below) and make sure the rest are committed.
5. Optionally, fix the 0644 `keys.json` in `.shepherdr-backup/20261109-165305/` with `chmod 600`.
6. Restart the 3.1 services (`systemctl --user start shepherdr.service`, then open the Herdr app). Check that
   the board shows the same card count.

## 4. Rehearsal on a replica (gate for G3)

**Pass criterion:** on a replica, the old Shepherdr payload and links, the data and the session settings are
restored together, and the existing tasks open. The image already has `hc` 0.1.20 (a copy of the host's
binary), so the replica exercises the same core.

1. Start a throwaway container from `eval/shepherdr-env` (`shepherdr-env:v3.1.26`, Ubuntu 24.04). Use a
   user whose home path matches the host's, because the `~/.herdr` links are absolute. Mount the archive
   read-only.
   ```sh
   docker run --rm -it -u root -v "$B/shepherdr-3.1.26.tar":/backup.tar:ro shepherdr-env:v3.1.26 bash
   # inside: useradd -m -d /home/<user> <user>; cd / && tar -xpf /backup.tar --numeric-owner; chown -R <user> /home/<user>
   ```
   Nothing of the host besides the archive is mounted. No systemd user manager runs here: start the service
   by hand only if you need it.
2. **Check the old payload and session settings.** As that user:
   - `readlink ~/.local/bin/herdr-task` shows the 3.1 path (`~/.config/herdr-app/mods/tasks/bin/herdr-task`).
   - `grep -c HC_SESSION ~/.config/systemd/user/shepherdr.service` prints 0.
   - `cat ~/.local/share/shepherdr/LAYOUT` prints `2`, and the `~/.herdr/*` links resolve (`ls -L ~/.herdr`).
3. **Check that the existing tasks open.**
   - `herdr-task list --json` shows the same 98 cards and folders as the host.
   - `herdr-task show <key> --folder <repo> --json` opens a done card and a running card.
   - The core starts in `default` (`hc server status --json` reports session `default`; inside the replica
     this probe is allowed).
   - Terminals from the host do not come back as processes, and task worktrees are not in the archive. That
     is expected: running cards show no live worker and no worktree.
4. **Run the 3.2 forward path on the same replica.** In the container, check out `v3.2.19` in `~/shepherdr`,
   run `shepherdr update` (or `install.sh --no-hooks --yes`), then `shepherdr doctor` and `shepherdr where`.
   Write down:
   - which kinds moved (expected: none, because the layout is already 2);
   - that the backup folder `~/.local/share/shepherdr/.shepherdr-backup/<ts>/` appeared;
   - that `HC_SESSION=shepherdr` is in the unit.
5. **Roll the replica back with section 6**, then repeat steps 2 and 3. The rehearsal passes when both
   checks pass after the rollback.
6. Record the result (date, image tag, card counts, any differences) at the end of this file before asking
   for G3.

## 5. Switch one repository (T11, a person runs it)

1. Do sections 3.1 to 3.4 again on the day of the switch, so the archive is fresh.
2. Fetch the tag (`git -C ~/shepherdr fetch --tags`), check out `v3.2.19`, and run `shepherdr update`.
   Then run `shepherdr doctor`; it must exit 0.
3. Check four things:
   - the session settings (`HC_SESSION=shepherdr` in the unit, and no `SHEPHERDR_SESSION` unless intended);
   - `shepherdr where`;
   - `shepherdr web status`;
   - which session your terminal tools attach to. `~/.profile` exports `HERDR_SESSION`; check its value.
4. Reinstall the bench-router runtime from the merged port (`uv tool install --force <checkout>`). The port
   reads the core session from the installed release. Then, in one repository, run one synthetic task through
   `bench-router --runner herdr route` and check:
   - the result was collected;
   - Ready was handed off;
   - the run's terminals were released;
   - its admission record was released.
5. Only then resume normal submissions.

## 6. Rollback (if the switch fails)

1. **Stop new submissions.** Keep the post-switch work: archive the current state with the same `tar` command
   to `"$B/shepherdr-3.2.19-failed.tar"` before changing anything.
2. **Settle or stop the 3.2 work.** List the agents in the `shepherdr` session. Note each card that is
   running there, because those agents will not move back by themselves.
3. **Remove 3.2.** Run `systemctl --user stop shepherdr.service`, then `shepherdr uninstall`. Uninstall
   removes only the files whose hashes match its record. It keeps the data folders and puts back the
   `~/.local/bin` links it replaced.
4. **Restore 3.1.**
   - Restore from the archive every payload and config path in section 3.4. Do not restore the board data
     yet: `tasks/`, `artifacts/` and `secrets/` under `~/.local/share/shepherdr`.
   - Restoring the payload restores the 3.1 window layout, mods and hooks, the 3.1 unit file and the
     `~/.local/bin` links. The 3.2 installer removed the 3.1 layout and mods, and only the archive (or the
     3.1 installer) brings them back. `herdr-core` and the Herdr app were not changed by the switch.
   - Or check out commit `7d183cf7` in `~/shepherdr` and re-run the 3.1 installer with the original flags.
     Then compare the result with the archive.
5. **Board data.** 3.2 adds fields to the card JSON; it does not remove any. So keep the current
   `tasks/`, which holds the post-switch cards, if 3.1 lists it cleanly. If `herdr-task list` fails or loses
   cards, restore `tasks/` from the archive, then re-enter the post-switch cards by hand from the
   `3.2.19-failed` archive.
   - Converted artifacts (recipes turned into pages) cannot be converted back. Restore `artifacts/` from the
     archive if 3.1 needs them.
6. **Restart.** Run `systemctl --user daemon-reload && systemctl --user start shepherdr.service`, then
   open the Herdr app.
   - Check `readlink ~/.local/bin/herdr-task` and the card count.
   - Run `grep -c HC_SESSION ~/.config/systemd/user/shepherdr.service`; it must print 0.
7. **bench-router.**
   - Receipts started under 3.2 recorded session `shepherdr`. After a rollback they collect as
     `delivery_uncertain`, by design: reconcile them by hand on the board.
   - Admission records of those runs stay `active` until reconciled.
   - The router itself need not roll back: the port supports both releases.

## 7. Known gaps

- Nobody has run 3.1.26 against card data that 3.2 wrote. The rehearsal's step 4 and 5 is the first check.
- `herdr-core` and `herdr-app` have no versioned copies on disk. The switch does not change them, so they
  are out of this runbook. Updating them is a separate change with its own backup.
- The program that performed the 2026-11-26 layout move is unknown. Its journal lists kinds only, with no
  from/to paths.
- Agents and terminals never survive a restore as processes. Running cards need to be restarted by hand.
- 3.2 moves idle agents from `default` to `shepherdr` and copies shared documents into `shepherdr`. Undoing
  those moves is not automated.
- Receipts written before the port have no `core_id`. The router can collect them, but it will not stop or
  release them; end those terminals by hand.

## Worktree cleanup (done 2026-11-27)

The runbook leaves `~/.herdr/worktrees` out of the archive. Its worktrees were checked before that decision:
- each worktree was matched to its card (`worktree` field);
- `git status --porcelain` showed whether it had uncommitted changes;
- `git cherry <base> HEAD` showed whether its commits were already in the base, as the same patch.

| Group | Action |
|---|---|
| 6 `done` cards, clean | Removed with `git worktree remove`. Their branches stay. 5 had all commits in the base. 1 has a commit that is not in the base and is still on its branch. |
| 3 router worktrees under `.bench-router/` | Removed, with their `br/*` branches. Every commit is in `shepherdr-port/T8fix`. |
| 3 `done` cards with uncommitted changes | Kept, because removing them would discard those changes. Commit or discard them by hand. |
| 11 `running` and 10 `ready` cards | Kept, because they are not finished. A `ready` card waits for the person to accept it. |
| 1 orphan (`~/.herdr/worktrees/bench-router/work-1-review-selection-redesign-plan`, 2026-10-20) | Kept. Its `.git` points to a worktree record that no longer exists, so git cannot tell what it holds. Delete it by hand once you have checked it. |

## Rehearsal record

| Date | Image | Before: cards / folders | After rollback: cards / folders | Result | Notes |
|---|---|---|---|---|---|
| | | | | | |
