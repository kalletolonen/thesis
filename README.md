# thesis

Turku University of Applied Sciences thesis repository

## Local LLMs with Ollama

This project uses [Ollama](https://ollama.com/) to run local large language models.

### Installation (macOS)

Install Ollama using Homebrew:

```bash
brew install ollama
brew services start ollama
```

### Models Used

We use the following models:

- `qwen2.5-coder:32b`
- `qwen2.5-coder:7b`

To pull them locally, run:

```bash
ollama pull qwen2.5-coder:32b
ollama pull qwen2.5-coder:7b
```

To run and interact with a model in your terminal:

```bash
ollama run qwen2.5-coder:32b
ollama run qwen2.5-coder:7b
```
