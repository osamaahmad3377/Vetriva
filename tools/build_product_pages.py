"""Build dog-products.html and cat-products.html.

The header, footer and WhatsApp button are copied from index.html (with links pointed back at
the home page), so after changing the header or footer on the home page, run:

    python3 tools/build_product_pages.py
"""
import html
import re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
WHATSAPP = '923239737896'  # TODO: replace with the clinic's real WhatsApp number

ICONS = {
    'food': '<path d="M3 11h18a9 9 0 0 1-18 0Z"/><path d="M8 7.5c.4-1.4 1.4-2.2 3-2.4M13.5 6.5c.4-1 1.3-1.6 2.8-1.7"/>',
    'treats': '<g transform="rotate(-40 12 12)"><path d="M7 10.6h10M7 13.4h10"/><circle cx="5.4" cy="10.2" r="1.9"/><circle cx="5.4" cy="13.8" r="1.9"/><circle cx="18.6" cy="10.2" r="1.9"/><circle cx="18.6" cy="13.8" r="1.9"/></g>',
    'toys': '<circle cx="12" cy="12" r="9"/><path d="M5.6 5.6c3.5 3.5 3.5 9.3 0 12.8M18.4 5.6c-3.5 3.5-3.5 9.3 0 12.8"/>',
    'accessories': '<path d="M20.6 13.4 13.4 20.6a2 2 0 0 1-2.8 0L3 13V3h10l7.6 7.6a2 2 0 0 1 0 2.8Z"/><circle cx="7.5" cy="7.5" r="1.5"/>',
    'grooming': '<circle cx="6" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M20 4 8.1 15.9M14.5 14.5 20 20M8.1 8.1 12 12"/>',
    'health-care': '<path d="M10.5 20.5 3.5 13.5a5 5 0 0 1 7-7l7 7a5 5 0 0 1-7 7Z"/><path d="m8.5 8.5 7 7"/>',
}

# Product photos (Pexels licence: free to use, no attribution required), one per product, in the
# same order as the products listed under each category below.
IMAGES = {
    'dog': [
        'dog-puppy-food', 'dog-adult-dry-food', 'dog-wet-food', 'dog-prescription-diets',
        'dog-training-treats', 'dog-dental-chews', 'dog-biscuits-jerky', 'dog-natural-chews',
        'dog-chew-toys', 'dog-balls-fetch', 'dog-rope-tug', 'dog-puzzle-toys',
        'dog-collars-leashes', 'dog-harnesses', 'dog-beds-mats', 'dog-bowls-feeders',
        'dog-shampoos', 'dog-brushes-combs', 'dog-nail-clippers', 'dog-ear-eye-care',
        'dog-flea-tick', 'dog-dewormers', 'dog-vitamins', 'dog-joint-care',
    ],
    'cat': [
        'cat-kitten-food', 'cat-adult-dry-food', 'cat-wet-food', 'cat-prescription-diets',
        'cat-crunchy-treats', 'cat-creamy-lickables', 'cat-dental-treats', 'cat-catnip-treats',
        'cat-teaser-wands', 'cat-balls-mice', 'cat-scratchers', 'cat-catnip-toys',
        'cat-litter', 'cat-beds', 'cat-bowls-fountains', 'cat-carriers',
        'cat-brushes', 'cat-shampoos', 'cat-nail-clippers', 'cat-hairball-care',
        'cat-flea-tick', 'cat-dewormers', 'cat-vitamins', 'cat-urinary-care',
    ],
}

CATEGORIES = [  # slug, name, intro
    ('food', 'Food', 'Complete, balanced nutrition for every life stage.'),
    ('treats', 'Treats', 'Healthy rewards for training and everyday love.'),
    ('toys', 'Toys', 'Play that keeps them active, busy and happy.'),
    ('accessories', 'Accessories', 'Everyday essentials for comfort and safety.'),
    ('grooming', 'Grooming', 'Keep coats clean, healthy and shiny at home.'),
    ('health-care', 'Health Care', 'Protection and support, chosen with our vets.'),
]

