"""
convert.py - MD presentation to HTML converter
"""
import pathlib, re, json, csv as csv_mod, io, argparse, os

# ── Constants ─────────────────────────────────────────────────────────────────

SLIDE_SIZES = {
    "16:9": (1280, 720),
    "4:3":  (1024, 768),
}

HIGHLIGHT_MAP = {
    "professional-dark":   "github-dark",
    "professional-light":  "github",
    "creative-gradient":   "atom-one-dark",
    "minimal-clean":       "default",
    "warm-earth":          "base16/solarized-light",
}

CONTENT_PADDING = "28px 48px 24px 48px"

# ── Asset CDN URLs ─────────────────────────────────────────────────────────────
# bootcdn.cn — 在中国大陆比 jsdelivr/cdnjs 更稳定
ASSET_URLS = {
    "chartjs":  "https://cdn.bootcdn.net/ajax/libs/Chart.js/4.4.1/chart.umd.min.js",
    "hljs_js":  "https://cdn.bootcdn.net/ajax/libs/highlight.js/11.9.0/highlight.min.js",
    "hljs_css": "https://cdn.bootcdn.net/ajax/libs/highlight.js/11.9.0/styles/{theme}.min.css",
}

CHARTJS_TYPE_MAP = {    "bar":            "bar",
    "bar-horizontal": "bar",
    "line":           "line",
    "area":           "line",
    "pie":            "pie",
    "donut":          "doughnut",
    "scatter":        "scatter",
    "table":          None,
}

# ── Slide JS (embedded) ───────────────────────────────────────────────────────

SLIDE_JS = r"""const slides = document.querySelectorAll('.slide');
const total = slides.length;
let current = 0;

document.getElementById('tot-pages').textContent = total;

function goTo(n) {
  if (n < 0 || n >= total) return;
  slides[current].classList.remove('active');
  current = n;
  slides[current].classList.add('active');
  document.getElementById('cur-page').textContent = current + 1;
  document.getElementById('progress-bar').style.width =
    ((current + 1) / total * 100) + '%';
}

function nextSlide() { goTo(current + 1); }
function prevSlide() { goTo(current - 1); }

document.addEventListener('keydown', (e) => {
  const next = ['ArrowRight', 'ArrowDown', ' ', 'PageDown', 'Enter'];
  const prev = ['ArrowLeft', 'ArrowUp', 'PageUp'];
  if (next.includes(e.key)) { e.preventDefault(); nextSlide(); }
  else if (prev.includes(e.key)) { e.preventDefault(); prevSlide(); }
});

let touchStartX = 0;
document.addEventListener('touchstart', e => { touchStartX = e.touches[0].clientX; });
document.addEventListener('touchend', e => {
  const dx = e.changedTouches[0].clientX - touchStartX;
  if (Math.abs(dx) > 50) { dx < 0 ? nextSlide() : prevSlide(); }
});

function scalePresentation() {
  const slideW = SLIDE_W_PLACEHOLDER, slideH = SLIDE_H_PLACEHOLDER;
  const scaleX = window.innerWidth / slideW;
  const scaleY = window.innerHeight / slideH;
  const scale = Math.min(scaleX, scaleY);
  document.getElementById('presentation').style.transform = 'scale(' + scale + ')';
}
window.addEventListener('resize', scalePresentation);
scalePresentation();
goTo(0);

// 溢出检测：调整内容密度以防止文字溢出
// 注意：使用 scrollHeight vs clientHeight，而非累加 offsetHeight（flex gap 不计入子元素高度）
// 注意：不用 getBoundingClientRect（CSS scale 后坐标为视觉坐标，不可靠）
function adjustSlideSpacing() {
  slides.forEach(function(slide) {
    var content = slide.querySelector('.slide-content');
    if (!content) return;
    var wasActive = slide.classList.contains('active');
    // 对非激活幻灯片：临时显示（visibility:hidden 不占视觉空间但可测量）
    if (!wasActive) {
      slide.style.display = 'flex';
      slide.style.visibility = 'hidden';
      void content.offsetHeight; // 强制 reflow，确保 scrollHeight 准确
    }
    var overflow = content.scrollHeight - content.clientHeight;
    if (overflow > 8) { // 8px 安全边距
      if (content.classList.contains('density-spacious')) {
        content.classList.remove('density-spacious');
        content.classList.add('density-normal');
      } else if (content.classList.contains('density-normal')) {
        content.classList.remove('density-normal');
        content.classList.add('density-compact');
      }
    }
    if (!wasActive) {
      slide.style.display = '';
      slide.style.visibility = '';
    }
  });
}
// 初始渲染后执行一次（延迟 150ms 等待字体加载）
setTimeout(adjustSlideSpacing, 150);"""

# ── Layout CSS (embedded) ─────────────────────────────────────────────────────

