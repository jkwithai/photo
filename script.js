// ============================================================
//  포트폴리오 갤러리 스크립트
//  수정할 필요 없음 — 자동으로 작동합니다
// ============================================================

let allImages     = [];   // 전체 이미지 목록
let filtered      = [];   // 현재 필터된 이미지 목록
let currentIndex  = 0;    // 라이트박스에서 현재 위치

// ──────────────────────────────────────────
//  앱 시작
// ──────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initDarkMode();
  initGallery();
  initFilters();
  initLightbox();
  initKeyboard();
  initSwipe();
});

// ──────────────────────────────────────────
//  다크모드
// ──────────────────────────────────────────
function initDarkMode() {
  const btn     = document.getElementById('darkModeToggle');
  const html    = document.documentElement;
  const saved   = localStorage.getItem('portfolio-theme');
  const prefers = window.matchMedia('(prefers-color-scheme: dark)').matches;

  // 저장된 설정 또는 시스템 설정을 따름
  if (saved === 'dark' || (!saved && prefers)) {
    html.setAttribute('data-theme', 'dark');
  }

  btn.addEventListener('click', () => {
    const isDark = html.getAttribute('data-theme') === 'dark';
    if (isDark) {
      html.setAttribute('data-theme', 'light');
      localStorage.setItem('portfolio-theme', 'light');
    } else {
      html.setAttribute('data-theme', 'dark');
      localStorage.setItem('portfolio-theme', 'dark');
    }
  });
}

// ──────────────────────────────────────────
//  갤러리 불러오기
// ──────────────────────────────────────────
async function initGallery() {
  const grid = document.getElementById('galleryGrid');

  try {
    const res = await fetch('images/gallery.json');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    allImages = Array.isArray(data.images) ? data.images : [];

    if (allImages.length === 0) {
      showEmpty(grid, '사진이 아직 없어요', 'generate_gallery.py 를 실행해 보세요.');
      return;
    }

    filtered = [...allImages];
    renderGrid(filtered);

  } catch (err) {
    console.warn('[Gallery]', err);
    showEmpty(
      grid,
      '갤러리를 불러오지 못했어요',
      'python -m http.server 8080 으로 로컬 서버를 실행한 뒤 열어주세요.'
    );
  }
}

// ──────────────────────────────────────────
//  그리드 렌더링
// ──────────────────────────────────────────
function renderGrid(images) {
  const grid = document.getElementById('galleryGrid');

  if (images.length === 0) {
    showEmpty(grid, '해당 카테고리에 사진이 없어요', '다른 카테고리를 선택해 보세요.');
    return;
  }

  grid.innerHTML = images.map((img, i) => `
    <article
      class="gallery-item"
      data-index="${i}"
      tabindex="0"
      role="button"
      aria-label="${img.title || '사진 보기'}"
    >
      <img
        src="${escHtml(img.src)}"
        alt="${escHtml(img.title || '')}"
        loading="lazy"
        decoding="async"
      >
      ${img.title ? `<div class="gallery-item-title">${escHtml(img.title)}</div>` : ''}
    </article>
  `).join('');

  grid.querySelectorAll('.gallery-item').forEach(el => {
    el.addEventListener('click', () => openLightbox(+el.dataset.index));
    el.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        openLightbox(+el.dataset.index);
      }
    });
  });
}

// ──────────────────────────────────────────
//  카테고리 필터
// ──────────────────────────────────────────
function initFilters() {
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const cat = btn.dataset.filter;
      filtered = cat === 'all'
        ? [...allImages]
        : allImages.filter(img => img.category === cat);

      renderGrid(filtered);
    });
  });
}

// ──────────────────────────────────────────
//  라이트박스
// ──────────────────────────────────────────
function initLightbox() {
  document.getElementById('lightboxBg').addEventListener('click', closeLightbox);
  document.getElementById('lightboxClose').addEventListener('click', closeLightbox);
  document.getElementById('lightboxPrev').addEventListener('click', () => moveLightbox(-1));
  document.getElementById('lightboxNext').addEventListener('click', () => moveLightbox(+1));
}

function openLightbox(index) {
  currentIndex = index;
  showLightboxImage(index);
  const lb = document.getElementById('lightbox');
  lb.classList.add('open');
  lb.setAttribute('aria-hidden', 'false');
  document.body.style.overflow = 'hidden';
}

function closeLightbox() {
  const lb = document.getElementById('lightbox');
  lb.classList.remove('open');
  lb.setAttribute('aria-hidden', 'true');
  document.body.style.overflow = '';
}

function moveLightbox(dir) {
  currentIndex = (currentIndex + dir + filtered.length) % filtered.length;
  showLightboxImage(currentIndex);
}

function showLightboxImage(index) {
  const img     = document.getElementById('lightboxImg');
  const title   = document.getElementById('lightboxTitle');
  const counter = document.getElementById('lightboxCounter');
  const entry   = filtered[index];
  if (!entry) return;

  img.classList.add('loading');
  img.onload = () => img.classList.remove('loading');
  img.src = entry.src;
  img.alt = entry.title || '';

  title.textContent   = entry.title || '';
  counter.textContent = `${index + 1} / ${filtered.length}`;
}

// ──────────────────────────────────────────
//  키보드 단축키
// ──────────────────────────────────────────
function initKeyboard() {
  document.addEventListener('keydown', e => {
    if (!document.getElementById('lightbox').classList.contains('open')) return;
    if (e.key === 'Escape')      closeLightbox();
    if (e.key === 'ArrowLeft')   moveLightbox(-1);
    if (e.key === 'ArrowRight')  moveLightbox(+1);
  });
}

// ──────────────────────────────────────────
//  모바일 스와이프
// ──────────────────────────────────────────
function initSwipe() {
  let startX = 0;
  const stage = document.querySelector('.lightbox-stage');

  stage.addEventListener('touchstart', e => {
    startX = e.touches[0].clientX;
  }, { passive: true });

  stage.addEventListener('touchend', e => {
    const dx = startX - e.changedTouches[0].clientX;
    if (Math.abs(dx) > 48) moveLightbox(dx > 0 ? 1 : -1);
  }, { passive: true });
}

// ──────────────────────────────────────────
//  유틸
// ──────────────────────────────────────────
function showEmpty(grid, heading, sub) {
  grid.innerHTML = `
    <div class="gallery-empty">
      <h3>${escHtml(heading)}</h3>
      <p>${escHtml(sub)}</p>
    </div>
  `;
}

function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}
