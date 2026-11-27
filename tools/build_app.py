"""Generate single-language Lingogo Chinese index.html from lingogo/index.html."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINGOGO_ROOT = ROOT.parent / "lingogo"
SRC_HTML = LINGOGO_ROOT / "index.html"
DST_HTML = ROOT / "index.html"
VERSION_JSON = ROOT / "version.json"
LANG_CODE = "zh"


def replace_exact(src: str, old: str, new: str, count: int = 1, label: str = "") -> str:
    found = src.count(old)
    if found != count:
        raise ValueError(f"Expected {count} match(es) for {label or repr(old[:60])}, found {found}")
    return src.replace(old, new)


def replace_json_lang_only(src: str, const_name: str) -> str:
    m = re.search(rf"const {re.escape(const_name)} = (\{{.*?\}});", src)
    if not m:
        raise ValueError(f"Could not find const {const_name}")
    obj = json.loads(m.group(1))
    trimmed = json.dumps({LANG_CODE: obj[LANG_CODE]}, ensure_ascii=False, separators=(",", ":"))
    return src[:m.start()] + f"const {const_name} = {trimmed};" + src[m.end():]


def main() -> None:
    ver_data = json.loads(VERSION_JSON.read_text(encoding="utf-8"))
    build_id = ver_data["build"]
    app_ver = ver_data["version"]
    html = SRC_HTML.read_text(encoding="utf-8")

    # 1. Head & branding
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

    # 2. Single-language LANGS & path helpers
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

    # 3. Trim CATEGORIES and JSON metadata constants to Chinese-only
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

    # 4. Path lookups from Chinese/<subpath> to root <subpath>
    html = replace_exact(
        html,
        "    const fld = langFolder(code);\n    const d = await getJSON(fld + '/data/' + code + '.json');",
        "    const d = await getJSON(langPath(code, 'data/' + code + '.json'));",
        label="loadLang",
    )
    html = replace_exact(
        html,
        "    const fld = langFolder(code);\n    try { STROKES[code] = await getJSON(fld + '/data/strokes-' + code + '.json'); } catch (e) { STROKES[code] = {}; }",
        "    try { STROKES[code] = await getJSON(langPath(code, 'data/strokes-' + code + '.json')); } catch (e) { STROKES[code] = {}; }",
        label="loadStrokes",
    )
    html = replace_exact(
        html,
        "  const fld = langFolder(code);\n  return code === 'en' ? { file: fld + '/audio/w' + a[0] + '.json', key: a[1] } : { file: fld + '/audio/' + code + '-' + a + '.json', key: text };",
        "  return code === 'en' ? { file: langPath(code, 'audio/w' + a[0] + '.json'), key: a[1] } : { file: langPath(code, 'audio/' + code + '-' + a + '.json'), key: text };",
        label="bundleOf",
    )
    html = replace_exact(
        html,
        "  if (track.audio.startsWith('audio/')) return langFolder(code) + '/' + track.audio;",
        "  if (track.audio.startsWith('audio/')) return langPath(code, track.audio);",
        label="resolveTrackAudioSrc",
    )

    # 5. State normalization
    html = replace_exact(
        html,
        "try { const raw = localStorage.getItem(KEY); if (raw) S = Object.assign(fresh(), JSON.parse(raw)); } catch (e) { /* bị chặn lưu trữ */ }",
        "try { const raw = localStorage.getItem(KEY); if (raw) S = Object.assign(fresh(), JSON.parse(raw)); } catch (e) { /* bị chặn lưu trữ */ }\nS.lang = 'zh';",
        label="force S.lang on boot",
    )
    html = replace_exact(html, "S = mergeState(S, remote);", "S = mergeState(S, remote); S.lang = 'zh';", count=2, label="sync normalize lang")
    html = replace_exact(html, "  if (!S.name) return welcomeView();", "  if (!LANGS[S.lang]) S.lang = 'zh';\n  if (!S.name) return welcomeView();", label="route guard S.lang")

    # 6. Schedule & Finish estimate for Chinese-only mode
    html = replace_exact(
        html,
        "const WEEKLY_SCHEDULE = {\n"
        "  1: { // Thứ Hai\n"
        "    name: 'Thứ Hai', focus: 'en',\n"
        "    title: '🇬🇧 Thứ Hai: Trọng tâm Tiếng Anh (Nghe + Nói)',\n"
        "    desc: 'Học 1 bài mới Tiếng Anh (Hội thoại B2 & Phản xạ) · Tiếng Trung & Nhật ôn nhẹ gói 10 từ',\n"
        "    goals: { en: 2.0, zh: 0.5, ja: 0.5 }\n"
        "  },\n"
        "  2: { // Thứ Ba\n"
        "    name: 'Thứ Ba', focus: 'zh',\n"
        "    title: '🇨🇳 Thứ Ba: Trọng tâm Tiếng Trung (Đọc + Viết + Từ vựng)',\n"
        "    desc: 'Học 1 bài mới Tiếng Trung (Bộ thủ, Chiết tự & HSK) · Tiếng Anh & Nhật ôn nhẹ gói 10 từ',\n"
        "    goals: { zh: 2.0, en: 0.5, ja: 0.5 }\n"
        "  },\n"
        "  3: { // Thứ Tư\n"
        "    name: 'Thứ Tư', focus: 'ja',\n"
        "    title: '🇯🇵 Thứ Tư: Trọng tâm Tiếng Nhật (Giải trí + Nghe + Nhại giọng)',\n"
        "    desc: 'Học 1 bài mới Tiếng Nhật N5 & Luyện nghe/nhại giọng · Tiếng Anh & Trung ôn nhẹ gói 10 từ',\n"
        "    goals: { ja: 2.0, en: 0.5, zh: 0.5 }\n"
        "  },\n"
        "  4: { // Thứ Năm\n"
        "    name: 'Thứ Năm', focus: 'en',\n"
        "    title: '🇬🇧 Thứ Năm: Trọng tâm Tiếng Anh (Nghe + Nói)',\n"
        "    desc: 'Học 1 bài mới Tiếng Anh (Podcast & Giao tiếp thực tế) · Tiếng Trung & Nhật ôn nhẹ gói 10 từ',\n"
        "    goals: { en: 2.0, zh: 0.5, ja: 0.5 }\n"
        "  },\n"
        "  5: { // Thứ Sáu\n"
        "    name: 'Thứ Sáu', focus: 'zh',\n"
        "    title: '🇨🇳 Thứ Sáu: Trọng tâm Tiếng Trung (Đọc + Viết + Từ vựng)',\n"
        "    desc: 'Học 1 bài mới Tiếng Trung (Viết Hán tự & Ngữ pháp HSK) · Tiếng Anh & Nhật ôn nhẹ gói 10 từ',\n"
        "    goals: { zh: 2.0, en: 0.5, ja: 0.5 }\n"
        "  },\n"
        "  6: { // Thứ Bảy\n"
        "    name: 'Thứ Bảy', focus: 'ja',\n"
        "    title: '🇯🇵 Thứ Bảy: Trọng tâm Tiếng Nhật (Giải trí + Nghe + Nhại giọng)',\n"
        "    desc: 'Học 1 bài mới Tiếng Nhật N5 & Ôn Kanji · Tiếng Anh & Trung ôn nhẹ gói 10 từ',\n"
        "    goals: { ja: 2.0, en: 0.5, zh: 0.5 }\n"
        "  },\n"
        "  0: { // Chủ Nhật\n"
        "    name: 'Chủ Nhật', focus: 'all',\n"
        "    title: '🧘 Chủ Nhật: Tổng ôn nhẹ 3 ngôn ngữ hoặc Nghỉ ngơi',\n"
        "    desc: 'Không học bài mới · Ôn gói từ vựng dễ quên trong tuần của cả 3 tiếng',\n"
        "    goals: { en: 1.0, zh: 1.0, ja: 1.0 }\n"
        "  }\n"
        "};",
        "const WEEKLY_SCHEDULE = {\n"
        "  1: { name: 'Thứ Hai', focus: 'zh', title: '🇨🇳 Thứ Hai: Từ vựng & Bộ thủ', desc: 'Học 1 bài mới theo lộ trình HSK 3.0 + Ôn gói từ SRS', goals: { zh: 1.0 } },\n"
        "  2: { name: 'Thứ Ba', focus: 'zh', title: '🇨🇳 Thứ Ba: Chiết tự & Tập viết Hán tự', desc: 'Học 1 bài mới + Luyện viết chữ Hán & nhớ bộ thủ', goals: { zh: 1.0 } },\n"
        "  3: { name: 'Thứ Tư', focus: 'zh', title: '🇨🇳 Thứ Tư: Nghe hiểu & Luyện nói Pinyin', desc: 'Học 1 bài mới + Luyện phát âm thanh điệu & hội thoại', goals: { zh: 1.0 } },\n"
        "  4: { name: 'Thứ Năm', focus: 'zh', title: '🇨🇳 Thứ Năm: Đọc hiểu & Ngữ pháp HSK', desc: 'Học 1 bài mới + Thực hành mẫu câu và điền từ ngữ cảnh', goals: { zh: 1.0 } },\n"
        "  5: { name: 'Thứ Sáu', focus: 'zh', title: '🇨🇳 Thứ Sáu: Kỹ năng & Luyện thi HSK/HSKK', desc: 'Học 1 bài mới + Thực hành đề HSK viết & HSKK nói', goals: { zh: 1.0 } },\n"
        "  6: { name: 'Thứ Bảy', focus: 'zh', title: '🇨🇳 Thứ Bảy: Củng cố & Ôn tập SRS', desc: 'Học 1 bài mới + Ôn tập từ vựng & chữ Hán dễ quên', goals: { zh: 1.0 } },\n"
        "  0: { name: 'Chủ Nhật', focus: 'all', title: '🧘 Chủ Nhật: Tổng ôn nhẹ hoặc Nghỉ ngơi', desc: 'Không học bài mới · Ôn nhẹ gói từ vựng & chữ Hán trong tuần', goals: { zh: 1.0 } }\n"
        "};",
        label="WEEKLY_SCHEDULE",
    )
    html = replace_exact(
        html,
        "    // Lịch xoay vòng 2-2-2-1 cân bằng 3 thứ tiếng:\n"
        "    // Tiếng Anh: T2, T5 (2 bài/tuần)\n"
        "    // Tiếng Trung: T3, T6 (2 bài/tuần)\n"
        "    // Tiếng Nhật: T4, T7 (2 bài/tuần)\n"
        "    topicsPerDay = 2 / 7;",
        "    // Lịch đều đặn T2–T7 (6 bài/tuần · Chủ Nhật tổng ôn nhẹ):\n"
        "    topicsPerDay = 6 / 7;",
        label="calcFinishEstimate topicsPerDay",
    )
    html = replace_exact(
        html,
        "function getUnifiedDaySlots(dayIdx) {\n"
        "  const sch = WEEKLY_SCHEDULE[dayIdx] || WEEKLY_SCHEDULE[0];\n"
        "  const isSun = sch.focus === 'all';\n"
        "  const baseItems = [\n"
        "    {\n"
        "      code: 'en',\n"
        "      langTitle: '🇬🇧 Tiếng Anh (Giao tiếp & B2)',\n"
        "      focusTask: 'Học 1 bài mới (Giao tiếp / B2) + Luyện Nghe/Nói phản xạ & Ôn gói 15 từ.',\n"
        "      lightTask: 'Không học bài mới · Ôn nhanh gói 10 từ SRS để giữ phản xạ.'\n"
        "    },\n"
        "    {\n"
        "      code: 'zh',\n"
        "      langTitle: '🇨🇳 Tiếng Trung (Bộ thủ & HSK)',\n"
        "      focusTask: 'Học 1 bài mới (Bộ thủ, Chiết tự & HSK) + Tập viết chữ Hán & Ôn gói 15 từ.',\n"
        "      lightTask: 'Không học bài mới · Ôn nhanh gói 10 từ/chữ Hán đã học.'\n"
        "    },\n"
        "    {\n"
        "      code: 'ja',\n"
        "      langTitle: '🇯🇵 Tiếng Nhật (Giải trí & N5)',\n"
        "      focusTask: 'Học 1 bài mới N5 + Nghe hội thoại / Nhại giọng & Ôn gói 15 từ.',\n"
        "      lightTask: 'Không học bài mới · Ôn nhẹ gói 10 từ Kana/Kanji đã học.'\n"
        "    }\n"
        "  ];",
        "function getUnifiedDaySlots(dayIdx) {\n"
        "  const sch = WEEKLY_SCHEDULE[dayIdx] || WEEKLY_SCHEDULE[0];\n"
        "  const isSun = sch.focus === 'all';\n"
        "  const baseItems = [\n"
        "    {\n"
        "      code: 'zh',\n"
        "      langTitle: '🇨🇳 Tiếng Trung (Bộ thủ, Chiết tự & HSK 1–9)',\n"
        "      focusTask: sch.desc || 'Học 1 bài mới (Bộ thủ, Chiết tự & HSK) + Tập viết chữ Hán & Ôn gói từ SRS.',\n"
        "      lightTask: 'Ôn nhẹ gói từ vựng & chữ Hán đã học.'\n"
        "    }\n"
        "  ];",
        label="getUnifiedDaySlots",
    )

    # 7. Direct-entry navigation & single-language UX (skip language picker screen)
    html = replace_exact(
        html,
        "function langSwitch() {\n"
        "  return h('button', { class: 'langchip', 'aria-label': 'Đang học ' + L().short + '. Đổi ngôn ngữ', onclick: () => { PICK_HUB_OPEN = false; go('pick'); } },\n"
        "    h('span', { lang: L().lang }, L().label), h('span', { class: 'caret', 'aria-hidden': 'true' }, '▾'));\n"
        "}",
        "function langSwitch() {\n"
        "  return h('button', { class: 'langchip', 'aria-label': 'Lộ trình & Thời gian biểu', title: 'Xem lộ trình học & tiến độ', onclick: () => { ROADMAP_LANG = 'zh'; PICK_TAB = 'roadmap'; PICK_HUB_OPEN = true; go('pick'); } },\n"
        "    h('span', {}, '🗺️ Lộ trình'));\n"
        "}",
        label="langSwitch",
    )
    html = replace_exact(
        html,
        "let VIEW = 'pick'; // mở app là màn hình chọn ngôn ngữ",
        "let VIEW = 'home'; // mở thẳng vào trang học Tiếng Trung",
        label="default VIEW",
    )
    html = replace_exact(
        html,
        "        h('span', { class: 'small muted', style: { fontWeight: 600 } }, isSunday ? '🧘 Nghỉ bài mới · Ôn nhẹ ngôn ngữ' : ('🎯 Trọng tâm: ' + LANGS[sch.focus].label))",
        "        h('span', { class: 'small muted', style: { fontWeight: 600 } }, isSunday ? '🧘 Nghỉ bài mới · Tổng ôn nhẹ' : ('🎯 Trọng tâm: ' + ((LANGS[sch.focus] && LANGS[sch.focus].label) || '中文')))",
        label="renderProgressTabContent header",
    )
    html = replace_exact(
        html,
        "  const shortDayNames = { 1: 'T2 (Anh)', 2: 'T3 (Trung)', 3: 'T4 (Nhật)', 4: 'T5 (Anh)', 5: 'T6 (Trung)', 6: 'T7 (Nhật)', 0: 'CN (Ôn)' };\n\n  return [\n    // 2. Bộ chọn Thứ trong tuần để xem hôm đó học gì",
        "  const shortDayNames = { 1: 'T2', 2: 'T3', 3: 'T4', 4: 'T5', 5: 'T6', 6: 'T7', 0: 'CN (Ôn)' };\n\n  return [\n    // 2. Bộ chọn Thứ trong tuần để xem hôm đó học gì",
        label="shortDayNames",
    )
    html = replace_exact(
        html,
        "        h('b', { style: { fontSize: '1rem', color: 'var(--ink)' } }, 'Nguyên tắc Lịch Học Xoay Vòng (1 Ngôn Ngữ Học Mới + 2 Ngôn Ngữ Ôn Nhẹ)')\n"
        "      ),\n"
        "      h('div', { class: 'stack', style: { gap: '5px', fontSize: '.82rem', lineHeight: 1.55, color: 'var(--muted)' } },\n"
        "        h('div', {}, h('b', { style: { color: 'var(--ink)' } }, '• Mỗi ngày chỉ học bài mới của 1 ngôn ngữ: '), 'Xoay vòng T2 & T5 Tiếng Anh · T3 & T6 Tiếng Trung · T4 & T7 Tiếng Nhật · Chủ Nhật nghỉ bài mới.'),\n"
        "        h('div', {}, h('b', { style: { color: 'var(--ink)' } }, '• 2 ngôn ngữ còn lại chỉ ôn duy trì: '), 'Không học bài mới, chỉ ôn nhanh gói 10 từ SRS để giữ phản xạ và chuỗi ngày học.'),",
        "        h('b', { style: { fontSize: '1rem', color: 'var(--ink)' } }, 'Nguyên tắc Học Tiếng Trung Đều Đặn Mỗi Ngày')\n"
        "      ),\n"
        "      h('div', { class: 'stack', style: { gap: '5px', fontSize: '.82rem', lineHeight: 1.55, color: 'var(--muted)' } },\n"
        "        h('div', {}, h('b', { style: { color: 'var(--ink)' } }, '• T2–T7 mỗi ngày học 1 bài mới: '), 'Kết hợp từ vựng, bộ thủ chiết tự, tập viết chữ Hán & luyện nói Pinyin.'),\n"
        "        h('div', {}, h('b', { style: { color: 'var(--ink)' } }, '• Chủ Nhật tổng ôn nhẹ: '), 'Không học bài mới, tập trung ôn nhanh gói từ & chữ Hán SRS để giữ trí nhớ dài hạn.'),",
        label="schedule principles copy",
    )
    html = replace_exact(
        html,
        "          h('p', { class: 'small muted', style: { margin: '4px 0 0 0', fontSize: '.76rem', lineHeight: 1.5 } },\n"
        "            'Xây dựng phản xạ Tiếng Anh giao tiếp, nắm vững Bộ thủ & 10 bài đầu của Tiếng Trung (HSK 1–2) và Tiếng Nhật (N5).'\n"
        "          )\n"
        "        ),\n"
        "        h('div', { class: 'panel', style: { background: 'var(--surface)', border: '1px solid var(--line)', borderRadius: '10px', padding: '10px' } },\n"
        "          h('b', { style: { fontSize: '.84rem', color: 'var(--amber)' } }, '⚡ Giai đoạn 2 (Tháng 4–6): Tăng tốc Nghe & Nói'),\n"
        "          h('p', { class: 'small muted', style: { margin: '4px 0 0 0', fontSize: '.76rem', lineHeight: 1.5 } },\n"
        "            'Đẩy mạnh kỹ năng nghe hội thoại, Shadowing (nhại giọng) và ôn cuốn chiếu gói 10–15 từ dễ quên.'\n"
        "          )\n"
        "        ),\n"
        "        h('div', { class: 'panel', style: { background: 'var(--surface)', border: '1px solid var(--line)', borderRadius: '10px', padding: '10px' } },\n"
        "          h('b', { style: { fontSize: '.84rem', color: 'var(--ink)' } }, '🔄 Giai đoạn 3 (Tháng 6+): Duy trì bền vững'),\n"
        "          h('p', { class: 'small muted', style: { margin: '4px 0 0 0', fontSize: '.76rem', lineHeight: 1.5 } },\n"
        "            'Duy trì đều đặn lịch xoay vòng 2-2-2-1: T2 & T5 Anh · T3 & T6 Trung · T4 & T7 Nhật · CN tổng ôn nhẹ.'\n"
        "          )",
        "          h('p', { class: 'small muted', style: { margin: '4px 0 0 0', fontSize: '.76rem', lineHeight: 1.5 } },\n"
        "            'Nắm vững Pinyin, thanh điệu, Bộ thủ & các bài nền tảng HSK 1–2 cùng tập viết chữ Hán cơ bản.'\n"
        "          )\n"
        "        ),\n"
        "        h('div', { class: 'panel', style: { background: 'var(--surface)', border: '1px solid var(--line)', borderRadius: '10px', padding: '10px' } },\n"
        "          h('b', { style: { fontSize: '.84rem', color: 'var(--amber)' } }, '⚡ Giai đoạn 2 (Tháng 4–6): Trung cấp HSK 3–4'),\n"
        "          h('p', { class: 'small muted', style: { margin: '4px 0 0 0', fontSize: '.76rem', lineHeight: 1.5 } },\n"
        "            'Mở rộng vốn chữ Hán qua Chiết tự, luyện đọc hội thoại dài và ôn cuốn chiếu gói 10–15 từ dễ quên.'\n"
        "          )\n"
        "        ),\n"
        "        h('div', { class: 'panel', style: { background: 'var(--surface)', border: '1px solid var(--line)', borderRadius: '10px', padding: '10px' } },\n"
        "          h('b', { style: { fontSize: '.84rem', color: 'var(--ink)' } }, '🏆 Giai đoạn 3 (Tháng 6+): Chinh phục HSK 5–9 & HSKK'),\n"
        "          h('p', { class: 'small muted', style: { margin: '4px 0 0 0', fontSize: '.76rem', lineHeight: 1.5 } },\n"
        "            'Luyện đề HSK & HSKK các cấp độ cao, đọc hiểu chuyên sâu và duy trì ôn tập SRS.'\n"
        "          )",
        label="schedule 3 stages copy",
    )
    html = replace_exact(
        html,
        "? 'Lộ trình cả 3 ngôn ngữ'",
        "? 'Lộ trình Tiếng Trung (HSK 3.0)'",
        label="roadmap header subtitle",
    )
    html = replace_exact(
        html,
        "  const paces = [\n"
        "    { id: 'schedule', name: '📅 Lịch chuẩn (2-2-2-1)', desc: currentLang === 'en' ? 'T2, T5 (2 bài/tuần)' : (currentLang === 'zh' ? 'T3, T6 (2 bài/tuần)' : (currentLang === 'ja' ? 'T4, T7 (2 bài/tuần)' : 'Mỗi tiếng 2 bài/tuần · CN ôn tổng hợp')) },\n"
        "    { id: 'daily1', name: '⚡ 1 bài/ngày', desc: '7 bài/tuần · Đều đặn mỗi ngày' },\n"
        "    { id: 'daily2', name: '🔥 2 bài/ngày', desc: '14 bài/tuần · Tăng tốc bứt phá' }\n"
        "  ];\n\n"
        "  const langFilterPills = [\n"
        "    { id: S.lang, label: (LANGS[S.lang] ? LANGS[S.lang].label : 'Ngôn ngữ đang học') + ' (Đang học)' },\n"
        "    ...Object.entries(LANGS).filter(([c]) => c !== S.lang).map(([c, v]) => ({ id: c, label: v.label })),\n"
        "    { id: 'all', label: '🌐 Cả 3 ngôn ngữ' }\n"
        "  ];",
        "  const paces = [\n"
        "    { id: 'schedule', name: '📅 Lịch đều đặn (T2–T7)', desc: '6 bài/tuần · CN tổng ôn' },\n"
        "    { id: 'daily1', name: '⚡ 1 bài/ngày', desc: '7 bài/tuần · Đều đặn mỗi ngày' },\n"
        "    { id: 'daily2', name: '🔥 2 bài/ngày', desc: '14 bài/tuần · Tăng tốc bứt phá' }\n"
        "  ];\n\n"
        "  const langFilterPills = [\n"
        "    { id: 'zh', label: '🇨🇳 中文 (HSK 3.0)' }\n"
        "  ];",
        label="roadmap paces and filter pills",
    )
    html = replace_exact(
        html,
        "        STUDY_PACE === 'schedule'\n"
        "          ? (currentLang === 'en'\n"
        "              ? '💡 Lịch chuẩn Tiếng Anh (Thứ 2 & Thứ 5): Học 2 bài mới/tuần (Nghe + Nói & Giao tiếp B2), các ngày khác ôn gói 10 từ.'\n"
        "              : (currentLang === 'zh'\n"
        "                ? '💡 Lịch chuẩn Tiếng Trung (Thứ 3 & Thứ 6): Học 2 bài mới/tuần (Bộ thủ, Chiết tự & HSK), các ngày khác ôn gói 10 từ.'\n"
        "                : (currentLang === 'ja'\n"
        "                  ? '💡 Lịch chuẩn Tiếng Nhật (Thứ 4 & Thứ 7): Học 2 bài mới/tuần (Nghe hội thoại & N5), các ngày khác ôn gói 10 từ.'\n"
        "                  : '💡 Lịch xoay vòng 2-2-2-1: Anh (T2, T5) · Trung (T3, T6) · Nhật (T4, T7) · Chủ nhật tổng ôn nhẹ.')))",
        "        STUDY_PACE === 'schedule'\n"
        "          ? '💡 Lịch đều đặn (Thứ 2 – Thứ 7): Học 6 bài mới/tuần kết hợp tập viết & ôn SRS · Chủ Nhật tổng ôn nhẹ.'",
        label="roadmap schedule description",
    )
    html = replace_exact(
        html,
        "  if (!PICK_HUB_OPEN) {\n",
        "  PICK_HUB_OPEN = true;\n  if (!PICK_HUB_OPEN) {\n",
        label="force PICK_HUB_OPEN true",
    )
    html = replace_exact(
        html,
        "      ['progress', '📊 Tiến độ ngôn ngữ'],\n",
        "      ['progress', '📊 Tiến độ Tiếng Trung'],\n",
        label="pick tab progress label",
    )
    html = replace_exact(
        html,
        "        onclick: () => { PICK_HUB_OPEN = false; pickView(); }\n      }, '← Quay lại chọn ngôn ngữ'),",
        "        onclick: () => { PICK_HUB_OPEN = false; go('home'); }\n      }, '← Về trang Học'),",
        label="pick hub back button",
    )
    html = replace_exact(
        html,
        "      h('p', { class: 'label' }, 'Lingogo'),\n"
        "      h('h1', {}, 'Học để nói được, mỗi ngày một chút'),\n"
        "      h('p', { class: 'muted' }, 'Ba thứ tiếng trong một app: bài học theo chủ đề, ôn tập đúng lúc, luyện nói và tập viết chữ Hán, kana.'),",
        "      h('p', { class: 'label' }, 'Lingogo Chinese'),\n"
        "      h('h1', {}, 'Học để nói được, mỗi ngày một chút'),\n"
        "      h('p', { class: 'muted' }, 'Học Tiếng Trung từ nền tảng đến nâng cao (HSK 1–9): từ vựng theo chủ đề, bộ thủ & chiết tự, tập viết chữ Hán, luyện nói & đề thi HSK/HSKK.'),",
        label="welcome header",
    )
    html = replace_exact(
        html,
        "    goals.replaceChildren(...[[20, 'Tối thiểu', '20 XP ≈ 4 từ mới mỗi thứ tiếng'], [30, 'Vừa phải', '30 XP mỗi thứ tiếng'], [50, 'Nghiêm túc', '50 XP mỗi thứ tiếng']]\n"
        "      .map(([v, t, s]) => h('button', { 'aria-pressed': String(goal === v), onclick: () => { goal = v; draw(); } }, h('span', {}, h('b', {}, t), ' · ', h('span', { class: 'muted' }, s)))));\n"
        "    langs.replaceChildren(...Object.entries(LANGS).map(([k, v]) => h('button', { 'aria-pressed': String(lang === k), lang: v.lang, onclick: () => { lang = k; draw(); start.textContent = 'Bắt đầu học ' + LANGS[lang].short; } }, v.label)));",
        "    goals.replaceChildren(...[[20, 'Tối thiểu', '20 XP ≈ 4 từ mới mỗi ngày'], [30, 'Vừa phải', '30 XP mỗi ngày'], [50, 'Nghiêm túc', '50 XP mỗi ngày']]\n"
        "      .map(([v, t, s]) => h('button', { 'aria-pressed': String(goal === v), onclick: () => { goal = v; draw(); } }, h('span', {}, h('b', {}, t), ' · ', h('span', { class: 'muted' }, s)))));",
        label="welcome goals without lang picker",
    )
    html = replace_exact(
        html,
        "    h('div', { class: 'stack' }, h('span', { class: 'label' }, 'Bạn muốn học thứ tiếng nào trước?'), langs, h('p', { class: 'small muted' }, 'Có thể đổi sang thứ tiếng khác bất cứ lúc nào.')),\n"
        "    h('div', { class: 'stack' }, h('span', { class: 'label' }, 'Mục tiêu mỗi ngày, cho từng thứ tiếng'), goals),\n"
        "    (start = h('button', { class: 'primary block', onclick: () => { S.name = name.value.trim() || 'bạn'; S.goal = goal; S.lang = lang; save(); go('home'); } }, 'Bắt đầu học ' + LANGS[lang].short))));",
        "    h('div', { class: 'stack' }, h('span', { class: 'label' }, 'Mục tiêu mỗi ngày'), goals),\n"
        "    (start = h('button', { class: 'primary block', onclick: () => { S.name = name.value.trim() || 'bạn'; S.goal = goal; S.lang = 'zh'; save(); go('home'); } }, 'Bắt đầu học Tiếng Trung'))));",
        label="welcome start button",
    )

    # 8. Review buttons, branding copy, achievements, reset warning
    html = replace_exact(
        html,
        "          h('button', { class: 'ghost', onclick: () => go('pick') }, 'Về Màn hình chính')",
        "          h('button', { class: 'ghost', onclick: () => { PICK_TAB = 'roadmap'; PICK_HUB_OPEN = true; go('pick'); } }, '🗺️ Xem lộ trình')",
        count=2,
        label="reviewView pick buttons",
    )
    html, n_footer = re.subn(
        r"'Lingogo v[0-9.]+ · Cập nhật [^']+'",
        f"'Lingogo Chinese v{app_ver} · Cập nhật 26/11/2026'",
        html,
    )
    assert n_footer == 1, f"Expected 1 homeView footer match, got {n_footer}"
    html = replace_exact(
        html,
        "h('p', { class: 'label' }, 'Lingogo'),\n        h('h1', {}, 'Chào ' + S.name + ', hôm nay học gì?')",
        "h('p', { class: 'label' }, 'Lingogo Chinese'),\n        h('h1', {}, 'Chào ' + S.name + ', hôm nay học gì?')",
        label="pickView label",
    )
    html = replace_exact(html, "tab Học của Lingogo", "tab Học của Lingogo Chinese", label="knowledge tip 1")
    html = replace_exact(html, "Tab Ôn tập của Lingogo", "Tab Ôn tập của Lingogo Chinese", label="knowledge tip 2")
    html = replace_exact(
        html,
        "  ['streak3', 'Ba ngày liền', 'Đạt mục tiêu một thứ tiếng 3 ngày liên tiếp', () => Object.keys(LANGS).some((c) => streak(c) >= 3)],\n"
        "  ['streak7', 'Một tuần bền bỉ', 'Đạt mục tiêu một thứ tiếng 7 ngày liên tiếp', () => Object.keys(LANGS).some((c) => streak(c) >= 7)],\n"
        "  ['goal3', 'Đủ cả ba', 'Một ngày đạt mục tiêu cả Anh, Trung, Nhật', () => Object.keys(LANGS).every((c) => metGoal(todayN(), c))],\n"
        "  ['words100', 'Trăm từ', '100 từ trong hàng ôn tập', () => Object.keys(S.srs).filter((k) => /:(w|v)/.test(k)).length >= 100],\n"
        "  ['polyglot', 'Ba thứ tiếng', 'Học ít nhất một bài mỗi thứ tiếng', () => ['en', 'zh', 'ja'].every((c) => Object.keys(S.lessons).some((k) => k.startsWith(c + ':')))],\n"
        "  ['speak20', 'Dám mở lời', 'Nói đạt từ 80% ở 20 câu', () => Object.values(S.spoken).filter((v) => v >= 80).length >= 20],\n"
        "  ['write50', 'Nắn nót', 'Tập viết 50 chữ khác nhau', () => Object.keys(S.written).length >= 50],",
        "  ['streak3', 'Ba ngày liền', 'Đạt mục tiêu Tiếng Trung 3 ngày liên tiếp', () => streak('zh') >= 3],\n"
        "  ['streak7', 'Một tuần bền bỉ', 'Đạt mục tiêu Tiếng Trung 7 ngày liên tiếp', () => streak('zh') >= 7],\n"
        "  ['words100', 'Trăm từ', '100 từ trong hàng ôn tập', () => Object.keys(S.srs).filter((k) => /:(w|v)/.test(k)).length >= 100],\n"
        "  ['lessons10', 'Chăm chỉ', 'Hoàn thành 10 bài học Tiếng Trung', () => Object.keys(S.lessons).filter((k) => k.startsWith('zh:')).length >= 10],\n"
        "  ['speak20', 'Dám mở lời', 'Nói đạt từ 80% ở 20 câu', () => Object.values(S.spoken).filter((v) => v >= 80).length >= 20],\n"
        "  ['write50', 'Nắn nót', 'Tập viết 50 chữ Hán khác nhau', () => Object.keys(S.written).length >= 50],",
        label="ACH single-language Chinese",
    )
    html = replace_exact(
        html,
        "      `### 💬 [Báo lỗi Lingogo] ${tagObj.label}\\n` +",
        "      `### 💬 [Báo lỗi Lingogo Chinese] ${tagObj.label}\\n` +",
        label="feedback title",
    )
    html = replace_exact(
        html,
        "if (!confirmReset) { confirmReset = true; resetBtn.textContent = 'Bấm lần nữa để xóa toàn bộ tiến độ của cả ba thứ tiếng'; return; }",
        "if (!confirmReset) { confirmReset = true; resetBtn.textContent = 'Bấm lần nữa để xóa toàn bộ tiến độ học Tiếng Trung'; return; }",
        label="reset button warning",
    )

    DST_HTML.write_text(html, encoding="utf-8")
    print(f"Generated {DST_HTML} ({len(html.encode('utf-8')):,} bytes, build {build_id}, v{app_ver})")


if __name__ == "__main__":
    main()