LAYOUT_CSS = """\
/* === 内容区基础 === */
.slide-content {
  flex: 1; min-height: 0; display: flex; flex-direction: column;
  padding: 0.15em 0; gap: 0.45em; overflow: hidden;
}
.slide h1 { margin-bottom: 0.25em; }

/* === 布局系统 (min-height:0 防止 flex 子元素高度膨胀) === */
.layout-split {
  flex: 1; min-height: 0; display: flex; flex-direction: row;
  gap: 3%; align-items: stretch; overflow: hidden;
}
.text-panel  { min-height: 0; display: flex; flex-direction: column; gap: 0.4em; overflow: hidden; }
.chart-panel { min-height: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; overflow: hidden; }
.chart-panel canvas { flex: 1; min-height: 0; width: 100%; }
.chart-title {
  font-size: 0.72em; text-align: center; opacity: 0.65;
  margin-bottom: 0.25em; letter-spacing: 0.04em; text-transform: uppercase;
}
.layout-full-chart {
  flex: 1; min-height: 0; display: flex; flex-direction: column; align-items: center; overflow: hidden;
}
.layout-full-chart canvas { flex: 1; min-height: 0; width: 92%; max-height: 80%; }
.layout-stacked { flex: 1; min-height: 0; display: flex; flex-direction: column; gap: 0.5em; overflow: hidden; }

/* === 内容密度自适应 === */
.density-spacious { gap: 0.9em !important; }
.density-spacious li { line-height: 1.95; }
.density-normal   { gap: 0.42em; }
.density-normal   li { line-height: 1.75; }
.density-compact  { gap: 0.15em !important; font-size: 0.9em; }
.density-compact  li { line-height: 1.45; }

/* === 封面页 === */
.slide[data-type="cover"] .slide-content {
  justify-content: center; align-items: center; text-align: center; gap: 0;
}
.slide[data-type="cover"] h1 {
  font-size: 3.0em;
  font-weight: 900;
  border-bottom: none;
  margin-bottom: 0.18em;
  letter-spacing: -0.03em;
  line-height: 1.1;
}
.slide[data-type="cover"] h2 {
  font-size: 1.15em;
  font-style: normal;
  opacity: 0.65;
  margin-top: 0.5em;
  font-weight: 300;
  letter-spacing: 0.12em;
}
/* 封面底部渐变装饰线 */
.slide[data-type="cover"]::after {
  content: "";
  position: absolute;
  left: 48px; bottom: 44px;
  width: 96px; height: 4px;
  background: linear-gradient(to right, var(--accent-color), transparent);
  border-radius: 2px;
}

/* === 结语页 === */
.slide[data-type="outro"] .slide-content {
  justify-content: center; align-items: center; text-align: center;
}
.slide[data-type="outro"] h1 {
  font-size: 2.6em;
  border-bottom: none;
  font-weight: 900;
  letter-spacing: -0.02em;
}
.slide[data-type="outro"] p {
  font-size: 0.9em; opacity: 0.65; margin-top: 0.6em; letter-spacing: 0.08em;
}

/* === 内容页：列表增强 === */
.slide[data-type="content"] ul,
.slide[data-type="content"] ol,
.slide[data-type="data"]    ul,
.slide[data-type="data"]    ol {
  list-style: none;
  padding-left: 0;
}
.slide[data-type="content"] li,
.slide[data-type="data"]    li {
  padding: 0.22em 0.5em 0.22em 1.5em;
  position: relative;
  border-radius: 4px;
  transition: background 0.15s;
}
/* 交替行淡底色 */
.slide[data-type="content"] li:nth-child(even),
.slide[data-type="data"]    li:nth-child(even) {
  background: var(--list-stripe-bg, rgba(128,128,128,0.05));
}
/* 左侧装饰竖线 (4px, accent色) */
.slide[data-type="content"] li::before,
.slide[data-type="data"]    li::before {
  content: "";
  position: absolute;
  left: 0; top: 0.22em; bottom: 0.22em;
  width: 3px;
  background: var(--accent-color);
  border-radius: 2px;
  opacity: 0.7;
}
/* 右侧 emoji 图标包装 */
.slide li .li-icon {
  display: inline-block;
  margin-right: 0.35em;
  font-style: normal;
}
/* 关键数字放大 */
.slide .key-number {
  font-size: 1.35em;
  font-weight: 800;
  color: var(--accent-color);
  letter-spacing: -0.02em;
  line-height: 1;
}
/* 重点高亮 */
.slide mark.hl {
  background: var(--accent-color);
  color: var(--slide-bg, #fff);
  padding: 0.05em 0.3em;
  border-radius: 3px;
  font-weight: 700;
  font-style: normal;
}

/* === 目录页：编号圆圈 === */
.slide[data-type="toc"] ul,
.slide[data-type="toc"] ol {
  list-style: none; padding-left: 0; counter-reset: toc-counter;
}
.slide[data-type="toc"] li {
  display: flex; align-items: center;
  padding: 0.3em 0;
  border-bottom: 1px solid var(--table-border, rgba(128,128,128,0.15));
  font-size: 1.02em;
  counter-increment: toc-counter;
}
.slide[data-type="toc"] li::before {
  content: counter(toc-counter, decimal-leading-zero);
  flex-shrink: 0;
  width: 2em; height: 2em;
  display: flex; align-items: center; justify-content: center;
  border-radius: 50%;
  background: var(--accent-color);
  color: #fff;
  font-size: 0.72em;
  font-weight: 700;
  margin-right: 0.7em;
  opacity: 0.88;
}

/* === blockquote：左色块引用 === */
.slide blockquote {
  border-left: 4px solid var(--accent-color);
  background: var(--list-stripe-bg, rgba(128,128,128,0.07));
  padding: 0.5em 0.9em;
  border-radius: 0 6px 6px 0;
  font-style: italic;
  opacity: 0.9;
  margin: 0.2em 0;
}
.slide blockquote p { margin: 0; }

/* === hr：渐变装饰线 === */
.slide hr {
  border: none;
  height: 2px;
  background: linear-gradient(to right, var(--accent-color), transparent);
  margin: 0.5em 0;
  border-radius: 1px;
}

/* === strong/em === */
.slide strong { color: var(--accent-color); font-weight: 700; }
.slide em { opacity: 0.85; }

/* === 通用元素 === */
.slide ul, .slide ol { padding-left: 1.2em; line-height: 1.75; }
.slide li { margin-bottom: 0.15em; }
.slide pre {
  border-radius: 8px; padding: 0.75em 1em; font-size: 0.78em;
  overflow-x: auto; background: var(--code-bg);
  border: 1px solid var(--table-border, rgba(128,128,128,0.15));
}
.slide table { width: 100%; border-collapse: collapse; font-size: 0.8em; }
.slide th, .slide td {
  padding: 0.45em 0.9em; border: 1px solid var(--table-border); text-align: center;
}
.slide th {
  background: var(--table-header-bg); font-weight: 700;
  letter-spacing: 0.03em; text-transform: uppercase; font-size: 0.88em;
}
.slide tr:nth-child(even) { background: var(--table-row-even-bg); }
.slide .data-table-wrap { flex: 1; overflow: auto; }

/* === 图片 === */
.slide-content img {
  max-width: 100%;
  height: auto;
  display: block;
  flex-shrink: 1;
}

/* === 版式：text-hero（大字留白） === */
.layout-hero { justify-content: center; }
.layout-hero > h1 { font-size: 2.6em; }
.layout-hero > ul, .layout-hero > ol { font-size: 1.15em; }
.layout-hero > p { font-size: 1.1em; opacity: 0.85; }

/* === 版式：text-two-column === */
.col-wrap {
  flex: 1; min-height: 0; display: flex; flex-direction: row;
  gap: 3%; overflow: hidden;
}
.col-wrap .col {
  flex: 1; min-height: 0; display: flex; flex-direction: column;
  gap: 0.4em; overflow: hidden;
}

/* === 版式：text-three-column === */
.col-wrap-3 {
  flex: 1; min-height: 0; display: flex; flex-direction: row;
  gap: 2%; overflow: hidden;
}
.col-wrap-3 .col {
  flex: 1; min-height: 0; display: flex; flex-direction: column;
  gap: 0.35em; overflow: hidden;
}
.col-wrap-3 .col h3 {
  color: var(--accent-color); font-size: 0.9em; letter-spacing: 0.04em;
  padding-bottom: 0.25em; border-bottom: 2px solid var(--accent-color);
  margin-bottom: 0.3em;
}

/* === 版式：statement（单句声明） === */
.layout-statement { justify-content: center; align-items: center; text-align: center; }
.layout-statement .stmt-text {
  font-size: 2.0em; font-weight: 700; line-height: 1.4;
  max-width: 80%; color: var(--accent-color);
}
.layout-statement .stmt-sub { font-size: 0.9em; opacity: 0.65; margin-top: 0.6em; }

/* === 版式：quote-center === */
.layout-quote-center { justify-content: center; align-items: center; text-align: center; }
.layout-quote-center blockquote {
  font-size: 1.45em; border-left: none; background: none;
  font-style: italic; max-width: 78%;
  border-top: 3px solid var(--accent-color);
  border-bottom: 3px solid var(--accent-color);
  padding: 0.65em 1.2em; opacity: 1;
}

/* === 版式：quote-side === */
.layout-quote-side {
  flex: 1; min-height: 0; display: flex; flex-direction: row;
  gap: 4%; align-items: center; overflow: hidden;
}
.layout-quote-side .quote-zone { flex: 0 0 50%; min-height: 0; }
.layout-quote-side .quote-zone blockquote { font-size: 1.2em; }
.layout-quote-side .text-zone {
  flex: 1; min-height: 0; display: flex; flex-direction: column; gap: 0.4em;
}

/* === 版式：image-right / image-left === */
.image-split {
  flex: 1; min-height: 0; display: flex; flex-direction: row;
  gap: 3%; align-items: center; overflow: hidden;
}
.image-split .img-panel {
  min-height: 0; display: flex; align-items: center; justify-content: center;
  overflow: hidden; flex-shrink: 0;
}
.image-split .img-panel img { max-width: 100%; max-height: 100%; object-fit: contain; display: block; }
.image-split .text-zone { min-height: 0; display: flex; flex-direction: column; gap: 0.4em; overflow: hidden; flex: 1; }

/* === 版式：image-top / image-bottom === */
.image-stack {
  flex: 1; min-height: 0; display: flex; flex-direction: column;
  gap: 3%; overflow: hidden;
}
.image-stack .img-zone {
  display: flex; align-items: center; justify-content: center; overflow: hidden; flex-shrink: 0;
}
.image-stack .img-zone img { max-width: 100%; max-height: 100%; object-fit: contain; display: block; }
.image-stack .text-zone { min-height: 0; display: flex; flex-direction: column; gap: 0.4em; overflow: hidden; flex: 1; }

/* === 版式：image-fullbleed === */
.slide.layout-fullbleed { background-size: cover; background-position: center; }
.slide.layout-fullbleed::before {
  content: ""; position: absolute; inset: 0; background: rgba(0,0,0,0.45); z-index: 0;
}
.layout-fullbleed-text {
  position: relative; z-index: 1; justify-content: flex-end; padding-bottom: 1em;
}
.layout-fullbleed-text h1 { color: #fff !important; text-shadow: 0 2px 8px rgba(0,0,0,0.6); }
.layout-fullbleed-text p, .layout-fullbleed-text li { color: rgba(255,255,255,0.88) !important; }

/* === 版式：image-only === */
.layout-image-only {
  flex: 1; min-height: 0; position: relative; display: flex;
  align-items: center; justify-content: center; overflow: hidden;
}
.layout-image-only img { max-width: 100%; max-height: 100%; object-fit: contain; display: block; }
.layout-image-only .img-caption {
  position: absolute; bottom: 0.6em; left: 0; right: 0;
  text-align: center; font-size: 0.72em; opacity: 0.65;
}

/* === 版式：stat-cards === */
.stat-grid {
  flex: 1; min-height: 0;
  display: grid;
  grid-template-columns: repeat(var(--stat-cols, 4), 1fr);
  gap: 1.2em 2%;
  align-content: center;
  overflow: hidden;
}
.stat-card {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  background: var(--list-stripe-bg, rgba(128,128,128,0.08));
  border-radius: 10px; padding: 0.75em 0.5em;
  border: 1px solid var(--table-border, rgba(128,128,128,0.15)); gap: 0.25em;
}
.stat-card .s-num { font-size: 2.0em; font-weight: 800; color: var(--accent-color); line-height: 1; }
.stat-card .s-lbl { font-size: 0.7em; opacity: 0.7; text-align: center; line-height: 1.3; }

/* === 版式：card-grid === */
.card-grid {
  flex: 1; min-height: 0;
  display: grid;
  grid-template-columns: repeat(var(--card-cols, 3), 1fr);
  gap: 1em;
  align-content: center;
  overflow: hidden;
}
.card-grid-item {
  background: var(--list-stripe-bg, rgba(128,128,128,0.08));
  border-radius: 10px; padding: 1em 1.2em;
  border: 1px solid var(--table-border, rgba(128,128,128,0.15));
  display: flex; flex-direction: column; gap: 0.3em;
}
.card-grid-item .cg-title {
  font-weight: 700; color: var(--accent-color);
  font-size: 0.9em; line-height: 1.2;
}
.card-grid-item .cg-body { font-size: 0.78em; opacity: 0.8; line-height: 1.45; }

/* === 版式：timeline-vertical === */
.tl-v-list { list-style: none; padding: 0; display: flex; flex-direction: column; gap: 0.5em; }
.tl-v-list > li {
  display: flex; align-items: flex-start; gap: 0.8em;
  padding: 0 !important; background: none !important;
}
.tl-v-list > li::before { display: none !important; }
.tl-v-num {
  flex-shrink: 0; width: 2em; height: 2em;
  display: flex; align-items: center; justify-content: center;
  border-radius: 50%; background: var(--accent-color);
  color: #fff; font-size: 0.78em; font-weight: 700;
}
.tl-v-content { flex: 1; padding-top: 0.25em; }

/* === 版式：timeline-horizontal === */
.tl-h-wrap { flex: 1; min-height: 0; display: flex; align-items: center; overflow: hidden; }
.tl-h-list {
  list-style: none; padding: 0; margin: 0;
  display: flex; flex-direction: row; width: 100%; align-items: flex-start;
}
.tl-h-list > li {
  flex: 1; display: flex; flex-direction: column; align-items: center;
  position: relative; padding: 0 0.4em !important; background: none !important;
}
.tl-h-list > li::before { display: none !important; }
.tl-h-list > li::after {
  content: ""; position: absolute; top: 0.9em; left: 50%; right: -50%;
  height: 2px; background: var(--accent-color); opacity: 0.35; z-index: 0;
}
.tl-h-list > li:last-child::after { display: none; }
.tl-h-dot {
  width: 1.8em; height: 1.8em; border-radius: 50%;
  background: var(--accent-color); color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.72em; font-weight: 700; margin-bottom: 0.4em;
  position: relative; z-index: 1; flex-shrink: 0;
}
.tl-h-text { font-size: 0.75em; text-align: center; line-height: 1.35; }

/* === 版式：compare-two / compare-three === */
.compare-wrap {
  flex: 1; min-height: 0; display: flex; flex-direction: row;
  overflow: hidden;
}
.compare-col {
  flex: 1; min-height: 0; display: flex; flex-direction: column;
  padding: 0 1.2em; overflow: hidden; gap: 0.4em;
}
.compare-col + .compare-col {
  border-left: 1px solid var(--table-border, rgba(128,128,128,0.2));
}
.compare-col > h3 {
  color: var(--accent-color); font-size: 0.9em; text-transform: uppercase;
  letter-spacing: 0.06em; margin-bottom: 0.3em; padding-bottom: 0.25em;
  border-bottom: 2px solid var(--accent-color);
}

/* === 版式：cover-image-bg === */
.slide.cover-image-bg { background-size: cover; background-position: center; }
.slide.cover-image-bg::before {
  content: ""; position: absolute; inset: 0; background: rgba(0,0,0,0.5); z-index: 0;
}
.cover-image-bg .slide-content {
  position: relative; z-index: 1;
  justify-content: center; align-items: center; text-align: center;
}
.cover-image-bg h1 { color: #fff !important; }
.cover-image-bg h2 { color: rgba(255,255,255,0.8) !important; }

/* === 版式：cover-split === */
.cover-split-wrap {
  flex: 1; min-height: 0; display: flex; flex-direction: row; overflow: hidden;
}
.cover-split-text {
  flex: 0 0 55%; display: flex; flex-direction: column;
  justify-content: center; padding-right: 4%; overflow: hidden;
}
.cover-split-img {
  flex: 1; min-height: 0; display: flex; align-items: center;
  justify-content: center; overflow: hidden;
}
.cover-split-img img { max-width: 100%; max-height: 100%; object-fit: cover; border-radius: 8px; }

/* === 版式：section-header（居中变体，≤4个章节）=== */
.layout-section-centered {
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  text-align: center; height: 100%; gap: 0;
}
.layout-section-centered .section-eyebrow { margin-bottom: 0.5em; }
.layout-section-centered .section-main { font-size: 3em; }
.layout-section-centered .section-sub { max-width: 70%; }
.section-dots {
  display: flex; gap: 0.7em; margin-top: 1.4em; align-items: center;
}
.section-dot {
  width: 0.45em; height: 0.45em; border-radius: 50%;
  background: var(--accent-color); opacity: 0.22; transition: all 0.2s;
}
.section-dot.active {
  opacity: 1; width: 0.6em; height: 0.6em;
}

/* === 版式：section-header（TOC变体，≥5个章节）=== */
.layout-section-toc {
  display: flex; flex-direction: row; height: 100%;
}
.section-toc-left {
  flex: 0 0 52%; display: flex; flex-direction: column;
  justify-content: center; padding-right: 6%;
  border-right: 2px solid var(--accent-color);
}
.section-toc-right {
  flex: 1; display: flex; flex-direction: column;
  justify-content: center; padding-left: 6%;
  gap: 0.55em; min-height: 0; overflow: hidden;
}
.toc-item {
  display: flex; align-items: center; gap: 0.55em;
  font-size: 0.82em; opacity: 0.35; line-height: 1.2;
  transition: opacity 0.2s;
}
.toc-item.toc-done { opacity: 0.55; }
.toc-item.toc-active {
  opacity: 1; font-weight: 700; color: var(--accent-color); font-size: 0.9em;
}
.toc-bullet {
  flex-shrink: 0; width: 0.42em; height: 0.42em;
  border-radius: 50%; background: currentColor;
}
.toc-item.toc-active .toc-bullet { width: 0.55em; height: 0.55em; }

/* shared section text */
.section-eyebrow {
  font-size: 0.78em; letter-spacing: 0.18em; opacity: 0.45;
  text-transform: uppercase; margin-bottom: 0.3em;
}
.section-main { font-size: 2.6em; font-weight: 800; color: var(--accent-color); line-height: 1.1; }
.section-sub { font-size: 0.9em; opacity: 0.65; margin-top: 0.5em; }

/* === 版式：table-full === */
.layout-table-full { flex: 1; min-height: 0; overflow: auto; }
.layout-table-full table { font-size: 0.85em; }
"""

