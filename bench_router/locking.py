"""Non-blocking, process-wide file locks for the shared cache and each workspace."""
import contextlib
import errno
import os
import time


@contextlib.contextmanager
def exclusive(path, busy, wait_s=0):
    with open(path, "a+b") as f:
        if os.name == "nt":
            import msvcrt
            if f.seek(0, os.SEEK_END) == 0:
                f.write(b"\0")
                f.flush()
            f.seek(0)
        else:
            import fcntl
        deadline = time.monotonic() + wait_s
        while True:
            try:
                if os.name == "nt":
                    msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError as e:
                if not (e.errno in (errno.EACCES, errno.EAGAIN, errno.EDEADLK) or getattr(e, "winerror", None) == 33):
                    raise
                if time.monotonic() >= deadline:
                    raise busy from e
                time.sleep(0.01)
        try:
            yield
        finally:
            if os.name == "nt":
                f.seek(0)
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(f, fcntl.LOCK_UN)
