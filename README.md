# AI Powered Chess Game

A lightweight chess app built with Python and Tkinter. It includes local two-player gameplay, AI-assisted modes, move tracking, save/load support, and a zipapp build for easy sharing.

## Features

- Human vs Human
- Human vs AI
- AI vs AI showcase mode
- Move history and captured-piece tracking
- Undo, resign, and draw controls
- JSON save/load support
- Optional commentary and hints

## Requirements

- Python 3.11+
- Tkinter
- python-chess

Install the base dependency:

```bash
pip install -r requirements.txt
```

If you want to use AI modes, install the providers you plan to use:

```bash
pip install openai google-generativeai
```

## Run locally

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

Then run:

```bash
python chess.pyz
```

This keeps the core game portable while leaving the AI providers as optional installs.

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

- API keys are stored in your home directory in a small config file instead of inside the app bundle.
- The AI providers are optional and will prompt you if the SDK is missing.
- The zipapp is designed for quick sharing, but AI features still depend on the provider packages being installed on the machine running the app.

## Recommended GitHub repo name

A cleaner GitHub slug is:

```text
ai-powered-chess-game
```

This is more polished than the underscore version and is easier to read in URLs.