# ── Helpers ───────────────────────────────────────────────────────────────────

def _base_dir() -> pathlib.Path:
    return pathlib.Path(__file__).parent.parent


def _fetch_url(url: str, timeout: int = 20) -> str:
    """Download URL as UTF-8 text."""
    import urllib.request
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return r.read().decode("utf-8")


def _load_asset(url: str, cache_name: str) -> str | None:
    """Return asset content from local cache or download from URL.
    Cache lives in md2slides/assets/. Returns None on failure.
    """
    cache_path = _base_dir() / "assets" / cache_name
    if cache_path.exists():
        return cache_path.read_text(encoding="utf-8")
    cache_path.parent.mkdir(exist_ok=True)
    try:
        print(f"  Downloading {cache_name} ...")
        content = _fetch_url(url)
        cache_path.write_text(content, encoding="utf-8")
        return content
    except Exception as e:
        print(f"Warning: failed to download {url}: {e}")
        return None


VALID_THEMES = {"professional-dark", "professional-light", "creative-gradient", "minimal-clean", "warm-earth"}

def load_theme_css(theme: str) -> str:
    p = _base_dir() / "references" / "themes" / f"{theme}.css"
    if not p.exists():
        valid = ", ".join(sorted(VALID_THEMES))
        print(f"Warning: unknown theme '{theme}', falling back to 'professional-dark'. Valid themes: {valid}")
        p = _base_dir() / "references" / "themes" / "professional-dark.css"
    return p.read_text(encoding="utf-8") if p.exists() else ""


def load_chart_defaults(theme: str) -> dict:
    p = _base_dir() / "references" / "chart-defaults.json"
    if p.exists():
        data = json.loads(p.read_text(encoding="utf-8"))
        return data.get(theme, data.get("professional-dark", {}))
    return {"colors": ["#4a90d9"], "gridColor": "rgba(128,128,128,0.15)", "textColor": "#aaa"}


def hex_to_rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return f"rgba({r},{g},{b},{alpha})"


# ── MD Parsing ────────────────────────────────────────────────────────────────

def parse_md(filepath: pathlib.Path) -> tuple[dict, list[str]]:
    import frontmatter as fm
    # Read with explicit UTF-8 (utf-8-sig handles BOM); fallback to GBK for
    # files saved by Chinese Windows editors.
    try:
        text = filepath.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        text = filepath.read_text(encoding="gbk")
        print(f"Warning: {filepath.name} is not UTF-8, decoded as GBK")
    post = fm.loads(text)
    meta = dict(post.metadata)

    # YAML parses "16:9" as sexagesimal integer; fix it back
    ratio = meta.get("ratio")
    if isinstance(ratio, int):
        for key in SLIDE_SIZES:
            h, m = map(int, key.split(":"))
            if h * 60 + m == ratio:
                meta["ratio"] = key
                break

    raw_slides = re.split(r"(?m)^---\s*$", post.content)
    return meta, [s.strip() for s in raw_slides if s.strip()]


def parse_chart_block(comment_text: str) -> dict:
    """Parse <!-- chart ... --> content into a params dict."""
    params: dict = {}
    for line in comment_text.splitlines():
        line = line.strip()
        if ":" in line:
            key, _, val = line.partition(":")
            params[key.strip()] = val.strip()
    # boolean coercion
    if "legend" in params:
        params["legend"] = params["legend"].lower() not in ("false", "0", "no")
    return params


def extract_chart_blocks(slide_content: str) -> tuple[list[dict], str]:
    """Extract all <!-- chart ... --> blocks, return (list_of_params, content_without_charts)."""
    charts = []
    def collect(m):
        charts.append(parse_chart_block(m.group(1)))
        return ""
    clean = re.sub(r"<!--\s*chart\s*([\s\S]*?)-->", collect, slide_content)
    return charts, clean.strip()


# ── Image path fixing ─────────────────────────────────────────────────────────

def fix_image_paths(html: str, md_dir: pathlib.Path, output_dir: pathlib.Path) -> str:
    """Rewrite relative <img src> paths to be relative to the output HTML directory.

    Skips http/https URLs, data URIs, and absolute paths.
    If md_dir == output_dir (same directory), returns html unchanged.
    """
    if md_dir.resolve() == output_dir.resolve():
        return html

    def _rewrite(m):
        full_tag, src = m.group(0), m.group(1)
        if re.match(r'^(https?://|//|data:|/)', src):
            return full_tag
        abs_path = (md_dir / src).resolve()
        if not abs_path.exists():
            print(f"Warning: image not found: {abs_path}")
            return full_tag
        new_src = pathlib.Path(os.path.relpath(abs_path, output_dir.resolve())).as_posix()
        return full_tag.replace(f'"{src}"', f'"{new_src}"', 1)

    return re.sub(r'<img\b[^>]*\bsrc="([^"]*)"', _rewrite, html)


# ── CSV Reading ───────────────────────────────────────────────────────────────

def read_csv(filepath: pathlib.Path) -> list[dict]:
    if filepath is None or not filepath.exists():
        if filepath is not None:
            print(f"Warning: CSV not found: {filepath}")
        return []
    with open(filepath, encoding="utf-8", newline="") as f:
        return list(csv_mod.DictReader(f))


def find_csv_field(rows: list[dict], field: str) -> str:
    """Fuzzy-match a field name against CSV headers.
    Tries: exact → strip whitespace → case-insensitive → warn & return original.
    """
    if not rows or not field:
        return field
    headers = list(rows[0].keys())
    if field in headers:
        return field
    field_s = field.strip()
    for h in headers:
        if h.strip() == field_s:
            return h
    field_lower = field_s.lower()
    for h in headers:
        if h.strip().lower() == field_lower:
            print(f"Warning: xField/yField '{field}' matched '{h}' (case-insensitive). "
                  "Consider updating your MD to match exactly.")
            return h
    print(f"Warning: field '{field}' not found in CSV. Available: {headers}")
    return field


# ── Chart JS generation ───────────────────────────────────────────────────────

