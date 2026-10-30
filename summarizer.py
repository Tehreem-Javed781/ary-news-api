"""Simple extractive summarizer (word-frequency based, no external downloads)."""
import re
from collections import Counter

STOPWORDS = set("""
a about above after again against all am an and any are as at be because been before being below
between both but by can could did do does doing down during each few for from further had has have
having he her here hers herself him himself his how i if in into is it its itself just me more most
my myself no nor not now of off on once only or other our ours ourselves out over own same she should
so some such than that the their theirs them themselves then there these they this those through to
too under until up very was we were what when where which while who whom why will with would you your
yours yourself yourselves also said says say according one two new mr ms
""".split())


def split_sentences(text):
    text = re.sub(r"\s+", " ", text).strip()
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'])", text)
    return [p.strip() for p in parts if len(p.split()) >= 5]


def summarize(text, max_sentences=3):
    sentences = split_sentences(text)
    if not sentences:
        return text[:500].strip()
    if len(sentences) <= max_sentences:
        return " ".join(sentences)

    words = [w for w in re.findall(r"[a-zA-Z']+", text.lower()) if w not in STOPWORDS and len(w) > 2]
    if not words:
        return " ".join(sentences[:max_sentences])
    freq = Counter(words)
    top = max(freq.values())

    scores = {}
    for i, s in enumerate(sentences):
        tokens = [w for w in re.findall(r"[a-zA-Z']+", s.lower()) if w in freq]
        if not tokens:
            continue
        score = sum(freq[w] / top for w in tokens) / len(tokens) ** 0.5
        if i == 0:
            score *= 1.2  # news articles front-load key facts
        scores[i] = score

    best = sorted(scores, key=scores.get, reverse=True)[:max_sentences]
    return " ".join(sentences[i] for i in sorted(best))
