"""Compare a TTS script line with a Whisper transcript: Swedish numbers spelled out, letters only.

Whisper writes "1947", "14.20", "070 432 965"; scripts spell them ("nittonhundrafyrtiosju"). Both sides are
turned into one string of letters, then compared with a character error rate (compound splits don't matter).
"""
import re

ONES = ["noll", "ett", "två", "tre", "fyra", "fem", "sex", "sju", "åtta", "nio", "tio", "elva", "tolv", "tretton",
        "fjorton", "femton", "sexton", "sjutton", "arton", "nitton"]
TENS = ["", "", "tjugo", "trettio", "fyrtio", "femtio", "sextio", "sjuttio", "åttio", "nittio"]


def spell(n, years=True):
    if n < 20:
        return ONES[n]
    if n < 100:
        return TENS[n // 10] + (ONES[n % 10] if n % 10 else "")
    if n < 1000:
        return ("ett" if n // 100 == 1 else ONES[n // 100]) + "hundra" + (spell(n % 100) if n % 100 else "")
    if years and 1100 <= n < 2000:
        return spell(n // 100) + "hundra" + (spell(n % 100) if n % 100 else "")
    if n < 1_000_000:
        return ("" if n // 1000 == 1 else spell(n // 1000)) + "tusen" + (spell(n % 1000) if n % 1000 else "")
    return spell(n // 1_000_000) + "miljoner" + (spell(n % 1_000_000) if n % 1_000_000 else "")


def numbers_to_words(text, years=True):
    text = re.sub(r"\b0\d+(?:[ -]\d+)+", lambda m: " ".join(ONES[int(c)] for c in m.group(0) if c.isdigit()), text)
    text = re.sub(r"(\d)[  ](\d{3})\b", r"\1\2", text)

    def word(m):
        s = m.group(0)
        if ":" in s or "." in s:
            a, b = re.split(r"[:.]", s, maxsplit=1)
            return f"{spell(int(a))} {spell(int(b)) if int(b) else ''}"
        if s.startswith("0") and len(s) > 1:
            return " ".join(ONES[int(c)] for c in s)
        return spell(int(s), years)

    return re.sub(r"\d+(?:[:.]\d{2})?", word, text)


def letters(text, years=True):
    text = numbers_to_words(text.lower(), years)
    text = re.sub(r"\boch\b", " ", text)
    return re.sub(r"[^a-zåäöé]", "", text)


def cer(ref, hyp):
    """1100–1999 can be a year (fjortonhundra…) or an amount (tusen fyrahundra…): keep the better reading."""
    return min(_cer(letters(ref, y), letters(hyp, y)) for y in (True, False))


def _cer(a, b):
    d = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        prev, d[0] = d[0], i
        for j, cb in enumerate(b, 1):
            prev, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, prev + (ca != cb))
    return d[-1] / max(len(a), 1)
