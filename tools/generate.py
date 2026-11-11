"""Generate a lesson or test with a local Ollama model.

  python3 tools/generate.py "s-passiv i presens" [--mode practice|exam] [--model gemma3:12b]

The model only writes content in small, schema-constrained steps (plan → items per section →
blind self-check). Code does ids, tags, shuffling, word tiles, the cover image, validation and audio.
"""
import argparse
import html
import http.client
import json
import os
import random
import re
import subprocess
import sys
import time
import unicodedata
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import validate  # noqa: E402

OLLAMA = os.environ.get("OLLAMA_URL", "http://localhost:11434")
MODEL = os.environ.get("OLLAMA_MODEL", "gemma3:12b")

TAGS = ["ordföljd.inversion", "ordföljd.bisats", "ordföljd.fråga", "verb.preteritum", "verb.supinum",
        "verb.presens", "verb.passiv", "verb.reflexiv", "verb.partikel", "verb.modal", "verb.futurum",
        "substantiv.plural", "substantiv.bestämd", "substantiv.en-ett", "adjektiv.ett-ord", "adjektiv.plural",
        "adjektiv.bestämd", "adjektiv.komparation", "adjektiv.adverb", "preposition", "preposition.tid",
        "preposition.plats", "pronomen.sin", "pronomen.objekt", "bisats.om-att", "konjunktion",
        "ord.synonym", "ord.kollokation", "ord.förväxling", "ord.tema"]
KINDS = ["gap", "mcq", "order", "reading", "listening"]

LEARNER = """Eleven: vuxen, modersmål persiska, flytande engelska. Nivå: på väg mot B1 (Swedex A2B1, SFI D).
Gillar mönster och sammanhang, inte rabblande. Vardagliga teman: arbete, boende, vård, skola, fritid, samhälle."""

RULES = """Regler:
- Skriv naturlig, korrekt svenska på B1-nivå: korta meningar, vanliga ord.
- Varje uppgift har EN tydligt rätt lösning. Kontrollera facit noga.
- Engelska fält (titleEn, qEn, introEn, instructionsEn) är korta översättningar/ledtrådar.
- Ingen persiska text utom i regelrutan (frivilligt, högst en kort mening)."""


