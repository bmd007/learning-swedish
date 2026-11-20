"""Turn the Rivstart B1/B2 Ordlista PDF into JSON: [{chapter, page, sv, forms, en}].

Usage: python3 -I tools/parse_ordlista.py <ordlista.pdf> <out.json>
Needs poppler's pdftohtml. Swedish is set in a 14 pt font, English in 13 pt, "sidan N" in 17 pt, "KAPITEL N" in 27 pt.
Output stays private (materials/ordlista/), the word list is © Natur & Kultur.
"""
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET


def chunks(pdf):
    xml = subprocess.run(["pdftohtml", "-xml", "-i", "-q", "-stdout", pdf], capture_output=True, text=True).stdout
    root = ET.fromstring(xml)
    sizes = {f.get("id"): int(f.get("size")) for f in root.iter("fontspec")}
    for page in root.iter("page"):
        mid = int(page.get("width")) / 2
        cols = [[], []]
        for t in page.iter("text"):
            text = "".join(t.itertext())
            if not text.strip():
                continue
            left, top = int(t.get("left")), int(t.get("top"))
            cols[left >= mid].append((top, left, sizes[t.get("font")], text))
        for col in cols:
            yield from sorted(col)


def parse(pdf):
    words, chapter, page, cur = [], 0, None, None
    for top, left, size, text in chunks(pdf):
        text = text.replace("­", "")
        if size >= 20:
            m = re.match(r"\s*KAPITEL (\d+)", text)
            if m:
                chapter, page, cur = int(m.group(1)), None, None
            continue
        if size == 17:
            m = re.match(r"\s*sidan (\d+)", text)
            if m:
                page, cur = int(m.group(1)), None
            continue
        if not chapter:
            continue
        if size == 14:
            if cur and not cur["en"]:
                cur["sv"] += text
            else:
                cur = {"chapter": chapter, "page": page, "sv": text, "en": ""}
                words.append(cur)
        elif size == 13 and cur:
            cur["en"] += text
    out = []
    for w in words:
        sv = re.sub(r"\s+", " ", w["sv"]).strip()
        m = re.match(r"(.*?)\s*\(([^)]*)\)\s*$", sv)
        out.append({"chapter": w["chapter"], "page": w["page"],
                    "sv": m.group(1) if m else sv, "forms": m.group(2) if m else "",
                    "en": re.sub(r"\s+", " ", w["en"]).strip()})
    return out


if __name__ == "__main__":
    words = parse(sys.argv[1])
    json.dump(words, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
    per = {}
    for w in words:
        per[w["chapter"]] = per.get(w["chapter"], 0) + 1
    print(len(words), "words", per)
