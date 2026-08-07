"""Probe harness — runs ONE round under an audit hook and writes NOTHING.

Classification, by exit code:
    3   BROKEN INPUT   a read-open resolved to a path that does not exist
    4   REACHED WRITE  inputs all resolved; the round tried to write inside the repo
    0   COMPLETED      finished without ever writing inside the repo
    1   OTHER ERROR    raised something else
    124 TIMEOUT        (applied by the caller) -> UNVERIFIED, never "ok"

The write block is scoped to the repo root ONLY. Blocking every write would break imports,
byte-compilation and library caches, and would then be indistinguishable from a real defect --
which is the failure mode this whole project keeps hitting. Writes to /tmp, site-packages and
anywhere outside the tree are allowed through untouched.
"""
import io
import os
import pathlib
import runpy
import sys

ROOT = pathlib.Path(sys.argv[1]).resolve()
TARGET = pathlib.Path(sys.argv[2]).resolve()
STATE = {"missing": None, "wrote": None}
# Library and cache territory. A miss in here is a normal import probe, never a round's input.
EXCLUDE = {".venv", "site-packages", "__pycache__", ".git", "node_modules", ".mypy_cache",
           ".pytest_cache", ".ruff_cache"}


def _hook(event, args):
    if event != "open":
        return
    path, mode = args[0], args[1]
    if not isinstance(path, (str, bytes, os.PathLike)) or mode is None:
        return
    try:
        p = pathlib.Path(os.fsdecode(path))
    except Exception:
        return
    if any(c in str(mode) for c in "wax+"):
        try:
            inside = p.resolve().is_relative_to(ROOT)
        except Exception:
            inside = False
        if inside and ".git" not in p.parts:
            STATE["wrote"] = str(p)
            raise PermissionError(f"__PROBE_WRITE_BLOCKED__ {p}")
        return
    if "r" in str(mode) and not p.exists():
        # A read of a nonexistent path is only decisive INSIDE the repo. Imports probe dozens
        # of nonexistent module paths on every startup and those are not defects.
        # ⚠ AND "INSIDE THE REPO" IS NOT ENOUGH -- measured, not anticipated. The first sweep
        # returned 15 broken rounds of which 4 were the INSTRUMENT: three rounds "failed" on
        # `.venv/.../markupsafe-3.0.3.dist-info/entry_points.txt` and one on a `__pycache__`
        # .pyc that had simply not been written yet. Both are libraries probing for optional
        # files, and both live under ROOT because the venv is in-tree. A 27% over-count, and it
        # would have been reported as repository breakage.
        if any(part in EXCLUDE for part in p.parts) or p.suffix in (".pyc", ".pyo"):
            return
        try:
            inside = p.resolve().is_relative_to(ROOT)
        except Exception:
            inside = False
        if inside and ".git" not in p.parts and STATE["missing"] is None:
            STATE["missing"] = str(p)


sys.addaudithook(_hook)
sys.argv = [str(TARGET)]
os.chdir(TARGET.parent)
code = 0
try:
    runpy.run_path(str(TARGET), run_name="__main__")
except PermissionError as e:
    code = 4 if "__PROBE_WRITE_BLOCKED__" in str(e) else 1
except SystemExit as e:
    code = 0 if not e.code else (1 if STATE["missing"] is None else 3)
except FileNotFoundError:
    code = 3
except Exception:
    code = 1
if STATE["missing"] and code in (1, 3):
    code = 3
sys.stderr.write(f"__PROBE__ missing={STATE['missing']} wrote={STATE['wrote']}\n")
os._exit(code)
