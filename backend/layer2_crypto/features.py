import numpy as np

def extract_features(prompt: str) -> np.ndarray:
    words = prompt.split()
    length = len(prompt)
    tokens = len(words)

    avg_word_len = sum(len(w) for w in words) / max(tokens, 1)

    punctuation = sum(1 for c in prompt if c in ".,!?;:")
    punctuation_ratio = punctuation / max(length, 1)

    uppercase_ratio = sum(1 for c in prompt if c.isupper()) / max(length, 1)

    special_chars = sum(1 for c in prompt if not c.isalnum())
    question_marks = prompt.count("?")

    numeric_ratio = sum(c.isdigit() for c in prompt) / max(length, 1)

    keyword_count = sum(1 for k in ["ignore", "bypass", "override"] if k in prompt.lower())

    # placeholders (can improve later)
    perplexity_score = 0.5
    semantic_similarity = 0.5

    ngrams = [
        prompt.lower().count("ignore previous"),
        prompt.lower().count("you are now"),
        prompt.lower().count("system override"),
        prompt.lower().count("act as"),
        prompt.lower().count("bypass rules"),
    ]

    return np.array([
        length,
        tokens,
        avg_word_len,
        punctuation_ratio,
        uppercase_ratio,
        special_chars,
        question_marks,
        numeric_ratio,
        keyword_count,
        perplexity_score,
        semantic_similarity,
        *ngrams
    ], dtype=np.float32)