def ask(messages, schema, temperature=0.5, log=print):
    body = {"model": MODEL, "messages": messages, "format": schema, "stream": False, "think": False,
            "options": {"temperature": temperature, "num_ctx": 8192}}
    req = urllib.request.Request(f"{OLLAMA}/api/chat", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                return json.loads(json.load(r)["message"]["content"])
        except (json.JSONDecodeError, KeyError) as e:
            log(f"  ogiltigt svar från modellen, försöker igen ({e})")
        except (OSError, http.client.HTTPException) as e:
            log(f"  ingen kontakt med Ollama, försöker igen om 10 s ({e})")
            time.sleep(10)
    raise RuntimeError("modellen gav inget giltigt JSON-svar")


def S(props, required=None, **extra):
    return {"type": "object", "properties": props, "required": required or list(props), **extra}


STR = {"type": "string"}


def arr(item, lo, hi):
    return {"type": "array", "items": item, "minItems": lo, "maxItems": hi}


def weak_tags():
    f = ROOT / "progress/tag-stats.md"
    if not f.exists():
        return ""
    rows = re.findall(r"^\| `([^`]+)` \| (\d+)/(\d+) \| (\d+)%", f.read_text(), re.M)
    weak = [t for t, w, n, p in rows if int(p) >= 50][:6]
    return "Elevens svaga områden just nu: " + ", ".join(weak) if weak else ""


def reference_lines():
    ex = ROOT / "materials/nok/exercises"
    for i in range(1, 11):
        f = ex / f"Kapitel_{i}.md"
        if f.exists():
            for line in f.read_text(encoding="utf-8").splitlines():
                if not line.startswith(("#", "<")) and 15 < len(line) < 160:
                    yield line.strip()
    for f in sorted((ROOT / "lessons").glob("*.json")):
        lesson = json.loads(f.read_text(encoding="utf-8"))
        if lesson.get("generated"):
            continue
        for sec in lesson.get("sections", []):
            for part in sec.get("parts") or [sec]:
                for it in part.get("items", []):
                    if it.get("type") == "gap" and it.get("answers"):
                        yield it["q"].replace("___", f"[{it['answers'][0]}]")


def references(topic, keywords=()):
    words = {w for w in re.findall(r"\w+", (topic + " " + " ".join(keywords)).lower()) if len(w) > 1}
    scored = []
    for line in reference_lines():
        score = len(words & set(re.findall(r"\w+", line.lower())))
        if score >= 2:
            scored.append((score, line))
    scored.sort(key=lambda x: -x[0])
    picked = list(dict.fromkeys(l for _, l in scored))[:14]
    return ("Korrekta exempel från läroboken (rätt svar inom [ ]). Följ samma språkbruk:\n" + "\n".join(f"- {l}" for l in picked)) if picked else ""


def review(sentences, focus, log, details=False):
    if not sentences:
        return []
    schema = S({"verdicts": arr(S({"n": {"type": "integer"}, "problem": STR, "correct": {"type": "boolean"}}),
                                len(sentences), len(sentences))})
    msg = (f"Du är en noggrann svensk språkgranskare med svenska som modersmål. Granska varje mening. "
           f"Är den grammatiskt korrekt OCH något en svensk faktiskt skulle säga? Underkänn om ordval, tempus, "
           f"preposition eller fras låter onaturlig eller ovanlig. Var extra noga med: {focus}. "
           f"Skriv först problem (eller \"inget\"), sedan correct=true/false.\n\n"
           + "\n".join(f"{i}. {t}" for i, t in enumerate(sentences)))
    res = ask([{"role": "user", "content": msg}], schema, temperature=0, log=log)
    verdicts = sorted(res["verdicts"], key=lambda v: v["n"])[:len(sentences)]
    if details:
        return [(v.get("correct", False), v.get("problem", "")) for v in verdicts]
    return [v.get("correct", False) for v in verdicts]


SENT = re.compile(r"[^.!?\n]+[.!?]")


def fix_text(text, focus, log):
    for attempt in range(2):
        sents = [x.strip() for x in SENT.findall(text) if len(x.split()) > 2]
        res = review(sents, focus, log, details=True)
        bad = [(t, why) for t, (ok, why) in zip(sents, res) if not ok]
        if not bad:
            return text
        log(f"  texten har {len(bad)} fel, rättar …")
        schema = S({"fixed": arr(STR, len(bad), len(bad))})
        msg = ("Skriv om varje mening så att den blir korrekt, idiomatisk svenska. Behåll innehållet och alla fakta. "
               "Svara ENDAST med den rättade meningen, inga kommentarer eller parenteser, i samma ordning.\n\n"
               + "\n".join(f"{i}. {t}  (problem: {why})" for i, (t, why) in enumerate(bad)))
        fixed = ask([{"role": "user", "content": msg}], schema, temperature=0.2, log=log)["fixed"]
        for (t, _), f in zip(bad, fixed):
            f = f.strip()
            if "(" in f and "(" not in t or len(f) > 1.5 * len(t) + 10:
                continue
            text = text.replace(t, f)
    sents = [x.strip() for x in SENT.findall(text) if len(x.split()) > 2]
    return text if all(review(sents, focus, log)) else None


EXAMPLE = re.compile(r"[A-ZÅÄÖ][^.!?\n|:]{6,}[.!?]")


def checked_rule(ctx, p, refs, log):
    md = p["rule_md"]
    for attempt in range(3):
        sents = [re.sub(r"[*_`]", "", m) for m in EXAMPLE.findall(md)]
        verdicts = review(sents, p["title"], log)
        bad = [t for t, ok in zip(sents, verdicts) if not ok]
        if not bad:
            return md
        log(f"  regelrutan har {len(bad)} felaktiga exempel, skriver om …")
        if attempt == 2:
            break
        schema = S({"rule_md": STR})
        msg = (f"{ctx}\n{refs}\n\nSkriv om regelrutan (markdown, liten tabell + 2–3 exempel, enkel svenska, en engelsk rad) för: {p['title']}. Alla exempel ska visa exakt ämnet.\n"
               f"Dessa meningar var FEL och får inte förekomma: " + " | ".join(bad))
        md = ask([{"role": "user", "content": msg}], schema, temperature=0.3, log=log)["rule_md"]
    keep = [l for l in md.splitlines() if not any(b[:25] in re.sub(r"[*_`]", "", l) for b in bad)]
    return "\n".join(keep)


def context(topic, mode):
    kind = "en lektion (övning med förklaring och direkt feedback)" if mode == "practice" else "ett kort test (utan förklaringar före uppgifterna)"
    return f"""Du är en erfaren lärare i svenska som andraspråk. Du gör {kind}, ca 12 minuter.
{LEARNER}
{RULES}
Ämne från eleven: "{topic}"
Håll dig till ämnet. Ett ämne per lektion."""


def plan(topic, mode, refs, log):
    schema = S({
        "title": STR, "titleEn": STR, "intro": STR, "introEn": STR,
        "rule_md": STR, "keywords": arr(STR, 3, 6),
        "sections": arr(S({"kind": {"type": "string", "enum": KINDS}, "title": STR, "titleEn": STR,
                           "instructions": STR, "instructionsEn": STR, "focus": STR,
                           "tag": {"type": "string", "enum": TAGS}}), 2, 4)})
    msg = context(topic, mode) + "\n" + refs + """

Steg 1: planera. Ge:
- title/titleEn: kort titel.
- intro/introEn: 1–2 meningar om vad eleven tränar.
- rule_md: regeln/mönstret i markdown (gärna en liten tabell + 2–3 exempel, enkel svenska, en engelsk rad). Alla exempel ska visa exakt ämnet, inget annat. Om ämnet är ett tema (t.ex. ett jobb) – de viktigaste orden och fraserna.
- keywords: 3–6 nyckelord.
- sections: 2–4 delar. kind = gap (luckmeningar), mcq (flerval), order (ordföljd), reading (kort text + Ja/Nej), listening (dialog + frågor). Välj det som passar ämnet; minst en del med text eller dialog om ämnet är ett tema. focus = exakt vad delen tränar. tag = närmaste etikett."""
    log("Planerar lektionen …")
    return ask([{"role": "user", "content": msg}], schema, log=log)


def section_items(ctx, p, sec, refs, log, dialogue=None):
    k = sec["kind"]
    head = f"""{ctx}
Lektionens titel: {p['title']}
Regel/ord: {p['rule_md'][:800]}
Del: {sec['title']} – fokus: {sec['focus']}
{refs}
Delen ska fungera för sig själv. Hänvisa inte till andra delar, texter eller dialoger{" – utom dialogen nedan, och då bara till det som faktiskt sägs i den" if dialogue else ""}.
{("Dialog i lektionen:" + chr(10) + dialogue) if dialogue else ""}
"""
    if k == "gap":
        schema = S({"items": arr(S({"q": STR, "qEn": STR, "base": STR, "answer": STR,
                                    "also_ok": arr(STR, 0, 3), "explain": STR}), 5, 6)})
        task = 'Skriv 5–6 luckmeningar. q har exakt EN lucka skriven "___". base = ordet i grundform (visas som ledtråd, får inte vara samma som svaret om det inte går). answer = rätt ord i luckan. also_ok = andra helt korrekta svar (ofta tom). explain = kort förklaring.'
    elif k == "mcq":
        schema = S({"items": arr(S({"q": STR, "qEn": STR, "options": arr(STR, 4, 4), "correct": STR,
                                    "explain": STR}), 4, 5)})
        task = "Skriv 4–5 flervalsfrågor med 4 alternativ. correct = exakt texten för det rätta alternativet. Fel alternativ ska vara rimliga (samma typ och ungefär samma längd som det rätta) men tydligt fel. Inga skämtalternativ."
    elif k == "order":
        schema = S({"items": arr(S({"sentence": STR, "qEn": STR, "explain": STR}), 3, 4)})
        task = "Skriv 3–4 meningar (5–9 ord) för en ordföljdsövning. Eleven får orden blandade. Bara en naturlig ordföljd ska vara rimlig (undvik meningar som kan börja med olika satsdelar). qEn = engelsk översättning."
    elif k == "reading":
        schema = S({"passageTitle": STR, "passage": STR,
                    "items": arr(S({"statement": STR, "is_true": {"type": "boolean"}, "explain": STR}), 5, 6)})
        task = "Skriv en kort text (120–180 ord) om ämnet, t.ex. annons, mejl, meddelande eller faktatext. Skriv sedan 5–6 påståenden; is_true = stämmer påståendet enligt texten? Blanda sanna och falska. Svaret ska stå klart i texten."
    else:
        schema = S({"woman": STR, "man": STR, "script": arr(S({"speaker": STR, "text": STR}), 8, 12),
                    "items": arr(S({"q": STR, "options": arr(STR, 4, 4), "correct": STR, "explain": STR}), 3, 4)})
        task = "Skriv en naturlig vardagsdialog (8–12 repliker) mellan en kvinna och en man. woman/man = deras förnamn; speaker = ett av de två namnen. Skriv tal som det låter (siffror och tider med ord). Skriv sedan 3–4 flervalsfrågor om detaljer i dialogen; correct = exakt texten för rätt alternativ."
    log(f"Skriver del: {sec['title']} ({k}) …")
    data = ask([{"role": "user", "content": head + "\n" + task}], schema, log=log)
    if k == "gap":
        for it in data["items"]:
            q = re.sub(r"_{2,}", "___", it["q"])
            if it.get("base"):
                q = re.sub(r"\s*\(\s*" + re.escape(it["base"]) + r"\s*\)", "", q)
            it["q"] = q.strip()
    return data


def norm(s):
    return re.sub(r"[^\wåäöéü ]", "", (s or "").lower()).strip()


def self_check(sec, data, log):
    k = sec["kind"]
    if k == "order":
        return data
    if k == "gap":
        qs = [f"{i}. {it['q']} ({it['base']})" for i, it in enumerate(data["items"])]
        task = "Fyll i luckan ___ i varje mening med rätt form av ordet inom parentes. Svara bara med ordet/orden som ska stå i luckan."
    elif k == "reading":
        qs = [f"{i}. {it['statement']}" for i, it in enumerate(data["items"])]
        task = (f"Läs texten. För varje påstående: citera först den mening i texten som avgör saken (quote), "
                f"svara sedan ja (stämmer), nej (stämmer inte) eller framgår_inte (texten säger inget säkert).\n\nText:\n{data['passage']}")
    else:
        qs = [f"{i}. {it['q']}\n   " + " | ".join(it["options"]) for i, it in enumerate(data["items"])]
        task = "Välj rätt alternativ för varje fråga. Svara med exakt texten för alternativet."
        if k == "listening":
            task += "\n\nDialog:\n" + "\n".join(f"{l['speaker']}: {l['text']}" for l in data["script"])
    if k == "reading":
        item = S({"n": {"type": "integer"}, "quote": STR, "answer": {"type": "string", "enum": ["ja", "nej", "framgår_inte"]}})
    else:
        item = S({"n": {"type": "integer"}, "answer": STR})
    schema = S({"answers": arr(item, len(qs), len(qs))})
    res = ask([{"role": "user", "content": f"{task}\n\n" + "\n".join(qs)}], schema, temperature=0, log=log)
    got = {a["n"]: a["answer"] for a in res["answers"]}
    keep = []
    for i, it in enumerate(data["items"]):
        a = got.get(i)
        if k == "gap":
            ok = norm(a) in {norm(x) for x in [it["answer"], *it.get("also_ok", [])]}
        elif k == "reading":
            ok = a == ("ja" if it["is_true"] else "nej")
        else:
            ok = norm(a) == norm(it["correct"]) and sum(norm(o) == norm(it["correct"]) for o in it["options"]) == 1
        if ok:
            keep.append(it)
        else:
            log(f"  tar bort osäker uppgift: {(it.get('q') or it.get('statement'))[:60]}")
    data["items"] = keep
    return data


def review_section(sec, data, log):
    k = sec["kind"]
    checks = []
    for i, it in enumerate(data["items"]):
        if k == "gap":
            checks.append((i, True, it["q"].replace("___", it["answer"], 1)))
            for alt in it.get("also_ok", []):
                checks.append((("alt", i, alt), True, it["q"].replace("___", alt, 1)))
        elif k == "order":
            checks.append((i, True, it["sentence"]))
        elif k == "mcq" and "__" in it["q"]:
            for o in it["options"]:
                checks.append((i, norm(o) == norm(it["correct"]), re.sub(r"_{2,}", o, it["q"], count=1)))
    if k == "reading":
        log(f"Granskar texten: {sec['title']} …")
        data["passage"] = fix_text(data["passage"], sec["focus"], log)
        if data["passage"] is None:
            data["items"] = []
        return data
    if k == "listening":
        log(f"Granskar dialogen: {sec['title']} …")
        texts = [l["text"] for l in data["script"]]
        verdicts = review(texts, sec["focus"], log, details=True)
        for line, (ok, why) in zip(data["script"], verdicts):
            if not ok:
                line["text"] = fix_text(line["text"], sec["focus"], log) or line["text"]
        return data
    if not checks:
        return data
    log(f"Granskar språket: {sec['title']} …")
    verdicts = review([c[2] for c in checks], sec["focus"], log)
    bad = {i for (i, should, _), ok in zip(checks, verdicts) if ok != should and not isinstance(i, tuple)}
    for (i, should, _), ok in zip(checks, verdicts):
        if isinstance(i, tuple) and not ok:
            _, j, alt = i
            data["items"][j]["also_ok"] = [a for a in data["items"][j].get("also_ok", []) if a != alt]
    for i in sorted(bad):
        it = data["items"][i]
        log(f"  tar bort: {(it.get('q') or it.get('sentence'))[:60]}")
    data["items"] = [it for i, it in enumerate(data["items"]) if i not in bad]
    return data


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:40] or "lektion"


