# Chess app

A simple chess app with a Tkinter board, local match tracking, and optional AI support. It works as a normal Python project and can also be packaged as a zipapp for easier sharing.

## What it does

- Human vs Human
- Human vs AI
- AI vs AI demo mode
- Move history and captured pieces
- Undo, resign, and draw actions
- Save and load games as JSON
- Optional AI commentary and hints

## Requirements

- Python 3.11+
- Tkinter
- python-chess

Install the base dependency:

```bash
pip install -r requirements.txt
```

If you want the AI modes, install the SDKs for the providers you plan to use:

```bash
pip install openai google-generativeai
```

## Run it locally

From the project folder:

```bash
python -m chess_app
```

Or:

```bash
python __main__.py
```

## Build the zipapp

From the project root:

```bash
python -m zipapp . -o chess.pyz -p "/usr/bin/env python3"
```

Then launch it with:

```bash
python chess.pyz
```

The project includes the main dependency in the repo when needed, so the basic chess experience still works without extra package installs beyond the standard Python setup.

## Project layout

```text
Chess/
├── README.md
├── requirements.txt
├── .gitignore
├── __main__.py
├── chess_app/
│   ├── __init__.py
│   ├── __main__.py
│   ├── ai.py
│   ├── app.py
│   ├── config.py
│   └── game_state.py
├── chess.pyz
└── .git/
```

## Notes

- API keys are stored in your home directory in a small config file, not inside the app bundle.
- The AI providers are optional and will prompt you if the SDK is missing.
- The zipapp is meant to be easy to share, but the AI providers still depend on the machine running the app having their packages installed.
