import random
import re


def _call_openai(prompt, api_key, model):
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model or "gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


def _call_gemini(prompt, api_key, model):
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    gmodel = genai.GenerativeModel(model or "gemini-1.5-pro")
    return gmodel.generate_content(prompt).text.strip()


def call_llm(provider, prompt, cfg):
    if provider == "gemini":
        return _call_gemini(prompt, cfg.get("gemini_key", ""), cfg.get("gemini_model", ""))
    return _call_openai(prompt, cfg.get("openai_key", ""), cfg.get("openai_model", ""))


def build_move_prompt(fen, legal_moves, color):
    return (
        f"You are a strong chess player playing as {color}.\n"
        f"Current position (FEN): {fen}\n"
        f"Legal moves (UCI format): {', '.join(legal_moves)}\n\n"
        "Choose the strongest move. Respond in EXACTLY this format, nothing else:\n"
        "MOVE: <uci move from the list above>\n"
        "REASON: <one short sentence on why>"
    )


def get_ai_move(fen, legal_moves, color, provider, cfg):
    for _ in range(3):
        try:
            raw = call_llm(provider, build_move_prompt(fen, legal_moves, color), cfg)
        except Exception as exc:
            return random.choice(legal_moves), f"(AI error, played randomly: {exc})"

        move_match = re.search(r"MOVE:\s*([a-h][1-8][a-h][1-8][qrbn]?)", raw, re.IGNORECASE)
        reason_match = re.search(r"REASON:\s*(.+)", raw, re.IGNORECASE)
        move = move_match.group(1).lower() if move_match else ""
        reason = reason_match.group(1).strip() if reason_match else ""
        if move in legal_moves:
            return move, reason

    return random.choice(legal_moves), "(AI gave an invalid move a few times, played randomly)"


def get_commentary(fen_before, move_san, color, provider, cfg):
    prompt = (
        f"You are a friendly chess commentator watching a human play as {color}. "
        f"Before their move the position was (FEN): {fen_before}. They just played {move_san}. "
        "Give ONE short, encouraging sentence of commentary. No preamble."
    )
    try:
        return call_llm(provider, prompt, cfg)
    except Exception as exc:
        return f"(commentator unavailable: {exc})"


def get_hint(fen, legal_moves, color, provider, cfg):
    prompt = (
        f"You are a friendly chess coach helping a human playing as {color}. "
        f"Position (FEN): {fen}\nLegal moves (UCI): {', '.join(legal_moves)}\n\n"
        "Give a short 1-2 sentence hint about a good plan or move, WITHOUT stating "
        "the exact move in UCI notation."
    )
    try:
        return call_llm(provider, prompt, cfg)
    except Exception as exc:
        return f"(hint unavailable: {exc})"


def get_draw_decision(fen, color, provider, cfg):
    prompt = (
        f"You are a chess engine playing as {color} in this position (FEN): {fen}\n"
        "Your opponent has offered a draw. Consider the position objectively. "
        "Respond with EXACTLY one word: YES if you accept the draw, or NO if you decline."
    )
    try:
        raw = call_llm(provider, prompt, cfg).strip().upper()
        return raw.startswith("Y")
    except Exception:
        return False
