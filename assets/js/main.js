// Vetriva Animal Hospital: site interactions

// TODO: replace with the clinic's real WhatsApp number (country code, no + or spaces)
const WHATSAPP_NUMBER = '923239737896';

const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

// Header turns solid after scrolling
const header = document.querySelector('.header');
const onScroll = () => header.classList.toggle('is-scrolled', window.scrollY > 20);
onScroll();
window.addEventListener('scroll', onScroll, { passive: true });

// Mobile menu
const toggle = document.getElementById('menuToggle');
const nav = document.getElementById('nav');
const setMenu = (open) => {
  nav.classList.toggle('is-open', open);
  toggle.setAttribute('aria-expanded', String(open));
  toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
};
toggle.addEventListener('click', () => setMenu(!nav.classList.contains('is-open')));
nav.querySelectorAll('a').forEach((a) => a.addEventListener('click', () => setMenu(false)));
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') setMenu(false); });

// Mega menus (Services, Products): open on hover (with a short grace period so they don't
// flicker) or keyboard focus on desktop, and with the chevron button inside the mobile menu
const desktopNav = window.matchMedia('(min-width: 921px)');
const megaMenus = [...document.querySelectorAll('.has-mega')].map((item) => {
  const button = item.querySelector('.mega-toggle');
  let timer;
  const set = (open) => {
    clearTimeout(timer);
    item.classList.toggle('is-open', open);
    button.setAttribute('aria-expanded', String(open));
  };
  return { item, set, later: () => { timer = setTimeout(() => set(false), 180); } };
});
megaMenus.forEach(({ item, set, later }) => {
  const others = () => megaMenus.forEach((m) => { if (m.item !== item) m.set(false); });
  item.addEventListener('mouseenter', () => { if (desktopNav.matches) { others(); set(true); } });
  item.addEventListener('mouseleave', () => { if (desktopNav.matches) later(); });
  item.addEventListener('focusin', () => { if (desktopNav.matches) { others(); set(true); } });
  item.addEventListener('focusout', (e) => {
    if (desktopNav.matches && !item.contains(e.relatedTarget)) set(false);
  });
  item.querySelector('.mega-toggle').addEventListener('click', () => set(!item.classList.contains('is-open')));
  item.querySelectorAll('.mega a').forEach((a) => a.addEventListener('click', () => {
    set(false);
    a.blur();
  }));
});
const closeMegas = () => megaMenus.forEach((m) => m.set(false));
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeMegas(); });
desktopNav.addEventListener('change', closeMegas);

// Hero highlight card: rotates through a few services
const slides = [...document.querySelectorAll('.hero__feature')];
const dots = [...document.querySelectorAll('.hero__dots button')];
let current = 0;
let timer;
const showSlide = (i) => {
  current = (i + slides.length) % slides.length;
  slides.forEach((s, n) => {
    s.classList.toggle('is-active', n === current);
    s.setAttribute('aria-hidden', String(n !== current));
  });
  dots.forEach((d, n) => {
    d.classList.toggle('is-active', n === current);
    d.setAttribute('aria-selected', String(n === current));
  });
};
const startSlider = () => {
  if (reduceMotion) return;
  clearInterval(timer);
  timer = setInterval(() => showSlide(current + 1), 5000);
};
dots.forEach((d, n) => d.addEventListener('click', () => { showSlide(n); startSlider(); }));
const heroCopy = document.querySelector('.hero__copy');
if (heroCopy && slides.length) {
  heroCopy.addEventListener('mouseenter', () => clearInterval(timer));
  heroCopy.addEventListener('mouseleave', startSlider);
  startSlider();
}

