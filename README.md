# youtube-tldw
YouTube - Too Long; Didn't Watch

Python webapp to summarize YouTube videos. Tested on macOS. Requires [ollama](https://ollama.ai) to run on host.

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

Then access `http://localhost:5555`.
