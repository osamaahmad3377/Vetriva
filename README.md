# Vetriva Animal Hospital website

Static website (HTML, CSS, JavaScript) for Vetriva Animal Hospital, Islamabad. No build step: open `index.html` in a browser, or host the folder on any static host.

## Pages
- `index.html` home page (hero, services, facility, booking form, contact)
- `about.html` about us
- `service-*.html` one page per service (16)
- `dog-products.html`, `cat-products.html` product pages

## Generated pages
The About, service and product pages are generated. They copy the header and footer from `index.html`, so after changing those, re-run:

```
python3 tools/build_about_page.py
python3 tools/build_service_pages.py
python3 tools/build_product_pages.py
```

Edit the page text in those scripts, not in the generated HTML.

## Before going live
Replace the remaining placeholders (marked `TODO` in the code): email, opening hours, Facebook and Instagram links, and check the Google Maps pin.

Photos are from Unsplash and Pexels.

Developed by [NextCore](https://nextcore.com.pk/).
