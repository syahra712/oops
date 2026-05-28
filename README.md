<div align="center">

# oops

**Type `oops` after a command fails. It figures out the fix and runs it.**

Like [`thefuck`](https://github.com/nvbn/thefuck), but it reads the actual error text with an LLM instead of matching predefined rules. Zero dependencies. Works offline with a local model — no API key needed.

[![PyPI](https://img.shields.io/pypi/v/oops-cli?v=2)](https://pypi.org/project/oops-cli/)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue?v=2)](https://pypi.org/project/oops-cli/)
[![License](https://img.shields.io/github/license/syahra712/oops?v=2)](https://github.com/syahra712/oops/blob/main/LICENSE)

</div>




https://github.com/user-attachments/assets/6792310d-14f6-4c59-8cbd-4a5f28681b4b



---

```console
$ git statsu
git: 'statsu' is not a git command. See 'git --help'.

$ oops
↻ reproducing: git statsu
🤖 thinking...

  git status

Run this? [Y/n] y
On branch main
nothing to commit, working tree clean
```

You mistyped a command, it failed, you sigh — and instead of squinting at the error you just type `oops`.

## Install

```bash
pip install oops-cli
oops-fix --install     # adds a tiny shell hook to ~/.zshrc / ~/.bashrc
source ~/.zshrc        # or ~/.bashrc, or open a new terminal
```

Then point it at a brain — pick one:

```bash
# Anthropic — fast and smart.   https://console.anthropic.com/
export ANTHROPIC_API_KEY=sk-ant-...

# Gemini — generous free tier.  https://aistudio.google.com/apikey
export GEMINI_API_KEY=...

# Groq — very fast, free tier.  https://console.groq.com/keys
export GROQ_API_KEY=...
```

Add the `export` line to `~/.zshrc` (or `~/.bashrc`) so it survives a new shell. Or skip the key entirely and stay fully offline with [Ollama](https://ollama.com): `ollama pull llama3.2`.

After any failed command, type `oops`.

## Your key, your machine

There is no server. `oops` reads the key from your shell environment and talks to the provider directly over HTTPS — nothing routes through me. The entire provider layer is [one short file](https://github.com/syahra712/oops/blob/main/oops/llm.py); read it if you're not sure.

## How it works

1. The shell hook hands `oops` the command you just ran.
2. `oops` re-runs it to capture the exact error output.
3. It asks the model for a corrected command.
4. It shows you the fix and runs it **only if you say yes.** Nothing executes without your confirmation.

## Caveats

- **It re-runs your failed command** to capture the error, so don't point it at anything destructive (deploys, `rm`, migrations). Re-running has side effects.
- **The shell hook can mis-capture multi-line pastes.** If you paste several commands at once, `oops` may pick the wrong one — type commands on their own lines instead. Fix is on the list.

## Config

| Env var | Default | What |
|---------|---------|------|
| `ANTHROPIC_API_KEY` | – | Use the Anthropic API |
| `GEMINI_API_KEY` | – | Use the Gemini API |
| `GROQ_API_KEY` | – | Use the Groq API |
| `OOPS_MODEL` | `claude-haiku-4-5-20251001` | Anthropic model |
| `OOPS_GEMINI_MODEL` | `gemini-2.0-flash` | Gemini model |
| `OOPS_GROQ_MODEL` | `llama-3.3-70b-versatile` | Groq model |
| `OOPS_OLLAMA_MODEL` | `llama3.2` | Local model name |
| `OOPS_OLLAMA_URL` | `http://localhost:11434` | Ollama endpoint |

Provider precedence: Anthropic → Gemini → Groq → local Ollama. The first key found wins.

## Why

The error message almost always contains the answer. `oops` just reads it for you so you don't have to context-switch. It's the difference between a 200ms `oops` and a 30-second detour to your browser.

## Contributing

Issues and PRs welcome. Good first ones: more providers (OpenAI, Mistral), a `--yes` auto-run flag, multi-suggestion mode, and a `--explain` mode that explains instead of fixing.

## License

[MIT](https://github.com/syahra712/oops/blob/main/LICENSE)