PAGES = {
    'dog': {
        'title': 'Dog', 'other': 'cat', 'image': ('assets/img/pets/terrier.webp', 842, 860),
        'lead': 'Food, treats, toys and care essentials for your dog, recommended by our vets and available at the clinic.',
        'items': {
            'food': [('Puppy Food', 'Growth formulas for healthy development.'),
                     ('Adult Dry Food', 'Everyday kibble for active adult dogs.'),
                     ('Wet Food', 'Tasty, hydrating meals and toppers.'),
                     ('Prescription Diets', 'Special diets prescribed by our vets.')],
            'treats': [('Training Treats', 'Small, soft rewards for good behaviour.'),
                       ('Dental Chews', 'Help keep teeth clean and breath fresh.'),
                       ('Biscuits & Jerky', 'Crunchy and chewy everyday snacks.'),
                       ('Natural Chews', 'Long-lasting chews for keen chewers.')],
            'toys': [('Chew Toys', 'Durable toys for strong jaws.'),
                     ('Balls & Fetch', 'For games in the park or garden.'),
                     ('Rope & Tug', 'Interactive play for you and your dog.'),
                     ('Puzzle Toys', 'Keep clever minds busy.')],
            'accessories': [('Collars & Leashes', 'Comfortable, secure everyday walking gear.'),
                            ('Harnesses', 'Gentle control without pulling on the neck.'),
                            ('Beds & Mats', 'A cosy place to rest.'),
                            ('Bowls & Feeders', 'Easy-clean bowls and slow feeders.')],
            'grooming': [('Shampoos & Conditioners', 'Gentle formulas for every coat type.'),
                         ('Brushes & Combs', 'Remove loose hair and prevent tangles.'),
                         ('Nail Clippers', 'Safe trimming at home.'),
                         ('Ear & Eye Care', 'Gentle cleaners for daily care.')],
            'health-care': [('Flea & Tick Control', 'Treatments and collars to keep pests away.'),
                            ('Dewormers', 'Regular protection against worms.'),
                            ('Vitamins & Supplements', 'Support for skin, coat and immunity.'),
                            ('Joint Care', 'Help for growing and senior joints.')],
        },
    },
    'cat': {
        'title': 'Cat', 'other': 'dog', 'image': ('assets/img/pets/cat-tabby.webp', 696, 760),
        'lead': 'Food, litter, toys and care essentials for your cat, recommended by our vets and available at the clinic.',
        'items': {
            'food': [('Kitten Food', 'Nutrition for healthy growth.'),
                     ('Adult Dry Food', 'Balanced everyday meals.'),
                     ('Wet Food & Pouches', 'Tasty, hydrating meals.'),
                     ('Prescription Diets', 'Special diets prescribed by our vets.')],
            'treats': [('Crunchy Treats', 'Bite-sized rewards cats love.'),
                       ('Creamy Lickables', 'A favourite for bonding and pills.'),
                       ('Dental Treats', 'Help keep teeth clean.'),
                       ('Catnip Treats', 'A little fun in every bite.')],
            'toys': [('Teaser Wands', 'Feathers and ribbons for chasing.'),
                     ('Balls & Mice', 'Small toys for batting and pouncing.'),
                     ('Scratchers', 'Save your furniture.'),
                     ('Catnip Toys', 'Irresistible play.')],
            'accessories': [('Litter & Litter Boxes', 'Clumping litter and easy-clean trays.'),
                            ('Beds & Hideaways', 'Cosy spots to curl up.'),
                            ('Bowls & Fountains', 'Encourage healthy drinking.'),
                            ('Carriers', 'Safe, comfortable travel to the vet.')],
            'grooming': [('Brushes & Deshedding', 'Less loose hair around the home.'),
                         ('Shampoos', 'Gentle, cat-safe formulas.'),
                         ('Nail Clippers', 'Safe trimming at home.'),
                         ('Hairball Care', 'Gels and treats that help hairballs pass.')],
            'health-care': [('Flea & Tick Control', 'Spot-ons and treatments for cats.'),
                            ('Dewormers', 'Regular protection against worms.'),
                            ('Vitamins & Supplements', 'Support for skin, coat and immunity.'),
                            ('Urinary Care', 'Support for a healthy urinary tract.')],
        },
    },
}


def icon(slug, cls='icon'):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{ICONS[slug]}</svg>'


def wa(text):
    return f'https://wa.me/{WHATSAPP}?text={quote(text)}'


def shared_parts():
    """Header, footer and WhatsApp button from index.html, with in-page links sent back home."""
    src = (ROOT / 'index.html').read_text()
    header = src[src.index('  <header class="header"'):src.index('  </header>') + len('  </header>')]
    tail = src[src.index('  <!-- ============ FOOTER ============ -->'):src.index('</body>')]

    def home_links(part):
        part = re.sub(r'href="#book" ([^>]*)data-service="([^"]+)"',
                      lambda m: f'href="index.html?service={quote(html.unescape(m.group(2)))}#book" {m.group(1)}data-service="{m.group(2)}"',
                      part)
        part = part.replace('href="#home"', 'href="index.html"')
        return re.sub(r'href="#([\w-]+)"', r'href="index.html#\1"', part)

    header = home_links(header).replace(' class="is-active">Home<', '>Home<')
    header = header.replace('class="nav__link nav__link--plain"', 'class="nav__link nav__link--plain is-active"')
    return header, home_links(tail)


