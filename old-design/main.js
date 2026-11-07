// Vetriva Animal Hospital: site interactions

// TODO: replace with the clinic's real WhatsApp number (country code, no + or spaces)
const WHATSAPP_NUMBER = '923000000000';

// Sticky header shadow
const header = document.querySelector('.header');
const onScroll = () => header.classList.toggle('is-scrolled', window.scrollY > 8);
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
const links = [...nav.querySelectorAll('a[href^="#"]:not(.btn)')];
const sections = links.map((a) => document.querySelector(a.getAttribute('href'))).filter(Boolean);
if ('IntersectionObserver' in window) {
  const spy = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      links.forEach((a) => a.classList.toggle('is-active', a.getAttribute('href') === `#${entry.target.id}`));
    });
  }, { rootMargin: '-45% 0px -50% 0px' });
  sections.forEach((s) => spy.observe(s));
}

// Booking form: no past dates, then hand off to WhatsApp
const form = document.getElementById('bookingForm');
const errorEl = document.getElementById('formError');
const dateInput = form.elements.date;
const today = new Date();
dateInput.min = new Date(today.getTime() - today.getTimezoneOffset() * 60000).toISOString().split('T')[0];

form.addEventListener('submit', (e) => {
  e.preventDefault();
  const required = [...form.querySelectorAll('[required]')];
  let valid = true;
  required.forEach((field) => {
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

document.getElementById('year').textContent = new Date().getFullYear();
