"""Generate single-language Lingogo Chinese index.html from lingogo/index.html
with UI/UX parity matching Lingogo English (Duolingo Section/Unit S-path, 5 tabs,
3D Flashcards, Offline Chinese Dictionary, Practice Hub, Minutes tracking)."""
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
        raise ValueError(f"Expected {count} match(es) for {label or repr(old[:80])}, found {found}")
    return src.replace(old, new)


def replace_json_lang_only(src: str, const_name: str) -> str:
    m = re.search(rf"const {re.escape(const_name)} = (\{{.*?\}});", src)
    if not m:
        raise ValueError(f"Could not find const {const_name}")
    obj = json.loads(m.group(1))
    trimmed = json.dumps({LANG_CODE: obj[LANG_CODE]}, ensure_ascii=False, separators=(",", ":"))
    return src[:m.start()] + f"const {const_name} = {trimmed};" + src[m.end():]


DUO_CSS = """
.sec-acc { border: none; border-radius: 0; background: transparent; overflow: visible; }
.sec-hdr {
  width: 100%; border: none; border-radius: 18px;
  background: var(--sec-col, #58cc02); color: #fff;
  padding: 14px 16px; display: flex; align-items: center; justify-content: space-between;
  gap: 12px; text-align: left; cursor: pointer; list-style: none; user-select: none;
  box-shadow: 0 4px 0 var(--sec-lip, #46a302);
  transition: filter .18s ease, box-shadow .18s ease, transform .12s ease;
}
summary.sec-hdr::-webkit-details-marker { display: none; }
.sec-hdr .acc-arrow { transition: transform .18s ease; opacity: .92; flex: none; font-size: .9rem; color: #fff; }
.sec-ico {
  width: 46px; height: 46px; border-radius: 14px; flex: none;
  display: grid; place-items: center; font-size: 1.5rem; line-height: 1;
  background: rgba(255, 255, 255, .2); border: 1.5px solid rgba(255, 255, 255, .36);
}
.sec-kicker {
  font-size: .7rem; font-weight: 800; letter-spacing: .06em; text-transform: uppercase;
  color: rgba(255, 255, 255, .94);
}
.sec-hdr .muted { color: rgba(255, 255, 255, .88); }
.sec-hdr .chip.level {
  background: rgba(255, 255, 255, .22) !important;
  color: #fff !important;
  border-color: rgba(255, 255, 255, .38) !important;
  box-shadow: none !important;
}
.sec-prog {
  height: 5px; border-radius: 99px; background: rgba(255, 255, 255, .28);
  margin-top: 6px; overflow: hidden; width: 100%;
}
.sec-prog > i { display: block; height: 100%; background: #fff; border-radius: 99px; transition: width .3s ease; }
.sec-acc.sec-featured > .sec-hdr,
details.sec-acc[open] > .sec-hdr {
  box-shadow: 0 4px 0 var(--sec-lip, #46a302), 0 8px 22px var(--sec-glow, rgba(88, 204, 2, .24));
}
details.sec-acc[open] > .sec-hdr .acc-arrow { transform: rotate(180deg); }
.sec-body { padding: 14px 0 6px; display: flex; flex-direction: column; gap: 16px; }
.sec-test-btn {
  flex: none; display: inline-flex; align-items: center; justify-content: center;
  min-height: 36px; padding: 6px 12px; border-radius: 12px;
  background: rgba(0, 0, 0, .16); border: 2px solid rgba(255, 255, 255, .36);
  color: #fff; box-shadow: 0 2px 0 rgba(0, 0, 0, .16);
  font-size: .74rem; font-weight: 800; letter-spacing: .05em;
  text-transform: uppercase; cursor: pointer; white-space: nowrap;
}
.sec-test-btn:hover { background: rgba(0, 0, 0, .26); }
.sec-test-btn:active { transform: translateY(2px); box-shadow: 0 1px 0 rgba(0, 0, 0, .16); }
.duo-unit { border: none; border-radius: 0; background: transparent; overflow: visible; margin-bottom: 4px; }
summary.duo-unit-hdr {
  width: 100%; border: 2px solid var(--unit-col, #58cc02); border-radius: 16px; padding: 13px 15px;
  display: flex; align-items: center; justify-content: space-between; gap: 10px;
  text-align: left; background: var(--surface); color: var(--ink); cursor: pointer; list-style: none; user-select: none;
  box-shadow: 0 3px 0 var(--unit-lip, rgba(70, 163, 2, .4));
  transition: border-color .18s ease, box-shadow .18s ease, background .18s ease;
}
details.duo-unit[open] > summary.duo-unit-hdr {
  background: linear-gradient(135deg, var(--unit-soft, rgba(88, 204, 2, .10)) 0%, var(--surface) 100%);
}
summary.duo-unit-hdr::-webkit-details-marker { display: none; }
.duo-unit-hdr .acc-arrow { transition: transform .18s ease; opacity: .9; flex: none; font-size: .85rem; color: var(--unit-col, var(--muted)); }
details.duo-unit[open] > summary .acc-arrow { transform: rotate(180deg); }
.duo-unit-hdr .duo-u-meta { flex: 1; min-width: 0; }
.duo-unit-hdr .duo-u-kicker {
  font-size: .69rem; font-weight: 800; letter-spacing: .04em; text-transform: uppercase;
  color: var(--unit-col, var(--teal)); display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.duo-unit-hdr .duo-u-title { font-size: 1.04rem; font-weight: 800; display: block; line-height: 1.26; margin-top: 2px; color: var(--ink); }
.duo-guidebook-btn {
  flex: none; display: inline-flex; align-items: center; gap: 5px;
  min-height: 36px; padding: 6px 11px; border-radius: 12px;
  background: var(--unit-col, #58cc02); border: none;
  box-shadow: 0 2px 0 var(--unit-lip, #46a302);
  color: #fff; font-size: .72rem; font-weight: 800; letter-spacing: .04em;
  text-transform: uppercase; cursor: pointer; white-space: nowrap;
}
.duo-guidebook-btn:hover { filter: brightness(1.07); }
.duo-guidebook-btn:active { transform: translateY(1px); box-shadow: 0 1px 0 var(--unit-lip, #46a302); }
.duo-path {
  display: flex; flex-direction: column; align-items: center; gap: 26px;
  padding: 26px 8px 18px; position: relative;
}
.duo-step { display: flex; flex-direction: column; align-items: center; width: 100%; position: relative; }
.duo-node-anchor { display: flex; flex-direction: column; align-items: center; transform: translateX(var(--duo-x, 0px)); transition: transform .2s ease; position: relative; }
.duo-float-tip {
  position: relative; margin-bottom: 6px; padding: 7px 16px; border-radius: 12px;
  background: #ffffff; border: 2px solid #e2e8f0; color: #1cb0f6;
  font-size: .82rem; font-weight: 800; letter-spacing: .05em; text-transform: uppercase;
  box-shadow: 0 4px 10px rgba(15, 23, 42, .12); animation: duoBounce 1.8s ease-in-out infinite;
  white-space: nowrap; cursor: pointer; min-height: 0; z-index: 2;
}
.duo-float-tip::before {
  content: ''; position: absolute; left: 50%; bottom: -7px; transform: translateX(-50%) rotate(45deg);
  width: 11px; height: 11px; background: #ffffff; border-right: 2px solid #e2e8f0; border-bottom: 2px solid #e2e8f0;
}
.duo-float-tip::after {
  content: ''; position: absolute; left: 50%; bottom: 0; transform: translateX(-50%);
  width: 18px; height: 4px; background: #ffffff;
}
:root[data-theme="dark"] .duo-float-tip {
  background: #202f36; border-color: #37464f; box-shadow: 0 4px 12px rgba(0, 0, 0, .3);
}
:root[data-theme="dark"] .duo-float-tip::before {
  background: #202f36; border-right-color: #37464f; border-bottom-color: #37464f;
}
:root[data-theme="dark"] .duo-float-tip::after { background: #202f36; }
@keyframes duoBounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-4px); } }
.duo-node-stage {
  position: relative; width: 112px; height: 98px;
  display: flex; align-items: center; justify-content: center;
}
.duo-node-stage.compact { width: 78px; height: 68px; }
.duo-ring-svg {
  position: absolute; inset: 0; width: 112px; height: 98px;
  pointer-events: none; overflow: visible;
}
.duo-ring-track { stroke: #d8e0e8; }
:root[data-theme="dark"] .duo-ring-track { stroke: #37464f; }
.duo-btn {
  position: relative; z-index: 1;
  width: 74px; height: 60px; min-height: 0; padding: 0; border-radius: 50%; border: none;
  display: flex; align-items: center; justify-content: center;
  transform: translateY(-3px);
  transition: transform .1s ease, box-shadow .1s ease; cursor: pointer;
}
.duo-btn.cur, .duo-btn.prog {
  background: #1cb0f6; color: #fff;
  box-shadow: 0 8px 0 #1899d6, inset 0 2px 0 rgba(255,255,255,.24);
}
.duo-btn.cur:active, .duo-btn.prog:active { transform: translateY(1px); box-shadow: 0 3px 0 #1899d6; }
.duo-btn.done {
  background: #ffc800; color: #fff;
  box-shadow: 0 8px 0 #d69e00, inset 0 2px 0 rgba(255,255,255,.28);
}
.duo-btn.done:active { transform: translateY(1px); box-shadow: 0 3px 0 #d69e00; }
.duo-btn.idle {
  width: 72px; height: 56px;
  background: #e5e5e5; color: #9ca3af;
  box-shadow: 0 8px 0 #c7c7c7, inset 0 2px 0 rgba(255,255,255,.5);
}
.duo-btn.idle:active { transform: translateY(1px); box-shadow: 0 3px 0 #c7c7c7; }
:root[data-theme="dark"] .duo-btn.idle {
  background: #37464f; color: #6e818d;
  box-shadow: 0 8px 0 #263138, inset 0 2px 0 rgba(255,255,255,.06);
}
:root[data-theme="dark"] .duo-btn.idle:active { box-shadow: 0 3px 0 #263138; }
.duo-popover {
  position: relative; width: 100%; max-width: 440px; margin-top: 14px; padding: 14px; border-radius: 18px;
  background: var(--surface); border: 2px solid var(--bubble-col, #1cb0f6);
  box-shadow: 0 12px 28px rgba(0,0,0,.22);
  display: flex; flex-direction: column; gap: 10px; animation: fadeInDown .16s ease; z-index: 3;
}
.duo-popover::before, .duo-popover::after {
  content: ''; position: absolute; left: clamp(28px, calc(50% + var(--duo-x, 0px)), calc(100% - 28px));
  transform: translateX(-50%) rotate(45deg); pointer-events: none;
}
.duo-popover::before {
  top: -10px; width: 18px; height: 18px; background: var(--surface);
  border-top: 2px solid var(--bubble-col, #1cb0f6); border-left: 2px solid var(--bubble-col, #1cb0f6);
}
.duo-popover::after {
  top: -7px; width: 16px; height: 16px; background: var(--surface);
}
.duo-cta-btn {
  width: 100%; border: none; border-radius: 14px; min-height: 46px; padding: 10px 14px;
  font-weight: 800; font-size: .94rem; letter-spacing: .02em; color: #fff;
  background: var(--bubble-col, #1cb0f6);
  box-shadow: 0 4px 0 rgba(0,0,0,.22); transition: transform .1s ease, box-shadow .1s ease;
}
.duo-cta-btn:active { transform: translateY(2px); box-shadow: 0 2px 0 rgba(0,0,0,.22); }
"""


NEW_CURRICULUM_HELPERS = """function buildCurriculumSections(code, d) {
  const cats = (CATEGORIES[code] || []).filter((c) => c.id !== 'all');
  const defCat = code === 'zh' ? 'hsk1' : (code === 'ja' ? 'n5' : 'a1');
  if (!cats.length) {
    const units = [];
    let uCur = null;
    for (const t of (d.topics || [])) {
      const uName = cleanPhaseName(t.phase) || ('Unit ' + (units.length + 1));
      if (!uCur || uCur.name !== uName) {
        uCur = { num: units.length + 1, secNum: 1, secId: 'all', secLevel: '', id: 'all:u' + (units.length + 1), name: uName, topics: [] };
        units.push(uCur);
      }
      uCur.topics.push(t);
    }
    return [{ num: 1, id: 'all', name: d.name || 'Lộ trình', level: '', short: '', icon: '📘', desc: '', units, topics: d.topics || [] }];
  }
  return cats.map((c, secIdx) => {
    const secTopics = (d.topics || []).filter((t) => (t.category || defCat) === c.id);
    const rawUnits = [];
    let uCur = null;
    for (const t of secTopics) {
      const uName = cleanPhaseName(t.phase) || ('Chủ đề ' + (rawUnits.length + 1));
      if (!uCur || uCur.name !== uName) {
        uCur = { name: uName, topics: [] };
        rawUnits.push(uCur);
      }
      uCur.topics.push(t);
    }
    const expanded = [];
    rawUnits.forEach((ru) => {
      if (ru.topics.length > 7) {
        const nChunks = Math.ceil(ru.topics.length / 6);
        const chunkSz = Math.ceil(ru.topics.length / nChunks);
        for (let i = 0; i < ru.topics.length; i += chunkSz) {
          expanded.push({ name: `${ru.name} (Phần ${Math.floor(i / chunkSz) + 1})`, topics: ru.topics.slice(i, i + chunkSz) });
        }
      } else {
        expanded.push(ru);
      }
    });
    const units = expanded.map((u, ui) => ({
      num: ui + 1,
      secNum: secIdx + 1,
      secId: c.id,
      secLevel: c.level,
      id: `${c.id}:u${ui + 1}`,
      name: u.name,
      topics: u.topics
    }));
    return {
      num: secIdx + 1,
      id: c.id,
      name: String(c.name || '').replace(/^(?:Sơ cấp\\s*\\d+|Trung cấp\\s*\\d+|Cao cấp\\s*\\d+)\\s*[·.:-]\\s*/i, '').trim() || c.name,
      level: c.level,
      short: c.short,
      icon: c.icon,
      desc: c.desc,
      catObj: c,
      units,
      topics: secTopics
    };
  }).filter((s) => s.topics.length > 0);
}
"""