// Hero puppy: the head turns left/right to follow the cursor horizontally.
// The turn is a 31-frame sequence (far left -> far right) that the cursor scrubs through.
// Every frame is one real photo bent into position, so each stays sharp. Neighbouring frames
// from the same photo are blended for smooth motion; where the sequence hands over from one
// photo to the next, it switches cleanly and fades the change over a moment instead.
// While the cursor moves the head follows it; once the cursor rests it looks to the front, and while
// the mouse button is held down (or a finger is held on the hero) it turns to look right.
const FRAME_COUNT = 31;
const KEY_FRAMES = [0, 5, 15, 25, 30]; // the real photos: far left, left, front, right, far right
const SWITCH_AFTER = [2, 9, 19, 27];   // frame i comes from one photo, frame i + 1 from the next
const SWITCH_FADE_MS = 140;
const LOOK_FRONT = 0;     // the real front-facing photo
const LOOK_RIGHT = 0.5;   // the real "right" photo
const FOLLOW_FOR_MS = 1200; // how long the head keeps following after the cursor stops
const pup = document.getElementById('pup');
if (pup && !reduceMotion) {
  const still = pup.querySelector('.pup__head');
  const canvas = pup.querySelector('.pup__canvas');
  const ctx = canvas.getContext('2d');
  const headWrap = pup.querySelector('.pup__heads');
  const ring = document.querySelector('.hero__ring');
  const clamp = (v) => Math.max(-1, Math.min(1, v));
  const frames = [];
  const offscreen = () => Object.assign(document.createElement('canvas'), { width: canvas.width, height: canvas.height });
  const snapshot = offscreen();  // the picture being faded out after a photo switch
  const clean = offscreen();     // the last frame as drawn, without any fade on top
  const snapCtx = snapshot.getContext('2d');
  const cleanCtx = clean.getContext('2d');
  let ready = false;
  let drawn = -1;
  let photo = -1;
  let fadeStart = -Infinity;
  let cursorTarget = LOOK_FRONT;
  let x = LOOK_FRONT;
  let lastMove = -Infinity;
  let holding = false;
  let last = 0;
  let running = false;

  // Load the frames after the page itself, then swap the still image for the canvas
  const loadFrames = () => Promise.all(
    Array.from({ length: FRAME_COUNT }, (_, i) => new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = resolve;
      img.onerror = reject;
      img.src = `assets/img/puppy/frames/f${String(i).padStart(2, '0')}.webp`;
      frames[i] = img;
    })),
  ).then(() => {
    // Draw every frame once so they are all decoded before the first movement
    frames.forEach((img) => ctx.drawImage(img, 0, 0, canvas.width, canvas.height));
    ready = true;
    drawn = -1;
    canvas.hidden = false;
    still.hidden = true;
  }).catch(() => { /* keep the still image */ });
  if (document.readyState === 'complete') loadFrames();
  else window.addEventListener('load', loadFrames, { once: true });

  // Cursor position (-1..1) -> frame position. Within each stretch between two real photos
  // the curve eases in and out, so the head settles on a real photo rather than a blend.
  const framePosition = (v) => {
    const p = ((v + 1) / 2) * (KEY_FRAMES.length - 1);
    const seg = Math.min(KEY_FRAMES.length - 2, Math.floor(p));
    const u = p - seg;
    const eased = u * u * u * (u * (u * 6 - 15) + 10);
    return KEY_FRAMES[seg] + eased * (KEY_FRAMES[seg + 1] - KEY_FRAMES[seg]);
  };

  // Which real photo a frame position is drawn from
  const photoAt = (f) => SWITCH_AFTER.filter((i) => f >= i + 0.5).length;

  const draw = (f, now) => {
    const fading = now - fadeStart < SWITCH_FADE_MS;
    if (Math.abs(f - drawn) < 0.004 && !fading) return;
    drawn = f;

    const p = photoAt(f);
    if (photo !== -1 && p !== photo) {
      // Fade the last clean frame out over the new photo (never a frame that is itself mid-fade)
      snapCtx.clearRect(0, 0, snapshot.width, snapshot.height);
      snapCtx.drawImage(clean, 0, 0);
      fadeStart = now;
    }
    photo = p;

    let i = Math.min(FRAME_COUNT - 1, Math.floor(f));
    let mix = f - i;
    if (SWITCH_AFTER.includes(i)) {  // never blend two different photos
      i = mix < 0.5 ? i : i + 1;
      mix = 0;
    }
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.globalAlpha = 1;
    ctx.drawImage(frames[i], 0, 0, canvas.width, canvas.height);
    if (mix > 0.004 && i + 1 < FRAME_COUNT) {
      ctx.globalAlpha = mix;
      ctx.drawImage(frames[i + 1], 0, 0, canvas.width, canvas.height);
    }
    cleanCtx.clearRect(0, 0, clean.width, clean.height);
    cleanCtx.drawImage(canvas, 0, 0);
    const fadeLeft = 1 - (now - fadeStart) / SWITCH_FADE_MS;
    if (fadeLeft > 0) {
      ctx.globalAlpha = fadeLeft * fadeLeft;
      ctx.drawImage(snapshot, 0, 0);
    }
    ctx.globalAlpha = 1;
  };

  window.addEventListener('pointermove', (e) => {
    const r = pup.getBoundingClientRect();
    const cx = r.left + r.width / 2;
    const dx = e.clientX - cx;
    // Full turn just before the screen edge on that side (the puppy is not centred on desktop)
    const reach = Math.max((dx < 0 ? cx : window.innerWidth - cx) * 0.85, 120);
    cursorTarget = clamp(dx / reach);
    lastMove = performance.now();
  }, { passive: true });
  document.documentElement.addEventListener('mouseleave', () => { lastMove = -Infinity; });

  // Press and hold: any mouse button press, or a finger held on the hero section
  const hero = document.querySelector('.hero');
  window.addEventListener('pointerdown', (e) => {
    if (e.pointerType === 'mouse' || hero.contains(e.target)) holding = true;
  });
  const release = () => { holding = false; };
  ['pointerup', 'pointercancel', 'blur'].forEach((type) => window.addEventListener(type, release));

  const frame = (now) => {
    if (!running) return;
    const dt = Math.min(64, now - (last || now));
    last = now;

    let target = LOOK_FRONT;
    if (holding) target = LOOK_RIGHT;
    else if (now - lastMove < FOLLOW_FOR_MS) target = cursorTarget;

    // Frame-rate independent easing towards the target
    const k = 1 - Math.pow(1 - 0.1, dt / 16.67);
    x += (target - x) * k;

    if (ready) draw(framePosition(x), now);

    headWrap.style.transform = `translate3d(${x * 6}px, 0, 0)`;
    ring.style.translate = `${-x * 12}px 0`;

    requestAnimationFrame(frame);
  };

  // Only animate while the hero is on screen
  new IntersectionObserver(([entry]) => {
    if (entry.isIntersecting && !running) {
      running = true;
      last = 0;
      requestAnimationFrame(frame);
    } else if (!entry.isIntersecting) {
      running = false;
    }
  }).observe(document.querySelector('.hero'));
}

