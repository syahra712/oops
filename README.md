<div align="center">

# oops

**Type `oops` after a command fails. It figures out the fix and runs it.**

LLM-powered command-line repair. Zero dependencies. Works with a local model — no API key, fully offline.

<!-- Record a terminal GIF and drop it here before launch. This single GIF
     is the most important asset in the whole repo. Try `vhs` or `asciinema`. -->
<img src="docs/demo.gif" alt="oops demo" width="600">

</div>

---

```console
$ git statsu
git: 'statsu' is not a git command. See 'git --help'.

$ oops
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
oops --install      # adds a tiny shell hook to your .bashrc / .zshrc
source ~/.bashrc    # or just open a new terminal
```

That's it. After any failed command, type `oops`.

## Pick a brain

`oops` auto-detects a provider:

| Provider | Setup | Notes |
|----------|-------|-------|
| **Anthropic** | `export ANTHROPIC_API_KEY=...` | Fast, smart, default if the key is set |
| **Local (Ollama)** | install [Ollama](https://ollama.com), `ollama pull llama3.2` | No key, fully offline, free |

If `ANTHROPIC_API_KEY` is set it uses that; otherwise it falls back to a local Ollama model.

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
| `OOPS_MODEL` | `claude-haiku-4-5-...` | Anthropic model |
| `OOPS_OLLAMA_MODEL` | `llama3.2` | Local model name |
| `OOPS_OLLAMA_URL` | `http://localhost:11434` | Ollama endpoint |

## Why

The error message almost always contains the answer. `oops` just reads it for you so you don't have to context-switch. It's the difference between a 200ms `oops` and a 30-second detour to your browser.

## Contributing

Issues and PRs welcome. Good first ones: more providers (OpenAI, Gemini, Groq), a `--yes` auto-run flag, multi-suggestion mode, and a `--explain` mode that explains instead of fixing.

## License

MIT
