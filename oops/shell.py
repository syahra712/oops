"""Install a shell function so `oops` grabs your actual last command.

We can't reliably read the just-typed command from a child process, so we
install a tiny shell function that captures it with `fc` and forwards it to
the real entry point (`oops-fix`).
"""

import os
from pathlib import Path

HOOK = r"""
# >>> oops shell hook >>>
oops() {
    oops-fix "$(fc -ln -1 | sed 's/^[[:space:]]*//')"
}
# <<< oops shell hook <<<
""".strip()


def _rc_file() -> Path:
    shell = os.environ.get("SHELL", "")
    home = Path.home()
    if "zsh" in shell:
        return home / ".zshrc"
    return home / ".bashrc"


def install_hook():
    rc = _rc_file()
    existing = rc.read_text() if rc.exists() else ""
    if "oops shell hook" in existing:
        print(f"oops hook already installed in {rc}")
        return
    with rc.open("a") as f:
        f.write("\n" + HOOK + "\n")
    print(f"✓ Installed oops hook in {rc}")
    print(f"  Run:  source {rc}   (or open a new terminal)")
    print("  Then after any failed command, just type:  oops")