NEW_DICT_FLASHCARD_PRACTICE = """function dictBtn() {
  return h('button', {
    type: 'button',
    class: 'dict-btn',
    title: 'Từ điển Tiếng Trung Offline',
    'aria-label': 'Từ điển Tiếng Trung Offline',
    onclick: () => go('dict')
  }, '🔍');
}

function normPinyinPlain(s) {
  return String(s || '').normalize('NFD').replace(/[\\u0300-\\u036f]/g, '').replace(/ü/g, 'u').toLowerCase();
}

function dictView() {
  ACTIVE_STUDY_MODE = true;
  setTabs(false);
  const d = DATA.zh;
  const qRaw = (DICT_Q || '').trim();
  const q = qRaw.toLowerCase();
  const qPy = normPinyinPlain(qRaw);
  const isOffline = typeof navigator !== 'undefined' && navigator.onLine === false;

  const allItems = [];
  const seen = new Set();
  if (d && d.topics) {
    d.topics.forEach((tp) => {
      const catLv = (tp.category || 'hsk1').toUpperCase();
      (tp.vocab || []).forEach((v) => {
        if (!v || !v.w) return;
        const w = plain(v.w);
        const key = 'v:' + w + '|' + (v.m || '');
        if (seen.has(key)) return;
        seen.add(key);
        const chInfo = d.chars && w.length === 1 ? d.chars[w] : null;
        allItems.push({
          kind: 'vocab',
          w,
          lv: catLv,
          r: v.r || '',
          hv: chInfo && chInfo.hv ? chInfo.hv : '',
          m: v.m || '',
          d: chInfo && chInfo.rad ? ('Bộ thủ: ' + chInfo.rad) : '',
          ex: v.ex ? plain(v.ex) : '',
          exr: v.exr || '',
          exm: v.exm || '',
          src: (tp.sub || tp.title || '') + ' (' + catLv + ')'
        });
      });
    });
  }
  if (d && d.chiet_tu) {
    d.chiet_tu.forEach((ct) => {
      if (!ct || !ct.char) return;
      allItems.push({
        kind: 'chiet_tu',
        w: ct.char,
        lv: ct.type || 'Chiết tự',
        r: ct.pinyin || '',
        hv: ct.hv || '',
        m: ct.m || '',
        d: [ct.parts, ct.story].filter(Boolean).join(' · '),
        ex: ct.ex || '',
        exr: '',
        exm: '',
        src: 'Chiết tự chữ Hán' + (ct.rad ? ' · Bộ ' + ct.rad : '')
      });
    });
  }
  if (d && d.chars) {
    Object.entries(d.chars).forEach(([ch, info]) => {
      if (!info || (!info.hv && !info.m)) return;
      allItems.push({
        kind: 'char',
        w: ch,
        lv: info.rad ? ('Bộ ' + info.rad) : 'Hán tự',
        r: '',
        hv: info.hv || '',
        m: info.m || '',
        d: info.story || info.parts || '',
        ex: info.ex || '',
        exr: '',
        exm: '',
        src: 'Kho chữ Hán Hán Việt'
      });
    });
  }

  let matches = allItems.filter((it) => {
    if (DICT_FILTER !== 'all' && it.kind !== DICT_FILTER) return false;
    if (!q) return true;
    return it.w.indexOf(qRaw) !== -1 ||
      (it.r && (it.r.toLowerCase().indexOf(q) !== -1 || normPinyinPlain(it.r).indexOf(qPy) !== -1)) ||
      (it.hv && it.hv.toLowerCase().indexOf(q) !== -1) ||
      it.m.toLowerCase().indexOf(q) !== -1 ||
      (it.d && it.d.toLowerCase().indexOf(q) !== -1) ||
      (it.ex && it.ex.indexOf(qRaw) !== -1);
  });

  if (q) {
    matches.sort((a, b2) => {
      const aw = a.w.toLowerCase(), bw = b2.w.toLowerCase();
      const aExact = (aw === qRaw || normPinyinPlain(a.r) === qPy) ? 0 : (aw.indexOf(qRaw) === 0 ? 1 : 2);
      const bExact = (bw === qRaw || normPinyinPlain(b2.r) === qPy) ? 0 : (bw.indexOf(qRaw) === 0 ? 1 : 2);
      if (aExact !== bExact) return aExact - bExact;
      const order = { vocab: 0, chiet_tu: 1, char: 2 };
      if (order[a.kind] !== order[b2.kind]) return order[a.kind] - order[b2.kind];
      return aw.length - bw.length;
    });
  }

  const totalMatches = matches.length;
  const shown = matches.slice(0, 60);

  const cards = shown.map((it) => h('div', { class: 'dict-item stack', style: { gap: '6px' } },
    h('div', { class: 'row between', style: { alignItems: 'flex-start', gap: '8px' } },
      h('div', { class: 'stack', style: { gap: '2px', flex: 1, minWidth: 0 } },
        h('div', { class: 'row wrap', style: { gap: '8px', alignItems: 'baseline' } },
          h('b', { lang: 'zh-Hans', style: { fontSize: '1.22rem', color: 'var(--teal)' } }, it.w),
          it.r ? h('span', { class: 'read small', style: { color: 'var(--muted)', fontWeight: 600 } }, it.r) : null,
          it.hv ? h('span', { class: 'chip small', style: { fontSize: '.7rem' } }, it.hv.toUpperCase()) : null
        ),
        h('div', { style: { fontWeight: 600, fontSize: '.95rem' } }, it.m),
        it.d ? h('div', { class: 'small muted', style: { lineHeight: 1.45 } }, it.d) : null
      ),
      spk('zh', it.w)
    ),
    it.ex ? h('div', {
      class: 'row between',
      style: { alignItems: 'center', gap: '8px', padding: '6px 8px', borderRadius: '8px', background: 'rgba(15,82,87,.05)' }
    },
      h('div', { class: 'stack', style: { gap: '2px', flex: 1, minWidth: 0 } },
        h('span', { class: 'small', lang: 'zh-Hans', style: { fontWeight: 500 } }, it.ex),
        it.exr ? h('span', { class: 'small muted', style: { fontSize: '.78rem' } }, it.exr) : null,
        it.exm ? h('span', { class: 'small muted', style: { fontSize: '.78rem' } }, it.exm) : null
      ),
      spk('zh', it.ex)
    ) : null,
    h('div', { class: 'row between wrap', style: { gap: '6px', alignItems: 'center' } },
      h('span', { class: 'chip small ' + (it.kind === 'chiet_tu' ? 'good' : ''), style: { fontSize: '.7rem' } },
        it.kind === 'chiet_tu' ? '🧩 Chiết tự' : (it.kind === 'char' ? '🈴 Hán tự' : '📚 ' + it.lv)
      ),
      h('span', { class: 'small muted', style: { fontSize: '.74rem' } }, it.src)
    )
  ));

  const extBox = qRaw ? h('div', { class: 'panel stack', style: { gap: '8px', padding: '12px', background: 'rgba(15,82,87,.04)' } },
    h('div', { class: 'row between wrap', style: { gap: '8px', alignItems: 'center' } },
      h('span', { class: 'small', style: { fontWeight: 600 } }, 'Nghe phát âm & tra thêm cho “' + qRaw + '”:'),
      h('button', { type: 'button', class: 'accent mini', onclick: () => say('zh', qRaw) }, '🔊 Nghe phát âm')
    ),
    !isOffline ? h('div', { class: 'row wrap', style: { gap: '6px' } },
      h('a', {
        class: 'ghost mini',
        href: 'https://hanzii.net/search/word/' + encodeURIComponent(qRaw),
        target: '_blank', rel: 'noopener noreferrer',
        style: { textDecoration: 'none', padding: '5px 10px', borderRadius: '8px', border: '1px solid var(--line)' }
      }, 'Hanzii Online ↗'),
      h('a', {
        class: 'ghost mini',
        href: 'https://translate.google.com/?sl=zh-CN&tl=vi&text=' + encodeURIComponent(qRaw),
        target: '_blank', rel: 'noopener noreferrer',
        style: { textDecoration: 'none', padding: '5px 10px', borderRadius: '8px', border: '1px solid var(--line)' }
      }, 'Google Dịch ↗')
    ) : h('p', { class: 'small muted', style: { margin: 0 } }, '⚡ Đang ngoại tuyến: bạn vẫn tra từ điển Tiếng Trung Offline và nghe phát âm bình thường.')
  ) : null;

  mount(h('div', { class: 'stack-lg', style: { gap: '10px' } },
    h('div', { class: 'row between wrap', style: { alignItems: 'center', gap: '6px' } },
      h('button', { type: 'button', class: 'ghost mini', onclick: () => { setTabs(true); go('review'); } }, '← Từ vựng'),
      h('span', { class: 'chip good small' }, isOffline ? '⚡ Đang Offline · Sẵn sàng' : '📖 Từ điển Trung Offline')
    ),
    h('div', { class: 'row', style: { gap: '6px', alignItems: 'center' } },
      h('input', Object.assign({
        type: 'search',
        class: 'zh-dict-inp',
        value: DICT_Q,
        placeholder: '🔍 Tra chữ Hán, Pinyin (vd: nihao), Hán Việt hoặc nghĩa Việt...',
        style: { flex: 1, padding: '10px 12px', borderRadius: '12px', border: '1px solid var(--line)', background: 'var(--surface)', color: 'var(--ink)', fontSize: '.96rem' }
      }, searchInputHandlers('zh-dict-inp', (v) => { DICT_Q = v; }, dictView))),
      DICT_Q ? h('button', { type: 'button', class: 'ghost mini', onclick: () => { DICT_Q = ''; dictView(); } }, '✕') : null
    ),
    h('div', { class: 'row wrap', style: { gap: '6px', alignItems: 'center', justifyContent: 'space-between' } },
      h('div', { class: 'row wrap', style: { gap: '6px' } },
        [['all', 'Tất cả'], ['vocab', 'Từ vựng HSK'], ['chiet_tu', 'Chiết tự'], ['char', 'Chữ Hán']].map(([k, lbl]) => h('button', {
          type: 'button',
          class: 'mini ' + (DICT_FILTER === k ? 'primary' : 'ghost'),
          onclick: () => { DICT_FILTER = k; dictView(); }
        }, lbl))
      ),
      h('span', { class: 'small muted' }, totalMatches + ' mục' + (totalMatches > shown.length ? ' (hiện ' + shown.length + ')' : ''))
    ),
    shown.length ? h('div', { class: 'stack', style: { gap: '8px' } }, cards) : h('p', { class: 'small muted center', style: { padding: '16px 0' } }, 'Không tìm thấy trong kho offline.'),
    extBox
  ));
}

function openFlashcardPractice() {
  if (document.getElementById('flashcard-overlay')) return;
  const d = DATA.zh;
  const pool = [];
  if (d && d.topics) {
    const learnedTopics = d.topics.filter((t) => t.lessons && t.lessons.some((_, i) => lessonDone(t, i)));
    const srcTopics = learnedTopics.length ? learnedTopics : d.topics.slice(0, 6);
    srcTopics.forEach((t) => {
      const lv = String(t.category || 'hsk1').toUpperCase().replace('HSK', 'HSK ');
      (t.vocab || []).forEach((v) => {
        if (v && v.w && v.m) {
          pool.push({
            lv,
            cls: String(t.category || 'hsk1').toLowerCase(),
            zh: plain(v.w),
            py: v.r || '',
            vi: v.m,
            ex: v.ex ? plain(v.ex) : '',
            exr: v.exr || '',
            exm: v.exm || ''
          });
        }
      });
    });
  }
  const CARDS = pool.length ? shuffle(pool).slice(0, 12) : [
    { lv: 'HSK 1', cls: 'hsk1', zh: '你好', py: 'nǐ hǎo', vi: 'xin chào', ex: '你好，很高兴认识你。', exr: 'Nǐ hǎo, hěn gāoxìng rènshi nǐ.', exm: 'Xin chào, rất vui được làm quen với bạn.' },
    { lv: 'HSK 1', cls: 'hsk1', zh: '谢谢', py: 'xièxie', vi: 'cảm ơn', ex: '谢谢你的帮助！', exr: 'Xièxie nǐ de bāngzhù!', exm: 'Cảm ơn sự giúp đỡ của bạn!' },
    { lv: 'HSK 2', cls: 'hsk2', zh: '准备', py: 'zhǔnbèi', vi: 'chuẩn bị', ex: '我已经准备好了。', exr: 'Wǒ yǐjīng zhǔnbèi hǎo le.', exm: 'Tôi đã chuẩn bị xong rồi.' }
  ];
  let idx = 0;
  let flipped = false;

  const overlay = h('div', {
    id: 'flashcard-overlay',
    style: {
      position: 'fixed', inset: '0', zIndex: '9999',
      background: 'rgba(15, 23, 42, 0.65)', backdropFilter: 'blur(4px)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '16px'
    }
  });
  const wrap = h('div', {
    class: 'panel stack',
    style: { width: '100%', maxWidth: '400px', padding: '18px', gap: '14px', borderRadius: '18px' }
  });
  overlay.appendChild(wrap);

  function render() {
    wrap.innerHTML = '';
    const c = CARDS[idx];
    wrap.appendChild(h('div', { class: 'row between', style: { alignItems: 'center' } },
      h('span', { style: { fontWeight: 700, fontSize: '1.02rem' } }, `🃏 Flashcard 3D (${idx + 1}/${CARDS.length})`),
      h('button', { class: 'ghost mini', onclick: () => overlay.remove() }, '✕')
    ));

    const inner = h('div', {
      style: {
        position: 'relative', width: '100%', height: '220px',
        transformStyle: 'preserve-3d', transition: 'transform 0.5s cubic-bezier(.2,.8,.2,1)',
        transform: flipped ? 'rotateY(180deg)' : 'rotateY(0deg)',
        cursor: 'pointer'
      },
      onclick: () => { flipped = !flipped; render(); }
    });

    const faceStyle = {
      position: 'absolute', inset: '0', backfaceVisibility: 'hidden',
      background: '#ffffff', color: '#0f172a', borderRadius: '16px',
      border: '1px solid #e2e8f0', boxShadow: '0 10px 28px rgba(15, 23, 42, 0.14)',
      padding: '16px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between'
    };

    const front = h('div', { style: faceStyle },
      h('div', { class: 'row between', style: { alignItems: 'center' } },
        h('span', { class: 'chip level ' + c.cls }, c.lv),
        h('div', { onclick: (e) => e.stopPropagation() }, spk('zh', c.zh))
      ),
      h('div', { class: 'stack center', style: { gap: '6px', textAlign: 'center' } },
        h('div', { lang: 'zh-Hans', style: { fontSize: '2.1rem', fontWeight: 800, color: '#0f172a' } }, c.zh),
        c.py ? h('div', { style: { fontSize: '.98rem', color: '#0f766e', fontWeight: 600 } }, c.py) : null
      ),
      h('div', { style: { textAlign: 'center', fontSize: '.75rem', color: '#94a3b8' } }, '👆 Chạm vào thẻ để lật')
    );

    const back = h('div', { style: Object.assign({}, faceStyle, { transform: 'rotateY(180deg)', background: '#f8fafc' }) },
      h('div', { class: 'row between', style: { alignItems: 'center' } },
        h('span', { style: { fontSize: '.75rem', fontWeight: 700, color: '#64748b' } }, 'NGHĨA TIẾNG VIỆT'),
        c.ex ? h('div', { onclick: (e) => e.stopPropagation() }, spk('zh', c.ex)) : h('span')
      ),
      h('div', { class: 'stack center', style: { gap: '6px', textAlign: 'center' } },
        h('div', { style: { fontSize: '1.3rem', fontWeight: 800, color: '#0f766e' } }, c.vi),
        c.ex ? h('div', { lang: 'zh-Hans', style: { fontSize: '.92rem', color: '#1e293b', fontWeight: 600 } }, c.ex) : null,
        c.exr ? h('div', { style: { fontSize: '.78rem', color: '#64748b' } }, c.exr) : null,
        c.exm ? h('div', { style: { fontSize: '.8rem', color: '#475569' } }, c.exm) : null
      ),
      h('div', { style: { textAlign: 'center', fontSize: '.75rem', color: '#94a3b8' } }, '👆 Chạm để lật lại')
    );

    inner.appendChild(front);
    inner.appendChild(back);

    wrap.appendChild(h('div', { style: { perspective: '1000px', width: '100%', maxWidth: '340px', margin: '0 auto' } }, inner));

    wrap.appendChild(h('div', { class: 'row between', style: { gap: '8px' } },
      h('button', {
        class: 'ghost small',
        disabled: idx === 0,
        onclick: () => { if (idx > 0) { idx--; flipped = false; render(); } }
      }, '← Trước'),
      h('button', {
        class: 'ghost small',
        onclick: () => { flipped = !flipped; render(); }
      }, '🔄 Lật thẻ'),
      h('button', {
        class: 'btn small',
        onclick: () => {
          if (idx < CARDS.length - 1) { idx++; flipped = false; render(); }
          else overlay.remove();
        }
      }, idx < CARDS.length - 1 ? 'Tiếp →' : 'Xong ✓')
    ));
  }
  render();
  document.body.appendChild(overlay);
}

let ONBOARDING_SHOWN_SESSION = false;
function openOnboardingModal(force = false) {
  if (document.getElementById('onboarding-overlay')) return;
  const GOALS = [
    { id: 'comm', icon: '🚀', label: 'Giao tiếp hàng ngày', desc: 'Nghe nói phản xạ tự nhiên, du lịch & đời sống' },
    { id: 'work', icon: '💼', label: 'Công việc & Thương mại', desc: 'Đàm phán, đơn hàng, họp hành & email tiếng Trung' },
    { id: 'hsk', icon: '🎓', label: 'Luyện thi HSK / HSKK', desc: 'Chinh phục chứng chỉ HSK 1–9 & HSKK nói' },
    { id: 'foundation', icon: '🌱', label: 'Học từ nền tảng Pinyin', desc: 'Thanh điệu, bộ thủ, chiết tự & viết chữ Hán' }
  ];
  const TIMES = [10, 20, 30];
  const QUESTIONS = [
    {
      level: 'HSK 1', type: 'Từ vựng',
      q: '我 _____ 喝茶。(Wǒ _____ hē chá. — Tôi thích uống trà.)',
      opts: ['喜欢 (xǐhuan)', '知道 (zhīdào)', '准备 (zhǔnbèi)', '以为 (yǐwéi)'], ans: 0
    },
    {
      level: 'HSK 2', type: 'Nghe hiểu',
      audioText: '请问，洗手间在哪里？',
      q: 'Nghe câu hỏi và chọn ý nghĩa đúng:',
      opts: ['Xin hỏi nhà vệ sinh ở đâu?', 'Xin hỏi mấy giờ rồi?', 'Món này bao nhiêu tiền?', 'Bạn tên là gì?'], ans: 0
    },
    {
      level: 'HSK 3', type: 'Ngữ pháp',
      q: '他 _____ 汉语学得很好。',
      opts: ['把 (bǎ)', '被 (bèi)', '比 (bǐ)', '让 (ràng)'], ans: 0
    },
    {
      level: 'HSK 4', type: 'Nghe hiểu',
      audioText: '请把报价单发到我的邮箱。',
      q: 'Nghe câu nói và chọn hành động phù hợp:',
      opts: ['Gửi bảng báo giá vào email', 'Hủy đơn hàng ngay lập tức', 'Đặt lịch hẹn ngày mai', 'Kiểm tra lại địa chỉ kho'], ans: 0
    },
    {
      level: 'HSK 5', type: 'Từ vựng & Cấu trúc',
      q: '虽然工作很忙，_____ 他每天坚持学习中文。',
      opts: ['但是 (dànshì)', '因为 (yīnwèi)', '所以 (suǒyǐ)', '如果 (rúguǒ)'], ans: 0
    }
  ];

  const prev = S.onboarding || {};
  const st = {
    step: 1,
    name: S.name || prev.name || '',
    goalType: prev.goalType || 'comm',
    dailyMinutes: prev.dailyMinutes || S.goal || 20,
    qIdx: 0,
    answers: new Array(QUESTIONS.length).fill(-1),
    skipped: false,
    score: 0,
    level: 'hsk1'
  };

  const overlay = h('div', {
    id: 'onboarding-overlay',
    style: {
      position: 'fixed', inset: '0', zIndex: '9999',
      background: 'rgba(15, 23, 42, 0.65)', backdropFilter: 'blur(4px)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '16px'
    }
  });
  const card = h('div', {
    class: 'panel stack',
    style: {
      width: '100%', maxWidth: '520px', maxHeight: '90vh', overflowY: 'auto',
      padding: '20px', gap: '14px', borderRadius: '18px',
      boxShadow: '0 20px 50px rgba(0,0,0,0.3)'
    }
  });
  overlay.appendChild(card);

  function closeModal() { overlay.remove(); }

  function computeResult(skipped) {
    st.skipped = skipped;
    if (skipped) {
      st.score = 0;
      st.level = 'hsk1';
    } else {
      let sc = 0;
      QUESTIONS.forEach((q, i) => { if (st.answers[i] === q.ans) sc++; });
      st.score = sc;
      st.level = sc >= 5 ? 'hsk5' : sc >= 4 ? 'hsk4' : sc >= 3 ? 'hsk3' : sc >= 2 ? 'hsk2' : 'hsk1';
    }
    st.step = 3;
    renderStep();
  }

  function finishAndApply() {
    if (st.name.trim()) S.name = st.name.trim();
    S.goal = st.dailyMinutes;
    S.zhCat = 'all';
    const startSec = st.level || 'hsk1';
    openPhases.add('zh:sec:' + startSec);
    openPhases.add('zh:unit:' + startSec + ':u1');
    S.onboarding = {
      done: true,
      name: S.name,
      goalType: st.goalType,
      dailyMinutes: st.dailyMinutes,
      level: st.level,
      score: st.score,
      total: QUESTIONS.length,
      skipped: st.skipped,
      ts: Date.now()
    };
    save();
    closeModal();
    homeView();
  }

  function renderStep() {
    card.innerHTML = '';
    const header = h('div', { class: 'row between', style: { alignItems: 'center' } },
      h('div', { class: 'row', style: { gap: '8px', alignItems: 'center' } },
        h('span', { class: 'chip', style: { fontWeight: 700 } }, `Bước ${st.step}/3`),
        h('span', { class: 'small muted' },
          st.step === 1 ? 'Thông tin & Mục tiêu' :
          st.step === 2 ? 'Kiểm tra trình độ HSK' : 'Lộ trình gợi ý'
        )
      ),
      h('button', { class: 'ghost mini', onclick: closeModal, 'aria-label': 'Đóng' }, '✕')
    );
    card.appendChild(header);

    if (st.step === 1) {
      const nameInput = h('input', {
        type: 'text', placeholder: 'Nhập tên của bạn...', value: st.name,
        oninput: (e) => { st.name = e.target.value; }
      });
      card.appendChild(h('h2', { style: { margin: 0, fontSize: '1.22rem' } }, 'Chào mừng đến với Lingogo Chinese 🇨🇳'));
      card.appendChild(h('div', { class: 'stack', style: { gap: '6px' } },
        h('label', { class: 'small', style: { fontWeight: 600 } }, 'Tên gọi của bạn'),
        nameInput
      ));
      card.appendChild(h('div', { class: 'stack', style: { gap: '8px' } },
        h('label', { class: 'small', style: { fontWeight: 600 } }, 'Mục tiêu học Tiếng Trung'),
        h('div', { class: 'stack', style: { gap: '6px' } },
          GOALS.map((g) => h('button', {
            class: st.goalType === g.id ? 'panel' : 'ghost',
            style: {
              textAlign: 'left', padding: '10px 12px', borderRadius: '12px',
              border: st.goalType === g.id ? '2px solid var(--teal)' : '1px solid var(--line)',
              background: st.goalType === g.id ? 'rgba(15,82,87,0.08)' : 'var(--surface)'
            },
            onclick: () => { st.goalType = g.id; renderStep(); }
          },
            h('div', { class: 'row', style: { gap: '8px', alignItems: 'center' } },
              h('span', { style: { fontSize: '1.15rem' } }, g.icon),
              h('div', { class: 'stack', style: { gap: '2px' } },
                h('b', { style: { fontSize: '.92rem' } }, g.label),
                h('span', { class: 'small muted', style: { fontSize: '.76rem' } }, g.desc)
              )
            )
          ))
        )
      ));
      card.appendChild(h('div', { class: 'stack', style: { gap: '6px' } },
        h('label', { class: 'small', style: { fontWeight: 600 } }, 'Thời gian học mỗi ngày'),
        h('div', { class: 'row', style: { gap: '8px' } },
          TIMES.map((m) => h('button', {
            class: st.dailyMinutes === m ? 'btn small' : 'ghost small',
            style: { flex: 1 },
            onclick: () => { st.dailyMinutes = m; renderStep(); }
          }, `${m} phút/ngày`))
        )
      ));
      card.appendChild(h('button', {
        class: 'btn block',
        style: { marginTop: '4px' },
        onclick: () => { st.step = 2; renderStep(); }
      }, 'Tiếp tục: Kiểm tra trình độ →'));
      return;
    }

    if (st.step === 2) {
      const q = QUESTIONS[st.qIdx];
      card.appendChild(h('div', { class: 'row between', style: { alignItems: 'center' } },
        h('span', { class: 'chip level ' + q.level.toLowerCase().replace(/\\s+/g, '') }, `${q.level} · ${q.type}`),
        h('span', { class: 'small muted' }, `Câu ${st.qIdx + 1} / ${QUESTIONS.length}`)
      ));
      if (q.audioText) {
        card.appendChild(h('div', { class: 'row', style: { gap: '8px', alignItems: 'center' } },
          h('button', { class: 'btn small', onclick: () => say('zh', q.audioText) }, '🔊 Nghe câu mẫu'),
          h('span', { class: 'small muted' }, 'Bấm để nghe phát âm tiếng Trung')
        ));
      }
      card.appendChild(h('p', { style: { fontWeight: 600, fontSize: '1rem', margin: '4px 0', lineHeight: 1.5 } }, q.q));
      card.appendChild(h('div', { class: 'stack', style: { gap: '8px' } },
        q.opts.map((opt, idx) => {
          const picked = st.answers[st.qIdx] === idx;
          return h('button', {
            class: picked ? 'panel' : 'ghost',
            style: {
              textAlign: 'left', padding: '10px 12px', borderRadius: '10px',
              border: picked ? '2px solid var(--teal)' : '1px solid var(--line)',
              background: picked ? 'rgba(15,82,87,0.08)' : 'var(--surface)'
            },
            onclick: () => {
              st.answers[st.qIdx] = idx;
              if (st.qIdx < QUESTIONS.length - 1) { st.qIdx++; renderStep(); }
              else { computeResult(false); }
            }
          }, `${String.fromCharCode(65 + idx)}. ${opt}`);
        })
      ));
      card.appendChild(h('div', { class: 'row between', style: { marginTop: '8px', gap: '8px' } },
        h('button', {
          class: 'ghost small',
          onclick: () => {
            if (st.qIdx > 0) { st.qIdx--; renderStep(); }
            else { st.step = 1; renderStep(); }
          }
        }, '← Quay lại'),
        h('button', {
          class: 'ghost small',
          style: { color: 'var(--muted)' },
          onclick: () => computeResult(true)
        }, 'Bỏ qua, bắt đầu từ HSK 1')
      ));
      return;
    }

    const lvUp = st.level.toUpperCase().replace('HSK', 'HSK ');
    card.appendChild(h('div', { class: 'stack center', style: { textAlign: 'center', gap: '8px', padding: '8px 0' } },
      h('div', { style: { fontSize: '2.2rem' } }, '🎯'),
      h('h2', { style: { margin: 0 } }, `Trình độ gợi ý: ${lvUp}`),
      st.skipped
        ? h('p', { class: 'muted small' }, 'Bạn đã chọn bắt đầu từ nền tảng HSK 1 (Pinyin & Bộ thủ).')
        : h('p', { class: 'muted small' }, `Bạn trả lời đúng ${st.score}/${QUESTIONS.length} câu. Lộ trình ưu tiên mở từ ${lvUp}.`)
    ));
    card.appendChild(h('button', { class: 'btn block', onclick: finishAndApply }, `Vào học ${lvUp} ngay →`));
  }
  renderStep();
  document.body.appendChild(overlay);
}

function practiceTabView() {
  ACTIVE_STUDY_MODE = false;
  const groups = [
    {
      iconEl: '🎧',
      title: 'Nghe, Nói & Viết chữ Hán',
      subtitle: 'Luyện nghe chủ đề, nói phản xạ Pinyin, tập viết Hán tự theo nét & đọc hiểu',
      chip: '4 kỹ năng',
      defaultOpen: true,
      items: [
        { icon: '🎧', title: 'Luyện Nghe theo chủ đề', desc: 'Nghe từ vựng & mẫu câu giọng chuẩn bản xứ HSK 1–9.', badge: 'Nghe', fn: () => { SKILL_TAB = 'listen'; go('skills'); } },
        { icon: '🎙️', title: 'Luyện Nói & Phản xạ Pinyin', desc: 'Luyện phát âm thanh điệu, hội thoại giao tiếp & chấm điểm giọng nói.', badge: 'Nói', fn: () => { SKILL_TAB = 'speak'; go('skills'); } },
        { icon: '✍️', title: 'Tập viết chữ Hán (Nét & Bút thuận)', desc: 'Luyện viết từng nét Hán tự chuẩn thứ tự bút thuận kèm âm Hán Việt.', badge: 'Viết', fn: () => { SKILL_TAB = 'write'; go('skills'); } },
        { icon: '💬', title: 'Hội thoại & Đọc hiểu thực tế', desc: 'Luyện đọc hiểu tình huống đời sống, thương mại và làm bài tập kiểm tra.', badge: 'Đọc', fn: () => { KNOWLEDGE_TAB = 'read301'; go('knowledge'); } }
      ]
    },
    {
      iconEl: '📘',
      title: 'Ngữ pháp, Chiết tự & Bộ thủ',
      subtitle: 'Hệ thống ngữ pháp HSK 1–9, 133+ bài chiết tự nhớ nhanh và 214 bộ thủ Khang Hy',
      chip: '3 chuyên đề',
      defaultOpen: false,
      items: [
        { icon: '📖', title: 'Ngữ pháp HSK (Cấp 1–9)', desc: 'Cấu trúc câu, mẫu câu ví dụ có Pinyin và quiz kiểm tra từng chủ điểm.', badge: 'Ngữ pháp', fn: () => { KNOWLEDGE_TAB = 'gram'; go('knowledge'); } },
        { icon: '🧩', title: 'Chiết tự & Mẹo nhớ chữ Hán', desc: 'Phân tích cấu tạo chữ, câu chuyện chiết tự giúp nhớ chữ lâu.', badge: 'Chiết tự', fn: () => { KNOWLEDGE_TAB = 'chiet_tu'; go('knowledge'); } },
        { icon: '🈴', title: '214 Bộ thủ & Quy tắc Bút thuận', desc: 'Tra cứu 214 bộ thủ Khang Hy và 7 quy tắc viết chữ Hán căn bản.', badge: 'Bộ thủ', fn: () => { KNOWLEDGE_TAB = 'chars'; go('knowledge'); } }
      ]
    },
    {
      iconEl: '🎮',
      title: 'Trò chơi & Phản xạ từ vựng',
      subtitle: 'Ghép cặp Chữ Hán với nghĩa Tiếng Việt giúp tăng phản xạ mặt chữ',
      chip: 'Mini-game',
      defaultOpen: false,
      items: [
        { icon: '🎮', title: 'Trò chơi · Ghép cặp Chữ Hán – Nghĩa', desc: 'Phản xạ nhanh ghép chữ Hán đã học với nghĩa tiếng Việt.', badge: 'Chơi ngay', fn: () => go('games') }
      ]
    }
  ];

  const wrap = h('div', { class: 'stack-lg', style: { gap: '12px' } },
    h('div', { class: 'row between', style: { alignItems: 'center' } },
      h('h1', { style: { margin: 0 } }, 'Luyện tập'),
      h('div', { class: 'row', style: { gap: '6px', alignItems: 'center' } },
        feedbackBtn({ mode: 'practice' }),
        langSwitch()
      )
    ),
    h('div', { class: 'acc-toolbar' },
      h('span', { class: 'small muted', style: { fontWeight: 600 } }, '🎯 Chọn nhóm kỹ năng cần rèn luyện'),
      makeToggleAllBtn(() => wrap, 'details.practice-acc')
    ),
    ...groups.map((grp) => accordionItem({
      cls: 'acc-card practice-acc',
      iconEl: grp.iconEl,
      title: grp.title,
      subtitle: grp.subtitle,
      defaultOpen: grp.defaultOpen,
      chips: [h('span', { class: 'chip small' }, grp.chip)],
      body: grp.items.map((it) => h('button', {
        class: 'lesson',
        style: { marginTop: '6px' },
        onclick: it.fn
      },
        h('span', { style: { fontSize: '1.25rem', flexShrink: 0 } }, it.icon),
        h('div', { class: 'meta' },
          h('b', { style: { display: 'block', fontSize: '.94rem' } }, it.title),
          h('span', { class: 'small muted' }, it.desc)
        ),
        h('span', { class: 'chip small' }, it.badge)
      ))
    }))
  );
  mount(wrap);
}

function gamesTabView() {
  ACTIVE_STUDY_MODE = true;
  const d = DATA.zh;
  const pool = [];
  if (d && d.topics) {
    const learnedTopics = d.topics.filter((t) => t.lessons && t.lessons.some((_, i) => lessonDone(t, i)));
    const src = learnedTopics.length ? learnedTopics : d.topics.slice(0, 5);
    src.forEach((t) => (t.vocab || []).forEach((v) => {
      if (v && v.w && v.m && plain(v.w).length <= 4) pool.push({ zh: plain(v.w), py: v.r || '', vi: v.m });
    }));
  }
  const PAIRS = pool.length >= 6
    ? shuffle(pool).slice(0, 6)
    : [
        { zh: '你好', py: 'nǐ hǎo', vi: 'xin chào' },
        { zh: '谢谢', py: 'xièxie', vi: 'cảm ơn' },
        { zh: '朋友', py: 'péngyou', vi: 'bạn bè' },
        { zh: '学习', py: 'xuéxí', vi: 'học tập' },
        { zh: '工作', py: 'gōngzuò', vi: 'công việc' },
        { zh: '时间', py: 'shíjiān', vi: 'thời gian' }
      ];
  let selZh = null, selVi = null;
  const matched = new Set();
  const viList = [...PAIRS].sort((a, b) => a.vi.localeCompare(b.vi));

  function renderGame() {
    mount(h('div', { class: 'stack', style: { gap: '12px' } },
      h('div', { class: 'row between', style: { alignItems: 'center' } },
        h('button', { class: 'ghost mini', onclick: () => go('practice') }, '← Luyện tập'),
        h('button', { class: 'ghost mini', onclick: () => { matched.clear(); selZh = null; selVi = null; renderGame(); } }, 'Chơi lại')
      ),
      h('div', { class: 'panel stack', style: { padding: '14px', gap: '2px' } },
        h('h2', { style: { margin: 0, fontSize: '1.2rem' } }, '🎮 Trò chơi · Ghép cặp Chữ Hán – Nghĩa'),
        h('p', { class: 'small muted', style: { margin: 0 } }, `Đã ghép: ${matched.size}/${PAIRS.length} cặp`)
      ),
      matched.size === PAIRS.length
        ? h('div', { class: 'panel stack center', style: { padding: '20px', gap: '8px', background: 'rgba(16,185,129,0.1)' } },
            h('div', { style: { fontSize: '1.5rem' } }, '🎉'),
            h('div', { style: { fontWeight: 700 } }, 'Tuyệt vời! Bạn đã ghép đúng toàn bộ!'),
            h('button', { class: 'btn small', onclick: () => gamesTabView() }, 'Chơi ván mới')
          )
        : h('div', { style: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' } },
            h('div', { class: 'stack', style: { gap: '8px' } },
              PAIRS.map((p) => {
                const done = matched.has(p.zh);
                const active = selZh === p.zh;
                return h('button', {
                  class: active ? 'btn' : 'ghost',
                  disabled: done,
                  style: { opacity: done ? 0.35 : 1, fontWeight: 700, display: 'flex', flexDirection: 'column', gap: '2px', padding: '10px' },
                  onclick: () => {
                    selZh = p.zh;
                    say('zh', p.zh);
                    if (selVi) {
                      const found = PAIRS.find((x) => x.zh === selZh && x.vi === selVi);
                      if (found) matched.add(found.zh);
                      selZh = null; selVi = null;
                    }
                    renderGame();
                  }
                }, h('span', { lang: 'zh-Hans', style: { fontSize: '1.15rem' } }, p.zh), p.py ? h('span', { class: 'small muted', style: { fontWeight: 400 } }, p.py) : null);
              })
            ),
            h('div', { class: 'stack', style: { gap: '8px' } },
              viList.map((p) => {
                const done = matched.has(p.zh);
                const active = selVi === p.vi;
                return h('button', {
                  class: active ? 'btn' : 'ghost',
                  disabled: done,
                  style: { opacity: done ? 0.35 : 1, padding: '10px' },
                  onclick: () => {
                    selVi = p.vi;
                    if (selZh) {
                      const found = PAIRS.find((x) => x.zh === selZh && x.vi === selVi);
                      if (found) matched.add(found.zh);
                      selZh = null; selVi = null;
                    }
                    renderGame();
                  }
                }, p.vi);
              })
            )
          )
    ));
  }
  renderGame();
}
"""