def next_id(title):
    nums = [int(m.group(1)) for f in (ROOT / "lessons").glob("*.json") if (m := re.match(r"(\d{3})-", f.name))]
    return f"{max(nums, default=0) + 1:03d}-gen-{slug(title)}"


def cover_svg(title, keywords):
    words, lines, cur = title.split(), [], ""
    for w in words:
        if len(cur) + len(w) > 26 and cur:
            lines.append(cur); cur = w
        else:
            cur = f"{cur} {w}".strip()
    lines.append(cur)
    t = "".join(f'<text x="320" y="{70 + i * 40}" text-anchor="middle" font-size="32" font-weight="700" fill="#1a365d">{html.escape(l)}</text>' for i, l in enumerate(lines[:3]))
    colors = ["#bee3f8", "#c6f6d5", "#fefcbf", "#fed7d7", "#e9d8fd", "#feebc8"]
    chips, x, y = [], 40, 70 + len(lines[:3]) * 40 + 30
    for i, k in enumerate(keywords[:6]):
        w = 22 + len(k) * 11
        if x + w > 600:
            x, y = 40, y + 52
        chips.append(f'<rect x="{x}" y="{y}" width="{w}" height="38" rx="19" fill="{colors[i % 6]}"/>'
                     f'<text x="{x + w / 2}" y="{y + 25}" text-anchor="middle" font-size="18" fill="#222">{html.escape(k)}</text>')
        x += w + 12
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 300" font-family="system-ui, sans-serif">'
            f'<rect width="640" height="300" fill="#fff"/><rect x="0" y="0" width="640" height="8" fill="#2b6cb0"/>{t}{"".join(chips)}</svg>')


