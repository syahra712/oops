<div align="center">

# oops

**Type `oops` after a command fails. It figures out the fix and runs it.**

LLM-powered command-line repair. Zero dependencies. Works with a local model — no API key, fully offline.

[![PyPI](https://img.shields.io/pypi/v/oops-cli)](https://pypi.org/project/oops-cli/)
[![Python](https://img.shields.io/pypi/pyversions/oops-cli)](https://pypi.org/project/oops-cli/)
[![License](https://img.shields.io/github/license/syahra712/oops)](https://github.com/syahra712/oops/blob/main/LICENSE)

</div>

<!-- DEMO VIDEO: replace the line below with your video URL.
     Get it from your repo's README on GitHub (the pencil/edit view) — it's the
     line that looks like https://github.com/user-attachments/assets/xxxxxxxx
     Paste that URL on its own line, with a blank line above and below it. -->

REPLACE_THIS_LINE_WITH_YOUR_VIDEO_URL

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
oops-fix --install   # adds a tiny shell hook to your .zshrc / .bashrc
source ~/.zshrc      # or ~/.bashrc, or just open a new terminal
```

That's it. After any failed command, type `oops`.

## Pick a brain

`oops` auto-detects a provider based on which key is set (checked in this order),
falling back to a local model if none are:

| Provider | Setup | Notes |
|----------|-------|-------|
| **Anthropic** | `export ANTHROPIC_API_KEY=...` | Fast, smart |
| **Gemini** | `export GEMINI_API_KEY=...` | Generous free tier |
| **Groq** | `export GROQ_API_KEY=...` | Very fast, free tier |
| **Local (Ollama)** | install [Ollama](https://ollama.com), `ollama pull llama3.2` | No key, fully offline, free |

## How it works

1. The shell hook hands `oops` the command you just ran.
2. `oops` re-runs it to capture the exact error output.
3. It asks the model for a corrected command.
4. It shows you the fix and runs it **only if you say yes.**

Nothing executes without your confirmation.

## Config

| Env var | Default | What |
|---------|---------|------|
| `ANTHROPIC_API_KEY` | – | Use the Anthropic API |
| `GEMINI_API_KEY` | – | Use the Google Gemini API |
| `GROQ_API_KEY` | – | Use the Groq API |
| `OOPS_MODEL` | `claude-haiku-4-5-...` | Anthropic model |
| `OOPS_GEMINI_MODEL` | `gemini-2.0-flash` | Gemini model |
| `OOPS_GROQ_MODEL` | `llama-3.3-70b-versatile` | Groq model |
| `OOPS_OLLAMA_MODEL` | `llama3.2` | Local model name |
| `OOPS_OLLAMA_URL` | `http://localhost:11434` | Ollama endpoint |

## Why

The error message almost always contains the answer. `oops` just reads it for you so you don't have to context-switch. It's the difference between a 200ms `oops` and a 30-second detour to your browser.

## A note on safety

`oops` re-runs your command to read its error, then runs the suggested fix only after you confirm. It's built for the common cases — typos, wrong flags, missing files. Don't point it at destructive commands.

## Contributing

Issues and PRs welcome. Good first ones: more providers (OpenAI, Mistral), a `--yes` auto-run flag, multi-suggestion mode, and a `--explain` mode that explains instead of fixing.

## License

[MIT](https://github.com/syahra712/oops/blob/main/LICENSE)
