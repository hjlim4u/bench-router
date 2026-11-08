"""Owned subprocess lifecycle shared by CLI usage collectors."""
import os
import signal
import subprocess
import tempfile

CALL_TIMEOUT_S = 120


def run_cli(cmd, *, timeout=CALL_TIMEOUT_S, **kwargs):
    """Own only this probe's process group. Give CodexBar time to cancel its native children first."""
    with tempfile.TemporaryFile() as output:
        with subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=output, stderr=subprocess.DEVNULL,
                              start_new_session=True) as proc:
            try:
                proc.wait(timeout=timeout)
            finally:
                if proc.poll() is None:
                    try:
                        proc.terminate()
                        proc.wait(timeout=5)
                    except (ProcessLookupError, subprocess.TimeoutExpired):
                        pass
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                proc.wait()
            output.seek(0)
            return subprocess.CompletedProcess(cmd, proc.returncode, output.read(8 * 1024 * 1024 + 1).decode("utf-8", "replace"))