def build_chart_config(chart_params: dict, csv_data: list[dict], chart_defaults: dict) -> dict:
    chart_type = chart_params.get("type", "bar")
    x_field    = find_csv_field(csv_data, chart_params.get("xField", ""))
    y_fields   = [find_csv_field(csv_data, f.strip())
                  for f in chart_params.get("yField", "").split(",") if f.strip()]
    theme_colors = chart_defaults.get("colors", ["#4a90d9"])

    labels = [row.get(x_field, "") for row in csv_data]

    datasets = []
    for i, yf in enumerate(y_fields):
        color = theme_colors[i % len(theme_colors)]
        values = []
        for row in csv_data:
            v = row.get(yf, "0")
            try:
                values.append(float(v))
            except ValueError:
                values.append(0.0)

        ds: dict = {"label": yf, "data": values}
        if chart_type in ("line", "area"):
            ds["borderColor"]     = color
            ds["backgroundColor"] = hex_to_rgba(color, 0.2)
            ds["tension"]         = 0.4
            ds["borderWidth"]     = 2
            ds["pointRadius"]     = 4
            if chart_type == "area":
                ds["fill"] = True
        elif chart_type in ("pie", "donut"):
            ds["backgroundColor"] = theme_colors[: len(values)]
        else:
            ds["backgroundColor"] = color

        datasets.append(ds)

    text_color = chart_defaults.get("textColor", "#aaa")
    grid_color = chart_defaults.get("gridColor", "rgba(128,128,128,0.15)")

    options: dict = {
        "responsive": True,
        "maintainAspectRatio": False,
        "animation": {"duration": 0},
        "plugins": {
            "legend": {
                "display": chart_params.get("legend", True),
                "labels": {"color": text_color},
            },
            "title": {"display": False},
        },
    }

    if chart_type not in ("pie", "donut"):
        options["scales"] = {
            "x": {"ticks": {"color": text_color}, "grid": {"color": grid_color}},
            "y": {"ticks": {"color": text_color}, "grid": {"color": grid_color}},
        }

    config: dict = {
        "type": CHARTJS_TYPE_MAP.get(chart_type, "bar"),
        "data": {"labels": labels, "datasets": datasets},
        "options": options,
    }
    if chart_type == "bar-horizontal":
        config["options"]["indexAxis"] = "y"

    return config


def render_chart_js(canvas_id: str, config: dict) -> str:
    config_json = json.dumps(config, ensure_ascii=False)
    return (
        f"(function(){{\n"
        f"  new Chart(document.getElementById('{canvas_id}'), {config_json});\n"
        f"}})();"
    )


def render_data_table(table_id: str, csv_data: list[dict]) -> str:
    if not csv_data:
        return f'<p id="{table_id}">(no data)</p>'
    headers = list(csv_data[0].keys())
    ths = "".join(f"<th>{h}</th>" for h in headers)
    rows_html = ""
    for row in csv_data:
        tds = "".join(f"<td>{row.get(h,'')}</td>" for h in headers)
        rows_html += f"<tr>{tds}</tr>\n"
    return (
        f'<div class="data-table-wrap">'
        f'<table id="{table_id}"><thead><tr>{ths}</tr></thead>'
        f"<tbody>{rows_html}</tbody></table></div>"
    )


# ── Semantic HTML enhancement ─────────────────────────────────────────────────

# Regex: standalone number with optional unit (%, 万, K, M, x, etc.)
_NUM_RE = re.compile(
    r'(?<!["\w#-])'          # not preceded by quote / word / hex / minus
    r'(\d[\d,]*\.?\d*)'      # integer or decimal, optional thousands comma
    r'(\s*(?:%|万|亿|K|M|B|x倍?|倍|px|ms|s|TB|GB|MB|KB)?)'
    r'(?![\d\w])'            # not followed by more digits / word chars
)

# Sentence-final position chars that suggest this is a prose number, not standalone data
_PROSE_CONTEXT_RE = re.compile(r'(?:第|共|约|超过|不足|小于|大于|每|至少|最多)\d')


def _wrap_key_numbers(text: str) -> str:
    """Wrap standalone numbers with <span class="key-number">."""
    if _PROSE_CONTEXT_RE.search(text):
        return text  # prose context — leave as is
    def _replacer(m):
        num, unit = m.group(1), m.group(2)
        # Skip trivially small or ordinal-looking numbers (single digit without unit)
        if not unit.strip() and len(num) <= 1:
            return m.group(0)
        return f'<span class="key-number">{num}{unit}</span>'
    return _NUM_RE.sub(_replacer, text)


def _wrap_li_icons(li_html: str) -> str:
    """Wrap leading emoji in <li> with <span class="li-icon">."""
    # Match emoji at the very start of li content (after optional whitespace)
    emoji_re = re.compile(
        r'^(\s*)'
        r'([\U0001F300-\U0001FAFF\u2600-\u26FF\u2700-\u27BF])'
        r'(\s*)',
        re.UNICODE,
    )
    return emoji_re.sub(
        lambda m: f'{m.group(1)}<span class="li-icon">{m.group(2)}</span>{m.group(3)}',
        li_html,
        count=1,
    )


def enhance_inner_html(html: str, slide_type: str) -> str:
    """Post-process inner HTML for visual enrichment.

    Applied after markdown() conversion, before ID assignment.
    1. Wrap leading emoji in <li> with .li-icon span
    2. On content/data slides: wrap key numbers with .key-number span
    """
    if slide_type not in ("content", "data"):
        return html

    # 1. Emoji icon wrapping in list items
    def _enhance_li(m: re.Match) -> str:
        attrs    = m.group(1) or ""
        li_inner = m.group(2)
        li_inner = _wrap_li_icons(li_inner)
        return f"<li{attrs}>{li_inner}</li>"

    html = re.sub(r"<li([^>]*)>([\s\S]*?)</li>", _enhance_li, html)

    # 2. Key-number wrapping — only inside <li> text nodes, not inside tags
    def _enhance_li_nums(m: re.Match) -> str:
        attrs    = m.group(1) or ""
        li_inner = m.group(2)
        # Only process text nodes (between tags), avoid double-wrapping
        def _text_nodes(s: str) -> str:
            parts = re.split(r"(<[^>]+>)", s)
            return "".join(
                _wrap_key_numbers(p) if not p.startswith("<") else p
                for p in parts
            )
        li_inner = _text_nodes(li_inner)
        return f"<li{attrs}>{li_inner}</li>"

    html = re.sub(r"<li([^>]*)>([\s\S]*?)</li>", _enhance_li_nums, html)

    return html

def detect_slide_type(content: str) -> str:
    m = re.match(r"<!--\s*Slide\s+\d+\s*:\s*([^-]+?)\s*-->", content)
    hint = m.group(1).strip().lower() if m else ""
    if any(k in hint for k in ["封面", "cover", "title"]):
        return "cover"
    if any(k in hint for k in ["目录", "toc", "agenda", "contents"]):
        return "toc"
    if any(k in hint for k in ["结语", "结尾", "closing", "thank", "谢"]):
        return "outro"
    if "<!-- chart" in content:
        return "data"
    return "content"


# ── ID assignment ─────────────────────────────────────────────────────────────

TAG_ALIAS = {
    "h1": "title", "h2": "subtitle", "h3": "h3",
    "p": "p", "ul": "list", "ol": "list",
    "pre": "code", "table": "table", "blockquote": "quote",
    "img": "img",
}

def assign_ids(html: str, slide_index: int) -> str:
    counters: dict[str, int] = {}
    def replacer(m):
        tag   = m.group(1).lower()
        attrs = m.group(2) or ""
        alias = TAG_ALIAS.get(tag, tag)
        counters[alias] = counters.get(alias, 0) + 1
        if 'id=' not in attrs:
            eid = f"s{slide_index}-{alias}{counters[alias]}"
            return f'<{tag} id="{eid}"{attrs}>'
        return m.group(0)
    return re.sub(r"<(h[1-6]|p|ul|ol|pre|table|blockquote|img)(\s[^>]*)?>",
                  replacer, html)


# ── Tree extraction ───────────────────────────────────────────────────────────

def extract_tree_elements(html: str, chart_params_list: list[dict],
                          slide_index: int) -> list[dict]:
    elements = []
    seen_ids: set[str] = set()

    for m in re.finditer(
        r'<(h[1-6]|p|ul|ol|pre|table|blockquote)\s+id="(s\d+-\w+\d*)"([^>]*)>([\s\S]*?)</\1>',
        html
    ):
        tag, eid, _, inner = m.group(1), m.group(2), m.group(3), m.group(4)
        if eid in seen_ids:
            continue
        seen_ids.add(eid)
        node: dict = {"id": eid, "type": tag}
        if tag in ("ul", "ol"):
            items = re.findall(r"<li[^>]*>([\s\S]*?)</li>", inner)
            node["items"] = [re.sub(r"<[^>]+>", "", it).strip() for it in items]
        else:
            text = re.sub(r"<[^>]+>", "", inner).strip()
            if text:
                node["content"] = text[:120]
        elements.append(node)

    for m in re.finditer(r'<img\b[^>]*\bid="(s\d+-img\d+)"[^>]*>', html):
        eid = m.group(1)
        if eid in seen_ids:
            continue
        seen_ids.add(eid)
        src_m = re.search(r'\bsrc="([^"]*)"', m.group(0))
        alt_m = re.search(r'\balt="([^"]*)"', m.group(0))
        node: dict = {
            "id":  eid,
            "type": "img",
            "src": src_m.group(1) if src_m else "",
            "alt": alt_m.group(1) if alt_m else "",
        }
        elements.append(node)

    for i, cp in enumerate(chart_params_list, start=1):
        chart_id = f"s{slide_index}-chart{i}"
        node = {
            "id": chart_id,
            "type": "chart",
            "chartType": cp.get("type", "bar"),
            "dataSource": cp.get("dataSource", "") or cp.get("dataFile", ""),
            "xField": cp.get("xField", ""),
            "yField": cp.get("yField", ""),
        }
        if cp.get("title"):
            node["title"] = cp["title"]
        if cp.get("position"):
            node["layout"] = cp["position"]
        node["style"] = {
            "width":  cp.get("width", "55%"),
            "height": cp.get("height", "65%"),
        }
        elements.append(node)

    return elements


# ── Layout helpers ────────────────────────────────────────────────────────────

def _extract_title_html(html: str) -> tuple[str, str]:
    """Extract first h1 (or h2 if no h1). Returns (title_html, rest_html)."""
    for tag in ("h1", "h2"):
        m = re.search(rf'(<{tag}[^>]*>[\s\S]*?</{tag}>)', html)
        if m:
            return m.group(1), html[:m.start()] + html[m.end():]
    return "", html


def _extract_images_html(html: str) -> tuple[list[str], str]:
    """Extract all <img> tags. Also strips wrapping <p> if it only contained an img."""
    imgs = re.findall(r'<img\b[^>]*/?>|<img\b[^>]*></img>', html)
    clean = re.sub(r'<img\b[^>]*/?>|<img\b[^>]*></img>', '', html)
    clean = re.sub(r'<p[^>]*>\s*</p>', '', clean).strip()
    return imgs, clean