NEW_HOME_VIEW = """function homeView(opts = {}) {
  ACTIVE_STUDY_MODE = false;
  const _keepY = opts && opts.preserveScroll ? window.scrollY : null;
  const d = DATA[S.lang], st = streak(), xp = xpOf(todayN(), S.lang), due = dueIn(S.lang);
  const langCats = CATEGORIES[S.lang];
  if (!S.zhCatAllDefault || S.zhSecMigrated !== 1) { S.zhCat = 'all'; S.zhCatAllDefault = 1; S.zhSecMigrated = 1; save(); }
  if (!S.zhCat || S.zhCat === 'basic') S.zhCat = 'all';
  else if (S.zhCat === 'comm') S.zhCat = 'hsk2';
  else if (S.zhCat === 'business') S.zhCat = 'hsk4';
  else if (S.zhCat === 'advanced') S.zhCat = 'hsk5';
  const curCat = langCats ? (S.zhCat || 'all') : 'all';
  const gf = h('i'); requestAnimationFrame(() => { gf.style.width = Math.min(100, Math.round((xp / goal()) * 100)) + '%'; });

  const allSections = buildCurriculumSections(S.lang, d);
  const totalUnitsCount = allSections.reduce((sum, s) => sum + s.units.length, 0);
  const curSecObj = curCat !== 'all' ? (allSections.find((s) => s.id === curCat) || null) : null;
  const visibleSections = curSecObj ? [curSecObj] : allSections;
  const visibleUnitsCount = visibleSections.reduce((sum, s) => sum + s.units.length, 0);
  const filteredTopics = curSecObj ? curSecObj.topics : d.topics;

  const findNextIn = (list) => {
    for (const t of list) for (let i = 0; i < t.lessons.length; i++) if (!lessonDone(t, i)) return { t, i };
    return null;
  };
  const nx = findNextIn(filteredTopics) || nextLesson(d, 'all');

  const curCatObj = langCats ? (langCats.find((c) => c.id === curCat) || langCats[0]) : null;
  const catBar = h('div', { class: 'subjects-box stack', style: { gap: '8px', margin: '4px 0' } },
    h('button', {
      class: 'subjects-trigger' + (subjectsOpen ? ' open' : ''),
      'aria-expanded': String(subjectsOpen),
      'aria-haspopup': 'listbox',
      onclick: (e) => {
        e.stopPropagation();
        subjectsOpen = !subjectsOpen;
        homeView({ preserveScroll: true });
      }
    },
      h('div', { class: 'row', style: { gap: '8px', alignItems: 'center', flex: 1, minWidth: 0, overflow: 'hidden' } },
        h('span', { class: 'subjects-name' }, curSecObj ? (`${curSecObj.icon} S${curSecObj.num} · ${curSecObj.name}`) : '📚 Tất cả'),
        curSecObj
          ? h('span', { class: 'chip level ' + curSecObj.level.toLowerCase().replace(/\\s+/g, '') }, curSecObj.level)
          : h('span', { class: 'chip good', style: { fontWeight: 700 } }, `${allSections.length} Section`)
      ),
      h('div', { class: 'row', style: { gap: '8px', alignItems: 'center', flex: 'none' } },
        h('span', { class: 'small muted' }, `${visibleUnitsCount} Unit · ${filteredTopics.length} bài`),
        h('span', { class: 'subjects-arrow' }, subjectsOpen ? '▲' : '▼')
      )
    ),
    subjectsOpen && h('div', { class: 'subjects-dropdown stack', role: 'listbox' },
      (() => {
        const isSel = !curSecObj;
        return h('button', {
          class: 'subjects-item' + (isSel ? ' selected' : ''),
          role: 'option',
          'aria-selected': String(isSel),
          onclick: (e) => {
            e.stopPropagation();
            S.zhCat = 'all';
            subjectsOpen = false;
            save();
            homeView();
          }
        },
          h('div', { class: 'row between', style: { alignItems: 'center', width: '100%' } },
            h('div', { class: 'row', style: { gap: '8px', alignItems: 'center' } },
              h('span', { style: { fontSize: '1.15rem', lineHeight: 1 } }, '📚'),
              h('b', { style: { fontSize: '.95rem' } }, 'Tất cả Section (HSK 1–9)'),
              h('span', { class: 'chip good' }, `${allSections.length} Section`)
            ),
            h('div', { class: 'row', style: { gap: '8px', alignItems: 'center' } },
              h('span', { class: 'small muted' }, `${totalUnitsCount} Unit · ${d.topics.length} bài`),
              isSel && h('span', { class: 'subjects-check' }, '✓')
            )
          ),
          h('p', { class: 'small muted', style: { margin: '4px 0 0 28px', textAlign: 'left', lineHeight: 1.35 } }, `Mỗi Section là 1 cấp độ (${allSections.map((s) => s.level).join(' → ')}), tổng ${totalUnitsCount} Unit & ${d.topics.length} chủ đề`)
        );
      })(),
      ...allSections.map((sec) => {
        const isSel = curSecObj && curSecObj.id === sec.id;
        const doneS = sec.topics.filter((t) => topicDone(t)).length;
        const unitListText = sec.units.map((u) => `Unit ${u.num}: ${u.name}`).join(' · ');
        return h('button', {
          class: 'subjects-item' + (isSel ? ' selected' : ''),
          role: 'option',
          'aria-selected': String(isSel),
          onclick: (e) => {
            e.stopPropagation();
            S.zhCat = sec.id;
            subjectsOpen = false;
            save();
            homeView();
          }
        },
          h('div', { class: 'row between', style: { alignItems: 'center', width: '100%', gap: '8px' } },
            h('div', { class: 'row', style: { gap: '8px', alignItems: 'center', minWidth: 0, flex: 1 } },
              h('span', { style: { fontSize: '1.15rem', lineHeight: 1 } }, sec.icon),
              h('b', { style: { fontSize: '.93rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' } }, `Section ${sec.num} · ${sec.name}`),
              h('span', { class: 'chip level ' + sec.level.toLowerCase().replace(/\\s+/g, '') }, sec.level)
            ),
            h('div', { class: 'row', style: { gap: '8px', alignItems: 'center', flex: 'none' } },
              h('span', { class: 'small muted' }, `${sec.units.length} Unit · ${doneS}/${sec.topics.length}`),
              isSel && h('span', { class: 'subjects-check' }, '✓')
            )
          ),
          h('p', { class: 'small muted', style: { margin: '4px 0 0 28px', textAlign: 'left', lineHeight: 1.35 } }, unitListText)
        );
      })
    ),
    h('select', {
      'aria-label': 'Chọn nhanh chủ đề theo Section và Unit',
      style: { minHeight: '42px', padding: '8px 12px', fontSize: '.88rem', borderRadius: '12px' },
      onchange: (e) => {
        const tid = e.target.value;
        if (!tid) return;
        let foundSec = null, foundUnit = null, target = null;
        for (const s of visibleSections) {
          for (const u of s.units) {
            const hit = u.topics.find((t) => String(t.id) === String(tid));
            if (hit) { foundSec = s; foundUnit = u; target = hit; break; }
          }
          if (target) break;
        }
        if (!target) return;
        if (foundSec) {
          const sKey = S.lang + ':sec:' + foundSec.id;
          openPhases.add(sKey);
          closedPhases.delete(sKey);
        }
        if (foundUnit) {
          const uKey = S.lang + ':unit:' + foundUnit.id;
          openPhases.add(uKey);
          closedPhases.delete(uKey);
        }
        openTopics.clear();
        openTopics.add(target.lang + ':' + target.id);
        homeView();
        requestAnimationFrame(() => {
          const el = document.getElementById('duo-step-' + target.id);
          if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        });
      }
    },
      h('option', { value: '' }, `📌 Chọn nhanh chủ đề (${filteredTopics.length} chủ đề)...`),
      ...visibleSections.flatMap((sec) => sec.units.map((u) => h('optgroup', {
        label: `Section ${sec.num} (${sec.level}) · Unit ${u.num}: ${u.name}`
      },
        ...u.topics.map((t) => {
          const dnCnt = t.lessons.filter((_, i) => lessonDone(t, i)).length;
          const lbl = `${t.pos}. ${t.sub || t.title} (${dnCnt}/${t.lessons.length})`;
          return h('option', { value: String(t.id), selected: openTopics.has(t.lang + ':' + t.id) }, lbl);
        })
      )))
    )
  );

  const ob = S.onboarding;
  const g = goal(S.lang, todayN());
  const sch = getDaySchedule(todayN());
  const isFocus = sch.focus === S.lang;
  const doneRev = getReviewedToday(S.lang, todayN());
  const rawVault = rawDueIn(S.lang);
  const p = getLangProgress(S.lang);
  const estAll = calcFinishEstimate(p.remainingTopics, p.remainingLessons, STUDY_PACE, S.lang);
  const goalNames = { comm: 'Giao tiếp hàng ngày', work: 'Công việc & Thương mại', hsk: 'Luyện thi HSK / HSKK', foundation: 'Học từ nền tảng' };

  const todayCard = h('div', { class: 'panel stack', style: { gap: '10px' } },
    h('div', { class: 'row between small', style: { alignItems: 'center', gap: '6px' } },
      h('span', {},
        isFocus
          ? h('span', { class: 'chip accent', style: { fontSize: '.72rem', marginRight: '6px' } }, '🎯 Trọng tâm')
          : sch.focus === 'all'
          ? h('span', { class: 'chip good', style: { fontSize: '.72rem', marginRight: '6px' } }, '🧘 Chủ Nhật')
          : h('span', { class: 'chip', style: { fontSize: '.72rem', marginRight: '6px' } }, '⚡ Duy trì'),
        h('span', { style: { fontWeight: 600 } }, xp >= g ? 'Đã đạt mục tiêu hôm nay' : 'Học hôm nay')
      ),
      h('span', { class: 'muted', style: { fontWeight: 600 } }, xp + '/' + g + ' phút')
    ),
    h('div', { class: 'bar', role: 'progressbar', 'aria-label': 'Mục tiêu hôm nay', 'aria-valuenow': xp, 'aria-valuemax': g }, gf),
    h('div', { class: 'stats' },
      h('div', { class: 'stat' }, h('b', {}, st), h('span', {}, 'ngày liên tục')),
      h('div', { class: 'stat' }, h('b', {}, xp + 'p'), h('span', {}, 'phút hôm nay')),
      h('div', { class: 'stat' }, h('b', {}, due), h('span', {}, 'từ cần ôn'))
    ),
    nx ? h('button', { class: 'primary block', onclick: () => lessonView(nx.t, nx.i) },
      h('span', {}, '▶ Học tiếp: ', h('b', {}, nx.t.sub || nx.t.title)))
      : h('p', { class: 'muted center small' }, curSecObj ? (`Bạn đã học hết Section ${curSecObj.num} (${curSecObj.level}).`) : 'Bạn đã học hết lộ trình.'),
    due > 0 ? h('button', {
      class: 'accent block',
      onclick: () => { REVIEW_SKILL = 'vocab'; go('review'); }
    }, '🔄 Ôn tập ngay: Còn ' + due + ' từ' + (doneRev > 0 ? ' (đã ôn ' + doneRev + ')' : ''))
      : (doneRev > 0 || rawVault > 0 ? h('button', {
          class: 'ghost mini block',
          style: { color: 'var(--muted)' },
          onclick: () => { REVIEW_SKILL = 'vocab'; go('review'); }
        }, doneRev > 0 ? ('✓ Đã ôn ' + doneRev + ' từ hôm nay · Vào kho từ vựng') : ('📦 Kho chờ ' + rawVault + ' từ · Vào kho từ vựng')) : null)
  );

  const catExamCard = (() => {
    if (curCat === 'all' || !filteredTopics.length) return null;
    const catDoneTopics = filteredTopics.filter((t) => topicDone(t)).length;
    const lvLabel = curCatObj.level || curCatObj.short;
    const allDone = catDoneTopics >= filteredTopics.length;
    return h('div', {
      class: 'panel row between',
      style: {
        padding: '10px 14px',
        background: allDone ? 'rgba(35,120,74,.08)' : 'rgba(180,83,9,.06)',
        border: allDone ? '1px solid rgba(35,120,74,.32)' : '1px solid rgba(180,83,9,.28)',
        borderRadius: '12px',
        alignItems: 'center',
        gap: '10px',
        flexWrap: 'wrap'
      }
    },
      h('div', { style: { flex: '1 1 200px', minWidth: 0 } },
        h('div', { style: { fontSize: '.88rem', fontWeight: 700, color: allDone ? 'var(--good)' : 'var(--amber)' } },
          (allDone ? '🏆 Đã vượt cấp ' : '🚀 Kiểm tra vượt cấp ') + lvLabel + ' (' + catDoneTopics + '/' + filteredTopics.length + ' bài)'
        ),
        h('div', { class: 'small muted', style: { fontSize: '.76rem', marginTop: '2px' } },
          allDone
            ? ('Bạn đã hoàn thành 100% chuyên đề ' + lvLabel + '. Có thể làm lại đề thi xáo trộn bất cứ lúc nào.')
            : ('Đạt ≥ 80% để pass & hoàn thành 100% chuyên đề ' + curCatObj.name)
        )
      ),
      h('button', {
        class: (allDone ? 'primary' : 'accent') + ' mini',
        style: { whiteSpace: 'nowrap', padding: '7px 12px', fontSize: '.82rem', fontWeight: 700, flexShrink: 0 },
        onclick: () => startCategoryExam(S.lang, curCatObj, filteredTopics)
      }, allDone ? ('Làm lại đề ' + lvLabel) : 'Thi vượt cấp →')
    );
  })();

  const topicsNode = (() => {
    const unitPalettes = [
      { bg: '#58cc02', lip: '#46a302', soft: 'rgba(88, 204, 2, .11)' },
      { bg: '#1cb0f6', lip: '#148ec9', soft: 'rgba(28, 176, 246, .11)' },
      { bg: '#a855f7', lip: '#7e22ce', soft: 'rgba(168, 85, 247, .11)' },
      { bg: '#f97316', lip: '#c2410c', soft: 'rgba(249, 115, 22, .11)' },
      { bg: '#0f766e', lip: '#0b524d', soft: 'rgba(15, 118, 110, .11)' }
    ];
    const renderUnit = (u, uIdx, secHasNx, unitListLen) => {
      const uKey = S.lang + ':unit:' + u.id;
      const doneTopics = u.topics.filter((t) => t.lessons.every((_, i) => lessonDone(t, i))).length;
      const hasNx = !!(nx && u.topics.includes(nx.t));
      const isComplete = doneTopics === u.topics.length && u.topics.length > 0;
      const defOpen = hasNx || (!secHasNx && uIdx === 0) || unitListLen <= 1;
      const isOpen = openPhases.has(uKey) || (defOpen && !closedPhases.has(uKey));
      const pal = hasNx ? unitPalettes[0] : (isComplete ? { bg: '#eab308', lip: '#b45309', soft: 'rgba(234, 179, 8, .12)' } : unitPalettes[(u.num - 1) % unitPalettes.length]);

      const attrs = {
        class: 'duo-unit phase-acc',
        ontoggle: (e) => {
          if (e.target !== e.currentTarget) return;
          if (e.currentTarget.open) { openPhases.add(uKey); closedPhases.delete(uKey); }
          else { openPhases.delete(uKey); closedPhases.add(uKey); }
        }
      };
      if (isOpen) attrs.open = 'open';

      return h('details', attrs,
        h('summary', {
          class: 'duo-unit-hdr',
          style: { '--unit-col': pal.bg, '--unit-lip': pal.lip, '--unit-soft': pal.soft }
        },
          h('div', { class: 'duo-u-meta' },
            h('span', { class: 'duo-u-kicker' },
              `SECTION ${u.secNum}, UNIT ${u.num} · ${doneTopics}/${u.topics.length}`
            ),
            h('span', { class: 'duo-u-title' }, u.name)
          ),
          h('button', {
            type: 'button',
            class: 'duo-guidebook-btn',
            title: `Thi vượt cấp nhanh toàn bộ Unit ${u.num} (đạt ≥ 80% để hoàn thành)`,
            onclick: (e) => {
              e.preventDefault();
              e.stopPropagation();
              startCategoryExam(S.lang, {
                id: 'unit-' + u.id.replace(/[^a-z0-9_-]/gi, '-'),
                level: `Section ${u.secNum}, Unit ${u.num}`,
                short: `Unit ${u.num}`,
                name: u.name
              }, u.topics);
            }
          }, 'Test'),
          h('span', { class: 'acc-arrow', 'aria-hidden': 'true' }, '▾')
        ),
        h('div', { class: 'duo-path' },
          u.topics.map((t, ti) => topicCard(t, nx, t.pos, ti, { secNum: u.secNum, unitNum: u.num, secLevel: u.secLevel }))
        )
      );
    };

    const secThemes = [
      { col: '#58cc02', soft: 'rgba(88, 204, 2, .16)', border: 'rgba(88, 204, 2, .45)', lip: '#46a302', glow: 'rgba(88, 204, 2, .24)' },     // S1 HSK 1: Xanh lá
      { col: '#1cb0f6', soft: 'rgba(28, 176, 246, .14)', border: 'rgba(28, 176, 246, .4)', lip: '#148ec9', glow: 'rgba(28, 176, 246, .22)' }, // S2 HSK 2: Xanh dương
      { col: '#8b5cf6', soft: 'rgba(139, 92, 246, .14)', border: 'rgba(139, 92, 246, .4)', lip: '#6d28d9', glow: 'rgba(139, 92, 246, .22)' }, // S3 HSK 3: Tím
      { col: '#f97316', soft: 'rgba(249, 115, 22, .14)', border: 'rgba(249, 115, 22, .4)', lip: '#c2410c', glow: 'rgba(249, 115, 22, .22)' }, // S4 HSK 4: Cam
      { col: '#0d9488', soft: 'rgba(13, 148, 136, .14)', border: 'rgba(13, 148, 136, .4)', lip: '#0f766e', glow: 'rgba(13, 148, 136, .22)' }, // S5 HSK 5: Xanh ngọc
      { col: '#e11d48', soft: 'rgba(225, 29, 72, .14)', border: 'rgba(225, 29, 72, .4)', lip: '#be123c', glow: 'rgba(225, 29, 72, .22)' },     // S6 HSK 6: Đỏ ruby
      { col: '#4f46e5', soft: 'rgba(79, 70, 229, .14)', border: 'rgba(79, 70, 229, .4)', lip: '#3730a3', glow: 'rgba(79, 70, 229, .22)' },     // S7 HSK 7: Chàm Indigo
      { col: '#db2777', soft: 'rgba(219, 39, 119, .14)', border: 'rgba(219, 39, 119, .4)', lip: '#9d174d', glow: 'rgba(219, 39, 119, .22)' }, // S8 HSK 8: Hồng đậm
      { col: '#d97706', soft: 'rgba(217, 119, 6, .15)', border: 'rgba(217, 119, 6, .42)', lip: '#9a4604', glow: 'rgba(217, 119, 6, .22)' }    // S9 HSK 9: Vàng hổ phách
    ];

    const makeSecHdr = (sec, secHasNx, { interactive = true } = {}) => {
      const doneSec = sec.topics.filter((t) => topicDone(t)).length;
      const pctSec = sec.topics.length ? Math.round((doneSec / sec.topics.length) * 100) : 0;
      return h(interactive ? 'summary' : 'div', { class: 'sec-hdr', style: interactive ? null : { cursor: 'default' } },
        h('div', { class: 'row', style: { gap: '12px', alignItems: 'center', minWidth: 0, flex: 1 } },
          h('div', { class: 'sec-ico', 'aria-hidden': 'true' }, sec.icon),
          h('div', { class: 'stack', style: { gap: '2px', minWidth: 0, flex: 1 } },
            h('div', { class: 'row', style: { gap: '6px', alignItems: 'center', flexWrap: 'wrap' } },
              h('span', { class: 'sec-kicker' }, `SECTION ${sec.num}${secHasNx ? ' · ĐANG HỌC' : ''}`),
              sec.level ? h('span', { class: 'chip level ' + sec.level.toLowerCase().replace(/\\s+/g, '') }, sec.level) : null,
              h('span', { class: 'small muted', style: { fontSize: '.72rem' } }, `${sec.units.length} Unit · ${doneSec}/${sec.topics.length}`)
            ),
            h('b', { style: { fontSize: '1.03rem', fontWeight: 800, lineHeight: 1.25 } }, sec.name),
            h('div', { class: 'sec-prog' }, h('i', { style: { width: pctSec + '%' } }))
          )
        ),
        h('button', {
          type: 'button',
          class: 'sec-test-btn',
          title: `Học vượt cấp toàn bộ Section ${sec.num} (${sec.level || sec.name}) · Đạt ≥ 80% để pass cả Section`,
          onclick: (e) => {
            e.preventDefault();
            e.stopPropagation();
            startCategoryExam(S.lang, sec.catObj || {
              id: sec.id,
              level: sec.level || ('Section ' + sec.num),
              short: sec.short || sec.name,
              name: sec.name
            }, sec.topics);
          }
        }, 'TEST'),
        interactive ? h('span', { class: 'acc-arrow', 'aria-hidden': 'true' }, '▾') : null
      );
    };

    const wrap = h('div', { class: 'stack', style: { gap: '14px' } });
    if (visibleSections.length === 1) {
      const sec = visibleSections[0];
      const secHasNx = !!(nx && sec.topics.includes(nx.t));
      const st = secThemes[(sec.num - 1) % secThemes.length];
      wrap.append(h('div', { class: 'acc-toolbar' },
        h('span', { class: 'small muted', style: { fontWeight: 600 } }, `${sec.icon} Section ${sec.num} (${sec.level}) · ${sec.units.length} Unit · ${sec.topics.length} chủ đề`),
        sec.units.length > 1 ? makeToggleAllBtn(() => wrap, 'details.duo-unit') : null
      ));
      wrap.append(h('div', {
        class: 'sec-acc sec-featured',
        style: { '--sec-col': st.col, '--sec-soft': st.soft, '--sec-border': st.border, '--sec-lip': st.lip, '--sec-glow': st.glow }
      },
        makeSecHdr(sec, secHasNx, { interactive: false }),
        h('div', { class: 'sec-body' },
          ...sec.units.map((u, ui) => renderUnit(u, ui, secHasNx, sec.units.length))
        )
      ));
      return wrap;
    }

    const obStartLv = ob && ob.done && !p.totalLessonsDone ? (ob.level || 'hsk1') : '';
    wrap.append(h('div', { class: 'acc-toolbar' },
      h('span', { class: 'small muted', style: { fontWeight: 600 } }, `🗺️ ${visibleSections.length} Section (HSK 1–9) · ${visibleUnitsCount} Unit · ${filteredTopics.length} chủ đề`),
      makeToggleAllBtn(() => wrap, 'details.sec-acc', { groupSelector: 'details.duo-unit' })
    ));

    visibleSections.forEach((sec, secIdx) => {
      const sKey = S.lang + ':sec:' + sec.id;
      const secHasNx = !!(nx && sec.topics.includes(nx.t));
      const defSecOpen = secHasNx || (obStartLv && sec.id === obStartLv) || (!nx && !obStartLv && secIdx === 0);
      const isSecOpen = openPhases.has(sKey) || (defSecOpen && !closedPhases.has(sKey));
      const st = secThemes[(sec.num - 1) % secThemes.length];
      const isFeatured = sec.num === 1 || secHasNx;
      const secAttrs = {
        class: 'sec-acc' + (isFeatured ? ' sec-featured' : ''),
        style: { '--sec-col': st.col, '--sec-soft': st.soft, '--sec-border': st.border, '--sec-lip': st.lip, '--sec-glow': st.glow },
        ontoggle: (e) => {
          if (e.target !== e.currentTarget) return;
          if (e.currentTarget.open) { openPhases.add(sKey); closedPhases.delete(sKey); }
          else { openPhases.delete(sKey); closedPhases.add(sKey); }
        }
      };
      if (isSecOpen) secAttrs.open = 'open';

      wrap.append(h('details', secAttrs,
        makeSecHdr(sec, secHasNx, { interactive: true }),
        h('div', { class: 'sec-body' },
          ...sec.units.map((u, ui) => renderUnit(u, ui, secHasNx, sec.units.length))
        )
      ));
    });
    return wrap;
  })();

  const allUnitsFlat = allSections.flatMap((s) => s.units);
  const doneUnitsCount = allUnitsFlat.filter((u) => u.topics.every((t) => topicDone(t))).length;

  const metaFooterCard = h('div', { class: 'panel stack', style: { gap: '8px', padding: '12px 14px' } },
    h('div', {
      class: 'row between',
      style: { cursor: 'pointer', alignItems: 'center', gap: '8px' },
      onclick: () => { ROADMAP_LANG = S.lang; PICK_TAB = 'roadmap'; PICK_HUB_OPEN = true; go('pick'); }
    },
      h('div', { style: { minWidth: 0 } },
        h('div', { style: { fontSize: '.86rem', fontWeight: 600 } },
          '🚀 Lộ trình ' + LANGS[S.lang].short + ': ' + p.totalTopicsDone + '/' + p.totalAllTopics + ' bài (' + p.pct + '%)'
        ),
        h('div', { class: 'small muted', style: { fontSize: '.76rem' } },
          p.remainingTopics === 0 ? '🎉 Đã hoàn thành toàn bộ khóa học!' : (`Hoàn thành ${doneUnitsCount}/${allUnitsFlat.length} Unit · Dự kiến xong: ${estAll.timeText}`)
        )
      ),
      h('span', { class: 'small', style: { color: 'var(--teal)', fontWeight: 600, whiteSpace: 'nowrap' } }, 'Xem lộ trình →')
    ),
    h('div', { style: { height: '1px', background: 'var(--line)' } }),
    h('div', { class: 'row between', style: { alignItems: 'center', gap: '8px', flexWrap: 'wrap' } },
      ob && ob.done
        ? h('span', { class: 'small muted' }, `🎯 ${goalNames[ob.goalType] || 'Mục tiêu'} · ${ob.dailyMinutes || S.goal} phút/ngày (${(ob.level || 'hsk1').toUpperCase().replace('HSK', 'HSK ')})`)
        : h('span', { class: 'small muted' }, '✨ Xác định trình độ HSK & mục tiêu học'),
      h('button', {
        class: 'ghost mini',
        style: { whiteSpace: 'nowrap', padding: '4px 10px', fontSize: '.76rem', fontWeight: 600 },
        onclick: () => openOnboardingModal(true)
      }, ob && ob.done ? 'Làm lại khảo sát' : 'Bắt đầu khảo sát →')
    )
  );

  mount(h('div', { class: 'stack-lg' },
    h('div', { class: 'row between', style: { alignItems: 'center', gap: '8px' } },
      h('div', { class: 'row', style: { gap: '8px', alignItems: 'center', minWidth: 0 } },
        h('h1', { style: { margin: 0 } }, 'Chào ' + S.name + '!'),
        ob && ob.done ? h('span', { class: 'chip level ' + (ob.level || 'hsk1') }, (ob.level || 'hsk1').toUpperCase().replace('HSK', 'HSK ')) : null
      ),
      h('div', { class: 'row', style: { gap: '6px', alignItems: 'center', flexShrink: 0 } },
        feedbackBtn(),
        langSwitch()
      )
    ),
    todayCard,
    catBar,
    topicsNode,
    catExamCard,
    metaFooterCard,
    h('p', { class: 'small muted center', style: { margin: '12px 0', fontSize: '.76rem', opacity: .65 } }, 'Lingogo Chinese v__APP_VER__ · Section (HSK 1–9) & Unit')));
  if (_keepY != null) window.scrollTo(0, _keepY);
}
"""


