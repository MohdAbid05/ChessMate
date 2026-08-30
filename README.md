# ChessMate

A small chess game built in Python with a Tkinter interface. It supports local multiplayer, optional AI play, save/load, move tracking, and a packaged zipapp version for easy sharing.

## What it includes

- Human vs Human
- Human vs AI
- AI vs AI demo mode
- Move history and captured-piece tracking
- Undo, draw, and resign actions
- Save and load game states
- Optional commentary and hints

## Requirements

- Python 3.11+
- Tkinter
- python-chess

Install the base package:

```bash
pip install -r requirements.txt
```

If you want the AI modes, install the provider SDKs you plan to use:

```bash
pip install openai google-generativeai
```

## Run it

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

## Project structure

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

- API keys are stored in your home folder in a small config file, not inside the app bundle.
- AI support is optional and will prompt you if the required SDK is missing.
- The zipapp is useful for quick sharing, but the AI features still need their provider packages installed on the machine running the app.

## Repo name

Use this repo name:

```text
chessmate
```

It is short, clean, and matches the app branding.