def build(kind):
    page = PAGES[kind]
    title, other = page['title'], page['other']
    img, w, h = page['image']
    header, tail = shared_parts()

    chips = '\n'.join(
        f'          <li><a href="#{slug}">{icon(slug)}<span>{name}</span></a></li>' for slug, name, _ in CATEGORIES)

    sections = []
    photos = iter(IMAGES[kind])
    for n, (slug, name, intro) in enumerate(CATEGORIES):
        cards = '\n'.join(f'''          <article class="pitem reveal">
            <div class="pitem__img"><img src="assets/img/products/{next(photos)}.webp" alt="{html.escape(item)}" width="640" height="480" loading="lazy"></div>
            <div class="pitem__body">
              <span class="pitem__tag">{icon(slug)}{name}</span>
              <h3>{html.escape(item)}</h3>
              <p>{html.escape(desc)}</p>
              <div class="pitem__foot">
                <span class="pitem__price">Price on request</span>
                <a href="{wa(f'Hello Vetriva, I would like to order {item.lower()} for my {kind}. Please share the available options and prices.')}" class="pitem__btn" target="_blank" rel="noopener" aria-label="Order {html.escape(item)} on WhatsApp">Order<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M3 21l1.7-5A9 9 0 1 1 8 19.3z"/></svg></a>
              </div>
            </div>
          </article>''' for item, desc in page['items'][slug])
        sections.append(f'''    <section class="pcat{' pcat--tint' if n % 2 else ''}" id="{slug}" aria-labelledby="{slug}-title">
      <div class="container">
        <div class="pcat__head reveal">
          <span class="pcat__icon">{icon(slug)}</span>
          <div>
            <h2 id="{slug}-title">{title} {name}</h2>
            <p>{intro}</p>
          </div>
        </div>
        <div class="pitems">
{cards}
        </div>
      </div>
    </section>''')

    doc = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} Products | Vetriva Animal Hospital, Islamabad</title>
  <meta name="description" content="Vet-recommended {kind} food, treats, toys, accessories, grooming and health care products at Vetriva Animal Hospital, Islamabad.">
  <meta name="theme-color" content="#0E2944">
  <link rel="icon" type="image/png" href="assets/img/favicon.png">
  <link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Kaushan+Script&family=Nunito:wght@400;600;700;800;900&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/css/style.css">
  <script>document.documentElement.classList.add('js');</script>
</head>
<body class="page-products">
  <!-- Generated by tools/build_product_pages.py; edit that script (or index.html for the header/footer) and re-run it. -->

{header}

  <main>
    <section class="page-hero texture">
      <div class="container page-hero__grid">
        <div class="page-hero__copy">
          <nav class="crumbs" aria-label="Breadcrumb">
            <a href="index.html">Home</a><span aria-hidden="true">/</span><span>Products</span><span aria-hidden="true">/</span><span aria-current="page">{title}</span>
          </nav>
          <h1>{title} <span class="script">Products</span></h1>
          <p class="page-hero__lead">{page['lead']}</p>
          <div class="page-hero__actions">
            <a href="{wa(f'Hello Vetriva, I would like to ask about {kind} products.')}" class="btn btn--light" target="_blank" rel="noopener">Ask on WhatsApp</a>
            <a href="{other}-products.html" class="page-hero__switch">Shopping for a {other}? <span aria-hidden="true">&rarr;</span></a>
          </div>
        </div>
        <div class="page-hero__visual">
          <div class="page-hero__ring" aria-hidden="true"></div>
          <img src="{img}" alt="" width="{w}" height="{h}" fetchpriority="high">
        </div>
      </div>
      <svg class="wave wave--bottom" viewBox="0 0 1440 200" preserveAspectRatio="none" aria-hidden="true">
        <path d="M0 150c180-10 330 40 520 36 230-5 330-90 560-120 140-18 250-6 360 10v124H0Z"/>
      </svg>
    </section>

    <nav class="cat-nav" aria-label="{title} product categories">
      <div class="container">
        <ul class="cat-nav__list">
{chips}
        </ul>
      </div>
    </nav>

{chr(10).join(sections)}

    <section class="pcta">
      <div class="container">
        <div class="pcta__box reveal">
          <div>
            <h2>Not sure what's right for your {kind}?</h2>
            <p>Our vets can recommend the right food and care products for your {kind}'s age, breed and health.</p>
          </div>
          <div class="pcta__actions">
            <a href="index.html?service=Diet%20Management#book" class="btn btn--light">Book a consultation</a>
            <a href="{wa(f'Hello Vetriva, I need advice on products for my {kind}.')}" class="pcta__wa" target="_blank" rel="noopener">Ask on WhatsApp <span aria-hidden="true">&rarr;</span></a>
          </div>
        </div>
      </div>
    </section>
  </main>

{tail}</body>
</html>
'''
    (ROOT / f'{kind}-products.html').write_text(doc)
    print(f'wrote {kind}-products.html')


if __name__ == '__main__':
    for kind in PAGES:
        build(kind)
