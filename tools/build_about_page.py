"""Build about.html (header/footer are copied from index.html).

    python3 tools/build_about_page.py

TODO before going live: add Vetriva's real story, vets and photos. The text below is general and makes
no claims beyond what the rest of the site already says.
"""
import html
import re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
WHATSAPP = '923239737896'  # TODO: replace with the clinic's real WhatsApp number

ICONS = {
    'heart': '<path d="M19 14c1.5-1.5 3-3.2 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.8 0-3 .5-4.5 2-1.5-1.5-2.7-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4 3 5.5l7 7z"/>',
    'shield': '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>',
    'chat': '<path d="M21 15a2 2 0 0 1-2 2H8l-5 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    'sparkle': '<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/><path d="M19 17l.7 2 2 .7-2 .7-.7 2-.7-2-2-.7 2-.7z"/>',
    'screen': '<rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/>',
    'paw': '<ellipse cx="5.4" cy="10.4" rx="2.1" ry="2.6"/><ellipse cx="9.5" cy="5.9" rx="2.1" ry="2.7"/><ellipse cx="14.5" cy="5.9" rx="2.1" ry="2.7"/><ellipse cx="18.6" cy="10.4" rx="2.1" ry="2.6"/><path d="M12 11.6c-3 0-6.1 3.7-6.1 6.3 0 1.7 1.3 2.5 2.9 2.5 1.3 0 2.1-.7 3.2-.7s1.9.7 3.2.7c1.6 0 2.9-.8 2.9-2.5 0-2.6-3.1-6.3-6.1-6.3z"/>',
    'syringe': '<path d="m18 2 4 4M17 7l3-3M19 9 8.7 19.3a2.4 2.4 0 0 1-3.4 0l-.6-.6a2.4 2.4 0 0 1 0-3.4L15 5M9 11l4 4M5 19l-3 3M14 4l6 6"/>',
    'plus': '<rect x="3" y="3" width="18" height="18" rx="5"/><path d="M12 8v8M8 12h8"/>',
    'flask': '<path d="M9 3h6M10 3v6.5L4.5 19A1.5 1.5 0 0 0 5.8 21h12.4a1.5 1.5 0 0 0 1.3-2L14 9.5V3"/><path d="M7 15h10"/>',
}


def icon(name, cls='icon'):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'


def wa(text):
    return f'https://wa.me/{WHATSAPP}?text={quote(text)}'


def shared_parts():
    src = (ROOT / 'index.html').read_text()
    header = src[src.index('  <header class="header"'):src.index('  </header>') + len('  </header>')]
    tail = src[src.index('  <!-- ============ FOOTER ============ -->'):src.index('</body>')]

    def home_links(part):
        part = re.sub(r'href="#book" ([^>]*)data-service="([^"]+)"',
                      lambda m: f'href="index.html?service={quote(html.unescape(m.group(2)))}#book" {m.group(1)}data-service="{m.group(2)}"', part)
        part = part.replace('href="#home"', 'href="index.html"')
        return re.sub(r'href="#([\w-]+)"', r'href="index.html#\1"', part)

    header = home_links(header).replace(' class="is-active">Home<', '>Home<')
    header = header.replace('<a href="about.html">About</a>', '<a href="about.html" class="is-active">About</a>')
    return header, home_links(tail)


VALUES = [
    ('heart', 'Compassion first', 'Every pet is treated like family. We take time to listen, and we handle every animal gently.'),
    ('shield', 'Expert care', 'Qualified veterinarians who explain every step and every option in plain words.'),
    ('chat', 'Honest advice', 'Clear, honest recommendations, with no pressure, so you can make the right choice for your pet.'),
    ('sparkle', 'Clean and calm', 'A clean, welcoming clinic with low-stress handling that helps anxious pets relax.'),
]
PILLARS = [
    'Qualified, caring veterinarians',
    'Modern diagnostics and equipment',
    'Gentle, fear-free handling',
    'Strict hygiene from consultation to recovery',
    'Clear communication and follow-up',
]
SERVICES = [
    ('plus', 'Wellness Examination', 'wellness-examination', 'A thorough head-to-tail check-up to keep your pet healthy.'),
    ('syringe', 'Vaccination', 'vaccination', 'Protection against serious, preventable diseases.'),
    ('plus', 'Surgery', 'surgery', 'Safe, carefully monitored surgery with a focus on comfort and recovery.'),
    ('flask', 'Laboratory', 'laboratory', 'Blood and other tests that show what is happening inside.'),
]


