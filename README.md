# youtube-tldw
YouTube - Too Long; Didn't Watch

Python webapp to summarize YouTube videos. Tested on macOS. Requires [ollama](https://ollama.ai) to run on host.

## Ollama setup

Do not forget to pull at least [one model for Ollama](https://ollama.ai/library). Preferred are `mistral:latest` 🇫🇷 and `llama:latest`.

```
ollama pull <model_name>
```

## Local execution

```
pip install -r requirements
./src/app.py
```

Then access `http://localhost:5555`.

## Docker execution

```
make build
make run
```

or just `make all`.

Then access `http://localhost:5555`.
