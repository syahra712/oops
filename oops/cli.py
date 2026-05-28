"""oops — fix your last failed shell command with an LLM.

The shell function `oops` (installed via `oops --install`) passes your last
command here. We re-run it to capture the error, ask the model for a fix,
show it, and run it only if you say yes.
"""

import subprocess
import sys

from . import __version__
from .llm import LLMError, suggest_fix
from .shell import install_hook

_TTY = sys.stdout.isatty()


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _TTY else text


def dim(t):    return _c(t, "2")
def bold(t):   return _c(t, "1")
def red(t):    return _c(t, "31")
def green(t):  return _c(t, "32")
def yellow(t): return _c(t, "33")
def cyan(t):   return _c(t, "36")


def rerun(command: str, timeout: int = 20):
    """Re-run the command to capture its output. Returns (returncode, output)."""
    try:
        proc = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=timeout
        )
    except subprocess.TimeoutExpired:
        return None, "(command timed out while reproducing the error)"
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv

    if argv and argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if argv and argv[0] in ("-v", "--version"):
        print(f"oops {__version__}")
        return 0
    if argv and argv[0] == "--install":
        install_hook()
        return 0

    command = " ".join(argv).strip()
    if not command:
        print(red("oops: no command to fix."), file=sys.stderr)
        print(dim("Run `oops --install` to set up the shell hook, then just type "
                  "`oops` after a command fails."), file=sys.stderr)
        return 1

    print(dim(f"↻ reproducing: {command}"))
    code, output = rerun(command)

    if code == 0:
        print(green("✓ That command actually worked fine. Nothing to fix. 🤔"))
        return 0

    print(dim("🤖 thinking..."))
    try:
        fix = suggest_fix(command, output)
    except LLMError as e:
        print(red(f"oops: {e}"), file=sys.stderr)
        return 1

    fixed = fix["command"]
    if not fixed:
        print(yellow("oops: couldn't come up with a fix."))
        if fix["explanation"]:
            print(dim(fix["explanation"]))
        return 1

    if fix["explanation"]:
        print(f"\n{dim(fix['explanation'])}")
    print(f"\n  {bold(cyan(fixed))}\n")

    try:
        answer = input(f"Run this? {green('[Y/n]')} ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return 130
    if answer in ("", "y", "yes"):
        return subprocess.run(fixed, shell=True).returncode
    print(dim("ok, leaving it."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