// Mission banner: pets drift at different speeds while scrolling, for a sense of depth
const mission = document.querySelector('.mission__stage');
if (mission && !reduceMotion) {
  const layers = [...mission.querySelectorAll('[data-depth]')];
  let visible = false;
  let queued = false;
  const update = () => {
    queued = false;
    const r = mission.getBoundingClientRect();
    // -1 when the stage enters at the bottom of the screen, 1 when it leaves at the top
    const progress = 1 - (r.top + r.height) / ((window.innerHeight + r.height) / 2);
    layers.forEach((el) => {
      el.style.setProperty('--py', `${(-progress * el.dataset.depth * 70).toFixed(1)}px`);
    });
  };
  const onMissionScroll = () => {
    if (visible && !queued) { queued = true; requestAnimationFrame(update); }
  };
  new IntersectionObserver(([entry]) => {
    visible = entry.isIntersecting;
    if (visible) update();
  }).observe(mission);
  window.addEventListener('scroll', onMissionScroll, { passive: true });
  window.addEventListener('resize', onMissionScroll);
}

// Reveal on scroll
const reveals = document.querySelectorAll('.reveal');
if ('IntersectionObserver' in window) {
  const io = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('is-visible');
      io.unobserve(entry.target);
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
  reveals.forEach((el, i) => {
    el.style.transitionDelay = `${(i % 4) * 70}ms`;
    io.observe(el);
  });
} else {
  reveals.forEach((el) => el.classList.add('is-visible'));
}