def build(topic, mode, p, sections, lesson_id):
    rnd = random.Random(lesson_id)
    out_sections, n = [], 0

    def nid():
        nonlocal n
        n += 1
        return f"q{n}"

    def mcq(it, tag):
        opts = it["options"][:]
        rnd.shuffle(opts)
        idx = next(i for i, o in enumerate(opts) if norm(o) == norm(it["correct"]))
        return {"id": nid(), "type": "mcq", "tags": [tag], "q": it["q"], **({"qEn": it["qEn"]} if it.get("qEn") else {}),
                "options": opts, "answer": idx, "explain": it.get("explain", "")}

    seen = set()
    for si, (sec, data) in enumerate(sections):
        tag, k = sec["tag"], sec["kind"]
        fresh = []
        for it in data["items"]:
            key = norm(it.get("q") or it.get("sentence") or it.get("statement"))
            if key not in seen:
                seen.add(key)
                fresh.append(it)
        data["items"] = fresh
        items = []
        if si == 0 and mode == "practice":
            items.append({"id": "i1", "type": "info", "image": {"src": "cover.svg", "alt": p["title"]}, "md": p["rule_md"]})
        base = {"id": f"s{si + 1}", "title": f"Del {si + 1}: {sec['title']}", "titleEn": sec["titleEn"],
                "instructions": sec["instructions"], "instructionsEn": sec["instructionsEn"]}
        if si == 0 and mode != "practice":
            base["parts"] = [{"image": {"src": "cover.svg", "alt": p["title"]}, "items": []}]
        for it in data["items"]:
            if k == "gap":
                q = re.sub(r"_{2,}", "___", it["q"])
                if q.count("___") != 1:
                    continue
                g = {"id": nid(), "type": "gap", "tags": [tag], "q": q, "answers": list(dict.fromkeys([it["answer"], *it.get("also_ok", [])])),
                     "explain": it.get("explain", "")}
                if it.get("base") and norm(it["base"]) != norm(it["answer"]):
                    g["base"] = it["base"]
                if it.get("qEn"):
                    g["qEn"] = it["qEn"]
                items.append(g)
            elif k == "mcq" or k == "listening":
                items.append(mcq(it, tag if k == "mcq" else "hör.detalj"))
            elif k == "order":
                sent = it["sentence"].strip()
                words = re.sub(r"[.,!?;:]", "", sent).split()
                shuffled = words[:]
                while len(words) > 1 and shuffled == words:
                    rnd.shuffle(shuffled)
                items.append({"id": nid(), "type": "order", "tags": [tag], "q": it.get("qEn", ""), "words": shuffled,
                              "answers": [sent.rstrip(".!?")], "explain": it.get("explain", "")})
            elif k == "reading":
                items.append({"id": nid(), "type": "mcq", "tags": ["läs.janej"], "q": it["statement"], "options": ["Ja", "Nej"],
                              "answer": 0 if it["is_true"] else 1, "explain": it.get("explain", "")})
        if k == "reading":
            part = {"passageTitle": data["passageTitle"], "passage": re.sub(r"[*_`#]", "", data["passage"]), "items": items}
            base["parts"] = base.get("parts", []) + [part] if "parts" in base else [part]
        elif k == "listening":
            speakers = {data["woman"]: "f", data["man"]: "m"}
            script = [l for l in data["script"] if l["speaker"] in speakers]
            base["parts"] = base.get("parts", []) + [{"audio": {"id": f"a{si + 1}", "title": sec["title"], "maxPlays": 2,
                                                               "speakers": speakers, "script": script}, "items": items}]
        elif "parts" in base:
            base["parts"][0]["items"] = items
        else:
            base["items"] = items
        if [i for i in items if i["type"] != "info"]:
            out_sections.append(base)
    return {"id": lesson_id, "title": p["title"], "titleEn": p["titleEn"], "mode": mode, "minutes": 12,
            "intro": p["intro"], "introEn": p["introEn"],
            "generated": {"model": MODEL, "topic": topic, "reviewed": False},
            "sections": out_sections}