NEW_TOPIC_CARD = """function topicCard(t, nx, num, idxInPhase = 0, unitMeta = null) {
  const ok = t.lang + ':' + t.id, done = t.lessons.filter((l, i) => lessonDone(t, i)).length, open = openTopics.has(ok), isCur = nx && nx.t === t;
  const d = DATA[t.lang];
  const hasGram = !!(t.gram && t.gram.length && d && d.grammar);
  const hasQuickQuiz = !!((t.vocab && t.vocab.length) || (t.kanji && t.kanji.length) || (t.quiz && t.quiz.length) || hasGram);
  const quickOpen = openQuickQuizTopics.has(ok);
  const totalL = t.lessons.length || 1;
  const pct = Math.round((done / totalL) * 100);
  const isDone = done === totalL;
  const displayNum = num != null ? num : t.pos;
  const unitInfo = typeof unitMeta === 'object' && unitMeta ? unitMeta : { unitNum: unitMeta };
  const lvl = unitInfo.secLevel || t.level || null;
  const offsets = [0, -44, -64, -44, 0, 44, 64, 44];
  const shiftX = offsets[idxInPhase % offsets.length];

  const btnCls = isDone ? 'done' : (isCur ? 'cur' : (done > 0 ? 'prog' : 'idle'));
  const ringCol = isDone ? '#ffc800' : '#1cb0f6';
  const showRing = btnCls === 'cur' || btnCls === 'prog';
  const duoIcon = (kind) => {
    const ns = 'http://www.w3.org/2000/svg';
    const svg = document.createElementNS(ns, 'svg');
    svg.setAttribute('viewBox', '0 0 24 24');
    svg.setAttribute('width', kind === 'idle' ? '23' : '31');
    svg.setAttribute('height', kind === 'idle' ? '23' : '31');
    svg.setAttribute('aria-hidden', 'true');
    if (kind === 'done') {
      const p = document.createElementNS(ns, 'path');
      p.setAttribute('d', 'M5 12.8l4.5 4.5L19 7.8');
      p.setAttribute('fill', 'none');
      p.setAttribute('stroke', 'currentColor');
      p.setAttribute('stroke-width', '3.3');
      p.setAttribute('stroke-linecap', 'round');
      p.setAttribute('stroke-linejoin', 'round');
      svg.appendChild(p);
    } else if (kind === 'idle') {
      const shackle = document.createElementNS(ns, 'path');
      shackle.setAttribute('d', 'M7.5 10.2V7.6a4.5 4.5 0 0 1 9 0v2.6');
      shackle.setAttribute('fill', 'none');
      shackle.setAttribute('stroke', 'currentColor');
      shackle.setAttribute('stroke-width', '2.5');
      shackle.setAttribute('stroke-linecap', 'round');
      const body = document.createElementNS(ns, 'rect');
      body.setAttribute('x', '5');
      body.setAttribute('y', '10');
      body.setAttribute('width', '14');
      body.setAttribute('height', '10.5');
      body.setAttribute('rx', '3.2');
      body.setAttribute('fill', 'currentColor');
      svg.appendChild(shackle);
      svg.appendChild(body);
    } else {
      const star = document.createElementNS(ns, 'path');
      star.setAttribute('d', 'M12 3.1l2.68 5.44 6 .87-4.34 4.23 1.03 5.97L12 16.79l-5.37 2.82 1.03-5.97-4.34-4.23 6-.87L12 3.1z');
      star.setAttribute('fill', 'currentColor');
      star.setAttribute('stroke', 'currentColor');
      star.setAttribute('stroke-width', '2.5');
      star.setAttribute('stroke-linejoin', 'round');
      svg.appendChild(star);
    }
    return svg;
  };
  const duoRingSvg = (pctVal, col, isCurrent) => {
    const ns = 'http://www.w3.org/2000/svg';
    const svg = document.createElementNS(ns, 'svg');
    svg.setAttribute('class', 'duo-ring-svg');
    svg.setAttribute('viewBox', '0 0 112 98');
    svg.setAttribute('aria-hidden', 'true');
    const pathD = 'M 56 8 A 47 42 0 0 1 56 92 A 47 42 0 0 1 56 8';
    const track = document.createElementNS(ns, 'path');
    track.setAttribute('class', 'duo-ring-track');
    track.setAttribute('d', pathD);
    track.setAttribute('fill', 'none');
    track.setAttribute('stroke-width', '6.5');
    track.setAttribute('stroke-linecap', 'round');
    svg.appendChild(track);
    const arcVal = Math.max(pctVal, isCurrent ? 25 : 0);
    if (arcVal > 0) {
      const prog = document.createElementNS(ns, 'path');
      prog.setAttribute('d', pathD);
      prog.setAttribute('fill', 'none');
      prog.setAttribute('stroke', col);
      prog.setAttribute('stroke-width', '6.5');
      prog.setAttribute('stroke-linecap', 'round');
      prog.setAttribute('pathLength', '100');
      prog.setAttribute('stroke-dasharray', `${arcVal} 100`);
      svg.appendChild(prog);
    }
    return svg;
  };
  const nodeGlyph = duoIcon(btnCls);

  const nextLessonIdx = isCur && nx ? nx.i : Math.max(0, t.lessons.findIndex((_, i) => !lessonDone(t, i)));
  const ctaLabel = isDone
    ? '↺ ÔN LẠI CHỦ ĐỀ'
    : (done > 0 ? `▶ HỌC TIẾP: ${lessonTitle(t, nextLessonIdx).toUpperCase()}` : `▶ BẮT ĐẦU: ${lessonTitle(t, 0).toUpperCase()}`);

  const popover = open ? h('div', {
    class: 'duo-popover',
    style: { '--duo-x': shiftX + 'px', '--bubble-col': ringCol }
  },
    h('div', { class: 'row between', style: { alignItems: 'flex-start', gap: '8px' } },
      h('div', { class: 'stack', style: { gap: '2px', minWidth: 0, flex: 1 } },
        h('b', { lang: L().lang, style: { fontSize: '.98rem' } }, `${displayNum}. ${t.title}`),
        t.sub && t.sub !== t.title ? h('span', { class: 'small muted' }, t.sub) : null
      ),
      h('div', { class: 'row', style: { gap: '6px', alignItems: 'center', flexShrink: 0 } },
        unitInfo.unitNum ? h('span', { class: 'chip good', style: { fontWeight: 700 } }, (unitInfo.secNum ? `S${unitInfo.secNum} · ` : '') + 'Unit ' + unitInfo.unitNum) : null,
        lvl ? h('span', { class: 'chip level ' + lvl.toLowerCase().replace('+', '').replace(/\\s+/g, '') }, lvl) : null,
        h('span', { class: 'chip' + (isDone ? ' good' : '') }, done + '/' + totalL),
        h('button', { class: 'ghost mini', style: { minHeight: '28px', padding: '2px 8px' }, onclick: () => { openTopics.delete(ok); homeView({ preserveScroll: true }); } }, '✕')
      )
    ),
    h('button', {
      type: 'button',
      class: 'duo-cta-btn',
      onclick: () => lessonView(t, isDone ? 0 : nextLessonIdx)
    }, ctaLabel),
    (hasGram || hasQuickQuiz) && h('div', { class: 'extras', style: { gap: '6px', marginBottom: '2px' } },
      hasGram && h('button', {
        class: 'ghost mini',
        style: { border: '1px solid var(--line)', background: 'var(--surface)', fontSize: '.82rem', padding: '5px 10px' },
        onclick: () => grammarView(t, 'home')
      }, '📖 Ngữ pháp (' + t.gram.length + ')'),
      hasQuickQuiz && h('button', {
        class: quickOpen ? 'primary mini' : 'ghost mini',
        style: quickOpen ? { fontSize: '.82rem', padding: '5px 10px' } : { border: '1px solid rgba(15,82,87,.35)', background: 'rgba(15,82,87,.07)', fontSize: '.82rem', padding: '5px 10px', fontWeight: 600 },
        onclick: () => {
          if (quickOpen) openQuickQuizTopics.delete(ok);
          else {
            openQuickQuizTopics.add(ok);
            delete INLINE_TOPIC_QUIZ[ok];
          }
          homeView({ preserveScroll: true });
        }
      }, quickOpen ? '✕ Thu gọn bài tập' : '⚡ Bài tập kiểm tra nhanh'),
      hasGram && h('button', {
        class: 'ghost mini',
        style: { border: '1px solid var(--line)', background: 'var(--surface)', fontSize: '.82rem', padding: '5px 10px' },
        onclick: () => grammarTopicQuiz(t, 'home')
      }, '📝 Quiz 10 câu')
    ),
    quickOpen && renderInlineTopicQuiz(t),
    ...t.lessons.map((l, i) => {
      const dn = lessonDone(t, i);
      const lessonBtn = h('button', {
        class: 'lesson' + (dn ? ' done' : '') + (isCur && nx.i === i ? ' next' : ''),
        style: dn ? { flex: '1', minWidth: 0 } : null,
        onclick: () => lessonView(t, i)
      },
        h('span', { class: 'dot', 'aria-hidden': 'true' }, dn ? '✓' : i + 1),
        h('span', { class: 'meta' },
          h('span', { lang: l.kind === 'learn' ? L().lang : null }, lessonTitle(t, i)),
          dn && typeof S.lessons[lkey(t, i)] === 'number' && h('span', { class: 'small muted', style: { display: 'block' } }, 'Tốt nhất ' + S.lessons[lkey(t, i)] + '%')
        )
      );

      if (!dn) return lessonBtn;

      const resetBtn = h('button', {
        class: 'ghost mini',
        title: 'Xóa tiến độ bài này để học lại từ đầu',
        'aria-label': 'Xóa tiến độ bài ' + lessonTitle(t, i),
        style: {
          flex: 'none', padding: '0 10px', height: '52px', borderRadius: '12px',
          color: 'var(--muted)', fontSize: '.74rem', display: 'flex', flexDirection: 'column',
          alignItems: 'center', justifyContent: 'center', gap: '2px', lineHeight: 1.1,
          border: '1px solid var(--line)', background: 'var(--surface)'
        },
        onclick: (e) => {
          e.stopPropagation();
          if (confirm('Xóa tiến độ bài “' + lessonTitle(t, i) + '” để học lại từ đầu như bài mới?')) {
            resetLesson(t, i);
            homeView({ preserveScroll: true });
          }
        }
      }, h('span', { style: { fontSize: '1rem', lineHeight: 1 } }, '🗑️'), h('span', { style: { fontSize: '.68rem', whiteSpace: 'nowrap' } }, 'Xóa'));

      return h('div', { class: 'row', style: { gap: '6px', alignItems: 'stretch' } }, lessonBtn, resetBtn);
    }),
    done > 0 ? h('div', { class: 'extras', style: { justifyContent: 'flex-end', paddingTop: '4px' } },
      h('button', {
        class: 'ghost mini',
        style: { color: 'var(--muted)', fontSize: '.78rem' },
        title: 'Xóa tiến độ tất cả bài đã học trong chủ đề này',
        onclick: () => {
          if (confirm('Xóa tiến độ của toàn bộ ' + done + ' bài đã học trong chủ đề “' + (t.sub || t.title) + '”?')) {
            t.lessons.forEach((_, idx) => {
              if (lessonDone(t, idx)) resetLesson(t, idx, { silent: true });
            });
            save();
            toast('Đã xóa tiến độ các bài học trong chủ đề.');
            homeView({ preserveScroll: true });
          }
        }
      }, '↺ Xóa tiến độ chủ đề (' + done + ')')
    ) : null
  ) : null;

  return h('section', { id: 'duo-step-' + t.id, class: 'duo-step' },
    h('div', { class: 'duo-node-anchor', style: { '--duo-x': shiftX + 'px' } },
      isCur ? h('button', {
        type: 'button',
        class: 'duo-float-tip',
        onclick: () => lessonView(nx.t, nx.i)
      }, done > 0 ? 'HỌC TIẾP' : 'START') : null,
      h('div', { class: 'duo-node-stage' + (showRing ? '' : ' compact') },
        showRing ? duoRingSvg(pct, ringCol, isCur) : null,
        h('button', {
          type: 'button',
          class: 'duo-btn ' + btnCls,
          'aria-expanded': String(open),
          'aria-label': (t.sub || t.title) + ' (' + done + '/' + totalL + ')',
          onclick: () => {
            if (open) openTopics.delete(ok);
            else {
              openTopics.clear();
              openTopics.add(ok);
            }
            homeView({ preserveScroll: true });
          }
        }, nodeGlyph)
      ),
      h('div', { class: 'small center', style: { marginTop: '6px', maxWidth: '170px', fontWeight: 700, fontSize: '.78rem', lineHeight: 1.25, color: isCur ? 'var(--ink)' : 'var(--muted)' } },
        `${displayNum}. ${t.sub || t.title}`
      )
    ),
    popover
  );
}
"""


