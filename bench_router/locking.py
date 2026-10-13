"""Non-blocking, process-wide file locks for the shared cache and each workspace."""
import contextlib
import errno
import os


@contextlib.contextmanager
def exclusive(path, busy):
    with open(path, "a+b") as f:
        if os.name == "nt":
            import msvcrt
            if f.seek(0, os.SEEK_END) == 0:
                f.write(b"\0")
                f.flush()
            f.seek(0)
        else:
            import fcntl
        try:
            if os.name == "nt":
                msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as e:
            if e.errno in (errno.EACCES, errno.EAGAIN, errno.EDEADLK) or getattr(e, "winerror", None) == 33:
                raise busy from e
            raise
        try:
            yield
        finally:
            if os.name == "nt":
                f.seek(0)
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(f, fcntl.LOCK_UN)
