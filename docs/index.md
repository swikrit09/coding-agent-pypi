# coding-agent-python


**PyPi Link** - [Coding-Agent-Python](https://pypi.org/project/coding-agent-python/)

`coding-agent-python` is a small CLI wrapper around Google GenAI (Gemini) to run prompt-based agents that may call out to local helper functions.  
This repo provides an installable package with a `coding-agent-python` command-line entry point and a Python module `coding_agent` for programmatic usage.

> ⚠️ This project expects a Gemini API key in your environment (see **Configuration**).

---

## Features

- Installable package via `pip` (supports editable installs for development).
- Console script `coding-agent-python` for quick prompt runs.
- Includes a `call_function` helper module so the model can request function execution.
- Designed to be small and extensible.

---

## Quick install

**From PyPI (when published):**

```bash
pip install coding-agent-python
````

**From local source (editable, for development):**

```bash
# inside a virtualenv
pip install -e .
```

**From local source (non-editable wheel):**

```bash
python -m build
pip install dist/coding_agent-0.1.0-py3-none-any.whl
```

---

## Configuration
Create a `.env` file in the project root (or set environment variables). At minimum set:

```
GEMINI_API_KEY=your_real_gemini_api_key_here
```

To source the environment variables:

**Bash/Terminal:**
```bash
source .env
# or
export $(cat .env | xargs)
```

**PowerShell:**
```powershell
Get-Content .env | ForEach-Object {
    $name, $value = $_.split('=')
    Set-Content env:\$name $value
}
```

**Command Prompt (Windows):**
```cmd
for /f "tokens=1,2 delims==" %G in (.env) do set %G=%H
```

The package uses `python-dotenv` to load `.env` at runtime.
```
GEMINI_API_KEY=your_real_gemini_api_key_here
```

The package uses `python-dotenv` to load `.env` at runtime.

---

## Usage

### CLI

After installing (and activating your virtualenv if needed):

```bash
# Run the CLI; wrap your prompt in quotes
coding-agent "Write a Python script for calculation"
```

If `coding-agent` is not available on your PATH, you can run it with the module mode:

```bash
python -m coding_agent "Write a Python script for calculation"
```

### Programmatic

You can call the core runner from Python:

```python
from coding_agent.cli import run

# run returns None and prints output; you can modify run() to return values for tests
run("Write a small script that computes factorial", verbose=True)
```

---

## Development

Recommended project layout: use `src/` layout to avoid accidental packaging of extra top-level folders.

```
coding-agent-python/
├─ pyproject.toml
├─ README.md
├─ LICENSE
├─ src/
│  └─ coding_agent/
│     ├─ __init__.py
│     ├─ cli.py
│     ├─ __main__.py
│     ├─ config.py
│     └─ functions/
│        └─ call_function.py
├─ streamlit_app.py
├─ main.py
└─ tests/
```

Install development dependencies and editable install:

```bash
# inside a virtualenv
pip install -r requirements-dev.txt
pip install -e .
```

Made with 💖 by Swikrit and open for contributions