// Highlight the nav link for the section in view
const links = [...nav.querySelectorAll(':scope > a[href^="#"], .nav__link:not(.nav__link--plain)')];
const sections = links
  .map((a) => a.getAttribute('href'))
  .filter((href) => href.startsWith('#'))   // other pages link back to index.html#...
  .map((href) => document.querySelector(href))
  .filter(Boolean);
if ('IntersectionObserver' in window) {
  const spy = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      links.forEach((a) => a.classList.toggle('is-active', a.getAttribute('href') === `#${entry.target.id}`));
    });
  }, { rootMargin: '-45% 0px -50% 0px' });
  sections.forEach((s) => spy.observe(s));
}

// Accordion: keep one item open at a time
const accordionItems = document.querySelectorAll('#accordion details');
accordionItems.forEach((item) => {
  item.addEventListener('toggle', () => {
    if (!item.open) return;
    accordionItems.forEach((other) => { if (other !== item) other.open = false; });
  });
});

// Booking form (home page only)
const form = document.getElementById('bookingForm');
if (form) {
  const errorEl = document.getElementById('formError');
  const dateInput = form.elements.date;
  const today = new Date();
  dateInput.min = new Date(today.getTime() - today.getTimezoneOffset() * 60000).toISOString().split('T')[0];

  // "Book now" on a service card pre-selects that service
  document.querySelectorAll('[data-service]').forEach((link) => {
    link.addEventListener('click', () => { form.elements.service.value = link.dataset.service; });
  });

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    let valid = true;
    form.querySelectorAll('[required]').forEach((field) => {
      const ok = field.value.trim() !== '' && field.checkValidity();
      field.classList.toggle('is-invalid', !ok);
      if (!ok) valid = false;
    });
    errorEl.hidden = valid;
    if (!valid) {
      form.querySelector('.is-invalid').focus();
      return;
    }

    const d = Object.fromEntries(new FormData(form));
    const lines = [
      'Hello Vetriva, I would like to book an appointment.',
      '',
      `Name: ${d.name}`,
      `Phone: ${d.phone}`,
      `Pet: ${d.pet} (${d.species})`,
      `Service: ${d.service}`,
      `Preferred date: ${d.date}`,
    ];
    if (d.notes.trim()) lines.push(`Notes: ${d.notes.trim()}`);

    window.open(`https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(lines.join('\n'))}`, '_blank', 'noopener');
  });

  form.addEventListener('input', (e) => {
    if (e.target.classList.contains('is-invalid') && e.target.value.trim()) e.target.classList.remove('is-invalid');
  });

  // Links from other pages arrive as index.html?service=...#book
  const requested = new URLSearchParams(window.location.search).get('service');
  if (requested) form.elements.service.value = requested;
}

// Product pages: highlight the category in view in the sticky category bar
const catNav = document.querySelector('.cat-nav');
if (catNav && 'IntersectionObserver' in window) {
  const catList = catNav.querySelector('.cat-nav__list');
  const catLinks = [...catList.querySelectorAll('a')];
  const catSpy = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      catLinks.forEach((a) => {
        const on = a.getAttribute('href') === `#${entry.target.id}`;
        a.classList.toggle('is-active', on);
        // keep the active chip visible on narrow screens without moving the page itself
        if (on) catList.scrollTo({ left: a.offsetLeft - (catList.clientWidth - a.offsetWidth) / 2, behavior: reduceMotion ? 'auto' : 'smooth' });
      });
    });
  }, { rootMargin: '-40% 0px -55% 0px' });
  catLinks.forEach((a) => {
    const section = document.querySelector(a.getAttribute('href'));
    if (section) catSpy.observe(section);
  });
}

document.getElementById('year').textContent = new Date().getFullYear();