def main() -> None:
    ver_data = json.loads(VERSION_JSON.read_text(encoding="utf-8"))
    build_id = ver_data["build"]
    app_ver = ver_data["version"]
    html = SRC_HTML.read_text(encoding="utf-8")

    # 1. Head, CSS & branding
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
    html = replace_exact(
        html,
        ".lesson .meta { flex: 1; min-width: 0; }\n",
        ".lesson .meta { flex: 1; min-width: 0; }" + DUO_CSS,
        label="Duolingo Section/Unit/Path CSS",
    )
    html = replace_exact(
        html,
        ".tokens button { min-height: 44px;",
        "html { overscroll-behavior-y: contain; }\nbutton, a, [role=\"button\"] { touch-action: manipulation; }\n.tokens button { min-height: 44px;",
        label="Mobile tap touch CSS",
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

    # 5. Curriculum sections helper + state normalization + study minutes tracking
    html = replace_exact(
        html,
        "const EN_CATEGORIES = CATEGORIES.en;\nlet subjectsOpen = false;\n"
        "const fresh = () => ({ v: 2, name: '', goal: 20, lang: 'en', enCat: 'a1', zhCat: 'hsk1', jaCat: 'n5', days: {}, dl: {}, pv: {}, srs: {}, lessons: {}, spoken: {}, written: {}, fill: {}, gq: {}, en_crash30: {}, ach: {}, del: {}, delAll: 0, t: 0 });\n"
        "let S = fresh();\n"
        "try { const raw = localStorage.getItem(KEY); if (raw) S = Object.assign(fresh(), JSON.parse(raw)); } catch (e) { /* bị chặn lưu trữ */ }",
        NEW_CURRICULUM_HELPERS
        + "const EN_CATEGORIES = CATEGORIES.en;\nlet subjectsOpen = false;\n"
        + "const fresh = () => ({ v: 2, name: '', goal: 20, lang: 'zh', enCat: 'a1', zhCat: 'all', jaCat: 'n5', onboarding: null, days: {}, dl: {}, pv: {}, srs: {}, lessons: {}, spoken: {}, written: {}, fill: {}, gq: {}, en_crash30: {}, ach: {}, del: {}, delAll: 0, t: 0 });\n"
        + "let S = fresh();\n"
        + "try { const raw = localStorage.getItem(KEY); if (raw) S = Object.assign(fresh(), JSON.parse(raw)); } catch (e) { /* bị chặn lưu trữ */ }\nS.lang = 'zh';",
        label="buildCurriculumSections + fresh + S.lang",
    )
    html = replace_exact(html, "S = mergeState(S, remote);", "S = mergeState(S, remote); S.lang = 'zh';", count=2, label="sync normalize lang")
    html = replace_exact(html, "  if (!S.name) return welcomeView();", "  if (!LANGS[S.lang]) S.lang = 'zh';\n  if (!S.name) return welcomeView();", label="route guard S.lang")

    html = replace_exact(
        html,
        "function goal(code = S.lang, d = todayN()) {\n"
        "  const base = Math.max(20, S.goal || 20);\n"
        "  if (S.smartSchedule === false) return base;\n"
        "  const sch = getDaySchedule(d);\n"
        "  if (!sch || !sch.goals || !sch.goals[code]) return base;\n"
        "  return Math.max(10, Math.round(base * sch.goals[code]));\n"
        "}\n\n"
        "const xpOf = (d, code) => ((S.dl || {})[d] || {})[code] || 0;\n"
        "const metGoal = (d, code) => xpOf(d, code) >= goal(code, d);\n"
        "// Duy trì chuỗi ngày học liên tục (Streak): Chỉ cần người học duy trì việc học đều đặn mỗi ngày (tối thiểu 10 XP hoặc đạt mục tiêu)\n"
        "const hasLearnedDay = (d, code) => xpOf(d, code) >= Math.min(10, goal(code, d));\n\n"
        "function streak(code = S.lang) {\n"
        "  let d = todayN(); if (!hasLearnedDay(d, code)) d--;\n"
        "  let n = 0; while (hasLearnedDay(d, code)) { n++; d--; }\n"
        "  return n;\n"
        "}\n\n"
        "function longest(code = S.lang) {\n"
        "  const ks = Object.keys(S.dl || {}).filter((k) => hasLearnedDay(k, code)).map(Number).sort((a, b) => a - b);\n"
        "  let best = 0, run = 0, prev = null;\n"
        "  for (const k of ks) { run = prev !== null && k === prev + 1 ? run + 1 : 1; best = Math.max(best, run); prev = k; }\n"
        "  return best;\n"
        "}\n\n"
        "function addXp(n, code = S.lang) {\n"
        "  if (!n) return;\n"
        "  const t = todayN(), before = metGoal(t, code);\n"
        "  S.days[t] = (S.days[t] || 0) + n;\n"
        "  S.dl = S.dl || {}; S.dl[t] = S.dl[t] || {}; S.dl[t][code] = (S.dl[t][code] || 0) + n;\n"
        "  save();\n"
        "  if (!before && metGoal(t, code)) setTimeout(() => toast('Đạt mục tiêu ' + goal(code, t) + ' XP ' + LANGS[code].short + ' hôm nay! 🎉'), 300);\n"
        "}\n"
        "const XP_ITEM = 5; // mỗi từ (hoặc kanji, câu, tình huống) làm đúng = 5 XP",
        "function goal(code = S.lang, d = todayN()) {\n"
        "  const base = Math.max(10, S.goal || 10);\n"
        "  if (S.smartSchedule === false) return base;\n"
        "  const sch = getDaySchedule(d);\n"
        "  if (!sch || !sch.goals || !sch.goals[code]) return base;\n"
        "  return Math.max(10, Math.round(base * sch.goals[code]));\n"
        "}\n\n"
        "const xpOf = (d, code) => ((S.dl || {})[d] || {})[code] || 0;\n"
        "const metGoal = (d, code) => xpOf(d, code) >= goal(code, d);\n"
        "// Duy trì chuỗi ngày học liên tục (Streak): ít nhất 10 phút học mỗi ngày là đạt mốc\n"
        "const hasLearnedDay = (d, code) => xpOf(d, code) >= Math.min(10, goal(code, d));\n\n"
        "function streak(code = S.lang) {\n"
        "  let d = todayN(); if (!hasLearnedDay(d, code)) d--;\n"
        "  let n = 0; while (hasLearnedDay(d, code)) { n++; d--; }\n"
        "  return n;\n"
        "}\n\n"
        "function longest(code = S.lang) {\n"
        "  const ks = Object.keys(S.dl || {}).filter((k) => hasLearnedDay(k, code)).map(Number).sort((a, b) => a - b);\n"
        "  let best = 0, run = 0, prev = null;\n"
        "  for (const k of ks) { run = prev !== null && k === prev + 1 ? run + 1 : 1; best = Math.max(best, run); prev = k; }\n"
        "  return best;\n"
        "}\n\n"
        "function addXp(n, code = S.lang) {\n"
        "  if (!n) return;\n"
        "  const t = todayN(), before = metGoal(t, code);\n"
        "  S.days[t] = (S.days[t] || 0) + n;\n"
        "  S.dl = S.dl || {}; S.dl[t] = S.dl[t] || {}; S.dl[t][code] = (S.dl[t][code] || 0) + n;\n"
        "  save();\n"
        "  if (!before && metGoal(t, code)) setTimeout(() => toast('Đạt mục tiêu ' + goal(code, t) + ' phút học ' + LANGS[code].short + ' hôm nay! 🎉'), 300);\n"
        "}\n"
        "const XP_ITEM = 0; // Tính tiến độ theo thời gian học (phút), không cộng XP theo từng từ\n"
        "let ACTIVE_STUDY_MODE = false;\n"
        "let STUDY_SEC = 0;\n"
        "function isActivelyStudying() {\n"
        "  if (typeof document === 'undefined' || document.visibilityState !== 'visible') return false;\n"
        "  if (!S || !S.name) return false;\n"
        "  if (document.getElementById('flashcard-overlay')) return true;\n"
        "  return !!ACTIVE_STUDY_MODE;\n"
        "}\n"
        "setInterval(() => {\n"
        "  if (isActivelyStudying()) {\n"
        "    STUDY_SEC += 5;\n"
        "    if (STUDY_SEC >= 60) {\n"
        "      const mins = Math.floor(STUDY_SEC / 60);\n"
        "      STUDY_SEC -= mins * 60;\n"
        "      addXp(mins, S.lang || 'zh');\n"
        "    }\n"
        "  }\n"
        "}, 5000);",
        label="study minutes tracking",
    )
    html = replace_exact(
        html,
        "  const xpItems = Math.floor(xpOf(d, code) / XP_ITEM);",
        "  const xpItems = XP_ITEM > 0 ? Math.floor(xpOf(d, code) / XP_ITEM) : 0;",
        label="safe division in getReviewedToday",
    )

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

    # 7. Navigation: 5 logical tabs matching Lingogo English + direct entry
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
        "let VIEW = 'pick'; // mở app là màn hình chọn ngôn ngữ\n"
        "let SKILL_TAB = 'speak'; // 'speak' | 'write'\n"
        "let KNOWLEDGE_TAB = 'gram'; // 'gram' | 'chars' | 'kana'\n"
        "let EXAM_LV = { zh: 'HSK 1', ja: 'N5' };\n"
        "const TABS = [\n"
        "  ['home', 'Học', ICON.home],\n"
        "  ['exam', 'Luyện thi', ICON.exam],\n"
        "  ['knowledge', 'Kiến thức', ICON.book],\n"
        "  ['progress', 'Tiến độ', ICON.chart]\n"
        "];\n"
        "function setTabs(show) {\n"
        "  const nav = document.getElementById('tabs'); nav.hidden = !show;\n"
        "  document.body.classList.toggle('lessonmode', !show);\n"
        "  document.body.classList.toggle('has-tabs', !!show);\n"
        "  if (!show) return;\n"
        "  const code = S.lang;\n"
        "  const tabsList = TABS.map(([k, label, d]) => {\n"
        "    if (k === 'exam') {\n"
        "      const examLabel = code === 'en' ? 'Luyện IELTS' : (code === 'zh' ? 'Luyện HSKK' : 'Luyện JLPT');\n"
        "      return [k, examLabel, d];\n"
        "    }\n"
        "    return [k, label, d];\n"
        "  });\n"
        "  nav.replaceChildren(...tabsList.map(([k, label, d]) => {\n"
        "    const isCur = (VIEW === k) ||\n"
        "      (k === 'home' && (VIEW === 'home' || VIEW === 'review')) ||\n"
        "      (k === 'exam' && (VIEW === 'exam' || VIEW === 'ielts')) ||\n"
        "      (k === 'knowledge' && (VIEW === 'knowledge' || VIEW === 'grammar' || VIEW === 'kanji'));\n"
        "    return h('button', {\n"
        "      'aria-current': isCur ? 'page' : null,\n"
        "      onclick: () => go(k)\n"
        "    }, icon(d), label);\n"
        "  }));\n"
        "}",
        "let VIEW = 'home'; // mở thẳng vào trang học Tiếng Trung\n"
        "let SKILL_TAB = 'speak'; // 'listen' | 'speak' | 'read' | 'write'\n"
        "let KNOWLEDGE_TAB = 'gram'; // 'gram' | 'read301' | 'chiet_tu' | 'chars'\n"
        "let EXAM_LV = { zh: 'HSK 1', ja: 'N5' };\n"
        "const TABS = [\n"
        "  ['home', 'Trang chủ', ICON.home],\n"
        "  ['review', 'Từ vựng', ICON.cards],\n"
        "  ['practice', 'Luyện tập', ICON.skills],\n"
        "  ['exam', 'Luyện thi', ICON.exam],\n"
        "  ['progress', 'Tiến độ', ICON.chart]\n"
        "];\n"
        "function setTabs(show) {\n"
        "  const nav = document.getElementById('tabs'); nav.hidden = !show;\n"
        "  document.body.classList.toggle('lessonmode', !show);\n"
        "  document.body.classList.toggle('has-tabs', !!show);\n"
        "  if (!show) return;\n"
        "  nav.replaceChildren(...TABS.map(([k, label, d]) => {\n"
        "    const isCur = (VIEW === k) ||\n"
        "      (k === 'home' && (VIEW === 'home' || VIEW === 'pick')) ||\n"
        "      (k === 'review' && (VIEW === 'review' || VIEW === 'dict')) ||\n"
        "      (k === 'practice' && (VIEW === 'practice' || VIEW === 'games' || VIEW === 'knowledge' || VIEW === 'grammar' || VIEW === 'kanji' || VIEW === 'skills' || VIEW === 'speak' || VIEW === 'write')) ||\n"
        "      (k === 'exam' && (VIEW === 'exam' || VIEW === 'ielts'));\n"
        "    return h('button', {\n"
        "      'aria-current': isCur ? 'page' : null,\n"
        "      onclick: () => go(k)\n"
        "    }, icon(d), label);\n"
        "  }));\n"
        "}",
        label="5 navigation tabs",
    )
    html = replace_exact(
        html,
        "    ({\n"
        "      home: homeView,\n"
        "      review: reviewView,\n"
        "      skills: () => skillsView(SKILL_TAB),\n"
        "      ielts: ieltsTabView,\n"
        "      knowledge: knowledgeTabView,\n"
        "      grammar: knowledgeTabView,\n"
        "      exam: examTabView,\n"
        "      speak: () => skillsView('speak'),\n"
        "      write: () => skillsView('write'),\n"
        "      dict: dictView,\n"
        "      progress: progressView\n"
        "    })[VIEW]();",
        "    ({\n"
        "      home: homeView,\n"
        "      practice: practiceTabView,\n"
        "      games: gamesTabView,\n"
        "      review: reviewView,\n"
        "      skills: () => skillsView(SKILL_TAB),\n"
        "      ielts: ieltsTabView,\n"
        "      knowledge: knowledgeTabView,\n"
        "      grammar: knowledgeTabView,\n"
        "      exam: examTabView,\n"
        "      speak: () => skillsView('speak'),\n"
        "      write: () => skillsView('write'),\n"
        "      dict: dictView,\n"
        "      progress: progressView\n"
        "    })[VIEW]();",
        label="route views map",
    )

    # 8. Pick / Roadmap / Schedule / Welcome single-language UX
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
    html = replace_exact(html, "? 'Lộ trình cả 3 ngôn ngữ'", "? 'Lộ trình Tiếng Trung (HSK 3.0)'", label="roadmap header subtitle")
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
    html = replace_exact(html, "  if (!PICK_HUB_OPEN) {\n", "  PICK_HUB_OPEN = true;\n  if (!PICK_HUB_OPEN) {\n", label="force PICK_HUB_OPEN true")
    html = replace_exact(html, "      ['progress', '📊 Tiến độ ngôn ngữ'],\n", "      ['progress', '📊 Tiến độ Tiếng Trung'],\n", label="pick tab progress label")
    html = replace_exact(
        html,
        "        onclick: () => { PICK_HUB_OPEN = false; pickView(); }\n      }, '← Quay lại chọn ngôn ngữ'),",
        "        onclick: () => { PICK_HUB_OPEN = false; go('home'); }\n      }, '← Về Trang chủ'),",
        label="pick hub back button",
    )
    html = replace_exact(
        html,
        "h('p', { class: 'label' }, 'Lingogo'),\n        h('h1', {}, 'Chào ' + S.name + ', hôm nay học gì?')",
        "h('p', { class: 'label' }, 'Lingogo Chinese'),\n        h('h1', {}, 'Chào ' + S.name + ', hôm nay học gì?')",
        label="pickView label",
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
        "    goals.replaceChildren(...[[10, 'Nhẹ nhàng', '10 phút/ngày (Đạt mốc tối thiểu)'], [20, 'Vừa phải', '20 phút/ngày (Khuyên dùng)'], [30, 'Nghiêm túc', '30 phút/ngày (Tiến bộ nhanh)']]\n"
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

    # 9. Replace dictBtn + dictView + inject Flashcard 3D, Onboarding, Practice Hub, Mini-game
    dict_start = html.index("function dictBtn() {")
    home_start = html.index("function homeView() {")
    home_end = html.index("\n// ===== HỆ THỐNG LUYỆN THI IELTS", home_start)
    new_home = NEW_HOME_VIEW.replace("__APP_VER__", app_ver)
    html = html[:dict_start] + NEW_DICT_FLASHCARD_PRACTICE + "\n" + new_home + html[home_end:]

    # 10. Replace topicCard with Duolingo S-path coin + popover
    tc_start = html.index("function topicCard(t, nx, num) {")
    tc_end = html.index("\n// ===== Thẻ từ và câu cho bài học", tc_start)
    html = html[:tc_start] + NEW_TOPIC_CARD + html[tc_end:]

    # 11. Review tab (Từ vựng) header with Flashcard 3D + Từ điển quick buttons (matching Lingogo English)
    html = replace_exact(
        html,
        "  const head = (isReviewing = false) => h('div', { class: 'row between wrap', style: { alignItems: 'center', gap: '6px' } },\n"
        "    h('button', { class: 'ghost mini', style: { whiteSpace: 'nowrap', flexShrink: 0, padding: '6px 8px', fontSize: '.84rem' }, onclick: () => go('home') }, '← Về trang Học'),\n"
        "    isReviewing ? h('span', { class: 'label', style: { margin: 0, whiteSpace: 'nowrap' } }, 'Ôn tập FSRS') : null,\n"
        "    h('div', { class: 'row', style: { gap: '6px', alignItems: 'center', flexShrink: 0 } },\n"
        "      feedbackBtn({ mode: 'review_vocab' }),\n"
        "      langSwitch()\n"
        "    )\n"
        "  );",
        "  const head = (isReviewing = false) => h('div', { class: 'stack', style: { gap: '8px' } },\n"
        "    h('div', { class: 'row between wrap', style: { alignItems: 'center', gap: '6px' } },\n"
        "      h('h1', { style: { margin: 0, fontSize: '1.35rem' } }, isReviewing ? 'Từ vựng · Ôn FSRS' : 'Từ vựng'),\n"
        "      h('div', { class: 'row', style: { gap: '6px', alignItems: 'center', flexShrink: 0 } },\n"
        "        feedbackBtn({ mode: 'review_vocab' }),\n"
        "        langSwitch()\n"
        "      )\n"
        "    ),\n"
        "    h('div', { class: 'row', style: { gap: '8px' } },\n"
        "      h('button', {\n"
        "        class: 'panel row',\n"
        "        style: { flex: 1, padding: '8px 10px', gap: '6px', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '.84rem', minHeight: '40px' },\n"
        "        onclick: openFlashcardPractice\n"
        "      }, '🃏 Flashcard 3D'),\n"
        "      h('button', {\n"
        "        class: 'panel row',\n"
        "        style: { flex: 1, padding: '8px 10px', gap: '6px', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '.84rem', minHeight: '40px' },\n"
        "        onclick: () => go('dict')\n"
        "      }, '📖 Từ điển')\n"
        "    )\n"
        "  );",
        label="reviewView header matching English",
    )
    html = replace_exact(
        html,
        "          h('button', { class: 'ghost', onclick: () => go('pick') }, 'Về Màn hình chính')",
        "          h('button', { class: 'ghost', onclick: () => { PICK_TAB = 'roadmap'; PICK_HUB_OPEN = true; go('pick'); } }, '🗺️ Xem lộ trình')",
        count=2,
        label="reviewView pick buttons",
    )
    html = replace_exact(
        html,
        "            ? 'Bạn đã hoàn thành toàn bộ các từ vựng đến hạn. Hãy học thêm bài mới để tiếp tục lộ trình!'",
        "            ? 'Bạn đã hoàn thành toàn bộ các từ vựng đến hạn. Hãy mở Flashcard 3D hoặc Từ điển bên trên, hoặc học bài mới!'",
        label="reviewView empty vault message",
    )

    # 12. Back button to Luyện tập inside skillsView & knowledgeTabView
    html = replace_exact(
        html,
        "  const head = h('div', { class: 'stack', style: { gap: '6px' } },\n"
        "    h('div', { class: 'row between', style: { alignItems: 'center' } },\n"
        "      h('h1', { style: { margin: 0 } }, 'Kỹ năng'),",
        "  const head = h('div', { class: 'stack', style: { gap: '6px' } },\n"
        "    h('div', { class: 'row between', style: { alignItems: 'center' } },\n"
        "      h('div', { class: 'row', style: { gap: '8px', alignItems: 'center' } },\n"
        "        h('button', { class: 'ghost mini', onclick: () => go('practice') }, '← Luyện tập'),\n"
        "        h('h1', { style: { margin: 0, fontSize: '1.35rem' } }, 'Kỹ năng')\n"
        "      ),",
        label="skillsView back to practice",
    )
    html = replace_exact(
        html,
        "      h('p', { class: 'label', style: { margin: 0 } }, isJa ? 'Kiến thức Tiếng Nhật' : 'Kiến thức Tiếng Trung'),",
        "      h('div', { class: 'row', style: { gap: '8px', alignItems: 'center' } },\n"
        "        h('button', { class: 'ghost mini', onclick: () => go('practice') }, '← Luyện tập'),\n"
        "        h('p', { class: 'label', style: { margin: 0 } }, 'Kiến thức Tiếng Trung')\n"
        "      ),",
        label="knowledgeTabView back to practice",
    )

    # 13. Handle Unit-level Test cleanly inside startHskLevelExam & ACTIVE_STUDY_MODE hooks
    html = replace_exact(
        html,
        "  const level = 'HSK ' + num;",
        "  const isUnitExam = !!(opts && opts.catObj && opts.catObj.id && String(opts.catObj.id).startsWith('unit-'));\n"
        "  const level = isUnitExam ? (opts.catObj.level + ' · ' + opts.catObj.name) : ('HSK ' + num);\n"
        "  const attemptKey = isUnitExam ? opts.catObj.id : ('HSK ' + num);",
        label="startHskLevelExam unit attemptKey",
    )
    html = replace_exact(
        html,
        "const prev = S.hsk_attempts[level];",
        "const prev = S.hsk_attempts[attemptKey];",
        label="startHskLevelExam read attemptKey",
    )
    html = replace_exact(
        html,
        "S.hsk_attempts[level] = currentAtt;",
        "S.hsk_attempts[attemptKey] = currentAtt;",
        label="startHskLevelExam write attemptKey",
    )

    # Active study timer hooks (count only when actively studying, never idle on home/menus)
    html = replace_exact(html, "function go(k) {\n  stopSay();", "function go(k) {\n  ACTIVE_STUDY_MODE = false;\n  stopSay();", label="go reset study timer")
    html = replace_exact(html, "function pickView() {\n  setTabs(false);", "function pickView() {\n  ACTIVE_STUDY_MODE = false;\n  setTabs(false);", label="pickView study false")
    html = replace_exact(html, "function welcomeView() {\n  setTabs(false);", "function welcomeView() {\n  ACTIVE_STUDY_MODE = false;\n  setTabs(false);", label="welcomeView study false")
    html = replace_exact(html, "function lessonView(t, i, opts = null) {\n  VIEW = 'lesson'; setTabs(false);", "function lessonView(t, i, opts = null) {\n  ACTIVE_STUDY_MODE = true;\n  VIEW = 'lesson'; setTabs(false);", label="lessonView study true")
    html = replace_exact(html, "  const exit = () => { stopSay(); setFeedbackContext(null); go('home'); };", "  const exit = () => { ACTIVE_STUDY_MODE = false; stopSay(); setFeedbackContext(null); go('home'); };", label="lessonView exit study false")
    html = replace_exact(html, "  function finish() {\n    const all = [...first.values()]", "  function finish() {\n    ACTIVE_STUDY_MODE = false;\n    const all = [...first.values()]", label="lessonView finish study false")
    html = replace_exact(html, "function reviewView(forceExtra = false) {\n  const code = S.lang, t0 = todayN();", "function reviewView(forceExtra = false) {\n  ACTIVE_STUDY_MODE = false;\n  const code = S.lang, t0 = todayN();", label="reviewView entry study false")
    html = replace_exact(html, "    const item = queue[0];\n    if (!item) {\n      checkAch();", "    const item = queue[0];\n    ACTIVE_STUDY_MODE = !!item;\n    if (!item) {\n      checkAch();", label="reviewView active queue flag")
    html = replace_exact(html, "function skillsView(tab) {\n  stopSay();", "function skillsView(tab) {\n  ACTIVE_STUDY_MODE = true;\n  stopSay();", label="skillsView study true")
    html = replace_exact(html, "function charView(code, c, list) {\n  const idx = list.indexOf(c)", "function charView(code, c, list) {\n  ACTIVE_STUDY_MODE = true;\n  const idx = list.indexOf(c)", label="charView study true")
    html = replace_exact(html, "function grammarView(t, backTo) {\n  const code = t.lang", "function grammarView(t, backTo) {\n  ACTIVE_STUDY_MODE = true;\n  const code = t.lang", label="grammarView study true")
    html = replace_exact(html, "function grammarQuizView(levelKey, onlyWrong, customOpts) {\n  const code = S.lang", "function grammarQuizView(levelKey, onlyWrong, customOpts) {\n  ACTIVE_STUDY_MODE = true;\n  const code = S.lang", label="grammarQuizView study true")
    html = replace_exact(html, "function knowledgeTabView() {\n  const code = S.lang;", "function knowledgeTabView() {\n  ACTIVE_STUDY_MODE = true;\n  const code = S.lang;", label="knowledgeTabView study true")
    html = replace_exact(html, "function examTabView() {\n  const code = S.lang;", "function examTabView() {\n  ACTIVE_STUDY_MODE = false;\n  const code = S.lang;", label="examTabView menu study false")
    html = replace_exact(
        html,
        "  let paused = false;\n\n  const exit = () => {\n    stopExamLiveTimer();",
        "  let paused = false;\n  ACTIVE_STUDY_MODE = true;\n\n  const exit = () => {\n    ACTIVE_STUDY_MODE = false;\n    stopExamLiveTimer();",
        label="startHskLevelExam start/exit study flag",
    )
    html = replace_exact(
        html,
        "      onclick: () => {\n        paused = !paused;\n        const el = document.getElementById('hsk_timer_txt');",
        "      onclick: () => {\n        paused = !paused;\n        ACTIVE_STUDY_MODE = !submitted && !paused;\n        const el = document.getElementById('hsk_timer_txt');",
        label="startHskLevelExam pause study flag",
    )
    html = replace_exact(
        html,
        "      submitted = true;\n      renderExamPage();",
        "      submitted = true;\n      ACTIVE_STUDY_MODE = false;\n      renderExamPage();",
        count=2,
        label="exam submit study false",
    )
    html = replace_exact(html, "function progressView() {\n  const t = todayN()", "function progressView() {\n  ACTIVE_STUDY_MODE = false;\n  const t = todayN()", label="progressView study false")

    # 14. Branding copy, ACH, feedback title, Progress tab (study minutes + onboarding)
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
        "  const goalSel = h('select', { id: 'goal', onchange: (e) => { S.goal = Number(e.target.value); save(); toast('Đã lưu mục tiêu.'); } },\n"
        "    [[20, 'Tối thiểu · 20 XP cơ bản (Focus: 40 XP / Duy trì: 10 XP)'], [30, 'Vừa phải · 30 XP cơ bản (Focus: 60 XP / Duy trì: 15 XP)'], [50, 'Nghiêm túc · 50 XP cơ bản (Focus: 100 XP / Duy trì: 25 XP)']].map(([v, l]) => h('option', { value: v, selected: (S.goal || 20) === v }, l)));\n"
        "  const smartSchedCheck = h('input', { type: 'checkbox', id: 'smartSched', checked: S.smartSchedule !== false, onchange: (e) => { S.smartSchedule = e.target.checked; save(); toast('Đã cập nhật chế độ lộ trình.'); progressView(); } });\n"
        "  let confirmReset = false;\n"
        "  const resetBtn = h('button', { class: 'ghost block', onclick: async () => {\n"
        "    if (!confirmReset) { confirmReset = true; resetBtn.textContent = 'Bấm lần nữa để xóa toàn bộ tiến độ của cả ba thứ tiếng'; return; }\n"
        "    const resetTime = Date.now();\n"
        "    S = fresh();\n"
        "    S.delAll = resetTime;\n"
        "    S.t = resetTime;\n"
        "    save();\n"
        "    await pushGhSync(true);\n"
        "    toast('Đã xóa toàn bộ tiến độ và cập nhật lên máy chủ.');\n"
        "    welcomeView();\n"
        "  } }, 'Xóa tiến độ và học lại từ đầu');\n"
        "  const c0 = S.lang, k0 = Object.keys(S.srs).filter((k) => k.startsWith(c0 + ':'));\n"
        "  const xpTotal = (c) => Object.values(S.dl || {}).reduce((a, m) => a + (m[c] || 0), 0);\n"
        "  const w0 = Object.keys(S.written).filter((k) => k.startsWith(c0 + ':')).length;\n"
        "  mount(h('div', { class: 'stack-lg' },\n"
        "    h('div', { class: 'row between' }, h('h1', {}, 'Tiến độ'), h('div', { class: 'row', style: { gap: '6px', alignItems: 'center' } }, feedbackBtn({ mode: 'progress' }), langSwitch())), \n"
        "    h('div', { class: 'stats' },\n"
        "      h('div', { class: 'stat' }, h('b', {}, streak(c0)), h('span', {}, 'chuỗi ngày · dài nhất ' + longest(c0))),\n"
        "      h('div', { class: 'stat' }, h('b', {}, xpOf(t, c0) + '/' + goal()), h('span', {}, 'XP hôm nay')),\n"
        "      h('div', { class: 'stat' }, h('b', {}, xpTotal(c0)), h('span', {}, 'tổng XP ' + L().short))),\n"
        "    h('div', { class: 'stats' },\n"
        "      h('div', { class: 'stat' }, h('b', {}, Object.keys(S.lessons).filter((k) => k.startsWith(c0 + ':')).length), h('span', {}, 'bài đã học')),\n"
        "      h('div', { class: 'stat' }, h('b', {}, k0.length), h('span', {}, 'mục đang ôn')),\n"
        "      h('div', { class: 'stat' }, h('b', {}, LANGS[c0].cjk ? w0 : k0.filter((k) => S.srs[k].b >= 3).length), h('span', {}, LANGS[c0].cjk ? 'chữ đã viết' : 'đã nhớ chắc'))),\n"
        "    h('div', { class: 'panel stack' }, h('h3', {}, 'XP ' + L().short + ' 7 ngày qua'),\n"
        "      h('div', { class: 'week', role: 'img', 'aria-label': days.map((d) => wd[dayDate(d).getUTCDay()] + ': ' + xd(d) + ' XP').join(', ') },\n"
        "        days.map((d) => h('div', { class: d === t ? 'today' : '' }, h('span', {}, xd(d) || ''), h('i', { style: { height: (xd(d) / max * 100) + '%' } }), h('span', {}, wd[dayDate(d).getUTCDay()]))))),\n",
        "  const goalSel = h('select', { id: 'goal', onchange: (e) => { S.goal = Number(e.target.value); save(); toast('Đã lưu mục tiêu ' + S.goal + ' phút/ngày.'); progressView(); } },\n"
        "    [[10, 'Nhẹ nhàng · 10 phút/ngày (Đạt mốc tối thiểu)'], [20, 'Vừa phải · 20 phút/ngày (Khuyên dùng)'], [30, 'Chuyên sâu · 30 phút/ngày (Tiến bộ nhanh)']].map(([v, l]) => h('option', { value: v, selected: (S.goal || 20) === v }, l)));\n"
        "  const smartSchedCheck = h('input', { type: 'checkbox', id: 'smartSched', checked: S.smartSchedule !== false, onchange: (e) => { S.smartSchedule = e.target.checked; save(); toast('Đã cập nhật chế độ lộ trình.'); progressView(); } });\n"
        "  let confirmReset = false;\n"
        "  const resetBtn = h('button', { class: 'ghost block', onclick: async () => {\n"
        "    if (!confirmReset) { confirmReset = true; resetBtn.textContent = 'Bấm lần nữa để xóa toàn bộ tiến độ học Tiếng Trung'; return; }\n"
        "    const resetTime = Date.now();\n"
        "    S = fresh();\n"
        "    S.delAll = resetTime;\n"
        "    S.t = resetTime;\n"
        "    save();\n"
        "    await pushGhSync(true);\n"
        "    toast('Đã xóa toàn bộ tiến độ và cập nhật lên máy chủ.');\n"
        "    welcomeView();\n"
        "  } }, 'Xóa tiến độ và học lại từ đầu');\n"
        "  const c0 = S.lang, k0 = Object.keys(S.srs).filter((k) => k.startsWith(c0 + ':'));\n"
        "  const xpTotal = (c) => Object.values(S.dl || {}).reduce((a, m) => a + (m[c] || 0), 0);\n"
        "  const w0 = Object.keys(S.written).filter((k) => k.startsWith(c0 + ':')).length;\n"
        "  const ob = S.onboarding;\n"
        "  mount(h('div', { class: 'stack-lg' },\n"
        "    h('div', { class: 'row between', style: { alignItems: 'center' } },\n"
        "      h('h1', {}, 'Tiến độ'),\n"
        "      h('div', { class: 'row', style: { gap: '6px', alignItems: 'center' } }, syncButton(), feedbackBtn({ mode: 'progress' }), langSwitch())\n"
        "    ),\n"
        "    h('div', { class: 'stats' },\n"
        "      h('div', { class: 'stat' }, h('b', {}, streak(c0)), h('span', {}, 'chuỗi ngày · dài nhất ' + longest(c0))),\n"
        "      h('div', { class: 'stat' }, h('b', {}, xpOf(t, c0) + '/' + goal() + 'p'), h('span', {}, 'phút hôm nay')),\n"
        "      h('div', { class: 'stat' }, h('b', {}, xpTotal(c0) + 'p'), h('span', {}, 'tổng thời gian học'))),\n"
        "    h('div', { class: 'stats' },\n"
        "      h('div', { class: 'stat' }, h('b', {}, Object.keys(S.lessons).filter((k) => k.startsWith(c0 + ':')).length), h('span', {}, 'bài đã học')),\n"
        "      h('div', { class: 'stat' }, h('b', {}, k0.length), h('span', {}, 'mục đang ôn')),\n"
        "      h('div', { class: 'stat' }, h('b', {}, LANGS[c0].cjk ? w0 : k0.filter((k) => S.srs[k].b >= 3).length), h('span', {}, LANGS[c0].cjk ? 'chữ đã viết' : 'đã nhớ chắc'))),\n"
        "    h('div', { class: 'panel stack' }, h('h3', {}, 'Phút học ' + L().short + ' 7 ngày qua'),\n"
        "      h('div', { class: 'week', role: 'img', 'aria-label': days.map((d) => wd[dayDate(d).getUTCDay()] + ': ' + xd(d) + ' phút').join(', ') },\n"
        "        days.map((d) => h('div', { class: d === t ? 'today' : '' }, h('span', {}, xd(d) ? (xd(d) + 'p') : ''), h('i', { style: { height: (xd(d) / max * 100) + '%' } }), h('span', {}, wd[dayDate(d).getUTCDay()]))))),\n",
        label="progressView minutes & header",
    )
    html = replace_exact(
        html,
        "    accordionItem({\n"
        "      cls: 'acc-card',\n"
        "      iconEl: '⚙️',\n"
        "      title: 'Cài đặt lộ trình thông minh & Mục tiêu',\n"
        "      subtitle: (S.smartSchedule !== false ? 'Đang bật theo thứ · ' : 'Đang tắt · ') + 'Mục tiêu cơ bản ' + (S.goal || 20) + ' XP/ngày',\n"
        "      chips: [h('span', { class: 'chip small' }, (S.goal || 20) + ' XP')],\n"
        "      body: [\n"
        "        h('label', { class: 'row', style: { alignItems: 'center', gap: '8px', cursor: 'pointer', fontWeight: 600 } }, smartSchedCheck, h('span', {}, 'Bật lộ trình học theo thứ trong tuần (chống loạn ngôn ngữ)')),\n"
        "        h('p', { class: 'small muted', style: { margin: 0 } }, 'Tự động tăng mục tiêu XP cho ngôn ngữ trọng tâm trong ngày và giảm nhẹ cho các ngôn ngữ duy trì (kèm nhắc nhở Spaced Repetition).'),\n"
        "        h('label', { for: 'goal', class: 'label', style: { marginTop: '4px' } }, 'Mức độ mục tiêu cơ bản'), goalSel,\n"
        "        h('p', { class: 'small muted', style: { margin: 0 } }, 'Mỗi từ, kanji, câu hoặc tình huống làm đúng được 5 XP. Học lại bài cũ được nửa XP.'),\n"
        "        h('p', { class: 'small muted', style: { margin: 0 } }, 'Thêm vào màn hình chính trên iPhone: mở link bằng Safari, bấm Chia sẻ, chọn “Thêm vào MH chính”.')\n"
        "      ]\n"
        "    }),",
        "    accordionItem({\n"
        "      cls: 'acc-card',\n"
        "      iconEl: '⚙️',\n"
        "      title: 'Cài đặt lộ trình & Khảo sát trình độ',\n"
        "      subtitle: 'Mục tiêu ' + (S.goal || 20) + ' phút/ngày' + (ob && ob.done ? (' · Trình độ ' + (ob.level || 'hsk1').toUpperCase().replace('HSK', 'HSK ')) : ''),\n"
        "      chips: [h('span', { class: 'chip small' }, (S.goal || 20) + ' phút')],\n"
        "      body: [\n"
        "        h('label', { class: 'row', style: { alignItems: 'center', gap: '8px', cursor: 'pointer', fontWeight: 600 } }, smartSchedCheck, h('span', {}, 'Bật lịch nhắc thông minh theo thứ trong tuần')),\n"
        "        h('label', { for: 'goal', class: 'label', style: { marginTop: '4px' } }, 'Thời lượng mục tiêu mỗi ngày'), goalSel,\n"
        "        h('p', { class: 'small muted', style: { margin: 0 } }, 'Hệ thống tự động tính thời gian học thực tế (ít nhất 10 phút/ngày để giữ Streak).'),\n"
        "        h('button', { class: 'ghost mini block', style: { color: 'var(--teal)', border: '1px solid var(--line)', marginTop: '4px' }, onclick: () => openOnboardingModal(true) }, '🎯 Làm lại khảo sát trình độ & mục tiêu'),\n"
        "        h('p', { class: 'small muted', style: { margin: 0 } }, 'Thêm vào màn hình chính trên iPhone: mở link bằng Safari, bấm Chia sẻ, chọn “Thêm vào MH chính”.')\n"
        "      ]\n"
        "    }),",
        label="progressView settings accordion",
    )
    html = replace_exact(
        html,
        "const reloadKey = 'lingogo_reload_' + data.build;",
        "const reloadKey = 'zh_reload_' + data.build;",
        label="checkAppUpdate reloadKey",
    )

    DST_HTML.write_text(html, encoding="utf-8")
    print(f"Generated {DST_HTML} ({len(html.encode('utf-8')):,} bytes, build {build_id}, v{app_ver})")


if __name__ == "__main__":
    main()
