"""Board port: the router's only view of a task board (Shepherdr today).

The adapter translates board JSON and terminal labels into the values below; the router
(herdr.py) owns receipts, event logs and success decisions. This module is stdlib-only
and must not import herdr or Shepherdr code.

Receipt identifiers: create/start/resume return these keys, which the router copies into
the receipt unchanged. The Shepherdr adapter keeps the names so shepherdr-3 receipts load:
  thread_id          board card key (Shepherdr "key", e.g. "BR-12")
  task_id_on_board   board-internal card id (Shepherdr integer "id")
  terminal_id        terminal the agent runs in
  worktree, branch   where the agent works (start only)
Formats are adapter-private; the router compares them only for equality.

Observation (observe and stop return the same shape):
  task      the board's view, one of TASK_STATES, or None when retryable is True:
    not_started  card exists, never started            (Shepherdr: todo)
    queued       accepted, waiting for a slot          (queued, scheduled)
    working      running with a live working worker    (running + live worker "working")
    blocked      waiting for a human                   (status=needs, needs not in reply/stopped)
    turn_done    the turn ended; validate the result  (ready, done, or all live workers idle/done)
    stopped      agent stopped                         (needs=stopped)
    turn_done is not success: the router decides success from the run's result files.
  process   terminal evidence, one of PROCESS_STATES (from hc get state, ls --label):
    live | exited | gone | unknown
  identity  "ok" | "mismatch"; mismatch = the card/terminal found is not the one recorded
            (or a resumed session was not the recorded one) -> manual reconciliation, never auto-repair
  retryable True when the read failed transiently; task is then None and nothing else is inferred
  why       board-provided reason text or None
  ids       identifiers found by lookup (only when rc had none; see create row below)

Identifier persistence contract (the adapter only returns identifiers; the router persists):
| op      | router stores before call          | router stores on success   | on lost response                                          |
| create  | delivery_state=submission_attempted| returned ids               | delivery_uncertain; no re-call; lookup only by run-id title |
| start   | start_attempted                    | terminal/worktree/branch   | delivery_uncertain; no restart; only observe stored card  |
| resume  | resume_attempted                   | new terminal id            | no re-call; observe identity then manual reconciliation   |
| tell    | send attempt in event log          | send confirmed             | no automatic resend                                       |
| stop    | stop_sent in event log             | process=exited evidence    | keep admission; re-observe                                |
| handoff | ready.state=attempted              | board-given state          | uncertain; no re-call                                     |
"Lookup by run-id title": create titles the card with rc["run_id"]; observe(rc) on a receipt
without thread_id finds the card by that title only and returns its identifiers in "ids".
"""
from typing import Protocol, runtime_checkable

from .routing import InputError

TASK_STATES = frozenset({"not_started", "queued", "working", "blocked", "turn_done", "stopped"})
PROCESS_STATES = frozenset({"live", "exited", "gone", "unknown"})
CAPABILITIES = frozenset({"tell", "resume"})

# Rows of the persistence table above: op -> (before call, on success, on lost response).
PERSISTENCE = {
    "create": ("delivery_state=submission_attempted", "returned ids", "delivery_uncertain; no re-call; lookup only by run-id title"),
    "start": ("start_attempted", "terminal/worktree/branch", "delivery_uncertain; no restart; only observe stored card"),
    "resume": ("resume_attempted", "new terminal id", "no re-call; observe identity then manual reconciliation"),
    "tell": ("send attempt in event log", "send confirmed", "no automatic resend"),
    "stop": ("stop_sent in event log", "process=exited evidence", "keep admission; re-observe"),
    "handoff": ("ready.state=attempted", "board-given state", "uncertain; no re-call"),
}


@runtime_checkable
class Board(Protocol):
    """A task board. Every method takes the receipt dict rc read-only; none persists anything.

    Errors: unsupported protocol/capability or a changed binding -> InputError (nothing submitted).
    Any other exception from a mutating call is a lost response: the router follows PERSISTENCE.
    """
    backend: str
    capabilities: frozenset  # subset of CAPABILITIES

    def bind(self, session, cwd) -> dict:
        """Check connection and protocol; return the binding (protocol, space, version...). Unsupported -> InputError."""

    def create(self, rc) -> dict:
        """Create the card titled rc["run_id"]; do not start it. Return {thread_id, task_id_on_board}."""

    def start(self, rc) -> dict:
        """Re-validate rc["binding"] against bind() right before submission (changed -> InputError, nothing sent),
        then start the card. Return {terminal_id, worktree, branch}."""

    def observe(self, rc) -> dict:
        """Return an observation (see module docstring). Never mutates the board."""

    def stop(self, rc) -> dict:
        """Ask the agent to stop, then return an observation: process=exited is termination evidence;
        a successful request alone is not."""

    def handoff(self, rc) -> str:
        """Ready handoff to the human; return the board-given state."""

    def cleanup(self, rc) -> dict:
        """Close this run's terminals. Return {closed: [terminal ids], left_open: reason or None}."""

    def tell(self, rc, text) -> None:
        """Send text to the running agent. Requires "tell" in capabilities, else InputError."""

    def resume(self, rc) -> dict:
        """Resume the agent session. Requires "resume" in capabilities, else InputError.
        Return {terminal_id: new id, resumed: whether the recorded session was resumed}."""


def observation(task, process, identity="ok", retryable=False, why=None, **extra):
    """Build and validate an observation; adapters should return through this."""
    if retryable:
        task = None
    elif task not in TASK_STATES:
        raise ValueError(f"unknown task state: {task!r}")
    if process not in PROCESS_STATES or identity not in ("ok", "mismatch"):
        raise ValueError(f"bad observation: process={process!r} identity={identity!r}")
    return {"task": task, "process": process, "identity": identity, "retryable": bool(retryable), "why": why, **extra}
