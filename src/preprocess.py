import re


def prepare_text(text: str) -> str:
    text = re.sub(r"<([^_>]+)_[^>]+>", r"\1", text)
    text = re.sub(r"[^\w\s]", " ", text)
    return text.lower()