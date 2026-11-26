"""Generate single-language Lingogo Chinese index.html from lingogo/index.html."""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINGOGO_ROOT = ROOT.parent / "lingogo"
SRC_HTML = LINGOGO_ROOT / "index.html"
DST_HTML = ROOT / "index.html"
VERSION_JSON = ROOT / "version.json"
LANG_CODE = "zh"

def replace_exact(src, old, new, count=1, label=""):
    found = src.count(old)
    if found != count:
        raise ValueError(f"Expected {count} match(es) for {label or repr(old[:60])}, found {found}")
    return src.replace(old, new)

def replace_json_lang_only(src, const_name):
    m = re.search(rf"const {re.escape(const_name)} = (\{{.*?\}});", src)
    if not m:
        raise ValueError(f"Could not find const {const_name}")
    obj = json.loads(m.group(1))
    trimmed = json.dumps({LANG_CODE: obj[LANG_CODE]}, ensure_ascii=False, separators=(",", ":"))
    return src[:m.start()] + f"const {const_name} = {trimmed};" + src[m.end():]

def main():
    ver_data = json.loads(VERSION_JSON.read_text(encoding="utf-8"))
    build_id = ver_data["build"]
    html = SRC_HTML.read_text(encoding="utf-8")

    html = replace_exact(
        html,
        '<meta name="apple-mobile-web-app-title" content="Lingogo">\n<title>Lingogo</title>',
        '<meta name="apple-mobile-web-app-title" content="Lingogo Chinese">\n<title>Lingogo Chinese</title>',
        label="title tags",
    )
    html = replace_exact(
        html,
        '<script async src="English/data/ielts_30day_listening.js"></script>\n',
        "",
        label="ielts listening data script",
    )
    html = re.sub(r"const APP_BUILD_ID = '[^']+';", f"const APP_BUILD_ID = '{build_id}';", html, count=1)

    langs_old = (
        "const LANGS = {\n"
        "  en: { label: 'English', vi: 'Tiếng Anh', short: 'Anh', folder: 'English', tts: 'en-US', rec: 'en-US', lang: 'en', cjk: false },\n"
        "  zh: { label: '中文', vi: 'Tiếng Trung', short: 'Trung', folder: 'Chinese', tts: 'zh-CN', rec: 'zh-CN', lang: 'zh-Hans', cjk: true },\n"
        "  ja: { label: '日本語', vi: 'Tiếng Nhật', short: 'Nhật', folder: 'Japanese', tts: 'ja-JP', rec: 'ja-JP', lang: 'ja', cjk: true },\n"
        "};\n"
        "const langFolder = (code) => (LANGS[code] && LANGS[code].folder) || (code === 'en' ? 'English' : (code === 'zh' ? 'Chinese' : 'Japanese'));"
    )
    langs_new = (
        "const LANGS = {\n"
        "  zh: { label: '中文', vi: 'Tiếng Trung', short: 'Trung', folder: '', tts: 'zh-CN', rec: 'zh-CN', lang: 'zh-Hans', cjk: true },\n"
        "};\n"
        "const langFolder = (code) => (LANGS[code] && LANGS[code].folder) || '';\n"
        "const langPath = (code, rel) => { const f = langFolder(code); return f ? f + '/' + rel : rel; };"
    )
    html = replace_exact(html, langs_old, langs_new, label="LANGS")

    cats_start = html.index("const CATEGORIES = {")
    cats_end = html.index("\n// ===== DỮ LIỆU ĐỊNH DANH BÀI HỌC", cats_start)
    cats_block = html[cats_start:cats_end]
    m_cat = re.search(rf"  {LANG_CODE}: \[(.*?)\n  \]", cats_block, flags=re.S)
    if not m_cat:
        raise ValueError("Could not extract CATEGORIES for " + LANG_CODE)
    single_cats = "const CATEGORIES = {\n  " + LANG_CODE + ": [" + m_cat.group(1) + "\n  ]\n};\n"
    html = html[:cats_start] + single_cats + html[cats_end:]

    for const_name in ("TOPIC_META", "CAT_TOTAL_TOPICS", "CAT_TOTAL_LESSONS", "LANG_TOTAL_TOPICS", "LANG_TOTAL_LESSONS"):
        html = replace_json_lang_only(html, const_name)

    html = replace_exact(html, "    const fld = langFolder(code);\n    const d = await getJSON(fld + '/data/' + code + '.json');",
                         "    const d = await getJSON(langPath(code, 'data/' + code + '.json'));", label="loadLang")
    html = replace_exact(html, "    const fld = langFolder(code);\n    try { STROKES[code] = await getJSON(fld + '/data/strokes-' + code + '.json'); } catch (e) { STROKES[code] = {}; }",
                         "    try { STROKES[code] = await getJSON(langPath(code, 'data/strokes-' + code + '.json')); } catch (e) { STROKES[code] = {}; }", label="loadStrokes")
    html = replace_exact(html,
        "  const fld = langFolder(code);\n  return code === 'en' ? { file: fld + '/audio/w' + a[0] + '.json', key: a[1] } : { file: fld + '/audio/' + code + '-' + a + '.json', key: text };",
        "  return code === 'en' ? { file: langPath(code, 'audio/w' + a[0] + '.json'), key: a[1] } : { file: langPath(code, 'audio/' + code + '-' + a + '.json'), key: text };",
        label="bundleOf")
    html = replace_exact(html, "  if (track.audio.startsWith('audio/')) return langFolder(code) + '/' + track.audio;",
                         "  if (track.audio.startsWith('audio/')) return langPath(code, track.audio);", label="resolveTrackAudioSrc")

    html = replace_exact(html,
        "try { const raw = localStorage.getItem(KEY); if (raw) S = Object.assign(fresh(), JSON.parse(raw)); } catch (e) { /* bị chặn lưu trữ */ }",
        "try { const raw = localStorage.getItem(KEY); if (raw) S = Object.assign(fresh(), JSON.parse(raw)); } catch (e) { /* bị chặn lưu trữ */ }\nS.lang = 'zh';",
        label="force S.lang on boot")
    html = replace_exact(html, "S = mergeState(S, remote);", "S = mergeState(S, remote); S.lang = 'zh';", count=2, label="sync normalize lang")
    html = replace_exact(html, "  if (!S.name) return welcomeView();", "  if (!LANGS[S.lang]) S.lang = 'zh';\n  if (!S.name) return welcomeView();", label="route guard S.lang")

    DST_HTML.write_text(html, encoding="utf-8")
    print(f"Generated {DST_HTML} ({len(html.encode('utf-8')):,} bytes, build {build_id})")

if __name__ == "__main__":
    main()