def _extract_blockquote_html(html: str) -> tuple[str, str]:
    """Extract first <blockquote>. Returns (bq_html, rest_html)."""
    m = re.search(r'(<blockquote[\s\S]*?</blockquote>)', html)
    if m:
        return m.group(1), (html[:m.start()] + html[m.end():]).strip()
    return "", html


def _split_list_items(ul_html: str, n: int) -> list[str]:
    """Split <ul> or <ol> list items into n roughly equal groups. Returns list of HTML strings."""
    tag_m = re.match(r'<(ul|ol)([^>]*)>', ul_html)
    if not tag_m:
        return [ul_html] * n
    tag, attrs = tag_m.group(1), tag_m.group(2)
    items = re.findall(r'<li[\s\S]*?</li>', ul_html)
    if not items:
        return [ul_html] * n
    size = max(1, len(items) // n)
    groups = []
    for i in range(n):
        chunk = items[i*size:(i+1)*size] if i < n-1 else items[i*size:]
        groups.append(f'<{tag}{attrs}>' + ''.join(chunk) + f'</{tag}>')
    return groups


def _split_by_groups(inner_html: str, n: int) -> tuple[str, list[str]] | tuple[None, None]:
    """
    Split inner_html by p+ul groups into n columns (splitMode=group).
    Each group is an optional <p> followed by a <ul>/<ol>.
    Returns (prefix_html, [col1, col2, ...]) or (None, None) if fewer than 2 groups found.
    """
    group_pat = re.compile(r'(?:<p[^>]*>[\s\S]*?</p>\s*)?<[ou]l[\s\S]*?</[ou]l>')
    matches = list(group_pat.finditer(inner_html))
    if len(matches) < 2:
        return None, None

    prefix = inner_html[:matches[0].start()].strip()
    groups = [m.group(0) for m in matches]

    # Sequential split into n columns (round up so early columns get more)
    size = (len(groups) + n - 1) // n
    cols = []
    for i in range(n):
        chunk = groups[i * size:(i + 1) * size] if i < n - 1 else groups[i * size:]
        cols.append("".join(chunk))
    while len(cols) < n:
        cols.append("")
    return prefix, cols


def _extract_list_items_as_stats(html: str) -> list[dict]:
    """Try to extract (number, label) pairs from list items for stat-cards layout."""
    items = re.findall(r'<li[^>]*>([\s\S]*?)</li>', html)
    stats = []
    for item in items:
        num_m = re.search(r'<span class="key-number">([\s\S]*?)</span>', item)
        label = re.sub(r'<[^>]+>', '', item).strip()
        if num_m:
            num_text = re.sub(r'<[^>]+>', '', num_m.group(1)).strip()
            # Remove the number part from the label
            label = re.sub(re.escape(num_text), '', label).strip().lstrip('：:').strip()
            stats.append({"num": num_text, "label": label or "—"})
        else:
            stats.append({"num": "—", "label": label[:30]})
    return stats


def _wrap_slide_content(inner: str, extra_classes: str = "") -> str:
    cls = ("slide-content " + extra_classes).strip()
    return f'  <div class="{cls}">\n{inner}\n  </div>'


# ── Layout renderers ──────────────────────────────────────────────────────────

def _layout_text_default(cfg: dict, inner_html: str, title_html: str,
                         chart_html_parts: list, js_snippets: list, index: int) -> str:
    """Standard vertical stack (existing behavior)."""
    body = title_html + "\n" + inner_html if title_html else inner_html
    return _wrap_slide_content(body)


def _layout_text_hero(cfg: dict, inner_html: str, title_html: str,
                      chart_html_parts: list, js_snippets: list, index: int) -> str:
    body = title_html + "\n" + inner_html if title_html else inner_html
    return _wrap_slide_content(body, "layout-hero")


def _layout_statement(cfg: dict, inner_html: str, title_html: str,
                      chart_html_parts: list, js_snippets: list, index: int) -> str:
    # Use first <p> or first <li> text as the statement
    p_m = re.search(r'<p[^>]*>([\s\S]*?)</p>', inner_html)
    li_m = re.search(r'<li[^>]*>([\s\S]*?)</li>', inner_html)
    stmt_inner = ""
    if p_m:
        stmt_inner = re.sub(r'<[^>]+>', '', p_m.group(1)).strip()
    elif li_m:
        stmt_inner = re.sub(r'<[^>]+>', '', li_m.group(1)).strip()
    sub = title_html or ""
    stmt_html = f'<div class="stmt-text">{stmt_inner}</div>'
    return _wrap_slide_content(stmt_html + "\n" + sub, "layout-statement")


def _layout_text_two_column(cfg: dict, inner_html: str, title_html: str,
                             chart_html_parts: list, js_snippets: list, index: int) -> str:
    split_mode = cfg.get("splitMode", "item")

    if split_mode == "group":
        prefix, cols = _split_by_groups(inner_html, 2)
        if cols:
            cols_html = (
                f'<div class="col-wrap">'
                f'<div class="col">{cols[0]}</div>'
                f'<div class="col">{cols[1]}</div>'
                f'</div>'
            )
            body = (title_html or "") + ("\n" + prefix if prefix else "") + "\n" + cols_html
            return _wrap_slide_content(body)
        print(f"WARNING: slide-{index} splitMode=group requested but fewer than 2 p+ul groups found; "
              f"falling back to item split.")

    # item split (default): warn if multiple p+ul groups will cause stacking
    multi_groups = re.findall(r'(?:<p[^>]*>[\s\S]*?</p>\s*)?<[ou]l[\s\S]*?</[ou]l>', inner_html)
    if len(multi_groups) >= 2:
        print(f"WARNING: slide-{index} contains {len(multi_groups)} p+ul groups in two-column layout. "
              f"Only the first list will be split; remaining groups stack above. "
              f"Set splitMode=group in slide-tree.json to fix.")

    ul_m = re.search(r'<[ou]l[\s\S]*?</[ou]l>', inner_html)
    if ul_m:
        groups = _split_list_items(ul_m.group(0), 2)
        rest = inner_html[:ul_m.start()] + inner_html[ul_m.end():]
        cols_html = (
            f'<div class="col-wrap">'
            f'<div class="col">{groups[0]}</div>'
            f'<div class="col">{groups[1] if len(groups)>1 else ""}</div>'
            f'</div>'
        )
        body = (title_html or "") + "\n" + rest + "\n" + cols_html
    else:
        body = (title_html or "") + "\n" + inner_html
    return _wrap_slide_content(body)


def _layout_text_three_column(cfg: dict, inner_html: str, title_html: str,
                               chart_html_parts: list, js_snippets: list, index: int) -> str:
    split_mode = cfg.get("splitMode", "item")

    if split_mode == "group":
        prefix, cols = _split_by_groups(inner_html, 3)
        if cols:
            cols_html = (
                '<div class="col-wrap-3">'
                + "".join(f'<div class="col">{c}</div>' for c in cols)
                + '</div>'
            )
            body = (title_html or "") + ("\n" + prefix if prefix else "") + "\n" + cols_html
            return _wrap_slide_content(body)
        print(f"WARNING: slide-{index} splitMode=group requested but fewer than 2 p+ul groups found; "
              f"falling back to item split.")

    # item split (default): warn if multiple p+ul groups will cause stacking
    multi_groups = re.findall(r'(?:<p[^>]*>[\s\S]*?</p>\s*)?<[ou]l[\s\S]*?</[ou]l>', inner_html)
    if len(multi_groups) >= 2:
        print(f"WARNING: slide-{index} contains {len(multi_groups)} p+ul groups in three-column layout. "
              f"Only the first list will be split; remaining groups stack above. "
              f"Set splitMode=group in slide-tree.json to fix.")

    ul_m = re.search(r'<[ou]l[\s\S]*?</[ou]l>', inner_html)
    if ul_m:
        groups = _split_list_items(ul_m.group(0), 3)
        rest = inner_html[:ul_m.start()] + inner_html[ul_m.end():]
        cols_html = (
            '<div class="col-wrap-3">'
            + "".join(f'<div class="col">{g}</div>' for g in groups)
            + '</div>'
        )
        body = (title_html or "") + "\n" + rest + "\n" + cols_html
    else:
        body = (title_html or "") + "\n" + inner_html
    return _wrap_slide_content(body)


def _layout_quote_center(cfg: dict, inner_html: str, title_html: str,
                          chart_html_parts: list, js_snippets: list, index: int) -> str:
    bq, rest = _extract_blockquote_html(inner_html)
    body = (bq or inner_html) + ("\n" + rest if rest and bq else "")
    return _wrap_slide_content(body, "layout-quote-center")


def _layout_quote_side(cfg: dict, inner_html: str, title_html: str,
                        chart_html_parts: list, js_snippets: list, index: int) -> str:
    bq, rest = _extract_blockquote_html(inner_html)
    if not bq:
        return _layout_text_default(cfg, inner_html, title_html, chart_html_parts, js_snippets, index)
    split_html = (
        f'<div class="layout-quote-side">'
        f'<div class="quote-zone">{bq}</div>'
        f'<div class="text-zone">{rest}</div>'
        f'</div>'
    )
    body = (title_html or "") + "\n" + split_html
    return _wrap_slide_content(body)


def _layout_image_side(cfg: dict, inner_html: str, title_html: str,
                        chart_html_parts: list, js_snippets: list, index: int) -> str:
    """image-right or image-left based on cfg['template']."""
    imgs, text_html = _extract_images_html(inner_html)
    img_tag = imgs[0] if imgs else '<span style="opacity:0.3">[no image]</span>'
    img_w = cfg.get("imageWidth", "45%")
    img_panel = f'<div class="img-panel" style="width:{img_w};">{img_tag}</div>'
    text_panel = f'<div class="text-zone">{text_html}</div>'
    if cfg.get("template", "image-right") == "image-left":
        split_inner = img_panel + "\n" + text_panel
    else:
        split_inner = text_panel + "\n" + img_panel
    split = f'<div class="image-split">{split_inner}</div>'
    body = (title_html or "") + "\n" + split
    return _wrap_slide_content(body)


def _layout_image_top_bottom(cfg: dict, inner_html: str, title_html: str,
                              chart_html_parts: list, js_snippets: list, index: int) -> str:
    imgs, text_html = _extract_images_html(inner_html)
    img_tag = imgs[0] if imgs else '<span style="opacity:0.3">[no image]</span>'
    img_h = cfg.get("imageHeight", "45%")
    img_zone = f'<div class="img-zone" style="height:{img_h};">{img_tag}</div>'
    text_zone = f'<div class="text-zone">{text_html}</div>'
    if cfg.get("template", "image-bottom") == "image-top":
        stack_inner = img_zone + "\n" + text_zone
    else:
        stack_inner = (title_html or "") + "\n" + text_zone + "\n" + img_zone
        return _wrap_slide_content(f'<div class="image-stack">{stack_inner}</div>')
    body = (title_html or "") + "\n" + f'<div class="image-stack">{stack_inner}</div>'
    return _wrap_slide_content(body)


def _layout_image_fullbleed(cfg: dict, inner_html: str, title_html: str,
                             chart_html_parts: list, js_snippets: list, index: int) -> str:
    """Returns (body_html, extra_slide_attrs_dict) — caller must apply bg style to slide div."""
    imgs, text_html = _extract_images_html(inner_html)
    # Image goes as background — return marker so render_slide can set style
    body = (title_html or "") + "\n" + text_html
    return _wrap_slide_content(body, "layout-fullbleed-text")


def _get_fullbleed_img_src(inner_html_before_extract: str) -> str:
    """Extract src from first <img> for fullbleed background."""
    m = re.search(r'<img\b[^>]*\bsrc="([^"]*)"', inner_html_before_extract)
    return m.group(1) if m else ""


def _layout_image_only(cfg: dict, inner_html: str, title_html: str,
                        chart_html_parts: list, js_snippets: list, index: int) -> str:
    imgs, _ = _extract_images_html(inner_html)
    img_tag = imgs[0] if imgs else '<span style="opacity:0.3">[no image]</span>'
    caption = re.sub(r'<[^>]+>', '', title_html).strip() if title_html else ""
    cap_html = f'<div class="img-caption">{caption}</div>' if caption else ""
    body = f'<div class="layout-image-only">{img_tag}{cap_html}</div>'
    return _wrap_slide_content(body)


def _layout_stat_cards(cfg: dict, inner_html: str, title_html: str,
                        chart_html_parts: list, js_snippets: list, index: int) -> str:
    stats = _extract_list_items_as_stats(inner_html)
    if not stats:
        return _layout_text_default(cfg, inner_html, title_html, chart_html_parts, js_snippets, index)
    # columns: AI sets this in layout hint based on card count and content symmetry.
    # Default: all cards in one row (len(stats) columns).
    columns = cfg.get("columns", len(stats))
    cards = "".join(
        f'<div class="stat-card"><span class="s-num">{s["num"]}</span>'
        f'<span class="s-lbl">{s["label"]}</span></div>'
        for s in stats
    )
    body = (title_html or "") + f'\n<div class="stat-grid" style="--stat-cols:{columns};">{cards}</div>'
    return _wrap_slide_content(body)


def _layout_card_grid(cfg: dict, inner_html: str, title_html: str,
                      chart_html_parts: list, js_snippets: list, index: int) -> str:
    """General-purpose card grid. Each <li> becomes a card: <strong> = title, rest = body."""
    columns = cfg.get("columns", 3)
    items = re.findall(r'<li[^>]*>([\s\S]*?)</li>', inner_html)
    if not items:
        return _layout_text_default(cfg, inner_html, title_html, chart_html_parts, js_snippets, index)

    cards = []
    for item in items:
        strong_m = re.search(r'<strong>([\s\S]*?)</strong>', item)
        card_title = strong_m.group(1) if strong_m else ""
        card_body = re.sub(r'<strong>[\s\S]*?</strong>', '', item, count=1).strip()
        card_body = re.sub(r'^(<br\s*/?>|\s)+', '', card_body).strip()
        cards.append(
            f'<div class="card-grid-item">'
            + (f'<div class="cg-title">{card_title}</div>' if card_title else "")
            + (f'<div class="cg-body">{card_body}</div>' if card_body else "")
            + '</div>'
        )

    grid_html = f'<div class="card-grid" style="--card-cols:{columns};">{"".join(cards)}</div>'
    body = (title_html or "") + "\n" + grid_html
    return _wrap_slide_content(body)


def _layout_timeline_vertical(cfg: dict, inner_html: str, title_html: str,
                               chart_html_parts: list, js_snippets: list, index: int) -> str:
    ul_m = re.search(r'<[ou]l[^>]*>([\s\S]*?)</[ou]l>', inner_html)
    if not ul_m:
        return _layout_text_default(cfg, inner_html, title_html, chart_html_parts, js_snippets, index)
    items = re.findall(r'<li[^>]*>([\s\S]*?)</li>', ul_m.group(0))
    tl_items = "".join(
        f'<li><span class="tl-v-num">{i+1:02d}</span>'
        f'<div class="tl-v-content">{it}</div></li>'
        for i, it in enumerate(items)
    )
    body = (title_html or "") + f'\n<ul class="tl-v-list">{tl_items}</ul>'
    return _wrap_slide_content(body)


def _layout_timeline_horizontal(cfg: dict, inner_html: str, title_html: str,
                                  chart_html_parts: list, js_snippets: list, index: int) -> str:
    ul_m = re.search(r'<[ou]l[^>]*>([\s\S]*?)</[ou]l>', inner_html)
    if not ul_m:
        return _layout_text_default(cfg, inner_html, title_html, chart_html_parts, js_snippets, index)
    items = re.findall(r'<li[^>]*>([\s\S]*?)</li>', ul_m.group(0))
    tl_items = "".join(
        f'<li><div class="tl-h-dot">{i+1}</div>'
        f'<div class="tl-h-text">{re.sub(r"<[^>]+>","",it).strip()}</div></li>'
        for i, it in enumerate(items)
    )
    body = (
        (title_html or "") +
        f'\n<div class="tl-h-wrap"><ul class="tl-h-list">{tl_items}</ul></div>'
    )
    return _wrap_slide_content(body)


def _layout_compare(cfg: dict, inner_html: str, title_html: str,
                     chart_html_parts: list, js_snippets: list, index: int) -> str:
    n = 3 if cfg.get("template") == "compare-three" else 2
    # Try to split by h3 headings first
    parts = re.split(r'(?=<h3[^>]*>)', inner_html)
    parts = [p for p in parts if p.strip()]
    if len(parts) >= n:
        cols = parts[:n]
    else:
        # Fall back: split list items
        ul_m = re.search(r'<[ou]l[\s\S]*?</[ou]l>', inner_html)
        if ul_m:
            groups = _split_list_items(ul_m.group(0), n)
            cols = groups
        else:
            cols = [inner_html] + [""] * (n - 1)
    col_html = "".join(f'<div class="compare-col">{c}</div>' for c in cols)
    body = (title_html or "") + f'\n<div class="compare-wrap">{col_html}</div>'
    return _wrap_slide_content(body)


def _layout_cover_image_bg(cfg: dict, inner_html: str, title_html: str,
                            chart_html_parts: list, js_snippets: list, index: int) -> str:
    body = (title_html or "") + "\n" + inner_html
    return _wrap_slide_content(body)


def _layout_cover_split(cfg: dict, inner_html: str, title_html: str,
                         chart_html_parts: list, js_snippets: list, index: int) -> str:
    imgs, text_html = _extract_images_html(inner_html)
    img_tag = imgs[0] if imgs else ""
    text_content = (title_html or "") + "\n" + text_html
    split = (
        f'<div class="cover-split-wrap">'
        f'<div class="cover-split-text">{text_content}</div>'
        f'<div class="cover-split-img">{img_tag}</div>'
        f'</div>'
    )
    return _wrap_slide_content(split)


def _layout_section_header(cfg: dict, inner_html: str, title_html: str,
                            chart_html_parts: list, js_snippets: list, index: int) -> str:
    eyebrow = cfg.get("eyebrow", f"Section {index}")
    title_text = re.sub(r'<[^>]+>', '', title_html).strip() if title_html else ""
    sub_m = re.search(r'<p[^>]*>([\s\S]*?)</p>', inner_html)
    sub_text = re.sub(r'<[^>]+>', '', sub_m.group(1)).strip() if sub_m else ""
    sub_html = f'<div class="section-sub">{sub_text}</div>' if sub_text else ""

    sections: list[dict] = cfg.get("sections", [])   # [{index, title}, ...]
    total_sections = len(sections)
    # current section position among all section-header slides
    current_pos = next((i for i, s in enumerate(sections) if s["index"] == index), 0)

    if total_sections >= 5:
        # ── TOC variant ──────────────────────────────────────────────────────
        toc_items = []
        for i, s in enumerate(sections):
            if i < current_pos:
                cls = "toc-done"
            elif i == current_pos:
                cls = "toc-active"
            else:
                cls = ""
            toc_items.append(
                f'<div class="toc-item {cls}">'
                f'<span class="toc-bullet"></span>'
                f'<span>{s["title"]}</span>'
                f'</div>'
            )
        toc_html = "\n".join(toc_items)
        body = (
            f'<div class="layout-section-toc">'
            f'<div class="section-toc-left">'
            f'<div class="section-eyebrow">{eyebrow}</div>'
            f'<div class="section-main">{title_text}</div>'
            + sub_html +
            f'</div>'
            f'<div class="section-toc-right">{toc_html}</div>'
            f'</div>'
        )
    else:
        # ── Centered variant ─────────────────────────────────────────────────
        dots_html = ""
        if total_sections >= 2:
            dots = "".join(
                f'<span class="section-dot{"  active" if i == current_pos else ""}"></span>'
                for i in range(total_sections)
            )
            dots_html = f'<div class="section-dots">{dots}</div>'
        body = (
            f'<div class="layout-section-centered">'
            f'<div class="section-eyebrow">{eyebrow}</div>'
            f'<div class="section-main">{title_text}</div>'
            + sub_html
            + dots_html +
            f'</div>'
        )
    return _wrap_slide_content(body)


def _layout_table_full(cfg: dict, inner_html: str, title_html: str,
                        chart_html_parts: list, js_snippets: list, index: int) -> str:
    tbl_m = re.search(r'(<table[\s\S]*?</table>)', inner_html)
    tbl = tbl_m.group(1) if tbl_m else inner_html
    rest = inner_html.replace(tbl, "", 1).strip() if tbl_m else ""
    body = (title_html or "") + f'\n<div class="layout-table-full">{tbl}</div>' + (f"\n{rest}" if rest else "")
    return _wrap_slide_content(body)


# Layout dispatch map
_LAYOUT_DISPATCH = {
    "text-default":          _layout_text_default,
    "text-hero":             _layout_text_hero,
    "text-two-column":       _layout_text_two_column,
    "text-three-column":     _layout_text_three_column,
    "statement":             _layout_statement,
    "quote-center":          _layout_quote_center,
    "quote-side":            _layout_quote_side,
    "image-right":           _layout_image_side,
    "image-left":            _layout_image_side,
    "image-top":             _layout_image_top_bottom,
    "image-bottom":          _layout_image_top_bottom,
    "image-fullbleed":       _layout_image_fullbleed,
    "image-only":            _layout_image_only,
    "stat-cards":            _layout_stat_cards,
    "card-grid":             _layout_card_grid,
    "timeline-vertical":     _layout_timeline_vertical,
    "timeline-horizontal":   _layout_timeline_horizontal,
    "compare-two":           _layout_compare,
    "compare-three":         _layout_compare,
    "cover-image-bg":        _layout_cover_image_bg,
    "cover-split":           _layout_cover_split,
    "section-header":        _layout_section_header,
    "table-full":            _layout_table_full,
}


# ── Slide rendering ───────────────────────────────────────────────────────────

def render_chart_panel(chart_id: str, cp: dict, csv_data: list[dict],
                       chart_defaults: dict) -> tuple[str, str]:
    """
    Returns (html_fragment, js_snippet).
    html_fragment: the <div class="chart-panel"> or table HTML.
    js_snippet:    Chart.js initialization code (empty for table type).
    """
    chart_type = cp.get("type", "bar")
    width  = cp.get("width", "55%")
    height = cp.get("height", "65%")
    title  = cp.get("title", "")

    if chart_type == "table":
        table_html = render_data_table(chart_id, csv_data)
        panel = (
            f'<div class="chart-panel" id="{chart_id}-panel" '
            f'style="width:{width}; height:{height};">\n'
            + (f'  <p class="chart-title" id="{chart_id}-title">{title}</p>\n' if title else "")
            + f'  {table_html}\n</div>'
        )
        return panel, ""

    config   = build_chart_config(cp, csv_data, chart_defaults)
    js_snip  = render_chart_js(chart_id, config)
    panel = (
        f'<div class="chart-panel" id="{chart_id}-panel" '
        f'style="width:{width}; height:{height};">\n'
        + (f'  <p class="chart-title" id="{chart_id}-title">{title}</p>\n' if title else "")
        + f'  <canvas id="{chart_id}"></canvas>\n</div>'
    )
    return panel, js_snip


def _preprocess_col_blocks(md_text: str) -> str:
    """
    Convert :::col ... ::: blocks to HTML column divs before markdown parsing.

    Syntax:
        :::col
        **Column 1 title**
        - item
        :::col
        **Column 2 title**
        - item
        :::

    Two sections  → .col-wrap  (two-column)
    Three sections → .col-wrap-3 (three-column)
    """
    import markdown as _md

    def _replace(m: re.Match) -> str:
        inner = m.group(1)
        # First :::col is the block opener, subsequent ones are column separators
        parts = re.split(r'\n?:::col\n?', '\n' + inner)
        parts = [p.strip() for p in parts if p.strip()]
        if not parts:
            return m.group(0)
        wrap_cls = "col-wrap" if len(parts) <= 2 else "col-wrap-3"
        cols_html = "".join(
            f'<div class="col">{_md.markdown(p, extensions=["tables", "nl2br"])}</div>'
            for p in parts
        )
        return f'\n<div class="{wrap_cls}">\n{cols_html}\n</div>\n'

    return re.sub(r':::col\n([\s\S]*?)\n:::(?!col)', _replace, md_text)


def render_slide(
    index: int,
    raw_content: str,
    md_dir: pathlib.Path,
    chart_defaults: dict,
    output_dir: pathlib.Path | None = None,
    layout_hint: dict | None = None,
) -> tuple[str, dict, list[str]]:
    """
    Returns (html_fragment, tree_node, js_snippets).
    """
    import markdown

    slide_type = detect_slide_type(raw_content)

    # strip <!-- Slide N: ... --> comment
    content = re.sub(r"<!--\s*Slide\s+\d+[^>]*-->", "", raw_content, count=1).strip()

    # extract chart blocks
    chart_params_list, content_no_chart = extract_chart_blocks(content)

    # Pre-process :::col blocks → HTML column divs (before markdown parsing)
    content_no_chart = _preprocess_col_blocks(content_no_chart)

    # convert remaining MD to HTML
    inner_html = markdown.markdown(
        content_no_chart,
        extensions=["tables", "fenced_code", "nl2br"],
    )
    # Fix relative image paths (relative to MD) → relative to output HTML
    if output_dir is not None:
        inner_html = fix_image_paths(inner_html, md_dir, output_dir)
    # Semantic visual enhancement (emoji icons, key-number spans)
    inner_html = enhance_inner_html(inner_html, slide_type)
    inner_html = assign_ids(inner_html, index)

    js_snippets: list[str] = []

    # Determine layout template
    template = (layout_hint or {}).get("template", "")
    cfg = layout_hint or {}

    # ── rawHtml override: bypass layout dispatch entirely ────────────────────
    # Set layout_hint["rawHtml"] in slide-tree.json to inject arbitrary HTML
    # directly as the slide body, skipping MD parsing and all layout logic.
    if cfg.get("rawHtml"):
        body_html = (
            f'  <div class="slide-content">\n'
            f'{cfg["rawHtml"]}\n'
            f'  </div>'
        )
        html_frag = (
            f'<div class="slide" id="slide-{index}" '
            f'data-index="{index}" data-type="{slide_type}">\n'
            f'{body_html}\n'
            f'</div>'
        )
        tree_node = {"index": index, "type": slide_type, "elements": [],
                     "layout": layout_hint}
        return html_frag, tree_node, js_snippets
    # ─────────────────────────────────────────────────────────────────────────

    # Extract title before layout rendering (all layout renderers need it separately)
    title_html, body_inner_html = _extract_title_html(inner_html)

    # Chart layouts: delegate to existing chart rendering logic
    CHART_TEMPLATES = {"chart-full", "chart-right", "chart-left", "chart-bottom", ""}
    use_chart_path = bool(chart_params_list) and (template in CHART_TEMPLATES or not template)

    if use_chart_path:
        # ── existing chart layout logic (unchanged) ──────────────────────────
        chart_html_parts: list[str] = []
        for ci, cp in enumerate(chart_params_list, start=1):
            chart_id  = f"s{index}-chart{ci}"
            data_src  = cp.get("dataSource", "")
            if not data_src and cp.get("dataFile"):
                data_src = cp["dataFile"]
                print(f"Warning: 'dataFile' in chart block is deprecated, rename to 'dataSource'.")
            csv_path  = md_dir / data_src if data_src else None
            csv_data  = read_csv(csv_path) if csv_path else []
            panel_html, js_snip = render_chart_panel(
                chart_id, cp, csv_data, chart_defaults
            )
            chart_html_parts.append(panel_html)
            if js_snip:
                js_snippets.append(js_snip)

        position = chart_params_list[0].get("position", "full")
        # Override position from layout hint if given
        if template == "chart-right":  position = "right"
        elif template == "chart-left": position = "left"
        elif template == "chart-bottom": position = "bottom"
        elif template == "chart-full": position = "full"

        if position in ("right", "left"):
            chart_w = chart_params_list[0].get("width", "55%")
            try:
                text_w_pct = 100 - float(chart_w.rstrip("%")) - 3
                text_w = f"{text_w_pct:.0f}%"
            except Exception:
                text_w = "42%"
            text_panel = (
                f'<div class="text-panel" id="s{index}-text-panel" style="width:{text_w};">\n'
                f'{inner_html}\n</div>'
            )
            chart_panel = chart_html_parts[0] if chart_html_parts else ""
            if position == "right":
                split_inner = text_panel + "\n" + chart_panel
            else:
                split_inner = chart_panel + "\n" + text_panel
            body_html = (
                f'  <div class="slide-content">\n'
                f'    <div class="layout-split">\n{split_inner}\n    </div>\n'
                f'  </div>'
            )
        elif position == "full":
            charts_joined = "\n".join(chart_html_parts)
            body_html = (
                f'  <div class="slide-content">\n'
                f'{inner_html}\n'
                f'    <div class="layout-full-chart">\n{charts_joined}\n    </div>\n'
                f'  </div>'
            )
        else:
            charts_joined = "\n".join(chart_html_parts)
            if position == "bottom":
                body_html = (
                    f'  <div class="slide-content">\n'
                    f'    <div class="layout-stacked">\n'
                    f'{inner_html}\n{charts_joined}\n'
                    f'    </div>\n  </div>'
                )
            else:
                h1_match = re.search(r'(<h1[^>]*>.*?</h1>)', inner_html, re.DOTALL)
                rest_html = inner_html
                title_h1 = ""
                if h1_match:
                    title_h1 = h1_match.group(1)
                    rest_html = inner_html.replace(title_h1, "", 1).strip()
                body_html = (
                    f'  <div class="slide-content">\n'
                    f'{title_h1}\n'
                    f'    <div class="layout-stacked">\n{charts_joined}\n{rest_html}\n    </div>\n'
                    f'  </div>'
                )
    else:
        # ── layout dispatch ────────────────────────────────────────────────
        renderer = _LAYOUT_DISPATCH.get(template, _layout_text_default)
        body_html = renderer(cfg, body_inner_html, title_html, [], js_snippets, index)

        # Special: fullbleed needs bg image on slide div — handled below via extra_attrs

    # ── Content density class ────────────────────────────────────────────────
    li_count = inner_html.count("<li")
    if li_count <= 3:
        density_cls = "density-spacious"
    elif li_count <= 5:
        density_cls = "density-normal"
    else:
        density_cls = "density-compact"
    body_html = body_html.replace('class="slide-content"',
                                  f'class="slide-content {density_cls}"', 1)

    # Extra attributes for special layouts (fullbleed background)
    extra_slide_attrs = ""
    extra_slide_classes = ""
    if template == "image-fullbleed":
        bg_src = _get_fullbleed_img_src(inner_html)
        if bg_src:
            extra_slide_attrs = f' style="background-image:url(\'{bg_src}\')"'
        extra_slide_classes = " layout-fullbleed"
    elif template == "cover-image-bg":
        bg_src = _get_fullbleed_img_src(inner_html)
        if bg_src:
            extra_slide_attrs = f' style="background-image:url(\'{bg_src}\')"'
        extra_slide_classes = " cover-image-bg"

    html_frag = (
        f'<div class="slide{extra_slide_classes}" id="slide-{index}" '
        f'data-index="{index}" data-type="{slide_type}"{extra_slide_attrs}>\n'
        f'{body_html}\n'
        f'</div>'
    )

    tree_node = {
        "index": index,
        "type":  slide_type,
        "elements": extract_tree_elements(inner_html, chart_params_list, index),
    }
    if layout_hint:
        tree_node["layout"] = layout_hint

    return html_frag, tree_node, js_snippets


# ── Template rendering ─────────────────────────────────────────────────────────

def _replace_all(template: str, mapping: dict) -> str:
    """Replace all {{PLACEHOLDER}} tokens in a single regex pass (no double-substitution)."""
    pattern = re.compile("|".join(re.escape(k) for k in mapping))
    return pattern.sub(lambda m: mapping[m.group(0)], template)


# ── HTML generation ───────────────────────────────────────────────────────────

def generate_html(
    slides_html: str,
    charts_js: str,
    meta: dict,
    theme_css: str,
    slide_size: tuple,
    inline_assets: bool = False,
) -> str:
    template_path = _base_dir() / "references" / "template.html"
    template = template_path.read_text(encoding="utf-8")

    slide_w, slide_h = slide_size
    total       = slides_html.count('class="slide"')
    first_pct   = round(1 / total * 100, 2) if total else 0
    theme       = meta.get("theme", "professional-dark")
    hl_theme    = HIGHLIGHT_MAP.get(theme, "github-dark")

    slide_js = (
        SLIDE_JS
        .replace("SLIDE_W_PLACEHOLDER", str(slide_w))
        .replace("SLIDE_H_PLACEHOLDER", str(slide_h))
    )

    # Build asset tags: inline (offline-safe) or CDN links (bootcdn.cn for China)
    hljs_css_url  = ASSET_URLS["hljs_css"].format(theme=hl_theme)
    if inline_assets:
        print("Inlining assets (downloading if not cached)...")
        chartjs_content  = _load_asset(ASSET_URLS["chartjs"], "chart.umd.min.js")
        hljs_js_content  = _load_asset(ASSET_URLS["hljs_js"], "highlight.min.js")
        hljs_css_content = _load_asset(hljs_css_url, f"hljs-{hl_theme}.min.css")
        hljs_css_tag  = (f"<style>{hljs_css_content}</style>"
                         if hljs_css_content
                         else f'<link rel="stylesheet" href="{hljs_css_url}">')
        chartjs_tag   = (f"<script>{chartjs_content}</script>"
                         if chartjs_content
                         else f'<script src="{ASSET_URLS["chartjs"]}"></script>')
        hljs_js_tag   = (f"<script>{hljs_js_content}</script>"
                         if hljs_js_content
                         else f'<script src="{ASSET_URLS["hljs_js"]}"></script>')
    else:
        hljs_css_tag = f'<link rel="stylesheet" href="{hljs_css_url}">'
        chartjs_tag  = f'<script src="{ASSET_URLS["chartjs"]}"></script>'
        hljs_js_tag  = f'<script src="{ASSET_URLS["hljs_js"]}"></script>'

    mapping = {
        "{{TITLE}}":           meta.get("title", "Presentation"),
        "{{SLIDE_WIDTH}}":     str(slide_w),
        "{{SLIDE_HEIGHT}}":    str(slide_h),
        "{{CONTENT_PADDING}}": CONTENT_PADDING,
        "{{THEME_CSS}}":       theme_css,
        "{{LAYOUT_CSS}}":      LAYOUT_CSS,
        "{{HIGHLIGHT_THEME}}": hl_theme,
        "{{HLJS_CSS_TAG}}":    hljs_css_tag,
        "{{CHARTJS_TAG}}":     chartjs_tag,
        "{{HLJS_JS_TAG}}":     hljs_js_tag,
        "{{SLIDES_HTML}}":     slides_html,
        "{{TOTAL}}":           str(total),
        "{{FIRST_PROGRESS}}":  str(first_pct),
        "{{SLIDE_JS}}":        slide_js,
        "{{CHARTS_JS}}":       charts_js or "// no charts",
    }
    return _replace_all(template, mapping)


# ── Tree helpers ──────────────────────────────────────────────────────────────

def build_element_tree(slide_nodes: list[dict], meta: dict) -> dict:
    return {
        "presentation": {
            "ratio":       meta.get("ratio", "16:9"),
            "theme":       meta.get("theme", "professional-dark"),
            "totalSlides": len(slide_nodes),
            "slides":      slide_nodes,
        }
    }


def merge_preserved_styles(new_tree: dict, old_tree: dict) -> tuple[dict, list[str]]:
    """Merge customized style fields from old_tree back into new_tree."""
    old_map: dict[str, dict] = {}
    for slide in old_tree.get("presentation", {}).get("slides", []):
        for el in slide.get("elements", []):
            if el.get("style"):
                old_map[el["id"]] = el["style"]

    new_ids: set[str] = set()
    for slide in new_tree["presentation"]["slides"]:
        for el in slide.get("elements", []):
            new_ids.add(el["id"])
            if el["id"] in old_map:
                el.setdefault("style", {}).update(old_map[el["id"]])

    lost_ids = [eid for eid in old_map if eid not in new_ids]
    return new_tree, lost_ids


# ── Main convert function ─────────────────────────────────────────────────────

def convert(
    input_path: pathlib.Path,
    output_path: pathlib.Path,
    tree_path: pathlib.Path,
    ratio: str | None = None,
    theme: str | None = None,
    preserve_styles: bool = False,
    inline_assets: bool = False,
):
    # Resolve to absolute so md_dir / data_src works regardless of CWD
    input_path = pathlib.Path(input_path).resolve()
    meta, raw_slides = parse_md(input_path)

    meta["ratio"] = ratio or meta.get("ratio", "16:9")
    meta["theme"] = theme or meta.get("theme", "professional-dark")
    slide_size    = SLIDE_SIZES.get(meta["ratio"], (1280, 720))

    theme_css      = load_theme_css(meta["theme"])
    chart_defaults = load_chart_defaults(meta["theme"])

    md_dir = input_path.parent
    all_slides_html: list[str] = []
    all_tree_nodes:  list[dict] = []
    all_charts_js:   list[str]  = []

    # Read layout hints from existing tree file (if present)
    layout_hints: dict[int, dict] = {}
    if tree_path.exists():
        try:
            existing_tree = json.loads(tree_path.read_text(encoding="utf-8"))
            for slide in existing_tree.get("presentation", {}).get("slides", []):
                if slide.get("layout"):
                    layout_hints[slide["index"]] = slide["layout"]
        except Exception:
            pass

    # Pre-scan: collect section list for section-header TOC injection
    def _extract_raw_title(raw: str) -> str:
        m = re.search(r'^#{1,2}\s+(.+)$', raw, re.MULTILINE)
        return m.group(1).strip() if m else ""

    section_list: list[dict] = []
    for i, raw in enumerate(raw_slides, start=1):
        if layout_hints.get(i, {}).get("template") == "section-header":
            section_list.append({"index": i, "title": _extract_raw_title(raw)})

    # Inject section_list into each section-header layout hint
    for s in section_list:
        layout_hints.setdefault(s["index"], {})["sections"] = section_list

    for i, raw in enumerate(raw_slides, start=1):
        html_frag, tree_node, js_snippets = render_slide(
            i, raw, md_dir, chart_defaults,
            output_dir=output_path.parent,
            layout_hint=layout_hints.get(i),
        )
        all_slides_html.append(html_frag)
        all_tree_nodes.append(tree_node)
        all_charts_js.extend(js_snippets)

    slides_html = "\n\n".join(all_slides_html)
    charts_js   = "\n\n".join(all_charts_js)
    new_tree    = build_element_tree(all_tree_nodes, meta)

    if preserve_styles and tree_path.exists():
        old_tree = json.loads(tree_path.read_text(encoding="utf-8"))
        new_tree, lost_ids = merge_preserved_styles(new_tree, old_tree)
        if lost_ids:
            print(f"[preserve-styles] Style lost for: {', '.join(lost_ids)}")

    html_output = generate_html(slides_html, charts_js, meta, theme_css, slide_size, inline_assets)

    output_path.write_text(html_output, encoding="utf-8")
    tree_path.write_text(
        json.dumps(new_tree, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"Generated: {output_path}  ({len(all_tree_nodes)} slides)")
    print(f"Tree:      {tree_path}")
    if any(all_charts_js):
        chart_count = len([j for j in all_charts_js if j])
        print(f"Charts:    {chart_count} chart(s) rendered")


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert MD presentation to HTML")
    parser.add_argument("--input",  required=True)
    parser.add_argument("--output")
    parser.add_argument("--tree")
    parser.add_argument("--ratio")
    parser.add_argument("--theme")
    parser.add_argument("--preserve-styles", action="store_true")
    parser.add_argument("--inline-assets", action="store_true",
                        help="Download Chart.js & highlight.js and inline into HTML (offline-safe)")
    parser.add_argument("--serve", action="store_true",
                        help="After generating, open the HTML file directly in the default browser")
    args = parser.parse_args()

    inp  = pathlib.Path(args.input)
    out  = pathlib.Path(args.output) if args.output else inp.with_suffix(".html")
    if args.tree:
        tree = pathlib.Path(args.tree)
    else:
        slides_dir = inp.parent / ".slides"
        slides_dir.mkdir(exist_ok=True)
        tree = slides_dir / f"{inp.stem}.slide-tree.json"

    convert(
        input_path=inp,
        output_path=out,
        tree_path=tree,
        ratio=args.ratio,
        theme=args.theme,
        preserve_styles=args.preserve_styles,
        inline_assets=args.inline_assets,
    )

    if args.serve:
        import webbrowser
        uri = out.resolve().as_uri()
        print(f"Opening:   {uri}")
        webbrowser.open(uri)