def build():
    header, tail = shared_parts()
    values = '\n'.join(f'''          <article class="card reveal">
            <span class="card__icon">{icon(i)}</span>
            <h3>{t}</h3>
            <p>{d}</p>
          </article>''' for i, t, d in VALUES)
    pillars = '\n'.join(f'            <li><span class="check" aria-hidden="true">{icon("paw")}</span>{p}</li>' for p in PILLARS)
    services = '\n'.join(f'''          <article class="card reveal">
            <span class="card__icon">{icon(i)}</span>
            <h3>{n}</h3>
            <p>{d}</p>
            <a href="service-{slug}.html" class="card__link">Learn more <span aria-hidden="true">&rarr;</span></a>
          </article>''' for i, n, slug, d in SERVICES)
    species = '\n'.join(f'            <li class="sv-extra">{s}</li>' for s in ['Dogs', 'Cats', 'Birds', 'Rabbits', 'Small pets'])

    doc = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>About Us | Vetriva Animal Hospital, Islamabad</title>
  <meta name="description" content="Meet Vetriva Animal Hospital in Islamabad: expert, compassionate veterinary care for dogs, cats, birds, rabbits and small pets.">
  <meta name="theme-color" content="#0E2944">
  <link rel="icon" type="image/png" href="assets/img/favicon.png">
  <link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Kaushan+Script&family=Nunito:wght@400;600;700;800;900&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/css/style.css">
  <script>document.documentElement.classList.add('js');</script>
</head>
<body class="page-service page-about">
  <!-- Generated by tools/build_about_page.py; edit that script (or index.html for the header/footer) and re-run it. -->

{header}

  <main>
    <section class="page-hero sv-hero texture">
      <div class="sv-cover" aria-hidden="true">
        <img src="assets/img/photos/vet-cat.webp" alt="" style="object-position: 45% 40%" fetchpriority="high">
        <span class="sv-badge">{icon("heart")}</span>
      </div>
      <div class="container page-hero__grid">
        <div class="page-hero__copy">
          <nav class="crumbs" aria-label="Breadcrumb">
            <a href="index.html">Home</a><span aria-hidden="true">/</span><span aria-current="page">About Us</span>
          </nav>
          <p class="sv-group">About Vetriva</p>
          <h1>About <span class="script">Us</span></h1>
          <p class="page-hero__lead">Expert, gentle veterinary care for the pets you love, right here in Islamabad.</p>
          <div class="page-hero__actions">
            <a href="index.html#book" class="btn btn--light">Book appointment</a>
            <a href="index.html#contact" class="page-hero__switch">Find us <span aria-hidden="true">&rarr;</span></a>
          </div>
        </div>
      </div>
      <svg class="wave wave--bottom" viewBox="0 0 1440 200" preserveAspectRatio="none" aria-hidden="true">
        <path d="M0 150c180-10 330 40 520 36 230-5 330-90 560-120 140-18 250-6 360 10v124H0Z"/>
      </svg>
    </section>

    <section class="section sv-about">
      <div class="container sv-about__grid">
        <div class="sv-about__copy reveal">
          <p class="label">Our story</p>
          <h2>A clinic built around trust</h2>
          <p>Vetriva Animal Hospital is a veterinary clinic in Islamabad. We combine modern veterinary medicine with a calm, welcoming environment, so visits are easier for pets and for the people who love them.</p>
          <p class="ab-more">From a first vaccination to advanced diagnostics and surgery, our aim is simple: to look after every animal as if they were our own, and to give you the clear, honest information you need to make good decisions.</p>
          <ul class="sv-extras" aria-label="Animals we care for">
{species}
          </ul>
        </div>
        <div class="ab-photo reveal">
          <img src="assets/img/services/wellness-examination.webp" alt="A vet examining a dog" width="1400" height="933" loading="lazy">
        </div>
      </div>
    </section>

    <section class="section sv-tint">
      <div class="container">
        <div class="section__head reveal">
          <h2>What we stand for</h2>
          <p>The values behind everything we do for you and your pet.</p>
        </div>
        <div class="cards">
{values}
        </div>
      </div>
    </section>

    <section class="section ab-why-section">
      <div class="container">
        <div class="ab-why reveal">
          <img class="ab-why__cat" src="assets/img/photos/cat-paws.webp" alt="A curious cat holding on to the top of the card" width="1100" height="493" loading="lazy">
          <div class="sv-included ab-why__box">
            <p class="label">Why choose Vetriva</p>
            <h3>Care you can count on</h3>
            <ul>
{pillars}
            </ul>
            <a href="index.html#book" class="btn btn--primary">Book now</a>
          </div>
        </div>
      </div>
    </section>

    <section class="section sv-tint">
      <div class="container">
        <div class="section__head reveal">
          <h2>How we can help</h2>
          <p>A few of the services we offer. Browse them all from the Services menu.</p>
        </div>
        <div class="cards">
{services}
        </div>
      </div>
    </section>

    <section class="pcta">
      <div class="container">
        <div class="pcta__box reveal">
          <div>
            <h2>Come and meet us</h2>
            <p>Book a visit, or message us on WhatsApp with any questions about your pet.</p>
          </div>
          <div class="pcta__actions">
            <a href="index.html#book" class="btn btn--light">Book appointment</a>
            <a href="{wa("Hello Vetriva, I would like to know more about the clinic.")}" class="pcta__wa" target="_blank" rel="noopener">Ask on WhatsApp <span aria-hidden="true">&rarr;</span></a>
          </div>
        </div>
      </div>
    </section>
  </main>

{tail}</body>
</html>
'''
    (ROOT / 'about.html').write_text(doc)
    print('wrote about.html')


if __name__ == '__main__':
    build()