def generate(topic, mode="practice", log=print):
    ctx = context(topic, mode)
    refs = references(topic)
    if refs:
        log("Hittade exempel i läroboken.")
    p = plan(topic, mode, refs, log)
    refs = references(topic, p["keywords"]) or refs
    log("Granskar regelrutan …")
    p["rule_md"] = checked_rule(ctx, p, refs, log)
    sections, dialogue = [], None
    for sec in p["sections"]:
        data = section_items(ctx, p, sec, refs, log, dialogue if sec["kind"] == "mcq" else None)
        if sec["kind"] == "listening":
            dialogue = "\n".join(f"{l['speaker']}: {l['text']}" for l in data["script"])
        data = review_section(sec, data, log)
        log(f"Kontrollerar facit: {sec['title']} …")
        data = self_check(sec, data, log)
        if len(data["items"]) >= 2:
            sections.append((sec, data))
        else:
            log(f"  hoppar över delen (för få säkra uppgifter)")
    if not sections:
        raise RuntimeError("inga säkra uppgifter – prova att beskriva ämnet tydligare")
    md_lines = [l for l in p["rule_md"].splitlines() if l.strip() and not re.fullmatch(r"[|\s:-]+", l)]
    if len(md_lines) < 4:
        examples = [it["q"].replace("___", f"**{it['answer']}**", 1) for sec, d in sections if sec["kind"] == "gap" for it in d["items"]]
        examples += [it["sentence"] for sec, d in sections if sec["kind"] == "order" for it in d["items"]]
        p["rule_md"] = f"**{p['title']}**\n\n{p['intro']}\n\n**Exempel:**\n" + "\n".join(f"- {e}" for e in examples[:5])
        log("  regelrutan byggdes av granskade exempel")
    lesson_id = next_id(p["title"])
    lesson = build(topic, mode, p, sections, lesson_id)
    img = ROOT / "images" / lesson_id
    img.mkdir(parents=True, exist_ok=True)
    (img / "cover.svg").write_text(cover_svg(p["title"], p["keywords"]), encoding="utf-8")
    path = ROOT / "lessons" / f"{lesson_id}.json"
    path.write_text(json.dumps(lesson, ensure_ascii=False, indent=2), encoding="utf-8")
    errors = validate.check(path)
    if errors:
        path.unlink()
        raise RuntimeError("validering misslyckades: " + "; ".join(errors))
    if any("audio" in pt for s in lesson["sections"] for pt in s.get("parts", [])):
        log("Skapar ljud …")
        py = ROOT / ".venv/bin/python"
        subprocess.run([str(py if py.exists() else sys.executable), str(ROOT / "tools/build_audio.py"), str(path)],
                       capture_output=True, timeout=300)
    log(f"Klar: {lesson_id}")
    return lesson_id


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("topic")
    ap.add_argument("--mode", default="practice", choices=["practice", "exam"])
    ap.add_argument("--model")
    a = ap.parse_args()
    if a.model:
        MODEL = a.model
    print(generate(a.topic, a.mode))
