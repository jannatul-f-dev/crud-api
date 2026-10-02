# The polite scraper (A9)

A small, polite web scraper that collects book data from [Books to Scrape](https://books.toscrape.com), a public practice sandbox built for learning scraping.

## Target classification

- **Site:** books.toscrape.com
- **Why:** It is explicitly a public sandbox created for people to practise web scraping on. That is permission to scrape it, and this project touches no other site.
- **Scope:** Only the first 3 catalogue pages (60 books total).
- **Data collected:** Book title, price, availability, rating, description, and product URL — all publicly shown on the page, nothing behind a login.
- **robots.txt result:** Requested `https://books.toscrape.com/robots.txt` — it returns a 404 Not Found. No robots file exists for this site. A missing file is not permission by itself, but combined with the site's own stated purpose as a scraping sandbox, scraping it is appropriate here.

I will not reuse this code on another site without checking its rules and terms first.